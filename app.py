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

# 3. YOUTUBE EMBED FIXER
def get_embed_url(url):
    if not url or not isinstance(url, str):
        return None
    # Handle Playlists
    if "list=" in url:
        playlist_id = url.split("list=")[-1].split("&")[0]
        return f"https://www.youtube.com/embed/videoseries?list={playlist_id}"
    # Handle Standard Videos
    if "watch?v=" in url:
        video_id = url.split("v=")[-1].split("&")[0]
        return f"https://www.youtube.com/embed/{video_id}"
    # Handle Shortened Links
    if "youtu.be/" in url:
        video_id = url.split("youtu.be/")[-1].split("?")[0]
        return f"https://www.youtube.com/embed/{video_id}"
    return url

# 4. MODERN UI & GLASS NAVIGATION STYLING
st.set_page_config(page_title="Flux | Learning Portal", layout="wide")

st.markdown("""
<style>
    header[data-testid="stHeader"] { visibility: hidden; height: 0%; }
    .stApp { background-color: #f0f2f5; }
    
    /* Login Box Styling */
    .login-box {
        background-color: white; padding: 50px; border-radius: 20px;
        box-shadow: 0px 20px 60px rgba(0,0,0,0.3); max-width: 480px; margin: auto;
        text-align: center; border: 1px solid rgba(0,0,0,0.05);
    }
    .kmt-header { font-size: 10px; color: #aaa; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 2px; }
    .flux-box { 
        background-color: #000; color: #fff; padding: 15px 35px; border-radius: 10px;
        font-family: 'Trebuchet MS', sans-serif; font-weight: bold; font-size: 2.8em;
        display: inline-block; margin-bottom: 40px;
    }

    /* KIU GREEN SIGN UP BUTTON */
    .kiu-green-btn div[data-testid="stButton"] button {
        background-color: #28a745 !important;
        color: white !important; border: none !important;
        height: 55px; font-weight: bold !important; border-radius: 12px !important;
        font-size: 1.1em !important;
    }

    /* COURSE CONTENT STRUCTURE */
    .course-title-bar {
        background: #000; color: white; padding: 20px;
        border-radius: 15px 15px 0 0; margin-top: 30px;
        font-size: 1.6em; font-weight: bold;
    }
    .topic-container {
        background: white; padding: 30px; border-radius: 0 0 15px 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.05); margin-bottom: 40px;
    }
    .topic-name { font-size: 1.4em; font-weight: 700; color: #1a1a1b; margin-bottom: 15px; }
    
    /* MODERN SIDEBAR */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.9) !important;
        backdrop-filter: blur(10px);
    }
</style>
""", unsafe_allow_html=True)

# 5. AUTHENTICATION PAGES
if not st.session_state.logged_in:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.8, 1])
    with c2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown('<div class="kmt-header">Built by KMT dynamics Co Ltd</div>', unsafe_allow_html=True)
        st.markdown('<div class="flux-box">flux</div>', unsafe_allow_html=True)
        
        if st.session_state.page == "selector":
            if st.button("Sign In to Portal", use_container_width=True): 
                st.session_state.page = "login"; st.rerun()
            st.markdown('<div class="kiu-green-btn">', unsafe_allow_html=True)
            if st.button("Sign Up as KIU Student", use_container_width=True): 
                st.session_state.page = "signup"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            if st.button("Explore Public Content", use_container_width=True): 
                st.session_state.user_type = "public"; st.session_state.logged_in = True; st.rerun()

        elif st.session_state.page == "signup":
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            reg = st.text_input("Registration Number")
            if st.button("Complete Registration", type="primary", use_container_width=True):
                supabase.table("users").insert({"full_name": name, "email": email, "registration_number": reg, "is_kiu_student": True}).execute()
                st.session_state.page = "login"; st.rerun()
            if st.button("Back"): st.session_state.page = "selector"; st.rerun()

        elif st.session_state.page == "login":
            u_email = st.text_input("Enter Email")
            if st.button("Login", type="primary", use_container_width=True):
                user = supabase.table("users").select("*").eq("email", u_email).execute()
                if user.data:
                    st.session_state.user_type = "kiu" if user.data[0]['is_kiu_student'] else "public"
                    st.session_state.logged_in = True; st.rerun()
                else: st.error("Email not found.")
            if st.button("Back"): st.session_state.page = "selector"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# 6. NAVIGATION
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🌊 Flux</h2>", unsafe_allow_html=True)
    st.write("---")
    role = st.radio("Navigation", ["📖 Study Hub", "🛠 Admin Control"], label_visibility="collapsed")
    st.write("---")
    if st.button("Sign Out", use_container_width=True):
        st.session_state.logged_in = False; st.session_state.page = "selector"; st.rerun()

# --- ADMIN SECTION ---
if "Admin" in role:
    if st.sidebar.text_input("Password", type="password") == "flux":
        prog = st.text_input("Program Name")
        file = st.file_uploader("Upload CSV/Excel Data")
        if file and prog and st.button("Bulk Upload"):
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
            st.success("Successfully uploaded course content!")

# --- STUDY HUB ---
else:
    st.markdown("<h1 style='text-align:center;'>Your Learning Journey</h1>", unsafe_allow_html=True)
    res = supabase.table("materials").select("*").execute()
    if res.data:
        df = pd.DataFrame(res.data)
        for prog in df['course_program'].unique():
            st.markdown(f'<div class="course-title-bar">📂 {prog}</div>', unsafe_allow_html=True)
            st.markdown('<div class="topic-container">', unsafe_allow_html=True)
            
            topics = df[df['course_program'] == prog]
            for _, item in topics.iterrows():
                st.markdown(f'<div class="topic-name">{item.get("course_name")}</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    embed_link = get_embed_url(item.get('video_url'))
                    if embed_link:
                        # Using st.video with the corrected embed link
                        st.video(embed_link)
                    else:
                        st.info("No video link found for this topic.")
                
                with col2:
                    st.write("### Resources")
                    if item.get('notes_url'):
                        st.link_button("📚 Open Lecture Notes", item['notes_url'], use_container_width=True)
                    st.write("---")
                    st.caption("Please watch the video fully before proceeding to the notes.")
                st.divider()
            st.markdown('</div>', unsafe_allow_html=True)
