import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Setup & Styling
st.set_page_config(layout="wide", page_title="TMA Maturity Dashboard")

# Custom CSS for Button Selectors
st.markdown("""
    <style>
    div.row-widget.stRadio > div{
        flex-direction:row;
        display: flex;
        gap: 10px;
    }
    div.row-widget.stRadio label {
        background-color: #f0f2f6;
        padding: 8px 16px;
        border-radius: 5px;
        border: 1px solid #d1d5db;
        cursor: pointer;
    }
    div.row-widget.stRadio input {
        display: none;
    }
    .info-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-left: 5px solid #EB0A1E;
        border-radius: 5px;
        height: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    filename = 'maturity_mock_data.csv' # CHANGE THIS if your file is named differently
    
    # Debugging: Show files in the current directory if it fails
    if not os.path.exists(filename):
        st.error(f"❌ File '{filename}' not found.")
        st.write("Files actually found in your GitHub folder:")
        st.write(os.listdir(".")) 
        return pd.DataFrame()
    
    return pd.read_csv(filename)

df = load_data()

if not df.empty:
    st.title("🏭 Technology Maturity Dashboard")
    st.markdown("---")

    # 2. Theme Selector (Buttons)
    st.write("### 🏷️ Select Maturity Theme")
    theme_list = sorted(list(df['Theme'].unique()))
    selected_theme = st.radio("Theme Selector", theme_list, label_visibility="collapsed")
    
    # FILTER DATA BY THEME
    theme_df = df[df['Theme'] == selected_theme]

    if not theme_df.empty:
        # 3. DYNAMIC Y-AXIS LOGIC (Inside Theme Selection)
        # We get the names ONLY for the selected theme
        level_map = theme_df[['Level', 'Level Name']].drop_duplicates().sort_values('Level')
        y_vals = level_map['Level'].tolist()
        y_text = level_map['Level Name'].tolist()

        st.subheader(f"Maturity Overview: {selected_theme}")

        color_map = {"Green": "#28A745", "Yellow": "#FFD700", "Red": "#FF4D4D"}
        overview_pivot = theme_df.groupby(['Company', 'Level'])['Status'].first().reset_index()

        fig1 = px.scatter(
            overview_pivot, x="Company", y="Level", color="Status",
            color_discrete_map=color_map, symbol_sequence=['square'],
            height=450,
            category_orders={
                "Level": sorted(y_vals, reverse=True), # Highest level at top
                "Company": ["TMA", "TMT", "TMMIN", "STM", "ASSB", "TMP", "TMV", "TMY", "IMC"]
            }
        )
        
        # APPLY DYNAMIC THEME-BASED LABELS
        fig1.update_traces(marker=dict(size=35, line=dict(width=1, color='DarkSlateGrey')))
        fig1.update_yaxes(tickvals=y_vals, ticktext=y_text, gridcolor='LightGray')
        fig1.update_xaxes(gridcolor='LightGray')
        st.plotly_chart(fig1, use_container_width=True)

        # 4. Level Selector (Buttons)
        st.markdown("---")
        st.write("### 📶 Select Maturity Level to Explore Use Cases")
        
        # Create labels for the buttons like "L5: Autonomous..."
        button_labels = {row['Level']: f"L{row['Level']}: {row['Level Name']}" for _, row in level_map.iterrows()}
        
        # The radio shows the label but returns the Level number (int)
        selected_level_val = st.radio(
            "Level Selector", 
            options=y_vals, 
            format_func=lambda x: button_labels.get(x),
            horizontal=True, 
            label_visibility="collapsed"
        )

        level_df = theme_df[theme_df['Level'] == int(selected_level_val)]

        if not level_df.empty:
            st.subheader(f"Use Case Detail: {button_labels[selected_level_val]}")
            
            fig2 = px.scatter(
                level_df, x="Company", y="Use Case", color="Status",
                color_discrete_map=color_map, symbol_sequence=['square'],
                height=350,
                category_orders={"Company": ["TMA", "TMT", "TMMIN", "STM", "ASSB", "TMP", "TMV", "TMY", "IMC"]}
            )
            fig2.update_traces(marker=dict(size=25, line=dict(width=1, color='DarkSlateGrey')))
            st.plotly_chart(fig2, use_container_width=True)

            # 5. Details Section (Dropdowns)
            st.markdown("---")
            st.subheader("💡 Solution Details")
            col1, col2 = st.columns(2)

            with col1:
                target_affiliate = st.selectbox("Select Affiliate:", ["TMA", "TMT", "TMMIN", "STM", "ASSB", "TMP", "TMV", "TMY", "IMC"])

            with col2:
                active_df = level_df[(level_df['Company'] == target_affiliate) & (level_df['Status'].isin(['Green', 'Yellow']))]
                if not active_df.empty:
                    target_use_case = st.selectbox("Select Use Case (Active/Developing):", active_df['Use Case'].unique())
                else:
                    st.warning(f"No active solutions for {target_affiliate} at this level.")
                    target_use_case = None

            if target_use_case:
                detail = active_df[active_df['Use Case'] == target_use_case].iloc[0]
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f'<div class="info-box"><b>Solution Name</b><br>{detail["Solution Name"]}</div>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f'<div class="info-box"><b>Description</b><br>{detail["Solution Description"]}</div>', unsafe_allow_html=True)
                with c3:
                    st.markdown(f'<div class="info-box"><b>Function</b><br>{detail["Function in Solution"]}</div>', unsafe_allow_html=True)
                
                if detail['Capability to implement to others'] == 'Yes':
                    st.success(f"🌟 **{target_affiliate}** is a Center of Excellence for this specific solution.")
