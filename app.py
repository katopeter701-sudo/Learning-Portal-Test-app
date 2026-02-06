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
if 'current_course' not in st.session_state: st.session_state.current_course = None

# Hardcoded foundational course tiles
COURSE_TILES = {
    "Computer Science": "https://drive.google.com/uc?export=view&id=1-diy5YsO0TdGj73Y3SoC6FL8UWEJxy51",
    "ACCA": "https://drive.google.com/uc?export=view&id=1-diy5YsO0TdGj73Y3SoC6FL8UWEJxy51"
}

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
    .stApp {{ background-image: url("{bg_url}"); background-size: cover; background-attachment: fixed; }}
    
    h1, h2, h3, p, span, label, .stMarkdown {{ color: white !important; }}

    .login-box {{
        background-color: white; padding: 40px; border-radius: 15px;
        box-shadow: 0px 10px 40px rgba(0,0,0,0.4); max-width: 450px; margin: auto;
        text-align: center;
    }}
    .login-box h1, .login-box h2, .login-box h3, .login-box p, .login-box label {{ color: black !important; }}
    
    /* Login/Signup Hints (Placeholders) to Grey/Black */
    input::placeholder {{
        color: #333333 !important;
        opacity: 1;
    }}

    .flux-box {{ 
        background-color: #000; color: #fff !important; padding: 15px 30px; border-radius: 8px;
        font-family: "Comic Sans MS", cursive; font-weight: bold; font-size: 2.5em;
        display: inline-block; margin-bottom: 30px;
    }}
    
    .stTextInput label {{ color: white !important; }}
</style>
""", unsafe_allow_html=True)

# 5. AUTHENTICATION
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown('<div class="flux-box">flux</div>', unsafe_allow_html=True)
        
        if st.session_state.page == "selector":
            if st.button("Sign In", use_container_width=True): st.session_state.page = "login"; st.rerun()
            if st.button("Register", use_container_width=True): st.session_state.page = "signup"; st.rerun()
            if st.button("Public Access", use_container_width=True): 
                st.session_state.user_type = "public"; st.session_state.logged_in = True; st.rerun()

        elif st.session_state.page == "signup":
            name = st.text_input("Full Name", placeholder="Enter your full name")
            email = st.text_input("Email", placeholder="Enter your email address")
            if st.button("Create Account", use_container_width=True):
                supabase.table("users").insert({"full_name": name, "email": email}).execute()
                st.success("Success! Please Login.")
                st.session_state.page = "login"; st.rerun()
            if st.button("Back"): st.session_state.page = "selector"; st.rerun()

        elif st.session_state.page == "login":
            u_email = st.text_input("Email", placeholder="Enter your registered email")
            if st.button("Login", use_container_width=True):
                user = supabase.table("users").select("*").eq("email", u_email).execute()
                if user.data:
                    st.session_state.user_type = "kiu" if user.data[0].get('is_kiu_student') else "public"
                    st.session_state.logged_in = True; st.rerun()
                else: st.error("User not found.")
            if st.button("Back"): st.session_state.page = "selector"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# 6. MAIN NAVIGATION
role = st.sidebar.radio("Navigation", ["Learning Center", "Administrator"])

if role == "Administrator":
    if st.sidebar.text_input("Password", type="password") != "flux": st.stop()
    st.header("Admin Console")
    prog = st.text_input("Course Name")
    file = st.file_uploader("Upload CSV")
    if file and st.button("Upload"):
        df = pd.read_excel(file) if "xlsx" in file.name else pd.read_csv(file)
        df = df.replace({np.nan: None})
        for _, row in df.iterrows():
            supabase.table("materials").insert({
                "course_program": prog,
                "course_name": str(row.get('Topic Covered', 'No Title')),
                "week": int(pd.to_numeric(row.get('Week', 1), errors='coerce') or 1),
                "video_url": str(row.get('Embeddable YouTube Video Link', '')),
                "notes_url": str(row.get('Link to Google docs Document', ''))
            }).execute()
        st.success("Uploaded!")

else:
    # Handle Course Detailed View
    if st.session_state.current_course:
        if st.button("← Back to Learning Path"):
            st.session_state.current_course = None
            st.rerun()
        
        course_name = st.session_state.current_course
        st.title(f"Modules: {course_name}")
        
        res = supabase.table("materials").select("*").eq("course_program", course_name).execute()
        if res.data:
            for item in res.data:
                with st.expander(f"Week {item['week']}: {item['course_name']}"):
                    st.write("### Module Content")
                    if item.get('video_url'):
                        st.write("**Playlist Link / Video:**")
                        st.video(item['video_url'])
                    if item.get('notes_url'):
                        st.write("**Textbooks & Notes:**")
                        st.link_button("Open Textbook/Notes", item['notes_url'])
        else:
            st.info("No detailed modules found for this course yet.")

    else:
        st.title("My Learning Path")

        # 1. SEARCH BAR
        search = st.text_input("Search Database (e.g., ACCA, Computer Science)")
        if search and st.button("Explore Course"):
            st.session_state.current_course = search
            st.rerun()
        
        st.write("---")

        # 2. FOUNDATIONAL COURSES
        st.subheader("Foundation Courses")
        f1, f2 = st.columns(2)
        with f1:
            st.image(COURSE_TILES["Computer Science"], caption="Computer Science", use_container_width=True)
            st.video("https://youtu.be/TjPFZaMe2yw?si=vFV8DKTaoVVgGQ8j") 
            if st.button("View Computer Science Modules", key="cs_btn"):
                st.session_state.current_course = "Computer Science"
                st.rerun()
        with f2:
            st.image(COURSE_TILES["ACCA"], caption="ACCA", use_container_width=True)
            st.video("https://youtu.be/U-7THjkQdbg?si=QkDfHeJUws8h-79J")
            if st.button("View ACCA Modules", key="acca_btn"):
                st.session_state.current_course = "ACCA"
                st.rerun()

        st.write("---")
        st.info("Select a course above or search to view module titles, playlists, and textbooks.")
