#!/usr/bin/env python3
"""Lokale native Loaderprobe, ohne Anbieteraufruf oder persönliche Konfiguration."""

import argparse
from datetime import datetime, timezone
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading

from client_vorbereiten import prepare, source_contents, destination_path
from einrichten import write_private


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from strings(item)


def skill_listing(home):
    """Nur Metadaten, nie Skillinhalte oder Linkziele lesen."""
    result = subprocess.run(["/bin/ls", "-l", str(home / ".claude/skills"),
                             str(home / ".agents/skills")], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError("Skillverknüpfungen nicht vollständig lesbar, unveränderter Zustand nicht belegbar")
    return result.stdout


def sandbox_profile(root, actual_home, executables, port=None):
    quote = lambda value: json.dumps(str(value))
    # Clientprogramme unter dem echten Home brauchen ihre ausführbaren Bibliotheken.
    allowed = {Path(path).resolve() for path in executables}
    npm = actual_home / ".npm-global"
    if any(str(path).startswith(str(npm) + "/") for path in executables):
        package_libraries = npm / "lib/node_modules/@openai"
    else:
        package_libraries = None
    lines = ["(version 1)", "(allow default)", "(deny network*)",
             f"(deny file-read-data (subpath {quote(actual_home)}))",
             '(deny file-read-data (subpath "/Library/Keychains"))',
             '(deny mach-lookup (global-name "com.apple.securityd"))',
             "(deny file-write*)", f"(allow file-write* (subpath {quote(root)}))",
             '(allow file-write* (literal "/dev/null"))']
    for path in allowed:
        lines.append(f"(allow file-read-data (literal {quote(path)}))")
    if package_libraries is not None:
        lines.append(f"(allow file-read-data (subpath {quote(package_libraries)}))")
    lines.append(f"(allow file-read-data (subpath {quote(root)}))")
    if port is not None:
        lines.append(f'(allow network-outbound (remote ip "localhost:{port}"))')
    return "\n".join(lines)


def run(command, root, workspace, env, actual_home, port=None):
    policy = root / "isolation.sb"
    policy.write_text(sandbox_profile(root, actual_home, [command[0]], port), encoding="utf-8")
    try:
        return subprocess.run(["/usr/bin/sandbox-exec", "-f", str(policy), *command],
                              cwd=workspace, env=env, capture_output=True, text=True, timeout=45)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(command, 124, "", "Zeitlimit der isolierten Probe erreicht")


def environment(root):
    # Keine geerbten Tokens, Anbieter-URLs, Hooks oder persönlichen Einstellungen.
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LANG": "en_US.UTF-8",
           "HOME": str(root / "home"), "CODEX_HOME": str(root / "codex"),
           "CLAUDE_CONFIG_DIR": str(root / "claude"), "XDG_CONFIG_HOME": str(root / "xdg"),
           "TMPDIR": str(root / "temp"), "TERM": "dumb",
           "DISABLE_AUTOUPDATER": "1", "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
           "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1", "CLAUDE_CODE_AUTO_CONNECT_IDE": "0"}
    for key in ("HOME", "CODEX_HOME", "CLAUDE_CONFIG_DIR", "XDG_CONFIG_HOME", "TMPDIR"):
        Path(env[key]).mkdir(mode=0o700)
    return env


def codex_probe(binary, root, workspace, env, actual_home, core, prompt=None, expected_texts=None):
    command = [binary, "debug", "prompt-input", prompt or "Synthetische lokale Loaderprüfung. Keine Aktionen."]
    result = run(command, root, workspace, env, actual_home)
    try:
        text = "\n".join(strings(json.loads(result.stdout)))
    except json.JSONDecodeError:
        text = ""
    return {"client": "codex", "exit_code": result.returncode,
            "core_loaded": core in text, "prompt_json": bool(text),
            "text_checks": {key: value in text for key, value in (expected_texts or {}).items()},
            "error_excerpt": result.stderr[-600:] if result.returncode else "",
            "method": "debug prompt-input, OS-Netzwerk gesperrt, kein Modellaufruf"}


def codex_request_probe(binary, root, workspace, env, actual_home, core, prompt, expected_texts):
    """exec expandiert explizite Skills, der Debug-Dump allein tut dies nicht."""
    seen = []

    class Capture(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def do_POST(self):
            size = int(self.headers.get("Content-Length", "0"))
            if size > 2 * 1024 * 1024:
                self.send_error(413)
                return
            data = self.rfile.read(size)
            try:
                seen.append(json.loads(data))
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
            body = json.dumps({"error": {"type": "invalid_request_error",
                              "message": "AIOS_SYNTHETIC_LOADER_STOP"}}).encode()
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Capture)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_address[1]
    provider = ('model_providers.aios_test={name="AIOS local fixture",'
                f'base_url="http://127.0.0.1:{port}/v1",wire_api="responses",'
                'requires_openai_auth=false,supports_websockets=false,request_max_retries=0,stream_max_retries=0}')
    command = [binary, "exec", "--ignore-user-config", "--ephemeral", "--skip-git-repo-check",
               "--sandbox", "read-only", "--json", "-c", 'model_provider="aios_test"',
               "-c", provider, "-c", 'model="aios-local-test"', prompt]
    try:
        result = run(command, root, workspace, env, actual_home, port)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
    texts = ["\n".join(strings(body)) for body in seen]
    observed = "AIOS_SYNTHETIC_LOADER_STOP" in result.stdout + result.stderr
    return {"client": "codex", "exit_code": result.returncode,
            "core_loaded": any(core in text for text in texts), "captured_requests": len(seen),
            "text_checks": {key: any(value in text for text in texts) for key, value in expected_texts.items()},
            "synthetic_error_observed": observed,
            "error_excerpt": (result.stdout + result.stderr)[-800:] if not observed else "",
            "method": "codex exec bis lokalem Responses-Testserver, HTTP-400-Abbruch, kein Modellaufruf"}


def claude_probe(binary, root, workspace, env, actual_home, core, prompt=None, expected_texts=None,
                 setting_sources="project"):
    seen = []

    class Capture(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def do_POST(self):
            size = int(self.headers.get("Content-Length", "0"))
            if size > 2 * 1024 * 1024:
                self.send_error(413)
                return
            data = self.rfile.read(size)
            try:
                seen.append((self.path, json.loads(data)))
            except json.JSONDecodeError:
                pass
            body = json.dumps({"type": "error", "error": {"type": "invalid_request_error",
                              "message": "AIOS_SYNTHETIC_LOADER_STOP"}}).encode()
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Capture)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_address[1]
    local_env = {**env, "ANTHROPIC_API_KEY": "aios-synthetic-not-a-real-key",
                 "ANTHROPIC_BASE_URL": f"http://127.0.0.1:{port}", "API_TIMEOUT_MS": "10000"}
    command = [binary, "--print", "--setting-sources", setting_sources,
               "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
               "--settings", '{"disableAllHooks":true,"autoMemoryEnabled":false}',
               "--tools", "Skill" if expected_texts else "", "--no-session-persistence", "--output-format", "json",
               prompt or "Synthetische lokale Loaderprüfung. Keine Aktionen."]
    try:
        result = run(command, root, workspace, local_env, actual_home, port)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
    requests = [body for path, body in seen if path.split("?")[0] == "/v1/messages"]
    core_body = core.split("\n\n", 1)[1]
    texts = ["\n".join(strings(body)) for body in requests]
    loaded = any(core_body in text for text in texts)
    paragraphs = core_body.split("\n\n")
    return {"client": "claude-code", "exit_code": result.returncode,
            "core_loaded": loaded, "captured_message_requests": len(requests),
            "text_checks": {key: any(value in text for text in texts)
                            for key, value in (expected_texts or {}).items()},
            "core_paragraphs_loaded": sum(any(part in text for text in texts) for part in paragraphs),
            "core_paragraphs_total": len(paragraphs),
            "synthetic_error_observed": "AIOS_SYNTHETIC_LOADER_STOP" in result.stdout + result.stderr,
            "error_excerpt": (result.stdout + result.stderr)[-600:]
                if "AIOS_SYNTHETIC_LOADER_STOP" not in result.stdout + result.stderr else "",
            "method": "Native CLAUDE.md-Ladung bis lokalem HTTP-Testserver, absichtlicher HTTP-400-Abbruch, kein Modellaufruf"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client", choices=("codex", "claude", "beide"), default="beide")
    parser.add_argument("--codex", default=shutil.which("codex"))
    parser.add_argument("--claude", default=shutil.which("claude"))
    parser.add_argument("--evidence-dir", help="Optionaler neuer absoluter Ordner für JSON und ls-Belege")
    args = parser.parse_args(argv)
    if not Path("/usr/bin/sandbox-exec").is_file():
        parser.error("Diese isolierte Probe benötigt macOS sandbox-exec")
    actual_home = Path.home().resolve()
    evidence_dir = destination_path(args.evidence_dir) if args.evidence_dir else None
    before = skill_listing(actual_home)
    evidence = []
    with tempfile.TemporaryDirectory(prefix="aios-loader-") as temporary:
        root = Path(temporary).resolve()
        workspace = root / "workspace"
        prepare(workspace, source_contents())
        core = (workspace / "AGENTS.md").read_text(encoding="utf-8").strip()
        env = environment(root)
        for name, binary, probe in (("codex", args.codex, codex_probe), ("claude", args.claude, claude_probe)):
            if args.client not in (name, "beide"):
                continue
            if not binary:
                evidence.append({"client": name, "core_loaded": False, "reason": "Client fehlt"})
                continue
            version = run([binary, "--version"], root, workspace, env, actual_home)
            record = probe(binary, root, workspace, env, actual_home, core)
            record["version"] = version.stdout.strip()
            record["executable"] = binary
            rules = [workspace / filename for filename in ("AGENTS.md", "CLAUDE.md")]
            for rule in rules:
                rule.unlink()
            try:
                missing = probe(binary, root, workspace, env, actual_home, core)
            finally:
                for rule in rules:
                    rule.write_text(core + "\n", encoding="utf-8")
            record["negative_control"] = missing
            record["negative_control_passed"] = not missing["core_loaded"] and (
                missing.get("prompt_json", False) if name == "codex" else
                missing.get("captured_message_requests", 0) > 0 and missing["synthetic_error_observed"])
            evidence.append(record)
    after = skill_listing(actual_home)
    report = {"scope": "Loadernachweis, keine Modell-Verhaltensprüfung oder Dienstabnahme",
              "checked_at": datetime.now(timezone.utc).isoformat(),
              "generated_core_sha256": hashlib.sha256(core.encode()).hexdigest(),
              "clients": evidence, "skill_links_unchanged": before == after,
              "ls_before_sha256": hashlib.sha256(before.encode()).hexdigest(),
              "ls_after_sha256": hashlib.sha256(after.encode()).hexdigest()}
    if evidence_dir:
        destination_path(str(evidence_dir))
        evidence_dir.mkdir(mode=0o700)
        write_private(evidence_dir / "loader.json", json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        write_private(evidence_dir / "skills-vorher.ls.txt", before)
        write_private(evidence_dir / "skills-nachher.ls.txt", after)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if evidence and all(item["core_loaded"] and item.get("negative_control_passed")
                                and (item.get("synthetic_error_observed", True))
                                for item in evidence) and before == after else 1


if __name__ == "__main__":
    raise SystemExit(main())
