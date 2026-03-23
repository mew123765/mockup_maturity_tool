import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Page Configuration
st.set_page_config(layout="wide", page_title="TMA Maturity Dashboard")

# Custom CSS to create "Buttons" from Radio Selectors
st.markdown("""
    <style>
    div.row-widget.stRadio > div {
        flex-direction: row;
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
    }
    div.row-widget.stRadio label {
        background-color: #f0f2f6;
        padding: 10px 20px;
        border-radius: 8px;
        border: 1px solid #d1d5db;
        cursor: pointer;
        transition: 0.3s;
    }
    div.row-widget.stRadio input {
        display: none;
    }
    /* Hover and Selection Effect */
    div.row-widget.stRadio label:hover {
        background-color: #e2e8f0;
        border-color: #EB0A1E;
    }
    .info-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        height: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Robust Data Loader
@st.cache_data
def load_data():
    # Looks for the original or the extended version
    for target in ['maturity_mock_data.csv', 'maturity_mock_data_extended.csv']:
        if os.path.exists(target):
            for enc in ['utf-8', 'latin1', 'iso-8859-1']:
                try:
                    df = pd.read_csv(target, encoding=enc)
                    df.columns = df.columns.str.strip()
                    return df
                except:
                    continue
    return pd.DataFrame()

df = load_data()

if not df.empty:
    st.title("🏭 Technology Maturity Dashboard")
    st.markdown("---")

    # 3. Theme Selector (STITCH-STYLE BUTTONS)
    st.write("### 🏷️ Select Maturity Theme")
    theme_list = sorted(df['Theme'].dropna().unique().tolist())
    selected_theme = st.radio("Theme Selector", theme_list, label_visibility="collapsed")
    
    theme_df = df[df['Theme'] == selected_theme]

    if not theme_df.empty:
        # 4. Dynamic Y-Axis Labels (Changes based on Theme)
        level_map = theme_df[['Level', 'Level Name']].drop_duplicates().sort_values('Level')
        y_vals = level_map['Level'].tolist()
        y_text = level_map['Level Name'].tolist()

        st.subheader(f"Maturity Overview: {selected_theme}")

        # Status Priority: Red > Yellow > Green (for the summary view)
        status_order = {'Red': 0, 'Yellow': 1, 'Green': 2}
        
        # We group to show 1 square per Level/Company in the top chart
        overview_pivot = theme_df.sort_values(by='Status', key=lambda x: x.map(status_order))
        overview_pivot = overview_pivot.groupby(['Company', 'Level']).first().reset_index()

        color_map = {"Green": "#28A745", "Yellow": "#FFD700", "Red": "#FF4D4D"}
        
        fig1 = px.scatter(
            overview_pivot, x="Company", y="Level", color="Status",
            color_discrete_map=color_map, symbol_sequence=['square'],
            height=450,
            category_orders={
                "Level": sorted(y_vals, reverse=True),
                "Company": ["TMA", "TMT", "TMMIN", "STM", "ASSB", "TMP", "TMV", "TMY", "IMC"]
            }
        )
        fig1.update_traces(marker=dict(size=38, line=dict(width=1, color='DarkSlateGrey')))
        fig1.update_yaxes(tickvals=y_vals, ticktext=y_text)
        st.plotly_chart(fig1, use_container_width=True)

        # 5. Level Selector (STITCH-STYLE BUTTONS)
        st.markdown("---")
        st.write("### 📶 Select Level to view Multiple Use Cases")
        
        button_labels = {row['Level']: f"Level {row['Level']}" for _, row in level_map.iterrows()}
        selected_level_val = st.radio(
            "Level Selector", options=y_vals, 
            format_func=lambda x: button_labels.get(x),
            horizontal=True, label_visibility="collapsed"
        )

        # Filter for the specific Level
        level_df = theme_df[theme_df['Level'] == selected_level_val]

        if not level_df.empty:
            st.subheader(f"Use Case Drill-down: {level_map[level_map['Level']==selected_level_val]['Level Name'].iloc[0]}")
            
            # Use Case Chart: This now shows ALL use cases on the Y-axis
            fig2 = px.scatter(
                level_df, x="Company", y="Use Case", color="Status",
                color_discrete_map=color_map, symbol_sequence=['square'],
                height=500, # Increased height to fit multiple use cases
                category_orders={
                    "Company": ["TMA", "TMT", "TMMIN", "STM", "ASSB", "TMP", "TMV", "TMY", "IMC"],
                    "Use Case": sorted(level_df['Use Case'].unique())
                }
            )
            fig2.update_traces(marker=dict(size=25, line=dict(width=1, color='DarkSlateGrey')))
            st.plotly_chart(fig2, use_container_width=True)

            # 6. Details Section (DROPDOWNS)
            st.markdown("---")
            st.subheader("💡 Solution Details")
            col1, col2 = st.columns(2)

            with col1:
                target_affiliate = st.selectbox("Select Affiliate:", sorted(level_df['Company'].unique()))

            with col2:
                # This ensures the dropdown shows ALL use cases for that affiliate/level
                aff_use_cases = level_df[level_df['Company'] == target_affiliate]
                target_use_case = st.selectbox("Select Use Case to see Details:", aff_use_cases['Use Case'].unique())

            if target_use_case:
                detail = aff_use_cases[aff_use_cases['Use Case'] == target_use_case].iloc[0]
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f'<div class="info-box"><b>Solution Name</b><br><br>{detail["Solution Name"]}</div>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f'<div class="info-box"><b>Description</b><br><br>{detail["Solution Description"]}</div>', unsafe_allow_html=True)
                with c3:
                    st.markdown(f'<div class="info-box"><b>Function</b><br><br>{detail["Function in Solution"]}</div>', unsafe_allow_html=True)
                
                if detail['Capability to implement to others'] == 'Yes':
                    st.success(f"🌟 **{target_affiliate}** can support other affiliates as a Center of Excellence.")
        else:
            st.info("No data available for this specific level.")
else:
    st.error("CSV File not found. Please ensure 'maturity_mock_data.csv' is uploaded to GitHub.")
