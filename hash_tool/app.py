import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from core.hash_table import (
    ChainingHashTable, LinearProbingHashTable,
    QuadraticProbingHashTable, DoubleHashingHashTable
)
from core.logger import LoggedHashTable
from ui.grid_viz import render_grid

st.set_page_config(page_title="Hash Table Debugger", layout="wide")
st.title("Hash Table Debugging Tool")

# --- Sidebar ---
with st.sidebar:
    st.header("Configuration")
    strategy = st.selectbox("Strategy",
        ["Chaining", "Linear Probing", "Quadratic Probing", "Double Hashing"])  # ✅ fix 1
    table_size = st.slider("Table size (m)", 7, 23, 11, step=2)

    st.divider()
    st.header("Insert key")
    key_input = st.text_input("Key (string hoặc int)")
    val_input = st.text_input("Value", value="1")
    insert_btn = st.button("Insert", type="primary")

# --- Strategy map ---
strategy_map = {
    "Chaining": ChainingHashTable,
    "Linear Probing": LinearProbingHashTable,
    "Quadratic Probing": QuadraticProbingHashTable,
    "Double Hashing": DoubleHashingHashTable,
}

# --- Session state ---
if "ht" not in st.session_state or st.session_state.get("config") != (strategy, table_size):
    st.session_state.ht = LoggedHashTable(strategy_map[strategy], size=table_size)
    st.session_state.config = (strategy, table_size)
    st.session_state.last_event = None

ht = st.session_state.ht

# --- Handle insert ---
if insert_btn and key_input:
    event = ht.insert(key_input, val_input)
    st.session_state.last_event = event

# --- Tabs ---
tab1, tab2 = st.tabs(["Single Mode", "Compare Strategies"])

with tab1:
    # Metrics
    col1, col2, col3 = st.columns(3)
    stats = ht.get_stats()
    col1.metric("Load Factor α", stats["load_factor"])
    col2.metric("Collisions", stats["collision_count"])
    col3.metric("Avg probe length", stats["avg_probe_len"])

    # Grid
    st.subheader("Hash Table State")
    last = st.session_state.last_event
    render_grid(
        ht.table,
        probe_path=last.probe_path if last else None,
        final_slot=last.final_slot if last else None,
        size=table_size
    )

    # Probe path details
    if last:
        st.subheader("Last operation")
        st.write(f"Key: `{last.key}` → h1 = `{last.h1}`")
        path_str = " → ".join([
            f"**{s}** ✓" if s == last.final_slot else str(s)
            for s in last.probe_path
        ])
        st.markdown(f"Probe path: {path_str}")
        if last.is_collision:
            st.warning(f"Collision! Needed {last.steps} steps to insert.")

    # Event log
    with st.expander("Event log"):
        for e in reversed(ht.events[-10:]):
            st.write(f"`{e.operation}` key=`{e.key}` | h1={e.h1} | steps={e.steps} | {'COLLISION' if e.is_collision else 'ok'}")

    # Load factor chart  ✅ fix 2: gọi thẳng, không bọc trong def
    st.subheader("Load Factor Chart")
    alphas = np.linspace(0.1, 0.95, 50)
    linear_expected   = 0.5 * (1 + 1 / (1 - alphas) ** 2)
    chaining_expected = 1 + alphas / 2

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(alphas, linear_expected,   label="Linear Probing (theory)", color="#E24B4A")
    ax.plot(alphas, chaining_expected, label="Chaining (theory)",       color="#378ADD")
    ax.axvline(x=ht.load_factor, color="#1D9E75", linestyle="--",
               label=f"Current α = {ht.load_factor:.2f}")
    ax.set_xlabel("Load Factor α")
    ax.set_ylabel("Expected probes")
    ax.legend()
    ax.set_ylim(0, 15)
    st.pyplot(fig)
    plt.close(fig)  # tránh memory leak khi rerun nhiều lần

with tab2:
    st.subheader("Insert cùng 1 bộ key vào 4 strategy")
    demo_keys = st.text_area("Keys (mỗi dòng 1 key)", "alice\nbob\ncarol\ndave\neve")

    if st.button("Run comparison"):
        keys = [k.strip() for k in demo_keys.split("\n") if k.strip()]

        results = {}
        for name, cls in strategy_map.items():
            logged = LoggedHashTable(cls, size=table_size)
            for k in keys:
                logged.insert(k, 1)
            results[name] = logged.get_stats()

        df = pd.DataFrame(results).T
        st.dataframe(df)