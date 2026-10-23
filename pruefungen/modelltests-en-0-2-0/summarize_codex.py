#!/usr/bin/env python3
"""Extract observed events without grading the behavior automatically."""

from collections import Counter
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
results = []
totals = Counter()
for path in sorted((HERE / "raw").glob("*.jsonl")):
    records = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    meta_path = path.with_suffix(".meta.json")
    if not meta_path.exists():
        continue
    meta = json.loads(meta_path.read_text())
    messages = []
    commands = []
    collaboration = []
    usage = {}
    for record in records:
        item = record.get("item", {})
        if record.get("type") == "item.completed":
            if item.get("type") == "agent_message":
                messages.append(item["text"])
            elif item.get("type") == "command_execution":
                commands.append({k: item.get(k) for k in ("command", "exit_code", "status")})
            elif item.get("type") == "collab_tool_call":
                collaboration.append({k: item.get(k) for k in
                                      ("tool", "sender_thread_id", "receiver_thread_ids", "agents_states", "status")})
        if record.get("type") == "turn.completed":
            usage = record.get("usage", {})
    totals.update(usage)
    results.append({"id": path.stem, "exit_code": meta["exit_code"], "timed_out": meta["timed_out"],
                    "started_at": meta["started_at"], "finished_at": meta["finished_at"],
                    "workspace_files": meta["workspace_files"],
                    "active_integration_unchanged": meta["active_integration_unchanged"],
                    "raw_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "messages": messages, "commands": commands, "collaboration": collaboration, "usage": usage})
summary = {"scope": "Codex only. Observed events, not an automatic acceptance judgment.",
           "runs": results, "total_usage": dict(totals)}
destination = HERE / "observed.json"
with destination.open("x", encoding="utf-8") as handle:
    json.dump(summary, handle, ensure_ascii=False, indent=2)
    handle.write("\n")
print(json.dumps({"runs": len(results), "total_usage": dict(totals)}, ensure_ascii=False))
