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

# 2. SAFE FETCH SETTINGS (Prevents crash if table is empty)
bg_url = "https://images.unsplash.com/photo-1497366216548-37526070297c" 
try:
    bg_query = supabase.table("portal_settings").select("login_bg_url").eq("id", 1).execute()
    if bg_query.data:
        bg_url = bg_query.data[0]['login_bg_url']
except Exception:
    pass 

# 3. UI CONFIG & ADVANCED STYLING
st.set_page_config(page_title="Flux", layout="wide")

# CSS for login background, high-contrast visibility, and branding
if not st.session_state.get('logged_in', False):
    st.markdown(f"""
    <style>
        .stApp {{
            background-image: url("{bg_url}");
            background-size: cover;
            background-attachment: fixed;
        }}
        .login-box {{
            background-color: rgba(255, 255, 255, 0.95);
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0px 10px 30px rgba(0,0,0,0.5);
            color: black !important;
        }}
        /* VISIBILITY FIX: Ensuring all hints and labels are black and bold */
        .stTextInput label, .stHeader, .login-box h2 {{
            color: black !important;
            font-weight: bold !important;
        }}
        input::placeholder {{
            color: #555 !important;
        }}
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
<style>
    /* Small Black Flux Branding */
    .flux-font {
        font-family: "Comic Sans MS", "Comic Sans", cursive, sans-serif;
        font-weight: bold;
        font-size: 0.9em;
        color: black;
    }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; padding: 10px; color: #666; font-size: 14px; background: white; border-top: 1px solid #eee; z-index: 999; }
    
    /* Navigation/Sidebar Appearance */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# 4. LOGIN PAGE LOGIC
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'><span class='flux-font'>Flux</span></h2>", unsafe_allow_html=True)
        st.text_input("Username", key="l_user", placeholder="Enter your username")
        st.text_input("Password", type="password", key="l_pass", placeholder="Enter your password")
        
        # Syntax Error Fixed (Button text on one line)
        if st.button("Login", use_container_width=True) or st.button("Skip & Browse", use_container_width=True):
            st.session_state.logged_in = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# 5. IMPROVED SIDEBAR NAVIGATION
with st.sidebar:
    st.markdown(f"### <span class='flux-font'>Flux</span> Menu", unsafe_allow_html=True)
    st.write("---")
    role = st.radio(
        "Navigation:",
        ["📖 Student Portal", "🛠 Admin Dashboard"],
        index=0,
        key="nav_menu"
    )
    st.write("---")
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

# --- ADMIN DASHBOARD ---
if "Admin Dashboard" in role:
    admin_pw = st.sidebar.text_input("Confirm Admin Access", type="password")
    if admin_pw != "flux":
        st.warning("Locked. Enter 'flux' in the sidebar to proceed.")
        st.stop()

    st.header("Management Console")
    t1, t2, t3, t4 = st.tabs(["Add Entry", "Bulk Upload", "Delete Content", "App Settings"])
    
    with t4:
        st.subheader("Login Page Customization")
        new_bg = st.text_input("New Background Image URL", value=bg_url)
        if st.button("Update Background"):
            supabase.table("portal_settings").upsert({"id": 1, "login_bg_url": new_bg}).execute()
            st.success("Background Updated!")

    with t1:
        with st.form("manual"):
            p = st.text_input("Course Name")
            t = st.text_input("Module Topic")
            w = st.number_input("Week Number", 1, 15)
            img = st.text_input("Image URL (for Tile)")
            v = st.text_input("YouTube Link")
            n = st.text_input("Notes Link")
            if st.form_submit_button("Save to Flux"):
                supabase.table("materials").insert({
                    "course_program": p, "course_name": t, "week": w, 
                    "video_url": v, "notes_url": n, "image_url": img
                }).execute()
                st.success("Successfully saved!")

    with t2:
        target_course = st.text_input("Target Course Name")
        target_img = st.text_input("Course Tile Image URL")
        f = st.file_uploader("Upload CSV/Excel", type=["xlsx", "csv"])
        if f and target_course and st.button("Start Bulk Upload"):
            df = pd.read_excel(f) if "xlsx" in f.name else pd.read_csv(f)
            # Sanitized bulk upload to prevent APIErrors
            for _, row in df.iterrows():
                supabase.table("materials").insert({
                    "course_program": str(target_course),
                    "course_name": str(row.get('Topic Covered', "No Title")),
                    "week": int(pd.to_numeric(row.get('Week', 1), errors='coerce') or 1),
                    "video_url": str(row.get('Embeddable YouTube Video Link', "")),
                    "notes_url": str(row.get('link to Google docs Document', "")),
                    "image_url": str(target_img)
                }).execute()
            st.success("Bulk Upload Finished!")

    with t3:
        data = supabase.table("materials").select("*").execute()
        if data.data:
            for item in data.data:
                c1, c2 = st.columns([4, 1])
                c1.write(f"**{item.get('course_program')}** | Wk {item.get('week')}: {item.get('course_name')}")
                if c2.button("Delete", key=f"del_{item['id']}"):
                    supabase.table("materials").delete().eq("id", item['id']).execute()
                    st.rerun()

# --- STUDENT PORTAL ---
else:
    st.markdown("<h1><span class='flux-font'>Flux</span></h1>", unsafe_allow_html=True)
    search = st.text_input("🔍 Search Courses...").strip()
    
    st.write("### Courses")
    course_list = supabase.table("materials").select("course_program, image_url").execute()
    if course_list.data:
        unique_courses = {}
        for c in course_list.data:
            cp = c.get('course_program')
            if cp and cp not in unique_courses:
                unique_courses[cp] = c.get('image_url')

        cols = st.columns(4)
        for i, (name, img_url) in enumerate(unique_courses.items()):
            with cols[i % 4]:
                if img_url:
                    st.image(img_url, use_container_width=True)
                st.markdown(f"<p style='text-align: center;'><b>{name}</b></p>", unsafe_allow_html=True)

    if search:
        st.write("---")
        res = supabase.table("materials").select("*").or_(f"course_program.ilike.%{search}%,course_name.ilike.%{search}%").order("week").execute()
        if res.data:
            for item in res.data:
                with st.expander(f"Week {item.get('week')} - {item.get('course_name')}"):
                    v_url = item.get('video_url', "")
                    if v_url and ("youtube.com" in v_url or "youtu.be" in v_url):
                        v_id = v_url.split("v=")[1].split("&")[0] if "v=" in v_url else v_url.split("/")[-1]
                        st.markdown(f'<div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; background: #000; border-radius: 8px; margin-bottom: 10px;"><iframe src="https://www.youtube.com/embed/{v_id}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;" allowfullscreen></iframe></div>', unsafe_allow_html=True)
                    if item.get('notes_url'):
                        st.link_button("Read Lecture Notes", item['notes_url'])

st.markdown('<div class="footer">Built by KMT Dynamics</div>', unsafe_allow_html=True)
