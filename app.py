# --- STUDENT PORTAL ---
else:
    st.title("🌊 My Learning Path")

    # --- 1. HARD-CODED NATIVE COURSES ---
    st.subheader("🚀 Foundation Courses")
    f_col1, f_col2 = st.columns(2)

    with f_col1:
        st.markdown("### Course 1: Playlist Title")
        # PASTE YOUR FIRST PLAYLIST LINK BELOW
        st.video("https://www.youtube.com/watch?v=your_video_id") 
        st.write("This is a native foundation course available to all users.")

    with f_col2:
        st.markdown("### Course 2: Playlist Title")
        # PASTE YOUR SECOND PLAYLIST LINK BELOW
        st.video("https://www.youtube.com/watch?v=your_video_id")
        st.write("This is a native foundation course available to all users.")

    st.write("---")

    # --- 2. SEARCH BAR ---
    search_query = st.text_input("🔍 Search Database", placeholder="Search for uploaded materials...")

    # --- 3. DYNAMIC DATABASE CONTENT ---
    try:
        data = supabase.table("materials").select("*").execute()
        if data.data:
            df = pd.DataFrame(data.data)
            
            # Apply Search Filter if query exists
            if search_query:
                df = df[df['course_name'].str.contains(search_query, case=False, na=False) | 
                        df['course_program'].str.contains(search_query, case=False, na=False)]

            if not df.empty:
                for prog in df['course_program'].unique():
                    st.subheader(f"📂 {prog}")
                    items = df[df['course_program'] == prog]
                    cols = st.columns(3)
                    for i, (_, item) in enumerate(items.iterrows()):
                        with cols[i % 3]:
                            week = item.get('week', '1')
                            name = item.get('course_name', 'Lesson')
                            with st.expander(f"Week {week}: {name}"):
                                if item.get('video_url'): st.video(item['video_url'])
                                if item.get('notes_url'): st.link_button("View Notes", item['notes_url'])
            else:
                st.info("No matching results found in the database.")
    except Exception as e:
        st.error(f"Database error: {e}")
