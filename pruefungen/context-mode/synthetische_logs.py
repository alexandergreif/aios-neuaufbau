"""Synthetischer Test. Liest keine Nutzerdaten und schreibt keine Dateien."""

import json


def make_log():
    special = {
        100: ("ERROR", "AIOS_SYNTH_ALPHA Verbindung verweigert", "service-a.py:41"),
        5000: ("ERROR", "AIOS_SYNTH_BETA Zeitlimit 30 Sekunden", "service-b.py:82"),
        6000: ("WARN", "Vorheriger ERROR wurde behoben", "service-c.py:19"),
        9999: ("ERROR", "AIOS_SYNTH_GAMMA Zugriff verweigert", "service-d.py:73"),
    }
    rows = []
    for n in range(1, 10001):
        level, message, location = special.get(n, ("INFO", "Routine erfolgreich", "worker.py:10"))
        rows.append(json.dumps(dict(line=n, level=level, message=message, location=location)))
    return "\n".join(rows)


def analyze(raw):
    errors = []
    count = 0
    for count, line in enumerate(raw.splitlines(), 1):
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Ungültiges JSON in Zeile {count}") from exc
        if record["level"] == "ERROR":
            errors.append(record)
    return dict(records=count, errors=errors)


def verify():
    raw = make_log()
    result = analyze(raw)
    assert result["records"] == 10000
    assert [r["line"] for r in result["errors"]] == [100, 5000, 9999]
    assert [r["location"] for r in result["errors"]] == ["service-a.py:41", "service-b.py:82", "service-d.py:73"]
    try:
        analyze(raw + "\nkein-json")
    except ValueError as exc:
        assert str(exc) == "Ungültiges JSON in Zeile 10001"
        failure = str(exc)
    else:
        raise AssertionError("Ungültige Eingabe blieb unerkannt")
    summary = json.dumps(result)
    return dict(raw_bytes=len(raw.encode()), summary_bytes=len(summary.encode()),
                result=result, failure_case=failure, checks="PASS")


if __name__ == "__main__":
    print(json.dumps(verify()))
