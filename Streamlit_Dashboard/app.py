import base64
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Customer Churn Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# 2. COLOR PALETTE
# =========================================================
GREEN = "#4F7D32"
YELLOW = "#FFD16A"
ORANGE = "#F5B52E"
RED = "#D9361E"

BG = "#111510"
PANEL = "#1B2118"
CARD = "#252D20"
TEXT = "#F5F5F5"
MUTED = "#B9C1B3"

CHART_HEIGHT = 200

# Set to True to drop the top 1% Monthly_Spend values from the whole dashboard
REMOVE_SPEND_OUTLIERS = False

COLOR_MAP = {
    "Retained": YELLOW,
    "Churned": RED,
    "Active": GREEN,
    "At Risk": ORANGE,
    "Inactive": RED,
}

CHART_COLORS = [GREEN, YELLOW, ORANGE, RED]

# =========================================================
# 3. DASHBOARD STYLE
# =========================================================
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {BG};
        color: {TEXT};
    }}

    [data-testid="stHeader"] {{
        background-color: {BG};
        height: 2.8rem;
    }}

    [data-testid="stSidebar"] {{
        background-color: {PANEL};
        min-width: 245px;
    }}

    [data-testid="stSidebar"] * {{
        color: {TEXT};
    }}

    /* Sidebar logo (circular) */
    .sidebar-logo {{
        display: flex;
        justify-content: center;
        margin: 0.2rem 0 0.6rem 0;
    }}

    .sidebar-logo img {{
        width: 110px;
        height: 110px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid {GREEN};
        box-shadow: 0 0 12px rgba(79, 125, 50, 0.45);
    }}

    /* Reduce page spacing (leave room for the Streamlit header) */
    .block-container {{
        padding-top: 3.5rem !important;
        padding-bottom: 0.6rem !important;
        padding-left: 1.1rem !important;
        padding-right: 1.1rem !important;
        gap: 0.3rem !important;
    }}

    /* Make dashboard title visible */
    h1 {{
        color: {YELLOW} !important;
        font-size: 1.9rem !important;
        font-weight: 800 !important;
        margin-top: 0 !important;
        margin-bottom: 0.7rem !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        line-height: 1.5 !important;
        overflow: visible !important;
        visibility: visible !important;
        opacity: 1 !important;
    }}

    h2, h3 {{
        color: {TEXT} !important;
        font-size: 1rem !important;
        margin-top: 0.35rem !important;
        margin-bottom: 0.45rem !important;
        padding-bottom: 0 !important;
        line-height: 1.35 !important;
    }}

    p, label {{
        color: {MUTED};
    }}

    /* KPI cards */
    [data-testid="stMetric"] {{
        background-color: {CARD};
        border: 1px solid {GREEN};
        border-left: 4px solid {GREEN};
        border-radius: 8px;
        padding: 7px 10px !important;
        margin-bottom: 0 !important;
    }}

    [data-testid="stMetricLabel"] {{
        color: {MUTED} !important;
        font-size: 0.78rem !important;
    }}

    [data-testid="stMetricValue"] {{
        color: {YELLOW} !important;
        font-size: 1.35rem !important;
    }}

    [data-testid="stMetricDelta"] {{
        color: {TEXT} !important;
    }}

    /* Reduce vertical spacing between elements */
    [data-testid="stVerticalBlock"] {{
        gap: 0.4rem !important;
    }}

    [data-testid="stHorizontalBlock"] {{
        gap: 0.7rem !important;
    }}

    /* Tabs */
    [data-testid="stTabs"] {{
        margin-top: -0.2rem !important;
    }}

    [data-testid="stTabs"] button {{
        font-size: 0.82rem;
    }}

    /* Charts */
    [data-testid="stPlotlyChart"] {{
        margin-top: 0.1rem !important;
        margin-bottom: 0.15rem !important;
    }}

    div[data-baseweb="select"] > div {{
        background-color: {CARD};
        border-color: {GREEN};
    }}

    div[data-baseweb="slider"] {{
        padding-top: 0.2rem;
    }}

    hr {{
        margin-top: 0.2rem !important;
        margin-bottom: 0.2rem !important;
        border-color: #394333;
    }}

    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# 4. LOAD AND PREPARE DATA
# =========================================================
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_customer_churn.csv")

    text_columns = [
        "Region",
        "Subscription_Plan",
        "Gender",
        "Payment_Method",
    ]

    for col in text_columns:
        df[col] = df[col].astype("string").str.strip()

    for col in ["Region", "Subscription_Plan", "Gender"]:
        df[col] = df[col].str.title()

    df["Payment_Method"] = df["Payment_Method"].str.title()

    # Remove invalid ages (negative values / unrealistic outliers like 150).
    # Adjust the limits to match your data.
    df = df[df["Age"].between(10, 100)].copy()

    # Optional: remove extreme spend outliers (top 1%) and negative values.
    # Keep False if the large values are real customers, not errors.
    if REMOVE_SPEND_OUTLIERS:
        spend_cap = df["Monthly_Spend"].quantile(0.99)
        df = df[df["Monthly_Spend"].between(0, spend_cap)].copy()

    df["Login_Activity"] = pd.cut(
        df["Days_Since_Last_Login"],
        bins=[-1, 30, 90, float("inf")],
        labels=["Active", "At Risk", "Inactive"],
    )

    df["Days_Bucket"] = pd.cut(
        df["Days_Since_Last_Login"],
        bins=[-1, 30, 60, 90, 120, 150, float("inf")],
        labels=[
            "0-30",
            "31-60",
            "61-90",
            "91-120",
            "121-150",
            "151+",
        ],
    )

    return df


df_raw = load_data()

# =========================================================
# 5. SIDEBAR FILTERS
# =========================================================
logo_path = Path(__file__).parent / "logo_round.png"

if logo_path.exists():
    logo_b64 = base64.b64encode(logo_path.read_bytes()).decode()
    st.sidebar.markdown(
        f"<div class='sidebar-logo'>"
        f"<img src='data:image/png;base64,{logo_b64}' alt='Logo'>"
        f"</div>",
        unsafe_allow_html=True,
    )

st.sidebar.title("Filters")
st.sidebar.caption("Filter the customers shown in the dashboard.")

regions_available = sorted(df_raw["Region"].dropna().unique())
plans_available = sorted(df_raw["Subscription_Plan"].dropna().unique())
genders_available = sorted(df_raw["Gender"].dropna().unique())
payments_available = sorted(df_raw["Payment_Method"].dropna().unique())

regions = st.sidebar.multiselect(
    "Region",
    options=regions_available,
    default=regions_available,
)

plans = st.sidebar.multiselect(
    "Subscription Plan",
    options=plans_available,
    default=plans_available,
)

genders = st.sidebar.multiselect(
    "Gender",
    options=genders_available,
    default=genders_available,
)

payment_methods = st.sidebar.multiselect(
    "Payment Method",
    options=payments_available,
    default=payments_available,
)

age_min = int(df_raw["Age"].min())
age_max = int(df_raw["Age"].max())

age_range = st.sidebar.slider(
    "Age Range",
    min_value=age_min,
    max_value=age_max,
    value=(age_min, age_max),
)

churn_filter = st.sidebar.radio(
    "Customer Status",
    ["All", "Churned Only", "Retained Only"],
    index=0,
)

if st.sidebar.button("Reset Filters", use_container_width=True):
    st.rerun()

st.sidebar.divider()
st.sidebar.caption("Source: cleaned_customer_churn.csv")

# =========================================================
# 6. APPLY FILTERS
# =========================================================
df = df_raw[
    df_raw["Region"].isin(regions)
    & df_raw["Subscription_Plan"].isin(plans)
    & df_raw["Gender"].isin(genders)
    & df_raw["Payment_Method"].isin(payment_methods)
    & df_raw["Age"].between(age_range[0], age_range[1])
].copy()

if churn_filter == "Churned Only":
    df = df[df["Churn"] == 1]
elif churn_filter == "Retained Only":
    df = df[df["Churn"] == 0]

if df.empty:
    st.title("📊 Customer Churn Analytics Dashboard")

    st.warning(
        "No customers match the selected filters. "
        "Please change your selections."
    )
    st.stop()

# =========================================================
# 7. CHART HELPER
# =========================================================
def style_chart(fig, height=CHART_HEIGHT, showlegend=False):
    fig.update_layout(
        height=height,
        template="plotly_dark",
        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,
        font=dict(
            family="Arial",
            size=10,
            color=TEXT,
        ),
        margin=dict(l=8, r=8, t=12, b=30),
        showlegend=showlegend,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=9),
        ),
        colorway=CHART_COLORS,
    )

    fig.update_xaxes(
        title_font=dict(size=10),
        tickfont=dict(size=9),
        gridcolor="#394333",
        zerolinecolor="#394333",
        automargin=True,
    )

    fig.update_yaxes(
        title_font=dict(size=10),
        tickfont=dict(size=9),
        gridcolor="#394333",
        zerolinecolor="#394333",
        automargin=True,
    )

    return fig


def show_chart(fig):
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "responsive": True,
        },
    )


# =========================================================
# 8. HEADER AND KPI CARDS
# =========================================================
st.title("📊 Customer Churn Analytics Dashboard")

churn_rate = df["Churn"].mean() * 100

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("Total Customers", f"{len(df):,}")
k2.metric("Churn Rate", f"{churn_rate:.1f}%")
k3.metric("Avg Monthly Spend", f"{df['Monthly_Spend'].mean():,.1f}")
k4.metric(
    "Avg Service Calls",
    f"{df['Customer_Service_Calls'].mean():.1f}",
)
k5.metric("Avg Customer Age", f"{df['Age'].mean():.1f}")

# Smaller gap between KPIs and charts
st.markdown(
    "<div style='height: 10px;'></div>",
    unsafe_allow_html=True,
)


# =========================================================
# 9. TABS
# =========================================================
tab_overview, tab_drivers, tab_corr, tab_bivariate, tab_data = st.tabs(
    [
        "📈 Overview",
        "🎯 Churn Drivers",
        "📊 Correlation",
        "🔬 Bivariate Analysis",
        "📋 Data",
    ]
)

# =========================================================
# TAB 1: OVERVIEW
# =========================================================
with tab_overview:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Retained vs Churned")

        counts = df["Churn"].value_counts().reindex(
            [0, 1], fill_value=0
        )

        fig = px.pie(
            names=["Retained", "Churned"],
            values=counts.values,
            color=["Retained", "Churned"],
            color_discrete_map=COLOR_MAP,
            hole=0.58,
        )

        fig.update_traces(
            textinfo="percent+label",
            textfont_size=10,
            marker=dict(line=dict(color=PANEL, width=2)),
        )

        style_chart(fig)
        show_chart(fig)

    with c2:
        st.subheader("Payment Method Distribution")

        payment_counts = df["Payment_Method"].value_counts()

        fig = px.pie(
            names=payment_counts.index,
            values=payment_counts.values,
            color_discrete_sequence=CHART_COLORS,
            hole=0.58,
        )

        fig.update_traces(
            textinfo="percent+label",
            textfont_size=9,
            marker=dict(line=dict(color=PANEL, width=2)),
        )

        style_chart(fig)
        show_chart(fig)

    c3, c4 = st.columns(2)

    with c3:
        st.subheader("Age Distribution by Churn")

        age_df = df.assign(
            Churn_Status=df["Churn"].map({
                0: "Retained",
                1: "Churned",
            })
        )

        fig = px.histogram(
            age_df,
            x="Age",
            color="Churn_Status",
            barmode="overlay",
            nbins=20,
            opacity=0.8,
            color_discrete_map=COLOR_MAP,
        )

        fig.update_layout(legend_title_text="")

        style_chart(fig, showlegend=True)
        show_chart(fig)

    with c4:
        st.subheader("Customers by Gender")

        gender_counts = (
            df["Gender"]
            .value_counts()
            .rename_axis("Gender")
            .reset_index(name="Customers")
        )

        fig = px.bar(
            gender_counts,
            x="Gender",
            y="Customers",
            text="Customers",
            color_discrete_sequence=[GREEN],
        )

        fig.update_traces(
            textposition="outside",
            textfont_size=9,
            cliponaxis=False,
        )

        style_chart(fig)
        show_chart(fig)


# =========================================================
# TAB 2: CHURN DRIVERS
# =========================================================
with tab_drivers:
    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader("Churn by Login Activity")

        activity = (
            df.groupby("Login_Activity", observed=True)["Churn"]
            .mean()
            .mul(100)
            .reset_index(name="Churn Rate")
            .sort_values("Churn Rate", ascending=False)
        )

        fig = px.bar(
            activity,
            x="Login_Activity",
            y="Churn Rate",
            text="Churn Rate",
            color_discrete_sequence=[GREEN],
        )

        fig.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside",
            cliponaxis=False,
        )

        style_chart(fig)
        show_chart(fig)

    with c2:
        st.subheader("Churn by Days Since Login")

        days_churn = (
            df.groupby("Days_Bucket", observed=True)["Churn"]
            .mean()
            .mul(100)
            .reset_index(name="Churn Rate")
        )

        fig = px.line(
            days_churn,
            x="Days_Bucket",
            y="Churn Rate",
            markers=True,
        )

        fig.update_traces(
            line_color=RED,
            marker_color=ORANGE,
            line_width=2,
            marker_size=6,
        )

        style_chart(fig)
        show_chart(fig)

    with c3:
        st.subheader("Churn by Subscription Plan")

        plan_churn = (
            df.groupby("Subscription_Plan")["Churn"]
            .mean()
            .mul(100)
            .reset_index(name="Churn Rate")
        )

        fig = px.bar(
            plan_churn,
            x="Subscription_Plan",
            y="Churn Rate",
            text="Churn Rate",
            color_discrete_sequence=[ORANGE],
        )

        fig.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside",
            cliponaxis=False,
        )

        style_chart(fig)
        show_chart(fig)

    c4, c5, c6 = st.columns(3)

    with c4:
        st.subheader("Churn by Region")

        region_churn = (
            df.groupby("Region")["Churn"]
            .mean()
            .mul(100)
            .reset_index(name="Churn Rate")
        )

        fig = px.bar(
            region_churn,
            x="Region",
            y="Churn Rate",
            text="Churn Rate",
            color_discrete_sequence=[GREEN],
        )

        fig.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside",
            cliponaxis=False,
        )

        style_chart(fig)
        show_chart(fig)

    with c5:
        st.subheader("Avg Service Calls by Status")

        calls = (
            df.groupby("Churn")["Customer_Service_Calls"]
            .mean()
            .reindex([0, 1])
        )

        calls_df = pd.DataFrame({
            "Status": ["Retained", "Churned"],
            "Avg Service Calls": calls.values,
        })

        fig = px.bar(
            calls_df,
            x="Status",
            y="Avg Service Calls",
            color="Status",
            color_discrete_map=COLOR_MAP,
            text="Avg Service Calls",
        )

        fig.update_traces(
            texttemplate="%{text:.1f}",
            textposition="outside",
            cliponaxis=False,
        )

        style_chart(fig)
        show_chart(fig)

    with c6:
        st.subheader("Avg Monthly Spend by Status")

        spend = (
            df.groupby("Churn")["Monthly_Spend"]
            .mean()
            .reindex([0, 1])
        )

        spend_df = pd.DataFrame({
            "Status": ["Retained", "Churned"],
            "Avg Monthly Spend": spend.values,
        })

        fig = px.bar(
            spend_df,
            x="Status",
            y="Avg Monthly Spend",
            color="Status",
            color_discrete_map=COLOR_MAP,
            text="Avg Monthly Spend",
        )

        fig.update_traces(
            texttemplate="%{text:,.1f}",
            textposition="outside",
            cliponaxis=False,
        )

        style_chart(fig)
        show_chart(fig)


# =========================================================
# TAB 3: CORRELATION MATRIX
# =========================================================
with tab_corr:
    st.subheader("Correlation Matrix")

    numeric_cols = [
        "Age",
        "Days_Since_Last_Login",
        "Customer_Service_Calls",
        "Monthly_Spend",
        "Churn",
    ]

    corr = df[numeric_cols].corr().round(2)

    fig = px.imshow(
        corr,
        text_auto=".2f",
        color_continuous_scale=[
            GREEN,
            "#252D20",
            YELLOW,
            ORANGE,
            RED,
        ],
        zmin=-1,
        zmax=1,
        aspect="auto",
    )

    style_chart(fig, height=350)
    show_chart(fig)

    st.caption(
        "Values range from -1 to +1. "
        "Correlation indicates association, not causation."
    )


# =========================================================
# TAB 4: BIVARIATE ANALYSIS
# =========================================================
with tab_bivariate:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Monthly Spend by Subscription Plan")

        # Cap the y-axis so extreme outliers don't squash the boxes
        y_cap = df["Monthly_Spend"].quantile(0.99)

        fig = px.box(
            df,
            x="Subscription_Plan",
            y="Monthly_Spend",
            color="Subscription_Plan",
            color_discrete_sequence=CHART_COLORS,
            points=False,
        )

        fig.update_layout(showlegend=False)
        fig.update_yaxes(range=[0, y_cap * 1.1])

        style_chart(fig, height=260)
        show_chart(fig)

    with c2:
        st.subheader("Churn by Region and Plan")

        region_plan_churn = (
            df.groupby(
                ["Region", "Subscription_Plan"]
            )["Churn"]
            .mean()
            .mul(100)
            .unstack()
        )

        fig = px.imshow(
            region_plan_churn,
            text_auto=".1f",
            color_continuous_scale=[
                "#252D20",
                GREEN,
                YELLOW,
                ORANGE,
                RED,
            ],
            aspect="auto",
            labels={"color": "Churn Rate (%)"},
        )

        style_chart(fig, height=260)
        show_chart(fig)


# =========================================================
# TAB 5: FILTERED DATA
# =========================================================
with tab_data:
    st.subheader("Filtered Customer Data")

    st.caption(f"{len(df):,} rows displayed")

    st.dataframe(
        df,
        use_container_width=True,
        height=350,
        hide_index=True,
    )

    st.download_button(
        label="⬇️ Download Filtered Data as CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="filtered_churn_data.csv",
        mime="text/csv",
    )


# =========================================================
# FOOTER
# =========================================================
st.markdown(
    "<div style='height: 2px;'></div>",
    unsafe_allow_html=True,
)

st.caption(
    "E-Commerce Customer Churn Analysis | "
    "Python • Pandas • Plotly • Streamlit"
)
