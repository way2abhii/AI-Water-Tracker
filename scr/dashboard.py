"""
dashboard.py  –  AI Water Tracker  |  Streamlit front-end
Includes: Signup, Login, Profile, Dashboard (log, history, charts, AI tips)
"""

import sys
from pathlib import Path
# Ensure the project root is on sys.path so `scr.*` imports work regardless
# of how Streamlit was invoked (e.g. `streamlit run scr/dashboard.py`)
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import streamlit as st
import pandas as pd
from datetime import datetime, date

from scr.agent import WaterIntakeAgent
from scr.database import (
    create_user,
    authenticate_user,
    get_user_by_id,
    update_user_profile,
    log_intake,
    get_today_total,
    get_intake_history,
    get_daily_totals,
    calculate_daily_goal,
)

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="💧 AI Water Tracker",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Global CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Dark gradient background */
.stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #1a1a4e 50%, #0f3460 100%);
    color: #e0e0ff;
}

/* Card style */
.glass-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 20px;
    padding: 2rem;
    margin: 1rem 0;
    backdrop-filter: blur(10px);
}

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, rgba(0,180,255,0.15), rgba(0,90,255,0.1));
    border: 1px solid rgba(0,180,255,0.3);
    border-radius: 16px;
    padding: 1.2rem 1.5rem;
    text-align: center;
}

.metric-value {
    font-size: 2.4rem;
    font-weight: 800;
    color: #00d4ff;
    line-height: 1;
}

.metric-label {
    font-size: 0.8rem;
    color: #a0aec0;
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* Progress bar */
.progress-wrap {
    background: rgba(255,255,255,0.08);
    border-radius: 999px;
    height: 18px;
    overflow: hidden;
    margin: 0.6rem 0;
}

.progress-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #00d4ff, #0057ff);
    transition: width 0.5s ease;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(135deg, #00d4ff, #0057ff) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.4rem !important;
    transition: opacity 0.2s ease !important;
}

.stButton>button:hover {
    opacity: 0.85 !important;
}

/* Inputs */
.stTextInput>div>div>input,
.stNumberInput>div>div>input,
.stSelectbox>div>div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 10px !important;
    color: #e0e0ff !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(15,12,41,0.9) !important;
    border-right: 1px solid rgba(255,255,255,0.08) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.04) !important;
    border-radius: 12px !important;
    padding: 4px !important;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    color: #a0aec0 !important;
    font-weight: 600 !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #00d4ff22, #0057ff22) !important;
    color: #00d4ff !important;
}

/* Divider */
hr { border-color: rgba(255,255,255,0.08) !important; }

/* Alert / info */
.stAlert { border-radius: 12px !important; }

/* Success green */
.stSuccess { background: rgba(0,200,100,0.12) !important; }

h1,h2,h3 { color: #e0e0ff !important; }
</style>
""", unsafe_allow_html=True)

# ─── Session state init ───────────────────────────────────────────────────────
for key, default in {
    "authenticated": False,
    "user": None,          # dict from DB
    "auth_page": "login",  # "login" | "signup"
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

agent = WaterIntakeAgent()


# ══════════════════════════════════════════════════════════════════════════════
#  AUTH PAGES
# ══════════════════════════════════════════════════════════════════════════════

def render_auth_header():
    st.markdown("""
    <div style="text-align:center; padding: 2rem 0 1rem;">
        <div style="font-size:3.5rem;">💧</div>
        <h1 style="font-size:2.2rem; font-weight:800; margin:0.2rem 0;">
            AI Water Tracker
        </h1>
        <p style="color:#a0aec0; font-size:1rem;">
            Stay hydrated, stay healthy — powered by AI
        </p>
    </div>
    """, unsafe_allow_html=True)


def page_login():
    render_auth_header()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 👋 Welcome back")

        username_or_email = st.text_input(
            "Username or Email", key="login_user",
            placeholder="your@email.com or username"
        )
        password = st.text_input(
            "Password", type="password", key="login_pass",
            placeholder="••••••••"
        )

        if st.button("🔑  Log In", use_container_width=True, key="btn_login"):
            if not username_or_email or not password:
                st.error("Please fill in all fields.")
            else:
                user = authenticate_user(username_or_email, password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.success(f"Welcome back, **{user['full_name'] or user['username']}**! 🎉")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Please try again.")

        st.markdown("---")
        st.markdown(
            "<p style='text-align:center;color:#a0aec0;font-size:0.9rem;'>"
            "Don't have an account?</p>",
            unsafe_allow_html=True,
        )
        if st.button("✨  Create Account", use_container_width=True, key="btn_go_signup"):
            st.session_state.auth_page = "signup"
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)


def page_signup():
    render_auth_header()

    col1, col2, col3 = st.columns([1, 2.5, 1])
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🚀 Create your account")

        full_name = st.text_input("Full Name", key="su_name", placeholder="Jane Doe")
        username  = st.text_input("Username", key="su_user", placeholder="jdoe99")
        email     = st.text_input("Email", key="su_email", placeholder="jane@example.com")

        c1, c2 = st.columns(2)
        with c1:
            password = st.text_input("Password", type="password", key="su_pass",
                                     placeholder="Min 6 characters")
        with c2:
            confirm  = st.text_input("Confirm Password", type="password", key="su_confirm",
                                     placeholder="Repeat password")

        st.markdown("#### 🏃 Tell us about yourself")
        c3, c4 = st.columns(2)
        with c3:
            weight_kg = st.number_input(
                "Body Weight (kg)", min_value=20.0, max_value=300.0,
                value=70.0, step=0.5, key="su_weight"
            )
        with c4:
            activity_level = st.selectbox(
                "Activity Level", key="su_activity",
                options=["sedentary", "light", "moderate", "active", "very_active"],
                index=2,
                format_func=lambda x: {
                    "sedentary":  "🛋️  Sedentary",
                    "light":      "🚶 Light",
                    "moderate":   "🏃 Moderate",
                    "active":     "🏋️ Active",
                    "very_active":"⚡ Very Active",
                }[x]
            )

        recommended_goal = calculate_daily_goal(weight_kg, activity_level)
        st.info(
            f"💡 Based on your profile, your recommended daily water goal is "
            f"**{recommended_goal:,} ml** ({recommended_goal/1000:.1f} L)."
        )

        if st.button("🎉  Sign Up", use_container_width=True, key="btn_signup"):
            # Validation
            errors = []
            if not full_name:
                errors.append("Full name is required.")
            if not username or len(username) < 3:
                errors.append("Username must be at least 3 characters.")
            if not email or "@" not in email:
                errors.append("Enter a valid email address.")
            if not password or len(password) < 6:
                errors.append("Password must be at least 6 characters.")
            if password != confirm:
                errors.append("Passwords do not match.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                result = create_user(
                    username=username,
                    email=email,
                    password=password,
                    full_name=full_name,
                    weight_kg=weight_kg,
                    activity_level=activity_level,
                )
                if result["success"]:
                    user = authenticate_user(username, password)
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.success(
                        f"✅ Account created! Your User ID is `{result['user_id']}`. Welcome aboard! 🎊"
                    )
                    st.rerun()
                else:
                    st.error(f"❌ {result['error']}")

        st.markdown("---")
        st.markdown(
            "<p style='text-align:center;color:#a0aec0;font-size:0.9rem;'>"
            "Already have an account?</p>",
            unsafe_allow_html=True,
        )
        if st.button("🔑  Log In instead", use_container_width=True, key="btn_go_login"):
            st.session_state.auth_page = "login"
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD (authenticated)
# ══════════════════════════════════════════════════════════════════════════════

def render_sidebar(user: dict):
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center;padding:1rem 0;">
            <div style="font-size:3rem;">💧</div>
            <h2 style="margin:0.3rem 0;font-size:1.3rem;">
                {user['full_name'] or user['username']}
            </h2>
            <p style="color:#a0aec0;font-size:0.8rem;margin:0;">
                @{user['username']}
            </p>
            <p style="color:#0057ff88;font-size:0.75rem;margin-top:4px;">
                ID: {user['user_id']}
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        st.markdown("### ⚡ Quick Log")
        quick_amounts = [150, 250, 350, 500, 750, 1000]
        cols = st.columns(3)
        for i, ml in enumerate(quick_amounts):
            if cols[i % 3].button(f"{ml}ml", key=f"quick_{ml}"):
                log_intake(user["user_id"], ml, note="Quick log")
                st.success(f"Logged {ml} ml!")
                st.rerun()

        st.divider()

        st.markdown("### 🔧 Custom Log")
        custom_ml = st.number_input(
            "Amount (ml)", min_value=50, max_value=2000,
            value=250, step=50, key="custom_ml_sidebar"
        )
        custom_note = st.text_input("Note (optional)", key="custom_note_sidebar",
                                    placeholder="Coffee, juice, water…")
        if st.button("➕ Log Custom", use_container_width=True, key="btn_custom_log"):
            log_intake(user["user_id"], custom_ml, note=custom_note)
            st.success(f"Logged {custom_ml} ml!")
            st.rerun()

        st.divider()

        if st.button("🚪 Log Out", use_container_width=True, key="btn_logout"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()


def render_progress_bar(current_ml: int, goal_ml: int):
    pct = min(current_ml / goal_ml * 100, 100)
    color = (
        "#ff4444" if pct < 30 else
        "#ffaa00" if pct < 60 else
        "#00cc88" if pct < 100 else
        "#00d4ff"
    )
    st.markdown(f"""
    <div class="progress-wrap">
        <div class="progress-fill"
             style="width:{pct:.1f}%; background: linear-gradient(90deg, {color}aa, {color});"></div>
    </div>
    <p style="text-align:right;color:#a0aec0;font-size:0.8rem;margin:0;">
        {pct:.1f}% of daily goal
    </p>
    """, unsafe_allow_html=True)


def tab_overview(user: dict):
    today_total = get_today_total(user["user_id"])
    goal = user["daily_goal_ml"]
    remaining = max(goal - today_total, 0)
    pct = min(today_total / goal * 100, 100)

    # Top metrics
    c1, c2, c3, c4 = st.columns(4)
    metrics = [
        ("💧 Today's Intake", f"{today_total:,} ml", f"{today_total/1000:.2f} L"),
        ("🎯 Daily Goal",     f"{goal:,} ml",         f"{goal/1000:.1f} L"),
        ("⏳ Remaining",      f"{remaining:,} ml",    f"{remaining/1000:.2f} L"),
        ("📈 Progress",       f"{pct:.1f}%",           "of today's goal"),
    ]
    for col, (label, value, sub) in zip([c1, c2, c3, c4], metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{value}</div>
                <div class="metric-label">{label}</div>
                <div style="color:#718096;font-size:0.75rem;margin-top:2px;">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Progress bar
    st.markdown("#### 🌊 Today's Hydration Progress")
    render_progress_bar(today_total, goal)

    # Motivation / status
    if pct >= 100:
        st.success("🎉 **Amazing!** You've hit your water goal for today. Keep it up!")
    elif pct >= 75:
        st.info(f"💪 **Almost there!** Just {remaining:,} ml more to reach your goal.")
    elif pct >= 40:
        st.warning(f"⚠️ **Keep drinking!** You still need {remaining:,} ml today.")
    else:
        st.error(f"🚨 **Hydration low!** Drink up — {remaining:,} ml left to go.")

    st.divider()

    # 7-day chart
    st.markdown("#### 📊 Last 7 Days")
    daily_data = get_daily_totals(user["user_id"], days=7)
    if daily_data:
        df = pd.DataFrame(daily_data).sort_values("date")
        df["goal"] = goal
        df.rename(columns={"date": "Date", "total_ml": "Consumed (ml)"}, inplace=True)
        df = df.set_index("Date")
        st.bar_chart(df[["Consumed (ml)"]], color="#00d4ff")
    else:
        st.info("No historical data yet. Start logging to see your trends!")


def tab_history(user: dict):
    st.markdown("#### 📋 Intake History")
    records = get_intake_history(user["user_id"])
    if not records:
        st.info("No records yet. Start logging water to see your history!")
        return

    df = pd.DataFrame(records)
    df = df.rename(columns={
        "intake_ml":  "Amount (ml)",
        "note":       "Note",
        "logged_at":  "Logged At",
        "date":       "Date",
    })
    df["Amount (L)"] = (df["Amount (ml)"] / 1000).round(2)

    # Summary per day
    st.markdown("##### Daily Totals")
    daily = df.groupby("Date")["Amount (ml)"].sum().reset_index()
    daily.columns = ["Date", "Total (ml)"]
    daily["Total (L)"] = (daily["Total (ml)"] / 1000).round(2)
    daily["vs Goal"] = daily["Total (ml)"].apply(
        lambda x: f"✅ {x/user['daily_goal_ml']*100:.0f}%"
        if x >= user["daily_goal_ml"] else f"❌ {x/user['daily_goal_ml']*100:.0f}%"
    )
    st.dataframe(daily, use_container_width=True)

    st.markdown("##### All Logs")
    st.dataframe(
        df[["Logged At", "Amount (ml)", "Amount (L)", "Note"]],
        use_container_width=True,
    )


def tab_ai_analysis(user: dict):
    st.markdown("#### 🤖 AI Hydration Analysis")

    today_total = get_today_total(user["user_id"])
    goal = user["daily_goal_ml"]

    st.markdown(
        f"Today you've had **{today_total:,} ml** out of your goal of **{goal:,} ml**."
    )

    if st.button("✨ Get AI Analysis", use_container_width=False, key="btn_ai"):
        with st.spinner("Consulting your AI hydration coach…"):
            analysis = agent.analyze_intake(
                intake_ml=today_total,
                daily_goal_ml=goal,
                weight_kg=user["weight_kg"],
                activity_level=user["activity_level"],
            )
        st.markdown(f"""
        <div class="glass-card">
            <h4>🤖 Your Personalised Hydration Tip</h4>
            <p style="line-height:1.7;font-size:1rem;">{analysis}</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.markdown("#### 💬 Motivational Quote")
    if st.button("🎲 Inspire Me!", key="btn_quote"):
        with st.spinner("Fetching inspiration…"):
            quote = agent.get_motivational_quote()
        st.markdown(f"""
        <div class="glass-card" style="border-color:rgba(0,212,255,0.3);">
            <p style="font-size:1.15rem;font-style:italic;color:#00d4ff;">
                "{quote}"
            </p>
        </div>
        """, unsafe_allow_html=True)


def tab_profile(user: dict):
    st.markdown("#### 👤 Your Profile")

    st.markdown(f"""
    <div class="glass-card">
        <p><strong>User ID:</strong> <code>{user['user_id']}</code></p>
        <p><strong>Username:</strong> {user['username']}</p>
        <p><strong>Email:</strong> {user['email']}</p>
        <p><strong>Member since:</strong> {user.get('created_at','—')[:10]}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### ✏️ Edit Profile")
    with st.form("profile_form"):
        full_name_new = st.text_input("Full Name", value=user.get("full_name", ""))
        weight_new    = st.number_input(
            "Body Weight (kg)", min_value=20.0, max_value=300.0,
            value=float(user.get("weight_kg", 70)), step=0.5
        )
        activity_new  = st.selectbox(
            "Activity Level",
            options=["sedentary", "light", "moderate", "active", "very_active"],
            index=["sedentary","light","moderate","active","very_active"].index(
                user.get("activity_level","moderate")
            ),
            format_func=lambda x: {
                "sedentary":  "🛋️  Sedentary",
                "light":      "🚶 Light",
                "moderate":   "🏃 Moderate",
                "active":     "🏋️ Active",
                "very_active":"⚡ Very Active",
            }[x]
        )

        submitted = st.form_submit_button("💾 Save Changes", use_container_width=True)
        if submitted:
            new_goal = update_user_profile(
                user["user_id"], full_name_new, weight_new, activity_new
            )
            # Refresh session user dict
            updated = get_user_by_id(user["user_id"])
            st.session_state.user = updated
            st.success(
                f"✅ Profile updated! New daily goal: **{new_goal:,} ml** ({new_goal/1000:.1f} L)."
            )
            st.rerun()


def page_dashboard():
    user = st.session_state.user

    render_sidebar(user)

    # Header
    hour = datetime.now().hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"
    st.markdown(f"""
    <div style="padding: 1.5rem 0 0.5rem;">
        <h1 style="font-size:2rem;font-weight:800;margin:0;">
            {greeting}, {user['full_name'].split()[0] if user['full_name'] else user['username']}! 💧
        </h1>
        <p style="color:#a0aec0;margin:0;">
            {date.today().strftime('%A, %B %d, %Y')}
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    tabs = st.tabs(["🏠 Overview", "📋 History", "🤖 AI Analysis", "👤 Profile"])
    with tabs[0]:
        tab_overview(user)
    with tabs[1]:
        tab_history(user)
    with tabs[2]:
        tab_ai_analysis(user)
    with tabs[3]:
        tab_profile(user)


# ══════════════════════════════════════════════════════════════════════════════
#  ROUTER
# ══════════════════════════════════════════════════════════════════════════════

def main():
    if st.session_state.authenticated and st.session_state.user:
        page_dashboard()
    else:
        if st.session_state.auth_page == "signup":
            page_signup()
        else:
            page_login()


main()
