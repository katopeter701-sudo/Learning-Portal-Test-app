import streamlit as st
import pandas as pd
from supabase import create_client

# 1. DATABASE CONNECTION
PROJECT_ID = "uxtmgdenwfyuwhezcleh"
SUPABASE_URL = f"https://{PROJECT_ID}.supabase.co"
SUPABASE_KEY = "sb_publishable_1BIwMEH8FVDv7fFafz31uA_9FqAJr0-"

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception:
    st.error("Database Connection Failed. Check your Supabase credentials.")
    st.stop()

# 2. UI CONFIG & SELECTIVE STYLING
st.set_page_config(page_title="Flux Portal", layout="wide")
st.markdown("""
<style>
    /* Only the word 'Flux' gets Comic Sans */
    .flux-font {
        font-family: "Comic Sans MS", "Comic Sans", cursive, sans-serif;
        font-weight: bold;
        font-size: 1.2em;
    }
    /* Rest of the app remains standard font */
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; padding: 10px; color: #666; font-size: 14px; background: white; border-top: 1px solid #eee; z-index: 999; }
    .video-container { position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; background: #000; border-radius: 8px; margin-bottom: 10px; }
    .video-container iframe { position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0; }
</style>
""", unsafe_allow_html=True)

# 3. LOGIN PAGE LOGIC
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'><span class='flux-font'>Flux</span> Portal</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            st.subheader("Login Access")
            st.text_input("Username")
            st.text_input("Password", type="password")
            if st.button("Login", use_container_width=True) or st.button("Skip & Browse", use_container_width=True):
                st.session_state.logged_in = True
                st.rerun()
    st.stop()

# 4. SIDEBAR NAVIGATION
role = st.sidebar.radio("Navigation", ["Student Portal", "Admin Dashboard", "President Board"])

# --- ADMIN DASHBOARD (Password: flux) ---
if role == "Admin Dashboard":
    admin_pw = st.sidebar.text_input("Enter Admin Password", type="password")
    if admin_pw != "flux":
        st.warning("Locked. Please enter the correct password in the sidebar.")
        st.stop()

    st.header("Management Console")
    t1, t2, t3 = st.tabs(["Add Entry", "Bulk Upload", "Delete Content"])
    
    with t1:
        with st.form("manual"):
            p = st.text_input("Course Name")
            t = st.text_input("Module Topic")
            w = st.number_input("Week Number", 1, 15)
            img = st.text_input("Image URL (Google Drive/Web Link)")
            v = st.text_input("YouTube/Slide Link")
            n = st.text_input("Notes Link")
            if st.form_submit_button("Save to Portal"):
                supabase.table("materials").insert({
                    "course_program": p, "course_name": t, "week": w, 
                    "video_url": v, "notes_url": n, "image_url": img
                }).execute()
                st.success("Module saved successfully!")

    with t2:
        target = st.text_input("Target Course Name")
        batch_img = st.text_input("Default Image URL
