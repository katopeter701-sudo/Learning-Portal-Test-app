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

# 3. DYNAMIC BACKGROUND FETCH
bg_url = "https://images.unsplash.com/photo-1497366216548-37526070297c" # Default
try:
    bg_query = supabase.table("portal_settings").select("login_bg_url").eq("id", 1).execute()
    if bg_query.data: bg_url = bg_query.data[0]['login_bg_url']
except: pass

# 4. STYLING
st.set_page_config(page_title="Flux | Portal", layout="wide")

st.markdown(f"""
<style>
    .stApp {{ background-image: url("{bg_url}"); background-size: cover; background-attachment: fixed; }}
    .login-box {{
        background-color: white; padding: 30px; border-radius: 8px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.3); max-width: 450px; margin: auto;
    }}
    .flux-brand {{ font-family: "Comic Sans MS"; font-weight: bold; color: black; font-size: 0.9em; }}
</style>
""", unsafe_allow_html=True)

# 5. AUTHENTICATION PAGES
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.image("https://kiu.ac.ug/assets/images/logo.png", width=150)
        
        # --- SELECTOR PAGE ---
        if st.session_state.page == "selector":
            st.subheader("Welcome to Flux")
            if st.button("Sign In", use_container_width=True):
                st.session_state.page = "login"
                st.rerun()
            if st.button("Create Account (Sign Up)", use_container_width=True):
                st.session_state.page = "signup"
                st.rerun()
            if st.button("Continue as Guest (Public Courses)", use_container_width=True):
                st.session_state.user_type = "public"; st.session_state.logged_in = True
                st.rerun()

        # --- SIGN UP PAGE ---
        elif st.session_state.page == "signup":
            st.subheader("Create Account")
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            is_kiu = st.checkbox("I am a KIU Student")
            reg_no = ""
            if is_kiu:
                reg_no = st.text_input("Registration Number (e.g. 2024/01/...)")
            
            if st.button("Register", type="primary", use_container_width=True):
                if name and email:
                    try:
                        supabase.table("users").insert({
                            "full_name": name, "email": email, 
                            "registration_number": reg_no, "is_kiu_student": is_kiu
                        }).execute()
                        st.success("Account created! Please Sign In.")
                        st.session_state.page = "login"
                        st.rerun()
                    except: st.error("Email already registered or Database error.")
            if st.button("Back to Menu"):
                st.session_state.page = "selector"; st.rerun()

        # --- LOGIN PAGE ---
        elif st.session_state.page == "login":
            st.subheader("Sign In")
            u_email = st.text_input("Email")
            if st.button("Sign In", type="primary", use_container_width=True):
                # Simple check for this prototype: if email exists in users table
                user_check = supabase.table("users").select("*").eq("email", u_email).execute()
                if user_check.data:
                    st.session_state.user_type = "kiu" if user_check.data[0]['is_kiu_student'] else "public"
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Account not found. Please Sign Up.")
            if st.button("Back to Menu"):
                st.session_state.page = "selector"; st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# 6. MAIN APP
with st.sidebar:
    st.markdown("<span class='flux-brand'>Flux Menu</span>", unsafe_allow_html=True)
    role = st.radio("Navigation", ["📖 Courses", "🛠 Admin Dashboard"])
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.page = "selector"
        st.rerun()

# --- ADMIN DASHBOARD ---
if role == "🛠 Admin Dashboard":
    if st.sidebar.text_input("Password", type="password") != "flux": st.stop()
    
    t1, t2 = st.tabs(["Bulk Upload", "App Settings"])
    
    with t1:
        st.subheader("Bulk Content Upload")
        course_name = st.text_input("Program Name (e.g. ACCA)")
        file = st.file_uploader("Upload CSV/Excel", type=['xlsx', 'csv'])
        if file and course_name and st.button("Start Upload"):
            df = pd.read_excel(file) if "xlsx" in file.name else pd.read_csv(file)
            # FIX FOR APIERROR: Replace NaN with empty strings/None
            df = df.replace({np.nan: None}) 
            
            for _, row in df.iterrows():
                try:
                    supabase.table("materials").insert({
                        "course_program": course_name,
                        "course_name": str(row.get('Topic Covered', 'Untitled')),
                        "week": int(row.get('Week', 1)) if row.get('Week') else 1,
                        "video_url": str(row.get('Embeddable YouTube Video Link', '')),
                        "notes_url": str(row.get('link to Google docs Document', '')),
                        "image_url": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3"
                    }).execute()
                except Exception as e:
                    st.error(f"Error in row: {row.get('Topic Covered')}. Skip...")
            st.success("Upload Complete!")

    with t2:
        st.subheader("Login Page Settings")
        new_bg = st.text_input("Login Background Image URL (Google Drive/Docs Direct Link)")
        if st.button("Update Login Background"):
            supabase.table("portal_settings").upsert({"id": 1, "login_bg_url": new_bg}).execute()
            st.success("Background Updated!")

# --- COURSES PAGE ---
else:
    st.title("Flux Courses")
    data = supabase.table("materials").select("*").execute()
    if data.data:
        df = pd.DataFrame(data.data)
        for prog in df['course_program'].unique():
            with st.expander(f"📚 {prog}"):
                items = df[df['course_program'] == prog]
                for _, item in items.iterrows():
                    st.write(f"**Week {item['week']}: {item['course_name']}**")
                    if item['video_url']: st.video(item['video_url'])
