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

# 3. BACKGROUND IMAGE
bg_url = "https://images.unsplash.com/photo-1497366216548-37526070297c"
try:
    bg_query = supabase.table("portal_settings").select("login_bg_url").eq("id", 1).execute()
    if bg_query.data: bg_url = bg_query.data[0]['login_bg_url']
except: pass

# 4. UI STYLING (Strictly matching your provided image)
st.set_page_config(page_title="Flux | Portal", layout="wide")

st.markdown(f"""
<style>
    /* Global Background */
    .stApp {{ 
        background-image: url("{bg_url}"); 
        background-size: cover; 
        background-attachment: fixed; 
    }}

    /* Remove the empty white bar at the top */
    header {{visibility: hidden;}}
    .main .block-container {{padding-top: 1rem;}}

    /* Center branding container */
    .brand-container {{
        display: flex;
        justify-content: center;
        margin-bottom: 2rem;
    }}

    /* Flux Logo Styling */
    .flux-logo {{ 
        background-color: #000; 
        color: #fff !important; 
        padding: 15px 40px; 
        border-radius: 12px;
        font-family: "Comic Sans MS", cursive; 
        font-weight: bold; 
        font-size: 3em;
        text-align: center;
        width: fit-content;
    }}

    /* Button Styling - Matching your image (White Pill, Full Width, Black Text) */
    div.stButton > button {{
        background-color: #ffffff !important;
        color: #000000 !important; /* Text is black */
        border-radius: 30px !important; /* Exact Pill Shape */
        border: none !important;
        width: 100% !important;
        height: 3.8em !important;
        font-weight: 600 !important;
        font-size: 1.1em !important;
        margin-bottom: 15px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
    }}
    
    div.stButton > button:hover {{
        background-color: #f8f8f8 !important;
        color: #000000 !important;
    }}

    /* Navigation Header in Sidebar - Black */
    .sidebar-nav-header {{
        color: #000000 !important;
        font-size: 1.6rem;
        font-weight: bold;
        margin-bottom: 1.2rem;
    }}

    /* Sidebar and Course Page Button Text - Black */
    [data-testid="stSidebar"] button div p, 
    .stExpander button div p,
    .stDownloadButton button div p {{
        color: black !important;
    }}

    /* Signup Page override */
    .signup-area button {{
        background-color: #28a745 !important;
        color: #000000 !important;
    }}

    /* General Text */
    h1, h2, h3, p, span, label {{ color: white !important; }}
    
    /* Input Field Placeholders */
    input::placeholder {{
        color: black !important;
        opacity: 0.8;
    }}
</style>
""", unsafe_allow_html=True)

# 5. AUTHENTICATION SCREENS
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
            if st.button("Login"):
                st.session_state.logged_in = True; st.rerun()
            if st.button("Back"): st.session_state.page = "selector"; st.rerun()
    st.stop()

# 6. MAIN APP CONTENT
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
        if st.button("← Back to Learning Path"): st.session_state.current_course = None; st.rerun()
        st.title(f"Modules: {st.session_state.current_course}")
        # Fetching course data...
    else:
        st.title("My Learning Path")
        
        # Course Section using your YouTube links
        st.subheader("Foundation Courses")
        v_col1, v_col2 = st.columns(2)
        
        with v_col1:
            st.video("https://youtu.be/SzJ46YA_RaA?si=Kd6qlQnGtQ5y2wez")
            if st.button("Select Computer Science"): 
                st.session_state.current_course = "Computer Science"; st.rerun()
        
        with v_col2:
            st.video("https://youtu.be/0b01vrBjT8I?si=wl6X9A1b5jsznlFk")
            if st.button("Select ACCA"): 
                st.session_state.current_course = "ACCA"; st.rerun()

        st.write("---")
        st.subheader("Introductory Overviews")
        ov1, ov2 = st.columns(2)
        with ov1: st.video("https://youtu.be/TjPFZaMe2yw")
        with ov2: st.video("https://youtu.be/U-7THjkQdbg")
