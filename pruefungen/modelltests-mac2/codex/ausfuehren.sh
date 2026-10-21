#!/bin/sh
# Führt die AIOS-Modellfälle in der isolierten Codex-Testumgebung aus.
set -u
OUT="$1"; FAELLE="$2"; T="$HOME/aios-test-codex"
run_case() {
  id="$1"; prompt="$2"; dir="$T/arbeitsordner/$id"; mkdir -p "$dir"
  ( HOME="$T" CODEX_HOME="$T/.codex" codex exec --skip-git-repo-check -s read-only -C "$dir" --json "$prompt" < /dev/null > "$OUT/$id.jsonl" 2> "$OUT/$id.err"; echo $? > "$OUT/$id.exit" ) &
}
run_case einstieg-auftrag "\$auftrag-vorbereiten Plane einen einstündigen Lernblock für Python."
n=$(jq '.cases|length' "$FAELLE"); i=0
while [ $i -lt $n ]; do
  id=$(jq -r ".cases[$i].id" "$FAELLE"); skill=$(jq -r ".cases[$i].skill" "$FAELLE"); p=$(jq -r ".cases[$i].prompt" "$FAELLE")
  run_case "$id" "\$$skill $p"; i=$((i+1))
done
wait
