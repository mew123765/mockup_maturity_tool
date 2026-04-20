import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Page Configuration
st.set_page_config(layout="wide", page_title="TMA Maturity Dashboard")

# --- UPDATED CSS ---
st.markdown('''
<style>
/* This blurs the entire app behind the login box */
.stApp {
    filter: ''' + ('blur(15px)' if not st.session_state.get("authenticated", False) else 'none') + ''';
}

/* Position the login box in the center of the screen */
.login-container {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    z-index: 10000;
    background: white;
    padding: 30px;
    border-radius: 15px;
    border: 1px solid #EB0A1E;
    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    text-align: center;
    width: 350px;
}

/* Yokoten & Folder Buttons */
.yokoten-box {
    width: 100%; padding: 20px; border-radius: 8px;
    text-align: center; font-weight: 800; color: white !important;
    margin-bottom: 10px;
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

# 2. Password Protection Logic (Clean version)
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    # Using an empty placeholder to force the login box to show on top of everything
    login_placeholder = st.empty()
    
    with login_placeholder.container():
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.write("### 🔒 Enterprise Access")
        st.write("Enter the password to view Maturity Data.")
        
        # This is the actual input field
        pwd = st.text_input("Password", type="password", label_visibility="collapsed")
        
        if st.button("Unlock Dashboard", use_container_width=True):
            if pwd == "Toyota2026": # <--- Change your password here
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Incorrect Password")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop() # This prevents the rest of the app from loading until authenticated

# --- THE REST OF YOUR DASHBOARD CODE STARTS HERE ---
# (df = load_data(), charts, layout etc.)

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
