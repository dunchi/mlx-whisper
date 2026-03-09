#!/bin/bash
# myspeak 녹음 토글 트리거
# 이 스크립트는 /tmp/voice-toggle 파일을 생성하여 메인 앱에 녹음 시작/중지 신호를 보냅니다.
#
# 사용 방법:
# - Automator로 앱 생성 (Run Shell Script 액션)
# - Alfred/Raycast workflow
# - 키보드 단축키 할당
# - Stream Deck 버튼

touch /tmp/voice-toggle
