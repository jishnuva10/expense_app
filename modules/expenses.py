import streamlit as st
import pandas as pd
from services.finance_service import add_transaction, get_transactions
from datetime import date


def show():
    st.title("💸 Income & Expense Management")

    # ✅ Get logged-in user
    user = st.session_state.get("user")

    if not user:
        st.warning("Please login first")
        return

    user_id = user.id

    # =========================
    # ➕ ADD EXPENSE SECTION
    # =========================
    st.subheader("➕ Add Income / Expense")

    # Create 4 columns
    col0, col1, col2, col3, col4 = st.columns(5)

    with col0:
            type = st.selectbox(
                "type",
                ["Income","Expense"])
   
    with col3:
        transaction_date = st.date_input(
            "Date",
            value=date.today()  # ✅ default today
        )

    with col2:
        description = st.text_input("Description")
    
    
    with col4:
        amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0)

    with col1:
        if type == "Income":
            category = st.selectbox("Category", ["Salary","Gift","Debt"])
        else:
            category = st.selectbox(
                "Category",
                [
                    "Loan", "Credit Card", "Cloths", "Fuel", "House Rent",
                    "Chitty", "Bills", "Health", "Grocery", "Insurance",
                    "Sports", "Eating Out", "Entertainment"
                ] )

    

    notes = st.text_input("Notes (optional)")

    if st.button("Add Expense"):
        if amount <= 0:
            st.error("Please enter a valid amount")
        else:
            add_transaction(user_id, amount, category, transaction_date, description,type,notes)
            st.success("Expense added successfully!")

    st.divider()

    # =========================
    # 📊 VIEW EXPENSES SECTION
    # =========================
    st.subheader("📊 Your Expenses")

    res = get_transactions(user_id)

    # Filter only expenses
    expenses = [r for r in res if r.get("type") in ["Expense"]]
    income1 = [r for r in res if r.get("type") in ["Income"]]

    if expenses:
        df = pd.DataFrame(expenses)

        # Optional: sort by latest
        if "id" in df.columns:
            df = df.sort_values(by="id", ascending=False)

        st.dataframe(df, use_container_width=True)
    st.subheader("📊 Your Income")
    if income1:
        df1 = pd.DataFrame(income1)

        # Optional: sort by latest
        if "id" in df1.columns:
            df1 = df1.sort_values(by="id", ascending=False)

        st.dataframe(df1, use_container_width=True)

        # =========================
        # 💰 SUMMARY
        # =========================
        total_expense = df1["amount"].sum() - df["amount"].sum()

        st.metric("Total Expense", f"₹ {total_expense:.2f}")

    else:
        st.info("No expenses found")