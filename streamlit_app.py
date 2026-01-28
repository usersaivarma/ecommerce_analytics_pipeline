"""
Streamlit Dashboard for E-Commerce Analytics
Main application file
"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# Page configuration
st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# Helper Functions
# ============================================
def fetch_api_data(endpoint):
    """Fetch data from API endpoint"""
    try:
        response = requests.get(f"{API_URL}{endpoint}", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from API: {e}")
        return None

def format_currency(value):
    """Format value as currency"""
    return f"${value:,.2f}"

def format_number(value):
    """Format number with commas"""
    return f"{value:,}"

# ============================================
# Sidebar
# ============================================
st.sidebar.title("📊 Navigation")
st.sidebar.markdown("---")

# API Health Check
with st.sidebar:
    st.subheader("System Status")
    health_data = fetch_api_data("/health")
    
    if health_data:
        if health_data.get("status") == "healthy":
            st.success("✅ API Connected")
            st.info(f"🗄️ Database: {health_data.get('database', 'unknown')}")
        else:
            st.error("❌ API Disconnected")
    else:
        st.error("❌ Cannot reach API")
    
    st.markdown("---")
    
    # Date range filter (for future use)
    st.subheader("Filters")
    date_range = st.date_input(
        "Date Range",
        value=(datetime.now() - timedelta(days=30), datetime.now()),
        max_value=datetime.now()
    )

# ============================================
# Main Page
# ============================================
st.markdown('<p class="main-header">🛒 E-Commerce Analytics Dashboard</p>', unsafe_allow_html=True)
st.markdown("Real-time insights into sales, products, and customer behavior")
st.markdown("---")

# Fetch summary data
sales_summary = fetch_api_data("/sales/summary")

if sales_summary:
    # KPI Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Revenue",
            format_currency(sales_summary.get('total_revenue', 0)),
            delta=None,
            help="Total revenue across all orders"
        )
    
    with col2:
        st.metric(
            "Total Orders",
            format_number(sales_summary.get('total_orders', 0)),
            delta=None,
            help="Total number of orders"
        )
    
    with col3:
        st.metric(
            "Avg Order Value",
            format_currency(sales_summary.get('avg_order_value', 0)),
            delta=None,
            help="Average value per order"
        )
    
    with col4:
        st.metric(
            "Total Items Sold",
            format_number(sales_summary.get('total_items_sold', 0)),
            delta=None,
            help="Total items sold"
        )
    
    st.markdown("---")
    
    # Charts Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Daily Sales Trend")
        daily_sales = fetch_api_data("/sales/daily?limit=30")
        
        if daily_sales and daily_sales.get('data'):
            df_daily = pd.DataFrame(daily_sales['data'])
            df_daily['date'] = pd.to_datetime(df_daily['date'])
            df_daily = df_daily.sort_values('date')
            
            fig = px.line(
                df_daily,
                x='date',
                y='total_revenue',
                title='Revenue Over Time',
                labels={'total_revenue': 'Revenue ($)', 'date': 'Date'},
                markers=True
            )
            fig.update_layout(hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No daily sales data available")
    
    with col2:
        st.subheader("🏆 Top Product Categories")
        categories = fetch_api_data("/products/categories")
        
        if categories and categories.get('data'):
            df_categories = pd.DataFrame(categories['data'])
            df_categories = df_categories.head(5)
            
            fig = px.bar(
                df_categories,
                x='category',
                y='total_revenue',
                title='Revenue by Category',
                labels={'total_revenue': 'Revenue ($)', 'category': 'Category'},
                color='total_revenue',
                color_continuous_scale='Blues'
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No category data available")
    
    st.markdown("---")
    
    # Charts Row 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👥 Customer Segments")
        segments = fetch_api_data("/customers/segments")
        
        if segments and segments.get('data'):
            df_segments = pd.DataFrame(segments['data'])
            
            fig = px.pie(
                df_segments,
                values='customer_count',
                names='segment',
                title='Customer Distribution by Segment',
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No customer segment data available")
    
    with col2:
        st.subheader("🌎 Geographic Performance")
        geo_data = fetch_api_data("/customers/geographic?limit=10")
        
        if geo_data and geo_data.get('data'):
            df_geo = pd.DataFrame(geo_data['data'])
            
            fig = px.bar(
                df_geo,
                x='state',
                y='total_revenue',
                title='Top 10 States by Revenue',
                labels={'total_revenue': 'Revenue ($)', 'state': 'State'},
                color='total_revenue',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(showlegend=False, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No geographic data available")
    
    st.markdown("---")
    
    # Top Products Table
    st.subheader("🔥 Top Products by Revenue")
    
    top_products = fetch_api_data("/products/top?metric=revenue&limit=10")
    
    if top_products and top_products.get('data'):
        df_products = pd.DataFrame(top_products['data'])
        
        # Format the dataframe for display
        df_display = df_products[[
            'product_name', 'category', 'total_revenue', 
            'units_sold', 'avg_rating', 'review_count'
        ]].copy()
        
        df_display.columns = [
            'Product Name', 'Category', 'Revenue', 
            'Units Sold', 'Avg Rating', 'Reviews'
        ]
        
        # Format numeric columns
        df_display['Revenue'] = df_display['Revenue'].apply(format_currency)
        df_display['Units Sold'] = df_display['Units Sold'].apply(format_number)
        df_display['Avg Rating'] = df_display['Avg Rating'].round(2)
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("No product data available")
    
    st.markdown("---")
    
    # Data Quality Section
    st.subheader("✅ Data Quality Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        dq_metrics = fetch_api_data("/data-quality/metrics")
        
        if dq_metrics and dq_metrics.get('data'):
            st.write("**Quality Checks:**")
            for metric in dq_metrics['data']:
                status_icon = "✅" if metric['status'] == 'PASS' else "⚠️"
                st.write(f"{status_icon} **{metric['metric_name']}**: {metric['metric_value']}")
        else:
            st.info("No data quality metrics available")
    
    with col2:
        etl_history = fetch_api_data("/etl/history?limit=5")
        
        if etl_history and etl_history.get('data'):
            st.write("**Recent ETL Runs:**")
            for run in etl_history['data']:
                status_icon = "✅" if run['status'] == 'SUCCESS' else "❌"
                run_date = run['run_date'].split('T')[0] if run['run_date'] else 'N/A'
                st.write(f"{status_icon} {run_date} - {run.get('records_processed', 'N/A')} records")
        else:
            st.info("No ETL history available")

else:
    st.error("Unable to load dashboard data. Please check if the API is running.")
    st.info("Run `make up` to start all services.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>E-Commerce Analytics Dashboard | Built with Streamlit & FastAPI</p>
        <p style='font-size: 0.8rem;'>Last updated: {}</p>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    unsafe_allow_html=True
)
