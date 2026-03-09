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
