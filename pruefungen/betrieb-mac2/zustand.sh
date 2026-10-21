#!/bin/sh
# Hält Marker-Hashes, geschützte Profildateien und AIOS-Einbindungen eines Test-Homes fest.
TH="$1"; cd "$TH" || exit 1
echo "## Marker und geschützte Dateien (SHA256)"
for f in .claude/skills/fremder-testskill/SKILL.md .agents/skills/fremder-testskill/SKILL.md aios-profile/marker.txt aios-output/marker.txt aios-runtime/fremd-marker.txt aios-profile/profil.md aios-profile/pfade.json aios-profile/projekte.md aios-profile/.env aios-profile/wissen/INDEX.md; do
  if [ -e "$f" ]; then echo "$(shasum -a 256 "$f" | cut -c1-16)  $f"; else echo "FEHLT             $f"; fi
done
echo "## Skillverknüpfungen in .claude/skills: $(find .claude/skills -maxdepth 1 -type l | wc -l | tr -d ' ')"
echo "## Regeldatei .claude/CLAUDE.md: $( [ -f .claude/CLAUDE.md ] && shasum -a 256 .claude/CLAUDE.md | cut -c1-16 || echo fehlt)"
echo "## Runtime-Dateien: $(find aios-runtime -type f | wc -l | tr -d ' '), Version: $(python3 -c 'import json;print(json.load(open("aios-runtime/paket.json"))["version"])' 2>/dev/null || echo keine)"
