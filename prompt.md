# 개발 기록

## 2025-02-12: myspeak.app 개선 및 의존성 문제 해결

### 문제 발생
- 캐시 삭제 후 MLX 라이브러리 ImportError 발생
- `Failed to load the default metallib` 오류
- `llvmlite.dylib` 파일을 찾을 수 없음

### 해결 방법
1. **MLX 재설치**
   - `mlx`, `mlx-metal` 제거 후 재설치 (0.30.6 → 0.31.0)

2. **llvmlite/numba 재설치**
   - `numba`, `llvmlite` 제거 후 재설치
   - 손상된 `.dylib` 파일 복구

### myspeak.app 개선
**이전**: Terminal 앱을 열어서 실행
- 터미널 창이 화면에 표시됨
- 터미널을 닫으면 앱도 종료됨

**변경 후**: 백그라운드 실행
- `do shell script`로 직접 실행
- venv Python 경로 직접 지정
- 출력을 `/dev/null`로 리다이렉트
- 터미널 없이 깔끔하게 실행

**AppleScript 변경**:
```applescript
on run {input, parameters}
  do shell script "cd /Users/hanju/02hobby/mlx-whisper && /Users/hanju/02hobby/mlx-whisper/venv/bin/python app.py > /dev/null 2>&1 &"
  return input
end run
```

### 클립보드 복사/붙여넣기 문제 해결 (추가 작업)

재부팅 후 테스트 중 발견된 문제:
- 녹음은 되지만 클립보드 복사 및 자동 붙여넣기가 작동하지 않음
- 🎤 → 🔴 → ⏳ → 🎤 아이콘 전환은 정상

#### 원인 1: ffmpeg PATH 문제
**문제**:
- mlx-whisper는 오디오 처리를 위해 ffmpeg 필요
- Automator 환경에서는 `/opt/homebrew/bin`이 기본 PATH에 없음
- ffmpeg를 찾지 못해 전사 실패: `FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'`

**해결**:
- AppleScript에 `export PATH=/opt/homebrew/bin:$PATH` 추가
- 터미널에서는 PATH에 homebrew가 포함되어 있어 문제 없었으나, Automator는 최소 PATH만 사용

#### 원인 2: 접근성 권한
**문제**:
- pyautogui가 키보드 입력(Cmd+V)을 하려면 접근성 권한 필요
- Python.app이 아닌 **myspeak.app에 접근성 권한** 필요

**해결**:
- 시스템 설정 → 개인 정보 보호 및 보안 → 접근성
- myspeak.app 추가 및 권한 허용

#### 디버깅 과정
1. 디버그 로그 추가 (`print` 문)
2. 출력을 `/dev/null` 대신 `/tmp/myspeak.log`로 변경
3. 로그에서 `FileNotFoundError: 'ffmpeg'` 발견
4. PATH 추가 후 해결

**최종 AppleScript**:
```applescript
on run {input, parameters}
  do shell script "export PATH=/opt/homebrew/bin:$PATH && cd /Users/hanju/02hobby/mlx-whisper && /Users/hanju/02hobby/mlx-whisper/venv/bin/python app.py > /dev/null 2>&1 &"
  return input
end run
```

### 앱 재생성 및 사용 방법
**상세한 가이드는 [APPS.md](./APPS.md)를 참조하세요.**

APPS.md에 포함된 내용:
- myspeak.app 재생성 방법 (Automator 단계별 가이드)
- myspeaktoggle.app 재생성 방법
- 로그인 시 자동 실행 설정
- 키보드 단축키 설정
- Alfred/Raycast 연동 방법
- ffmpeg PATH 문제 및 접근성 권한 해결 방법 (상세)
- 문제 해결 가이드
- 사용법 및 팁
