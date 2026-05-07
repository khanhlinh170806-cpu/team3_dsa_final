import streamlit as st

def render_formula_breakdown(event, strategy: str, table_size: int):
    st.markdown("#### 🔢 Công thức từng bước")

    st.markdown("**① Hash ban đầu:**")

    # ✅ fix: detect int key để hiện công thức đúng
    try:
        int(event.key)
        h1_formula = f"{event.key} % {table_size}  =  {event.h1}"
    except (ValueError, TypeError):
        h1_formula = f'hash("{event.key}") % {table_size}  =  {event.h1}'

    st.code(h1_formula, language="")

    if len(event.probe_path) == 1:
        st.success(f"Slot [{event.h1}] trống → insert thẳng, không collision.")
        return

    st.markdown("**② Probe sequence (slot bị chiếm → tìm slot tiếp):**")

    # ✅ fix: detect int key cho h2
    h2 = None
    if strategy == "Double Hashing":
        try:
            int(event.key)
            h2 = 7 - (int(event.key) % 7)
            st.code(f"h2({event.key}) = 7 - ({event.key} % 7)  =  {h2}", language="")
        except (ValueError, TypeError):
            h2 = 7 - (hash(event.key) % 7)
            st.code(f'h2("{event.key}") = 7 - (hash("{event.key}") % 7)  =  {h2}', language="")

    rows = []
    for i, slot in enumerate(event.probe_path):
        is_final = (slot == event.final_slot)
        status = "✅ trống → INSERT" if is_final else "❌ occupied"

        if strategy == "Linear Probing":
            formula = f"({event.h1} + {i}) % {table_size}  =  {slot}"
        elif strategy == "Quadratic Probing":
            formula = f"({event.h1} + {i}²) % {table_size}  =  ({event.h1} + {i*i}) % {table_size}  =  {slot}"
        elif strategy == "Double Hashing":
            formula = f"({event.h1} + {i} × {h2}) % {table_size}  =  {slot}"
        else:  # Chaining
            formula = f"hash → bucket [{slot}]"

        rows.append(f"  i={i}:  {formula}   {status}")

    st.code("\n".join(rows), language="")


def render_probe_arrow(event):
    steps = []
    for i, slot in enumerate(event.probe_path):
        is_final = (slot == event.final_slot)
        if is_final:
            steps.append(
                f"<span style='background:#5DCAA5;color:white;padding:3px 10px;"
                f"border-radius:6px;font-weight:bold'>[{slot}] ✓</span>"
            )
        elif i == 0:
            steps.append(
                f"<span style='background:#F09595;color:white;padding:3px 10px;"
                f"border-radius:6px'>[{slot}] collision</span>"
            )
        else:
            steps.append(
                f"<span style='background:#FAC775;color:#333;padding:3px 10px;"
                f"border-radius:6px'>[{slot}] full</span>"
            )

    arrow = " &nbsp;→&nbsp; "
    st.markdown(
        f"<div style='margin:8px 0;line-height:2.6'>{arrow.join(steps)}</div>",
        unsafe_allow_html=True
    )