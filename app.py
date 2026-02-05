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
    st.error("Database Connection Failed. Check your Supabase credentials.")
    st.stop()

# 2. UI CONFIG & SELECTIVE STYLING
st.set_page_config(page_title="Flux", layout="wide")
st.markdown("""
<style>
    /* Only the word 'Flux' gets Comic Sans */
    .flux-font {
        font-family: "Comic Sans MS", "Comic Sans", cursive, sans-serif;
        font-weight: bold;
        font-size: 1.5em;
        color: #007BFF;
    }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; padding: 10px; color: #666; font-size: 14px; background: white; border-top: 1px solid #eee; z-index: 999; }
    .video-container { position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; background: #000; border-radius: 8px; margin-bottom: 10px; }
    .video-container iframe { position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0; }
</style>
""", unsafe_allow_html=True)

# 3. LOGIN PAGE LOGIC
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'><span class='flux-font'>Flux</span></h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            st.subheader("Access Login")
            st.text_input("Username", key="login_user")
            st.text_input("Password", type="password", key="login_pass")
            if st.button("Login", use_container_width=True) or st.button("Skip & Browse", use_container_width=True):
                st.session_state.logged_in = True
                st.rerun()
    st.stop()

# 4. SIDEBAR NAVIGATION
role = st.sidebar.radio("Navigation", ["Student Portal", "Admin Dashboard", "President Board"])

# --- ADMIN DASHBOARD (Password Protected: flux) ---
if role == "Admin Dashboard":
    admin_pw = st.sidebar.text_input("Admin Password", type="password")
    if admin_pw != "flux":
        st.warning("Dashboard Locked. Enter 'flux' in the sidebar to proceed.")
        st.stop()

    st.header("Management Console")
    t1, t2, t3 = st.tabs(["Add Entry", "Bulk Upload", "Delete Content"])
    
    with t1:
        with st.form("manual_entry"):
            p = st.text_input("Course Name")
            t = st.text_input("Module Topic")
            w = st.number_input("Week Number", 1, 15)
            img = st.text_input("Image URL (Direct link for Tile)")
            v = st.text_input("YouTube Link")
            n = st.text_input("Notes Link")
            if st.form_submit_button("Save to Flux"):
                supabase.table("materials").insert({
                    "course_program": p, "course_name": t, "week": w, 
                    "video_url": v, "notes_url": n, "image_url": img
                }).execute()
                st.success("Successfully saved to database!")

    with t2:
        target_course = st.text_input("Target Course Name")
        target_img = st.text_input("Course Tile Image URL")
        f = st.file_uploader("Upload CSV/Excel", type=["xlsx", "csv"])
        if f and target_course and st.button("Start Bulk Upload"):
            df = pd.read_excel(f) if "xlsx" in f.name else pd.read_csv(f)
            for _, row in df.iterrows():
                supabase.table("materials").insert({
                    "course_program": target_course,
                    "course_name": str(row.get('Topic Covered', "No Title")),
                    "week": int(row.get('Week', 1)),
                    "video_url": str(row.get('Embeddable YouTube Video Link', "")),
                    "notes_url": str(row.get('link to Google docs Document', "")),
                    "image_url": target_img
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
elif role == "Student Portal":
    st.markdown("<h1><span class='flux-font'>Flux</span></h1>", unsafe_allow_html=True)
    
    # Keyword Search Logic
    search = st.text_input("🔍 Search Courses or Topics...").strip()
    
    # DISPLAY COURSE TILES
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
                else:
                    st.info("No Preview")
                st.markdown(f"<p style='text-align: center;'><b>{name}</b></p>", unsafe_allow_html=True)

    if search:
        st.write("---")
        # Search by both course name and module title
        res = supabase.table("materials").select("*")\
            .or_(f"course_program.ilike.%{search}%,course_name.ilike.%{search}%")\
            .order("week").execute()
            
        if res.data:
            for item in res.data:
                with st.expander(f"Week {item.get('week')} - {item.get('course_name')}"):
                    st.caption(f"Course: {item.get('course_program')}")
                    v_url = item.get('video_url', "")
                    if v_url and ("youtube.com" in v_url or "youtu.be" in v_url):
                        v_id = v_url.split("v=")[1].split("&")[0] if "v=" in v_url else v_url.split("/")[-1]
                        st.markdown(f'<div class="video-container"><iframe src="https://www.youtube.com/embed/{v_id}" allowfullscreen></iframe></div>', unsafe_allow_html=True)
                    if item.get('notes_url'):
                        st.link_button("Read Lecture Notes", item['notes_url'])
        else:
            st.info("No matching content found.")

st.markdown('<div class="footer">Built by KMT Dynamics</div>', unsafe_allow_html=True)
