"""
Dashboard Utilities Module

Helper functions for the Streamlit dashboard including formatting,
styling, and chart creation utilities.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, Dict, Any


def format_currency(value: float) -> str:
    """
    Format currency values for display in dashboard.
    
    Args:
        value (float): Currency value to format
        
    Returns:
        str: Formatted currency string
    """
    if pd.isna(value) or value == 0:
        return "$0"
    
    if abs(value) >= 1_000_000:
        return f"${value/1_000_000:.1f}M"
    elif abs(value) >= 1_000:
        return f"${value/1_000:.0f}K"
    else:
        return f"${value:.0f}"


def format_number(value: float) -> str:
    """
    Format large numbers for display.
    
    Args:
        value (float): Number to format
        
    Returns:
        str: Formatted number string
    """
    if pd.isna(value) or value == 0:
        return "0"
    
    if abs(value) >= 1_000_000:
        return f"{value/1_000_000:.1f}M"
    elif abs(value) >= 1_000:
        return f"{value/1_000:.0f}K"
    else:
        return f"{value:.0f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format percentage values for display.
    
    Args:
        value (float): Percentage value to format
        decimals (int): Number of decimal places
        
    Returns:
        str: Formatted percentage string
    """
    if pd.isna(value):
        return "0.00%"
    return f"{value:.{decimals}f}%"


def create_trend_indicator(current_value: float, previous_value: float) -> str:
    """
    Create HTML trend indicator with arrow and color.
    
    Args:
        current_value (float): Current period value
        previous_value (float): Previous period value
        
    Returns:
        str: HTML string with trend indicator
    """
    if pd.isna(current_value) or pd.isna(previous_value) or previous_value == 0:
        return ""
    
    change = ((current_value - previous_value) / previous_value) * 100
    arrow = "↗" if change > 0 else "↘"
    color = "trend-positive" if change > 0 else "trend-negative"
    
    return f'<span class="{color}">{arrow} {change:.2f}%</span>'


def create_kpi_card(title: str, value: Any, trend_html: str = "", format_func: callable = str) -> str:
    """
    Create HTML for a KPI card with trend indicator.
    
    Args:
        title (str): Card title
        value (Any): Value to display
        trend_html (str): HTML for trend indicator
        format_func (callable): Function to format the value
        
    Returns:
        str: HTML string for KPI card
    """
    formatted_value = format_func(value) if callable(format_func) else str(value)
    
    return f"""
    <div class="kpi-container">
        <p class="kpi-label">{title}</p>
        <p class="kpi-value">{formatted_value}</p>
        <div class="kpi-trend">{trend_html}</div>
    </div>
    """


def get_dashboard_css() -> str:
    """
    Get CSS styles for the dashboard.
    
    Returns:
        str: CSS styles as string
    """
    return """
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            margin-bottom: 1rem;
        }
        .kpi-container {
            background-color: white;
            padding: 1.5rem;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            height: 140px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .kpi-value {
            font-size: 2rem;
            font-weight: bold;
            margin: 0;
        }
        .kpi-label {
            font-size: 0.9rem;
            color: #666;
            margin: 0;
        }
        .kpi-trend {
            font-size: 0.8rem;
            margin-top: 0.5rem;
        }
        .trend-positive {
            color: #28a745;
        }
        .trend-negative {
            color: #dc3545;
        }
        .chart-container {
            background-color: white;
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            height: 400px;
        }
        .bottom-card {
            background-color: white;
            padding: 1.5rem;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            height: 120px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            text-align: center;
        }
        .review-score {
            font-size: 2.5rem;
            font-weight: bold;
            color: #ffc107;
        }
        .stars {
            font-size: 1.5rem;
            color: #ffc107;
        }
        .stSelectbox > div > div {
            background-color: white;
        }
    </style>
    """


def create_revenue_trend_chart(sales_data: pd.DataFrame, current_year: int, 
                             previous_year: Optional[int] = None) -> go.Figure:
    """
    Create revenue trend line chart with current and previous period.
    
    Args:
        sales_data (pd.DataFrame): Sales dataset
        current_year (int): Current year for analysis
        previous_year (int, optional): Previous year for comparison
        
    Returns:
        go.Figure: Plotly figure object
    """
    fig = go.Figure()
    
    # Current year data
    current_data = sales_data[sales_data['year'] == current_year]
    if not current_data.empty:
        monthly_current = current_data.groupby('month')['price'].sum().reset_index()
        
        # Ensure all months are represented
        all_months = pd.DataFrame({'month': range(1, 13)})
        monthly_current = all_months.merge(monthly_current, on='month', how='left')
        monthly_current['price'].fillna(0, inplace=True)
        
        fig.add_trace(go.Scatter(
            x=monthly_current['month'],
            y=monthly_current['price'],
            mode='lines+markers',
            name=f'{current_year}',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=6),
            hovertemplate='Month: %{x}<br>Revenue: $%{y:,.0f}<extra></extra>'
        ))
    
    # Previous year data (dashed line)
    if previous_year:
        previous_data = sales_data[sales_data['year'] == previous_year]
        if not previous_data.empty:
            monthly_previous = previous_data.groupby('month')['price'].sum().reset_index()
            
            # Ensure all months are represented
            all_months = pd.DataFrame({'month': range(1, 13)})
            monthly_previous = all_months.merge(monthly_previous, on='month', how='left')
            monthly_previous['price'].fillna(0, inplace=True)
            
            fig.add_trace(go.Scatter(
                x=monthly_previous['month'],
                y=monthly_previous['price'],
                mode='lines',
                name=f'{previous_year}',
                line=dict(color='#7f7f7f', width=2, dash='dash'),
                hovertemplate='Month: %{x}<br>Revenue: $%{y:,.0f}<extra></extra>'
            ))
    
    fig.update_layout(
        title="Monthly Revenue Trend",
        xaxis_title="Month",
        yaxis_title="Revenue",
        hovermode='x unified',
        showlegend=True,
        height=350,
        margin=dict(l=0, r=0, t=40, b=0),
        plot_bgcolor='white',
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#f0f0f0',
            tickmode='linear',
            tick0=1,
            dtick=1,
            range=[0.5, 12.5]
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#f0f0f0',
            tickformat='$,.0s'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


def create_category_bar_chart(products_df: pd.DataFrame, sales_data: pd.DataFrame, 
                            year: int) -> go.Figure:
    """
    Create horizontal bar chart for top 10 product categories.
    
    Args:
        products_df (pd.DataFrame): Products dataset
        sales_data (pd.DataFrame): Sales dataset
        year (int): Year to analyze
        
    Returns:
        go.Figure: Plotly figure object
    """
    # Merge sales with products to get categories
    category_data = pd.merge(
        products_df[['product_id', 'product_category_name']],
        sales_data[sales_data['year'] == year][['product_id', 'price']],
        on='product_id'
    )
    
    if category_data.empty:
        # Return empty chart if no data
        fig = go.Figure()
        fig.update_layout(
            title="Top 10 Product Categories by Revenue",
            xaxis_title="Revenue",
            yaxis_title="Category",
            height=350,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        return fig
    
    # Calculate category totals and get top 10
    category_totals = category_data.groupby('product_category_name')['price'].sum().reset_index()
    category_totals = category_totals.sort_values('price', ascending=True).tail(10)
    
    # Create color values based on revenue (lighter for lower values)
    normalized_values = (category_totals['price'] - category_totals['price'].min()) / \
                       (category_totals['price'].max() - category_totals['price'].min())
    colors = [f'rgba(31, 119, 180, {0.4 + 0.6 * val})' for val in normalized_values]
    
    fig = go.Figure(data=go.Bar(
        x=category_totals['price'],
        y=[cat.replace('_', ' ').title() for cat in category_totals['product_category_name']],
        orientation='h',
        marker_color=colors,
        hovertemplate='Category: %{y}<br>Revenue: $%{x:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Top 10 Product Categories by Revenue",
        xaxis_title="Revenue",
        yaxis_title="Category",
        height=350,
        margin=dict(l=0, r=0, t=40, b=0),
        xaxis=dict(tickformat='$,.0s'),
        showlegend=False
    )
    
    return fig


def create_choropleth_map(customers_df: pd.DataFrame, orders_df: pd.DataFrame, 
                         sales_data: pd.DataFrame, year: int) -> go.Figure:
    """
    Create US choropleth map for revenue by state.
    
    Args:
        customers_df (pd.DataFrame): Customers dataset
        orders_df (pd.DataFrame): Orders dataset
        sales_data (pd.DataFrame): Sales dataset
        year (int): Year to analyze
        
    Returns:
        go.Figure: Plotly figure object
    """
    # Get sales data for the year
    year_data = sales_data[sales_data['year'] == year]
    
    if year_data.empty:
        # Return empty map if no data
        fig = go.Figure(data=go.Choropleth(
            locations=[],
            z=[],
            locationmode='USA-states',
        ))
        fig.update_layout(
            title="Revenue by State",
            geo_scope='usa',
            height=350,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        return fig
    
    # Merge to get customer state info
    sales_with_customers = pd.merge(
        year_data[['order_id', 'price']],
        orders_df[['order_id', 'customer_id']],
        on='order_id'
    )
    
    geographic_data = pd.merge(
        sales_with_customers,
        customers_df[['customer_id', 'customer_state']],
        on='customer_id'
    )
    
    # Aggregate by state
    state_revenue = geographic_data.groupby('customer_state')['price'].sum().reset_index()
    
    fig = go.Figure(data=go.Choropleth(
        locations=state_revenue['customer_state'],
        z=state_revenue['price'],
        locationmode='USA-states',
        colorscale='Blues',
        hovertemplate='State: %{location}<br>Revenue: $%{z:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Revenue by State",
        geo_scope='usa',
        height=350,
        margin=dict(l=0, r=0, t=40, b=0),
        geo=dict(bgcolor='rgba(0,0,0,0)'),
        coloraxis_colorbar=dict(
            title="Revenue",
            tickformat='$,.0s'
        )
    )
    
    return fig


def create_satisfaction_bar_chart(sales_data: pd.DataFrame, reviews_df: pd.DataFrame, 
                                year: int) -> go.Figure:
    """
    Create bar chart showing satisfaction vs delivery time.
    
    Args:
        sales_data (pd.DataFrame): Sales dataset with delivery metrics
        reviews_df (pd.DataFrame): Reviews dataset
        year (int): Year to analyze
        
    Returns:
        go.Figure: Plotly figure object
    """
    # Get year data with delivery metrics
    year_data = sales_data[sales_data['year'] == year]
    
    if year_data.empty:
        # Return empty chart if no data
        fig = go.Figure()
        fig.update_layout(
            title="Customer Satisfaction vs Delivery Time",
            xaxis_title="Delivery Time",
            yaxis_title="Average Review Score",
            height=350,
            margin=dict(l=0, r=0, t=40, b=0),
            yaxis=dict(range=[0, 5])
        )
        return fig
    
    # Merge with reviews
    satisfaction_data = pd.merge(
        year_data[['order_id', 'delivery_speed_category']],
        reviews_df[['order_id', 'review_score']],
        on='order_id'
    )
    
    if satisfaction_data.empty:
        # Return empty chart if no review data
        fig = go.Figure()
        fig.update_layout(
            title="Customer Satisfaction vs Delivery Time",
            xaxis_title="Delivery Time",
            yaxis_title="Average Review Score",
            height=350,
            margin=dict(l=0, r=0, t=40, b=0),
            yaxis=dict(range=[0, 5])
        )
        return fig
    
    # Calculate average satisfaction by delivery speed
    avg_satisfaction = satisfaction_data.groupby('delivery_speed_category')['review_score'].mean().reset_index()
    
    # Define order for categories and ensure all categories are present
    category_order = ['1-3 days', '4-7 days', '8+ days']
    
    # Create a complete dataframe with all categories
    complete_categories = pd.DataFrame({'delivery_speed_category': category_order})
    avg_satisfaction = complete_categories.merge(avg_satisfaction, on='delivery_speed_category', how='left')
    avg_satisfaction['review_score'].fillna(0, inplace=True)
    
    # Create color mapping based on score (red-yellow-green gradient)
    colors = []
    for score in avg_satisfaction['review_score']:
        if score >= 4.0:
            colors.append('#28a745')  # Green
        elif score >= 3.0:
            colors.append('#ffc107')  # Yellow
        else:
            colors.append('#dc3545')  # Red
    
    fig = go.Figure(data=go.Bar(
        x=avg_satisfaction['delivery_speed_category'],
        y=avg_satisfaction['review_score'],
        marker_color=colors,
        hovertemplate='Delivery Time: %{x}<br>Avg Review Score: %{y:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Customer Satisfaction vs Delivery Time",
        xaxis_title="Delivery Time",
        yaxis_title="Average Review Score",
        height=350,
        margin=dict(l=0, r=0, t=40, b=0),
        yaxis=dict(range=[0, 5]),
        showlegend=False
    )
    
    return fig