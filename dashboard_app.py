import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Page Configuration
st.set_page_config(layout="wide", page_title="TMA Maturity Dashboard")

# Custom CSS for Horizontal Rectangle Buttons and Yokoten UI
st.markdown("""
    <style>
    /* --- Horizontal Rectangle Button Styling --- */
    div.row-widget.stRadio > div {
        flex-direction: row;
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
        justify-content: flex-start;
    }
    
    /* Individual Button Style */
    div.row-widget.stRadio label {
        background-color: #f8f9fa;
        padding: 12px 24px;
        border-radius: 4px; /* Rectangle style */
        border: 1px solid #dee2e6;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 600;
        color: #495057 !important;
        min-width: 150px;
        text-align: center;
        display: inline-block;
    }

    /* Hover State */
    div.row-widget.stRadio label:hover {
        background-color: #e9ecef;
        border-color: #adb5bd;
    }

    /* Active/Selected State (Streamlit specific hack) */
    div.row-widget.stRadio div[data-testid="stMarkdownContainer"] p {
        margin-bottom: 0px;
    }
    
    /* Hide the radio circle */
    div.row-widget.stRadio input {
        display: none;
    }

    /* --- Solution Detail Cards --- */
    .detail-card {
        background-color: #ffffff;
        padding: 18px;
        border-radius: 6px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        min-height: 110px;
    }
    .card-title {
        color: #868e96;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 8px;
        letter-spacing: 0.5px;
    }
    .card-content {
        color: #212529 !important;
        font-size: 1rem;
        font-weight: 500;
        line-height: 1.5;
    }

    /* --- Yokoten Status Boxes --- */
    .yokoten-container {
        margin-top: 10px;
    }
    .yokoten-label {
        font-weight: bold;
        margin-bottom: 5px;
        font-size: 0.9rem;
    }
    .yokoten-box {
        padding: 12px;
        border-radius: 4px;
        text-align: center;
        font-weight: 800;
        font-size: 1.1rem;
        color: white !important;
        text-transform: uppercase;
    }
    .yokoten-can {
        background-color: #28A745;
        border: 1px solid #1e7e34;
    }
    .yokoten-cant {
        background-color: #DC3545;
        border: 1px solid #bd2130;
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
            
            # Map Status to your requested labels
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

    # 3. Theme Selector (Horizontal Rectangle Buttons)
    st.write("### 🏷️ Select Maturity Theme")
    theme_list = sorted(df['Theme'].dropna().unique().tolist())
    selected_theme = st.radio("Theme Selector", theme_list, label_visibility="collapsed")
    
    theme_df = df[df['Theme'] == selected_theme]

    if not theme_df.empty:
        # 4. Overview Chart
        level_map = theme_df[['Level', 'Level Name']].drop_duplicates().sort_values('Level')
        y_vals = level_map['Level'].tolist()
        y_text = level_map['Level Name'].tolist()

        color_map = {
            "Have solution": "#28A745", 
            "Solution under develop": "#FFD700", 
            "Doesn't have solution": "#FF4D4D"
        }
        
        # Summary View (Prioritize showing issues if multiple cases exist)
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

        # 5. Level Selector (Horizontal Rectangle Buttons)
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
                    "Company": ["TMA", "TMT", "TMMIN", "STM", "ASSB", "TMP", "TMV", "TMY", "IMC"]
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
                
                # Solution Content Row
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f'<div class="detail-card"><div class="card-title">Solution Name</div><div class="card-content">{detail["Solution Name"]}</div></div>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f'<div class="detail-card"><div class="card-title">Description</div><div class="card-content">{detail["Solution Description"]}</div></div>', unsafe_allow_html=True)
                with c3:
                    st.markdown(f'<div class="detail-card"><div class="card-title">Main Function</div><div class="card-content">{detail["Function in Solution"]}</div></div>', unsafe_allow_html=True)
                
                # Yokoten Box Row
                st.markdown('<div class="yokoten-container">', unsafe_allow_html=True)
                st.write("**Yokoten Capability:**")
                is_yokoten = str(detail['Capability to implement to others']).strip().lower() == 'yes'
                
                if is_yokoten:
                    st.markdown('<div class="yokoten-box yokoten-can">Can Yokoten</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="yokoten-box yokoten-cant">Cann\'t Yokoten</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
else:
    st.error("CSV file not found. Please upload 'maturity_mock_data.csv' to your repository.")
