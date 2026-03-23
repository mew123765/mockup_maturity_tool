import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Page Configuration
st.set_page_config(layout="wide", page_title="TMA Maturity Dashboard")

# 2. Smart Data Loader (with encoding safety)
@st.cache_data
def load_data():
    target_file = 'maturity_mock_data.csv'
    if not os.path.exists(target_file):
        return pd.DataFrame()
    for enc in ['utf-8', 'latin1', 'iso-8859-1']:
        try:
            return pd.read_csv(target_file, encoding=enc)
        except:
            continue
    return pd.DataFrame()

df = load_data()

if not df.empty:
    df.columns = df.columns.str.strip()
    st.title("🏭 Technology Maturity Dashboard")
    st.markdown("---")

    # 3. Theme Selector
    theme_list = sorted(df['Theme'].dropna().unique().tolist())
    selected_theme = st.selectbox("Select Maturity Theme", theme_list)
    theme_df = df[df['Theme'] == selected_theme]

    if not theme_df.empty:
        # 4. Level Overview Chart
        level_map = theme_df[['Level', 'Level Name']].drop_duplicates().sort_values('Level')
        y_vals = level_map['Level'].tolist()
        y_text = level_map['Level Name'].tolist()

        color_map = {"Green": "#28A745", "Yellow": "#FFD700", "Red": "#FF4D4D"}
        
        # Grid view (Pivot to show one status per cell)
        overview_pivot = theme_df.groupby(['Company', 'Level'])['Status'].first().reset_index()

        fig1 = px.scatter(
            overview_pivot, x="Company", y="Level", color="Status",
            color_discrete_map=color_map, symbol_sequence=['square'],
            height=450,
            category_orders={"Level": sorted(y_vals, reverse=True)}
        )
        fig1.update_traces(marker=dict(size=35, line=dict(width=1, color='DarkSlateGrey')))
        fig1.update_yaxes(tickvals=y_vals, ticktext=y_text)
        st.plotly_chart(fig1, use_container_width=True)

        # 5. Level & Use Case Drill Down
        st.markdown("---")
        selected_level = st.radio("Select Level to Drill Down:", y_vals, horizontal=True)
        level_df = theme_df[theme_df['Level'] == selected_level]

        st.subheader(f"Level {selected_level} Use Cases")
        fig2 = px.scatter(
            level_df, x="Company", y="Use Case", color="Status",
            color_discrete_map=color_map, symbol_sequence=['square'],
            height=400
        )
        fig2.update_traces(marker=dict(size=25))
        st.plotly_chart(fig2, use_container_width=True)

        # 6. Detailed Solution Comparison
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            target_affiliate = st.selectbox("Select Affiliate:", sorted(level_df['Company'].unique()))
        with col2:
            aff_df = level_df[level_df['Company'] == target_affiliate]
            target_use_case = st.selectbox("Select Specific Use Case:", aff_df['Use Case'].unique())

        if target_use_case:
            detail = aff_df[aff_df['Use Case'] == target_use_case].iloc[0]
            c1, c2, c3 = st.columns(3)
            c1.info(f"**Solution:**\n{detail['Solution Name']}")
            c2.success(f"**Description:**\n{detail['Solution Description']}")
            c3.warning(f"**Function:**\n{detail['Function in Solution']}")
