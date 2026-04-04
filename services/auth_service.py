import streamlit as st
from services.supabase_client import get_client

supabase = get_client()

def login(email, password):
    try:
        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return res
    except:
        return None

def logout():
    supabase.auth.sign_out()
    st.session_state.clear()