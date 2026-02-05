import streamlit as st
import pandas as pd
from supabase import create_client
import numpy as np

# 1. DATABASE CONNECTION
PROJECT_ID = "uxtmgdenwfyuwhezcleh"
SUPABASE_URL = f"https://{PROJECT_ID}.supabase.co"
SUPABASE_KEY = "sb_publishable_1BIwMEH8FVDv7fFafz31uA_9FqAJr0-"

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception:
    st.error("Database Connection Failed.")
    st.stop()

# 2. SESSION STATE
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_type' not in st.session_state: st.session_state.user_type = None
if 'page' not in st.session_state: st.session_state.page = "selector"

# 3. BACKGROUND FETCH
bg_url = "https://images.unsplash.com/photo-1497366216548-37526070297c"
try:
    bg_query = supabase.table("portal_settings").select("login_bg_url").eq("id", 1).execute()
    if bg_query.data: bg_url = bg_query.data[0]['login_bg_url']
except: pass

# 4. MODERN UI STYLING & BRANDING
st.set_page_config(page_title="Flux | Portal", layout="wide")

st.markdown(f"""
<style>
    /* REMOVE TOP WHITE BAR */
    header[data-testid="stHeader"] {{
        visibility: hidden;
        height: 0%;
    }}
    
    /* Global Background */
    .stApp {{ background-image: url("{bg_url}"); background-size: cover; background-attachment: fixed; }}
    
    /* Modern Login Box */
    .login-box {{
        background-color: white; padding: 40px; border-radius: 15px;
        box-shadow: 0px 10px 40px rgba(0,0,0,0.4); max-width: 450px; margin: auto;
        text-align: center;
    }}
    
    /* Branding Header */
    .kmt-header {{ font-size: 11px; color: #777; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1.5px; }}
    
    /* Centered Flux Block */
    .flux-box {{ 
        background-color: #000; color: #fff; padding: 15px 30px; border-radius: 8px;
        font-family: "Comic Sans MS", cursive; font-weight: bold; font-size: 2.5em;
        display: inline-block; margin-bottom: 30px;
    }}

    /* HINTS VISIBILITY */
    .stTextInput label {{ color: black !important; font-weight: bold !important; }}
    input::placeholder {{ color: #666 !important; opacity: 1; }} 
    
    /* Modernized Sidebar */
    [data-testid="stSidebar"] {{
        background: rgba(255, 255, 255, 0.9) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(0,0,0,0.05);
    }}
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
            if st.button("Register / Sign Up", use_container_width=True): 
                st.session_state.page = "signup"; st.rerun()
            if st.button("Guest Access", use_container_width=True): 
                st.session_state.user_type = "public"; st.session_state.logged_in = True; st.rerun()

        elif st.session_state.page == "signup":
            name = st.text_input("Full Name", placeholder="Enter full name")
            email = st.text_input("Email Address", placeholder="e.g. name@email.com")
            is_kiu = st.checkbox("I am a KIU Student")
            reg = st.text_input("Registration Number", placeholder="202X/XX/XXX") if is_kiu else ""
            if st.button("Create Account", type="primary", use_container_width=True):
                if name and email:
                    try:
                        supabase.table("users").insert({
                            "full_name": name, "email": email, "registration_number": reg, "is_kiu_student": is_kiu
                        }).execute()
                        st.success("Account created!")
                        st.session_state.page = "login"; st.rerun()
                    except: st.error("Registration failed.")
            if st.button("Back"): st.session_state.page = "selector"; st.rerun()

        elif st.session_state.page == "login":
            u_email = st.text_input("Email", placeholder="Enter registered email")
            if st.button("Sign In", type="primary", use_container_width=True):
                user = supabase.table("users").select("*").eq("email", u_email).execute()
                if user.data:
                    st.session_state.user_type = "kiu" if user.data[0]['is_kiu_student'] else "public"
                    st.session_state.logged_in = True; st.rerun()
                else: st.error("Email not found.")
            if st.button("Back"): st.session_state.page = "selector"; st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# 6. MAIN APP INTERFACE
with st.sidebar:
    st.markdown("### 🌊 Flux Navigator")
    st.write("---")
    role = st.radio("Menu", ["📖 Learning Center", "🛠 Administrator"], label_visibility="collapsed")
    st.write("---")
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False; st.session_state.page = "selector"; st.rerun()

# --- ADMIN CONSOLE ---
if "Administrator" in role:
    if st.sidebar.text_input("Admin Password", type="password") != "flux": st.stop()
    
    t1, t2 = st.tabs(["Bulk Upload Content", "Portal Design"])
    
    with t1:
        prog_name = st.text_input("Program Name")
        tile_img = st.text_input("Course Tile Image URL")
        file = st.file_uploader("Upload CSV/Excel", type=['xlsx', 'csv'])
        if file and prog_name and st.button("Start Bulk Upload"):
            df = pd.read_excel(file) if "xlsx" in file.name else pd.read_csv(file)
            df = df.replace({np.nan: None}) 
            for _, row in df.iterrows():
                try:
                    supabase.table("materials").insert({
                        "course_program": prog_name,
                        "course_name": str(row.get('Topic Covered', 'No Title')),
                        "week": int(pd.to_numeric(row.get('Week', 1), errors='coerce') or 1),
                        "video_url": str(row.get('Embeddable YouTube Video Link', '')),
                        "notes_url": str(row.get('Link to Google docs Document', '')),
                        "image_url": tile_img
                    }).execute()
                except: continue
            st.success("Upload successful!")

    with t2:
        new_bg = st.text_input("New Background URL")
        if st.button("Update Portal Look"):
            supabase.table("portal_settings").upsert({"id": 1, "login_bg_url": new_bg}).execute()
            st.rerun()

# --- STUDENT PORTAL ---
else:
    st.title("My Learning Path")
    data = supabase.table("materials").select("*").execute()
    if data.data:
        df = pd.DataFrame(data.data)
        for prog in df['course_program'].unique():
            st.subheader(f"📂 {prog}")
            items = df[df['course_program'] == prog]
            cols = st.columns(3)
            for i, (_, item) in enumerate(items.iterrows()):
                with cols[i % 3]:
                    week = item.get('week', '1')
                    name = item.get('course_name', 'Lesson')
                    with st.expander(f"Week {week}: {name}"):
                        if item.get('video_url'): st.video(item['video_url'])
                        if item.get('notes_url'): st.link_button("View Notes", item['notes_url'])
