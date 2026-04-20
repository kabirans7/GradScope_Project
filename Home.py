import streamlit as st
# from auth import init_auth_state, render_auth_router, logout_button_top_right

st.set_page_config(page_title="GradScope", page_icon=":bar_chart:", layout="wide", initial_sidebar_state="expanded")

def local_css(file_name: str):
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"CSS file not found: {file_name}")

# init_auth_state()

# URL Routing for reset password
params = st.query_params
if params.get("page") == "reset":
    st.session_state["auth_view"] = "reset"
    st.session_state["reset_token"] = params.get("token", "")

# Global CSS
st.markdown("<style>img{border-radius:15px;}</style>", unsafe_allow_html=True)
local_css("style/style.css")


# # Authentication gate
# if not st.session_state.authenticated:
#     render_auth_router()
#     st.stop()

# ---------------------------------------------------------------
# Layout + hide sidebar
# ---------------------------------------------------------------
# logout_button_top_right()

st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none; }
        [data-testid="collapsedControl"] { display: none; }
        .block-container {
            padding-top: 1.5rem !important;
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

# # ---------------------------------------------------------------
# # Welcome content
# # ---------------------------------------------------------------
# col1, col2 = st.columns([1.2, 2])

# with col1:
#     st.markdown("")

# with col2:
#     st.title("WELCOME TO GRADSCOPE!")
#     st.subheader("A Real-Time Data Dashboard Analysing The Graduate Employment Market")
#     st.markdown("""
# Gradscope transforms fragmented labour-market data into clear insights to
# help students and universities understand emerging skills, roles and employer demand.
# """)
#     st.divider()

#     st.header("Who is this for?")
#     colA, colB, colC = st.columns(3)
#     with colA:
#         st.info("**Students**")
#     with colB:
#         st.info("**Careers**")
#     with colC:
#         st.info("**Academics**")

# ---------------------------------------------------------------
# Welcome content
# ---------------------------------------------------------------
st.markdown(f"""
    <style>
        .hero {{
            text-align: center;
            padding: 3rem 0 1.5rem 0;
        }}
        .hero h1 {{
            font-size: 2.8rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
        }}
        .hero h3 {{
            font-weight: 500;
            opacity: 0.85;
            margin-bottom: 1rem;
        }}
        .hero p {{
            opacity: 0.75;
            font-size: 1rem;
            max-width: 620px;
            margin: 0 auto 1.5rem auto;
        }}
        .content h2 {{
            text-align: center;
            margin-bottom: 1.5rem;
        }}
        .card-row {{
            display: flex;
            justify-content: center;
            gap: 1.5rem;
            margin-top: 1rem;
            padding-bottom: 5rem;
        }}
        .card {{
            background-color: #0a2a45;
            border: 1px solid #1a4a6e;
            border-radius: 14px;
            padding: 1.5rem;
            width: 220px;
            height: 80px;
            text-align: center;
            position: relative;
            cursor: default;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .card:hover {{
            transform: translateY(-6px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.4);
        }}
        .card .label {{
            font-weight: 700;
            font-size: 1.05rem;
        }}
        .card .tooltip {{
            visibility: hidden;
            opacity: 0;
            background-color: #1a4a6e;
            color: #fff;
            text-align: left;
            border-radius: 10px;
            padding: 0.75rem 1rem;
            position: absolute;
            top: 110%;
            left: 50%;
            transform: translateX(-50%);
            width: 250px;
            font-size: 0.85rem;
            line-height: 1.6;
            box-shadow: 0 4px 16px rgba(0,0,0,0.3);
            transition: opacity 0.2s ease;
            z-index: 999;
        }}
        .card:hover .tooltip {{
            visibility: visible;
            opacity: 1;
        }}
    </style>

    <div class="hero">
        <h1>WELCOME TO GRADSCOPE!</h1>
        <h3>A Real-Time Data Dashboard Analysing The Graduate Employment Market</h3>
        <p>Gradscope transforms fragmented labour-market data into clear insights to help
        students and universities understand emerging skills, roles and employer demand.</p>
    </div>

    <hr style="border-color: #1a4a6e; margin: 1rem 0 2rem 0;">

    <div class="content">
    <h2>Who this targets</h3>
    <div class="card-row">
        <div class="card">
            <div class="icon"></div>
            <div class="label">Students</div>
            <div class="tooltip">
                <b>Purpose of Use</b><br><br>
             To prepare for employability after graduation by discovering
             in-demand skills and roles, salary insights, employer demand and many more useful trends.
            </div>
        </div>
        <div class="card">
            <div class="icon"></div>
            <div class="label">Academics</div>
            <div class="tooltip">
            <b>Purpose of Use</b><br><br>
            To align curriculum relevance with industry demand.
            </div>
        </div>
        <div class="card">
            <div class="icon"></div>
            <div class="label">Career Consultants</div>
            <div class="tooltip">
            <b>Purpose of Use</b><br><br>
            To enhance employability support services and initiatives, aligned with industry demand.
            </div>
        </div>
    </div>
</div>

<div class="disclaimer">
    <h4>Disclaimer</h4>
    <p>This dashboard is GDPR compliant. All data displayed is aggregated and anonymised.
            No personally identifiable information is stored or processed.</p>
</div>
""", unsafe_allow_html=True)
