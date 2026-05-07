import streamlit as st
import time

COLORS = {
    "empty":     "#F1F0EA",
    "occupied":  "#B5D4F4",
    "deleted":   "#F7C1C1",
    "probe":     "#FAC775",
    "final":     "#5DCAA5",
    "collision": "#F09595",
    "current":   "#FF6B6B",  # slot đang được probe trong animation
}

def _slot_html(idx, content, color, border_color="#CCCCCC", glow=False):
    shadow = "0 0 8px 3px #FAC775" if glow else "none"
    return f"""
    <div style="
        background:{color}; border-radius:8px; padding:6px 3px;
        text-align:center; font-size:11px; min-height:64px;
        border: 2px solid {border_color};
        box-shadow: {shadow};
        transition: background 0.3s;
    ">
        <div style="font-size:10px;color:#888;margin-bottom:2px">[{idx}]</div>
        <div style="font-weight:600;font-size:12px;word-break:break-all">{content or "·"}</div>
    </div>
    """

def _get_slot_content(table, idx):
    slot = table[idx]
    if slot is None or str(slot) == "DELETED":
        return ""
    if isinstance(slot, list):  # Chaining
        return "<br>".join([f"{k}:{v}" for k, v in slot]) if slot else ""
    return f"{slot[0]}:{slot[1]}"  # Open addressing — hiện key:value

def render_grid(table, probe_path=None, final_slot=None, highlight_slot=None, size=11):
    """
    Render grid tĩnh (sau khi insert xong).
    highlight_slot: slot đang được animate (dùng trong animation loop)
    """
    probe_set = set(probe_path[:-1]) if probe_path else set()
    cols = st.columns(size)

    for idx, col in enumerate(cols):
        content = _get_slot_content(table, idx)
        slot = table[idx]
        is_empty = slot is None

        if highlight_slot == idx:
            color = COLORS["current"]
            border = "#E74C3C"
            glow = True
        elif probe_path and idx == final_slot:
            color = COLORS["final"]
            border = "#1D9E75"
            glow = False
        elif idx in probe_set:
            color = COLORS["collision"]
            border = "#E74C3C"
            glow = False
        elif is_empty:
            color = COLORS["empty"]
            border = "#CCCCCC"
            glow = False
        elif str(slot) == "DELETED":
            color = COLORS["deleted"]
            border = "#E74C3C"
            glow = False
        else:
            color = COLORS["occupied"]
            border = "#378ADD"
            glow = False

        col.markdown(
            _slot_html(idx, content, color, border, glow),
            unsafe_allow_html=True
        )


def animate_probe(table, probe_path, final_slot, size, delay=0.5):
    """
    Animate probe path từng bước dùng st.empty + time.sleep.
    Mỗi bước highlight slot đang được xét.
    """
    placeholder = st.empty()

    for step_idx, current_slot in enumerate(probe_path):
        is_last = (step_idx == len(probe_path) - 1)

        with placeholder.container():
            # Hiện grid với slot đang được probe
            render_grid(
                table,
                probe_path=probe_path[:step_idx + 1],
                final_slot=final_slot if is_last else None,
                highlight_slot=current_slot,
                size=size
            )

            # Caption mô tả bước hiện tại
            if is_last:
                st.success(f"✅ Bước {step_idx} → slot [{current_slot}] trống — INSERT thành công!")
            else:
                st.warning(f"⏳ Bước {step_idx} → slot [{current_slot}] đã có người — tiếp tục probe...")

        time.sleep(delay)

    # Frame cuối: grid hoàn chỉnh không có highlight
    with placeholder.container():
        render_grid(table, probe_path=probe_path, final_slot=final_slot, size=size)
        st.success(f"✅ Hoàn tất! Insert vào slot [{final_slot}] sau {len(probe_path)} bước.")