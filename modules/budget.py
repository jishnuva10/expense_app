import streamlit as st
import pandas as pd
from services.finance_service import add_transaction, get_transactions
from datetime import date


def show():
    st.title("💸 Budget Management")

    # ✅ Get logged-in user
    user = st.session_state.get("user")

    if not user:
        st.warning("Please login first")
        return

    user_id = user.id

    # =========================
    # ➕ ADD EXPENSE SECTION
    # =========================
    st.subheader("➕ Add Budget")

    # Create 4 columns
    col0, col1, col2, col3, col4 = st.columns(5)

    with col0:
            Type = st.selectbox(
                "type",
                ["Budget"])
            type = Type
   
    with col4:
        transaction_date = st.date_input(
            "Date",
            value=date.today()  # ✅ default today
        )

    with col2:
        description = st.text_input("Description")
    
    
    with col3:
        amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0)

    with col1:
        category = st.selectbox(
            "Category",
            ["Salary", "Loan","Credit card", "Cloths","Fuel", "House Rent", "Chitty", "Bills", "Health", "Grocery", "Insurance", "Sports", "Eating Out", "Entertainment"]
        )

    

    notes = st.text_input("Notes (optional)")

    if st.button("Add Expense"):
        if amount <= 0:
            st.error("Please enter a valid amount")
        else:
            add_transaction(user_id, amount, category, transaction_date, description,type, notes)
            st.success("Expense added successfully!")

    st.divider()

    # =========================
    # 📊 VIEW EXPENSES SECTION
    # =========================
    st.subheader("📊 Your Budget")

    res = get_transactions(user_id)

    # Filter only expenses
    Budget = [r for r in res if r.get("type") == "Budget"]

    if Budget:
        df = pd.DataFrame(Budget)

        # Optional: sort by latest
        if "id" in df.columns:
            df = df.sort_values(by="id", ascending=False)

        st.dataframe(df, use_container_width=True)

        # =========================
        # 💰 SUMMARY
        # =========================
        total_expense = df["amount"].sum()

        st.metric("Total Budget", f"₹ {total_expense:.2f}")

    else:
        st.info("No Budget found")