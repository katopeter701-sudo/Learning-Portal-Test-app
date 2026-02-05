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

# 4. MODERN UI STYLING
st.set_page_config(page_title="Flux | Portal", layout="wide")

st.markdown(f"""
<style>
    /* Background */
    .stApp {{ background-image: url("{bg_url}"); background-size: cover; background-attachment: fixed; }}
    
    /* Modernized Login Box */
    .login-box {{
        background-color: white; padding: 40px; border-radius: 12px;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.3); max-width: 450px; margin: auto;
    }}
    .kmt-header {{ font-size: 10px; color: #888; text-align: center; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 1px; }}
    .flux-center {{ 
        background-color: #000; color: #fff; padding: 10px 20px; border-radius: 5px;
        font-family: "Comic Sans MS", cursive; font-weight: bold; font-size: 2em;
        text-align: center; display: block; margin-bottom: 30px;
    }}

    /* Modernized Sidebar */
    [data-testid="stSidebar"] {{
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(0,0,0,0.1);
    }}
    .nav-card {{
        background: white; padding: 15px; border-radius: 10px;
        margin-bottom: 10px; border: 1px solid #eee;
    }}
</style>
""", unsafe_allow_html=True)

# 5. AUTHENTICATION FLOW
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown('<div class="kmt-header">Built by KMT dynamics Co Ltd</div>', unsafe_allow_html=True)
        st.markdown('<div class="flux-center">flux</div>', unsafe_allow_html=True)
        
        if st.session_state.page == "selector":
            if st.button("Sign In", use_container_width=True): st.session_state.page = "login"; st.rerun()
            if st.button("Create Account", use_container_width=True): st.session_state.page = "signup"; st.rerun()
            if st.button("Guest Access", use_container_width=True): 
                st.session_state.user_type = "public"; st.session_state.logged_in = True; st.rerun()

        elif st.session_state.page == "signup":
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            reg = st.text_input("Registration Number (Optional)")
            if st.button("Register", type="primary", use_container_width=True):
                supabase.table("users").insert({"full_name": name, "email": email, "registration_number": reg}).execute()
                st.session_state.page = "login"; st.rerun()
            if st.button("Back"): st.session_state.page = "selector"; st.rerun()

        elif st.session_state.page == "login":
            u_email = st.text_input("Email")
            if st.button("Login", type="primary", use_container_width=True):
                st.session_state.logged_in = True; st.rerun()
            if st.button("Back"): st.session_state.page = "selector"; st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# 6. MAIN INTERFACE
with st.sidebar:
    st.markdown("### 🌊 Flux Navigation")
    st.write("---")
    role = st.radio("Go to", ["📖 Learning Portal", "⚙️ Admin Settings"], label_visibility="collapsed")
    st.write("---")
    if st.button("Log Out", use_container_width=True):
        st.session_state.logged_in = False; st.rerun()

# --- ADMIN SETTINGS ---
if "Admin" in role:
    if st.sidebar.text_input("Admin Key", type="password") == "flux":
        t1, t2 = st.tabs(["Upload Content", "Portal Design"])
        with t1:
            c_name = st.text_input("Course Name")
            c_img = st.text_input("Course Tile Image URL", value="https://images.unsplash.com/photo-1516321318423-f06f85e504b3")
            file = st.file_uploader("Upload CSV/Excel")
            if file and st.button("Process Bulk Upload"):
                df = pd.read_excel(file) if "xlsx" in file.name else pd.read_csv(file)
                df = df.replace({np.nan: None})
                for _, row in df.iterrows():
                    supabase.table("materials").insert({
                        "course_program": c_name, "image_url": c_img,
                        "course_name": str(row.get('Topic Covered', 'Topic')),
                        "week": int(row.get('Week', 1)) if row.get('Week') else 1,
                        "video_url": str(row.get('Embeddable YouTube Video Link', '')),
                        "notes_url": str(row.get('link to Google docs Document', ''))
                    }).execute()
                st.success("Done!")
        with t2:
            new_bg = st.text_input("New Background URL")
            if st.button("Save Design"):
                supabase.table("portal_settings").upsert({"id": 1, "login_bg_url": new_bg}).execute()
                st.rerun()

# --- PORTAL ---
else:
    st.title("My Courses")
    data = supabase.table("materials").select("*").execute()
    if data.data:
        df = pd.DataFrame(data.data)
        for prog in df['course_program'].unique():
            st.subheader(f"📂 {prog}")
            items = df[df['course_program'] == prog]
            for _, item in items.iterrows():
                # FIXED: KeyError Safety Check
                wk = item.get('week', '1')
                name = item.get('course_name', 'Unnamed Lesson')
                with st.expander(f"Week {wk}: {name}"):
                    if item.get('video_url'): st.video(item['video_url'])
                    if item.get('notes_url'): st.link_button("View Notes", item['notes_url'])
