# app.py  —  Produscope (Streamlit)
# One-file demo: colorful, responsive, single-click flows, corrected logic.

import streamlit as st
import datetime as dt
from collections import defaultdict

# ----------------------------
# CONFIG & THEME
# ----------------------------
st.set_page_config(page_title="Produscope", layout="wide")

st.markdown(
    """
<style>
/* Background + typography */
.stApp { 
  background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
  font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, "Helvetica Neue", Arial;
}
/* Colorful gradient buttons */
.stButton button {
  border-radius: 12px;
  font-weight: 600;
  padding: .65rem 1.15rem;
  border: 0;
  background: linear-gradient(90deg, #00c6ff 0%, #0072ff 100%);
  color: white;
  transition: transform .05s ease, box-shadow .2s ease, opacity .2s ease;
  box-shadow: 0 6px 16px rgba(0,114,255,.25);
}
.stButton button:hover { 
  background: linear-gradient(90deg, #ff6a00 0%, #ee0979 100%);
  box-shadow: 0 8px 20px rgba(238,9,121,.25);
}
.stButton button:active { transform: translateY(1px); }

/* Card look */
.card {
  background: #fff; border-radius: 16px; padding: 16px;
  box-shadow: 0 10px 24px rgba(0,0,0,.08);
}

/* Mobile tweaks */
@media (max-width: 768px) {
  .stButton button { width: 100% !important; }
  div[data-testid="stMetricValue"] { font-size: 1.1rem !important; }
}

/* Section headings */
h1, h2, h3 { letter-spacing: .2px; }
</style>
""",
    unsafe_allow_html=True,
)

# ----------------------------
# STATE & HELPERS
# ----------------------------
def init_state():
    s = st.session_state
    s.setdefault("page", "signup")
    s.setdefault("user", None)
    s.setdefault("contacts", ["Aarav", "Riya", "Karan", "Meera", "Zoya"])
    s.setdefault("bank_connected", False)
    s.setdefault("bank_name", None)
    s.setdefault("bank_balance", 15200)  # mock balance
    s.setdefault("payments", [])  # list of dicts: {date, note, amount_signed(int), type}
    s.setdefault("expenses", [])  # list of dicts: {date, reason, amount}
    # savings: monthly target, reason, entries
    s.setdefault("savings", {"target": 0, "reason": "", "entries": []})  # entries: [{date, amount}]
    # groups: {name: {"members":[...], "expenses":[{desc, amount, date, split_type, shares{m:amt}, paid{m:bool}}]}}
    s.setdefault("groups", dict())
    s.setdefault("starting_budget", 10000)  # visible top-line "Total Amount" for demo

def go(page: str):
    st.session_state.page = page

def today():
    return dt.date.today()

def month_key(d):
    return d.strftime("%Y-%m")

def add_payment(note: str, amount: int, ptype: str):
    st.session_state.payments.insert(0, {"date": today(), "note": note, "amount": amount, "type": ptype})

def calc_metrics():
    """Compute dashboard metrics from state."""
    s = st.session_state
    # Spent = daily expenses + your share of group expenses + UPI sent (positive amounts treated as sent)
    spent_daily = sum(e["amount"] for e in s.expenses)
    spent_upi = sum(p["amount"] for p in s.payments if p["type"] == "upi_send" and p["amount"] > 0)
    # Your share in groups (assume user name "You" is auto-added when creating expenses)
    spent_groups = 0
    for g in s.groups.values():
        for ex in g["expenses"]:
            if "You" in ex["shares"]:
                spent_groups += ex["shares"]["You"]
    spent_total = int(spent_daily + spent_groups + spent_upi)

    total_amount = s.starting_budget  # demo: a fixed budget pool for the month
    remaining = max(total_amount - spent_total, 0)

    # Savings %
    target = s.savings.get("target", 0) or 0
    saved = sum(e["amount"] for e in s.savings.get("entries", []))
    savings_pct = int((saved / target) * 100) if target > 0 else 0
    return total_amount, spent_total, remaining, savings_pct

def month_group(values):
    buckets = defaultdict(int)
    for v in values:
        buckets[month_key(v["date"])] += v["amount"]
    return dict(buckets)

def unpaid_members(expense):
    """Return members that are not marked paid for a given group expense."""
    return [m for m, ok in expense["paid"].items() if not ok]

init_state()

# ----------------------------
# AUTH PAGES
# ----------------------------
if st.session_state.page == "signup":
    st.title("🌈 Produscope — Sign Up")
    with st.form("signup_form", clear_on_submit=False):
        colA, colB = st.columns(2)
        name = colA.text_input("Name")
        email = colB.text_input("Email")
        pwd = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Create account")
    if submitted:
        st.session_state.user = name or "User"
        go("dashboard")

    st.caption("Already on Produscope?")
    if st.button("Go to Sign In"):
        go("signin")

elif st.session_state.page == "signin":
    st.title("🔑 Sign In — Produscope")
    with st.form("signin_form"):
        email = st.text_input("Email")
        pwd = st.text_input("Password", type="password")
        ok = st.form_submit_button("Sign In")
    if ok:
        st.session_state.user = email or "User"
        go("dashboard")
    if st.button("Back to Sign Up"):
        go("signup")

# ----------------------------
# DASHBOARD
# ----------------------------
elif st.session_state.page == "dashboard":
    u = st.session_state.get("user", "User")
    st.title(f"📊 Dashboard — Welcome, {u}")

    total_amount, spent_total, remaining, savings_pct = calc_metrics()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Amount (budget)", f"₹{total_amount:,}")
    m2.metric("Amount Spent", f"₹{spent_total:,}")
    m3.metric("Remaining Amount", f"₹{remaining:,}")
    m4.metric("Savings Percent", f"{savings_pct}%")

    st.subheader("🚀 Quick Actions")
    features = [
        ("💸 UPI", "upi"),
        ("🏦 Connect Bank", "bank"),
        ("💰 Check Balance", "balance"),
        ("👥 Split Groups", "split"),
        ("📖 Financial Knowledge", "knowledge"),
        ("📝 Daily Expense Log", "expenses"),
        ("🎯 Savings Log & Race", "savings"),
        ("🎮 Finance Fun Games", "games"),
        ("💼 Freelancer Suggestions", "freelance"),
    ]
    for i in range(0, len(features), 3):
        cols = st.columns(3)
        for j, (label, page) in enumerate(features[i : i + 3]):
            if cols[j].button(label, use_container_width=True):
                go(page)

    st.subheader("📜 History of Payments")
    if st.session_state.payments:
        for p in st.session_state.payments[:15]:
            amt = f"₹{p['amount']:,}"
            st.write(f"{p['date']} — {p['note']} ({amt})")
    else:
        st.info("No payments yet.")

# ----------------------------
# UPI — contacts & send money
# ----------------------------
elif st.session_state.page == "upi":
    st.header("💸 UPI — Send Money")
    st.caption("Demo only — no real payments are processed.")

    with st.form("upi_form"):
        contact = st.selectbox("Choose contact", st.session_state.contacts)
        method = st.selectbox("Method", ["UPI ID", "Phone Number", "QR"])
        amount = st.number_input("Amount (₹)", min_value=0, step=10)
        note = st.text_input("Note (optional)", value="UPI transfer")
        send = st.form_submit_button("Send securely")
    if send:
        add_payment(f"Sent to {contact} via {method} — {note}", int(amount), "upi_send")
        st.success(f"✅ Sent ₹{int(amount):,} to {contact}")

    st.button("⬅ Back", on_click=lambda: go("dashboard"))

# ----------------------------
# CONNECT BANK
# ----------------------------
elif st.session_state.page == "bank":
    st.header("🏦 Connect Your Bank")
    with st.form("bank_form"):
        bank = st.selectbox("Select bank", ["SBI", "HDFC", "ICICI", "Axis", "Kotak"])
        connect = st.form_submit_button("Connect")
    if connect:
        st.session_state.bank_connected = True
        st.session_state.bank_name = bank
        st.success(f"✅ Connected to {bank}.")
    st.button("⬅ Back", on_click=lambda: go("dashboard"))

# ----------------------------
# CHECK BALANCE
# ----------------------------
elif st.session_state.page == "balance":
    st.header("💰 Account Balance")
    if not st.session_state.bank_connected:
        st.warning("No bank connected yet.")
    else:
        st.info(f"Connected bank: **{st.session_state.bank_name}**")
        st.success(f"Available balance: **₹{st.session_state.bank_balance:,}**")
    st.button("⬅ Back", on_click=lambda: go("dashboard"))

# ----------------------------
# SPLIT GROUPS — GPay-like flow
# ----------------------------
elif st.session_state.page == "split":
    st.header("👥 Split Groups (GPay-style)")
    st.caption("Create groups, add expenses, auto/manual split, mark who paid, weekly reminders.")

    # Create / update group
    with st.form("group_create"):
        gname = st.text_input("Group name")
        members = st.multiselect(
            "Members",
            options=["You"] + st.session_state.contacts,
            default=["You"],
            help="Include yourself as 'You' to track your share.",
        )
        created = st.form_submit_button("Create / Update Group")
    if created and gname:
        st.session_state.groups.setdefault(gname, {"members": members, "expenses": []})
        st.session_state.groups[gname]["members"] = members
        st.success(f"✅ Group '{gname}' saved with {len(members)} member(s).")

    if not st.session_state.groups:
        st.info("No groups yet. Create one above.")
    else:
        # pick a group to work with
        gsel = st.selectbox("Select a group", list(st.session_state.groups.keys()))
        group = st.session_state.groups[gsel]

        # Add expense to selected group (form to avoid double-click issues)
        with st.form("add_expense_form"):
            col1, col2 = st.columns([2, 1])
            desc = col1.text_input("Expense description", value="Dinner")
            amount = col2.number_input("Amount (₹)", min_value=0, step=50)
            split_type = st.radio("Split Type", ["Auto Split", "Manual Split"], horizontal=True)
            shares = {}
            if split_type == "Manual Split":
                st.caption("Enter share for each member (must sum to total).")
                for m in group["members"]:
                    shares[m] = st.number_input(f"{m}'s share (₹)", min_value=0, step=10, key=f"{gsel}_{m}_{len(group['expenses'])}")
            addit = st.form_submit_button("Add Expense")

        if addit and amount > 0:
            if split_type == "Auto Split":
                per = round(amount / max(len(group["members"]), 1), 2)
                shares = {m: per for m in group["members"]}
                # correct rounding error on the last member:
                gap = round(amount - sum(shares.values()), 2)
                if group["members"]:
                    shares[group["members"][-1]] = round(shares[group["members"][-1]] + gap, 2)
            else:
                total_manual = round(sum(shares.values()), 2)
                if total_manual != round(amount, 2):
                    st.error(f"Manual shares (₹{total_manual}) must equal total (₹{amount}). Not added.")
                else:
                    pass

            if split_type == "Auto Split" or round(sum(shares.values()), 2) == round(amount, 2):
                expense = {
                    "desc": desc,
                    "amount": float(amount),
                    "date": today(),
                    "split_type": "auto" if split_type == "Auto Split" else "manual",
                    "shares": shares,
                    "paid": {m: (m == "You") for m in group["members"]},  # mark 'You' as paid instantly
                }
                group["expenses"].insert(0, expense)
                st.success(f"✅ Added: {desc} — ₹{int(amount):,}")

        # Display current expenses for the group with pay tracking
        st.subheader(f"Expenses in '{gsel}'")
        if not group["expenses"]:
            st.info("No expenses yet.")
        else:
            for idx, ex in enumerate(group["expenses"]):
                with st.expander(f"{ex['date']} — {ex['desc']} (₹{ex['amount']:,})", expanded=False):
                    st.write(f"Split: **{ex['split_type']}**")
                    st.write("Shares:")
                    for m, a in ex["shares"].items():
                        st.write(f"- {m}: ₹{a}")
                    # toggle paid
                    cols = st.columns(len(ex["paid"]))
                    toggled = False
                    for i, member in enumerate(ex["paid"].keys()):
                        new_val = cols[i].checkbox(f"{member} paid", value=ex["paid"][member], key=f"paid_{gsel}_{idx}_{member}")
                        if new_val != ex["paid"][member]:
                            ex["paid"][member] = new_val
                            toggled = True
                    if toggled:
                        st.success("Updated paid status.")

                    # Reminder if > 7 days or someone unpaid
                    if unpaid_members(ex):
                        st.warning(f"Reminder: Pending — {', '.join(unpaid_members(ex))}")
                    if (today() - ex["date"]).days >= 7 and unpaid_members(ex):
                        st.info("⏰ Weekly reminder: Some members still haven't paid.")

    st.button("⬅ Back", on_click=lambda: go("dashboard"))

# ----------------------------
# DAILY EXPENSE LOG
# ----------------------------
elif st.session_state.page == "expenses":
    st.header("📝 Daily Expense Log")
    with st.form("expense_form"):
        reason = st.text_input("Reason", value="Food")
        amount = st.number_input("Amount (₹)", min_value=0, step=10)
        add = st.form_submit_button("Add Expense")
    if add and amount > 0:
        st.session_state.expenses.insert(0, {"date": today(), "reason": reason, "amount": int(amount)})
        st.success("✅ Expense added")

    if st.session_state.expenses:
        st.subheader("This Month — Summary")
        # Group by date (day) and show top spend day
        per_day = defaultdict(int)
        for e in st.session_state.expenses:
            per_day[e["date"]] += e["amount"]
        top_day, top_amt = None, 0
        for d, a in per_day.items():
            if a > top_amt:
                top_day, top_amt = d, a
        if top_day:
            st.info(f"Highest daily spend: **{top_day} — ₹{top_amt:,}**")

        st.subheader("All Expenses")
        for e in st.session_state.expenses[:100]:
            st.write(f"{e['date']} — ₹{e['amount']:,} for {e['reason']}")
    else:
        st.info("No expenses yet.")

    st.button("⬅ Back", on_click=lambda: go("dashboard"))

# ----------------------------
# SAVINGS LOG & RACE
# ----------------------------
elif st.session_state.page == "savings":
    st.header("🎯 Savings Log & Race")
    with st.form("savings_setup"):
        col1, col2 = st.columns(2)
        target = col1.number_input("Monthly saving target (₹)", min_value=0, step=500, value=st.session_state.savings.get("target", 0))
        reason = col2.text_input("Why are you saving?", value=st.session_state.savings.get("reason", "Goa Trip"))
        setit = st.form_submit_button("Save target")
    if setit:
        st.session_state.savings["target"] = int(target)
        st.session_state.savings["reason"] = reason
        st.success("✅ Target saved")

    with st.form("savings_entry"):
        amt = st.number_input("Add a saving entry (₹)", min_value=0, step=100)
        savebtn = st.form_submit_button("Log saving")
    if savebtn and amt > 0:
        st.session_state.savings["entries"].insert(0, {"date": today(), "amount": int(amt)})
        st.success("✅ Saving logged")

    target = st.session_state.savings.get("target", 0) or 0
    saved = sum(e["amount"] for e in st.session_state.savings.get("entries", []))
    pct = int(saved / target * 100) if target else 0
    st.progress(min(pct, 100))
    st.write(f"Progress: **₹{saved:,} / ₹{target:,}**  •  Reason: _{st.session_state.savings.get('reason','')}_")

    if target and saved < target:
        st.warning("Not at target yet — check unnecessary expenses below.")
        # Suggest "unnecessary" from expense log (simple heuristic: snacks/shopping/ride/etc.)
        flagged = [e for e in st.session_state.expenses if any(k in e["reason"].lower() for k in ["snack", "ride", "auto", "cab", "coffee", "swiggy", "zomato", "shopping"])]
        if flagged:
            st.write("Potentially unnecessary spends:")
            for e in flagged[:10]:
                st.write(f"- {e['date']} — ₹{e['amount']:,} on {e['reason']}")
    elif target and saved >= target:
        st.success("🎉 Target met! Great job.")

    st.button("⬅ Back", on_click=lambda: go("dashboard"))

# ----------------------------
# FINANCIAL KNOWLEDGE
# ----------------------------
elif st.session_state.page == "knowledge":
    st.header("📖 Financial Knowledge")
    c1, c2, c3 = st.columns(3)
    c1.metric("Inflation", "5.4%")
    c2.metric("GDP Growth", "6.8%")
    c3.metric("Repo Rate", "6.5%")

    st.markdown(
        """
**Beat Inflation:**
- Automate monthly savings (SIP mindset)
- Track daily spend & cut low-joy, high-cost items
- Build an emergency fund (3–6 months)

**Smart Saving Strategies:**
- 50/30/20 rule (Needs/Wants/Savings)
- Snowball small wins: start with ₹100/day
- Avoid high-interest debt traps

**Credit Basics:**
- Pay on time, keep utilization low
- Don’t open too many new accounts
"""
    )
    st.button("⬅ Back", on_click=lambda: go("dashboard"))

# ----------------------------
# FREELANCER SUGGESTIONS
# ----------------------------
elif st.session_state.page == "freelance":
    st.header("💼 Freelancer Suggestions")
    with st.form("freelance_form"):
        skill = st.text_input("Your skill (e.g., Canva, Python, Reels editing)")
        show = st.form_submit_button("Get sites")
    if show:
        st.success("Try: Upwork, Fiverr, Freelancer, Internshala, Contra, Toptal (for devs)")
        if skill:
            st.write(f"Tip: Search for **'{skill} freelance'** and add results to your campus CV/portfolio.")
    st.button("⬅ Back", on_click=lambda: go("dashboard"))

# ----------------------------
# GAMES (placeholder)
# ----------------------------
elif st.session_state.page == "games":
    st.header("🎮 Finance Fun Games")
    st.info("Mini games coming soon: Budget tycoon, Inflation dodger, Credit score quest.")
    st.button("⬅ Back", on_click=lambda: go("dashboard"))
