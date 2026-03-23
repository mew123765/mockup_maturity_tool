import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Setup
st.set_page_config(layout="wide", page_title="TMA Maturity Dashboard")

@st.cache_data
def load_data():
    # Ensure this filename matches your CSV exactly
    return pd.read_csv('maturity_mock_data.csv')

# Load the data
df = load_data()

st.title("🏭 Technology Maturity Dashboard")
st.markdown("---")

# 2. Theme Selector
themes = df['Theme'].unique()
selected_theme = st.selectbox('Select Maturity Theme', themes, index=0)

# Filter data based on selection
theme_df = df[df['Theme'] == selected_theme]

# 3. Overview Chart
st.subheader(f"Level Overview: {selected_theme}")

color_map = {'Green': '#28A745', 'Yellow': '#FFD700', 'Red': '#FF4D4D'}

# Grouping to ensure one status per company/level
overview_pivot = theme_df.groupby(['Company', 'Level'])['Status'].first().reset_index()

fig1 = px.scatter(
    overview_pivot, 
    x='Company', 
    y='Level', 
    color='Status',
    color_discrete_map=color_map,
    symbol_sequence=['square'],
    height=400,
    category_orders={
        'Level': [5, 4, 3, 2], 
        'Company': ['TMA', 'TMT', 'TMMIN', 'STM', 'ASSB', 'TMP', 'TMV', 'TMY', 'IMC']
    }
)

fig1.update_traces(marker=dict(size=35, line=dict(width=1, color='DarkSlateGrey')))
fig1.update_yaxes(tickvals=[2, 3, 4, 5], ticktext=['L2: Manual', 'L3: Digital', 'L4: Predictive', 'L5: Autonomous'])

st.plotly_chart(fig1, use_container_width=True)

# 4. Drill Down Section
st.markdown("---")
selected_level = st.radio('Select Maturity Level to see Use Cases:', [2, 3, 4, 5], horizontal=True, index=0)

level_name = df[df['Level'] == selected_level]['Level Name'].iloc[0]
st.subheader(f"Use Case Detail: Level {selected_level}")

level_df = theme_df[theme_df['Level'] == selected_level]

fig2 = px.scatter(
    level_df, 
    x='Company', 
    y='Use Case', 
    color='Status',
    color_discrete_map=color_map,
    symbol_sequence=['square'],
    height=350,
    category_orders={'Company': ['TMA', 'TMT', 'TMMIN', 'STM', 'ASSB', 'TMP', 'TMV', 'TMY', 'IMC']}
)

fig2.update_traces(marker=dict(size=25, line=dict(width=1, color='DarkSlateGrey')))
st.plotly_chart(fig2, use_container_width=True)

# 5. Detail Panel
st.markdown("---")
st.subheader("💡 Solution Details")

col1, col2 = st.columns(2)
with col1:
    target_affiliate = st.selectbox('Select Affiliate for Details:', ['TMA', 'TMT', 'TMMIN', 'STM', 'ASSB', 'TMP', 'TMV', 'TMY', 'IMC'])
with col2:
    # Filter for active use cases (Green/Yellow)
    active_df = level_df[(level_df['Company'] == target_affiliate) & (level_df['Status'].isin(['Green', 'Yellow']))]
    if not active_df.empty:
        target_use_case = st.selectbox('Select Use Case:', active_df['Use Case'].unique())
    else:
        st.warning("No active solutions for this affiliate at this level.")
        target_use_case = None

if target_use_case:
    detail = active_df[active_df['Use Case'] == target_use_case].iloc[0]
    
    # Displaying the 3 text boxes you requested
    c1, c2, c3 = st.columns(3)
    c1.metric("Solution Name", detail['Solution Name'])
    c2.write(f"**Description:** \n{detail['Solution Description']}")
    c3.write(f"**Function:** \n{detail['Function in Solution']}")
    
    if detail['Capability to implement to others'] == 'Yes':
        st.success(f"🌟 {target_affiliate} can assist other companies with this implementation.")
