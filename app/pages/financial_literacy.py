import streamlit as st

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Finance Learning Path",
    page_icon="💸",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- HIDE STREAMLIT DEFAULT UI (except sidebar) ---
hide_default_format = """
    <style>
        #MainMenu {visibility: hidden;}  /* Hide the top-right menu */
        footer {visibility: hidden;}     /* Hide footer */
        header {visibility: hidden;}     /* Hide Streamlit header */
    </style>
"""
st.markdown(hide_default_format, unsafe_allow_html=True)

if 'page_status' not in st.session_state:
    st.session_state['page_status'] = 'login' # Start at login/home page
    st.switch_page("pages/login.py")

# --- USER SESSION ---
if "username" not in st.session_state:
    st.session_state.username = "Unknown user"

# --- HEADER ---
st.markdown(f"### 👋 Welcome, **{st.session_state.username}!**")
st.caption("Continue your personalized finance learning journey below.")

st.title("💸 Finance Learning Path")
st.caption("Master finance step-by-step — unlock the next topic by completing the test.")

# --- CURRICULUM TOPICS ---
topics = {
    "Finance Fundamentals": [
        "Introduction to Finance",
        "Time Value of Money",
        "Financial Statements",
        "Budgeting & Saving",
        "Understanding Credit & Debt"
    ],
    "Investments & Markets": [
        "Stock Market Basics",
        "Bonds & Fixed Income",
        "Mutual Funds & ETFs",
        "Derivatives",
        "Portfolio Diversification",
        "Risk & Return"
    ],
    "Personal Finance": [
        "Income & Expenses",
        "Emergency Fund Planning",
        "Retirement Planning",
        "Tax Planning",
        "Insurance Basics"
    ],
    "Corporate Finance": [
        "Capital Budgeting",
        "Cost of Capital",
        "Financial Ratios",
        "Capital Structure",
        "Dividend Policy"
    ],
    "Financial Literacy & Behavior": [
        "Behavioral Finance",
        "Emotional Investing",
        "Financial Decision-Making",
        "Wealth Mindset"
    ],
    "Macroeconomics & Policy": [
        "Economic Indicators",
        "Inflation & Interest Rates",
        "Monetary Policy",
        "Fiscal Policy",
        "Global Financial Systems"
    ],
    "Banking & FinTech": [
        "Central Banking",
        "Retail & Commercial Banking",
        "Digital Payments",
        "Blockchain & Cryptocurrencies",
        "FinTech Innovations"
    ],
    "Data-Driven Finance": [
        "Financial Modeling",
        "Technical Analysis",
        "Fundamental Analysis",
        "Quantitative Finance",
        "Algorithmic Trading"
    ],
    "Advanced & Professional Topics": [
        "Corporate Valuation",
        "Mergers & Acquisitions",
        "Risk Management",
        "Financial Regulations",
        "ESG & Sustainable Finance"
    ]
}

# --- STATE MANAGEMENT ---
if "completed_topics" not in st.session_state:
    st.session_state.completed_topics = []

# --- SIDEBAR (Progress Tracker Only) ---
with st.sidebar:
    st.header("📘 Progress Tracker")
    progress = len(st.session_state.completed_topics)
    total = sum(len(t) for t in topics.values())
    st.progress(progress / total)
    st.write(f"**Progress:** {progress}/{total} topics completed")

# --- MAIN CONTENT ---
st.markdown("---")
st.subheader("Your Curriculum")

for section, subtopics in topics.items():
    with st.expander(f"📂 {section}", expanded=False):
        for i, topic in enumerate(subtopics):
            completed = topic in st.session_state.completed_topics
            locked = not completed and any(t not in st.session_state.completed_topics for t in subtopics[:i])
            
            if locked:
                st.button(f"🔒 {topic}", disabled=True)
            elif completed:
                st.success(f"✅ {topic} (Completed)")
            else:
                if st.button(f"▶️ {topic}"):
                    st.session_state.selected_topic = topic

# --- TOPIC PROMPT AREA ---
if "selected_topic" in st.session_state:
    st.markdown("---")
    st.subheader(f"📖 {st.session_state.selected_topic}")
    st.info("🧠 Enter your thoughts or answer the test prompt below:")
    st.text_area("Your Answer / Prompt Input", key="user_input")
    st.button("Submit Test", key="submit_test")

# --- FOOTER (LOGOUT) ---
st.markdown("---")
col1, col2 = st.columns([4, 1])
with col2:
    if st.button("🚪 Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("You have been logged out.")
        st.stop()
