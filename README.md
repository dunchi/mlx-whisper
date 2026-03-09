# MySpeak - MLX Whisper 음성 인식 앱

macOS 메뉴바에서 작동하는 음성 인식 앱입니다. Apple Silicon의 MLX를 활용하여 빠르고 정확한 실시간 음성 전사를 제공합니다.

## 특징

- 🎤 **메뉴바 통합**: 깔끔한 메뉴바 인터페이스
- ⌨️ **글로벌 단축키**: 어디서나 단축키로 녹음 제어
- 🚀 **빠른 전사**: Apple Silicon MLX 기반 고성능
- 📋 **자동 붙여넣기**: 인식된 텍스트를 자동으로 클립보드에 복사 및 붙여넣기
- 🔧 **커스터마이징**: 단축키, 언어 설정 가능
- 🎯 **외부 트리거**: Alfred, Raycast, Stream Deck 등과 연동 가능

## 시스템 요구사항

- macOS (Apple Silicon 권장)
- Python 3.9 이상
- 마이크 권한

## 빠른 시작

### 1. 환경 설정

```bash
# 저장소 클론
git clone https://github.com/dunchi/mlx-whisper.git
cd mlx-whisper

# 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install mlx mlx-whisper rumps pyaudio pyperclip pyautogui pynput
```

### 2. 직접 실행 (테스트)

```bash
python app.py
```

메뉴바에 🎤 아이콘이 나타나면 성공입니다.

### 3. Automator 앱 생성

편리한 실행을 위해 Automator 앱을 만드세요.

**상세한 가이드**: [APPS.md](./APPS.md)

## 사용법

### 기본 사용

1. **앱 실행**: myspeak.app 실행
2. **녹음 시작**: `⌃⇧M` (Ctrl+Shift+M) 또는 메뉴바 클릭
3. **녹음 중지**: 다시 `⌃⇧M` 또는 메뉴바 클릭
4. **결과**: 자동으로 클립보드에 복사 및 붙여넣기

### 단축키 커스터마이징

메뉴바 아이콘 → "녹음 단축키 설정"에서 변경 가능:
- `⌃⇧M` - Ctrl+Shift+M (기본값)
- `⌘⇧R` - Cmd+Shift+R
- `⌥Space` - Alt+Space
- `⌘⌥Space` - Cmd+Alt+Space
- `⌃⇧Space` - Ctrl+Shift+Space

### 외부 트리거 (고급)

myspeaktoggle.app을 사용하면 다양한 방법으로 녹음을 제어할 수 있습니다:
- Alfred/Raycast workflow
- 시스템 키보드 단축키
- Stream Deck 버튼
- Hammerspoon 스크립트

**상세 설정**: [APPS.md](./APPS.md#alfredraycast와-연동)

## 문서

- **[APPS.md](./APPS.md)**: 앱 재생성 및 상세 사용 가이드
- **[prompt.md](./prompt.md)**: 개발 기록 및 변경 이력

## 문제 해결

### 앱이 실행되지 않음

```bash
# 터미널에서 직접 실행하여 오류 확인
cd /path/to/mlx-whisper
source venv/bin/activate
python app.py
```

### ImportError: Failed to load metallib

```bash
# MLX 라이브러리 재설치
pip uninstall -y mlx mlx-metal mlx-whisper numba llvmlite
pip install mlx mlx-whisper numba llvmlite
```

### 마이크 권한 오류

**시스템 설정** → **개인 정보 보호 및 보안** → **마이크**에서 권한 허용

**더 많은 문제 해결**: [APPS.md](./APPS.md#문제-해결)

## 기술 스택

- **MLX**: Apple Silicon 최적화 머신러닝 프레임워크
- **Whisper**: OpenAI 음성 인식 모델
- **rumps**: macOS 메뉴바 앱 프레임워크
- **pynput**: 글로벌 단축키 처리
- **pyaudio**: 오디오 녹음

## 라이선스

이 프로젝트는 개인 사용을 위한 것입니다.

## 기여

버그 리포트나 개선 제안은 Issues에 등록해주세요.

## 참고 자료

- [MLX Whisper](https://github.com/ml-explore/mlx-examples/tree/main/whisper)
- [rumps Documentation](https://github.com/jaredks/rumps)
