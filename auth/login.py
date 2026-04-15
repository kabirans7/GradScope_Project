import streamlit as st
from .auth_state import card_start, card_end
from backend.auth_repo import login


def render_login():
    card_start("Log In", "Welcome to GradScope!")

    login_email = st.text_input("Email", key="login_email")
    login_password = st.text_input("Password", type="password", key="login_password")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Forgot Password?", key="btn_login_forgot"):
            st.session_state.auth_view = "forgot"
            st.rerun()

    if st.button("Log In", key="btn_login_submit", use_container_width=True):
        if not login_email or not login_password:
            st.error("Please enter email and password.")
        else:
            user = login(login_email, login_password) #PostgreSQL call

            if user:
                st.session_state.authenticated = True
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Invalid email or password")
    
    if st.button("I don't have an account", key="btn_login_to_signup", use_container_width=True):
        st.session_state.auth_view = "signup"
        st.session_state.signup_step = 1
        st.rerun()

    card_end()
