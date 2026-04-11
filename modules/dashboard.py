import streamlit as st
import pandas as pd
import calendar
import datetime
from services.finance_service import get_transactions
from services.mail_service import send_email
from datetime import datetime


# =========================
# 📧 HTML REPORT
# =========================
def generate_full_report_html(df, month_name, year):

    # 🔥 CLEAN DATA
    df["category"] = df["category"].str.strip().str.title()
    df["type"] = df["type"].str.strip().str.title()

    # =========================
    # 💰 SUMMARY
    # =========================
    total_income = df[df["type"] == "Income"]["amount"].sum()
    total_expense = df[df["type"] == "Expense"]["amount"].sum()
    balance = total_income - total_expense
    total_budget = df[df["type"] == "Budget"]["amount"].sum()
    # =========================
    # 👤 CFO SUMMARY
    # =========================
    cfo_summary = (
        df[df["type"].isin(["Expense", "Budget"])]
        .groupby(["CFO", "type"])["amount"]
        .sum()
        .unstack(fill_value=0)
    )

    cfo_summary["Remaining"] = cfo_summary.get("Budget", 0) - cfo_summary.get("Expense", 0)

    # =========================
    # 📊 CATEGORY SUMMARY
    # =========================
    expense_df = df[df["type"] == "Expense"]
    budget_df = df[df["type"] == "Budget"]

    expense_group = expense_df.groupby("category")["amount"].sum().reset_index()
    budget_group = budget_df.groupby("category")["amount"].sum().reset_index()

    merged = pd.merge(
        budget_group,
        expense_group,
        on="category",
        how="outer",
        suffixes=("_budget", "_expense")
    ).fillna(0)

    merged["remaining"] = merged["amount_budget"] - merged["amount_expense"]

    # =========================
    # 📊 CATEGORY HTML TABLE
    # =========================
    rows = ""
    for _, row in merged.iterrows():
        color = "#d4edda" if row["remaining"] >= 0 else "#f8d7da"

        rows += f"""
        <tr style="background-color:{color};">
            <td>{row['category']}</td>
            <td>₹ {row['amount_budget']:.2f}</td>
            <td>₹ {row['amount_expense']:.2f}</td>
            <td>₹ {row['remaining']:.2f}</td>
        </tr>
        """

    # =========================
    # 👤 CFO HTML TABLE
    # =========================
    cfo_rows = ""
    for cfo, row in cfo_summary.iterrows():
        cfo_rows += f"""
        <tr>
            <td>{cfo}</td>
            <td>₹ {row.get('Budget', 0):.2f}</td>
            <td>₹ {row.get('Expense', 0):.2f}</td>
            <td>₹ {row['Remaining']:.2f}</td>
        </tr>
        """

    html = f"""
    <div style="font-family: Arial;">
        <h2>📊 Finance Report - {month_name} {year}</h2>

        <h3>💰 Summary</h3>
        <p><b>Total Income:</b> ₹ {total_income:.2f}</p>
        <p><b>Total Expense:</b> ₹ {total_expense:.2f}</p>
        <p><b>Remaining Balance:</b> ₹ {balance:.2f}</p>

        <h3>👤 CFO Summary</h3>
        <table border="1" cellpadding="6">
            <tr>
                <th>CFO</th>
                <th>Budget</th>
                <th>Expense</th>
                <th>Remaining</th>
            </tr>
            {cfo_rows}
        </table>

        <h3>📂 Category Summary</h3>
        <table border="1" cellpadding="6">
            <tr>
                <th>Category</th>
                <th>Budget</th>
                <th>Expense</th>
                <th>Remaining</th>
            </tr>
            {rows}
        </table>
    </div>
    """

    return html


# =========================
# 📊 DASHBOARD
# =========================
def show():
    st.title("📊 Dashboard")

    user = st.session_state.get("user")
    if not user:
        st.warning("Please login")
        return

    user_id = user.id
    res = get_transactions(user_id)

    if not res:
        st.info("No data available")
        return

    df = pd.DataFrame(res)

    # 🔥 CLEAN DATA
    df["category"] = df["category"].str.strip().str.title()
    df["type"] = df["type"].str.strip().str.title()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # =========================
    # 📅 FILTER
    # =========================
    col1, col2 = st.columns(2)
    today = datetime.today()

    today = datetime.today()
    current_year = today.year
    

    with col1:
        years = sorted(df["date"].dt.year.dropna().unique(), reverse=True)
        if current_year in years:
            default_index = years.index(current_year)
        else:
            default_index = 0  # latest available year
        selected_year = st.selectbox(
            "Year",years,
            index=default_index 
        )

    with col2:

        current_month = today.month

        months = [
            "January", "February", "March", "April",
            "May", "June", "July", "August",
            "September", "October", "November", "December"
        ]

        selected_month = st.selectbox(
            "Month",
            months,
            index=current_month - 1
        )
        month_number = months.index(selected_month) + 1
        '''months = list(calendar.month_name)[1:]
        selected_month_name = st.selectbox("Month", months)
        selected_month = months.index(selected_month_name) + 1
'''
    df = df[
            (df["date"].dt.year == selected_year) &
            (df["date"].dt.month == month_number)
        ]

    if df.empty:
        st.warning("No data")
        return

    # =========================
    # 💰 SUMMARY
    # =========================
    total_income = df[df["type"] == "Income"]["amount"].sum()
    total_expense = df[df["type"] == "Expense"]["amount"].sum()
    balance = total_income - total_expense
    total_budget = df[df["type"] == "Budget"]["amount"].sum()
    col0, col1, col2, col3 = st.columns(4)

    col0.metric("Budget", f"₹ {total_budget:.0f}")
    col1.metric("Income", f"₹ {total_income:.0f}")
    col2.metric("Expense", f"₹ {total_expense:.0f}")
    col3.metric("Remaining", f"₹ {balance:.0f}")

    st.divider()

    # =========================
    # 👤 CFO SUMMARY
    # =========================
    cfo_summary = (
        df[df["type"].isin(["Expense", "Budget"])]
        .groupby(["CFO", "type"])["amount"]
        .sum()
        .unstack(fill_value=0)
    )

    cfo_summary["Remaining"] = cfo_summary.get("Budget", 0) - cfo_summary.get("Expense", 0)

    st.subheader("👤 CFO Summary")
    st.dataframe(cfo_summary)

    # =========================
    # 📊 CATEGORY TABLE
    # =========================
    expense_df = df[df["type"] == "Expense"]
    budget_df = df[df["type"] == "Budget"]

    merged = pd.merge(
        budget_df.groupby("category")["amount"].sum().reset_index(),
        expense_df.groupby("category")["amount"].sum().reset_index(),
        on="category",
        how="outer",
        suffixes=("_budget", "_expense")
    ).fillna(0)

    merged["remaining"] = merged["amount_budget"] - merged["amount_expense"]

    st.subheader("📂 Category Summary")
    st.dataframe(merged)

    # =========================
    # 📧 EMAIL
    # =========================
    if st.button("📧 Send Report"):
        html = generate_full_report_html(df, selected_month, selected_year)

        send_email(
            user_id,
            f"📊 Finance Report - {selected_month} {selected_year}",
            html
        )

        st.success("Email sent!")