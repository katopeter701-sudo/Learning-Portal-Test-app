import streamlit as st
import pandas as pd
from supabase import create_client

# 1. DATABASE CONNECTION
PROJECT_ID = "uxtmgdenwfyuwhezcleh" [cite: 5]
SUPABASE_URL = f"https://{PROJECT_ID}.supabase.co" [cite: 6]
SUPABASE_KEY = "sb_publishable_1BIwMEH8FVDv7fFafz31uA_9FqAJr0-" [cite: 7]

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY) [cite: 9]
except Exception:
    st.error("Database Connection Failed. Check your Supabase credentials.") [cite: 11]
    st.stop() [cite: 12]

# 2. UI CONFIG & CSS STYLING
st.set_page_config(page_title="KIU Q10 Portal", layout="wide") [cite: 14]
st.markdown("""
<style>
.footer { position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; padding: 10px; color: #666; font-size: 14px; background: white; border-top: 1px solid #eee; z-index: 999; }
.video-container { position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; background: #000; border-radius: 8px; margin-bottom: 10px; }
.video-container iframe { position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0; }
</style>
""", unsafe_allow_html=True) [cite: 15-21]

# 3. LOGIN PAGE LOGIC
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False [cite: 23-24]

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'> KIU Q10 Portal</h1>", unsafe_allow_html=True) [cite: 26]
    col1, col2, col3 = st.columns([1, 1.5, 1]) [cite: 27]
    with col2:
        with st.container(border=True):
            st.subheader("Login Access") [cite: 30]
            st.text_input("Username") [cite: 31]
            st.text_input("Password", type="password") [cite: 32]
            if st.button("Login", use_container_width=True) or st.button(" Skip & Browse", use_container_width=True): [cite: 33]
                st.session_state.logged_in = True [cite: 34]
                st.rerun() [cite: 35]
    st.markdown('<div class="footer">Built by KMT Dynamics</div>', unsafe_allow_html=True) [cite: 36]
    st.stop() [cite: 37]

# 4. SIDEBAR NAVIGATION
role = st.sidebar.radio("Navigation", ["Student Portal", "Admin Dashboard", "President Board"]) [cite: 39]

# --- ADMIN DASHBOARD ---
if role == "Admin Dashboard":
    st.header(" Management Console") [cite: 42]
    t1, t2, t3 = st.tabs([" Add Entry", "Bulk Upload", "Delete Content"]) [cite: 44]
    
    with t1:
        with st.form("manual"):
            p = st.text_input("Course Name") [cite: 47]
            t = st.text_input("Module Topic") [cite: 48]
            w = st.number_input("Week Number", 1, 15) [cite: 49]
            v = st.text_input("YouTube/Slide Link") [cite: 50]
            n = st.text_input("Notes Link") [cite: 51]
            if st.form_submit_button("Save to Portal"):
                supabase.table("materials").insert({
                    "course_program": p, "course_name": t, "week": w, "video_url": v, "notes_url": n
                }).execute() [cite: 53-59]
                st.success("Module saved successfully!") [cite: 60]

    with t2:
        target = st.text_input("Target Course Name (e.g. Petroleum Engineering)") [cite: 62]
        wipe = st.checkbox("Wipe current data for this course before upload?") [cite: 62]
        f = st.file_uploader("Upload CSV/Excel", type=["xlsx", "csv"]) [cite: 63]
        if f and target and st.button(" Start Bulk Upload"):
            if wipe:
                supabase.table("materials").delete().eq("course_program", target).execute() [cite: 66]
            df = pd.read_excel(f) if "xlsx" in f.name else pd.read_csv(f) [cite: 67]
            for index, row in df.iterrows(): [cite: 70]
                supabase.table("materials").insert({
                    "course_program": target,
                    "course_name": str(row.get('Topic Covered', "")),
                    "week": int(row.get('Week', 1)),
                    "video_url": str(row.get('Embeddable YouTube Video Link', "")),
                    "notes_url": str(row.get('link to Google docs Document', ""))
                }).execute() [cite: 71-77]
            st.success("Bulk Upload Finished!") [cite: 78]

    with t3:
        data = supabase.table("materials").select("*").execute() [cite: 80]
        if data.data:
            for item in data.data:
                c1, c2 = st.columns([4, 1]) [cite: 83]
                c1.write(f"**{item['course_program']}** | Wk {item['week']}: {item['course_name']}") [cite: 84]
                if c2.button("Delete", key=f"del_{item['id']}"): [cite: 86]
                    supabase.table("materials").delete().eq("id", item['id']).execute() [cite: 87]
                    st.rerun() [cite: 88]

# PRESIDENT BOARD
elif role == "President Board":
    st.header(" Post Announcements") [cite: 91]
    with st.form("notice"):
        tt = st.text_input("Notice Title") [cite: 93]
        mm = st.text_area("Detailed Message") [cite: 94]
        if st.form_submit_button("Publish Now"): [cite: 95]
            supabase.table("notices").insert({"title": tt, "content": mm}).execute() [cite: 96]
            st.success("Notice published to all students!") [cite: 97]

# --- STUDENT PORTAL
elif role == "Student Portal":
    st.title(" Learning Modules") [cite: 100]
    search = st.text_input(" Search for your Course (e.g. 'Petroleum Engineering')").strip() [cite: 101]
    if search:
        res = supabase.table("materials").select("*").ilike("course_program", f"%{search}%").order("week").execute() [cite: 103]
        if res.data:
            for item in res.data:
                with st.expander(f" Week {item['week']} - {item['course_name']}"): [cite: 106]
                    raw_url = str(item.get('video_url', "")) [cite: 107]
                    if "youtube.com" in raw_url or "youtu.be" in raw_url: [cite: 110]
                        v_id = raw_url.split("v=")[1].split("&")[0] if "v=" in raw_url else raw_url.split("/")[-1] [cite: 111]
                        embed_url = f"https://www.youtube.com/embed/{v_id}" [cite: 112]
                        st.markdown(f'<div class="video-container"><iframe src="{embed_url}" allowfullscreen></iframe></div>', unsafe_allow_html=True) [cite: 113-114]
                    elif "docs.google.com" in raw_url: [cite: 117]
                        slide_url = raw_url.replace("/edit", "/embed") [cite: 119]
                        st.markdown(f'<div class="video-container"><iframe src="{slide_url}"></iframe></div>', unsafe_allow_html=True) [cite: 120-121]
                    
                    if item.get('notes_url'): [cite: 123]
                        st.link_button(" Read Lecture Notes", item['notes_url']) [cite: 125]
    else:
        st.info("Search for a course to view available weeks.") [cite: 126]
    st.markdown('<div class="footer">Built by KMT Dynamics</div>', unsafe_allow_html=True) [cite: 127]
