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

### 사용 방법
1. myspeak.app 더블클릭으로 실행
2. 메뉴바 🎤 아이콘으로 제어
3. 종료는 메뉴바 아이콘 → "종료" 선택

### myspeak-trigger (외부 녹음 토글)
앱 내부 단축키(ctrl+shift+m) 외에도 외부에서 녹음을 제어할 수 있는 트리거입니다.

**작동 원리**:
- `/tmp/voice-toggle` 파일을 생성
- 메인 앱이 0.05초마다 파일 존재 체크
- 파일이 있으면 녹음 토글 실행 후 파일 삭제

**사용 예시**:
- Automator 앱으로 생성 (Run Shell Script 액션)
- Alfred/Raycast workflow에서 실행
- 시스템 키보드 단축키 할당
- Stream Deck 버튼으로 실행

**파일**: `myspeak-trigger.sh`
