import rumps
import pyaudio
import threading
import tempfile
import wave
import json
import os
from pathlib import Path
import queue
import traceback
import time

import mlx_whisper
import pyperclip
import pyautogui
from pynput import keyboard

LANG_BADGE = {"ko": "KR", "en": "EN", "vi": "VN", "ja": "JP", "zh": "CH"}

class VoiceRecorderApp(rumps.App):
    def __init__(self):
        super().__init__("🎤", quit_button=None)

        # 설정 로드
        self.config_path = Path.home() / ".config" / "voice-recorder" / "config.json"
        self.load_config()
        self.title = "🎤"
        # 오디오 설정
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.CHUNK = 1024

        self.is_recording = False
        self.frames = []
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.record_thread = None

        # UI 작업 큐(메인 루프에서만 UI 변경/notification 실행)
        self._uiq: "queue.Queue[callable]" = queue.Queue()

        # 핫키 이벤트 (pynput 스레드 -> event set -> 메인 타이머 처리)
        self._toggle_event = threading.Event()

        # 타이머: UI 큐 drain + 이벤트 처리
        self._ui_timer = rumps.Timer(self._drain_mainloop, 0.05)
        self._ui_timer.start()

        # 단축키 리스너
        self.hotkey_listener = None
        self.setup_hotkey()

        # 메뉴 구성
        self.build_menu()

    # ---------------------------
    # Config
    # ---------------------------
    def load_config(self):
        """설정 파일 로드"""
        default_config = {
            "record_hotkey": "ctrl+shift+m",
            "language": "ko",
            "model": "mlx-community/whisper-large-v3-turbo",
        }

        cfg = {}
        try:
            if self.config_path.exists():
                with open(self.config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f) or {}
        except Exception:
            cfg = {}

        # 구버전 호환: 예전 key가 "hotkey"면 record_hotkey로 흡수
        if "record_hotkey" not in cfg and "hotkey" in cfg:
            cfg["record_hotkey"] = cfg["hotkey"]

        # merge defaults
        self.config = {**default_config, **cfg}

        # record_hotkey가 없으면 안전하게 기본값
        if not self.config.get("record_hotkey"):
            self.config["record_hotkey"] = default_config["record_hotkey"]

    def save_config(self):
        """설정 파일 저장"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    # ---------------------------
    # UI helpers (main thread via queue)
    # ---------------------------
    def _ui(self, fn):
        """메인 루프에서 실행할 UI 작업 등록"""
        self._uiq.put(fn)

    def _notify(self, title, subtitle, message):
        """notification도 메인 루프에서 실행"""
        def _do():
            try:
                rumps.notification(title, subtitle, message)
            except Exception:
                # 알림 실패는 치명적이지 않음
                pass
        self._ui(_do)

    def _drain_mainloop(self, _):
        """메인 루프에서: 이벤트 처리 + UI 큐 실행"""
        # 0) 파일 트리거 체크
        trigger_file = Path("/tmp/voice-toggle")
        if trigger_file.exists():
            try:
                trigger_file.unlink()
            except Exception:
                pass
            self._toggle_event.set()

        # 1) 핫키 이벤트 처리
        if self._toggle_event.is_set():
            self._toggle_event.clear()
            self.toggle_recording(None)

        # 2) UI 큐 drain
        for _ in range(50):  # 한 tick에 과도 실행 방지
            try:
                fn = self._uiq.get_nowait()
            except queue.Empty:
                break
            try:
                fn()
            except Exception:
                # 디버그용: 여기서 죽으면 앱이 조용히 종료될 수 있어서 방어
                traceback.print_exc()

    # ---------------------------
    # Menu
    # ---------------------------
    def build_menu(self):
        """메뉴 구성"""
        self.menu.clear()

        record_hk = self.config.get("record_hotkey", "")

        # 녹음 상태
        status = "🔴 녹음 중지" if self.is_recording else "녹음 시작"
        self.status_item = rumps.MenuItem(
            f"{status} ({self.format_hotkey(record_hk)})",
            callback=self.toggle_recording
        )
        self.menu.add(self.status_item)

        self.menu.add(rumps.separator)

        # 단축키 설정(녹음 토글용)
        hotkey_menu = rumps.MenuItem("녹음 단축키 설정")
        hotkeys = [
            ("ctrl+shift+m", "⌃⇧M"),
            ("cmd+shift+r", "⌘⇧R"),
            ("alt+space", "⌥Space"),
            ("cmd+alt+space", "⌘⌥Space"),
            ("ctrl+shift+space", "⌃⇧Space"),
        ]
        for key, label in hotkeys:
            item = rumps.MenuItem(
                f"{'✓ ' if record_hk == key else '   '}{label}",
                callback=lambda sender, k=key: self.set_record_hotkey(k)
            )
            hotkey_menu.add(item)
        self.menu.add(hotkey_menu)

        self.menu.add(rumps.separator)
        self.menu.add(rumps.MenuItem("종료", callback=self.quit_app))

    def format_hotkey(self, hotkey: str) -> str:
        """단축키를 보기 좋게 포맷"""
        if not hotkey:
            return "-"
        replacements = {
            "cmd": "⌘", "shift": "⇧", "alt": "⌥",
            "ctrl": "⌃", "space": "Space", "+": ""
        }
        result = hotkey.lower()
        for k, v in replacements.items():
            result = result.replace(k, v)
        return result

    # ---------------------------
    # Hotkey parsing/normalization
    # ---------------------------
    def _norm_key(self, key):
        """pynput key를 비교 가능한 표준 형태로 정규화"""
        # modifiers canonicalize
        if key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
            return keyboard.Key.ctrl
        if key in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r):
            return keyboard.Key.shift
        if key in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt_gr):
            return keyboard.Key.alt
        if key in (keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r):
            return keyboard.Key.cmd
        if key == keyboard.Key.space:
            return keyboard.Key.space

        # characters
        if isinstance(key, keyboard.KeyCode) and key.char:
            return ("char", key.char.lower())

        return key

    def parse_hotkey_for_pynput(self, hotkey: str):
        """pynput용 단축키 파싱 -> 정규화된 키 set 반환"""
        parts = (hotkey or "").lower().split("+")
        keys = set()
        for part in parts:
            part = part.strip()
            if part == "cmd":
                keys.add(keyboard.Key.cmd)
            elif part == "shift":
                keys.add(keyboard.Key.shift)
            elif part == "alt":
                keys.add(keyboard.Key.alt)
            elif part == "ctrl":
                keys.add(keyboard.Key.ctrl)
            elif part == "space":
                keys.add(keyboard.Key.space)
            elif len(part) == 1:
                keys.add(("char", part))
        return keys

    def setup_hotkey(self):
        """글로벌 단축키 설정 (녹음 토글)"""
        if self.hotkey_listener:
            self.hotkey_listener.stop()

        record_keys = self.parse_hotkey_for_pynput(self.config.get("record_hotkey", "ctrl+shift+m"))

        current_keys = set()
        fired_record = False

        def on_press(key):
            nonlocal fired_record
            nk = self._norm_key(key)
            current_keys.add(nk)

            if (not fired_record) and record_keys.issubset(current_keys):
                fired_record = True
                self._toggle_event.set()

        def on_release(key):
            nonlocal fired_record
            nk = self._norm_key(key)
            current_keys.discard(nk)

            if not record_keys.issubset(current_keys):
                fired_record = False

        self.hotkey_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.hotkey_listener.start()

    # ---------------------------
    # Settings actions
    # ---------------------------
    def set_record_hotkey(self, hotkey: str):
        """녹음 단축키 변경"""
        self.config["record_hotkey"] = hotkey
        self.save_config()
        self.setup_hotkey()
        self.build_menu()
        self._notify("음성 인식", "", f"녹음 단축키: {self.format_hotkey(hotkey)}")

    def set_language(self, lang: str):
        """언어 변경(직접 선택)"""
        self.config["language"] = lang
        self.save_config()
        self.build_menu()
        lang_names = {
            "ko": "한국어",
            "en": "English",
            "ja": "日本語",
            "zh": "中文",
            "vi": "Tiếng Việt",
        }
        self._notify("음성 인식", "", f"전사 언어: {lang_names.get(lang, lang)}")

    def cycle_language(self):
        """언어 순환 전환 (cmd+shift+space)"""
        order = ["ko", "en", "vi", "ja", "zh"]  # 원하는 순서로 조정 가능
        cur = self.config.get("language", "ko")
        try:
            nxt = order[(order.index(cur) + 1) % len(order)]
        except ValueError:
            nxt = "ko"

        self.config["language"] = nxt
        self.save_config()
        self.build_menu()
        self._notify("음성 인식", "", f"전사 언어 전환: {nxt}")
        badge = LANG_BADGE.get(self.config["language"], self.config["language"].upper())
        if str(self.title).startswith("🔴"):
            self.title = f"🔴{badge}"
        elif str(self.title).startswith("⏳"):
            self.title = f"⏳{badge}"
        else:
            self.title = f"🎤{badge}"
    # ---------------------------
    # Recording
    # ---------------------------
    def toggle_recording(self, sender):
        """녹음 토글"""
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        """녹음 시작"""
        if self.is_recording:
            return

        self.is_recording = True
        self.frames = []

        # UI 업데이트는 메인루프에서
        self.title = "🔴"
        self.build_menu()

        try:
            self.stream = self.audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )
        except Exception as e:
            self.is_recording = False
            self.title = "🎤"
            self.build_menu()
            self._notify("오디오 오류", "", str(e)[:120])
            return

        def record():
            while self.is_recording:
                try:
                    data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                    self.frames.append(data)
                except Exception as e:
                    # 백그라운드 스레드 -> 메인루프 알림
                    self._notify("오디오 오류", "", str(e)[:120])
                    break

        self.record_thread = threading.Thread(target=record, daemon=True)
        self.record_thread.start()

    def stop_recording(self):
        """녹음 중지 및 전사"""
        if not self.is_recording:
            return

        self.is_recording = False
        self.title = "⏳"
        self.build_menu()

        if self.record_thread:
            self.record_thread.join(timeout=1)

        if self.stream:
            try:
                self.stream.stop_stream()
            except Exception:
                pass
            try:
                self.stream.close()
            except Exception:
                pass
            self.stream = None

        if not self.frames:
            self.title = "🎤"
            self.build_menu()
            return

        frames_snapshot = self.frames[:]  # 전사 스레드에 안전하게 전달
        self.frames = []

        threading.Thread(target=self.transcribe_and_paste, args=(frames_snapshot,), daemon=True).start()

    # ---------------------------
    # Transcription
    # ---------------------------
    def transcribe_and_paste(self, frames_snapshot):
        """전사 및 붙여넣기 (백그라운드)"""
        temp_path = None
        try:
            # WAV 파일로 저장
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                temp_path = f.name

            wf = wave.open(temp_path, "wb")
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b"".join(frames_snapshot))
            wf.close()

            # mlx-whisper로 전사 (한국어 고정)
            result = mlx_whisper.transcribe(
                temp_path,
                path_or_hf_repo=self.config["model"],
                language="ko"
            )
            text = (result.get("text") or "").strip()

            if text:
                pyperclip.copy(text)

                # 붙여넣기 (메인루프에서 실행하는 게 더 안전)
                def do_paste():
                    try:
                        pyautogui.hotkey("command", "v")
                    except Exception as e:
                        self._notify("붙여넣기 오류", "", str(e)[:120])

                # 약간 딜레이 후 메인루프에서 수행
                time.sleep(0.1)
                self._ui(do_paste)

                self._notify("음성 인식 완료", "", text[:50] + ("..." if len(text) > 50 else ""))
            else:
                self._notify("음성 인식", "", "인식된 텍스트가 없습니다.")

        except Exception as e:
            self._notify("오류", "", str(e)[:160])

        finally:
            if temp_path:
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass

            # UI 복귀
            self._ui(lambda: setattr(self, "title", "🎤"))
            self._ui(self.build_menu)

    # ---------------------------
    # Quit
    # ---------------------------
    def quit_app(self, sender):
        """앱 종료"""
        try:
            if self.hotkey_listener:
                self.hotkey_listener.stop()
        except Exception:
            pass

        try:
            if self._ui_timer:
                self._ui_timer.stop()
        except Exception:
            pass

        try:
            if self.stream:
                self.stream.close()
        except Exception:
            pass

        try:
            self.audio.terminate()
        except Exception:
            pass

        rumps.quit_application()


if __name__ == "__main__":
    app = VoiceRecorderApp()
    app.run()
