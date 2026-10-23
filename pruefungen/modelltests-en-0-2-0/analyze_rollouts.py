#!/usr/bin/env python3
"""Read the stored Codex rollouts of the test home and show the native review trace per case."""
import json, sys
from pathlib import Path

state = json.loads((Path(__file__).parent / "run-state.json").read_text())
sessions = Path(state["root"]) / "home/.codex/sessions"
threads = {}
for path in sorted(sessions.rglob("rollout-*.jsonl")):
    rows = [json.loads(line) for line in path.open()]
    meta = rows[0]["payload"]
    threads[meta["id"]] = {"meta": meta, "rows": rows, "file": path.name}

report = {}
for tid, t in threads.items():
    meta = t["meta"]
    if meta.get("parent_thread_id"):
        continue
    case = Path(meta["cwd"]).name
    entry = {"thread": tid, "spawns": [], "child_results_delivered": [], "final": None}
    for row in t["rows"]:
        p = row.get("payload", {})
        if row.get("type") == "response_item" and p.get("type") == "function_call" and p.get("name") == "spawn_agent":
            args = json.loads(p["arguments"])
            entry["spawns"].append({"task_name": args.get("task_name"), "fork_turns": args.get("fork_turns"),
                                    "message_encrypted": str(args.get("message", "")).startswith("gAAAA")})
        if row.get("type") == "response_item" and p.get("type") == "function_call_output" and "task_name" in str(p.get("output")):
            entry["spawns"].append({"spawn_output": p["output"]})
        if row.get("type") == "response_item" and p.get("type") == "agent_message" and p.get("recipient") == "/root":
            text = " ".join(c.get("text", "") for c in p["content"] if c.get("type") == "input_text")
            entry["child_results_delivered"].append(text[:400])
        if row.get("type") == "event_msg" and p.get("type") == "task_complete" and p.get("turn_id") == p.get("root_turn_id"):
            entry["final"] = (p.get("last_agent_message") or "")
    children = [c for c in threads.values() if c["meta"].get("parent_thread_id") == tid]
    entry["child_threads"] = []
    for c in children:
        last = None
        for row in c["rows"]:
            p = row.get("payload", {})
            if row.get("type") == "event_msg" and p.get("type") == "task_complete":
                last = p.get("last_agent_message")
        entry["child_threads"].append({"thread": c["meta"]["id"], "forked_from": c["meta"].get("forked_from_id"), "final": (last or "")[:400]})
    report[case] = entry
json.dump(report, sys.stdout, ensure_ascii=False, indent=1)
