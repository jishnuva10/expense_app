import streamlit as st


st.set_page_config(
    page_title="Finance App",
    layout="wide"
)




from modules import dashboard, expenses, budget, settings
from services.auth_service import login, logout





# ---- SESSION ----
if "user" not in st.session_state:
    st.session_state.user = None

# ---- LOGIN ----
if not st.session_state.user:
    st.title("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        res = login(email, password)
        if res:
            st.session_state.user = res.user
            st.success("Logged in")
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.stop()

# ---- SIDEBAR ----
st.sidebar.title("📊 Menu")

menu = st.sidebar.radio("Go to", [
    "Dashboard",
    "Expenses",
    "Budget",
    "Settings"
])

if st.sidebar.button("Logout"):
    logout()

# ---- ROUTING ----
if menu == "Dashboard":
    dashboard.show()

elif menu == "Expenses":
    expenses.show()

elif menu == "Budget":
    budget.show()

elif menu == "Settings":
    settings.show()





    