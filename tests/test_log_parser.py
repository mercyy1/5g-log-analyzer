from pathlib import Path

from log_parser import classify, decode_lines, is_spike, parse_log

SAMPLE = Path(__file__).resolve().parent.parent / "sample.log"


def test_sample_log_counts():
    summary = parse_log(decode_lines(SAMPLE.read_bytes()))
    assert summary.total_lines == 5
    assert summary.errors == 1
    assert summary.warnings == 1
    assert summary.packets == 3
    assert summary.latencies == [18, 20, 22, 85]


def test_rows_keep_timestamp_type_and_message():
    row = parse_log(["[10:00:05] Warning: Latency spike. RTT=85ms"]).rows[0]
    assert row == {"timestamp": "10:00:05", "rtt": 85, "type": "Warning",
                   "message": "Warning: Latency spike. RTT=85ms"}


def test_error_mentioning_packet_counts_as_error_not_packet():
    assert classify("[10:00:03] Error: Packet dropped. Code=504") == "Error"


def test_decimal_and_spaced_rtt_values():
    rows = parse_log(["[09:15:00] Packet sent. RTT=12.5 ms", "[09:15:01] Packet sent. rtt=7ms"]).rows
    assert [r["rtt"] for r in rows] == [12.5, 7]


def test_lines_without_rtt_are_counted_but_not_tabled():
    summary = parse_log(["[10:00:08] Error: Timeout occurred. Code=408"])
    assert summary.errors == 1
    assert summary.rows == []


def test_invalid_utf8_does_not_crash():
    assert decode_lines(b"[10:00:01] Packet ok RTT=5ms\n\xff\xfe junk\n") == [
        "[10:00:01] Packet ok RTT=5ms", "�� junk"]


def test_spike_threshold():
    assert is_spike(100) and not is_spike(99)
    assert is_spike(60, threshold_ms=50)
