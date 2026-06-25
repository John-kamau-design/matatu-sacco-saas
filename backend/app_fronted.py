import streamlit as st
import httpx

# Configure the page style to feel like a mobile-first app dashboard
st.set_page_config(page_title="Matatu SaaS Operator", page_icon="🚌", layout="centered")

BASE_URL = "https://matatu-sacco-saas.onrender.com"

st.title("🚌 Matatu SACCO SaaS MVP")
st.write("Simplified Management Interface for Field Operations")

# Sidebar navigation menu tabs
menu = ["Onboard SACCO", "Register Owner", "Daily Ledger Entry", "Financial Summaries"]
choice = st.sidebar.selectbox("Navigation Menu", menu)

# --- TAB 1: ONBOARD SACCO ---
if choice == "Onboard SACCO":
    st.subheader("🏢 Register a New SACCO")
    sacco_name = st.text_input("Enter SACCO Name (e.g., Ganji Sacco)")
    if st.button("Submit Registration"):
        if sacco_name:
            with httpx.Client(follow_redirects=True) as client:
                response = client.post(f"{BASE_URL}/saccos/", json={"sacco_name": sacco_name})
            if response.status_code == 201:
                data = response.json()
                st.success(f"🎉 Success! Registered {data['sacco_name']}")
                st.info(f"Copy this Unique SACCO ID:  `{data['sacco_id']}`")
            else:
                try:
                    error_detail = response.json().get('detail', response.text)
                except Exception:
                    error_detail = f"Status Code {response.status_code}: {response.text}"
                st.error(f"Error: {error_detail}")

# --- TAB 2: REGISTER OWNER ---
elif choice == "Register Owner":
    st.subheader("👤 Onboard Vehicle Owner")
    sacco_id = st.text_input("Paste SACCO Unique ID")
    owner_name = st.text_input("Owner Full Name")
    phone = st.text_input("Phone Number (e.g., +2547...)")
    
    if st.button("Register Owner"):
        if sacco_id and owner_name and phone:
            payload = {"sacco_id": sacco_id, "owner_name": owner_name, "phone_number": phone}
            with httpx.Client(follow_redirects=True) as client:
                response = client.post(f"{BASE_URL}/owners", json=payload)
            if response.status_code == 201:
                data = response.json()
                st.success(f"🎉 Registered {data['owner_name']} successfully!")
                st.info(f"Copy Owner Unique ID:  `{data['owner_id']}`")
            else:
                st.error(f"Error: {response.json().get('detail')}")

# --- TAB 3: DAILY LEDGER ENTRY ---
elif choice == "Daily Ledger Entry":
    st.subheader("📝 Record Daily Matatu Runs")
    sacco_id = st.text_input("SACCO Unique ID")
    owner_id = st.text_input("Owner Unique ID")
    reg_no = st.text_input("Matatu Plate Number (e.g., KBC 123X)")
    cash = st.number_input("Cash Collected (KES)", min_value=0.0, step=500.0)
    mpesa = st.number_input("M-Pesa Collected (KES)", min_value=0.0, step=500.0)
    expenses = st.number_input("Total Expenses / Fuel (KES)", min_value=0.0, step=100.0)

    if st.button("Save Ledger Entry"):
        payload = {
            "sacco_id": sacco_id,
            "owner_id": owner_id,
            "registration_number": reg_no,
            "cash_collected": cash,
            "mpesa_collected": mpesa,
            "total_expenses": expenses
        }
        with httpx.Client(follow_redirects=True) as client:
            response = client.post(f"{BASE_URL}/ledgers", json=payload)
        if response.status_code == 201:
            st.success("🚀 Operational record saved! 500 KES automatic 'Debe' deducted.")
        else:
            st.error(f"Failed: {response.json().get('detail')}")

# --- TAB 4: FINANCIAL SUMMARIES ---
elif choice == "Financial Summaries":
    st.subheader("📊 Live SACCO Financial Report Dashboard")
    sacco_id = st.text_input("Paste SACCO ID to view records")
    
    if st.button("Fetch Live Reports"):
        with httpx.Client(follow_redirects=True) as client:
            response = client.get(f"{BASE_URL}/saccos/{sacco_id}/summary")
        if response.status_code == 200:
            data = response.json()
            st.metric("Total Gross Revenue", f"KES {data['total_gross_revenue']:,}")
            
            col1, col2 = st.columns(2)
            col1.metric("SACCO Fees Collected", f"KES {data['total_sacco_debe_collected']:,}")
            col2.metric("Net Payout to Owners", f"KES {data['net_payout_to_owners']:,}")
            
            st.caption(f"Reporting from {data['active_vehicles_reported']} active fleet submissions today.")
        else:
            st.error("Could not load reports. Make sure the SACCO ID is correct.")