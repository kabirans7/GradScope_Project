import streamlit as st
from sqlalchemy import create_engine
 
 
@st.cache_resource
def get_engine():
    pg = st.secrets["postgres"]
    db_url = (
        f"postgresql+psycopg2://{pg['user']}:{pg['password']}"
        f"@{pg['host']}:{pg['port']}/{pg['database']}"
    )
    return create_engine(
        db_url,
        pool_pre_ping=True,        # tests connection before using it
        pool_recycle=300,          # recycle connections every 5 minutes
        pool_size=5,               # max 5 persistent connections
        max_overflow=10,           # allow 10 extra connections if needed
        connect_args={"sslmode": "require"},
    )
  
