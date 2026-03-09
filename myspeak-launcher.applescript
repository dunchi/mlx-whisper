-- myspeak.app AppleScript Launcher
-- 터미널 없이 백그라운드에서 음성 인식 앱 실행

on run {input, parameters}
  do shell script "cd /Users/hanju/02hobby/mlx-whisper && /Users/hanju/02hobby/mlx-whisper/venv/bin/python app.py > /dev/null 2>&1 &"
  return input
end run
