import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

WARN_THRESHOLD   = 0.70
DANGER_THRESHOLD = 0.85


def render_metrics(stats: dict):
    """
    Display load factor, collision count, and average probe length
    as metric cards. Show a warning banner when load factor is high.
    """
    alpha = stats["load_factor"]
    colls = stats["collision_count"]
    avg_p = stats["avg_probe_len"]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Load Factor  α = n/m",
            value=f"{alpha:.3f}",
            delta=_alpha_label(alpha),
            delta_color="inverse" if alpha >= DANGER_THRESHOLD else
                        "off"     if alpha >= WARN_THRESHOLD    else "normal",
            help="α = elements / table size. Keep α < 0.7 for good performance.",
        )

    with col2:
        st.metric(
            label="Total Collisions",
            value=colls,
            delta="none yet" if colls == 0 else f"{colls} collision(s)",
            delta_color="normal" if colls == 0 else "inverse",
            help="Number of inserts that encountered at least one occupied slot.",
        )

    with col3:
        st.metric(
            label="Avg Probe Length",
            value=f"{avg_p:.2f}",
            delta=_probe_label(avg_p),
            delta_color="inverse" if avg_p > 2.0 else "normal",
            help="Average steps per insert. Ideal ≈ 1.0",
        )

    # Warning banners
    if alpha >= DANGER_THRESHOLD:
        st.error(
            f"🚨 Load factor = {alpha:.2f} — Critical! "
            f"Performance is degrading severely. Consider rehashing (double the table size)."
        )
    elif alpha >= WARN_THRESHOLD:
        st.warning(
            f"⚠️ Load factor = {alpha:.2f} — Approaching danger zone (threshold: 0.7). "
            f"Collision rate will increase significantly from here."
        )


def render_load_factor_chart(current_alpha: float):
    """
    Plot theoretical expected probe length vs load factor for all strategies.
    Mark the current alpha with a vertical dashed line.
    """
    alphas = np.linspace(0.05, 0.95, 300)

    # Theoretical formulas (unsuccessful search)
    linear_theory   = 0.5 * (1 + 1 / (1 - alphas) ** 2)
    chaining_theory = 1 + alphas / 2
    double_theory   = 1 / (1 - alphas)

    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_alpha(0)
    ax.set_facecolor("#FAFAFA")

    ax.plot(alphas, linear_theory,   label="Linear Probing",   color="#E24B4A", linewidth=2)
    ax.plot(alphas, chaining_theory, label="Chaining",         color="#378ADD", linewidth=2)
    ax.plot(alphas, double_theory,   label="Double Hashing",   color="#1D9E75", linewidth=2, linestyle="--")

    ax.axvline(
        x=current_alpha,
        color="#BA7517", linewidth=2, linestyle=":",
        label=f"Current α = {current_alpha:.2f}",
    )
    ax.axvspan(0.70, 0.95, alpha=0.07, color="red", label="Danger zone (α > 0.7)")

    ax.set_xlabel("Load Factor α",            fontsize=11)
    ax.set_ylabel("Expected probe steps",     fontsize=11)
    ax.set_title("Load Factor vs Expected Probe Length (theoretical)", fontsize=12)
    ax.set_ylim(0, 15)
    ax.set_xlim(0.05, 0.95)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    st.pyplot(fig)
    plt.close(fig)


def render_comparison_table(results: dict):
    """
    Show a side-by-side comparison table after inserting the same keys
    into multiple strategies.
    results: { "Linear Probing": stats_dict, ... }
    """
    if not results:
        return

    rows = [
        {
            "Strategy":         strategy,
            "Load Factor α":    stats["load_factor"],
            "Collisions":       stats["collision_count"],
            "Avg Probe Length": stats["avg_probe_len"],
            "Total Ops":        stats["total_ops"],
        }
        for strategy, stats in results.items()
    ]

    df = pd.DataFrame(rows).set_index("Strategy")

    st.dataframe(
        df.style
          .highlight_min(subset=["Avg Probe Length", "Collisions"], color="#D5F5E3")
          .highlight_max(subset=["Avg Probe Length", "Collisions"], color="#FADBD8"),
        use_container_width=True,
    )

    best = df["Avg Probe Length"].idxmin()
    st.success(f"✅ Best performing strategy in this test: **{best}**")


# ── Helpers ────────────────────────────────────────────────────

def _alpha_label(alpha: float) -> str:
    if alpha < 0.5:  return "Good (< 0.5)"
    if alpha < 0.7:  return "Acceptable (0.5 – 0.7)"
    if alpha < 0.85: return "Warning (> 0.7)"
    return "Critical (> 0.85)"


def _probe_label(avg: float) -> str:
    if avg <= 1.2: return "Ideal"
    if avg <= 2.0: return "Acceptable"
    if avg <= 4.0: return "Degrading"
    return "Critical — rehash needed"