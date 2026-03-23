import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Setup & Styling
st.set_page_config(layout="wide", page_title="TMA Maturity Dashboard")

# Custom CSS to turn radio buttons into a "Button Group"
st.markdown("""
    <style>
    /* Styling for the horizontal radio buttons to look like a button group */
    div.row-widget.stRadio > div{
        flex-direction:row;
        display: flex;
        gap: 10px;
    }
    div.row-widget.stRadio label {
        background-color: #f0f2f6;
        padding: 10px 20px;
        border-radius: 5px;
        border: 1px solid #d1d5db;
        cursor: pointer;
        transition: 0.3s;
    }
    div.row-widget.stRadio label:hover {
        background-color: #e2e8f0;
    }
    /* Style for the 'selected' button */
    div[data-testid="stMarkdownContainer"] p {
        font-weight: 600;
    }
    /* Hide the actual radio circle */
    div.row-widget.stRadio div[data-testid="stMarkdownContainer"] {
        margin-left: 0px;
    }
    div.row-widget.stRadio input {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    return pd.read_csv('maturity_mock_data.csv')

df = load_data()

st.title("🏭 Technology Maturity Dashboard")

# 2. Theme Selector (NOW BUTTONS)
st.write("### 🏷️ Select Maturity Theme")
themes = ["Quality", "Maintenance", "Digital Workplace", "Demand & Supply", "Smart Process Equipment Preparation"]
selected_theme = st.radio("Theme Selector", themes, label_visibility="collapsed")

theme_df = df[df['Theme'] == selected_theme]

# 3. Main Overview Chart
st.markdown("---")
st.subheader(f"Maturity Overview: {selected_theme}")

color_map = {"Green": "#28A745", "Yellow": "#FFD700", "Red": "#FF4D4D"}
overview_pivot = theme_df.groupby(['Company', 'Level'])['Status'].first().reset_index()

fig1 = px.scatter(
    overview_pivot, x="Company", y="Level", color="Status",
    color_discrete_map=color_map, symbol_sequence=['square'],
    height=400,
    category_orders={"Level": [5, 4, 3, 2], "Company": ["TMA", "TMT", "TMMIN", "STM", "ASSB", "TMP", "TMV", "TMY", "IMC"]}
)
