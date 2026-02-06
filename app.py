import streamlit as st
import pandas as pd
from supabase import create_client
import numpy as np

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
if 'page' not in st.session_state: st.session_state.page = "selector"
if 'current_course' not in st.session_state: st.session_state.current_course = None
if 'role' not in st.session_state: st.session_state.role = "Learning Center"

# 3. HARDCODED GITHUB RAW LINKS
# Replace these URLs with your actual GitHub Raw links once you upload them
COURSE_TILES = {
    "Computer Science": "https://raw.githubusercontent.com/streamlit/st-vizz-images/main/cat.jpg", 
    "ACCA": "https://raw.githubusercontent.com/streamlit/st-vizz-images/main/dog.jpg"
}

# 4. BACKGROUND IMAGE
bg_url = "https://images.unsplash.com/photo-1497366216548-37526070297c"
try:
    bg_query = supabase.table("portal_settings").select("login_bg_url").eq("id", 1).execute()
    if bg_query.data: bg_url = bg_query.data[0]['login_bg_url']
except: pass

# 5. UI STYLING
st.set_page_config(page_title="Flux | Portal", layout="wide")

st.markdown(f"""
<style>
    .stApp {{ background-image: url("{bg_url}"); background-size: cover; background-attachment: fixed; }}
    header {{visibility: hidden;}}
    .main .block-container {{padding-top: 2rem;}}

    .brand-container {{ display: flex; justify-content: center; margin-bottom: 2rem; }}
    .flux-logo {{ 
        background-color: #000; color: #fff !important; padding: 15px 40px; border-radius: 12px;
        font-family: "Comic Sans MS", cursive; font-weight: bold; font-size: 3em; text-align: center; width: fit-content;
    }}

    /* Global Button Styling - White Pill with Black Text */
    div.stButton > button {{
        background-color: #ffffff !important;
        color: #000000 !important;
        border-radius: 25px !important;
        border: none !important;
        width: 100% !important;
        height: 3.5em !important;
        font-weight: 600 !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
    }}
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {{ background-color: rgba(0, 0, 0, 0.8) !important; }}
    .sidebar-nav-header {{ color: #333333 !important; font-size: 1.5rem; font-weight: bold; margin-bottom: 1rem; }}
    [data-testid="stSidebar"] button div p {{ color: black !important; }}

    /* Signup Button override to Green */
    .signup-area button {{ background-color: #28a745 !important; color: #000000 !important; }}

    /* Placeholders/Hints and General Text */
    input::placeholder {{ color: black !important; font-size: 13px; }}
    h1, h2, h3, p, span, label {{ color: white !important; }}
</style>
""", unsafe_allow_html=True)

# 6. AUTHENTICATION SCREENS
if not st.session_state.logged_in:
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        st.markdown('<div class="brand-container"><div class="flux-logo">flux</div></div>', unsafe_allow_html=True)
        
        if st.session_state.page == "selector":
            if st.button("Sign In"): st.session_state.page = "login"; st.rerun()
            if st.button("Register"): st.session_state.page = "signup"; st.rerun()
            if st.button("Public Access"): st.session_state.logged_in = True; st.rerun()

        elif st.session_state.page == "signup":
            st.text_input("Full Name", placeholder="enter your full name")
            st.text_input("Email", placeholder="enter your email address")
            st.text_input("Registration ID", placeholder="KIU- Student ID")
            st.markdown('<div class="signup-area">', unsafe_allow_html=True)
            if st.button("Create Account"):
                st.success("Account Created! Please Login.")
                st.session_state.page = "login"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            if st.button("Back"): st.session_state.page = "selector"; st.rerun()

        elif st.session_state.page == "login":
            st.text_input("Email", placeholder="enter your registered email")
            if st.button("Login"): st.session_state.logged_in = True; st.rerun()
            if st.button("Back"): st.session_state.page = "selector"; st.rerun()
    st.stop()

# 7. MAIN APP CONTENT
with st.sidebar:
    st.markdown('<div class="sidebar-nav-header">Navigation</div>', unsafe_allow_html=True)
    if st.button("Learning Center"): st.session_state.role = "Learning Center"; st.rerun()
    if st.button("Administrator"): st.session_state.role = "Administrator"; st.rerun()
    st.write("---")
    if st.button("Logout"): st.session_state.clear(); st.rerun()

if st.session_state.role == "Administrator":
    st.title("Admin Console")
else:
    if st.session_state.current_course:
        if st.button("← Back to Path"): st.session_state.current_course = None; st.rerun()
        st.title(f"Modules: {st.session_state.current_course}")
    else:
        st.title("My Learning Path")
        c1, c2 = st.columns(2)
        with c1:
            st.image(COURSE_TILES["Computer Science"], caption="Computer Science", use_container_width=True)
            if st.button("Open Computer Science"): st.session_state.current_course = "Computer Science"; st.rerun()
        with c2:
            st.image(COURSE_TILES["ACCA"], caption="ACCA", use_container_width=True)
            if st.button("Open ACCA"): st.session_state.current_course = "ACCA"; st.rerun()

        st.write("---")
        st.subheader("Introductory Overviews")
        v1, v2 = st.columns(2)
        with v1: st.video("https://youtu.be/TjPFZaMe2yw")
        with v2: st.video("https://youtu.be/U-7THjkQdbg")
