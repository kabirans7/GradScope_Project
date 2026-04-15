import streamlit as st
from .auth_state import init_auth_state, hide_when_locked
from .login import render_login
from .signup import render_signup
from .forgot import render_forgot
from .reset import render_reset
from .reset_success import render_reset_success

def render_auth_router():
    init_auth_state()
    hide_when_locked()

    view = st.session_state.get("auth_view", "login")

    # What state each Streamlit page is at
    if view == "login":
        render_login()
    elif view == "signup":
        render_signup()
    elif view == "forgot":
        render_forgot()
    elif view == "reset":
        render_reset()
    elif view == "reset_success":
        render_reset_success()
    else:
        st.session_state.auth_view = "login"
        st.rerun()
