import streamlit as st
import pandas as pd
import calendar
import datetime
from services.finance_service import get_transactions
from services.mail_service import send_email


# =========================
# 📧 HTML REPORT
# =========================
def generate_full_report_html(df, month_name, year):
    total_income = df[df["type"] == "Income"]["amount"].sum()
    total_expense = df[df["type"] == "Expense"]["amount"].sum()
    balance = total_income - total_expense

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

    rows = ""
    for _, row in merged.iterrows():
        color = "#d4edda" if row["remaining"] >= 0 else "#f8d7da"

        rows += f"""
        <tr style="background-color:{color};">
            <td>{row['category']}</td>
            <td style="text-align:right;">₹ {row['amount_budget']:.2f}</td>
            <td style="text-align:right;">₹ {row['amount_expense']:.2f}</td>
            <td style="text-align:right;">₹ {row['remaining']:.2f}</td>
        </tr>
        """

    html = f"""
    <div style="font-family: Arial;">
        <h2 style="color:#2E86C1;">📊 Finance Report - {month_name} {year}</h2>

        <h3>💰 Summary</h3>
        <p><b>Total Income:</b> ₹ {total_income:.2f}</p>
        <p><b>Total Expense:</b> ₹ {total_expense:.2f}</p>
        <p><b>Remaining Balance:</b> ₹ {balance:.2f}</p>

        <h3>📂 Budget vs Expense</h3>

        <table style="width:100%; border-collapse: collapse;">
            <thead>
                <tr style="background-color:#2E86C1; color:white;">
                    <th>Category</th>
                    <th>Budget</th>
                    <th>Expense</th>
                    <th>Remaining</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
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

    # =========================
    # 🔥 DATA CLEANING (IMPORTANT)
    # =========================
    df["category"] = df["category"].str.strip().str.title()
    df["type"] = df["type"].str.strip().str.title()

    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # =========================
    # 📅 DATE FILTER
    # =========================
    col1, col2 = st.columns(2)

    with col1:
        selected_year = st.selectbox(
            "Select Year",
            sorted(df["date"].dt.year.dropna().unique(), reverse=True)
        )

    with col2:
        months = list(calendar.month_name)[1:]
        current_month = datetime.datetime.now().month

        selected_month_name = st.selectbox(
            "Select Month",
            months,
            index=current_month - 1
        )

        selected_month = months.index(selected_month_name) + 1

    # Filter data
    df = df[
        (df["date"].dt.year == selected_year) &
        (df["date"].dt.month == selected_month)
    ]

    if df.empty:
        st.warning("No data for selected period")
        return

    # =========================
    # 💰 SUMMARY
    # =========================
    total_income = df[df["type"] == "Income"]["amount"].sum()
    total_expense = df[df["type"] == "Expense"]["amount"].sum()
    balance = total_income - total_expense

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("💰 Income", f"₹ {total_income:.2f}")

    with col2:
        st.metric("💸 Expense", f"₹ {total_expense:.2f}")

    with col3:
        st.metric("🏦 Remaining", f"₹ {balance:.2f}")

    st.divider()

    # =========================
    # 📊 CATEGORY TABLE
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

    merged.rename(columns={
        "category": "Category",
        "amount_budget": "Budget",
        "amount_expense": "Expense",
        "remaining": "Remaining"
    }, inplace=True)

    st.subheader("📂 Budget vs Expense")
    st.dataframe(merged, use_container_width=True)

    st.divider()

    # =========================
    # 📧 SEND EMAIL
    # =========================
    if st.button("📧 Send Monthly Report"):
        try:
            html = generate_full_report_html(df, selected_month_name, selected_year)

            send_email(
                
                user_id,
                f"Finance Report - {selected_month_name} {selected_year}",
                html
            )

            st.success("✅ Email sent successfully!")

        except Exception as e:
            st.error(str(e))