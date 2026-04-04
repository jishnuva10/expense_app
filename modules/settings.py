import streamlit as st
from services.email_settings_service import save_email_settings, get_email_settings
from services.mail_service import send_email


def show():
    st.title("⚙️ Email Settings")

    user = st.session_state.get("user")
    if not user:
        st.warning("Please login first")
        return

    user_id = user.id

    config = get_email_settings(user_id)

    st.subheader("📧 SMTP Configuration")

    smtp_server = st.text_input("SMTP Server", value=config.get("smtp_server", "smtp.gmail.com"))
    smtp_port = st.number_input("SMTP Port", value=config.get("smtp_port", 587))

    sender_email = st.text_input("Sender Email", value=config.get("sender_email", ""))
    sender_password = st.text_input("App Password", type="password", value=config.get("sender_password", ""))

    st.divider()

    st.subheader("📨 Recipients")

    to_email = st.text_input("To Email", value=config.get("to_email", ""))
    cc_email = st.text_input("CC Emails (comma separated)", value=config.get("cc_email", ""))

    if st.button("💾 Save Configuration"):
        data = {
            "smtp_server": smtp_server,
            "smtp_port": smtp_port,
            "sender_email": sender_email,
            "sender_password": sender_password,
            "to_email": to_email,
            "cc_email": cc_email
        }

        save_email_settings(user_id, data)
        st.success("Saved successfully!")

    st.divider()

    if st.button("📤 Send Test Email"):
        try:
            send_email(
                user_id,
                "Test Email",
                "Your email setup is working 🚀"
            )
            st.success("Email sent!")
        except Exception as e:
            st.error(str(e))