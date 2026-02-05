import streamlit as st
import pandas as pd
from supabase import create_client
import numpy as np
import re

# 1. DATABASE CONNECTION
PROJECT_ID = "uxtmgdenwfyuwhezcleh"
SUPABASE_URL = f"https://{PROJECT_ID}.supabase.co"
SUPABASE_KEY = "sb_publishable_1BIwMEH8FVDv7fFaf_31uA_9FqAJr0-"

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception:
    st.error("Database Connection Failed.")
    st.stop()

# 2. SESSION STATE
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_type' not in st.session_state: st.session_state.user_type = None
if 'page' not in st.session_state: st.session_state.page = "selector"

# 3. HELPER: FIX YOUTUBE LINKS FOR EMBEDDING
def fix_youtube_link(url):
    if not url or not isinstance(url, str): return None
    # Convert watch?v= or playlist?list= to embed format if possible
    if "list=" in url:
        playlist_id = url.split("list=")[-1]
        return f"https://www.youtube.com/embed/videoseries?list={playlist_id}"
    if "watch?v=" in url:
        video_id = url.split("v=")[-1].split("&")[0]
        return f"https://www.youtube.com/embed/{video_id}"
    return url

# 4. MODERN UI STYLING
st.set_page_config(page_title="Flux | Portal", layout="wide")

st.markdown("""
<style>
    header[data-testid="stHeader"] { visibility: hidden; height: 0%; }
    .stApp { background-color: #f8f9fa; }
    
    /* Login Branding */
    .login-box {
        background-color: white; padding: 40px; border-radius: 20px;
        box-shadow: 0px 10px 40px rgba(0,0,0,0.2); max-width: 450px; margin: auto;
        text-align: center; border: 1px solid #eee;
    }
    .kmt-header { font-size: 11px; color: #888; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1.5px; }
    .flux-box { 
        background-color: #000; color: #fff; padding: 12px 30px; border-radius: 8px;
        font-family: 'Courier New', Courier, monospace; font-weight: bold; font-size: 2.5em;
        display: inline-block; margin-bottom: 30px;
    }

    /* KIU Green Button */
    .kiu-btn div[data-testid="stButton"] button {
        background-color: #28a745 !important;
        color: white !important; border: none !important;
        height: 50px; font-weight: bold !important; border-radius: 10px !important;
    }

    /* Course Display Cards */
    .course-header {
        background: #000; color: #fff; padding: 15px 25px;
        border-radius: 12px 12px 0 0; margin-top: 20px;
    }
    .content-card {
        background: white; padding: 25px; border-radius: 0 0 12px 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 30px;
        border: 1px solid #eee;
    }
    
    /* Input Labels */
    .stTextInput label { color: black !important; font-weight: 600 !important; }
    input::placeholder { color: #999 !important; }
</style>
""", unsafe_allow_html=True)

# 5. AUTHENTICATION PAGES
if not st.session_state.logged_in:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown('<div class="kmt-header">Built by KMT dynamics Co Ltd</div>', unsafe_allow_html=True)
        st.markdown('<div class="flux-box">flux</div>', unsafe_allow_html=True)
        
        if st.session_state.page == "selector":
            if st.button("Sign In", use_container_width=True): 
                st.session_state.page = "login"; st.rerun()
            st.markdown('<div class="kiu-btn">', unsafe_allow_html=True)
            if st.button("Register as KIU Student", use_container_width=True): 
                st.session_state.page = "signup"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            if st.button("Public Guest Access", use_container_width=True): 
                st.session_state.user_type = "public"; st.session_state.logged_in = True; st.rerun()

        elif st.session_state.page == "signup":
            name = st.text_input("Full Name", placeholder="e.g. John Doe")
            email = st.text_input("Email Address")
            reg = st.text_input("KIU Registration No.")
            if st.button("Complete Sign Up", type="primary", use_container_width=True):
                supabase.table("users").insert({"full_name": name, "email": email, "registration_number": reg, "is_kiu_student": True}).execute()
                st.success("Account Created! Please Login.")
                st.session_state.page = "login"; st.rerun()
            if st.button("← Back"): st.session_state.page = "selector"; st.rerun()

        elif st.session_state.page == "login":
            u_email = st.text_input("Email", placeholder="Enter your email")
            if st.button("Enter Portal", type="primary", use_container_width=True):
                user = supabase.table("users").select("*").eq("email", u_email).execute()
                if user.data:
                    st.session_state.user_type = "kiu" if user.data[0]['is_kiu_student'] else "public"
                    st.session_state.logged_in = True; st.rerun()
                else: st.error("Account not found.")
            if st.button("← Back"): st.session_state.page = "selector"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# 6. MAIN APP INTERFACE
with st.sidebar:
    st.markdown("### 🌊 Flux Navigator")
    st.write("---")
    role = st.radio("Navigation", ["📖 Learning Center", "🛠 Administrator"], label_visibility="collapsed")
    if st.button("Sign Out", use_container_width=True):
        st.session_state.logged_in = False; st.session_state.page = "selector"; st.rerun()

# --- ADMIN SECTION ---
if "Administrator" in role:
    if st.sidebar.text_input("Admin Password", type="password") == "flux":
        st.header("Admin Control")
        prog_name = st.text_input("Course Program Name (e.g. Computer Science)")
        file = st.file_uploader("Bulk Upload Content", type=['xlsx', 'csv'])
        if file and prog_name and st.button("Execute Bulk Upload"):
            df = pd.read_excel(file) if "xlsx" in file.name else pd.read_csv(file)
            df = df.replace({np.nan: None})
            for _, row in df.iterrows():
                try:
                    supabase.table("materials").insert({
                        "course_program": prog_name,
                        "course_name": str(row.get('Topic Covered', 'Unnamed Topic')),
                        "video_url": str(row.get('Embeddable YouTube Video Link', '')),
                        "notes_url": str(row.get('Link to Google docs Document', '')),
                        "week": 1
                    }).execute()
                except: continue
            st.success("Bulk Upload Complete!")

# --- LEARNING CENTER ---
else:
    st.title("My Study Hub")
    res = supabase.table("materials").select("*").execute()
    if res.data:
        df = pd.DataFrame(res.data)
        for prog in df['course_program'].unique():
            st.markdown(f'<div class="course-header">📚 {prog}</div>', unsafe_allow_html=True)
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            
            items = df[df['course_program'] == prog]
            for _, item in items.iterrows():
                st.subheader(item.get('course_name'))
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    v_url = fix_youtube_link(item.get('video_url'))
                    if v_url:
                        st.video(v_url)
                    else:
                        st.info("No video available for this topic.")
                
                with col2:
                    st.write("**Resources**")
                    if item.get('notes_url'):
                        st.link_button("📂 View Documents", item['notes_url'], use_container_width=True)
                    st.caption("Instructions: Study the video first, then open the notes for in-depth reading.")
                st.divider()
            st.markdown('</div>', unsafe_allow_html=True)
