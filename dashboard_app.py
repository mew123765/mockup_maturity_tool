import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(layout="wide", page_title="TMA Maturity Dashboard")

# --- CUSTOM CSS ---
st.markdown('''
<style>
/* Login Card Styling (High Priority Layer) */
.login-card {
    position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
    z-index: 10000; background: white; padding: 40px; border-radius: 15px;
    border: 2px solid #EB0A1E; box-shadow: 0 15px 35px rgba(0,0,0,0.3);
    text-align: center; width: 400px;
}

/* Background Blur - Active only when not authenticated */
.blur-content {
    filter: blur(15px); pointer-events: none; user-select: none;
}

/* Tab/Radio Button Styling */
[data-testid="stRadio"] div[role="radiogroup"] { flex-direction: row !important; gap: 10px; }
[data-testid="stRadio"] div[role="radiogroup"] label {
    background-color: #f1f3f5 !important; padding: 10px 20px !important;
    border-radius: 6px !important; border: 1px solid #ced4da !important;
}
[data-testid="stRadio"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
    color: #111 !important; font-weight: 700 !important;
}
[data-testid="stRadio"] div[role="radiogroup"] label > div:first-child { display: none !important; }
[data-testid="stRadio"] div[role="radiogroup"] [aria-checked="true"] { border: 2px solid #EB0A1E !important; background: white !important; }

/* Detail Cards */
.detail-card { background: #fff; padding: 15px; border-radius: 8px; border: 1px solid #dee2e6; margin-bottom: 12px; }
.card-title { color: #6c757d; font-size: 0.75rem; font-weight: bold; text-transform: uppercase; }
.card-content { color: #000 !important; font-size: 0.95rem; }
.scroll-box { max-height: 120px; overflow-y: auto; }

/* Status & Folder Buttons */
.yokoten-box {
    width: 100%; padding: 20px; border-radius: 8px;
    text-align: center; font-weight: 800; color: white !important; margin-bottom: 10px;
}
.yokoten-can { background-color: #28A745 !important; }
.yokoten-cant { background-color: #DC3545 !important; }

.folder-btn {
    display: block; width: 100%; padding: 15px;
    background-color: #0078D4; color: white !important;
    text-align: center; border-radius: 8px; text-decoration: none;
    font-weight: bold; font-size: 0.9rem;
}
</style>
''', unsafe_allow_html=True)

# 2. Authentication Logic
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    # Login card (Sharp)
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.write("### 🔒 Toyota Enterprise Access")
    pwd = st.text_input("Enter Password", type="password", key="login_field")
    if st.button("Unlock Dashboard", use_container_width=True):
        if pwd == "Toyota2026": # Create your password here
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect Password")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Blurred background simulation
    st.markdown('<div class="blur-content">', unsafe_allow_html=True)
    st.title("Loading Secure Data...")
    st.write("█" * 100)
    st.write("█" * 80)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# 3. Data Loading
@st.cache_data
def load_data():
    df = pd.read_csv('maturity_mock_data.csv')
    df.columns = [c.strip() for c in df.columns]
    status_map = {'Green': 'Have solution', 'Yellow': 'Solution under develop', 'Red': "Doesn't have solution"}
    df['Status_Label'] = df['Status'].map(status_map).fillna("Unknown")
    return df

df = load_data()
affiliate_order = ["TMA", "TMT", "TMMIN", "STM", "ASSB", "TMP", "TMV", "TMY", "IMC"]

st.title("🏭 Technology Maturity Dashboard")

# --- CHART 1: THEME OVERVIEW (THE MISSING CHART) ---
st.subheader("1. Theme Maturity Overview")
# Aggregate to find the max level reached for each theme/company
theme_overview = df.groupby(['Company', 'Theme'])['Level'].max().reset_index()

fig1 = px.density_heatmap(
    theme_overview, x="Theme", y="Company", z="Level",
    color_continuous_scale="RdYlGn", text_auto=True,
    category_orders={"Company": affiliate_order},
    height=400, labels={"Level": "Max Level"}
)
fig1.update_layout(xaxis_title=None, yaxis_title=None)
st.plotly_chart(fig1, use_container_width=True)

# --- CHART 2: LEVEL OVERVIEW ---
st.divider()
st.subheader("2. Level Detail by Theme")
theme_list = sorted(df['Theme'].unique())
selected_theme = st.radio("Select Theme to Filter:", theme_list, horizontal=True)

theme_df = df[df['Theme'] == selected_theme]
color_map = {"Have solution": "#28A745", "Solution under develop": "#FFD700", "Doesn't have solution": "#FF4D4D"}

fig2 = px.scatter(
    theme_df, x="Company", y="Level", color="Status_Label",
    color_discrete_map=color_map, symbol_sequence=['square'], height=400,
    category_orders={"Company": affiliate_order, "Level": [5, 4, 3, 2]}
)
fig2.update_traces(marker=dict(size=35, line=dict(width=2, color='DarkSlateGrey')))
fig2.update_layout(xaxis_title=None, yaxis_title="Maturity Level")
st.plotly_chart(fig2, use_container_width=True)

# --- 3. TECHNICAL DRILL-DOWN ---
st.divider()
st.subheader("3. Technical Use Case Details")
col_sel1, col_sel2 = st.columns(2)
with col_sel1:
    affiliate = st.selectbox("Affiliate", sorted(theme_df['Company'].unique()))
with col_sel2:
    use_cases = theme_df[theme_df['Company'] == affiliate]
    selected_uc = st.selectbox("Use Case", sorted(use_cases['Use Case'].unique()))

if selected_uc:
    detail = use_cases[use_cases['Use Case'] == selected_uc].iloc[0]
    
    left_info, right_status = st.columns([4, 1])
    with left_info:
        st.markdown(f'''
            <div class="detail-card"><div class="card-title">Solution Name</div><div class="card-content">{detail.get("Solution Name", "N/A")}</div></div>
            <div class="detail-card"><div class="card-title">Solution Description</div><div class="card-content">{detail.get("Solution Description", "N/A")}</div></div>
            <div class="detail-card"><div class="card-title">Function (Scrollable)</div><div class="card-content scroll-box">{detail.get("Function in Solution", "N/A")}</div></div>
        ''', unsafe_allow_html=True)
        
    with right_status:
        # Yokoten Box
        is_yokoten = str(detail.get('Capability to implement to others', 'No')).strip().lower() == 'yes'
        y_cls = "yokoten-can" if is_yokoten else "yokoten-cant"
        y_txt = "Can Yokoten" if is_yokoten else "No Yokoten"
        
        # OneDrive Link
        folder_url = detail.get("Folder_URL", "#")
        
        st.markdown(f'''
            <div class="yokoten-box {y_cls}">{y_txt}</div>
            <a href="{folder_url}" target="_blank" class="folder-btn">📁 View OneDrive Folder</a>
        ''', unsafe_allow_html=True)
