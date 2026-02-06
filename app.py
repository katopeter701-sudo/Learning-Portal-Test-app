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

# 2. SESSION STATE & UI CONFIG 
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Hardcoded Image Tiles for specified courses
COURSE_TILES = {
    "ACCA": "https://drive.google.com/file/d/1-diy5YsO0TdGj73Y3SoC6FL8UWEJxy51/view?usp=sharing",
    "Computer Science": "https://drive.google.com/file/d/1-diy5YsO0TdGj73Y3SoC6FL8UWEJxy51/view?usp=sharing"
}

st.set_page_config(page_title="KIU Q10 Portal", layout="wide", page_icon="🎓") [cite: 2]

# 3. LOGIN PAGE 
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>🎓 KIU Q10 Portal</h1>", unsafe_allow_html=True) [cite: 2]
    col1, col2, col3 = st.columns([1,1.5,1]) [cite: 2]
    with col2:
        with st.container(border=True): [cite: 2]
            st.subheader("Login Access") [cite: 2]
            st.text_input("Username") [cite: 2]
            st.text_input("Password", type="password") [cite: 2]
            if st.button("Login", use_container_width=True) or st.button("⏭️ Skip & Browse", use_container_width=True): [cite: 2]
                st.session_state.logged_in = True [cite: 2]
                st.rerun() [cite: 2]
    st.stop() [cite: 2]

# 4. SIDEBAR NAVIGATION 
role = st.sidebar.radio("Navigation", ["Student Portal", "Admin Dashboard", "President Board"]) [cite: 2]

# --- ADMIN DASHBOARD --- 
if role == "Admin Dashboard":
    st.header("🛠️ Management Console") [cite: 2]
    t1, t2, t3 = st.tabs(["➕ Add Entry", "📊 Bulk Upload", "🗑️ Delete Content"]) [cite: 2]
    
    with t1:
        with st.form("manual"): [cite: 2]
            p = st.text_input("Course Name") [cite: 2]
            t = st.text_input("Module Topic") [cite: 2]
            w = st.number_input("Week Number", 1, 15) [cite: 2]
            y = st.text_input("YouTube/Slide Link") [cite: 2]
            n = st.text_input("Notes Link") [cite: 2]
            if st.form_submit_button("Save to Portal"): [cite: 2]
                supabase.table("materials").insert({"course_program": p, "course_name": t, "week": w, "video_url": y, "notes_url": n}).execute() [cite: 2]
                st.success("Module saved successfully!") [cite: 2]

    with t2:
        target = st.text_input("Target Course Name") [cite: 2]
        f = st.file_uploader("Upload CSV/Excel", type=["xlsx", "csv"]) [cite: 2]
        if f and target and st.button("🚀 Start Bulk Upload"): [cite: 2]
            df = pd.read_excel(f) if "xlsx" in f.name else pd.read_csv(f) [cite: 2]
            for _, row in df.iterrows():
                supabase.table("materials").insert({
                    "course_program": target,
                    "course_name": str(row.get('Topic Covered', '')),
                    "week": int(row.get('Week', 1)),
                    "video_url": str(row.get('Embeddable YouTube Video Link', '')),
                    "notes_url": str(row.get('link to Google docs Document', ''))
                }).execute() [cite: 2]
            st.success("Bulk Upload Finished!") [cite: 2]

    with t3:
        data = supabase.table("materials").select("*").execute() [cite: 2]
        if data.data:
            for item in data.data:
                c1, c2 = st.columns([4, 1]) [cite: 2]
                c1.write(f"**{item['course_program']}** | Wk {item['week']}: {item['course_name']}") [cite: 2]
                if c2.button("🗑️ Delete", key=f"del_{item['id']}"): [cite: 2]
                    supabase.table("materials").delete().eq("id", item['id']).execute() [cite: 2]
                    st.rerun() [cite: 2]

# --- PRESIDENT BOARD --- 
elif role == "President Board":
    st.header("📢 Post Announcements") [cite: 2]
    with st.form("notice"): [cite: 2]
        tt = st.text_input("Notice Title") [cite: 2]
        mm = st.text_area("Detailed Message") [cite: 2]
        if st.form_submit_button("Publish Now"): [cite: 2]
            supabase.table("notices").insert({"title": tt, "content": mm}).execute() [cite: 2]
            st.success("Notice published to all students!") [cite: 2]

# --- STUDENT PORTAL --- 
else:
    st.title("📖 Learning Modules") [cite: 2]
    search = st.text_input("🔍 Search for your Course (e.g. 'ACCA')").strip() [cite: 2]
    
    if search:
        # Display hardcoded image tile if course matches 
        if search in COURSE_TILES:
            st.image(COURSE_TILES[search], caption=f"{search} Image Tile", use_container_width=True)
            
        res = supabase.table("materials").select("*").ilike("course_program", f"%{search}%").order("week").execute() [cite: 2]
        if res.data:
            for item in res.data:
                with st.expander(f"📚 Week {item['week']} - {item['course_name']}"): [cite: 2]
                    raw_url = str(item.get('video_url', '')) [cite: 2]
                    if "youtube.com" in raw_url or "youtu.be" in raw_url: [cite: 2]
                        v_id = raw_url.split("v=")[1].split("&")[0] if "v=" in raw_url else raw_url.split("/")[-1] [cite: 2]
                        st.video(f"https://www.youtube.com/watch?v={v_id}") [cite: 2]
                    if item.get('notes_url'): [cite: 2]
                        st.link_button("📝 Read Lecture Notes", item['notes_url']) [cite: 2]
        else:
            st.warning("No materials found for this course.") [cite: 2]
    else:
        st.info("Search for a course to view available modules.") [cite: 2]

st.markdown('<div class="footer">Built by KMT Dynamics</div>', unsafe_allow_html=True) [cite: 2]
