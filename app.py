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
bg_url = "https://images.unsplash.com/photo-1497366216548-37526070297c"
try:
    bg_query = supabase.table("portal_settings").select("login_bg_url").eq("id", 1).execute()
    if bg_query.data: bg_url = bg_query.data[0]['login_bg_url']
except: pass

# 4. ADVANCED MODERN UI & NAVIGATION STYLING
st.set_page_config(page_title="Flux | Modern Portal", layout="wide")

st.markdown(f"""
<style>
    /* REMOVE TOP WHITE BAR */
    header[data-testid="stHeader"] {{ visibility: hidden; height: 0%; }}
    
    /* Global Background */
    .stApp {{ background-image: url("{bg_url}"); background-size: cover; background-attachment: fixed; }}
    
    /* Glassmorphism Sidebar */
    [data-testid="stSidebar"] {{
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(15px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(15px) saturate(180%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.2) !important;
    }}
    
    /* Navigation Link Styling */
    .stRadio > div {{ gap: 15px; padding-top: 20px; }}
    .stRadio label {{
        background: rgba(255, 255, 255, 0.8);
        padding: 12px 20px !important;
        border-radius: 10px !important;
        border: 1px solid rgba(0,0,0,0.05) !important;
        transition: all 0.3s ease !important;
        font-weight: 500 !important;
    }}
    .stRadio label:hover {{ transform: translateX(5px); background: #fff !important; }}

    /* Modern Login Box */
    .login-box {{
        background-color: white; padding: 50px; border-radius: 20px;
        box-shadow: 0px 20px 50px rgba(0,0,0,0.5); max-width: 450px; margin: auto;
        text-align: center;
    }}
    .kmt-header {{ font-size: 10px; color: #aaa; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 2px; font-weight: 600; }}
    .flux-box {{ 
        background-color: #000; color: #fff; padding: 18px 40px; border-radius: 12px;
        font-family: "Comic Sans MS", cursive; font-weight: bold; font-size: 2.8em;
        display: inline-block; margin-bottom: 40px; box-shadow: 0 10px 20px rgba(0,0
