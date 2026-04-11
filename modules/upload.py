import streamlit as st
import pandas as pd
from services.finance_service import add_transaction
import io


def show():
    st.title("📤 Upload Transactions (Excel)")

    # =========================
    # 📥 DOWNLOAD TEMPLATE
    # =========================
    template_df = pd.DataFrame({
        "amount": [1000],
        "category": ["Food"],
        "type": ["Expense"],
        "date": ["01-04-2026"],
        "description": ["Lunch"],
        "notes": [""],
        "CFO": ["Jishnu"]
    })

    buffer = io.BytesIO()
    template_df.to_excel(buffer, index=False)
    buffer.seek(0)

    st.download_button(
        label="📥 Download Template",
        data=buffer,
        file_name="transaction_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # =========================
    # 👤 USER CHECK
    # =========================
    user = st.session_state.get("user")
    if not user:
        st.warning("Please login")
        return

    user_id = user.id

    # =========================
    # 📤 FILE UPLOAD
    # =========================
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)

        st.subheader("📄 Preview")
        st.dataframe(df, use_container_width=True)

        # =========================
        # ✅ STRICT COLUMN VALIDATION
        # =========================
        expected_columns = [
            "amount", "category", "type",
            "date", "description", "notes", "CFO"
        ]

        if list(df.columns) != expected_columns:
            st.error("❌ Column format mismatch. Please use template.")
            st.write("Expected:", expected_columns)
            st.write("Found:", list(df.columns))
            return

        # =========================
        # 🚀 UPLOAD
        # =========================
        if st.button("🚀 Upload Data"):

            success_count = 0
            error_count = 0

            for _, row in df.iterrows():
                try:
                    # =========================
                    # ✅ DATE HANDLING
                    # =========================
                    date_value = row["date"]

                    # Case 1: Excel auto-parsed Timestamp
                    if isinstance(date_value, pd.Timestamp):
                        date_value = date_value.date().isoformat()

                    # Case 2: String format DD-MM-YYYY
                    elif isinstance(date_value, str):
                        parsed_date = pd.to_datetime(
                            date_value,
                            format="%d-%m-%Y",
                            errors="coerce"
                        )

                        if pd.isna(parsed_date):
                            raise Exception("Invalid date format")

                        date_value = parsed_date.date().isoformat()

                    else:
                        raise Exception("Unsupported date format")

                    # =========================
                    # ✅ CLEAN DATA
                    # =========================
                    txn_type = str(row["type"]).strip().title()

                    if txn_type not in ["Expense", "Income", "Budget"]:
                        raise Exception("Invalid type")

                    category = str(row["category"]).strip().title()
                    description = str(row["description"])
                    notes = str(row.get("notes", ""))
                    CFO = str(row.get("CFO", "Jishnu"))

                    # =========================
                    # ✅ INSERT
                    # =========================
                    add_transaction(
                        user_id=user_id,
                        amount=float(row["amount"]),
                        category=category,
                        date=date_value,
                        description=description,
                        type=txn_type,
                        notes=notes,
                        CFO=CFO
                    )

                    success_count += 1

                except Exception as e:
                    error_count += 1
                    st.error(f"❌ Error: {e}")
                    st.warning(f"Row failed: {row.to_dict()}")

            # =========================
            # 📊 RESULT
            # =========================
            st.success(f"✅ Uploaded: {success_count}")

            if error_count > 0:
                st.error(f"❌ Failed: {error_count}")