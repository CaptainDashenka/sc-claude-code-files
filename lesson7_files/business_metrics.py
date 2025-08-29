"""
Business Metrics Calculation Module for E-commerce Analysis

This module contains functions to calculate key business metrics including revenue,
growth rates, customer metrics, product performance, and geographic analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns


class BusinessMetricsCalculator:
    """
    A class to calculate various business metrics for e-commerce analysis.
    """
    
    def __init__(self, sales_data: pd.DataFrame):
        """
        Initialize with sales data.
        
        Args:
            sales_data (pd.DataFrame): Processed sales dataset
        """
        self.sales_data = sales_data.copy()
    
    def calculate_revenue_metrics(self, current_year: int, 
                                 comparison_year: Optional[int] = None) -> Dict:
        """
        Calculate revenue metrics for specified years.
        
        Args:
            current_year (int): Year to analyze
            comparison_year (int, optional): Year to compare against
            
        Returns:
            Dict: Revenue metrics including totals and growth rates
        """
        current_data = self.sales_data[self.sales_data['year'] == current_year]
        current_revenue = current_data['price'].sum()
        
        metrics = {
            'current_year': current_year,
            'current_revenue': current_revenue,
            'current_orders': current_data['order_id'].nunique(),
            'current_avg_order_value': current_data.groupby('order_id')['price'].sum().mean()
        }
        
        if comparison_year:
            comparison_data = self.sales_data[self.sales_data['year'] == comparison_year]
            comparison_revenue = comparison_data['price'].sum()
            comparison_orders = comparison_data['order_id'].nunique()
            comparison_aov = comparison_data.groupby('order_id')['price'].sum().mean()
            
            # Calculate growth rates
            revenue_growth = ((current_revenue - comparison_revenue) / comparison_revenue) * 100
            orders_growth = ((metrics['current_orders'] - comparison_orders) / comparison_orders) * 100
            aov_growth = ((metrics['current_avg_order_value'] - comparison_aov) / comparison_aov) * 100
            
            metrics.update({
                'comparison_year': comparison_year,
                'comparison_revenue': comparison_revenue,
                'comparison_orders': comparison_orders,
                'comparison_avg_order_value': comparison_aov,
                'revenue_growth_pct': revenue_growth,
                'orders_growth_pct': orders_growth,
                'aov_growth_pct': aov_growth
            })
        
        return metrics
    
    def calculate_monthly_growth_trend(self, year: int) -> pd.Series:
        """
        Calculate month-over-month growth rates for a specific year.
        
        Args:
            year (int): Year to analyze
            
        Returns:
            pd.Series: Monthly growth rates
        """
        year_data = self.sales_data[self.sales_data['year'] == year]
        monthly_revenue = year_data.groupby('month')['price'].sum()
        monthly_growth = monthly_revenue.pct_change() * 100
        
        return monthly_growth
    
    def get_product_category_performance(self, products_df: pd.DataFrame, 
                                       year: Optional[int] = None) -> pd.DataFrame:
        """
        Calculate product category performance metrics.
        
        Args:
            products_df (pd.DataFrame): Products dataset
            year (int, optional): Specific year to analyze
            
        Returns:
            pd.DataFrame: Category performance metrics
        """
        analysis_data = self.sales_data.copy()
        
        if year:
            analysis_data = analysis_data[analysis_data['year'] == year]
        
        # Merge with products to get categories
        category_data = pd.merge(
            left=products_df[['product_id', 'product_category_name']],
            right=analysis_data[['product_id', 'price', 'order_id']],
            on='product_id',
            how='inner'
        )
        
        # Calculate category metrics
        category_metrics = category_data.groupby('product_category_name').agg({
            'price': ['sum', 'mean', 'count'],
            'order_id': 'nunique'
        }).round(2)
        
        # Flatten column names
        category_metrics.columns = ['total_revenue', 'avg_item_price', 'total_items', 'unique_orders']
        category_metrics = category_metrics.sort_values('total_revenue', ascending=False)
        
        # Calculate percentages
        total_revenue = category_metrics['total_revenue'].sum()
        category_metrics['revenue_share_pct'] = (category_metrics['total_revenue'] / total_revenue * 100).round(2)
        
        return category_metrics.reset_index()
    
    def get_geographic_performance(self, orders_df: pd.DataFrame, 
                                  customers_df: pd.DataFrame,
                                  year: Optional[int] = None) -> pd.DataFrame:
        """
        Calculate geographic performance metrics by state.
        
        Args:
            orders_df (pd.DataFrame): Orders dataset
            customers_df (pd.DataFrame): Customers dataset
            year (int, optional): Specific year to analyze
            
        Returns:
            pd.DataFrame: Geographic performance metrics
        """
        analysis_data = self.sales_data.copy()
        
        if year:
            analysis_data = analysis_data[analysis_data['year'] == year]
        
        # Get customer state information
        sales_with_customers = pd.merge(
            left=analysis_data[['order_id', 'price']],
            right=orders_df[['order_id', 'customer_id']],
            on='order_id',
            how='inner'
        )
        
        geographic_data = pd.merge(
            left=sales_with_customers,
            right=customers_df[['customer_id', 'customer_state', 'customer_city']],
            on='customer_id',
            how='inner'
        )
        
        # Calculate state-level metrics
        state_metrics = geographic_data.groupby('customer_state').agg({
            'price': ['sum', 'mean', 'count'],
            'order_id': 'nunique',
            'customer_id': 'nunique'
        }).round(2)
        
        # Flatten column names
        state_metrics.columns = ['total_revenue', 'avg_order_value', 'total_items', 
                               'unique_orders', 'unique_customers']
        state_metrics = state_metrics.sort_values('total_revenue', ascending=False)
        
        return state_metrics.reset_index()
    
    def calculate_customer_experience_metrics(self, reviews_df: pd.DataFrame,
                                            year: Optional[int] = None) -> Dict:
        """
        Calculate customer experience metrics including delivery and satisfaction.
        
        Args:
            reviews_df (pd.DataFrame): Reviews dataset
            year (int, optional): Specific year to analyze
            
        Returns:
            Dict: Customer experience metrics
        """
        analysis_data = self.sales_data.copy()
        
        if year:
            analysis_data = analysis_data[analysis_data['year'] == year]
        
        # Add delivery metrics if not already present
        if 'delivery_days' not in analysis_data.columns:
            from data_loader import add_delivery_metrics
            analysis_data = add_delivery_metrics(analysis_data)
        
        # Merge with reviews
        experience_data = pd.merge(
            left=analysis_data[['order_id', 'delivery_days', 'delivery_speed_category']],
            right=reviews_df[['order_id', 'review_score']],
            on='order_id',
            how='inner'
        )
        
        # Remove duplicates (one record per order)
        experience_data = experience_data.drop_duplicates(subset=['order_id'])
        
        # Calculate metrics
        metrics = {
            'avg_delivery_days': experience_data['delivery_days'].mean(),
            'median_delivery_days': experience_data['delivery_days'].median(),
            'avg_review_score': experience_data['review_score'].mean(),
            'review_score_distribution': experience_data['review_score'].value_counts(normalize=True).to_dict(),
            'delivery_speed_distribution': experience_data['delivery_speed_category'].value_counts(normalize=True).to_dict()
        }
        
        # Calculate average review score by delivery speed
        delivery_satisfaction = experience_data.groupby('delivery_speed_category')['review_score'].mean().to_dict()
        metrics['avg_review_by_delivery_speed'] = delivery_satisfaction
        
        return metrics
    
    def get_order_status_distribution(self, orders_df: pd.DataFrame, 
                                    year: Optional[int] = None) -> pd.Series:
        """
        Get order status distribution for specified year.
        
        Args:
            orders_df (pd.DataFrame): Orders dataset with status information
            year (int, optional): Specific year to analyze
            
        Returns:
            pd.Series: Order status distribution
        """
        analysis_data = orders_df.copy()
        
        if year:
            # Ensure year column exists
            if 'year' not in analysis_data.columns:
                analysis_data['year'] = pd.to_datetime(analysis_data['order_purchase_timestamp']).dt.year
            analysis_data = analysis_data[analysis_data['year'] == year]
        
        status_dist = analysis_data['order_status'].value_counts(normalize=True) * 100
        return status_dist.round(2)


class MetricsVisualizer:
    """
    A class to create visualizations for business metrics.
    """
    
    def __init__(self, color_palette: str = 'viridis'):
        """
        Initialize with color scheme.
        
        Args:
            color_palette (str): Color palette for visualizations
        """
        self.color_palette = color_palette
        plt.style.use('default')
    
    def plot_monthly_revenue_trend(self, monthly_data: pd.DataFrame, 
                                  year: int, title_suffix: str = "") -> None:
        """
        Create monthly revenue trend plot.
        
        Args:
            monthly_data (pd.DataFrame): Monthly aggregated data
            year (int): Year being analyzed
            title_suffix (str): Additional text for title
        """
        plt.figure(figsize=(12, 6))
        plt.plot(monthly_data['month'], monthly_data['price'], 
                marker='o', linewidth=2, markersize=8, color='#1f77b4')
        plt.title(f'Monthly Revenue Trend - {year} {title_suffix}', fontsize=16, fontweight='bold')
        plt.xlabel('Month', fontsize=12)
        plt.ylabel('Revenue ($)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.xticks(range(1, 13))
        
        # Format y-axis to show values in thousands/millions
        ax = plt.gca()
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K' if x < 1000000 else f'${x/1000000:.1f}M'))
        
        plt.tight_layout()
        plt.show()
    
    def plot_category_performance(self, category_data: pd.DataFrame, 
                                 year: Optional[int] = None) -> None:
        """
        Create horizontal bar chart for category performance.
        
        Args:
            category_data (pd.DataFrame): Category performance data
            year (int, optional): Year being analyzed for title
        """
        plt.figure(figsize=(12, 8))
        
        # Sort by revenue and take top categories
        top_categories = category_data.head(10)
        
        bars = plt.barh(range(len(top_categories)), top_categories['total_revenue'], 
                       color=plt.cm.Set3(range(len(top_categories))))
        
        year_text = f" - {year}" if year else ""
        plt.title(f'Revenue by Product Category{year_text}', fontsize=16, fontweight='bold')
        plt.xlabel('Total Revenue ($)', fontsize=12)
        plt.ylabel('Product Category', fontsize=12)
        
        # Set category labels
        plt.yticks(range(len(top_categories)), 
                  [cat.replace('_', ' ').title() for cat in top_categories['product_category_name']])
        
        # Add value labels on bars
        for i, bar in enumerate(bars):
            width = bar.get_width()
            plt.text(width, bar.get_y() + bar.get_height()/2, 
                    f'${width/1000:.0f}K', ha='left', va='center', fontweight='bold')
        
        plt.tight_layout()
        plt.show()
    
    def plot_geographic_choropleth(self, geographic_data: pd.DataFrame, 
                                  year: Optional[int] = None) -> None:
        """
        Create choropleth map for geographic performance.
        
        Args:
            geographic_data (pd.DataFrame): Geographic performance data
            year (int, optional): Year being analyzed for title
        """
        year_text = f" - {year}" if year else ""
        
        fig = px.choropleth(
            geographic_data,
            locations='customer_state',
            color='total_revenue',
            locationmode='USA-states',
            scope='usa',
            title=f'Revenue by State{year_text}',
            color_continuous_scale='Reds',
            labels={'total_revenue': 'Total Revenue ($)'}
        )
        
        fig.update_layout(
            title_font_size=16,
            geo=dict(bgcolor='rgba(0,0,0,0)')
        )
        
        fig.show()
    
    def plot_review_score_distribution(self, review_data: pd.Series, 
                                     year: Optional[int] = None) -> None:
        """
        Create horizontal bar chart for review score distribution.
        
        Args:
            review_data (pd.Series): Review score distribution data
            year (int, optional): Year being analyzed for title
        """
        plt.figure(figsize=(10, 6))
        
        # Sort by review score
        sorted_data = review_data.sort_index()
        
        bars = plt.barh(range(len(sorted_data)), sorted_data.values, 
                       color=plt.cm.RdYlGn(np.linspace(0.2, 1, len(sorted_data))))
        
        year_text = f" - {year}" if year else ""
        plt.title(f'Review Score Distribution{year_text}', fontsize=16, fontweight='bold')
        plt.xlabel('Proportion of Reviews', fontsize=12)
        plt.ylabel('Review Score', fontsize=12)
        
        # Set score labels
        plt.yticks(range(len(sorted_data)), sorted_data.index)
        
        # Add percentage labels on bars
        for i, bar in enumerate(bars):
            width = bar.get_width()
            plt.text(width, bar.get_y() + bar.get_height()/2, 
                    f'{width:.1%}', ha='left', va='center', fontweight='bold')
        
        plt.tight_layout()
        plt.show()


def print_metrics_summary(revenue_metrics: Dict, monthly_growth: pd.Series, 
                         experience_metrics: Dict, year: int) -> None:
    """
    Print a formatted summary of key business metrics.
    
    Args:
        revenue_metrics (Dict): Revenue metrics dictionary
        monthly_growth (pd.Series): Monthly growth data
        experience_metrics (Dict): Customer experience metrics
        year (int): Year being analyzed
    """
    print("="*60)
    print(f"BUSINESS METRICS SUMMARY - {year}")
    print("="*60)
    print()
    
    # Revenue Metrics
    print("REVENUE PERFORMANCE:")
    print(f"  Total Revenue: ${revenue_metrics['current_revenue']:,.2f}")
    print(f"  Total Orders: {revenue_metrics['current_orders']:,}")
    print(f"  Average Order Value: ${revenue_metrics['current_avg_order_value']:.2f}")
    
    if 'revenue_growth_pct' in revenue_metrics:
        print(f"  Revenue Growth vs {revenue_metrics['comparison_year']}: {revenue_metrics['revenue_growth_pct']:.2f}%")
        print(f"  Orders Growth vs {revenue_metrics['comparison_year']}: {revenue_metrics['orders_growth_pct']:.2f}%")
        print(f"  AOV Growth vs {revenue_metrics['comparison_year']}: {revenue_metrics['aov_growth_pct']:.2f}%")
    
    print()
    
    # Growth Trends
    print("GROWTH TRENDS:")
    avg_monthly_growth = monthly_growth.mean()
    print(f"  Average Monthly Growth: {avg_monthly_growth:.2f}%")
    best_month = monthly_growth.idxmax()
    worst_month = monthly_growth.idxmin()
    print(f"  Best Month: {best_month} ({monthly_growth[best_month]:.2f}%)")
    print(f"  Worst Month: {worst_month} ({monthly_growth[worst_month]:.2f}%)")
    print()
    
    # Customer Experience
    print("CUSTOMER EXPERIENCE:")
    print(f"  Average Delivery Time: {experience_metrics['avg_delivery_days']:.1f} days")
    print(f"  Average Review Score: {experience_metrics['avg_review_score']:.2f}/5")
    
    # Delivery speed satisfaction
    if 'avg_review_by_delivery_speed' in experience_metrics:
        print("  Review Scores by Delivery Speed:")
        for speed, score in experience_metrics['avg_review_by_delivery_speed'].items():
            print(f"    {speed}: {score:.2f}/5")
    
    print()
    print("="*60)