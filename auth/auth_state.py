# # Admin Codes - Will be integrated in future iteration 
# import streamlit as st

# def init_auth_state():
#     st.session_state.setdefault("authenticated", False)
#     st.session_state.setdefault("auth_view", "login")
#     st.session_state.setdefault("signup_step", 1)

#     for field in ["first_name", "last_name", "university_name", "occupation", "email", "password"]:
#         st.session_state.setdefault(field, "")

#     st.session_state.setdefault("reset_email", "")

# def hide_when_locked():
#     """Hide sidebar + Streamlit when user is not authenticated."""
#     st.markdown(
#      """
#         <style>
#             [data-testid="stSidebar"] { display: none; }
#             header { visibility: hidden; }
#             footer { visibility: hidden; }
#         </style>
#         """,
#         unsafe_allow_html=True,
#     )

# def require_auth():
#      """Use at the top of every page in /pages to block unauth users."""
#      if not st.session_state.get("authenticated", False):
#         st.warning("Please log in to access this page.")
#         st.switch_page("Home.py")

# def logout_button_top_right():
#     left, right = st.columns([6,2])
#     with left:
#         st.markdown("")
#     with right:
#         if st.button("Log Out", key="btn_logout_header", use_container_width=True):
#             st.session_state.authenticated = False
#             st.session_state.auth_view = "login"
#             st.session_state.signup_step = 1
#             st.rerun()

# def card_start(title: str, subtitle: str = ""):
#     st.markdown(
#         """<div style="max-width:700px;margin:auto;background:#e6e6e6;
#            padding:30px;border-radius:10px;border:1px solid #cfcfcf;">""",
#         unsafe_allow_html=True,
#     )
#     st.markdown(f"<h3 style='text-align:center;margin-top:0;'>{title}</h3>", unsafe_allow_html=True)
#     if subtitle:
#         st.markdown(f"<p style='text-align:center;margin-top:-10px;'>{subtitle}</p>", unsafe_allow_html=True)

# def card_end():
#     st.markdown("</div>", unsafe_allow_html=True)
