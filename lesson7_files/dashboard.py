"""
E-commerce Business Performance Dashboard

A professional Streamlit dashboard for analyzing e-commerce business metrics
including revenue trends, product performance, geographic distribution, and customer experience.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, date
import warnings
warnings.filterwarnings('ignore')

# Import custom modules
from data_loader import (
    load_ecommerce_datasets, 
    preprocess_orders_data, 
    create_sales_dataset,
    filter_data_by_date_range,
    add_delivery_metrics
)
from business_metrics import BusinessMetricsCalculator
from dashboard_utils import (
    format_currency,
    format_number,
    format_percentage,
    create_trend_indicator,
    create_kpi_card,
    get_dashboard_css,
    create_revenue_trend_chart,
    create_category_bar_chart,
    create_choropleth_map,
    create_satisfaction_bar_chart
)


# Page configuration
st.set_page_config(
    page_title="E-commerce Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply custom CSS styling
st.markdown(get_dashboard_css(), unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load and preprocess all e-commerce datasets."""
    try:
        # Load datasets
        datasets = load_ecommerce_datasets('ecommerce_data')
        
        # Preprocess orders
        orders_processed = preprocess_orders_data(datasets['orders'])
        
        # Create sales dataset
        sales_data = create_sales_dataset(
            orders=orders_processed, 
            order_items=datasets['order_items'],
            order_status_filter='delivered'
        )
        
        # Add delivery metrics
        sales_data = add_delivery_metrics(sales_data)
        
        return {
            'sales_data': sales_data,
            'orders': orders_processed,
            'products': datasets['products'],
            'customers': datasets['customers'],
            'reviews': datasets['reviews']
        }
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None






def main():
    """Main dashboard application."""
    
    # Load data
    data = load_data()
    if data is None:
        st.error("Failed to load data. Please check your data files.")
        return
    
    # Header section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown('<h1 class="main-header">E-commerce Business Dashboard</h1>', unsafe_allow_html=True)
    
    with col2:
        # Date range filter
        available_years = sorted(data['sales_data']['year'].unique())
        selected_year = st.selectbox(
            "Select Year",
            options=available_years,
            index=len(available_years)-1 if available_years else 0,
            key="year_filter"
        )
    
    # Filter data based on selection
    filtered_data = data['sales_data'][data['sales_data']['year'] == selected_year]
    previous_year = selected_year - 1
    previous_data = data['sales_data'][data['sales_data']['year'] == previous_year]
    
    # Initialize metrics calculator
    metrics_calc = BusinessMetricsCalculator(data['sales_data'])
    
    # Calculate KPI metrics
    revenue_metrics = metrics_calc.calculate_revenue_metrics(
        current_year=selected_year,
        comparison_year=previous_year if not previous_data.empty else None
    )
    
    monthly_growth = metrics_calc.calculate_monthly_growth_trend(selected_year)
    avg_monthly_growth = monthly_growth.mean() if not monthly_growth.empty else 0
    
    experience_metrics = metrics_calc.calculate_customer_experience_metrics(
        reviews_df=data['reviews'],
        year=selected_year
    )
    
    # KPI Row
    st.markdown("### Key Performance Indicators")
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    with kpi_col1:
        trend_html = ""
        if 'revenue_growth_pct' in revenue_metrics:
            current_revenue = revenue_metrics['current_revenue']
            previous_revenue = revenue_metrics['comparison_revenue']
            trend_html = create_trend_indicator(current_revenue, previous_revenue)
        
        st.markdown(
            create_kpi_card(
                "Total Revenue", 
                revenue_metrics['current_revenue'], 
                trend_html,
                format_currency
            ), 
            unsafe_allow_html=True
        )
    
    with kpi_col2:
        st.markdown(
            create_kpi_card(
                "Monthly Growth", 
                avg_monthly_growth, 
                "",
                lambda x: f"{x:.2f}%"
            ), 
            unsafe_allow_html=True
        )
    
    with kpi_col3:
        trend_html = ""
        if 'aov_growth_pct' in revenue_metrics:
            current_aov = revenue_metrics['current_avg_order_value']
            previous_aov = revenue_metrics['comparison_avg_order_value']
            trend_html = create_trend_indicator(current_aov, previous_aov)
        
        st.markdown(
            create_kpi_card(
                "Average Order Value", 
                revenue_metrics['current_avg_order_value'], 
                trend_html,
                lambda x: f"${x:.2f}"
            ), 
            unsafe_allow_html=True
        )
    
    with kpi_col4:
        trend_html = ""
        if 'orders_growth_pct' in revenue_metrics:
            current_orders = revenue_metrics['current_orders']
            previous_orders = revenue_metrics['comparison_orders']
            trend_html = create_trend_indicator(current_orders, previous_orders)
        
        st.markdown(
            create_kpi_card(
                "Total Orders", 
                revenue_metrics['current_orders'], 
                trend_html,
                format_number
            ), 
            unsafe_allow_html=True
        )
    
    # Charts Grid (2x2)
    st.markdown("### Performance Analytics")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # Revenue trend chart
        revenue_fig = create_revenue_trend_chart(
            data['sales_data'], 
            selected_year, 
            previous_year if not previous_data.empty else None
        )
        st.plotly_chart(revenue_fig, use_container_width=True)
    
    with chart_col2:
        # Category chart
        category_fig = create_category_bar_chart(
            data['products'], 
            data['sales_data'], 
            selected_year
        )
        st.plotly_chart(category_fig, use_container_width=True)
    
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        # Geographic chart
        geo_fig = create_choropleth_map(
            data['customers'],
            data['orders'],
            data['sales_data'],
            selected_year
        )
        st.plotly_chart(geo_fig, use_container_width=True)
    
    with chart_col4:
        # Satisfaction chart
        satisfaction_fig = create_satisfaction_bar_chart(
            data['sales_data'],
            data['reviews'],
            selected_year
        )
        st.plotly_chart(satisfaction_fig, use_container_width=True)
    
    # Bottom Row Cards
    st.markdown("### Customer Experience")
    bottom_col1, bottom_col2 = st.columns(2)
    
    with bottom_col1:
        avg_delivery = experience_metrics.get('avg_delivery_days', 0)
        st.markdown(
            f"""
            <div class="bottom-card">
                <p class="kpi-label">Average Delivery Time</p>
                <p class="kpi-value">{avg_delivery:.1f} days</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with bottom_col2:
        avg_review = experience_metrics.get('avg_review_score', 0)
        stars = "★" * int(round(avg_review))
        st.markdown(
            f"""
            <div class="bottom-card">
                <p class="kpi-label">Average Review Score</p>
                <p class="review-score">{avg_review:.2f}</p>
                <p class="stars">{stars}</p>
            </div>
            """,
            unsafe_allow_html=True
        )


if __name__ == "__main__":
    main()