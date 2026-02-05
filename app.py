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

# 4. MODERN UI STYLING (Fixed Syntax)
st.set_page_config(page_title="Flux | Portal", layout="wide")

st.markdown(f"""
<style>
    /* REMOVE TOP WHITE BAR */
    header[data-testid="stHeader"] {{ visibility: hidden; height: 0%; }}
    
    /* Global Background */
    .stApp {{ 
        background-image: url("{bg_url}"); 
        background-size: cover; 
        background-attachment: fixed; 
    }}
    
    /* Modern Login Box */
    .login-box {{
        background-color: white; padding: 40px; border-radius: 15px;
        box-shadow: 0px 10px 40px rgba(0,0,0,0.4); max-width: 450px; margin: auto;
        text-align: center;
    }}
    
    .kmt-header {{ font-size: 11px; color: #777; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1.5px; }}
    
    .flux-box {{ 
        background-color: #000; color: #fff; padding: 15px 30px; border-radius: 8px;
        font-family: "Comic Sans MS", cursive; font-weight: bold; font-size: 2.5em;
        display: inline-block; margin-bottom: 30px;
    }}

    /* GREEN KIU BUTTON */
    div[data-testid="stButton"] > button:first-child {{
        border-radius: 8px;
    }}
    
    /* Targeted Green Button for KIU */
    .kiu-green-btn div[data-testid="stButton"] button {{
        background-color: #28a745 !important;
        color: white !important;
        border: none !important;
        height: 50px;
        font-weight: bold !important;
    }}

    /* CONTENT DISPLAY */
    .course-card {{
        background: rgba(255,255,255,0.9); border-radius: 12px; padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 20px;
        border-left: 10px solid #000;
    }}
    
    /* Modern Sidebar */
    [data-testid="stSidebar"] {{
        background: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: blur(10px);
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
            
            st.markdown('<div class="kiu-green-btn">', unsafe_allow_html=True)
            if st.button("Sign Up as KIU Student", use_container_width=True): 
                st.session_state.page = "signup"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
            if st.button("Guest Access", use_container_width=True): 
                st.session_state.user_type = "public"; st.session_state.logged_in = True; st.rerun()

        elif st.session_state.page == "signup":
            name = st.text_input("Full Name", placeholder="Enter name")
            email = st.text_input("Email", placeholder="email@example.com")
            reg = st.text_input("Registration Number", placeholder="202X/XX/XXX")
            if st.button("Complete Sign Up", type="primary", use_container_width=True):
                supabase.table("users").insert({"full_name": name, "email": email, "registration_number": reg, "is_kiu_student": True}).execute()
                st.session_state.page = "login"; st.rerun()
            if st.button("Back"): st.session_state.page = "selector"; st.rerun()

        elif st.session_state.page == "login":
            u_email = st.text_input("Email", placeholder="Enter your registered email")
            if st.button("Login", type="primary", use_container_width=True):
                user = supabase.table("users").select("*").eq("email", u_email).execute()
                if user.data:
                    st.session_state.user_type = "kiu" if user.data[0]['is_kiu_student'] else "public"
                    st.session_state.logged_in = True; st.rerun()
                else: st.error("Account not found.")
            if st.button("Back"): st.session_state.page = "selector"; st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# 6. MAIN INTERFACE
with st.sidebar:
    st.markdown("### 🌊 Flux Navigator")
    st.write("---")
    role = st.radio("Menu", ["📖 Learning Center", "🛠 Administrator"], label_visibility="collapsed")
    st.write("---")
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False; st.session_state.page = "selector"; st.rerun()

# --- ADMIN ---
if "Administrator" in role:
    if st.sidebar.text_input("Admin Password", type="password") == "flux":
        prog_name = st.text_input("Program Name")
        file = st.file_uploader("Upload CSV/Excel", type=['xlsx', 'csv'])
        if file and prog_name and st.button("Process Bulk Upload"):
            df = pd.read_excel(file) if "xlsx" in file.name else pd.read_csv(file)
            df = df.replace({np.nan: None}) 
            for _, row in df.iterrows():
                try:
                    supabase.table("materials").insert({
                        "course_program": prog_name,
                        "course_name": str(row.get('Topic Covered', 'No Title')),
                        "week": 1, # Defaulting to 1 to avoid KeyError
                        "video_url": str(row.get('Embeddable YouTube Video Link', '')),
                        "notes_url": str(row.get('Link to Google docs Document', ''))
                    }).execute()
                except: continue
            st.success("Upload Successful!")

# --- LEARNING CENTER ---
else:
    st.title("Study Portal")
    data = supabase.table("materials").select("*").execute()
    if data.data:
        df = pd.DataFrame(data.data)
        for prog in df['course_program'].unique():
            st.markdown(f"## {prog}")
            items = df[df['course_program'] == prog]
            for _, item in items.iterrows():
                st.markdown(f"""
                <div class="course-card">
                    <h3 style="margin:0;">{item.get('course_name', 'Lesson')}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2 = st.columns([2, 1])
                with c1:
                    if item.get('video_url'): st.video(item['video_url'])
                with c2:
                    if item.get('notes_url'):
                        st.link_button("📂 View Notes", item['notes_url'], use_container_width=True)
                st.write("---")
                
