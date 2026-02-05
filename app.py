import streamlit as st
import pandas as pd
from supabase import create_client

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

# 3. STYLING
st.set_page_config(page_title="Flux | KIU", layout="wide")

def apply_styles():
    st.markdown("""
    <style>
        .stApp { background-color: #f4f4f4; }
        .login-box {
            background-color: white; padding: 40px; border-radius: 2px;
            box-shadow: 0px 2px 10px rgba(0,0,0,0.1); text-align: center;
            max-width: 450px; margin: auto; border: 1px solid #ddd;
        }
        .kiu-btn { 
            background-color: #3eb46d !important; color: white !important; 
            font-weight: bold !important; width: 100%; border-radius: 4px !important;
        }
        .flux-brand { font-family: "Comic Sans MS"; font-weight: bold; color: black; font-size: 0.9em; }
    </style>
    """, unsafe_allow_html=True)

apply_styles()

# 4. PAGE: SELECTOR
if st.session_state.page == "selector" and not st.session_state.logged_in:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.image("https://kiu.ac.ug/assets/images/logo.png", width=200)
        st.write("### Welcome to Flux")
        if st.button("I am a KIU Student", use_container_width=True):
            st.session_state.page = "kiu_login"
            st.rerun()
        if st.button("I am not a KIU Student", use_container_width=True):
            st.session_state.user_type = "public"
            st.session_state.logged_in = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# 5. PAGE: KIU LOGIN (Styled like screenshot)
if st.session_state.page == "kiu_login" and not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.image("https://kiu.ac.ug/assets/images/logo.png", width=200)
        st.markdown("#### **Student Portal**")
        reg = st.text_input("", placeholder="Email or Registration number")
        if st.button("Next", type="primary", use_container_width=True):
            if reg:
                st.session_state.user_type = "kiu"
                st.session_state.logged_in = True
                st.rerun()
        st.markdown("""<p style='font-size: 13px; color: #777; margin-top: 15px;'>
            Please use your registration number or KIU student email address to login.</p>""", unsafe_allow_html=True)
        if st.button("← Back", key="back"):
            st.session_state.page = "selector"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# 6. APP CONTENT
with st.sidebar:
    st.markdown("<span class='flux-brand'>Flux Menu</span>", unsafe_allow_html=True)
    menu = ["📖 Student Portal", "🛠 Admin Dashboard"]
    choice = st.radio("Navigation", menu)
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.page = "selector"
        st.rerun()

# --- ADMIN DASHBOARD ---
if choice == "🛠 Admin Dashboard":
    pw = st.sidebar.text_input("Password", type="password")
    if pw != "flux": st.stop()
    
    st.header("Admin Console")
    t1, t2 = st.tabs(["Manual Entry", "Bulk Upload (Your Format)"])
    
    with t2:
        target_course = st.text_input("Course Name (e.g., ACCA Financial Accounting)")
        target_img = st.text_input("Course Image URL")
        file = st.file_uploader("Upload Excel/CSV", type=['xlsx', 'csv'])
        if file and target_course and st.button("Execute Bulk Upload"):
            df = pd.read_excel(file) if "xlsx" in file.name else pd.read_csv(file)
            for _, row in df.iterrows():
                # Mapping specifically to your uploaded file format
                supabase.table("materials").insert({
                    "course_program": target_course,
                    "course_name": str(row.get('Topic Covered', 'No Title')),
                    "week": int(pd.to_numeric(row.get('Week', 1), errors='coerce') or 1),
                    "video_url": str(row.get('Embeddable YouTube Video Link', '')),
                    "notes_url": str(row.get('link to Google docs Document', '')),
                    "image_url": target_img
                }).execute()
            st.success(f"Uploaded {len(df)} topics to {target_course}")

# --- STUDENT PORTAL ---
else:
    st.markdown(f"<h1><span class='flux-brand'>Flux</span> Student Portal</h1>", unsafe_allow_html=True)
    # Logic to filter content based on user type
    filter_val = "ACCA" if st.session_state.user_type == "public" else ""
    
    query = supabase.table("materials").select("*")
    if filter_val:
        query = query.ilike("course_program", f"%{filter_val}%")
    
    data = query.execute()
    if data.data:
        df = pd.DataFrame(data.data)
        for course in df['course_program'].unique():
            st.subheader(course)
            course_data = df[df['course_program'] == course]
            cols = st.columns(3)
            for i, (_, item) in enumerate(course_data.iterrows()):
                with cols[i % 3]:
                    with st.expander(f"Week {item['week']}: {item['course_name']}"):
                        if item['video_url']:
                            st.video(item['video_url'])
                        if item['notes_url']:
                            st.link_button("View Notes", item['notes_url'])
