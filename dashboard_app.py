import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Page Configuration
st.set_page_config(layout="wide", page_title="TMA Maturity Dashboard")

# --- UPDATED CUSTOM CSS ---
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

/* Container for the 4/5 and 1/5 split */
.detail-container {
    display: flex;
    gap: 20px;
    align-items: stretch;
}

.text-stack {
    flex: 4; 
    display: flex;
    flex-direction: column;
    gap: 30px;
}

/* Specific Box Styling */
.detail-card {
    background-color: #ffffff; 
    padding: 12px; 
    border-radius: 8px;
    border: 1px solid #dee2e6;
    color: #111111 !important;
}

.card-title { color: #6c757d; font-size: 0.75rem; font-weight: bold; text-transform: uppercase; margin-bottom: 2px; }
.card-content { color: #000000 !important; font-size: 0.95rem; }

/* Scrollable Box for Function */
.scroll-box {
    max-height: 150px;
    overflow-y: auto;
    padding-right: 5px;
}

/* Yokoten & Folder Buttons */
.yokoten-box {
    width: 100%;
    padding: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    font-weight: 800 !important;
    color: white !important;
    text-transform: uppercase;
    text-align: center;
    font-size: 1.1rem;
    margin-bottom: 10px;
}
.yokoten-can { background-color: #28A745 !important; border: 1px solid #1e7e34; }
.yokoten-cant { background-color: #DC3545 !important; border: 1px solid #bd2130; }

.folder-btn {
    display: block; 
    width: 100%; 
    padding: 15px;
    background-color: #0078D4; 
    color: white !important;
    text-align: center; 
    border-radius: 8px; 
    text-decoration: none;
    font-weight: bold; 
    font-size: 0.9rem;
    border: 1px solid #005a9e;
}
.folder-btn:hover {
    background-color: #005a9e;
    text-decoration: none;
}
</style>
''', unsafe_allow_html=True)

# 1.1. Authentication Logic
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.write("### 🔒 Toyota Enterprise Access")
    pwd = st.text_input("Enter Password", type="password", key="login_field")
    if st.button("Unlock Dashboard", use_container_width=True):
        if pwd == "Toyota2026": 
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect Password")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="blur-content">', unsafe_allow_html=True)
    st.title("Loading Secure Data...")
    st.write("█" * 100)
    st.write("█" * 80)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# 2. Robust Data Loader
@st.cache_data
def load_data():
    file_name = 'maturity_mock_data.csv'
    if not os.path.exists(file_name):
        st.error(f"File '{file_name}' not found.")
        return pd.DataFrame()
    
    df = pd.read_csv(file_name)
    df.columns = [c.strip() for c in df.columns]
    
    # Map Casing
    cols_map = {c.lower(): c for c in df.columns}
    if 'use case' in cols_map: df = df.rename(columns={cols_map['use case']: 'Use Case'})
    if 'status' in cols_map: df = df.rename(columns={cols_map['status']: 'Status'})
        
    # Standardize Status
    status_map = {'Green': 'Have solution', 'Yellow': 'Solution under develop', 'Red': "Doesn't have solution"}
    if 'Status' in df.columns:
        df['Status_Label'] = df['Status'].map(status_map).fillna("Unknown Status")
    else:
        df['Status'] = 'Red'
        df['Status_Label'] = "Doesn't have solution"
        
    return df

df = load_data()

if not df.empty:
    st.title("🏭 Technology Maturity Dashboard")
    
    # 1. THEME SELECTION
    theme_list = sorted(df['Theme'].dropna().unique().tolist())
    st.write("**1. Select Maturity Theme**")
    selected_theme = st.radio("Theme Selector", theme_list, horizontal=True, label_visibility="collapsed")
    theme_df = df[df['Theme'] == selected_theme]

    if not theme_df.empty:
        # 2. OVERVIEW CHART
        level_map = theme_df[['Level', 'Level Name']].drop_duplicates().sort_values('Level')
        y_vals = level_map['Level'].tolist()
        y_text = [f"L{row['Level']}: {row['Level Name']}" for _, row in level_map.iterrows()]
        color_map = {"Have solution": "#28A745", "Solution under develop": "#FFD700", "Doesn't have solution": "#FF4D4D"}
        
        status_priority = {'Have solution': 2, 'Solution under develop': 1, "Doesn't have solution": 0, "Unknown Status": -1}
        
        ov_data = theme_df.copy()
        ov_data = ov_data.sort_values(by='Status_Label', key=lambda x: x.map(status_priority), ascending=False)
        ov_data = ov_data.groupby(['Company', 'Level', 'Level Name'])['Status_Label'].first().reset_index()

        fig1 = px.scatter(
            ov_data, x="Company", y="Level", color="Status_Label",
            color_discrete_map=color_map, symbol_sequence=['square'], height=380,
            category_orders={
                "Level": sorted(y_vals, reverse=True),
                "Company": ["TMA", "TMT", "TMMIN", "STM", "ASSB", "TMP", "TMV", "TMY", "IMC"],
                "Status_Label": ["Have solution", "Solution under develop", "Doesn't have solution"]
            }
        )
        fig1.update_traces(marker=dict(size=45, line=dict(width=2, color='DarkSlateGrey')))
        fig1.update_layout(xaxis=dict(title=None), yaxis=dict(tickvals=y_vals, ticktext=y_text, title=None), 
                          legend=dict(orientation="h", y=1.1, x=1, title=None))
        st.plotly_chart(fig1, use_container_width=True)

        # 3. LEVEL SELECTION
        st.write("**2. Select Level for Use Case Detail**")
        available_levels = sorted(theme_df['Level'].unique())
        selected_level = st.radio("Level Selector", options=available_levels, format_func=lambda x: f"Level {x}", horizontal=True, label_visibility="collapsed")
        
        level_df = theme_df[theme_df['Level'] == selected_level]

        if not level_df.empty:
            num_use_cases = len(level_df['Use Case'].unique())
            chart_height = max(300, num_use_cases * 45)

            fig2 = px.scatter(
                level_df, x="Company", y="Use Case", color="Status_Label",
                color_discrete_map=color_map, symbol_sequence=['square'], height=chart_height,
                category_orders={
                    "Company": ["TMA", "TMT", "TMMIN", "STM", "ASSB", "TMP", "TMV", "TMY", "IMC"],
                    "Status_Label": ["Have solution", "Solution under develop", "Doesn't have solution"]
                }
            )
            fig2.update_traces(marker=dict(size=30, line=dict(width=1.5, color='DarkSlateGrey')))
            fig2.update_layout(xaxis=dict(title=None), yaxis=dict(title=None), 
                              legend=dict(orientation="h", y=1.1, x=1, title=None))
            st.plotly_chart(fig2, use_container_width=True)

            # --- 4. DRILL-DOWN ---
            st.markdown("**3. Technical Solution Details**")
            d_col1, d_col2 = st.columns(2)
            with d_col1:
                target_affiliate = st.selectbox("Select Affiliate:", sorted(level_df['Company'].unique()))
            with d_col2:
                aff_spec = level_df[level_df['Company'] == target_affiliate]
                target_use_case = st.selectbox("Select Use Case:", sorted(aff_spec['Use Case'].unique()))

            if target_use_case:
                detail = aff_spec[aff_spec['Use Case'] == target_use_case].iloc[0]
    
                # Check Yokoten Status
                is_yokoten = str(detail.get('Capability to implement to others', 'No')).strip().lower() == 'yes'
                y_cls = "yokoten-can" if is_yokoten else "yokoten-cant"
                y_txt = "Can Yokoten" if is_yokoten else "Cannot Yokoten"
                
                # Get OneDrive URL
                folder_url = detail.get("Folder_URL", "#")

                left_info, right_status = st.columns([4, 1])

                with left_info:
                    st.markdown(f'''
                        <div class="detail-card">
                            <div class="card-title">Solution Name</div>
                            <div class="card-content">{detail.get("Solution Name", "N/A")}</div>
                        </div>''', unsafe_allow_html=True)
        
                    st.markdown(f'''
                        <div class="detail-card">
                            <div class="card-title">Solution Description</div>
                            <div class="card-content">{detail.get("Solution Description", "N/A")}</div>
                        </div>''', unsafe_allow_html=True)
        
                    st.markdown(f'''
                        <div class="detail-card">
                            <div class="card-title">Function (Scrollable)</div>
                            <div class="card-content scroll-box">{detail.get("Function in Solution", "N/A")}</div>
                        </div>''', unsafe_allow_html=True)

                with right_status:
                    # Combined Status Box and OneDrive Link
                    st.markdown(f'''
                        <div class="yokoten-box {y_cls}">{y_txt}</div>
                        <a href="{folder_url}" target="_blank" class="folder-btn">
                            📁 View OneDrive Folder For More Detail
                        </a>
                        ''', unsafe_allow_html=True)
