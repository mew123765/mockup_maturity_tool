import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Page Configuration
st.set_page_config(layout="wide", page_title="TMA Maturity Dashboard")

# --- CUSTOM CSS: COMPACT & BRANDED LOOK ---
st.markdown('''
<style>
/* Horizontal Radio Buttons as 'Tabs' */
[data-testid="stRadio"] div[role="radiogroup"] {
    flex-direction: row !important;
    display: flex !important;
    gap: 8px !important;
    flex-wrap: wrap !important;
}
[data-testid="stRadio"] div[role="radiogroup"] label {
    background-color: #f8f9fa !important;
    padding: 8px 16px !important;
    border-radius: 4px !important;
    border: 1px solid #dee2e6 !important;
    cursor: pointer !important;
    min-width: 140px !important;
    display: flex !important;
    justify-content: center !important;
}
[data-testid="stRadio"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
    color: #212529 !important;
    font-weight: 600 !important;
    margin: 0 !important;
}
[data-testid="stRadio"] div[role="radiogroup"] label > div:first-child { display: none !important; }
[data-testid="stRadio"] div[role="radiogroup"] [aria-checked="true"] {
    background-color: #ffffff !important;
    border: 2px solid #EB0A1E !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
}
/* Detail Cards */
.detail-card {
    background-color: #ffffff; padding: 12px; border-radius: 6px;
    border: 1px solid #dee2e6; margin-bottom: 8px;
}
.card-title { color: #6c757d; font-size: 0.75rem; font-weight: bold; text-transform: uppercase; margin-bottom: 3px; }
.card-content { color: #111111 !important; font-size: 0.95rem; }
/* Yokoten Status */
.yokoten-box {
    padding: 10px; border-radius: 4px; text-align: center;
    font-weight: 700; color: white !important; text-transform: uppercase;
}
.yokoten-can { background-color: #28A745; }
.yokoten-cant { background-color: #DC3545; }
.block-container { padding-top: 2rem !important; }
</style>
''', unsafe_allow_html=True)

# 2. Data Loader
@st.cache_data
def load_data():
    target = 'final_maturity_data.csv'
    if not os.path.exists(target):
        st.error("Data file 'final_maturity_data.csv' not found.")
        return pd.DataFrame()
    df = pd.read_csv(target)
    # Map the Red/Yellow/Green to clear legend labels
    status_map = {'Green': 'Have solution', 'Yellow': 'Solution under develop', 'Red': "Doesn't have solution"}
    df['Status_Label'] = df['Status'].map(status_map)
    return df

df = load_data()

if not df.empty:
    st.title("🏭 Technology Maturity Dashboard")
    
    # --- 1. THEME SELECTION ---
    theme_list = sorted(df['Theme'].dropna().unique().tolist())
    st.write("**1. Select Maturity Theme**")
    selected_theme = st.radio("Theme Selector", theme_list, horizontal=True, label_visibility="collapsed")
    theme_df = df[df['Theme'] == selected_theme]

    if not theme_df.empty:
        # --- 2. OVERVIEW CHART (LEVELS) ---
        level_map = theme_df[['Level', 'Level Name']].drop_duplicates().sort_values('Level')
        y_vals = level_map['Level'].tolist()
        y_text = [f"L{row['Level']}: {row['Level Name']}" for _, row in level_map.iterrows()]
        color_map = {"Have solution": "#28A745", "Solution under develop": "#FFD700", "Doesn't have solution": "#FF4D4D"}
        
        # Aggregate to show one summary dot per company per level
        status_priority = {'Have solution': 2, 'Solution under develop': 1, "Doesn't have solution": 0}
        ov_data = theme_df.sort_values(by='Status_Label', key=lambda x: x.map(status_priority), ascending=False)
        ov_data = ov_data.groupby(['Company', 'Level', 'Level Name'])['Status_Label'].first().reset_index()

        fig1 = px.scatter(
            ov_data, x="Company", y="Level", color="Status_Label",
            color_discrete_map=color_map, symbol_sequence=['square'], height=380,
            category_orders={
                "Level": sorted(y_vals, reverse=True),
                "Company": ["TMA", "TMT", "TMMIN", "STM", "ASSB", "TMP", "TMV", "TMY", "IMC"]
            }
        )
        fig1.update_traces(marker=dict(size=45, line=dict(width=2, color='DarkSlateGrey')))
        fig1.update_layout(xaxis=dict(title=None), yaxis=dict(tickvals=y_vals, ticktext=y_text, title=None), 
                          legend=dict(orientation="h", y=1.1, x=1, title=None))
        st.plotly_chart(fig1, use_container_width=True)

        # --- 3. LEVEL & USE CASE SELECTION ---
        st.write("**2. Select Level for Use Case Detail**")
        available_levels = sorted(theme_df['Level'].unique())
        selected_level = st.radio("Level Selector", options=available_levels, format_func=lambda x: f"Level {x}", horizontal=True, label_visibility="collapsed")
        
        level_df = theme_df[theme_df['Level'] == selected_level]

        if not level_df.empty:
            current_lname = level_map[level_map['Level'] == selected_level]['Level Name'].iloc[0]
            st.markdown(f"**Level {selected_level} Detail:** *{current_lname}*")
            
            # Dynamic Height based on Use Cases
            num_use_cases = len(level_df['Use case'].unique())
            chart_height = max(300, num_use_cases * 45)

            fig2 = px.scatter(
                level_df, x="Company", y="Use case", color="Status_Label",
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

            # --- 4. SOLUTION DRILL-DOWN ---
            st.markdown("**3. Technical Solution Details**")
            d_col1, d_col2 = st.columns(2)
            with d_col1:
                target_affiliate = st.selectbox("Select Affiliate:", sorted(level_df['Company'].unique()))
            with d_col2:
                aff_spec = level_df[level_df['Company'] == target_affiliate]
                target_use_case = st.selectbox("Select Use Case:", sorted(aff_spec['Use case'].unique()))

            if target_use_case:
                detail = aff_spec[aff_spec['Use case'] == target_use_case].iloc[0]
                c1, c2, c3 = st.columns([2, 2, 1])
                with c1: st.markdown(f'<div class="detail-card"><div class="card-title">Solution Name</div><div class="card-content">{detail["Solution Name"]}</div></div>', unsafe_allow_html=True)
                with c2: st.markdown(f'<div class="detail-card"><div class="card-title">Function</div><div class="card-content">{detail["Function in Solution"]}</div></div>', unsafe_allow_html=True)
                with c3:
                    is_yokoten = str(detail['Capability to implement to others']).strip().lower() == 'yes'
                    y_cls = "yokoten-can" if is_yokoten else "yokoten-cant"
                    y_txt = "Can Yokoten" if is_yokoten else "Cannot Yokoten"
                    st.markdown(f'<div class="yokoten-box {y_cls}">{y_txt}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="detail-card"><div class="card-title">Solution Description</div><div class="card-content">{detail["Solution Description"]}</div></div>', unsafe_allow_html=True)
