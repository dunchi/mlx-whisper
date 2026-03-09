# myspeak 앱 가이드

이 문서는 myspeak 음성 인식 시스템의 Automator 앱들을 재생성하고 설정하는 방법을 설명합니다.

## 시스템 구성

### 1. myspeak.app
**역할**: 메인 음성 인식 앱을 백그라운드에서 실행
- 터미널 없이 깔끔하게 실행
- 메뉴바에 🎤 아이콘 표시
- 단축키로 녹음 제어 가능

### 2. myspeaktoggle.app
**역할**: 외부에서 녹음을 토글하는 트리거
- 파일 기반 트리거 (`/tmp/voice-toggle`)
- 키보드 단축키, Alfred, Stream Deck 등에서 실행 가능
- 앱 내부 단축키 외에 추가 제어 방법 제공

---

## myspeak.app 재생성 방법

### 1. Automator 실행
```bash
open -a Automator
```

### 2. 새로운 Application 생성
1. "파일" → "신규" 선택
2. "응용 프로그램" 선택
3. "선택" 클릭

### 3. AppleScript 액션 추가
1. 왼쪽 액션 목록에서 "AppleScript 실행" 검색
2. "AppleScript 실행" 액션을 오른쪽 워크플로우로 드래그

### 4. AppleScript 코드 입력
기본 코드를 모두 지우고 다음 코드 입력:

```applescript
on run {input, parameters}
  do shell script "cd /Users/hanju/02hobby/mlx-whisper && /Users/hanju/02hobby/mlx-whisper/venv/bin/python app.py > /dev/null 2>&1 &"
  return input
end run
```

**중요**: 경로는 실제 프로젝트 위치에 맞게 수정하세요.

### 5. 저장
1. "파일" → "저장" (⌘S)
2. 이름: `myspeak`
3. 위치: 원하는 곳 (예: 응용 프로그램, Documents 등)
4. "저장" 클릭

### 6. 확인
1. myspeak.app 더블클릭
2. 메뉴바에 🎤 아이콘이 나타나는지 확인
3. 단축키 (⌃⇧M)로 녹음 테스트

---

## myspeaktoggle.app 재생성 방법

### 1. Automator 실행
```bash
open -a Automator
```

### 2. 새로운 Application 생성
1. "파일" → "신규" 선택
2. "응용 프로그램" 선택
3. "선택" 클릭

### 3. Shell Script 액션 추가
1. 왼쪽 액션 목록에서 "셸 스크립트 실행" 검색
2. "셸 스크립트 실행" 액션을 오른쪽 워크플로우로 드래그

### 4. Shell Script 코드 입력
기본 코드를 모두 지우고 다음 코드 입력:

```bash
touch /tmp/voice-toggle
```

### 5. 저장
1. "파일" → "저장" (⌘S)
2. 이름: `myspeaktoggle`
3. 위치: 원하는 곳
4. "저장" 클릭

### 6. 확인
1. myspeak.app이 실행 중인 상태에서
2. myspeaktoggle.app 더블클릭
3. 녹음이 시작/중지되는지 확인

---

## 로그인 시 자동 실행 설정

### 방법 1: 시스템 설정 (권장)

1. **시스템 설정** 열기
2. **일반** → **로그인 항목** 선택
3. **+** 버튼 클릭
4. `myspeak.app` 선택
5. **열기** 클릭

이제 컴퓨터를 켤 때마다 자동으로 myspeak이 실행됩니다.

### 방법 2: 명령어로 추가

```bash
osascript -e 'tell application "System Events" to make login item at end with properties {path:"/Applications/myspeak.app", hidden:false}'
```

**경로 수정**: myspeak.app의 실제 경로로 변경하세요.

### 로그인 항목 확인

```bash
osascript -e 'tell application "System Events" to get the name of every login item'
```

---

## 키보드 단축키 설정 (myspeaktoggle용)

myspeaktoggle.app을 키보드 단축키로 실행하고 싶다면:

### 1. 시스템 설정
1. **시스템 설정** → **키보드** → **키보드 단축키**
2. 왼쪽에서 **앱 단축키** 선택
3. **+** 버튼 클릭

### 2. 단축키 설정
1. **응용 프로그램**: 기타... → myspeaktoggle.app 선택
2. **메뉴 제목**: (비워둠)
3. **키보드 단축키**: 원하는 단축키 입력 (예: ⌥⌘Space)
4. **추가** 클릭

**참고**: 이 방법은 완벽하지 않을 수 있습니다. Alfred, Raycast, Hammerspoon 사용을 권장합니다.

---

## Alfred/Raycast와 연동

### Alfred Workflow
1. Alfred Preferences → Workflows
2. **+** → Blank Workflow
3. **+** → Inputs → Hotkey
4. 원하는 단축키 설정
5. **+** → Actions → Run Script
6. Language: `/bin/bash`
7. Script: `touch /tmp/voice-toggle`
8. 저장

### Raycast Script Command
파일 생성: `~/Library/Application Support/Raycast/Scripts/myspeak-toggle.sh`

```bash
#!/bin/bash

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Toggle MySpeak Recording
# @raycast.mode silent

# Optional parameters:
# @raycast.icon 🎤

touch /tmp/voice-toggle
```

실행 권한 부여:
```bash
chmod +x ~/Library/Application\ Support/Raycast/Scripts/myspeak-toggle.sh
```

---

## 사용법

### myspeak.app

**실행**:
- myspeak.app 더블클릭
- 로그인 항목에 추가했다면 자동 실행

**녹음 제어**:
- 단축키: `⌃⇧M` (Ctrl+Shift+M) - 기본값
- 메뉴바 🎤 아이콘 클릭 → "녹음 시작/중지"

**단축키 변경**:
- 메뉴바 아이콘 클릭
- "녹음 단축키 설정" 선택
- 원하는 단축키 선택

**종료**:
- 메뉴바 🎤 아이콘 클릭 → "종료"

### myspeaktoggle.app

**실행 방법**:
1. 더블클릭으로 직접 실행
2. 키보드 단축키로 실행 (시스템 설정에서 설정)
3. Alfred/Raycast workflow로 실행
4. Hammerspoon 스크립트로 실행
5. Stream Deck 버튼으로 실행

**동작**:
- 실행하면 즉시 녹음이 시작/중지됨
- 창이 뜨지 않고 백그라운드에서 동작
- myspeak.app이 실행 중이어야 함

---

## 문제 해결

### myspeak.app 실행 후 메뉴바 아이콘이 안 보임

**원인**: Python 앱이 제대로 시작되지 않음

**해결**:
1. 터미널에서 직접 실행해서 오류 확인:
   ```bash
   cd /Users/hanju/02hobby/mlx-whisper
   source venv/bin/activate
   python app.py
   ```

2. 오류 메시지 확인:
   - `ImportError`: 의존성 재설치 필요
   - `PermissionError`: 마이크 권한 확인

### ImportError: Failed to load metallib

**원인**: MLX 라이브러리 손상 (캐시 삭제 등)

**해결**:
```bash
cd /Users/hanju/02hobby/mlx-whisper
source venv/bin/activate
pip uninstall -y mlx mlx-metal mlx-whisper numba llvmlite
pip install mlx mlx-whisper numba llvmlite
```

### myspeaktoggle.app이 작동하지 않음

**확인 사항**:
1. myspeak.app이 실행 중인가?
   ```bash
   ps aux | grep "python app.py" | grep -v grep
   ```

2. 트리거 파일 생성 확인:
   ```bash
   touch /tmp/voice-toggle
   # 잠시 후
   ls /tmp/voice-toggle  # 파일이 사라져야 정상
   ```

3. 파일이 사라지지 않으면 myspeak.app 재시작

### 마이크 권한 오류

**macOS 설정**:
1. **시스템 설정** → **개인 정보 보호 및 보안**
2. **마이크** 선택
3. Python 또는 Terminal 앱 권한 허용

### 녹음이 안 됨 / 인식이 안 됨

**확인**:
1. 마이크가 제대로 연결되어 있는지
2. 시스템 환경설정 → 사운드 → 입력에서 마이크 선택
3. 입력 레벨이 너무 낮지 않은지
4. 터미널에서 직접 실행하여 오류 확인

### venv가 없거나 손상됨

**재생성**:
```bash
cd /Users/hanju/02hobby/mlx-whisper
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**requirements.txt가 없다면**:
```bash
pip install mlx mlx-whisper rumps pyaudio pyperclip pyautogui pynput
```

---

## 개발자 정보

### 파일 구조
```
mlx-whisper/
├── app.py                    # 메인 Python 앱
├── myspeak.applescript       # myspeak.app 복구용 스크립트
├── myspeak-trigger.sh        # myspeaktoggle.app 복구용 스크립트
├── venv/                     # Python 가상환경
├── APPS.md                   # 이 문서
└── prompt.md                 # 개발 기록
```

### 트리거 메커니즘

**app.py** (112-119줄):
```python
# 파일 트리거 체크 (0.05초마다 실행)
trigger_file = Path("/tmp/voice-toggle")
if trigger_file.exists():
    try:
        trigger_file.unlink()  # 파일 삭제
    except Exception:
        pass
    self._toggle_event.set()   # 녹음 토글 이벤트 발생
```

### 내부 단축키 시스템

app.py는 pynput을 사용한 글로벌 단축키를 지원합니다:
- 기본값: `ctrl+shift+m`
- 설정 파일: `~/.config/voice-recorder/config.json`
- 메뉴에서 변경 가능

---

## 참고 자료

- [MLX Whisper GitHub](https://github.com/ml-explore/mlx-examples/tree/main/whisper)
- [rumps 문서](https://github.com/jaredks/rumps)
- [macOS Automator 가이드](https://support.apple.com/guide/automator/welcome/mac)

---

**마지막 업데이트**: 2025-02-12
