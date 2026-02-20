import streamlit as st
from PIL import Image, ImageDraw
import json
import os

import streamlit as st

st.markdown("""
<meta name="google-site-verification" content="VP_h96a1RKInZPnxtsMURIuxTDce8gaB4eB47lR9dPM" />
""", unsafe_allow_html=True)

# -------------------------
# Setup
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "flags.json"), "r", encoding="utf-8") as f:
    FLAGS = json.load(f)

# -------------------------
# Flag image loader
# -------------------------
def load_flag_image(path):
    full_path = os.path.join(BASE_DIR, path)
    try:
        img = Image.open(full_path).resize((80, 50))
    except FileNotFoundError:
        img = Image.new("RGB", (80, 50), color="gray")
        draw = ImageDraw.Draw(img)
        draw.text((5, 20), "No Img", fill="white")
    return img

# -------------------------
# Search function
# -------------------------
def search_flags(colours, patterns):
    results = []
    for flag in FLAGS:
        if colours and not all(c in flag["colours"] for c in colours):
            continue
        if patterns and not all(p in flag["patterns"] for p in patterns):
            continue
        results.append(flag)
    return results

# -------------------------
# Sidebar: Search controls
# -------------------------
st.sidebar.title("Flag Finder Controls")
col_input = st.sidebar.text_input("Colours (comma separated, check Help)", "")
pat_input = st.sidebar.text_input("Patterns (comma separated, check Help)", "")
search_btn = st.sidebar.button("Search")
reset_btn = st.sidebar.button("Reset")
help_btn = st.sidebar.button("Help")

# -------------------------
# Help modal
# -------------------------
if help_btn:
    st.sidebar.subheader("Help: Colours")
    unique_colours = sorted({c for f in FLAGS for c in f["colours"]})
    st.sidebar.write(", ".join(unique_colours))

    st.sidebar.subheader("Help: Patterns")
    unique_patterns = sorted({p for f in FLAGS for p in f["patterns"]})
    st.sidebar.write(", ".join(unique_patterns))

# -------------------------
# Process search
# -------------------------
if "results" not in st.session_state:
    st.session_state.results = FLAGS

if search_btn:
    cols = [c.strip().lower() for c in col_input.split(",") if c.strip()]
    pats = [p.strip().lower() for p in pat_input.split(",") if p.strip()]
    st.session_state.results = search_flags(cols, pats)

if reset_btn:
    st.session_state.results = FLAGS
    col_input = ""
    pat_input = ""

# -------------------------
# Display flags in grid
# -------------------------
flags = st.session_state.results
cols_per_row = 6  # adjust for width

for i in range(0, len(flags), cols_per_row):
    row_flags = flags[i:i+cols_per_row]
    cols = st.columns(len(row_flags))
    for col, flag in zip(cols, row_flags):
        img = load_flag_image(flag["file"])
        col.image(img)
        col.caption(flag["country"].capitalize())
