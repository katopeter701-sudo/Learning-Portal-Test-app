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
    st.error("Database Connection Failed. Check credentials.")
    st.stop()

# 2. UI CONFIG & COMIC SANS STYLING
st.set_page_config(page_title="Flux Learning Portal", layout="wide")
st.markdown("""
<style>
    /* Global Font Change to Comic Sans */
    html, body, [class*="st-"] {
        font-family: "Comic Sans MS", "Comic Sans", cursive, sans-serif;
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
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>🚀 Flux Portal</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            st.subheader("Login Access")
            st.text_input("Username")
            st.text_input("Password", type="password")
            if st.button("Login", use_container_width=True) or st.button("Skip & Browse", use_container_width=True):
                st.session_state.logged_in = True
                st.rerun()
    st.stop()

# 4. SIDEBAR NAVIGATION
role = st.sidebar.radio("Navigation", ["Student Portal", "Admin Dashboard", "President Board"])

# --- ADMIN DASHBOARD ---
if role == "Admin Dashboard":
    st.header("Flux Management Console")
    t1, t2, t3 = st.tabs(["Add Entry", "Bulk Upload", "Delete Content"])
    
    with t1:
        with st.form("manual"):
            p = st.text_input("Course Name")
            t = st.text_input("Module Topic")
            w = st.number_input("Week Number", 1, 15)
            v = st.text_input("YouTube/Slide Link")
            n = st.text_input("Notes Link")
            if st.form_submit_button("Save to Portal"):
                supabase.table("materials").insert({
                    "course_program": p, "course_name": t, "week": w, "video_url": v, "notes_url": n
                }).execute()
                st.success("Module saved!")

    with t2:
        target = st.text_input("Target Course Name")
        f = st.file_uploader("Upload CSV/Excel", type=["xlsx", "csv"])
        if f and target and st.button("Start Bulk Upload"):
            df = pd.read_excel(f) if "xlsx" in f.name else pd.read_csv(f)
            for _, row in df.iterrows():
                supabase.table("materials").insert({
                    "course_program": target,
                    "course_name": str(row.get('Topic Covered', "Untitled")),
                    "week": int(row.get('Week', 1)),
                    "video_url": str(row.get('Embeddable YouTube Video Link', "")),
                    "notes_url": str(row.get('link to Google docs Document', ""))
                }).execute()
            st.success("Bulk Upload Finished!")

    with t3:
        data = supabase.table("materials").select("*").execute()
        if data.data:
            for item in data.data:
                c1, c2 = st.columns([4, 1])
                # FIXED KeyError by using .get()
                prog = item.get('course_program', 'Unknown')
                wk = item.get('week', '?')
                name = item.get('course_name', 'No Name')
                c1.write(f"**{prog}** | Wk {wk}: {name}")
                if c2.button("Delete", key=f"del_{item['id']}"):
                    supabase.table("materials").delete().eq("id", item['id']).execute()
                    st.rerun()

# --- STUDENT PORTAL ---
elif role == "Student Portal":
    st.title("🌊 Flux Learning Modules")
    
    # Keyword Search Logic
    search = st.text_input("🔍 Search by Course, Topic, or Keywords").strip()
    
    # DISPLAY ALL UNIQUE COURSE TITLES UPLOADED
    st.write("### Available Courses")
    course_list = supabase.table("materials").select("course_program").execute()
    if course_list.data:
        unique_courses = sorted(list(set([c['course_program'] for c in course_list.data if c['course_program']])))
        st.caption(" • ".join(unique_courses))
    
    if search:
        # Search multiple columns for the keyword
        res = supabase.table("materials").select("*")\
            .or_(f"course_program.ilike.%{search}%,course_name.ilike.%{search}%")\
            .order("week").execute()
            
        if res.data:
            for item in res.data:
                with st.expander(f"Week {item.get('week', '1')} - {item.get('course_name', 'Module')}"):
                    st.write(f"**Course:** {item.get('course_program')}")
                    raw_url = str(item.get('video_url', ""))
                    if "youtube.com" in raw_url or "youtu.be" in raw_url:
                        v_id = raw_url.split("v=")[1].split("&")[0] if "v=" in raw_url else raw_url.split("/")[-1]
                        st.markdown(f'<div class="video-container"><iframe src="https://www.youtube.com/embed/{v_id}" allowfullscreen></iframe></div>', unsafe_allow_html=True)
                    if item.get('notes_url'):
                        st.link_button("Read Lecture Notes", item['notes_url'])
        else:
            st.info("No matches found.")
    else:
        st.info("Enter a keyword above to see specific modules.")

st.markdown('<div class="footer">Built by KMT Dynamics</div>', unsafe_allow_html=True)
