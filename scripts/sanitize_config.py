#!/usr/bin/env python3
"""Redact secrets from Cisco running-config text files before publishing.

Usage:
    python3 sanitize_config.py input.txt output.txt
    python3 sanitize_config.py raw_configs_folder configs/hq

Redacts: user password hashes, enable secrets, NTP keys, IPsec pre-shared keys,
SNMP community strings, and licence serial numbers.
It only catches the patterns below, so ALWAYS review the output by hand
(search for: key, secret, password, community, sn).
"""
import pathlib
import re
import sys

RULES = [
    (r"(username \S+ (?:privilege \d+ )?secret \d )\S+", r"\1<REDACTED>"),
    (r"(username \S+ (?:privilege \d+ )?password(?: \d)? )\S+", r"\1<REDACTED>"),
    (r"(enable (?:secret|password)(?: \d)? )\S+", r"\1<REDACTED>"),
    (r"(^\s*password(?: \d)? )\S+", r"\1<REDACTED>"),
    (r"(ntp authentication-key \d+ md5 )\S+(?: \d)?", r"\1<REDACTED>"),
    (r"(crypto isakmp key )\S+( address \S+)", r"\1<PRE-SHARED-KEY>\2"),
    (r"(snmp-server community )\S+", r"\1<COMMUNITY>"),
    (r"(license udi pid \S+ sn )\S+", r"\1<SERIAL>"),
]


def sanitize(text: str) -> str:
    lines = []
    for line in text.splitlines():
        for pattern, repl in RULES:
            line = re.sub(pattern, repl, line)
        lines.append(line)
    return "\n".join(lines) + "\n"


def main() -> None:
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    if src.is_dir():
        dst.mkdir(parents=True, exist_ok=True)
        for f in sorted(src.iterdir()):
            if f.suffix.lower() in {".txt", ".cfg", ".conf"}:
                (dst / f.name).write_text(sanitize(f.read_text(encoding="utf-8", errors="replace")), encoding="utf-8")
                print("sanitized", f.name)
    else:
        dst.write_text(sanitize(src.read_text(encoding="utf-8", errors="replace")), encoding="utf-8")
        print("sanitized", src.name)


if __name__ == "__main__":
    main()
