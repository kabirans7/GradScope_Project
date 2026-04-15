import streamlit as st
from sqlalchemy import create_engine

@st.cache_resource
def get_engine():
    pg = st.secrets["postgres"]

    url = (
        f"postgresql+psycopg2://{pg['user']}:{pg['password']}"
        f"@{pg['host']}:{pg['port']}/{pg['database']}"
    )

    return create_engine(
        url,
        pool_pre_ping=True,   # detects dead connections
        pool_recycle=1800     # refreshes old connections
    )
