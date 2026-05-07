import streamlit as st
import matplotlib.pyplot as plt
import numpy as np


def render_metrics(stats: dict, prev_stats: dict = None):
    """
    3 chỉ số chính + delta so với lần trước.
    """
    col1, col2, col3 = st.columns(3)

    alpha = stats["load_factor"]
    delta_alpha = round(alpha - prev_stats["load_factor"], 3) if prev_stats else None

    col1.metric(
        "Load Factor α", f"{alpha:.3f}",
        delta=f"+{delta_alpha}" if delta_alpha else None,
        help="α = n/m. Vượt 0.7 → performance giảm rõ."
    )
    col2.metric(
        "Total Collisions", stats["collision_count"],
        delta=None,
        help="Số insert phải probe > 1 bước."
    )
    col3.metric(
        "Avg Probe Length", f"{stats['avg_probe_len']:.2f}",
        help="Trung bình số bước probe. Lý tưởng < 1.5"
    )

    if alpha >= 0.7:
        st.error(f"🔴 Load factor {alpha:.2f} — vượt ngưỡng 0.7! Nên tăng table size.")
    elif alpha >= 0.5:
        st.warning(f"🟡 Load factor {alpha:.2f} — theo dõi thêm.")


def render_load_factor_chart(current_alpha: float):
    alphas = np.linspace(0.01, 0.95, 200)

    linear_probes   = 0.5 * (1 + 1 / (1 - alphas) ** 2)
    chaining_probes = 1 + alphas / 2
    double_probes   = 1 / (1 - alphas)

    fig, ax = plt.subplots(figsize=(8, 3))
    fig.patch.set_alpha(0)

    ax.plot(alphas, linear_probes,   label="Linear Probing",  color="#E24B4A", linewidth=2)
    ax.plot(alphas, double_probes,   label="Double Hashing",  color="#378ADD", linewidth=2)
    ax.plot(alphas, chaining_probes, label="Chaining",        color="#1D9E75", linewidth=2)
    ax.axvline(x=current_alpha, color="#FAC775", linestyle="--", linewidth=2,
               label=f"Current α = {current_alpha:.2f}")
    ax.axvspan(0.7, 0.99, alpha=0.07, color="red")
    ax.text(0.72, 13, "Danger zone", color="red", fontsize=9)

    ax.set_xlabel("Load Factor α")
    ax.set_ylabel("Expected probes")
    ax.set_ylim(0, 15)
    ax.set_xlim(0, 1)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.25)
    st.pyplot(fig)
    plt.close(fig)


def render_comparison_table(results: dict):
    import pandas as pd
    df = pd.DataFrame(results).T
    df.index.name = "Strategy"
    df.columns = ["Load Factor α", "Collisions", "Total ops", "Avg Probe Length"]

    def highlight_best(col):
        if col.name in ["Collisions", "Avg Probe Length"]:
            return ["background-color:#D5F5E3" if v == col.min() else "" for v in col]
        return [""] * len(col)

    st.dataframe(df.style.apply(highlight_best).format(precision=3), use_container_width=True)