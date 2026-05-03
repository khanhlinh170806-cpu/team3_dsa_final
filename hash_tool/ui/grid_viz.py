import streamlit as st

COLORS = {
    "empty":    "#f1f0ea",
    "occupied": "#B5D4F4",
    "deleted":  "#F7C1C1",
    "probe":    "#FAC775",
    "final":    "#5DCAA5",
    "collision":"#F09595",
}

def render_grid(table, probe_path=None, final_slot=None, size=11):
    probe_set = set(probe_path[:-1]) if probe_path else set()
    
    cols = st.columns(size)
    for idx, col in enumerate(cols):
        with col:
            # xác định màu slot
            if probe_path and idx == final_slot:
                color = COLORS["final"]
            elif idx in probe_set:
                color = COLORS["probe"]
            elif table[idx] is None:
                color = COLORS["empty"]
            elif table[idx] == "DELETED":
                color = COLORS["deleted"]
            else:
                color = COLORS["occupied"]
            
            slot_content = ""
            if table[idx] and table[idx] != "DELETED":
                if isinstance(table[idx], list):   # Chaining
                    slot_content = "<br>".join([str(k) for k, v in table[idx]])
                else:
                    slot_content = str(table[idx][0])  # Open addressing
            
            st.markdown(f"""
            <div style="
                background:{color}; border-radius:6px; padding:8px 4px;
                text-align:center; font-size:12px; min-height:60px;
                border: 1px solid #ccc;
            ">
                <div style="font-size:10px;color:#888">[{idx}]</div>
                <div style="font-weight:500;margin-top:4px">{slot_content or "·"}</div>
            </div>
            """, unsafe_allow_html=True)