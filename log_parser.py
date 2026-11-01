"""Parsing logic for 5G-style network logs, kept separate from the Streamlit UI so it can be tested."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

# Matches lines like: [10:00:01] Packet sent from Node A to Node B. RTT=18ms
RTT_PATTERN = re.compile(r"\[(\d{1,2}:\d{2}:\d{2})\].*?\bRTT=(\d+(?:\.\d+)?)\s*ms", re.IGNORECASE)
TIMESTAMP_PATTERN = re.compile(r"\[(\d{1,2}:\d{2}:\d{2})\]")

DEFAULT_SPIKE_MS = 100


@dataclass
class LogSummary:
    packets: int = 0
    errors: int = 0
    warnings: int = 0
    total_lines: int = 0
    rows: list[dict] = field(default_factory=list)  # one row per line that has an RTT

    @property
    def latencies(self) -> list[float]:
        return [r["rtt"] for r in self.rows]


def classify(line: str) -> str:
    """Label a line by severity. Errors win over warnings, which win over plain packets."""
    lower = line.lower()
    if "error" in lower:
        return "Error"
    if "warning" in lower:
        return "Warning"
    if "packet" in lower:
        return "Packet"
    return "Info"


def decode_lines(raw: bytes) -> list[str]:
    """Decode an uploaded file, tolerating stray non-UTF-8 bytes instead of crashing."""
    text = raw.decode("utf-8", errors="replace")
    return [line.strip() for line in text.splitlines() if line.strip()]


def parse_log(lines: list[str]) -> LogSummary:
    summary = LogSummary(total_lines=len(lines))

    for line in lines:
        kind = classify(line)
        if kind == "Error":
            summary.errors += 1
        elif kind == "Warning":
            summary.warnings += 1
        elif kind == "Packet":
            summary.packets += 1

        match = RTT_PATTERN.search(line)
        if match:
            rtt = float(match.group(2))
            summary.rows.append({
                "timestamp": match.group(1),
                "rtt": int(rtt) if rtt.is_integer() else rtt,
                "type": kind,
                "message": TIMESTAMP_PATTERN.sub("", line, count=1).strip(),
            })

    return summary


def is_spike(rtt: float, threshold_ms: float = DEFAULT_SPIKE_MS) -> bool:
    return rtt >= threshold_ms
