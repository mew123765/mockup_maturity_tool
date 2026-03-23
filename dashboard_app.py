import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Page Configuration
st.set_page_config(layout="wide", page_title="TMA Maturity Dashboard")

# Custom CSS for Buttons, Detail Cards, and Yokoten Boxes
st.markdown("""
    <style>
    /* Radio Buttons Styling */
    div.row-widget.stRadio > div {
        flex-direction: row;
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
    }
    div.row-widget.stRadio label {
        background-color: #f1f3f5;
        padding: 8px 16px;
        border-radius: 5px;
        border: 1px solid #ced4da;
        cursor: pointer;
        transition: 0.2s;
        font-weight: 600;
        color: #212529 !important;
    }
    div.row-widget.stRadio input {
        display: none;
    }
    
    /* Solution Detail Cards */
    .detail-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 10px;
        min-height: 100px;
    }
    .card-title {
        color: #6c757d;
        font-size: 0.75rem;
        font-weight: bold;
        text-transform: uppercase;
        margin-bottom: 5px;
    }
    .card-content {
        color: #212529 !important;
        font-size: 0.95rem;
        font-weight: 500;
    }

    /* Yokoten Indicator Boxes */
    .yokoten-box {
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
        font-size: 1rem;
        color: white !important;
        margin-top: 10px;
    }
    .yokoten-can {
        background-color: #28A745;
    }
    .yokoten-cant {
        background-color: #DC3545;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Data Loader with Status Mapping
@st.cache_data
def load_data():
    target = 'maturity_mock_data.csv'
    if not os.path.exists(target):
        return pd.DataFrame()
    
    for enc in ['utf-8', 'latin1', 'iso-8859-1']:
        try:
            df = pd.read_csv(target, encoding=enc)
            df.columns = df.columns.str.strip()
            
            # Map Status to new labels requested
            status_map = {
                'Green': 'Have solution',
                'Yellow': 'Solution under develop',
                'Red': "Doesn't have solution"
            }
            df['Status'] = df['Status'].map(status_map)
            return df
        except:
            continue
    return pd.DataFrame()

df = load_data()

if not df.empty:
    st.title("🏭 Technology Maturity Dashboard")
    st.markdown("---")

    # 3. Theme Selector (Buttons)
    st.write("### 🏷️ Select Maturity Theme")
    theme_list = sorted(df['Theme'].dropna().unique().tolist())
    selected_theme = st.radio("Theme Selector", theme_list, label_visibility="collapsed")
    
    theme_df = df[df['Theme'] == selected_theme]

    if not theme_df.empty:
        # 4. Overview Chart
        level_map = theme_df[['Level', 'Level Name']].drop_duplicates().sort_values('Level')
        y_vals = level_map['Level'].tolist()
        y_text = level_map['Level Name'].tolist()

        # Define specific colors for the new labels
        color_map = {
            "Have solution": "#28A745", 
            "Solution under develop": "#FFD700", 
            "Doesn't have solution": "#FF4D4D"
        }
        
        # Summary View: Critical status first
        status_order = {'Doesn\'t have solution': 0, 'Solution under develop': 1, 'Have solution': 2}
        overview_data = theme_df.sort_values(by='Status', key=lambda x: x.map(status_order))
        overview_data = overview_data.groupby(['Company', 'Level']).first().reset_index()

        fig1 = px.scatter(
            overview_data, x="Company", y="Level", color="Status",
            color_discrete_map=color_map, symbol_sequence=['square'],
            height=400,
            category_orders={
                "Level": sorted(y_vals, reverse=True),
                "Status": ["Have solution", "Solution under develop", "Doesn't have solution"],
                "Company": ["TMA", "TMT", "TMMIN", "STM", "ASSB", "TMP", "TMV", "TMY", "IMC"]
            }
        )
        fig1.update_traces(marker=dict(size=35, line=dict(width=1, color='DarkSlateGrey')))
        fig1.update_yaxes(tickvals=y_vals, ticktext=y_text)
        st.plotly_chart(fig1, use_container_width=True)

        # 5. Level Selector (Buttons)
        st.markdown("---")
        st.write("### 📶 Select Level to Explore Use Cases")
        
        selected_level_val = st.radio(
            "Level Selector", 
            options=y_vals, 
            format_func=lambda x: f"Level {x}",
            horizontal=True, 
            label_visibility="collapsed"
        )

        level_df = theme_df[theme_df['Level'] == selected_level_val]

        if not level_df.empty:
            current_level_name = level_map[level_map['Level'] == selected_level_val]['Level Name'].iloc[0]
            st.subheader(f"Level {selected_level_val}: {current_level_name}")
            
            # Use Case Drill-down Chart
            fig2 = px.scatter(
                level_df, x="Company", y="Use Case", color="Status",
                color_discrete_map=color_map, symbol_sequence=['square'],
                height=450,
                category_orders={
                    "Company": ["TMA", "TMT", "TMMIN", "STM", "ASSB", "TMP", "TMV", "TMY", "IMC"],
                    "Status": ["Have solution", "Solution under develop", "Doesn't have solution"]
                }
            )
            fig2.update_traces(marker=dict(size=25, line=dict(width=1, color='DarkSlateGrey')))
            st.plotly_chart(fig2, use_container_width=True)

            # 6. Detailed Solution Information
            st.markdown("---")
            st.subheader("💡 Solution Details")
            
            d_col1, d_col2 = st.columns(2)
            with d_col1:
                target_affiliate = st.selectbox("1. Select Affiliate:", sorted(level_df['Company'].unique()))
            with d_col2:
                aff_specific_df = level_df[level_df['Company'] == target_affiliate]
                target_use_case = st.selectbox("2. Select Use Case:", aff_specific_df['Use Case'].unique())

            if target_use_case:
                detail = aff_specific_df[aff_specific_df['Use Case'] == target_use_case].iloc[0]
                
                # Top row for text boxes
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f'<div class="detail-card"><div class="card-title">Solution Name</div><div class="card-content">{detail["Solution Name"]}</div></div>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f'<div class="detail-card"><div class="card-title">Description</div><div class="card-content">{detail["Solution Description"]}</div></div>', unsafe_allow_html=True)
                with c3:
                    st.markdown(f'<div class="detail-card"><div class="card-title">Main Function</div><div class="card-content">{detail["Function in Solution"]}</div></div>', unsafe_allow_html=True)
                
                # Bottom row for the Yokoten Box
                st.write("**Yokoten Capability:**")
                is_yokoten = str(detail['Capability to implement to others']).strip().lower() == 'yes'
                
                if is_yokoten:
                    st.markdown('<div class="yokoten-box yokoten-can">Can Yokoten</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="yokoten-box yokoten-cant">Cann\'t Yokoten</div>', unsafe_allow_html=True)
else:
    st.error("Data file not found or empty.")
