import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from log_parser import DEFAULT_SPIKE_MS, decode_lines, is_spike, parse_log

st.set_page_config(page_title="5G Log Analyzer", layout="centered")
st.title("📶 5G Log Analyzer")
st.markdown("Upload a 5G `.log` or `.txt` file to start analysis.")

spike_ms = st.sidebar.slider("Spike threshold (ms)", min_value=10, max_value=500,
                             value=DEFAULT_SPIKE_MS, step=10)

uploaded_file = st.file_uploader("Choose a log file", type=["log", "txt"])

if uploaded_file is None:
    st.info("Please upload a file to continue.")
    st.stop()

lines = decode_lines(uploaded_file.getvalue())
summary = parse_log(lines)

st.subheader("📄 Raw Log Preview")
st.text_area("Log Contents", "\n".join(lines[:20]), height=300)
st.success(f"Loaded {summary.total_lines} log lines.")

# === Metrics ===
st.subheader("📊 Log Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Packets", summary.packets)
col2.metric("Errors", summary.errors)
col3.metric("Warnings", summary.warnings)

if not summary.rows:
    st.warning("No RTT (latency) data found in this log.")
    st.stop()

df = pd.DataFrame(summary.rows)
df["spike"] = df["rtt"].apply(lambda r: is_spike(r, spike_ms))

# === Latency Stats ===
st.subheader("📈 Latency Stats")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Average RTT", f"{df['rtt'].mean():.1f} ms")
c2.metric("Max RTT", f"{df['rtt'].max()} ms")
c3.metric("Min RTT", f"{df['rtt'].min()} ms")
c4.metric("Spikes", int(df["spike"].sum()))

# === Latency Chart with Spikes Highlighted ===
st.subheader("📉 Latency Over Time")
fig, ax = plt.subplots()
ax.plot(range(len(df)), df["rtt"], linestyle="--", color="gray", alpha=0.5)
ax.scatter(range(len(df)), df["rtt"], color=["red" if s else "green" for s in df["spike"]])
ax.axhline(spike_ms, color="red", linewidth=0.8, alpha=0.4)

# Thin out x-axis labels so long logs stay readable.
step = max(1, len(df) // 10)
ax.set_xticks(range(0, len(df), step))
ax.set_xticklabels(df["timestamp"][::step], rotation=45, ha="right")
ax.set_xlabel("Timestamp")
ax.set_ylabel("RTT (ms)")
ax.set_title(f"Latency Trend (red = spike ≥ {spike_ms} ms)")
ax.grid(True)
fig.tight_layout()
st.pyplot(fig)

# === Data Table + CSV Export ===
st.subheader("🧾 Parsed Log Table")
st.dataframe(df.style.apply(
    lambda row: ["background-color: #ffcccc" if row["spike"] else ""] * len(row), axis=1))

st.download_button(
    label="📥 Download as CSV",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="parsed_log.csv",
    mime="text/csv",
)
