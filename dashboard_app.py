import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Page Configuration
st.set_page_config(layout="wide", page_title="TMA Maturity Dashboard")

# --- CUSTOM CSS ---
st.markdown('''
<style>
/* Login Overlay Styling */
.login-overlay {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(10px);
    z-index: 9999;
    display: flex; justify-content: center; align-items: center;
}
.login-box {
    padding: 40px; background: white; border-radius: 12px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1); border: 1px solid #ddd;
}

/* Tab/Radio Button Styling */
[data-testid="stRadio"] div[role="radiogroup"] { flex-direction: row !important; gap: 10px; }
[data-testid="stRadio"] div[role="radiogroup"] label {
    background-color: #f8f9fa !important; padding: 10px 20px !important;
    border-radius: 6px !important; border: 1px solid #dee2e6 !important;
}
[data-testid="stRadio"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
    color: #111 !important; font-weight: bold;
}
[data-testid="stRadio"] div[role="radiogroup"] label > div:first-child { display: none !important; }
[data-testid="stRadio"] div[role="radiogroup"] [aria-checked="true"] { border: 2px solid #EB0A1E !important; }

/* Detail Cards */
.detail-card { background: #fff; padding: 15px; border-radius: 8px; border: 1px solid #dee2e6; margin-bottom: 15px; }
.card-title { color: #6c757d; font-size: 0.75rem; font-weight: bold; text-transform: uppercase; }
.card-content { color: #000 !important; font-size: 1rem; }
.scroll-box { max-height: 150px; overflow-y: auto; }

/* Status & Folder Buttons */
.yokoten-box {
    width: 100%; padding: 20px; border-radius: 8px;
    text-align: center; font-weight: 800; color: white !important;
}
.yokoten-can { background-color: #28A745 !important; }
.yokoten-cant { background-color: #DC3545 !important; }

.folder-btn {
    display: block; width: 100%; padding: 15px; margin-top: 15px;
    background-color: #0078D4; color: white !important;
    text-align: center; border-radius: 8px; text-decoration: none;
    font-weight: bold; font-size: 0.9rem;
}
.folder-btn:hover { background-color: #005a9e; }
</style>
''', unsafe_allow_html=True)

# 2. Password Protection Logic
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.markdown('<div class="login-overlay"><div class="login-box">', unsafe_allow_html=True)
    st.write("### 🔒 Enterprise Access")
    pwd = st.text_input("Enter Password", type="password")
    if st.button("Unlock Dashboard"):
        if pwd == "Toyota2026":  # Replace with your password
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect Password")
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.stop()

# 3. Data Loading
@st.cache_data
def load_data():
    df = pd.read_csv('maturity_mock_data.csv')
    df.columns = [c.strip() for c in df.columns]
    # Ensure Status mapping exists for the chart
    status_map = {'Green': 'Have solution', 'Yellow': 'Solution under develop', 'Red': "Doesn't have solution"}
    df['Status_Label'] = df['Status'].map(status_map).fillna("Unknown")
    return df

df = load_data()

# 4. Header & Filters
st.title("🏭 Technology Maturity Dashboard")
theme_list = sorted(df['Theme'].unique())
selected_theme = st.radio("Select Theme", theme_list, horizontal=True)
theme_df = df[df['Theme'] == selected_theme]

# 5. Maturity Chart (Scatter Plot)
st.subheader(f"Maturity Overview: {selected_theme}")
color_map = {"Have solution": "#28A745", "Solution under develop": "#FFD700", "Doesn't have solution": "#FF4D4D"}
fig = px.scatter(theme_df, x="Company", y="Level", color="Status_Label",
                 color_discrete_map=color_map, symbol_sequence=['square'], height=400,
                 category_orders={"Company": ["TMA", "TMT", "TMMIN", "STM", "ASSB", "TMP", "TMV", "TMY", "IMC"]})
fig.update_traces(marker=dict(size=40, line=dict(width=2, color='DarkSlateGrey')))
st.plotly_chart(fig, use_container_width=True)

# 6. Detail Drill-Down (4/5 Layout)
st.divider()
st.subheader("💡 Technical Use Case Details")
col_a, col_b = st.columns(2)
with col_a:
    affiliate = st.selectbox("Affiliate", sorted(theme_df['Company'].unique()))
with col_b:
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
        # Yokoten Status
        is_yokoten = str(detail.get('Capability to implement to others', 'No')).strip().lower() == 'yes'
        y_cls = "yokoten-can" if is_yokoten else "yokoten-cant"
        y_txt = "Can Yokoten" if is_yokoten else "No Yokoten"
        
        # Folder Link from CSV
        folder_url = detail.get("Folder_URL", "#")
        
        st.markdown(f'''
            <div class="yokoten-box {y_cls}">{y_txt}</div>
            <a href="{folder_url}" target="_blank" class="folder-btn">📁 View OneDrive Folder</a>
        ''', unsafe_allow_html=True)
