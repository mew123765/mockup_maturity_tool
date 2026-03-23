import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Page Configuration
st.set_page_config(layout="wide", page_title="TMA Maturity Dashboard")

# Custom CSS for "Button" style selectors
st.markdown("""
    <style>
    div.row-widget.stRadio > div {
        flex-direction: row;
        display: flex;
        gap: 10px;
    }
    div.row-widget.stRadio label {
        background-color: #f0f2f6;
        padding: 8px 16px;
        border-radius: 5px;
        border: 1px solid #d1d5db;
        cursor: pointer;
        transition: 0.2s;
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

# 2. Robust Data Loader with Encoding Support
@st.cache_data
def load_data():
    target_file = 'maturity_mock_data.csv'
    
    # Check if the file exists first
    if not os.path.exists(target_file):
        all_files = os.listdir(".")
        csv_files = [f for f in all_files if f.endswith('.csv')]
        if csv_files:
            target_file = csv_files[0]
        else:
            st.error("No CSV files found in GitHub.")
            return pd.DataFrame()

    # Try different encodings to solve UnicodeDecodeError
    encodings = ['utf-8', 'latin1', 'iso-8859-1', 'utf-16']
    for enc in encodings:
        try:
            return pd.read_csv(target_file, encoding=enc)
        except UnicodeDecodeError:
            continue
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return pd.DataFrame()
    
    st.error("Could not decode the CSV file. Please save it as 'CSV UTF-8 (Comma delimited)' in Excel.")
    return pd.DataFrame()

df = load_data()

if not df.empty:
    # Clean up column names (remove hidden spaces)
    df.columns = df.columns.str.strip()
    
    st.title("🏭 Technology Maturity Dashboard")
    st.markdown("---")

    # 3. Theme Selector (Buttons)
    st.write("### 🏷️ Select Maturity Theme")
    theme_list = sorted(df['Theme'].dropna().unique().tolist())
    selected_theme = st.radio("Theme Selector", theme_list, label_visibility="collapsed")
    
    # Filter by theme
    theme_df = df[df['Theme'] == selected_theme]

    if not theme_df.empty:
        # 4. Dynamic Y-Axis Mapping (Specific to Selected Theme)
        level_map = theme_df[['Level', 'Level Name']].drop_duplicates().sort_values('Level')
        y_vals = level_map['Level'].tolist()
        y_text = level_map['Level Name'].tolist()

        st.subheader(f"Maturity Overview: {selected_theme}")

        color_map = {"Green": "#28A745", "Yellow": "#FFD700", "Red": "#FF4D4D"}
        
        # Plotting the main chart
        fig1 = px.scatter(
            theme_df, 
            x="Company", 
            y="Level", 
            color="Status",
            color_discrete_map=color_map, 
            symbol_sequence=['square'],
            height=450,
            category_orders={
                "Level": sorted(y_vals, reverse=True),
                "Company": ["TMA", "TMT", "TMMIN", "STM", "ASSB", "TMP", "TMV", "TMY", "IMC"]
            }
        )
        
        # Apply the Dynamic Labels
        fig1.update_traces(marker=dict(size=35, line=dict(width=1, color='DarkSlateGrey')))
        fig1.update_yaxes(tickvals=y_vals, ticktext=y_text, gridcolor='LightGray')
        fig1.update_xaxes(gridcolor='LightGray')
        
        st.plotly_chart(fig1, use_container_width=True)

        # 5. Level Selector (Buttons)
        st.markdown("---")
        st.write("### 📶 Select Maturity Level to Explore Use Cases")
        
        button_labels = {row['Level']: f"L{row['Level']}: {row['Level Name']}" for _, row in level_map.iterrows()}
        
        selected_level_val = st.radio(
            "Level Selector", 
            options=y_vals, 
            format_func=lambda x: button_labels.get(x, f"Level {x}"),
            horizontal=True, 
            label_visibility="collapsed"
        )

        level_df = theme_df[theme_df['Level'] == selected_level_val]

        if not level_df.empty:
            st.subheader(f"Use Case Detail: {button_labels.get(selected_level_val, selected_level_val)}")
            
            fig2 = px.scatter(
                level_df, x="Company", y="Use Case", color="Status",
                color_discrete_map=color_map, symbol_sequence=['square'],
                height=350,
                category_orders={"Company": ["TMA", "TMT", "TMMIN", "STM", "ASSB", "TMP", "TMV", "TMY", "IMC"]}
            )
            fig2.update_traces(marker=dict(size=25, line=dict(width=1, color='DarkSlateGrey')))
            st.plotly_chart(fig2, use_container_width=True)

            # 6. Details Section (Dropdowns)
            st.markdown("---")
            st.subheader("💡 Solution Details")
            col1, col2 = st.columns(2)

            with col1:
                # Get only companies available in this filtered level
                available_cos = sorted(level_df['Company'].unique().tolist())
                target_affiliate = st.selectbox("Select Affiliate:", available_cos)

            with col2:
                active_df = level_df[(level_df['Company'] == target_affiliate) & (level_df['Status'].isin(['Green', 'Yellow']))]
                if not active_df.empty:
                    target_use_case = st.selectbox("Select Use Case:", active_df['Use Case'].unique())
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
                    st.success(f"🌟 **{target_affiliate}** is a Center of Excellence for this solution.")
