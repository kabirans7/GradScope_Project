import streamlit as st
from .auth_state import card_start, card_end
from backend.auth_repo import email_exists, signup_admin

def render_signup():
    card_start("Sign Up", "Admin Registration")

    # Prevents KeyError if auth_state didn't set them yet
    st.session_state.setdefault("signup_step", 1)
    st.session_state.setdefault("first_name", "")
    st.session_state.setdefault("last_name", "")
    st.session_state.setdefault("university_name", "")
    st.session_state.setdefault("occupation", "")
    st.session_state.setdefault("email", "")
    st.session_state.setdefault("password", "")

    
    # Step 1: Personal details

    if st.session_state.signup_step == 1:
        st.subheader("Personal Details")

        st.session_state.first_name = st.text_input("First Name", st.session_state.first_name)
        st.session_state.last_name = st.text_input("Last Name", st.session_state.last_name)
        st.session_state.university_name = st.text_input("University Name", st.session_state.university_name)
        st.session_state.occupation = st.text_input("University Occupation", st.session_state.occupation)

        if st.button("Continue", key="btn_signup_continue", use_container_width=True):
            if not all([
                st.session_state.first_name.strip(),
                st.session_state.last_name.strip(),
                st.session_state.university_name.strip(),
                st.session_state.occupation.strip(),
            ]):
                st.error("Please fill in all personal details before continuing.")
            else:
                st.session_state.signup_step = 2
                st.rerun()

       

    
    # Step 2: Admin Credentials
    
    elif st.session_state.signup_step == 2:
        st.subheader("Admin Credentials")

        st.session_state.email = st.text_input("Email", st.session_state.email)
        st.session_state.password = st.text_input("Password", type="password", value=st.session_state.password, key="signup_password")

        colA, colB = st.columns(2)

        with colA:
            if st.button("Previous", key="btn_signup_prev", use_container_width=True):
                st.session_state.signup_step = 1
                st.rerun()

        with colB:
            if st.button("Confirm", key="btn_signup_confirm", use_container_width=True):
                email = (st.session_state.email or "").strip().lower()
                password = (st.session_state.password or "").strip()

                # Validate
                if not email or not password:
                    st.error("Email and password are required.")
                    st.stop()

                if "@" not in email or "." not in email:
                    st.error("Please enter a valid email address.")
                    st.stop()

                if len(password) < 8:
                    st.error("Password must be at least 8 characters.")
                    st.stop()

                if email_exists(email):
                    st.error("An account with this email already exists.")
                    st.stop()

                # Insert into DB
                admin_id, err = signup_admin(
                    st.session_state.first_name,
                    st.session_state.last_name,
                    st.session_state.university_name,
                    st.session_state.occupation,
                    email,
                    password,
                )

                if err:
                    st.error(err)
                    st.stop()

                # Show account successfully created
                st.session_state.signup_step = 3
                st.rerun()

  
    # Step 3: Success screen
    
    elif st.session_state.signup_step == 3:
        st.subheader("Account Created")
        st.success("Welcome to GradScope!")
        st.write("Your account has been created successfully.")
        st.write("You can now access the GradScope Dashboard!")

        if st.button("Go to Log In", key="btn_signup_back_login", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.auth_view = "login"
            st.session_state.signup_step = 1

            # Optional: clear signup fields
            for k in ["first_name", "last_name", "university_name", "occupation", "email", "password"]:
                st.session_state[k] = ""

            st.rerun()

    card_end()
