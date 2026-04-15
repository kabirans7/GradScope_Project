import streamlit as st
from .auth_state import card_start, card_end
from backend.auth_repo import request_password_reset

def render_forgot():
    card_start("Reset Password", "Enter your email to reset your password")

   
    email = st.text_input("Email", key="reset_email_input")

    if st.button("Send Reset Link", key="btn_forgot_send_link", use_container_width=True):
        if not email.strip():
            st.error("Please enter your email.")
        else:
            request_password_reset(email)
            st.success("If that email exists, a reset link has been sent.")

card_end()
