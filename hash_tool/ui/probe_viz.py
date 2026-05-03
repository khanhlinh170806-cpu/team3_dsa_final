import streamlit as st


def render_probe_path(event):
    """
    Render the probe path of the last insert as step-by-step colored boxes.
    event: ProbeEvent from logger.py
    """
    if event is None:
        return

    st.markdown("#### Probe Path")

    path  = event.probe_path
    final = event.final_slot
    h1    = event.h1

    # Hash formula header
    st.markdown(
        f"<div style='font-family:monospace; font-size:14px; margin-bottom:10px'>"
        f"hash(<b>{event.key}</b>) = <b>{h1}</b>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Step boxes
    cols = st.columns(len(path))
    for i, (col, slot) in enumerate(zip(cols, path)):
        with col:
            is_final  = (slot == final)
            is_start  = (i == 0)

            if is_final and len(path) == 1:
                bg, label, icon, text_color = "#5DCAA5", "inserted", "✓", "#fff"
            elif is_final:
                bg, label, icon, text_color = "#5DCAA5", "inserted", "✓", "#fff"
            elif is_start:
                bg, label, icon, text_color = "#F09595", "collision", "✗", "#fff"
            else:
                bg, label, icon, text_color = "#FAC775", "skip", "→", "#5a3e00"

            arrow_html = (
                "<div style='text-align:center;font-size:18px;margin-top:6px'>→</div>"
                if not is_final else ""
            )

            st.markdown(
                f"""
                <div style="
                    background:{bg}; border-radius:8px; padding:10px 6px;
                    text-align:center; color:{text_color};
                    border:1px solid #ddd;
                ">
                    <div style="font-size:11px; opacity:0.85">step {i + 1}</div>
                    <div style="font-size:20px; font-weight:bold">slot {slot}</div>
                    <div style="font-size:11px; margin-top:4px">{icon} {label}</div>
                </div>
                {arrow_html}
                """,
                unsafe_allow_html=True,
            )

    # Result banner
    st.markdown("<div style='margin-top:12px'>", unsafe_allow_html=True)
    if event.is_collision:
        st.warning(
            f"⚠️ Collision detected! Key `{event.key}` required "
            f"**{event.steps} steps** to find an empty slot "
            f"(h1 = {h1} → final slot = {final})"
        )
    else:
        st.success(
            f"✅ No collision. Key `{event.key}` inserted directly at slot {final}."
        )
    st.markdown("</div>", unsafe_allow_html=True)


def render_probe_formula(strategy_name: str, key, h1: int, h2: int = None):
    """
    Display the probing formula currently being used.
    """
    st.markdown("**Probing formula:**")

    formulas = {
        "Chaining":          f"h(key) = hash({key}) mod m = {h1}  →  insert into chain at slot {h1}",
        "Linear Probing":    f"(h + i) mod m  =  ({h1} + i) mod m     i = 0, 1, 2, ...",
        "Quadratic Probing": f"(h + i²) mod m  =  ({h1} + i²) mod m   i = 0, 1, 2, ...",
        "Double Hashing":    f"(h1 + i × h2) mod m\nh1 = {h1},  h2 = {h2}  →  ({h1} + i × {h2}) mod m",
    }

    st.code(formulas.get(strategy_name, "Unknown strategy"), language="")