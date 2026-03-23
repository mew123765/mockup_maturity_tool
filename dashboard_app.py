import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Page Configuration
st.set_page_config(layout="wide", page_title="TMA Maturity Dashboard")

# --- IMPROVED CSS FOR 1080P AND LARGER TEXT ---
st.markdown("""
    <style>
    /* 1. Force horizontal layout for radio buttons */
    [data-testid="stRadio"] div[role="radiogroup"] {
        flex-direction: row !important;
        display: flex !important;
        gap: 15px !important;
        flex-wrap: wrap !important;
    }

    /* 2. Style the Label (The Button Rectangle) with 50% larger text */
    [data-testid="stRadio"] div[role="radiogroup"] label {
        background-color: #f8f9fa !important;
        padding: 15px 30px !important;
        border-radius: 6px !important;
        border: 1px solid #dee2e6 !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        min-width: 200px !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }

    /* 3. Target the text inside the button - 50% LARGER (1.5rem) */
    [data-testid="stRadio"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
        color: #212529 !important;
        font-weight: 700 !important;
        font-size: 1.5rem !important;
        margin: 0 !important;
    }

    /* 4. HIDE ONLY THE RADIO DOT */
    [data-testid="stRadio"] div[role="radiogroup"] label > div:first-child {
        display: none !important;
    }

    /* 5. Hover and Selected States */
    [data-testid="stRadio"] div[role="radiogroup"] label:hover {
        background-color: #e9ecef !important;
        border-color: #EB0A1E !important;
    }
    [data-testid="stRadio"] div[role="radiogroup"] [aria-checked="true"] {
        background-color: #ffffff !important;
        border: 3px solid #EB0A1E !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
    }

    /* --- Solution Detail Cards (Larger Text) --- */
    .detail-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        margin-bottom: 15px;
        min-height: 140px;
    }
    .card-title {
        color: #6c757d;
        font-size: 1.1rem;
        font-weight: bold;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .card-content {
        color: #111111 !important;
        font-size: 1.4rem;
        font-weight: 500;
    }

    /* --- Yokoten Status Boxes (Larger) --- */
    .yokoten-box {
        padding: 15px;
        border-radius: 6px;
        text-align: center;
        font-weight: 800;
        font-size: 1.6rem;
        color: white !important;
        text-transform: uppercase;
        margin-top: 10px;
    }
    .yokoten-can { background-color: #28A745; border: 1px solid #1e7e34; }
    .yokoten-cant { background-color: #DC3545; border: 1px solid #bd2130; }
    </style>
    """, unsafe_allow_html=True)

# 2. Data Loader
@st.cache_data
def load_data():
    target = 'maturity_mock_data.csv'
    if not os.path.exists(target): return pd.DataFrame()
    for enc in ['utf-8', 'latin1', 'iso-8859-1']:
        try:
            df = pd.read_csv(target, encoding=enc)
            df.columns = df.columns.str.strip()
            status_map = {
                'Green': 'Have solution', 
                'Yellow': 'Solution under develop', 
                'Red': "Doesn't have solution"
            }
            df['Status'] = df['Status'].map(status_map)
            return df
        except: continue
    return pd.DataFrame()

df = load_data()

if not df.empty:
    st.title("🏭 Technology Maturity Dashboard")
    st.markdown("---")

    # 3. Theme Selector
    st.write("### 🏷️ Select Maturity Theme")
    theme_list = sorted(df['Theme'].dropna().unique().tolist())
    selected_theme = st.radio("Theme Selector", theme_list, horizontal=True, label_visibility="collapsed")
    
    theme_df = df[df['Theme'] == selected_theme]

    if not theme_df.empty:
        # 4. Overview Chart
        level_map = theme_df[['Level', 'Level Name']].drop_duplicates().sort_values('Level')
        y_vals = level_map['Level'].tolist()
        y_text = [f"L{row['Level']}: {row['Level Name']}" for _, row in level_map.iterrows()]
        
        color_map = {"Have solution": "#28A745", "Solution under develop": "#FFD700", "Doesn't have solution": "#FF4D4D"}
        st_ord = {"Doesn't have solution": 0, "Solution under develop": 1, "Have solution": 2}
        
        overview_data = theme_df.sort_values(by='Status', key=lambda x: x.map(st_ord))
        overview_data = overview_data.groupby(['Company', 'Level']).first().reset_index()

        fig1 = px.scatter(
            overview_data, x="Company", y="Level", color="Status",
            color_discrete_map=color_map, symbol_sequence=['square'],
            height=600,
            category_orders={
                "Level": sorted(y_vals, reverse=True),
                "Status": ["Have solution", "Solution under develop", "Doesn't have solution"],
                "Company": ["TMA", "TMT", "TMMIN", "STM", "ASSB", "TMP", "TMV", "TMY", "IMC"]
            }
        )
        fig1.update_traces(marker=dict(size=60, line=dict(width=2, color='DarkSlateGrey')))
        fig1.update_yaxes(tickvals=y_vals, ticktext=y_text)
        
        # 50% Larger Font Settings
        fig1.update_layout(
            font=dict(size=18),
            legend=dict(font=dict(size=18)),
            margin=dict(l=50, r=50, t=50, b=50)
        )
        st.plotly_chart(fig1, use_container_width=True)

        # 5. Level Selector
        st.markdown("---")
        st.write("### 📶 Select Level to Explore Use Cases")
        selected_level_val = st.radio(
            "Level Selector", options=y_vals, 
            format_func=lambda x: f"Level {x}",
            horizontal=True, label_visibility="collapsed"
        )

        level_df = theme_df[theme_df['Level'] == selected_level_val]

        if not level_df.empty:
            current_lname = level_map[level_map['Level'] == selected_level_val]['Level Name'].iloc[0]
            st.subheader(f"Level {selected_level_val} Detail: {current_lname}")
            
            fig2 = px.scatter(
                level_df, x="Company", y="Use Case", color="Status",
                color_discrete_map=color_map, symbol_sequence=['square'],
                height=600,
                category_orders={"Company": ["TMA", "TMT", "TMMIN", "STM", "ASSB", "TMP", "TMV", "TMY", "IMC"]}
            )
            fig2.update_traces(marker=dict(size=45, line=dict(width=1.5, color='DarkSlateGrey')))
            
            fig2.update_layout(
                font=dict(size=18),
                legend=dict(font=dict(size=18)),
                margin=dict(l=50, r=50, t=50, b=50)
            )
            st.plotly_chart(fig2, use_container_width=True)

            # 6. Solution Details & Yokoten
            st.markdown("---")
            st.subheader("💡 Solution Details")
            d_col1, d_col2 = st.columns(2)
            with d_col1:
                target_affiliate = st.selectbox("1. Select Affiliate:", sorted(level_df['Company'].unique()))
            with d_col2:
                aff_spec = level_df[level_df['Company'] == target_affiliate]
                target_use_case = st.selectbox("2. Select Use Case:", aff_spec['Use Case'].unique())

            if target_use_case:
                detail = aff_spec[aff_spec['Use Case'] == target_use_case].iloc[0]
                c1, c2, c3 = st.columns(3)
                with c1: st.markdown(f'<div class="detail-card"><div class="card-title">Solution</div><div class="card-content">{detail["Solution Name"]}</div></div>', unsafe_allow_html=True)
                with c2: st.markdown(f'<div class="detail-card"><div class="card-title">Description</div><div class="card-content">{detail["Solution Description"]}</div></div>', unsafe_allow_html=True)
                with c3: st.markdown(f'<div class="detail-card"><div class="card-title">Function</div><div class="card-content">{detail["Function in Solution"]}</div></div>', unsafe_allow_html=True)
                
                st.write("**Yokoten Capability:**")
                is_yokoten = str(detail['Capability to implement to others']).strip().lower() == 'yes'
                if is_yokoten:
                    st.markdown('<div class="yokoten-box yokoten-can">Can Yokoten</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="yokoten-box yokoten-cant">Cann\'t Yokoten</div>', unsafe_allow_html=True)
