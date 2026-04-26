import streamlit as st
# from auth import require_auth
from visuals.skills import show as show_skills
from visuals.roles import show as show_roles, show_careers
from visuals.employer import show as show_employers
from visuals.jobdemand import show as show_demand, show_monthly
from visuals.sector import show as show_sectors

# require_auth()  # Blocks direct access if not logged in

st.set_page_config(layout="wide")

# ---------------------------------------------------------------
# Layout + hide sidebar + hide Streamlit header
# ---------------------------------------------------------------
st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none; }
        [data-testid="collapsedControl"] { display: none; }
        header[data-testid="stHeader"] { display: none; }
        .block-container {
            padding-top: 1rem !important;
            margin-top: 0rem !important;
            max-width: 100% !important;
            padding-left: 3rem !important;
            padding-right: 2rem !important;
        }
        div[data-testid="stTabs"] {
            margin-top: -1rem !important;
        }
        button[data-baseweb="tab"] p,
        button[data-baseweb="tab"],
        [data-testid="stTabs"] button p {
            font-size: 1.15rem !important;
            font-weight: 600 !important;
        }
        div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            padding: 0.75rem 1.5rem !important;
            height: 3rem !important;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------
# Logo + Title + Nav
# ---------------------------------------------------------------
logo_b64 = __import__('base64').b64encode(open('images/GradScope_Image.png', 'rb').read()).decode()

st.markdown(f"""
    <img src="data:image/png;base64,{logo_b64}"
         style="position: fixed; top: -25px; left: 5px; width: 180px; height: 180px; object-fit: contain; border-radius: 8px; z-index: 999; pointer-events: none;">
""", unsafe_allow_html=True)

_, spacer, nav1, nav2 = st.columns([0.05, 0.70, 0.1, 0.1])
with nav1:
    if st.button("Home", use_container_width=True):
        st.switch_page("Home.py")
with nav2:
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
    "Roles",
    "Employers",
    "Sectors",
    "Trends",
])

with tab1:
    with st.container(border=True):
        show_skills()

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            show_careers()
    with col2:
        with st.container(border=True):
            show_roles()

with tab3:
    with st.container(border=True):
        show_employers()

with tab4:
    with st.container(border=True):
        show_sectors()

with tab5:
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            show_monthly()
    with col2:
        with st.container(border=True):
            show_demand()
