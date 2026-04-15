import streamlit as st
# from auth import require_auth
from visuals.skills import show as show_skills
from visuals.roles import show as show_roles, show_careers
from visuals.employer import show as show_employers
from visuals.jobdemand import show as show_demand, show_monthly
from visuals.sector import show as show_sectors

# require_auth()  # Blocks direct access if not logged in

# ---------------------------------------------------------------
# Layout + hide sidebar
# ---------------------------------------------------------------
st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none; }
        [data-testid="collapsedControl"] { display: none; }
        .block-container {
            padding-top: 2.0rem !important;
            margin-top: 0rem !important;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------
# Logo + Title + Nav
# ---------------------------------------------------------------
logo_b64 = __import__('base64').b64encode(open('images/GradScope_Image.png', 'rb').read()).decode()

col1, spacer, nav1, nav2 = st.columns([0.15, 0.3, 0.15, 0.15]) #col2 with 0.25
with col1:
     st.markdown(f"""
        <img src="data:image/png;base64,{logo_b64}" 
             style="width: 120px; height: 120px; object-fit: contain; border-radius: 10px; margin-top: -30px; margin-left: -20px;">
    """, unsafe_allow_html=True)
# with col2:
#     st.markdown("<h4 style='margin: 0; padding-top: 10px; font-weight: 600;'>GradScope</h4>", unsafe_allow_html=True)
with nav1:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Home", use_container_width=True):
        st.switch_page("Home.py")
with nav2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Dashboard", use_container_width=True):
        st.switch_page("pages/Dashboard.py")

# ---------------------------------------------------------------
# Global card styling
# ---------------------------------------------------------------
st.markdown("""
    <style>
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 12px;
        padding: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------
# Initialise all visual session states
# ---------------------------------------------------------------
for key, default in [
    ("skill_page", "category"),
    ("roles_page", "overview"),
    ("careers_page", "treemap"),
    ("employers_page", "overview"),
    ("sectors_page", "overview"),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ---------------------------------------------------------------
# Centralised cursor control
# ---------------------------------------------------------------
on_final_level = (
    st.session_state.get("skill_page") == "trend" or
    st.session_state.get("roles_page") == "trend" or
    st.session_state.get("careers_page") == "job_detail" or
    st.session_state.get("employers_page") == "company_detail" or
    st.session_state.get("sectors_page") == "detail"
)

cursor = "default" if on_final_level else "pointer"

st.markdown(f"""
<style>
    [data-testid="stPlotlyChart"],
    [data-testid="stPlotlyChart"] *,
    [data-testid="stPlotlyChart"] iframe {{
        cursor: {cursor} !important;
    }}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------
# Tabbed Layout
# ---------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Skills",
    "Jobs & Roles",
    "Employers",
    "Sectors",
    "Trends",
])

with tab1:
    with st.container(border=True):
        show_skills()

with tab2:
     with st.container(border=True):
        show_careers()
     with st.container(border=True):
        show_roles()

with tab3:
    with st.container(border=True):
        show_employers()

with tab4:
    with st.container(border=True):
        show_sectors()

with tab5:
    with st.container(border=True):
        show_monthly()
        
    with st.container(border=True):
        show_demand()