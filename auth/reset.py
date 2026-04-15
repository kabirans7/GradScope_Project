import streamlit as st
from .auth_state import card_start, card_end
from backend.auth_repo import reset_password_with_token 

def render_reset():
    card_start("Reset Password", "Please enter your new password below")

    token = st.session_state.get("reset_token", "")
    if not token:
        st.error("Reset token missing. Please use the link from your email.")
        card_end()
        return

    new_pw = st.text_input("New Password", type="password", key="new_pw")
    confirm_pw = st.text_input("Confirm New Password", type="password", key="confirm_pw")

    if st.button("Update Password", key="btn_update_password", use_container_width=True):
        if not new_pw or not confirm_pw:
            st.error("Please fill in both password fields.")
        elif new_pw != confirm_pw:
            st.error("Passwords do not match.")
        else:
            ok, msg = reset_password_with_token(token, new_pw)
            if ok:
                st.session_state["auth_view"] = "reset_success"
                st.session_state.pop("reset_token", None)
                st.query_params.clear()
                st.rerun()
            else:
                st.error(msg)

    card_end()
