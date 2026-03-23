import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Page Configuration
st.set_page_config(layout="wide", page_title="TMA Maturity Dashboard")

# Custom CSS for "Button" style selectors and stable display boxes
st.markdown("""
    <style>
    /* Make Radio buttons look like horizontal buttons */
    div.row-widget.stRadio > div {
        flex-direction: row;
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
    }
    div.row-widget.stRadio label {
        background-color: #f0f2f6;
        padding: 8px 16px;
        border-radius: 5px;
        border: 1px solid #d1d5db;
        cursor: pointer;
        transition: 0.2s;
        font-weight: 500;
        color: #333 !important;
    }
    div.row-widget.stRadio input {
        display: none;
    }
    /* Specific styling for the detail boxes to ensure text visibility */
    .detail-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #EB0A1E;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 10px;
        min-height: 120px;
    }
    .card-title {
        color: #777;
        font-size: 0.8rem;
        font-weight: bold;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .card-content {
        color: #111;
        font-size: 1rem;
        line-height: 1.4;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Data Loader
@st.cache_data
def load_data():
    # Attempt to load the extended data or the original
    target = 'maturity_mock_data.csv'
    if not os.path.exists(target):
        st.error(f"File {target} not found.")
        return pd.DataFrame()
    
    # Try common encodings
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

        # Group by Company/Level to show the 'Summary' status in the top chart
        # (Shows the most critical status if multiple use cases exist)
        status_priority = {'Red': 0, 'Yellow': 1, 'Green': 2}
        overview_data = theme_df.sort_values(by='Status', key=lambda x: x.map(status_priority))
        overview_data = overview_data.groupby(['Company', 'Level']).first().reset_index()

        color_map = {"Green": "#28A745", "Yellow": "#FFD700", "Red": "#FF4D4D"}
        
        fig1 = px.scatter(
            overview_data, x="Company", y="Level", color="Status",
            color_discrete_map=color_map, symbol_sequence=['square'],
            height=400,
            category_orders={
                "Level": sorted(y_vals, reverse=True),
                "Company": ["TMA", "TMT", "TMMIN", "STM", "ASSB", "TMP", "TMV", "TMY", "IMC"]
            }
        )
        fig1.update_traces(marker=dict(size=35, line=dict(width=1, color='DarkSlateGrey')))
        fig1.update_yaxes(tickvals=y_vals, ticktext=y_text)
        st.plotly_chart(fig1, use_container_width=True)

        # 5. Level Selector (Buttons)
        st.markdown("---")
        st.write("### 📶 Select Level to Explore All Use Cases")
        
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
            st.subheader(f"Use Case Detail: {current_level_name}")
            
            # Drill-down Chart (Shows multiple rows if multiple use cases exist)
            fig2 = px.scatter(
                level_df, x="Company", y="Use Case", color="Status",
                color_discrete_map=color_map, symbol_sequence=['square'],
                height=350,
                category_orders={"Company": ["TMA", "TMT", "TMMIN", "STM", "ASSB", "TMP", "TMV", "TMY", "IMC"]}
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
                # Filter for the specific affiliate to show THEIR use cases
                aff_specific_df = level_df[level_df['Company'] == target_affiliate]
                target_use_case = st.selectbox("2. Select Use Case:", aff_specific_df['Use Case'].unique())

            if target_use_case:
                # Pull the full row for the selected solution
                detail = aff_specific_df[aff_specific_df['Use Case'] == target_use_case].iloc[0]
                
                # Display using custom HTML cards for high visibility
                c1, c2, c3 = st.columns(3)
                
                with c1:
                    st.markdown(f'''<div class="detail-card">
                        <div class="card-title">Solution Name</div>
                        <div class="card-content">{detail["Solution Name"]}</div>
                    </div>''', unsafe_allow_html=True)
                
                with c2:
                    st.markdown(f'''<div class="detail-card">
                        <div class="card-title">Solution Description</div>
                        <div class="card-content">{detail["Solution Description"]}</div>
                    </div>''', unsafe_allow_html=True)
                
                with c3:
                    st.markdown(f'''<div class="detail-card">
                        <div class="card-title">Main Function</div>
                        <div class="card-content">{detail["Function in Solution"]}</div>
                    </div>''', unsafe_allow_html=True)
                
                # Excellence badge
                if str(detail['Capability to implement to others']).strip().lower() == 'yes':
                    st.success(f"🌟 **{target_affiliate}** is a Center of Excellence for this specific solution.")
