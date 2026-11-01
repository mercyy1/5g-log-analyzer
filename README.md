# 📶 5G Log Analyzer

An interactive web app built with **Streamlit** to analyze and visualize 5G log files (`.log` or `.txt`). Easily detect packet latency spikes, parse error/warning patterns, and export structured results as a CSV.

---

## 🚀 Live Demo

👉 [Try it on Streamlit Cloud](https://5g-log-analyzer.streamlit.app/)

---

## 📂 Features

- ✅ Upload `.log` or `.txt` files
- ✅ Extract timestamp and RTT (Round Trip Time)
- ✅ Detect RTT spikes (default ≥ 100 ms, adjustable in the sidebar)
- ✅ Count packets, warnings, and errors
- ✅ Plot latency trends with spikes highlighted in red
- ✅ Export structured log data as CSV
- ✅ Highlight latency spikes in the table view

---

## 🖥️ Sample Log Format

```text
[10:00:01] Packet sent from Node A to Node B. RTT=18ms
[10:00:02] Packet received at Node B. RTT=20ms
[10:00:05] Warning: Latency spike. RTT=85ms
[10:00:08] Error: Timeout occurred. Code=408
```

Each line is labelled **Error**, **Warning**, **Packet** or **Info** (in that order of priority, so `Error: Packet dropped` counts as an error). Lines with an `RTT=<n>ms` value are added to the latency chart and table; RTT (round-trip time) is how long a packet takes to reach its destination and come back.


---

## 🔧 Technologies Used

- Python
- Streamlit
- Matplotlib
- Pandas
- Regex

---

## 📦 Install & Run Locally

```bash
git clone https://github.com/mercyy1/5g-log-analyzer.git
cd 5g-log-analyzer
pip install -r requirements.txt
streamlit run app.py
```

## 🧪 Tests

The parsing logic lives in `log_parser.py`, separate from the Streamlit UI in `app.py`, so it can be tested without a browser:

```bash
pip install pytest
pytest
```

## 🗂️ Project Structure

```text
app.py            Streamlit UI: upload, metrics, chart, table, CSV export
log_parser.py     Pure parsing: line classification, RTT extraction, spike check
tests/            pytest tests for the parser
sample.log        Small example log to try the app with
```
