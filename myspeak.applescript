-- myspeak.app AppleScript Launcher
-- 터미널 없이 백그라운드에서 음성 인식 앱 실행
--
-- 중요: ffmpeg PATH 설정 필수
-- mlx-whisper는 오디오 처리를 위해 ffmpeg가 필요합니다.
-- Automator 환경에서는 /opt/homebrew/bin이 기본 PATH에 없으므로 명시적으로 추가해야 합니다.

on run {input, parameters}
  do shell script "export PATH=/opt/homebrew/bin:$PATH && cd /Users/hanju/02hobby/mlx-whisper && /Users/hanju/02hobby/mlx-whisper/venv/bin/python app.py > /dev/null 2>&1 &"
  return input
end run
