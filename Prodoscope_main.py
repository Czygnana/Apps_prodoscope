# prodoscope_app.py
# Run: streamlit run prodoscope_app.py

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
from collections import defaultdict
import requests
import io
import base64
import json

st.set_page_config(page_title="Prodoscope", page_icon="🧭", layout="wide")

# ---------- CSS ----------
CUSTOM_CSS = """
<style>
.hero-title {font-size: 2.6rem; font-weight: 800; 
    background: linear-gradient(90deg,#ff7a7a,#ffd86f,#6fe7dd,#a77bf3);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
.subtitle {color: #666; font-size: 0.95rem; margin-bottom: 1rem;}
.card {
    border-radius: 14px;
    padding: 14px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    min-height: 170px;
    color: #111827;
    display:flex;
    flex-direction:column;
    justify-content:space-between;
}
.card .top {display:flex; align-items:center; gap:10px;}
.card-title {font-weight:800; font-size:1.05rem;}
.card-desc {color:#475569; margin-top:6px; font-size:0.95rem;}
.section-title {font-size: 1.15rem; font-weight: 700; margin: 12px 0 8px 0}
.btn-primary button {
    background: linear-gradient(90deg,#6fe7dd,#a77bf3);
    color: white !important;
    font-weight: 700;
    border-radius: 10px;
    padding: 0.55rem 1.0rem;
    border: none;
}
.btn-primary button:hover { background: linear-gradient(90deg,#53d8ce,#8e67e6); color:#fff !important; }
.stButton>button { padding: .45rem 0.9rem !important; } /* comfortable size */
.small-muted {color:#94a3b8; font-size:0.85rem}
.card-svg {width:34px; height:34px}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------- Inline SVG icons (embedded) ----------
SVG_UPI = """<svg class='card-svg' viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<linearGradient id="g1" x1="0" x2="1"><stop offset="0" stop-color="#FFB86B"/><stop offset="1" stop-color="#FF6A88"/></linearGradient>
<rect x="1" y="4" width="22" height="16" rx="2" fill="url(#g1)"/>
<path d="M7 9h10M7 12h6" stroke="white" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

SVG_BANK = """<svg class='card-svg' viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
<linearGradient id="g2" x1="0" x2="1"><stop offset="0" stop-color="#7EE8FA"/><stop offset="1" stop-color="#80FF72"/></linearGradient>
<path d="M12 3L2 9h20L12 3z" fill="url(#g2)"/>
<rect x="4" y="9" width="16" height="8" rx="1" fill="#FFFFFF" opacity="0.06"/>
<path d="M8 12h.01M12 12h.01M16 12h.01" stroke="#fff" stroke-width="1.5" stroke-linecap="round"/>
</svg>"""

SVG_BAL = """<svg class='card-svg' viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
<linearGradient id="g3" x1="0" x2="1"><stop offset="0" stop-color="#FF8A00"/><stop offset="1" stop-color="#DA1B60"/></linearGradient>
<circle cx="12" cy="10" r="6" fill="url(#g3)" />
<path d="M7 16c1.5-2 8-2 10 0" stroke="#fff" stroke-width="1.6" stroke-linecap="round"/>
</svg>"""

SVG_SPLIT = """<svg class='card-svg' viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
<linearGradient id="g4" x1="0" x2="1"><stop offset="0" stop-color="#9B5CF6"/><stop offset="1" stop-color="#6FE7DD"/></linearGradient>
<rect x="3" y="5" width="7" height="6" rx="1.5" fill="url(#g4)"/>
<rect x="14" y="5" width="7" height="6" rx="1.5" fill="#fff" opacity="0.06"/>
<rect x="8" y="13" width="8" height="6" rx="1.5" fill="url(#g4)" opacity="0.9"/>
</svg>"""

SVG_EXP = """<svg class='card-svg' viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
<linearGradient id="g5" x1="0" x2="1"><stop offset="0" stop-color="#FFD86F"/><stop offset="1" stop-color="#FF7A7A"/></linearGradient>
<rect x="3" y="4" width="18" height="16" rx="2" fill="url(#g5)"/>
<path d="M7 9h10M7 12h10M7 15h6" stroke="#fff" stroke-width="1.4" stroke-linecap="round"/>
</svg>"""

SVG_SAVE = """<svg class='card-svg' viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
<linearGradient id="g6" x1="0" x2="1"><stop offset="0" stop-color="#7AF0A0"/><stop offset="1" stop-color="#3BC7FF"/></linearGradient>
<path d="M12 3v6l4 2" fill="url(#g6)"/>
<circle cx="12" cy="15" r="5" fill="#fff" opacity="0.08"/>
</svg>"""

SVG_KNOW = """<svg class='card-svg' viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
<linearGradient id="g7" x1="0" x2="1"><stop offset="0" stop-color="#74EBD5"/><stop offset="1" stop-color="#9FACE6"/></linearGradient>
<rect x="4" y="4" width="16" height="16" rx="2" fill="url(#g7)"/>
<path d="M8 9h8M8 12h6" stroke="#fff" stroke-width="1.4" stroke-linecap="round"/>
</svg>"""

SVG_GAME = """<svg class='card-svg' viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
<linearGradient id="g8" x1="0" x2="1"><stop offset="0" stop-color="#FFD5A6"/><stop offset="1" stop-color="#FF8AA0"/></linearGradient>
<rect x="3" y="6" width="18" height="12" rx="2" fill="url(#g8)"/>
<circle cx="9" cy="12" r="1.2" fill="#fff"/><circle cx="15" cy="12" r="1.2" fill="#fff"/>
</svg>"""

SVG_FREEL = """<svg class='card-svg' viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
<linearGradient id="g9" x1="0" x2="1"><stop offset="0" stop-color="#A78BFA"/><stop offset="1" stop-color="#F472B6"/></linearGradient>
<path d="M4 7h16v10H4z" fill="url(#g9)"/>
<path d="M7 10h10M7 13h6" stroke="#fff" stroke-width="1.4" stroke-linecap="round"/>
</svg>"""

# map title -> svg string
ICON_MAP = {
    "UPI": SVG_UPI,
    "Connect Bank": SVG_BANK,
    "Check Balance": SVG_BAL,
    "Split Groups": SVG_SPLIT,
    "Daily Expense Log": SVG_EXP,
    "Savings Log & Race": SVG_SAVE,
    "Financial Knowledge": SVG_KNOW,
    "Financial Games": SVG_GAME,
    "Freelancer Suggestions": SVG_FREEL
}

# ---------- Session state init ----------
def _init_state():
    ss = st.session_state
    ss.setdefault('users', {})  # username -> {'password','email'}
    ss.setdefault('current_user', None)
    ss.setdefault('auth_mode', 'signup')  # 'signup' | 'login' | 'app'
    ss.setdefault('current_page', 'Top Page')
    ss.setdefault('contacts', [
        {"name":"Aarav", "upi":"aarav@upi"},
        {"name":"Diya", "upi":"diya@upi"},
        {"name":"Kabir", "upi":"kabir@upi"},
        {"name":"Saanvi", "upi":"saanvi@upi"},
        {"name":"Vikram", "upi":"vikram@upi"},
    ])
    ss.setdefault('bank', {'connected': False, 'name': None, 'balance': 0.0})
    ss.setdefault('transactions', [])  # list of {ts,type,to_from,amount,note}
    ss.setdefault('daily_expenses', [])  # list of {date, amount, reason}
    ss.setdefault('savings', {'month_key': None, 'target': 0.0, 'reason': '', 'logs': []})
    ss.setdefault('groups', {})  # name -> {'members':[], 'splits':[]}
_init_state()

# ---------- Auth pages ----------
def signup_page():
    st.markdown('<div class="hero-title">Prodoscope</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Sign up to your colourful money command center</div>', unsafe_allow_html=True)
    with st.form('signup_form', clear_on_submit=True):
        st.subheader("Create an account")
        username = st.text_input("Username", key='su_user')
        email = st.text_input("Email", key='su_email')
        password = st.text_input("Password", type='password', key='su_pass')
        agree = st.checkbox("I agree to the Terms & Privacy Policy")
        submitted = st.form_submit_button("Sign Up ✨")
    if submitted:
        if not (username and email and password and agree):
            st.error("Please fill all fields and accept the terms.")
        elif username in st.session_state.users:
            st.error("Username already exists. Please log in.")
            st.session_state.auth_mode = 'login'
            st.rerun()
        else:
            st.session_state.users[username] = {'password': password, 'email': email}
            st.success("Account created! Please log in.")
            st.session_state.auth_mode = 'login'
            st.rerun()

def login_page():
    st.markdown('<div class="hero-title">Prodoscope</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Log in to continue</div>', unsafe_allow_html=True)
    with st.form('login_form'):
        username = st.text_input("Username", key='li_user')
        password = st.text_input("Password", type='password', key='li_pass')
        submitted = st.form_submit_button("Log In 🔐")
    if submitted:
        user = st.session_state.users.get(username)
        if user and user['password'] == password:
            st.session_state.current_user = username
            st.session_state.auth_mode = 'app'
            st.session_state.current_page = 'Top Page'
            st.success(f"Welcome back, {username}!")
            st.rerun()
        else:
            st.error("Invalid credentials.")

def require_login():
    if st.session_state.auth_mode == 'signup':
        signup_page()
        st.stop()
    elif st.session_state.auth_mode == 'login':
        login_page()
        st.stop()
    elif st.session_state.current_user is None:
        signup_page()
        st.stop()

# ---------- Utilities ----------
def month_key(d):
    if isinstance(d, datetime):
        d = d.date()
    return d.strftime('%Y-%m')

def compute_top_metrics():
    tx = st.session_state.transactions
    total_in = sum(t.get('amount',0) for t in tx if t.get('type') == 'in')
    total_out = sum(t.get('amount',0) for t in tx if t.get('type') == 'out')
    total_amount = total_in
    amount_spent = total_out
    remaining = max(st.session_state.bank.get('balance',0.0), 0.0)
    sv = st.session_state.savings
    mk = month_key(date.today())
    reached = sum(l['amount'] for l in sv.get('logs', []) if month_key(pd.to_datetime(l['date'])) == mk)
    target = sv['target'] if sv.get('month_key') == mk else 0.0
    savings_percent = (reached / target * 100.0) if target > 0 else 0.0
    return total_amount, amount_spent, remaining, savings_percent

# ---------- Navigation widgets ----------
def back_to_dashboard():
    st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
    if st.button("⬅ Back to Dashboard", key=f"back_{st.session_state.current_page}"):
        st.session_state.current_page = "Top Page"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def card_wrapper(svg: str, title: str, desc: str, btn_text: str, key: str, bg_gradient: str):
    """Render a card with inline SVG, title, description and an action button.
       bg_gradient: CSS gradient for the card background area (string)"""
    # Use an outer div with background gradient (inline) and inner content
    html = f"""
    <div style="background: {bg_gradient}; border-radius:12px; padding:14px; color:white; height:170px; display:flex; flex-direction:column; justify-content:space-between;">
      <div class="top"><div>{svg}</div><div class="card-title">{title}</div></div>
      <div style="color:rgba(255,255,255,0.95);" class="card-desc">{desc}</div>
      <div style="display:flex; justify-content:flex-end;">
        <!-- placeholder for streamlit button -->
      </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
    if st.button(btn_text, key=key):
        st.session_state.current_page = title  # we use exact title as page key
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Require login ----------
require_login()

# ---------- Sidebar ----------
PAGES = [
    "Top Page", "UPI", "Connect Bank", "Check Balance", "Split Groups",
    "Daily Expense Log", "Savings Log & Race", "Financial Knowledge", "Financial Games", "Freelancer Suggestions"
]
try:
    idx = PAGES.index(st.session_state.current_page)
except ValueError:
    idx = 0
choice = st.sidebar.radio("📌 Navigate", PAGES, index=idx)
st.session_state.current_page = choice
if st.sidebar.button("Log out"):
    st.session_state.current_user = None
    st.session_state.auth_mode = 'signup'
    st.session_state.current_page = 'Top Page'
    st.rerun()

# ---------- Top Page ----------
def top_page():
    st.markdown('<div class="hero-title">Prodoscope</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Your colourful personal finance cockpit</div>', unsafe_allow_html=True)

    total_amount, amount_spent, remaining, savings_percent = compute_top_metrics()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Amount", f"₹{total_amount:,.2f}")
    with c2:
        st.metric("Amount Spent", f"₹{amount_spent:,.2f}")
    with c3:
        st.metric("Remaining Amount", f"₹{remaining:,.2f}")
    with c4:
        st.metric("Savings %", f"{savings_percent:.1f}%")

    st.markdown("<div class='section-title'>Quick Actions</div>", unsafe_allow_html=True)

    # Define card list: (title, desc, btn_text, key, gradient)
    features = [
        ("UPI", "Send money to contacts via UPI.", "Send Money to Contacts via UPI", "card_upi", "linear-gradient(135deg,#1e3c72,#2a5298)"),
        ("Connect Bank", "Securely connect a bank and set a balance.", "Connect Your Bank", "card_bank", "linear-gradient(135deg,#0f9b8e,#38ef7d)"),
        ("Check Balance", "View your connected bank balance.", "Check Bank Balance", "card_bal", "linear-gradient(135deg,#4568dc,#b06ab3)"),
        ("Split Groups", "Create groups and split bills automatically or manually.", "Manage & Split Group Expenses", "card_split", "linear-gradient(135deg,#8b5cf6,#6fe7dd)"),
        ("Daily Expense Log", "Log day-to-day spending and get monthly insights.", "Log Your Daily Expenses", "card_exp", "linear-gradient(135deg,#ffd86f,#ff7a7a)"),
        ("Savings Log & Race", "Set monthly target, log savings and track progress.", "Track & Log Monthly Savings", "card_save", "linear-gradient(135deg,#7af0a0,#3bc7ff)"),
        ("Financial Knowledge", "Inflation, rate changes, GDP and tips to beat inflation.", "Explore Financial Knowledge", "card_know", "linear-gradient(135deg,#74ebd5,#9face6)"),
        ("Financial Games", "Mini challenges to build healthy financial habits.", "Play Finance Learning Games", "card_games", "linear-gradient(135deg,#ffd5a6,#ff8aa0)"),
        ("Freelancer Suggestions", "Get platform suggestions based on your skills.", "Get Freelancer Opportunities", "card_free", "linear-gradient(135deg,#a78bfa,#f472b6)"),
    ]

    # Render 3 per row with SVGs
    for i in range(0, len(features), 3):
        cols = st.columns(3)
        for col, feat in zip(cols, features[i:i+3]):
            title, desc, btn_text, key, grad = feat
            svg = ICON_MAP.get(title, "")
            with col:
                card_wrapper(svg, title, desc, btn_text, key, grad)

    st.divider()
    st.subheader("History of payments")
    tx = st.session_state.transactions
    if not tx:
        st.info("No payments yet.")
    else:
        df = pd.DataFrame(tx)
        df = df.sort_values('ts', ascending=False)
        st.dataframe(df, use_container_width=True)
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Transactions CSV", data=csv_data, file_name="transactions.csv", mime="text/csv")

# ---------- Feature Pages (with logic) ----------

# UPI page
def upi_page():
    back_to_dashboard()
    st.header("UPI — Send Money")
    contacts = st.session_state.contacts
    names = [f"{c['name']} ({c['upi']})" for c in contacts]
    with st.form('upi_form'):
        to = st.selectbox("Select contact", names)
        amt = st.number_input("Amount (₹)", min_value=1.0, step=1.0)
        note = st.text_input("Note (optional)")
        method = st.selectbox("Method", ["UPI ID", "Phone", "QR"])
        send = st.form_submit_button("Send ₹")
    if send:
        st.session_state.transactions.append({
            'ts': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'type': 'out',
            'to_from': to,
            'amount': float(amt),
            'note': f"UPI via {method}. {note}".strip()
        })
        if st.session_state.bank.get('connected'):
            st.session_state.bank['balance'] -= float(amt)
        st.success(f"Sent ₹{amt:,.2f} to {to}")

    # show recent transactions + csv
    st.markdown("### Recent transactions")
    df_tx = pd.DataFrame(st.session_state.transactions)
    if not df_tx.empty:
        st.dataframe(df_tx.sort_values('ts', ascending=False), use_container_width=True)
        csv_data = df_tx.to_csv(index=False).encode('utf-8')
        st.download_button("Download Transactions CSV", data=csv_data, file_name="transactions.csv", mime="text/csv")
    else:
        st.info("No transactions yet.")

# Connect Bank
def connect_bank_page():
    back_to_dashboard()
    st.header("Connect Bank")
    banks = ["HDFC Bank", "ICICI Bank", "SBI", "Axis Bank", "Kotak Mahindra", "Yes Bank"]
    with st.form('bank_connect'):
        bank_name = st.selectbox("Select your bank", banks, index=0)
        starting_balance = st.number_input("Enter current balance (₹)", min_value=0.0, step=100.0)
        agree = st.checkbox("I authorise Prodoscope to view account balance.")
        submit = st.form_submit_button("Connect 🔗")
    if submit:
        if not agree:
            st.error("Please authorise to proceed.")
        else:
            st.session_state.bank['connected'] = True
            st.session_state.bank['name'] = bank_name
            st.session_state.bank['balance'] = float(starting_balance)
            st.success(f"Connected to {bank_name}. Balance set to ₹{starting_balance:,.2f}")
    if st.session_state.bank['connected']:
        st.info(f"Connected: {st.session_state.bank['name']} | Balance: ₹{st.session_state.bank['balance']:,.2f}")

# Check Balance
def check_balance_page():
    back_to_dashboard()
    st.header("Check Balance")
    if not st.session_state.bank['connected']:
        st.warning("No bank connected yet.")
        st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
        if st.button("Connect your bank now"):
            st.session_state.current_page = "Connect Bank"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.metric("Connected Bank", st.session_state.bank['name'])
        st.metric("Available Balance", f"₹{st.session_state.bank['balance']:,.2f}")
        st.progress(min(max(st.session_state.bank['balance'] / 100000.0, 0.0), 1.0))

# Split Groups
def split_groups_page():
    back_to_dashboard()
    st.header("Split Groups")
    all_contacts = [c['name'] for c in st.session_state.contacts]

    group_names = list(st.session_state.groups.keys()) or ["(no groups yet)"]
    colA, colB = st.columns([2,1])
    with colA:
        group_to_use = st.selectbox("Select group", group_names, index=0 if group_names[0] != "(no groups yet)" else 0)
    with colB:
        new_group = st.text_input("Create new group", placeholder="e.g., Flatmates")
        st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
        add_clicked = st.button("Add Group")
        st.markdown('</div>', unsafe_allow_html=True)
        if add_clicked and new_group:
            st.session_state.groups.setdefault(new_group, {'members':[], 'splits':[]})
            st.success(f"Group '{new_group}' created")
            st.rerun()

    if group_names and group_names[0] != "(no groups yet)":
        gname = group_to_use
        members = st.multiselect("Members", options=all_contacts, default=st.session_state.groups.get(gname, {}).get('members', []))
        st.session_state.groups.setdefault(gname, {'members':[], 'splits':[]})
        st.session_state.groups[gname]['members'] = members

        st.subheader("Create a split")
        with st.form('create_split'):
            total = st.number_input("Total bill amount (₹)", min_value=0.0, step=10.0)
            weekly_rem = st.checkbox("Weekly reminder")
            mode = st.radio("Split mode", ["Auto (equal)", "Manual"], horizontal=True)
            shares = {}
            if mode == "Manual":
                for m in members:
                    shares[m] = st.number_input(f"Share for {m}", min_value=0.0, step=1.0, key=f"share_{gname}_{m}")
            note = st.text_input("Note", placeholder="Dinner at Spice Hub")
            create = st.form_submit_button("Create Split ➗")
        if create:
            if not members:
                st.error("Add at least one member.")
            elif mode == "Manual" and abs(sum(shares.values()) - total) > 0.01:
                st.error("Manual shares must sum to total amount.")
            else:
                if mode == "Auto (equal)" and members:
                    equal = round(total / len(members), 2)
                    shares = {m: equal for m in members}
                st.session_state.groups[gname]['splits'].append({
                    'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'total': float(total),
                    'mode': 'auto' if mode.startswith('Auto') else 'manual',
                    'shares': shares,
                    'note': note,
                    'weekly_reminder': bool(weekly_rem)
                })
                st.success("Split created!")

        st.subheader("Group Splits")
        splits = st.session_state.groups.get(gname, {}).get('splits', [])
        if splits:
            for s in reversed(splits):
                with st.expander(f"{s['note'] or 'Split'} • ₹{s['total']:,.2f} • {s['created']}"):
                    st.write("Mode:", "Auto" if s['mode']=='auto' else "Manual")
                    st.write("Weekly reminder:", "On" if s['weekly_reminder'] else "Off")
                    st.table(pd.DataFrame([{'Member': m, 'Share (₹)': a} for m, a in s['shares'].items()]))
        else:
            st.info("No splits yet.")

# Daily Expense
def daily_expense_page():
    back_to_dashboard()
    st.header("Daily Expense Log")
    with st.form('expense_form', clear_on_submit=True):
        d = st.date_input("Date", value=date.today())
        amt = st.number_input("Amount (₹)", min_value=0.0, step=1.0)
        reason = st.text_input("Reason / Notes", placeholder="Groceries, commute, coffee…")
        add = st.form_submit_button("Add Expense ➕")
    if add:
        st.session_state.daily_expenses.append({'date': d.isoformat(), 'amount': float(amt), 'reason': reason})
        st.success("Expense added.")

    if st.session_state.daily_expenses:
        df = pd.DataFrame(st.session_state.daily_expenses)
        df['date'] = pd.to_datetime(df['date'])
        this_month = df[df['date'].dt.to_period('M') == pd.Timestamp.today().to_period('M')]
        if not this_month.empty:
            st.subheader("This Month Overview")
            by_day = this_month.groupby(this_month['date'].dt.day)['amount'].sum().reset_index(name='spent')
            top_day_row = by_day.sort_values('spent', ascending=False).head(1)
            top_day = int(top_day_row['date'].iloc[0]) if not top_day_row.empty else None
            top_spent = float(top_day_row['spent'].iloc[0]) if not top_day_row.empty else 0.0
            st.metric("Total Spent (This Month)", f"₹{this_month['amount'].sum():,.2f}")
            if top_day:
                reasons = this_month[this_month['date'].dt.day == top_day]['reason'].tolist()
                st.info(f"Highest spend on day {top_day}: ₹{top_spent:,.2f}. Reasons: {', '.join([r for r in reasons if r]) or '—'}")
            st.area_chart(by_day.set_index('date')['spent'])
        st.subheader("All Expenses")
        st.dataframe(df.sort_values('date', ascending=False), use_container_width=True)
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Expenses CSV", data=csv_data, file_name="expenses.csv", mime="text/csv")
    else:
        st.info("No expenses logged yet.")

# Savings
def savings_page():
    back_to_dashboard()
    st.header("Savings Log & Race")
    mk = month_key(date.today())
    sv = st.session_state.savings
    with st.form('savings_setup'):
        st.caption("Set your monthly target and reason (reminded daily)")
        target = st.number_input("This month's savings target (₹)", min_value=0.0, value=float(sv.get('target', 0.0)))
        reason = st.text_input("Reason for saving", value=sv.get('reason', ''))
        save_setup = st.form_submit_button("Save Target 🎯")
    if save_setup:
        st.session_state.savings.update({
            'month_key': mk,
            'target': float(target),
            'reason': reason,
            'logs': [l for l in sv.get('logs', []) if month_key(pd.to_datetime(l['date'])) == mk],
        })
        st.success("Target saved for this month.")
    with st.form('savings_log', clear_on_submit=True):
        amt = st.number_input("Add to savings (₹)", min_value=0.0, step=100.0)
        add = st.form_submit_button("Log Savings ➕")
    if add:
        st.session_state.savings.setdefault('logs', []).append({'date': date.today().isoformat(), 'amount': float(amt)})
        st.success("Savings logged.")
    sv = st.session_state.savings
    reached = sum(l['amount'] for l in sv.get('logs', []) if month_key(pd.to_datetime(l['date'])) == mk)
    target = sv.get('target', 0.0) if sv.get('month_key') == mk else 0.0
    pct = (reached/target) if target>0 else 0.0
    st.metric("Progress", f"₹{reached:,.2f} / ₹{target:,.2f}")
    st.progress(min(max(pct, 0.0), 1.0))
    if sv.get('reason'):
        st.info(f"Daily reminder: {sv['reason']}")
    st.subheader("End of Month Check")
    if target > 0:
        if reached >= target:
            st.success("Great! You met your savings target this month.")
        else:
            st.warning("Target not reached. Consider trimming the following expenses:")
            df = pd.DataFrame(st.session_state.daily_expenses)
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                this_month = df[df['date'].dt.to_period('M') == pd.Timestamp.today().to_period('M')]
                if not this_month.empty:
                    this_month = this_month.sort_values('amount', ascending=False).head(5)
                    st.table(this_month)

# Freelancer suggestions
def freelancer_page():
    back_to_dashboard()
    st.header("Freelancer Suggestions")
    skills = st.text_input("Your skills (comma-separated)", placeholder="e.g., writing, python, video editing")
    st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
    find = st.button("Get Freelancer Opportunities")
    st.markdown('</div>', unsafe_allow_html=True)
    if find:
        platforms = [
            {"Platform": "Upwork", "Focus": "Broad freelance marketplace"},
            {"Platform": "Fiverr", "Focus": "Gig-based services"},
            {"Platform": "Freelancer.com", "Focus": "Broad marketplace"},
            {"Platform": "Toptal", "Focus": "Elite dev/design/finance"},
            {"Platform": "Guru", "Focus": "General freelancing"},
            {"Platform": "PeoplePerHour", "Focus": "Hourly gigs"},
            {"Platform": "Contra", "Focus": "Commission-free client work"},
            {"Platform": "FlexJobs", "Focus": "Curated remote jobs"},
        ]
        st.table(pd.DataFrame(platforms))
        if skills.strip():
            st.caption(f"Tips for {skills}:")
            st.markdown("- Craft a niche title and 3 sample packages.\n- Showcase 2–3 strong portfolio items.\n- Start with smaller gigs to build reviews.")

# Financial knowledge (live via World Bank API fallback)
def fetch_worldbank_latest(country_code, indicator):
    """Fetch latest value for a World Bank indicator for a country.
       Returns (value, year) or (None, None) on failure."""
    try:
        url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator}?format=json&per_page=10"
        resp = requests.get(url, timeout=6)
        if resp.status_code != 200:
            return None, None
        data = resp.json()
        # data[1] is list of series points
        if isinstance(data, list) and len(data) > 1 and isinstance(data[1], list):
            for entry in data[1]:
                if entry and entry.get('value') is not None:
                    return entry['value'], entry.get('date')
    except Exception:
        return None, None
    return None, None

def financial_knowledge_page():
    back_to_dashboard()
    st.header("Financial Knowledge — Live data (World Bank)")
    st.caption("Data fetched from World Bank API when available; otherwise shows fallback estimates.")

    # Example: India's annual inflation proxy (CPI) - World Bank code: FP.CPI.TOTL.ZG
    infl_val, infl_year = fetch_worldbank_latest('IND', 'FP.CPI.TOTL.ZG')
    gdp_val, gdp_year = fetch_worldbank_latest('IND', 'NY.GDP.MKTP.KD.ZG')

    # fallback values (safe defaults) if API fails
    if infl_val is None:
        infl_val = 1.55  # fallback based on recent reports (replace when you want)
        infl_note = "fallback (no API)"
    else:
        infl_note = f"year: {infl_year}"

    if gdp_val is None:
        gdp_val = 6.5
        gdp_note = "fallback (no API)"
    else:
        gdp_note = f"year: {gdp_year}"

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Retail Inflation (India)", f"{infl_val:.2f}%", delta=None)
        st.caption(infl_note)
    with col2:
        st.metric("GDP Growth (India)", f"{gdp_val:.2f}%", delta=None)
        st.caption(gdp_note)

    st.subheader("How to beat inflation — Practical ideas")
    with st.expander("Core Ideas"):
        st.markdown("""
        - Build an emergency fund (3–6 months of expenses).
        - Automate investments monthly (SIPs, index funds).
        - Avoid high-interest debt; pay credit cards in full.
        - Upskill to increase income (freelancing, reskilling).
        - Diversify across asset classes.
        """)

# Financial games
def financial_games_page():
    back_to_dashboard()
    st.header("Financial Fun Games")
    st.write("Mini-challenges to build habits:")
    st.markdown("""
    - **No-Spend Streak**: Mark a day as \"no discretionary spend\". Keep a streak!
    - **Round-Up Challenge**: Every expense rounds up to the nearest ₹10 — the round-up goes to savings.
    - **Price Guess**: Before buying, guess total at checkout; compare with actual to build awareness.
    """)

# ---------- Router ----------
if st.session_state.current_page == "Top Page":
    top_page()
elif st.session_state.current_page == "UPI":
    upi_page()
elif st.session_state.current_page == "Connect Bank":
    connect_bank_page()
elif st.session_state.current_page == "Check Balance":
    check_balance_page()
elif st.session_state.current_page == "Split Groups":
    split_groups_page()
elif st.session_state.current_page == "Daily Expense Log":
    daily_expense_page()
elif st.session_state.current_page == "Savings Log & Race":
    savings_page()
elif st.session_state.current_page == "Financial Knowledge":
    financial_knowledge_page()
elif st.session_state.current_page == "Financial Games":
    financial_games_page()
elif st.session_state.current_page == "Freelancer Suggestions":
    freelancer_page()
else:
    top_page()
