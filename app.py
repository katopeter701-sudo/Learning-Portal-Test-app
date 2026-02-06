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

# 2. SESSION STATE INITIALIZATION
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'page' not in st.session_state: st.session_state.page = "selector"
if 'current_course' not in st.session_state: st.session_state.current_course = None
if 'role' not in st.session_state: st.session_state.role = "Learning Center"

# 3. GOOGLE DRIVE IMAGE FIX
# This format (uc?id=) is the most reliable for direct rendering in Streamlit
DRIVE_ID = "1-diy5YsO0TdGj73Y3SoC6FL8UWEJxy51"
IMAGE_URL = f"https://drive.google.com/uc?id={DRIVE_ID}"

COURSE_TILES = {
    "Computer Science": IMAGE_URL,
    "ACCA": IMAGE_URL
}

# 4. BACKGROUND FETCH
bg_url = "https://images.unsplash.com/photo-1497366216548-37526070297c"
try:
    bg_query = supabase.table("portal_settings").select("login_bg_url").eq("id", 1).execute()
    if bg_query.data: bg_url = bg_query.data[0]['login_bg_url']
except: pass

# 5. MODERN UI STYLING
st.set_page_config(page_title="Flux | Portal", layout="wide")

st.markdown(f"""
<style>
    .stApp {{ background-image: url("{bg_url}"); background-size: cover; background-attachment: fixed; }}
    
    /* Centering the flux branding and removing the top empty bar */
    .login-container {{
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        margin-top: 10vh;
    }}

    .flux-box {{ 
        background-color: #000; color: #fff !important; padding: 15px 40px; border-radius: 8px;
        font-family: "Comic Sans MS", cursive; font-weight: bold; font-size: 3em;
        margin-bottom: 40px; text-align: center;
    }}

    /* Buttons: Fixed visibility and styling */
    .stButton button {{
        background-color: white !important;
        color: black !important; /* Text always black and visible */
        border-radius: 10px !important;
        border: none !important;
        font-weight: bold !important;
        height: 3em !important;
        width: 100% !important;
    }}

    /* Sign Up Page Specifics */
    .signup-button button {{
        background-color: #28a745 !important; /* Green Button */
        color: black !important;
    }}

    /* Placeholder/Hint styling */
    input::placeholder {{
        color: black !important;
        font-size: 13px !important;
        opacity: 0.7 !important;
    }}

    /* Sidebar and General Text */
    [data-testid="stSidebar"] {{ background-color: rgba(0, 0, 0, 0.8) !important; }}
    h1, h2, h3, p, span, label {{ color: white !important; }}
    [data-testid="stSidebar"] button p {{ color: black !important; }}
</style>
""", unsafe_allow_html=True)

# 6. AUTHENTICATION FLOW
if not st.session_state.logged_in:
    # Use columns to keep the central alignment from your image
    _, col_mid, _ = st.columns([1, 2, 1])
    
    with col_mid:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="flux-box">flux</div>', unsafe_allow_html=True)
        
        if st.session_state.page == "selector":
            st.button("Sign In", key="btn_signin", on_click=lambda: setattr(st.session_state, 'page', 'login'))
            st.button("Register", key="btn_reg", on_click=lambda: setattr(st.session_state, 'page', 'signup'))
            st.button("Public Access", key="btn_pub", on_click=lambda: st.session_state.update({"logged_in": True}))

        elif st.session_state.page == "signup":
            name = st.text_input("Full Name", placeholder="enter your full name")
            email = st.text_input("Email", placeholder="enter your email address")
            student_id = st.text_input("Registration ID", placeholder="KIU- Student ID")
            
            # Green Button Container
            st.markdown('<div class="signup-button">', unsafe_allow_html=True)
            if st.button("Create Account", use_container_width=True):
                supabase.table("users").insert({"full_name": name, "email": email, "registration_number": student_id}).execute()
                st.success("Success! Please Login.")
                st.session_state.page = "login"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
            if st.button("Back"): st.session_state.page = "selector"; st.rerun()

        elif st.session_state.page == "login":
            u_email = st.text_input("Email", placeholder="enter your registered email")
            if st.button("Login", use_container_width=True):
                user = supabase.table("users").select("*").eq("email", u_email).execute()
                if user.data:
                    st.session_state.logged_in = True; st.rerun()
                else: st.error("User not found.")
            if st.button("Back"): st.session_state.page = "selector"; st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# 7. MAIN APP LOGIC (Sidebar and Content)
with st.sidebar:
    st.markdown("### Navigation")
    if st.button("Learning Center", use_container_width=True): st.session_state.role = "Learning Center"; st.rerun()
    if st.button("Administrator", use_container_width=True): st.session_state.role = "Administrator"; st.rerun()
    st.write("---")
    if st.button("Logout", use_container_width=True): st.session_state.clear(); st.rerun()

if st.session_state.role == "Administrator":
    st.title("Admin Console")
    # Admin tools here...
else:
    # Student Portal Content
    if st.session_state.current_course:
        if st.button("← Back"): st.session_state.current_course = None; st.rerun()
        st.title(f"Modules: {st.session_state.current_course}")
        # Fetching database content...
    else:
        st.title("My Learning Path")
        
        # Course Selection Tiles
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
