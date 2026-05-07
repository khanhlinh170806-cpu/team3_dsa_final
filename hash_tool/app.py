import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random
import string

from core.hash_table import (
    ChainingHashTable, LinearProbingHashTable,
    QuadraticProbingHashTable, DoubleHashingHashTable
)
from core.logger import LoggedHashTable
from ui.grid_viz import render_grid, animate_probe
from ui.probe_viz import render_formula_breakdown, render_probe_arrow
from ui.metrics import render_metrics, render_load_factor_chart, render_comparison_table

st.set_page_config(page_title="Hash Table Debugger", layout="wide")
st.title("🔍 Hash Table Debugging & Visualization Tool")

strategy_map = {
    "Chaining":          ChainingHashTable,
    "Linear Probing":    LinearProbingHashTable,
    "Quadratic Probing": QuadraticProbingHashTable,
    "Double Hashing":    DoubleHashingHashTable,
}

# ── Sidebar ──────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")
    strategy   = st.selectbox("Strategy", list(strategy_map.keys()))
    table_size = st.slider("Table size (m)", 7, 23, 11, step=2)
    anim_speed = st.slider("Animation speed (giây/bước)", 0.2, 1.5, 0.5, step=0.1)

    st.divider()
    st.header("➕ Insert key")
    key_input   = st.text_input("Key (string hoặc int)")
    val_input   = st.text_input("Value", value="1")
    insert_btn  = st.button("Insert", type="primary")
    animate_btn = st.button("Insert + Animate probe")

    st.divider()
    if st.button("🗑️ Reset table"):
        for k in ["ht", "config", "last_event", "prev_stats"]:
            st.session_state.pop(k, None)
        st.rerun()

# ── Session state ─────────────────────────────────────────────────
if "ht" not in st.session_state or st.session_state.get("config") != (strategy, table_size):
    st.session_state.ht         = LoggedHashTable(strategy_map[strategy], size=table_size)
    st.session_state.config     = (strategy, table_size)
    st.session_state.last_event = None
    st.session_state.prev_stats = None

ht = st.session_state.ht

# ── Handle insert ─────────────────────────────────────────────────
do_animate = False

if (insert_btn or animate_btn) and key_input:
    st.session_state.prev_stats = ht.get_stats()
    event = ht.insert(key_input, val_input)
    st.session_state.last_event = event
    do_animate = animate_btn

# ── Tabs ──────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🔬 Single Mode", "⚖️ Compare Strategies", "🐛 Debug Mode"])

# ═══════════════════════════════════════════════════════
# TAB 1 — Single Mode
# ═══════════════════════════════════════════════════════
with tab1:
    # Metrics
    render_metrics(ht.get_stats(), st.session_state.get("prev_stats"))

    st.subheader("Hash Table State")
    last = st.session_state.last_event

    # Animation hoặc grid tĩnh
    if do_animate and last and len(last.probe_path) > 0:
        st.info("▶️ Đang animate probe path...")
        animate_probe(ht.table, last.probe_path, last.final_slot, table_size, delay=anim_speed)
    else:
        render_grid(
            ht.table,
            probe_path=last.probe_path if last else None,
            final_slot=last.final_slot if last else None,
            size=table_size
        )

    # Probe path arrow + công thức
    if last:
        st.subheader("Tại sao key này vào slot đó?")
        render_probe_arrow(last)
        render_formula_breakdown(last, strategy, table_size)

    # Load factor chart
    st.subheader("Load Factor Chart")
    render_load_factor_chart(ht.load_factor)

    # Event log
    with st.expander("📋 Event log"):
        if not ht.events:
            st.write("Chưa có thao tác nào.")
        for e in reversed(ht.events[-15:]):
            icon = "🔴" if e.is_collision else "🟢"
            st.write(
                f"{icon} `{e.operation}` | key=`{e.key}` | "
                f"h1={e.h1} | steps={e.steps} | "
                f"path={e.probe_path}"
            )

# ═══════════════════════════════════════════════════════
# TAB 2 — Compare Strategies
# ═══════════════════════════════════════════════════════
with tab2:
    st.subheader("Insert cùng 1 bộ key vào 4 strategy")
    demo_keys = st.text_area("Keys (mỗi dòng 1 key)", "alice\nbob\ncarol\ndave\neve\nfrank\ngreg")

    if st.button("▶ Run comparison"):
        keys = [k.strip() for k in demo_keys.split("\n") if k.strip()]
        results = {}
        for name, cls in strategy_map.items():
            logged = LoggedHashTable(cls, size=table_size)
            for k in keys:
                logged.insert(k, 1)
            results[name] = logged.get_stats()

        render_comparison_table(results)

        # Chart collision count per strategy
        fig, axes = plt.subplots(1, 2, figsize=(10, 3))
        names = list(results.keys())

        axes[0].bar(names, [results[n]["collision_count"] for n in names],
                    color=["#E24B4A","#378ADD","#BA7517","#1D9E75"])
        axes[0].set_title("Số collision")
        axes[0].set_ylabel("count")
        axes[0].tick_params(axis='x', rotation=15)

        axes[1].bar(names, [results[n]["avg_probe_len"] for n in names],
                    color=["#E24B4A","#378ADD","#BA7517","#1D9E75"])
        axes[1].set_title("Avg probe length")
        axes[1].set_ylabel("steps")
        axes[1].tick_params(axis='x', rotation=15)

        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

# ═══════════════════════════════════════════════════════
# TAB 3 — Debug Mode (engineer-focused)
# ═══════════════════════════════════════════════════════
with tab3:
    st.subheader("🐛 Debug Mode — Phát hiện bottleneck tự động")
    st.caption("Bulk insert nhiều key, tool tự chẩn đoán vấn đề performance.")

    col_a, col_b = st.columns(2)
    with col_a:
        n_keys   = st.slider("Số key", 5, 20, 8)
        key_type = st.selectbox("Loại key", [
            "Random strings",
            "Integers gây clustering (× table_size)",
            "Sequential integers",
        ])
    with col_b:
        debug_strategy = st.selectbox("Strategy để debug", list(strategy_map.keys()), key="dbg_strategy")
        debug_size     = st.slider("Table size", 7, 23, 11, step=2, key="dbg_size")

    if st.button("▶ Run Debug"):
        # Sinh keys
        if key_type == "Random strings":
            keys = [''.join(random.choices(string.ascii_lowercase, k=4)) for _ in range(n_keys)]
        elif key_type == "Integers gây clustering (× table_size)":
            keys = [str(i * debug_size) for i in range(n_keys)]  # tất cả hash về 0
        else:
            keys = [str(i) for i in range(n_keys)]

        # Insert
        debug_ht = LoggedHashTable(strategy_map[debug_strategy], size=debug_size)
        for k in keys:
            debug_ht.insert(k, 1)

        stats = debug_ht.get_stats()

        # Grid
        st.markdown("**Trạng thái bảng sau khi insert:**")
        render_grid(debug_ht.table, size=debug_size)

        # ── Chẩn đoán tự động ─────────────────────────────
        st.markdown("---")
        st.markdown("### 🩺 Chẩn đoán")

        issues = 0

        if stats["load_factor"] >= 0.7:
            st.error(f"🔴 **Load factor = {stats['load_factor']}** — vượt ngưỡng 0.7. "
                     f"Table đang quá đầy, performance O(1) không còn đảm bảo. "
                     f"→ Giải pháp: tăng table size hoặc rehash.")
            issues += 1
        else:
            st.success(f"🟢 Load factor = {stats['load_factor']} — ổn.")

        if stats["avg_probe_len"] > 3:
            st.error(f"🔴 **Avg probe length = {stats['avg_probe_len']}** — quá cao. "
                     f"Có dấu hiệu clustering nghiêm trọng.")
            issues += 1
        elif stats["avg_probe_len"] > 1.5:
            st.warning(f"🟡 **Avg probe length = {stats['avg_probe_len']}** — bắt đầu có clustering.")
            issues += 1
        else:
            st.success(f"🟢 Avg probe length = {stats['avg_probe_len']} — phân tán tốt.")

        collision_rate = stats["collision_count"] / max(stats["total_ops"], 1)
        if collision_rate > 0.5:
            st.error(f"🔴 **Collision rate = {collision_rate:.0%}** — hơn một nửa insert bị collision. "
                     f"→ Xem xét đổi hash function hoặc strategy.")
            issues += 1
        else:
            st.success(f"🟢 Collision rate = {collision_rate:.0%} — chấp nhận được.")

        if issues == 0:
            st.info("✅ Không phát hiện vấn đề nào với bộ key này.")

        # ── Probe path toàn bộ ────────────────────────────
        st.markdown("---")
        st.markdown("### 📋 Probe path toàn bộ")
        for e in debug_ht.events:
            path_str = " → ".join([
                f"**[{s}]✓**" if s == e.final_slot else f"[{s}]"
                for s in e.probe_path
            ])
            icon = "🔴" if e.is_collision else "🟢"
            st.markdown(
                f"{icon} key=`{e.key}` | h1={e.h1} | "
                f"{path_str} | **{e.steps} bước**"
            )

        # Chart probe length per key
        fig, ax = plt.subplots(figsize=(10, 3))
        colors = ["#E24B4A" if e.is_collision else "#1D9E75" for e in debug_ht.events]
        ax.bar([e.key for e in debug_ht.events],
               [e.steps for e in debug_ht.events], color=colors)
        ax.axhline(y=stats["avg_probe_len"], color="#378ADD", linestyle="--",
                   label=f"avg = {stats['avg_probe_len']}")
        ax.set_xlabel("Key")
        ax.set_ylabel("Probe steps")
        ax.set_title("Số bước probe cho từng key (đỏ = collision)")
        ax.tick_params(axis='x', rotation=30)
        ax.legend()
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)