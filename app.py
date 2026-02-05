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
if 'user_type' not in st.session_state: st.session_state.user_type = None
if 'page' not in st.session_state: st.session_state.page = "selector"

# 3. YOUTUBE EMBED FIXER (Essential for viewing content)
def get_embed_url(url):
    if not url or not isinstance(url, str): return None
    if "list=" in url:
        playlist_id = url.split("list=")[-1].split("&")[0]
        return f"https://www.youtube.com/embed/videoseries?list={playlist_id}"
    if "watch?v=" in url:
        video_id = url.split("v=")[-1].split("&")[0]
        return f"https://www.youtube.com/embed/{video_id}"
    if "youtu.be/" in url:
        video_id = url.split("youtu.be/")[-1].split("?")[0]
        return f"https://www.youtube.com/embed/{video_id}"
    return url

# 4. ORIGINAL STYLING + REQUESTED BRANDING
st.set_page_config(page_title="Flux | Portal", layout="wide")

st.markdown("""
<style>
    /* REMOVE TOP BAR */
    header[data-testid="stHeader"] { visibility: hidden; height: 0%; }
    
    /* Login Branding */
    .login-box {
        background-color: white; padding: 40px; border-radius: 15px;
        box-shadow: 0px 10px 40px rgba(0,0,0,0.3); max-width: 450px; margin: auto;
        text-align: center;
    }
    .kmt-header { font-size: 11px; color: #777; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1.5px; }
    .flux-box { 
        background-color: #000; color: #fff; padding: 15px 30px; border-radius: 8px;
        font-family: "Comic Sans MS", cursive; font-weight: bold; font-size: 2.5em;
        display: inline-block; margin-bottom: 30px;
    }

    /* KIU GREEN BUTTON */
    .kiu-green-btn div[data-testid="stButton"] button {
        background-color: #28a745 !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
    }

    /* Hints Visibility */
    .stTextInput label { color: black !important; }
    input::placeholder { color: #888 !important; }
    
    /* Sidebar glass effect */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.9) !important;
        backdrop-filter: blur(10px);
    }
</style>
""", unsafe_allow_html=True)

# 5. AUTHENTICATION PAGES
if not st.session_state.logged_in:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown('<div class="kmt-header">Built by KMT dynamics Co Ltd</div>', unsafe_allow_html=True)
        st.markdown('<div class="flux-box">flux</div>', unsafe_allow_html=True)
        
        if st.session_state.page == "selector":
            if st.button("Sign In", use_container_width=True): 
                st.session_state.page = "login"; st.rerun()
            st.markdown('<div class="kiu-green-btn">', unsafe_allow_html=True)
            if st.button("Sign Up as KIU Student", use_container_width=True): 
                st.session_state.page = "signup"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            if st.button("Guest Access", use_container_width=True): 
                st.session_state.user_type = "public"; st.session_state.logged_in = True; st.rerun()

        elif st.session_state.page == "signup":
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            reg = st.text_input("Registration Number")
            if st.button("Complete Sign Up", type="primary", use_container_width=True):
                supabase.table("users").insert({"full_name": name, "email": email, "registration_number": reg, "is_kiu_student": True}).execute()
                st.session_state.page = "login"; st.rerun()
            if st.button("Back"): st.session_state.page = "selector"; st.rerun()

        elif st.session_state.page == "login":
            u_email = st.text_input("Email")
            if st.button("Login", type="primary", use_container_width=True):
                user = supabase.table("users").select("*").eq("email", u_email).execute()
                if user.data:
                    st.session_state.user_type = "kiu" if user.data[0]['is_kiu_student'] else "public"
                    st.session_state.logged_in = True; st.rerun()
                else: st.error("Email not found.")
            if st.button("Back"): st.session_state.page = "selector"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# 6. MAIN APP
with st.sidebar:
    st.markdown("### 🌊 Flux Navigator")
    st.write("---")
    role = st.radio("Menu", ["📖 Learning Center", "🛠 Administrator"], label_visibility="collapsed")
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False; st.session_state.page = "selector"; st.rerun()

# --- ADMIN ---
if "Administrator" in role:
    if st.sidebar.text_input("Password", type="password") == "flux":
        prog = st.text_input("Program Name")
        file = st.file_uploader("Bulk Upload CSV/Excel")
        if file and prog and st.button("Start Upload"):
            df = pd.read_excel(file) if "xlsx" in file.name else pd.read_csv(file)
            df = df.replace({np.nan: None})
            for _, row in df.iterrows():
                try:
                    supabase.table("materials").insert({
                        "course_program": prog,
                        "course_name": str(row.get('Topic Covered', 'No Title')),
                        "video_url": str(row.get('Embeddable YouTube Video Link', '')),
                        "notes_url": str(row.get('Link to Google docs Document', ''))
                    }).execute()
                except: continue
            st.success("Uploaded!")

# --- LEARNING CENTER ---
else:
    st.title("My Courses")
    res = supabase.table("materials").select("*").execute()
    if res.data:
        df = pd.DataFrame(res.data)
        for prog in df['course_program'].unique():
            with st.expander(f"📚 {prog}", expanded=True):
                items = df[df['course_program'] == prog]
                for _, item in items.iterrows():
                    st.subheader(item.get('course_name'))
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        v_url = get_embed_url(item.get('video_url'))
                        if v_url: st.video(v_url)
                    with col2:
                        if item.get('notes_url'):
                            st.link_button("📂 View Notes", item['notes_url'], use_container_width=True)
                    st.write("---")
