#!/bin/bash
# Reality Gap 로컬 일일 계산 + 커밋 (맥미니 — GHA runner IP 레이트리밋 우회)
# 플링크 크론: 매일 08:40 KST
set -u
cd /Users/mac/.openclaw/workspace/stockinsight

LOG=/tmp/reality_gap_local.log
echo "=== Reality Gap 로컬 런 $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG"

# 1) 최신 유지
git pull --rebase origin master >> "$LOG" 2>&1 || echo "pull 실패 (계속)" >> "$LOG"

# 2) 계산 (재시도 2회 — 각 시도 전 코드 최신화: 코드 fix 중 재시도 경쟁 방어)
RUN_OK=0
for i in 1 2; do
  echo "--- 시도 $i (코드 갱신 후) ---" >> "$LOG"
  git pull --rebase origin master >> "$LOG" 2>&1 || echo "재시도 전 pull 실패 (계속)" >> "$LOG"
  if python3 reality_gap.py >> "$LOG" 2>&1; then
    RUN_OK=1
    break
  fi
  echo "시도 $i 실패 — 120초 대기 후 재시도" >> "$LOG"
  sleep 120
done

if [ "$RUN_OK" -ne 1 ]; then
  echo "ERROR: 2회 시도 모두 실패 ($(date '+%H:%M'))" >> "$LOG"
  exit 1
fi

# 3) 종목수 검증
N=$(python3 -c "import json; print(json.load(open('static/reality_gap.json'))['total_stocks'])")
if [ "$N" -lt 30 ]; then
  echo "ERROR: 계산 종목 부족 ($N < 30)" >> "$LOG"
  exit 1
fi

# 4) 커밋+푸시 (재시도 3회)
for i in 1 2 3; do
  git add -f static/reality_gap.json
  git diff --staged --quiet && { echo "변경 없음 — 스킵" >> "$LOG"; exit 0; }
  git commit -m "Auto-update reality gap [local $(date -u '+%Y-%m-%d %H:%M UTC')]" >> "$LOG" 2>&1 || {
    echo "커밋 실패 (변경 이미 커밋됨?)" >> "$LOG"; exit 0; }
  if git push origin master >> "$LOG" 2>&1; then
    echo "SUCCESS: 총 $N종 푸시 완료 ($(date '+%H:%M'))" >> "$LOG"
    exit 0
  fi
  echo "push 시도 $i 실패 — 30초 대기 후 재시도" >> "$LOG"
  git pull --rebase origin master >> "$LOG" 2>&1
  sleep 30
done
echo "ERROR: push 3회 실패" >> "$LOG"
exit 1