import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ──────────────────────────────────────────────────────────────────────────────
# Page config
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FreightFox · Shipment Analytics",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# Theme system
# ──────────────────────────────────────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

THEMES = {
    "dark": {
        "bg": "#0a0a0a",
        "bg_secondary": "#111111",
        "bg_card": "#161616",
        "bg_card_border": "rgba(201, 168, 76, 0.25)",
        "bg_card_border_hover": "rgba(201, 168, 76, 0.50)",
        "bg_sidebar": "#0e0e0e",
        "text_primary": "#f5f5f0",
        "text_secondary": "#b8b8a8",
        "text_muted": "#7a7a6c",
        "text_heading": "#f5f5f0",
        "accent": "#c9a84c",
        "accent_secondary": "#d4b85c",
        "accent_dim": "rgba(201, 168, 76, 0.15)",
        "plotly_template": "plotly_dark",
        "plotly_paper": "rgba(0,0,0,0)",
        "plotly_plot": "rgba(0,0,0,0)",
        "plotly_font_color": "#e0e0d8",
        "plotly_grid": "rgba(255, 255, 255, 0.04)",
        "plotly_legend_bg": "rgba(22,22,22,0.9)",
    },
    "light": {
        "bg": "#f5f3ee",
        "bg_secondary": "#edeae3",
        "bg_card": "#ffffff",
        "bg_card_border": "rgba(160, 130, 50, 0.20)",
        "bg_card_border_hover": "rgba(160, 130, 50, 0.45)",
        "bg_sidebar": "#edeae3",
        "text_primary": "#1a1a18",
        "text_secondary": "#4a4a40",
        "text_muted": "#8a8a7a",
        "text_heading": "#1a1a18",
        "accent": "#a08232",
        "accent_secondary": "#b89a42",
        "accent_dim": "rgba(160, 130, 50, 0.10)",
        "plotly_template": "plotly_white",
        "plotly_paper": "rgba(0,0,0,0)",
        "plotly_plot": "rgba(0,0,0,0)",
        "plotly_font_color": "#2a2a28",
        "plotly_grid": "rgba(0, 0, 0, 0.06)",
        "plotly_legend_bg": "rgba(255,255,255,0.95)",
    },
}

T = THEMES[st.session_state.theme]

# Warm color palette for charts (matching reference)
CHART_COLORS = ["#c9a84c", "#8b7355", "#5c6b5c", "#a0522d", "#b8860b", "#6b8e6b", "#cd853f", "#daa520"]
STATUS_COLORS = {
    "Delivered": "#5c6b5c",
    "Delayed": "#a0522d",
    "In-Transit": "#c9a84c",
    "Cancelled": "#8b7355",
}
REGION_COLORS = {
    "Central": "#c9a84c",
    "North": "#5c6b5c",
    "East": "#a0522d",
    "South": "#8b7355",
    "West": "#b8860b",
}

# ──────────────────────────────────────────────────────────────────────────────
# CSS
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: {T['text_primary']} !important;
    }}

    .stApp {{
        background: {T['bg']} !important;
    }}

    /* ── Sidebar ─────────────────────────────────────────────────────────── */
    section[data-testid="stSidebar"] {{
        background: {T['bg_sidebar']} !important;
        border-right: 1px solid rgba(255,255,255,0.06) !important;
    }}
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {{
        color: {T['text_primary']} !important;
    }}
    section[data-testid="stSidebar"] label {{
        color: {T['text_primary']} !important;
        font-weight: 700 !important;
        font-size: 0.88rem !important;
    }}
    section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {{
        background-color: rgba(201, 168, 76, 0.20) !important;
        border: 1px solid rgba(201, 168, 76, 0.45) !important;
        color: {T['text_primary']} !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        border-radius: 6px !important;
    }}
    section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] span {{
        color: {T['text_primary']} !important;
    }}

    /* Force dark background on multiselect/select inputs */
    section[data-testid="stSidebar"] [data-baseweb="input"],
    section[data-testid="stSidebar"] [data-baseweb="select"] > div {{
        background-color: {T['bg_card']} !important;
        border-color: rgba(201, 168, 76, 0.18) !important;
        color: {T['text_primary']} !important;
    }}
    section[data-testid="stSidebar"] [data-baseweb="popover"] li {{
        color: {T['text_primary']} !important;
    }}
    section[data-testid="stSidebar"] input {{
        color: {T['text_primary']} !important;
    }}
    section[data-testid="stSidebar"] .stDateInput input {{
        background-color: {T['bg_card']} !important;
        color: {T['text_primary']} !important;
        border-color: rgba(201, 168, 76, 0.18) !important;
    }}

    /* Sidebar nav items */
    .sidebar-nav {{
        display: flex;
        flex-direction: column;
        gap: 2px;
        margin: 12px 0;
    }}
    .sidebar-nav-item {{
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 12px;
        border-radius: 8px;
        font-size: 0.88rem;
        font-weight: 500;
        color: {T['text_secondary']};
        transition: background 0.2s;
    }}
    .sidebar-nav-item:hover {{
        background: rgba(255,255,255,0.04);
    }}
    .sidebar-nav-icon {{
        font-size: 1rem;
        width: 20px;
        text-align: center;
    }}

    /* ── KPI Cards ────────────────────────────────────────────────────────── */
    .kpi-card {{
        background: {T['bg_card']};
        border: 1px solid {T['bg_card_border']};
        border-radius: 14px;
        padding: 22px 18px;
        text-align: center;
        transition: all 0.3s ease;
    }}
    .kpi-card:hover {{
        border-color: {T['bg_card_border_hover']};
        box-shadow: 0 4px 20px rgba(201, 168, 76, 0.08);
    }}
    .kpi-label {{
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: {T['accent']};
        margin-bottom: 8px;
    }}
    .kpi-value {{
        font-size: 2.2rem;
        font-weight: 800;
        color: {T['text_primary']};
        line-height: 1.1;
        margin: 4px 0;
    }}
    .kpi-delta {{
        font-size: 0.78rem;
        margin-top: 6px;
        font-weight: 500;
    }}
    .kpi-delta.good {{ color: #5c6b5c; }}
    .kpi-delta.bad {{ color: #c9534a; }}
    .kpi-delta.neutral {{ color: {T['text_muted']}; }}

    /* ── Section Headers ──────────────────────────────────────────────────── */
    .section-header {{
        font-size: 1.05rem;
        font-weight: 700;
        color: {T['text_heading']};
        margin: 24px 0 12px 0;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }}

    /* ── Insight Box ──────────────────────────────────────────────────────── */
    .insight-box {{
        background: {T['accent_dim']};
        border-left: 3px solid {T['accent']};
        border-radius: 0 10px 10px 0;
        padding: 16px 20px;
        margin: 12px 0;
        font-size: 0.92rem;
        line-height: 1.65;
        color: {T['text_secondary']};
    }}
    .insight-box strong {{
        color: {T['accent']};
    }}

    /* ── Data quality badges ──────────────────────────────────────────────── */
    .dq-issue {{
        background: rgba(200, 80, 70, 0.06);
        border: 1px solid rgba(200, 80, 70, 0.20);
        border-radius: 10px;
        padding: 14px 18px;
        margin: 8px 0;
        color: {T['text_secondary']};
    }}
    .dq-issue strong {{ color: {T['text_primary']}; }}
    .dq-ok {{
        background: rgba(92, 107, 92, 0.08);
        border: 1px solid rgba(92, 107, 92, 0.20);
        border-radius: 10px;
        padding: 14px 18px;
        margin: 8px 0;
        color: {T['text_secondary']};
    }}
    .dq-ok strong {{ color: {T['text_primary']}; }}

    /* ── Tabs ─────────────────────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0;
        background: transparent;
        border-bottom: 1px solid rgba(255,255,255,0.08);
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 0;
        padding: 12px 28px;
        font-weight: 600;
        font-size: 0.88rem;
        color: {T['text_muted']} !important;
        background: transparent !important;
        border-bottom: 2px solid transparent;
    }}
    .stTabs [aria-selected="true"] {{
        color: {T['text_primary']} !important;
        background: rgba(201, 168, 76, 0.06) !important;
        border-bottom: 2px solid {T['accent']} !important;
    }}

    /* ── Metrics ──────────────────────────────────────────────────────────── */
    [data-testid="stMetricValue"] {{
        font-size: 1.8rem !important;
        font-weight: 800 !important;
        color: {T['text_primary']} !important;
    }}
    [data-testid="stMetricLabel"] {{
        color: {T['text_muted']} !important;
        font-weight: 500 !important;
    }}

    /* ── Selectbox / Multiselect ──────────────────────────────────────────── */
    .stSelectbox label, .stMultiSelect label {{
        color: {T['text_primary']} !important;
        font-weight: 700 !important;
        font-size: 0.88rem !important;
    }}

    /* ── Download buttons ─────────────────────────────────────────────────── */
    .stDownloadButton > button {{
        background: {T['accent']} !important;
        color: #0a0a0a !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        padding: 8px 20px !important;
    }}
    .stDownloadButton > button:hover {{
        background: {T['accent_secondary']} !important;
    }}

    /* ── Expander ─────────────────────────────────────────────────────────── */
    .streamlit-expanderHeader {{
        font-weight: 600 !important;
        color: {T['text_primary']} !important;
        background: {T['bg_card']} !important;
        border-radius: 10px !important;
    }}

    /* ── Scrollbar ────────────────────────────────────────────────────────── */
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: {T['bg']}; }}
    ::-webkit-scrollbar-thumb {{ background: rgba(255,255,255,0.1); border-radius: 3px; }}

    /* ── Hide branding ────────────────────────────────────────────────────── */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    /* ── Dashboard title ──────────────────────────────────────────────────── */
    .dashboard-title {{
        font-size: 2.6rem;
        font-weight: 900;
        text-align: center;
        color: #ffffff;
        margin-bottom: 0;
        letter-spacing: -0.02em;
        text-shadow: 0 0 40px rgba(201, 168, 76, 0.15);
    }}
    .dashboard-subtitle {{
        text-align: center;
        color: {T['text_muted']};
        margin-bottom: 24px;
        font-size: 0.92rem;
        font-weight: 400;
    }}

    /* ── Filter pill summary ──────────────────────────────────────────────── */
    .filter-pill {{
        display: inline-block;
        background: {T['accent_dim']};
        border: 1px solid {T['bg_card_border']};
        border-radius: 16px;
        padding: 3px 12px;
        font-size: 0.75rem;
        font-weight: 500;
        color: {T['accent']};
        margin: 2px;
    }}

    /* ── Sidebar divider ──────────────────────────────────────────────────── */
    .sidebar-divider {{
        border: none;
        height: 1px;
        background: rgba(255,255,255,0.06);
        margin: 14px 0;
    }}

    /* ── FreightFox star watermark ─────────────────────────────────────── */
    .watermark {{
        position: fixed;
        bottom: 20px;
        right: 30px;
        font-size: 3rem;
        color: rgba(201, 168, 76, 0.08);
        pointer-events: none;
        z-index: 0;
    }}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# Data loading & cleaning
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("shipments.csv")
    date_cols = [
        "booking_date", "pickup_date", "delivery_date",
        "promised_delivery_date", "actual_delivery_date",
    ]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    df = df.drop_duplicates(subset=["shipment_id"], keep="first")
    df["delay_days"] = (
        df["actual_delivery_date"] - df["promised_delivery_date"]
    ).dt.days
    df["is_late"] = df["delay_days"] > 0
    df["cost_per_km"] = df["freight_cost"] / df["distance_km"]
    df["booking_month"] = df["booking_date"].dt.to_period("M").astype(str)
    return df


df = load_data()
delivered = df[df["actual_delivery_date"].notna()].copy()


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
def kpi_card(label, value, delta=None, delta_type="neutral"):
    delta_html = ""
    if delta:
        delta_html = f'<div class="kpi-delta {delta_type}">{delta}</div>'
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """


def insight_box(text):
    return f'<div class="insight-box">{text}</div>'


def fig_layout(fig, height=450):
    fig.update_layout(
        template=T["plotly_template"],
        height=height,
        paper_bgcolor=T["plotly_paper"],
        plot_bgcolor=T["plotly_plot"],
        font=dict(family="Inter, sans-serif", color=T["plotly_font_color"], size=12),
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(
            bgcolor=T["plotly_legend_bg"],
            bordercolor="rgba(255,255,255,0.06)",
            borderwidth=1,
            font=dict(size=11, color=T["plotly_font_color"]),
        ),
        xaxis=dict(
            gridcolor=T["plotly_grid"],
            title_font=dict(size=12, color=T["text_secondary"]),
            tickfont=dict(size=11, color=T["text_muted"]),
        ),
        yaxis=dict(
            gridcolor=T["plotly_grid"],
            title_font=dict(size=12, color=T["text_secondary"]),
            tickfont=dict(size=11, color=T["text_muted"]),
        ),
        hoverlabel=dict(
            bgcolor=T["bg_card"],
            bordercolor=T["bg_card_border"],
            font=dict(family="Inter, sans-serif", size=12, color=T["text_primary"]),
        ),
    )
    return fig


# ──────────────────────────────────────────────────────────────────────────────
# Sidebar (matching reference: simple, clean)
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand + theme toggle
    col_brand, col_theme = st.columns([4, 1])
    with col_brand:
        st.markdown(
            f"<div style='display:flex; align-items:center; gap:10px; padding:8px 0;'>"
            f"<span style='font-size:1.3rem;'>📦</span>"
            f"<span style='font-size:1.2rem; font-weight:800; color:{T['text_primary']};'>FreightFox</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with col_theme:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        theme_icon = "☀️" if st.session_state.theme == "dark" else "🌙"
        if st.button(theme_icon, key="theme_toggle", help="Toggle theme"):
            st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
            st.rerun()

    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

    # Region filter
    st.markdown(f"**Region**")
    regions = st.multiselect(
        "Region",
        options=sorted(df["region"].unique()),
        default=sorted(df["region"].unique()),
        label_visibility="collapsed",
    )

    # Carrier filter
    st.markdown(f"**Carrier**")
    carriers = st.multiselect(
        "Carrier",
        options=sorted(df["carrier_id"].unique()),
        default=sorted(df["carrier_id"].unique()),
        label_visibility="collapsed",
    )

    # Mode filter
    st.markdown(f"**Transport Mode**")
    modes = st.multiselect(
        "Transport Mode",
        options=sorted(df["mode"].unique()),
        default=sorted(df["mode"].unique()),
        label_visibility="collapsed",
    )

    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

    # Time Period / Status
    st.markdown(f"**Time Period**")
    statuses = st.multiselect(
        "Status",
        options=sorted(df["status"].unique()),
        default=sorted(df["status"].unique()),
        label_visibility="collapsed",
    )

    # Date range
    min_date = df["booking_date"].min()
    max_date = df["booking_date"].max()
    if pd.notna(min_date) and pd.notna(max_date):
        date_range = st.date_input(
            "Booking Date Range",
            value=(min_date.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date(),
            label_visibility="collapsed",
        )
    else:
        date_range = None


# ──────────────────────────────────────────────────────────────────────────────
# Apply filters
# ──────────────────────────────────────────────────────────────────────────────
mask = (
    df["region"].isin(regions)
    & df["carrier_id"].isin(carriers)
    & df["mode"].isin(modes)
    & df["status"].isin(statuses)
)
if date_range and len(date_range) == 2:
    date_start, date_end = date_range
    date_mask = (
        (df["booking_date"].dt.date >= date_start)
        & (df["booking_date"].dt.date <= date_end)
    ) | df["booking_date"].isna()
    mask = mask & date_mask

fdf = df[mask].copy()
fdel = fdf[fdf["actual_delivery_date"].notna()].copy()

if len(fdf) == 0:
    st.warning("⚠️ No shipments match the current filters. Adjust the sidebar filters.")
    st.stop()


# ──────────────────────────────────────────────────────────────────────────────
# Header
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    '<h1 class="dashboard-title">Shipment Analytics Dashboard</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="dashboard-subtitle">'
    'Freight performance insights • On-time delivery • Cost analysis • Data quality</p>',
    unsafe_allow_html=True,
)


# ──────────────────────────────────────────────────────────────────────────────
# Tabs (short names like reference)
# ──────────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview",
    "Regional",
    "Cost",
    "Delays",
    "Quality",
])


# ======================================================================
# TAB 1: OVERVIEW
# ======================================================================
with tab1:
    # KPI row — 4 cards matching reference
    total = len(fdf)
    on_time_count = (fdel["is_late"] == False).sum() if len(fdel) > 0 else 0
    on_time_pct = (on_time_count / len(fdel) * 100) if len(fdel) > 0 else 0
    avg_delay = fdel["delay_days"].mean() if len(fdel) > 0 else 0
    avg_cost = fdf["freight_cost"].mean()

    cols = st.columns(4)
    with cols[0]:
        st.markdown(kpi_card("Total Shipments", f"{total:,}"), unsafe_allow_html=True)
    with cols[1]:
        # On-Time Rate with gauge
        st.markdown(
            f'<div class="kpi-card">'
            f'<div class="kpi-label">On-Time Rate</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=on_time_pct,
            number={"suffix": "%", "font": {"size": 36, "color": T["text_primary"], "family": "Inter"}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 0, "tickcolor": T["bg"], "dtick": 25,
                         "tickfont": {"size": 9, "color": T["text_muted"]}},
                "bar": {"color": T["accent"], "thickness": 0.3},
                "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 50], "color": "rgba(200,80,70,0.15)"},
                    {"range": [50, 75], "color": "rgba(201,168,76,0.12)"},
                    {"range": [75, 100], "color": "rgba(92,107,92,0.15)"},
                ],
                "threshold": {
                    "line": {"color": "#c9534a", "width": 2},
                    "thickness": 0.8,
                    "value": 95,
                },
            },
        ))
        fig_gauge.update_layout(
            height=160,
            margin=dict(l=20, r=20, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"),
        )
        # Add "Target: 95%" annotation
        fig_gauge.add_annotation(
            text=f"<span style='color: #5c6b5c;'>Target: 95%</span>",
            x=0.5, y=-0.05,
            showarrow=False,
            font=dict(size=11, color="#5c6b5c", family="Inter"),
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    with cols[2]:
        st.markdown(
            kpi_card(
                "Avg Delay",
                f"{avg_delay:.1f}d",
                "vs promised date",
                "bad" if avg_delay > 0 else "good",
            ),
            unsafe_allow_html=True,
        )
    with cols[3]:
        st.markdown(
            kpi_card("Avg Freight Cost", f"₹{avg_cost:,.0f}"),
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 2: Status donut + Volume trend (combo chart)
    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.markdown('<div class="section-header">Shipment Status Breakdown</div>', unsafe_allow_html=True)
        status_counts = fdf["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]

        fig_status = px.pie(
            status_counts,
            values="Count",
            names="Status",
            color="Status",
            color_discrete_map=STATUS_COLORS,
            hole=0.6,
        )
        fig_status.update_traces(
            textposition="outside",
            textinfo="label+percent",
            textfont_size=12,
            textfont_color=T["plotly_font_color"],
            pull=[0.02] * len(status_counts),
            hovertemplate="<b>%{label}</b><br>Count: %{value:,}<br>Share: %{percent}<extra></extra>",
            marker=dict(line=dict(color=T["bg"], width=2)),
        )
        fig_layout(fig_status, 380)
        st.plotly_chart(fig_status, use_container_width=True)

    with col_right:
        st.markdown('<div class="section-header">Shipment Volume & On-Time Trend</div>', unsafe_allow_html=True)
        monthly = fdf.dropna(subset=["booking_date"]).copy()
        monthly["month"] = monthly["booking_date"].dt.to_period("M").dt.to_timestamp()
        trend = monthly.groupby("month").agg(
            shipments=("shipment_id", "count"),
        ).reset_index()

        monthly_del = fdel.dropna(subset=["booking_date"]).copy()
        monthly_del["month"] = monthly_del["booking_date"].dt.to_period("M").dt.to_timestamp()
        trend_ot = monthly_del.groupby("month").agg(
            on_time=("is_late", lambda x: (x == False).sum()),
            total_del=("is_late", "count"),
        ).reset_index()
        trend_ot["on_time_pct"] = trend_ot["on_time"] / trend_ot["total_del"] * 100
        trend = trend.merge(trend_ot[["month", "on_time_pct"]], on="month", how="left")

        fig_trend = make_subplots(specs=[[{"secondary_y": True}]])

        # Combo Chart label in legend
        fig_trend.add_trace(
            go.Bar(
                x=trend["month"],
                y=trend["shipments"],
                name="Combo Chart",
                marker_color=T["accent"],
                marker_line_width=0,
                opacity=0.75,
                hovertemplate="<b>%{x|%b %Y}</b><br>Shipments: %{y:,}<extra></extra>",
            ),
            secondary_y=False,
        )
        fig_trend.add_trace(
            go.Scatter(
                x=trend["month"],
                y=trend["on_time_pct"],
                name="On-Time %",
                line=dict(color="#5c6b5c", width=2.5),
                mode="lines+markers",
                marker=dict(size=6, color="#5c6b5c"),
                hovertemplate="<b>%{x|%b %Y}</b><br>On-Time: %{y:.1f}%<extra></extra>",
            ),
            secondary_y=True,
        )
        fig_trend.update_yaxes(title_text="Shipment Count", secondary_y=False, gridcolor=T["plotly_grid"])
        fig_trend.update_yaxes(title_text="On-Time %", secondary_y=True, range=[0, 100], gridcolor=T["plotly_grid"])
        fig_trend.update_xaxes(title_text="Month", gridcolor=T["plotly_grid"])
        fig_layout(fig_trend, 380)
        st.plotly_chart(fig_trend, use_container_width=True)

    # Row 3: Performance Heatmap (Region × Carrier) at bottom of overview
    st.markdown('<div class="section-header">Performance Heatmap</div>', unsafe_allow_html=True)

    col_heat1, col_heat2 = st.columns(2)

    with col_heat1:
        # Mode performance
        mode_perf = fdel.groupby("mode").agg(
            total=("shipment_id", "count"),
            late=("is_late", "sum"),
            avg_delay=("delay_days", "mean"),
        ).reset_index()
        mode_perf["on_time_pct"] = (1 - mode_perf["late"] / mode_perf["total"]) * 100

        fig_mode = go.Figure()
        fig_mode.add_trace(go.Bar(
            x=mode_perf["mode"],
            y=mode_perf["on_time_pct"],
            marker_color=CHART_COLORS[:len(mode_perf)],
            text=mode_perf["on_time_pct"].round(1).astype(str) + "%",
            textposition="outside",
            textfont=dict(size=12, color=T["plotly_font_color"]),
            hovertemplate="<b>%{x}</b><br>On-Time: %{y:.1f}%<br>Total: %{customdata[0]:,}<extra></extra>",
            customdata=np.stack((mode_perf["total"],), axis=-1),
        ))
        fig_mode.update_yaxes(range=[0, 100], title_text="On-Time %")
        fig_mode.update_layout(title=dict(text="By Transport Mode", font=dict(size=13, color=T["text_heading"])))
        fig_layout(fig_mode, 350)
        st.plotly_chart(fig_mode, use_container_width=True)

    with col_heat2:
        # Region performance
        region_perf = fdel.groupby("region").agg(
            total=("shipment_id", "count"),
            late=("is_late", "sum"),
            avg_delay=("delay_days", "mean"),
        ).reset_index()
        region_perf["on_time_pct"] = (1 - region_perf["late"] / region_perf["total"]) * 100
        region_perf = region_perf.sort_values("on_time_pct")

        fig_region = go.Figure()
        fig_region.add_trace(go.Bar(
            x=region_perf["region"],
            y=region_perf["on_time_pct"],
            marker_color=[REGION_COLORS.get(r, T["accent"]) for r in region_perf["region"]],
            text=region_perf["on_time_pct"].round(1).astype(str) + "%",
            textposition="outside",
            textfont=dict(size=12, color=T["plotly_font_color"]),
            hovertemplate="<b>%{x}</b><br>On-Time: %{y:.1f}%<br>Total: %{customdata[0]:,}<extra></extra>",
            customdata=np.stack((region_perf["total"],), axis=-1),
        ))
        fig_region.update_yaxes(range=[0, 100], title_text="On-Time %")
        fig_region.update_layout(title=dict(text="By Region", font=dict(size=13, color=T["text_heading"])))
        fig_layout(fig_region, 350)
        st.plotly_chart(fig_region, use_container_width=True)

    # Download
    with st.expander("📥 Download Filtered Data"):
        st.download_button(
            label="⬇️ Download CSV",
            data=fdf.to_csv(index=False).encode("utf-8"),
            file_name="freightfox_filtered.csv",
            mime="text/csv",
        )


# ======================================================================
# TAB 2: REGIONAL
# ======================================================================
with tab2:
    st.markdown(insight_box(
        "<strong>Key Finding:</strong> The <strong>Central</strong> region has the worst on-time delivery "
        "at <strong>50.3% late rate</strong>, driven primarily by carriers CARR_08 (61.1% late) and "
        "CARR_02 (58.6% late). South has fewer data points (only 126 delivered with actual dates) "
        "making its stats less reliable."
    ), unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">Late Delivery Rate by Region</div>', unsafe_allow_html=True)
        rp = fdel.groupby("region").agg(
            total=("shipment_id", "count"),
            late=("is_late", "sum"),
            avg_delay=("delay_days", "mean"),
        ).reset_index()
        rp["late_pct"] = rp["late"] / rp["total"] * 100
        rp = rp.sort_values("late_pct", ascending=True)

        fig_rp = go.Figure()
        fig_rp.add_trace(go.Bar(
            y=rp["region"],
            x=rp["late_pct"],
            orientation="h",
            marker_color=[REGION_COLORS.get(r, T["accent"]) for r in rp["region"]],
            text=rp.apply(lambda r: f"{r['late_pct']:.1f}% ({int(r['late'])}/{int(r['total'])})", axis=1),
            textposition="outside",
            textfont=dict(size=11, color=T["plotly_font_color"]),
            hovertemplate="<b>%{y}</b><br>Late: %{x:.1f}%<br>Avg Delay: %{customdata:.1f} days<extra></extra>",
            customdata=rp["avg_delay"],
        ))
        fig_rp.update_xaxes(title_text="Late Delivery %", range=[0, max(rp["late_pct"]) * 1.35])
        fig_layout(fig_rp, 370)
        st.plotly_chart(fig_rp, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Avg Delay (days) by Region</div>', unsafe_allow_html=True)
        rp_sorted = rp.sort_values("avg_delay", ascending=True)
        fig_delay = go.Figure()
        fig_delay.add_trace(go.Bar(
            y=rp_sorted["region"],
            x=rp_sorted["avg_delay"],
            orientation="h",
            marker_color=[REGION_COLORS.get(r, T["accent"]) for r in rp_sorted["region"]],
            text=rp_sorted["avg_delay"].round(2).astype(str) + " days",
            textposition="outside",
            textfont=dict(size=11, color=T["plotly_font_color"]),
            hovertemplate="<b>%{y}</b><br>Avg Delay: %{x:.2f} days<extra></extra>",
        ))
        fig_delay.update_xaxes(title_text="Avg Delay (days)")
        fig_layout(fig_delay, 370)
        st.plotly_chart(fig_delay, use_container_width=True)

    # Heatmap
    st.markdown('<div class="section-header">Late % Heatmap: Region × Carrier</div>', unsafe_allow_html=True)
    rc = fdel.groupby(["region", "carrier_id"]).agg(
        total=("shipment_id", "count"),
        late=("is_late", "sum"),
    ).reset_index()
    rc["late_pct"] = rc["late"] / rc["total"] * 100
    heatmap_data = rc.pivot_table(index="region", columns="carrier_id", values="late_pct", aggfunc="first")
    count_data = rc.pivot_table(index="region", columns="carrier_id", values="total", aggfunc="first")

    hover_text = []
    for i, region in enumerate(heatmap_data.index):
        row_text = []
        for j, carrier in enumerate(heatmap_data.columns):
            late_val = heatmap_data.iloc[i, j]
            count_val = count_data.iloc[i, j]
            if pd.notna(late_val):
                row_text.append(f"Region: {region}<br>Carrier: {carrier}<br>Late: {late_val:.1f}%<br>Shipments: {int(count_val)}")
            else:
                row_text.append("No data")
        hover_text.append(row_text)

    fig_heat = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns.tolist(),
        y=heatmap_data.index.tolist(),
        colorscale=[[0, "#2d3a2d"], [0.5, "#c9a84c"], [1, "#a0522d"]],
        text=heatmap_data.round(0).values,
        texttemplate="%{text}%",
        textfont=dict(size=11),
        hovertext=hover_text,
        hovertemplate="%{hovertext}<extra></extra>",
        colorbar=dict(title=dict(text="Late %", font=dict(color=T["plotly_font_color"])),
                      tickfont=dict(color=T["plotly_font_color"])),
    ))
    fig_layout(fig_heat, 400)
    st.plotly_chart(fig_heat, use_container_width=True)

    # Drill-down
    st.markdown('<div class="section-header">Drill Down: Region Performance</div>', unsafe_allow_html=True)
    selected_region = st.selectbox("Select region", sorted(fdel["region"].unique()), key="region_drill")
    region_data = fdel[fdel["region"] == selected_region]

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        carrier_br = region_data.groupby("carrier_id").agg(
            total=("shipment_id", "count"), late=("is_late", "sum"), avg_delay=("delay_days", "mean"),
        ).reset_index()
        carrier_br["late_pct"] = carrier_br["late"] / carrier_br["total"] * 100
        carrier_br = carrier_br.sort_values("late_pct", ascending=False)

        fig_cb = go.Figure()
        fig_cb.add_trace(go.Bar(
            x=carrier_br["carrier_id"], y=carrier_br["late_pct"],
            marker_color=np.where(carrier_br["late_pct"] > 55, "#a0522d",
                np.where(carrier_br["late_pct"] > 45, "#c9a84c", "#5c6b5c")),
            text=carrier_br["late_pct"].round(1).astype(str) + "%", textposition="outside",
            textfont=dict(size=11, color=T["plotly_font_color"]),
            hovertemplate="<b>%{x}</b><br>Late: %{y:.1f}%<extra></extra>",
        ))
        fig_cb.update_yaxes(range=[0, 100], title_text="Late %")
        fig_cb.update_layout(title=dict(text=f"Carriers in {selected_region}", font=dict(size=13, color=T["text_heading"])))
        fig_layout(fig_cb, 380)
        st.plotly_chart(fig_cb, use_container_width=True)

    with col_d2:
        mode_br = region_data.groupby("mode").agg(
            total=("shipment_id", "count"), late=("is_late", "sum"), avg_delay=("delay_days", "mean"),
        ).reset_index()
        mode_br["late_pct"] = mode_br["late"] / mode_br["total"] * 100

        fig_mb = go.Figure()
        fig_mb.add_trace(go.Bar(
            x=mode_br["mode"], y=mode_br["late_pct"],
            marker_color=CHART_COLORS[:len(mode_br)],
            text=mode_br["late_pct"].round(1).astype(str) + "%", textposition="outside",
            textfont=dict(size=11, color=T["plotly_font_color"]),
            hovertemplate="<b>%{x}</b><br>Late: %{y:.1f}%<extra></extra>",
        ))
        fig_mb.update_yaxes(range=[0, 100], title_text="Late %")
        fig_mb.update_layout(title=dict(text=f"Modes in {selected_region}", font=dict(size=13, color=T["text_heading"])))
        fig_layout(fig_mb, 380)
        st.plotly_chart(fig_mb, use_container_width=True)

    with st.expander(f"📋 View {selected_region} Shipment Data"):
        region_table = region_data[["shipment_id", "carrier_id", "mode", "customer_id",
                                     "promised_delivery_date", "actual_delivery_date",
                                     "delay_days", "freight_cost", "distance_km"]].sort_values("delay_days", ascending=False)
        st.dataframe(region_table,
            use_container_width=True, height=400)
        st.download_button(f"⬇️ Download {selected_region} Data",
            data=region_table.to_csv(index=False).encode("utf-8"),
            file_name=f"freightfox_{selected_region.lower()}.csv", mime="text/csv", key="dl_region")


# ======================================================================
# TAB 3: COST
# ======================================================================
with tab3:
    st.markdown(insight_box(
        "<strong>Key Finding:</strong> Overall correlation between freight cost and distance is "
        "<strong>weak (r = 0.30)</strong>. However, <strong>CARR_07 is an extreme outlier</strong> — "
        "charging on average <strong>₹206K per shipment</strong> vs ₹20K for other carriers, "
        "with costs <strong>548% above</strong> the regression line."
    ), unsafe_allow_html=True)

    st.markdown('<div class="section-header">Freight Cost vs Distance</div>', unsafe_allow_html=True)
    valid = fdf[fdf["distance_km"] > 0].copy()
    coeffs = np.polyfit(valid["distance_km"], valid["freight_cost"], 1)
    x_line = np.linspace(valid["distance_km"].min(), valid["distance_km"].max(), 100)
    y_line = np.polyval(coeffs, x_line)
    valid["carrier_group"] = np.where(valid["carrier_id"] == "CARR_07", "CARR_07 (Outlier)", "Other Carriers")

    fig_scatter = px.scatter(
        valid, x="distance_km", y="freight_cost", color="carrier_group",
        color_discrete_map={"CARR_07 (Outlier)": "#a0522d", "Other Carriers": "rgba(201,168,76,0.4)"},
        opacity=0.5, hover_data=["carrier_id", "shipment_id", "region"],
        labels={"distance_km": "Distance (km)", "freight_cost": "Freight Cost (₹)"},
    )
    fig_scatter.add_trace(go.Scatter(
        x=x_line, y=y_line, mode="lines",
        name=f"Regression (slope={coeffs[0]:.1f})",
        line=dict(color=T["accent"], width=2, dash="dash"),
    ))
    corr_val = valid['freight_cost'].corr(valid['distance_km'])
    fig_scatter.update_layout(title=dict(text=f"Pearson r = {corr_val:.3f}", font=dict(size=13, color=T["text_heading"])))
    fig_layout(fig_scatter, 480)
    st.plotly_chart(fig_scatter, use_container_width=True)

    col_ex1, col_ex2 = st.columns(2)
    with col_ex1:
        st.markdown('<div class="section-header">Excluding CARR_07</div>', unsafe_allow_html=True)
        valid_no7 = valid[valid["carrier_id"] != "CARR_07"]
        corr_no7 = valid_no7["freight_cost"].corr(valid_no7["distance_km"])
        coeffs_no7 = np.polyfit(valid_no7["distance_km"], valid_no7["freight_cost"], 1)
        fig_no7 = px.scatter(valid_no7, x="distance_km", y="freight_cost", color="carrier_id", opacity=0.4,
            labels={"distance_km": "Distance (km)", "freight_cost": "Freight Cost (₹)"})
        x_l2 = np.linspace(valid_no7["distance_km"].min(), valid_no7["distance_km"].max(), 100)
        fig_no7.add_trace(go.Scatter(x=x_l2, y=np.polyval(coeffs_no7, x_l2), mode="lines",
            name=f"Regression (slope={coeffs_no7[0]:.1f})", line=dict(color=T["accent"], width=2, dash="dash")))
        fig_no7.update_layout(title=dict(text=f"Excl. CARR_07 — r = {corr_no7:.3f}", font=dict(size=13, color=T["text_heading"])))
        fig_layout(fig_no7, 420)
        st.plotly_chart(fig_no7, use_container_width=True)

    with col_ex2:
        st.markdown('<div class="section-header">Carrier Cost Deviation</div>', unsafe_allow_html=True)
        valid["predicted_cost"] = np.polyval(coeffs, valid["distance_km"])
        valid["residual_pct"] = (valid["freight_cost"] - valid["predicted_cost"]) / valid["predicted_cost"] * 100
        carrier_res = valid.groupby("carrier_id").agg(
            avg_residual_pct=("residual_pct", "mean"), count=("shipment_id", "count"),
        ).reset_index().sort_values("avg_residual_pct", ascending=False)

        fig_res = go.Figure()
        fig_res.add_trace(go.Bar(
            x=carrier_res["carrier_id"], y=carrier_res["avg_residual_pct"],
            marker_color=np.where(carrier_res["avg_residual_pct"] > 50, "#a0522d",
                np.where(carrier_res["avg_residual_pct"] > 0, "#c9a84c", "#5c6b5c")),
            text=carrier_res["avg_residual_pct"].round(0).astype(int).astype(str) + "%",
            textposition="outside", textfont=dict(size=11, color=T["plotly_font_color"]),
            hovertemplate="<b>%{x}</b><br>Deviation: %{y:+.1f}%<br>Shipments: %{customdata:,}<extra></extra>",
            customdata=carrier_res["count"],
        ))
        fig_res.update_yaxes(title_text="Avg Deviation %")
        fig_res.update_layout(title=dict(text="Cost Deviation by Carrier", font=dict(size=13, color=T["text_heading"])))
        fig_layout(fig_res, 420)
        st.plotly_chart(fig_res, use_container_width=True)

    # Cost table
    st.markdown('<div class="section-header">Carrier Cost Comparison</div>', unsafe_allow_html=True)
    cost_table = valid.groupby("carrier_id").agg(
        shipments=("shipment_id", "count"), avg_cost=("freight_cost", "mean"),
        median_cost=("freight_cost", "median"), avg_distance=("distance_km", "mean"),
        avg_cost_per_km=("cost_per_km", "mean"), avg_deviation_pct=("residual_pct", "mean"),
    ).reset_index().sort_values("avg_deviation_pct", ascending=False)
    cost_table.columns = ["Carrier", "Shipments", "Avg Cost (₹)", "Median Cost (₹)", "Avg Distance (km)", "Avg ₹/km", "Avg Deviation %"]

    st.dataframe(cost_table,
        use_container_width=True, height=560)


# ======================================================================
# TAB 4: DELAYS
# ======================================================================
with tab4:
    st.markdown(insight_box(
        "<strong>Key Finding:</strong> <strong>CUST_026</strong> has the worst delay rate at "
        "<strong>73.9%</strong> (17/23 deliveries late). The top 5 worst customers all have "
        "delays spread across <strong>multiple carriers and regions</strong>, suggesting the "
        "issue is <strong>not carrier-driven</strong>."
    ), unsafe_allow_html=True)

    st.markdown('<div class="section-header">Top 20 Customers by Late Rate</div>', unsafe_allow_html=True)
    cust_perf = fdel.groupby("customer_id").agg(
        total=("shipment_id", "count"), late=("is_late", "sum"), avg_delay=("delay_days", "mean"),
    ).reset_index()
    cust_perf["late_pct"] = cust_perf["late"] / cust_perf["total"] * 100
    cust_perf = cust_perf.sort_values("late_pct", ascending=False)
    top20 = cust_perf.head(20)

    fig_cust = go.Figure()
    fig_cust.add_trace(go.Bar(
        x=top20["customer_id"], y=top20["late_pct"],
        marker_color=np.where(top20["late_pct"] > 65, "#a0522d",
            np.where(top20["late_pct"] > 55, "#c9a84c", "#5c6b5c")),
        text=top20.apply(lambda r: f"{r['late_pct']:.0f}%", axis=1),
        textposition="outside", textfont=dict(size=10, color=T["plotly_font_color"]),
        hovertemplate="<b>%{x}</b><br>Late: %{y:.1f}%<br>Avg Delay: %{customdata:.1f}d<extra></extra>",
        customdata=top20["avg_delay"],
    ))
    fig_cust.update_yaxes(range=[0, 100], title_text="Late %")
    fig_layout(fig_cust, 420)
    st.plotly_chart(fig_cust, use_container_width=True)

    # Customer drill-down
    st.markdown('<div class="section-header">Customer Root-Cause Analysis</div>', unsafe_allow_html=True)
    selected_cust = st.selectbox("Select customer", top20["customer_id"].tolist(), key="cust_drill")
    cust_data = fdel[fdel["customer_id"] == selected_cust]
    cust_info = cust_perf[cust_perf["customer_id"] == selected_cust].iloc[0]

    kcols = st.columns(4)
    with kcols[0]:
        st.markdown(kpi_card("Total Deliveries", f"{int(cust_info['total'])}"), unsafe_allow_html=True)
    with kcols[1]:
        st.markdown(kpi_card("Late Rate", f"{cust_info['late_pct']:.1f}%"), unsafe_allow_html=True)
    with kcols[2]:
        st.markdown(kpi_card("Late Shipments", f"{int(cust_info['late'])}"), unsafe_allow_html=True)
    with kcols[3]:
        st.markdown(kpi_card("Avg Delay", f"{cust_info['avg_delay']:.1f}d"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_c1, col_c2 = st.columns(2)

    with col_c1:
        cust_carrier = cust_data.groupby("carrier_id").agg(
            total=("shipment_id", "count"), late=("is_late", "sum"), avg_delay=("delay_days", "mean"),
        ).reset_index()
        cust_carrier["late_pct"] = cust_carrier["late"] / cust_carrier["total"] * 100
        cust_carrier = cust_carrier.sort_values("late_pct", ascending=False)

        fig_cc = go.Figure()
        fig_cc.add_trace(go.Bar(
            x=cust_carrier["carrier_id"], y=cust_carrier["late_pct"],
            marker_color=np.where(cust_carrier["late_pct"] > 70, "#a0522d",
                np.where(cust_carrier["late_pct"] > 40, "#c9a84c", "#5c6b5c")),
            text=cust_carrier.apply(lambda r: f"{r['late_pct']:.0f}%", axis=1),
            textposition="outside", textfont=dict(size=11, color=T["plotly_font_color"]),
        ))
        fig_cc.update_yaxes(range=[0, 120], title_text="Late %")
        fig_cc.update_layout(title=dict(text=f"{selected_cust} — by Carrier", font=dict(size=13, color=T["text_heading"])))
        fig_layout(fig_cc, 380)
        st.plotly_chart(fig_cc, use_container_width=True)

    with col_c2:
        cust_region = cust_data.groupby("region").agg(
            total=("shipment_id", "count"), late=("is_late", "sum"), avg_delay=("delay_days", "mean"),
        ).reset_index()
        cust_region["late_pct"] = cust_region["late"] / cust_region["total"] * 100

        fig_cr = go.Figure()
        fig_cr.add_trace(go.Bar(
            x=cust_region["region"], y=cust_region["late_pct"],
            marker_color=[REGION_COLORS.get(r, T["accent"]) for r in cust_region["region"]],
            text=cust_region.apply(lambda r: f"{r['late_pct']:.0f}%", axis=1),
            textposition="outside", textfont=dict(size=11, color=T["plotly_font_color"]),
        ))
        fig_cr.update_yaxes(range=[0, 120], title_text="Late %")
        fig_cr.update_layout(title=dict(text=f"{selected_cust} — by Region", font=dict(size=13, color=T["text_heading"])))
        fig_layout(fig_cr, 380)
        st.plotly_chart(fig_cr, use_container_width=True)

    with st.expander(f"📋 {selected_cust} — Shipment Details"):
        detail = cust_data[["shipment_id", "region", "carrier_id", "mode",
            "promised_delivery_date", "actual_delivery_date", "delay_days", "freight_cost", "distance_km"
        ]].sort_values("delay_days", ascending=False)
        st.dataframe(detail,
            use_container_width=True, height=400)


# ======================================================================
# TAB 5: QUALITY
# ======================================================================
with tab5:
    st.markdown(insight_box(
        "<strong>Data quality is critical</strong> — before trusting any analysis, we identified "
        "and handled several issues in this dataset."
    ), unsafe_allow_html=True)

    issues = [
        {"title": "🔴 15 Duplicate Shipment IDs",
         "desc": "15 rows share a <code>shipment_id</code> with another row.",
         "handling": "Kept first occurrence; dropped duplicates.", "severity": "high"},
        {"title": "🟠 1,488 Missing Actual Delivery Dates (29.7%)",
         "desc": "Nearly 30% of rows have no <code>actual_delivery_date</code>.",
         "handling": "Only used rows with actual dates for on-time analysis (3,527 usable).", "severity": "high"},
        {"title": "🟠 588 'Delivered' with No Actual Date",
         "desc": "Marked Delivered but lack actual delivery date.",
         "handling": "Excluded from on-time calculations; flagged as data gap.", "severity": "high"},
        {"title": "🟠 499 Rows with Actual Date but Status ≠ Delivered",
         "desc": "Status contradicts the date field.",
         "handling": "Included in on-time analysis (date is usable).", "severity": "medium"},
        {"title": "🟡 71 Missing Booking Dates, 88 Missing Pickup Dates",
         "desc": "Gaps in operational date tracking.",
         "handling": "Excluded from time-trend charts.", "severity": "medium"},
        {"title": "🟡 244 Same Origin & Destination City",
         "desc": "Non-zero distances suggest route distance, not city-to-city.",
         "handling": "Retained — distance_km reflects actual route.", "severity": "low"},
        {"title": "🟡 231 Freight Cost Outliers (>3×IQR)",
         "desc": "Almost all belong to CARR_07.",
         "handling": "Not removed — CARR_07 is consistently premium-priced.", "severity": "low"},
        {"title": "🟢 South Region Under-represented",
         "desc": "Only 126 delivered records vs 830+ for other regions.",
         "handling": "Stats interpreted with caution.", "severity": "low"},
    ]

    for issue in issues:
        sev_class = "dq-issue" if issue["severity"] in ("high", "medium") else "dq-ok"
        st.markdown(
            f'<div class="{sev_class}"><strong>{issue["title"]}</strong><br>'
            f'{issue["desc"]}<br><br><em>Handling:</em> {issue["handling"]}</div>',
            unsafe_allow_html=True)

    st.markdown('<div class="section-header">Data Quality Summary</div>', unsafe_allow_html=True)
    total_rows = len(df)
    dq_cols = st.columns(4)
    with dq_cols[0]:
        st.markdown(kpi_card("Total Rows", f"{total_rows:,}"), unsafe_allow_html=True)
    with dq_cols[1]:
        completeness = (1 - df.isnull().sum().sum() / (total_rows * len(df.columns))) * 100
        st.markdown(kpi_card("Completeness", f"{completeness:.1f}%"), unsafe_allow_html=True)
    with dq_cols[2]:
        st.markdown(kpi_card("Usable for On-Time", f"{len(delivered):,}"), unsafe_allow_html=True)
    with dq_cols[3]:
        st.markdown(kpi_card("Duplicate Rate", f"{15/total_rows*100:.2f}%"), unsafe_allow_html=True)

    # Missing data chart
    st.markdown('<div class="section-header">Missing Data by Column</div>', unsafe_allow_html=True)
    missing = df.isnull().sum().reset_index()
    missing.columns = ["Column", "Missing"]
    missing["Missing %"] = missing["Missing"] / len(df) * 100
    missing = missing[missing["Missing"] > 0].sort_values("Missing %", ascending=True)

    if len(missing) > 0:
        fig_missing = go.Figure()
        fig_missing.add_trace(go.Bar(
            y=missing["Column"], x=missing["Missing %"], orientation="h",
            marker_color=np.where(missing["Missing %"] > 20, "#a0522d",
                np.where(missing["Missing %"] > 5, "#c9a84c", "#5c6b5c")),
            text=missing.apply(lambda r: f"{r['Missing %']:.1f}% ({int(r['Missing']):,})", axis=1),
            textposition="outside", textfont=dict(size=11, color=T["plotly_font_color"]),
        ))
        fig_missing.update_xaxes(title_text="Missing %")
        fig_layout(fig_missing, 350)
        st.plotly_chart(fig_missing, use_container_width=True)


# ──────────────────────────────────────────────────────────────────────────────
# Watermark + Footer
# ──────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="watermark">✦</div>', unsafe_allow_html=True)
st.markdown(
    f"<div style='text-align:center; padding:30px 0 10px 0; color:{T['text_muted']}; font-size:0.78rem;'>"
    f"📦 FreightFox Analytics · Built with Streamlit & Plotly · "
    f"{'🌙 Dark' if st.session_state.theme == 'dark' else '☀️ Light'} Mode"
    f"</div>",
    unsafe_allow_html=True,
)
