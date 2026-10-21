#!/bin/sh
# Führt die AIOS-Modellfälle in der isolierten Testkonfiguration aus.
set -u
OUT="$1"; FAELLE="$2"
export CLAUDE_CONFIG_DIR="$HOME/aios-test.xgNSnI/.claude"
run_case() {
  id="$1"; prompt="$2"
  dir="$HOME/aios-test.xgNSnI/arbeitsordner/$id"; mkdir -p "$dir"
  ( cd "$dir" && claude -p "$prompt" --setting-sources user,project --output-format stream-json --verbose > "$OUT/$id.jsonl" 2> "$OUT/$id.err"; echo $? > "$OUT/$id.exit" ) &
}
run_case einstieg-auftrag "/auftrag-vorbereiten Plane einen einstündigen Lernblock für Python."
n=$(jq '.cases|length' "$FAELLE"); i=0
while [ $i -lt $n ]; do
  id=$(jq -r ".cases[$i].id" "$FAELLE"); skill=$(jq -r ".cases[$i].skill" "$FAELLE"); p=$(jq -r ".cases[$i].prompt" "$FAELLE")
  run_case "$id" "/$skill $p"; i=$((i+1))
done
wait
