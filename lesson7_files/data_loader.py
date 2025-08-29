"""
Data Loading and Processing Module for E-commerce Analysis

This module handles data loading, cleaning, and preprocessing for e-commerce datasets.
It provides functions to load various CSV files and perform common data transformations.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


def load_ecommerce_datasets(data_path: str = 'ecommerce_data') -> Dict[str, pd.DataFrame]:
    """
    Load all e-commerce datasets from CSV files.
    
    Args:
        data_path (str): Path to the directory containing CSV files
        
    Returns:
        Dict[str, pd.DataFrame]: Dictionary containing all loaded datasets
    """
    datasets = {}
    
    # Define file mappings
    files = {
        'orders': 'orders_dataset.csv',
        'order_items': 'order_items_dataset.csv', 
        'products': 'products_dataset.csv',
        'customers': 'customers_dataset.csv',
        'reviews': 'order_reviews_dataset.csv'
    }
    
    # Load each dataset
    for key, filename in files.items():
        try:
            file_path = f"{data_path}/{filename}"
            datasets[key] = pd.read_csv(file_path)
            print(f"Loaded {key}: {datasets[key].shape}")
        except FileNotFoundError:
            print(f"Warning: Could not find {filename}")
        except Exception as e:
            print(f"Error loading {filename}: {str(e)}")
    
    return datasets


def preprocess_orders_data(orders: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess orders dataset by converting timestamps and extracting date components.
    
    Args:
        orders (pd.DataFrame): Raw orders dataframe
        
    Returns:
        pd.DataFrame: Processed orders dataframe
    """
    orders_processed = orders.copy()
    
    # Convert timestamp columns to datetime
    timestamp_cols = [
        'order_purchase_timestamp', 
        'order_approved_at',
        'order_delivered_carrier_date',
        'order_delivered_customer_date',
        'order_estimated_delivery_date'
    ]
    
    for col in timestamp_cols:
        if col in orders_processed.columns:
            orders_processed[col] = pd.to_datetime(orders_processed[col])
    
    # Extract date components from purchase timestamp
    if 'order_purchase_timestamp' in orders_processed.columns:
        orders_processed['year'] = orders_processed['order_purchase_timestamp'].dt.year
        orders_processed['month'] = orders_processed['order_purchase_timestamp'].dt.month
        orders_processed['quarter'] = orders_processed['order_purchase_timestamp'].dt.quarter
        orders_processed['day_of_week'] = orders_processed['order_purchase_timestamp'].dt.day_name()
    
    return orders_processed


def create_sales_dataset(orders: pd.DataFrame, order_items: pd.DataFrame, 
                        order_status_filter: str = 'delivered') -> pd.DataFrame:
    """
    Create a unified sales dataset by merging orders and order items.
    
    Args:
        orders (pd.DataFrame): Orders dataframe
        order_items (pd.DataFrame): Order items dataframe
        order_status_filter (str): Filter for order status (default: 'delivered')
        
    Returns:
        pd.DataFrame: Merged sales dataset
    """
    # Select relevant columns from each dataset
    orders_cols = [
        'order_id', 'customer_id', 'order_status', 
        'order_purchase_timestamp', 'order_delivered_customer_date',
        'year', 'month', 'quarter', 'day_of_week'
    ]
    
    items_cols = [
        'order_id', 'order_item_id', 'product_id', 'seller_id', 
        'price', 'freight_value'
    ]
    
    # Merge datasets
    sales_data = pd.merge(
        left=order_items[items_cols],
        right=orders[orders_cols],
        on='order_id',
        how='inner'
    )
    
    # Filter by order status if specified
    if order_status_filter:
        sales_data = sales_data[sales_data['order_status'] == order_status_filter]
    
    # Calculate total item value
    sales_data['total_item_value'] = sales_data['price'] + sales_data['freight_value']
    
    return sales_data


def filter_data_by_date_range(df: pd.DataFrame, 
                             start_year: Optional[int] = None,
                             end_year: Optional[int] = None,
                             start_month: Optional[int] = None,
                             end_month: Optional[int] = None,
                             date_column: str = 'order_purchase_timestamp') -> pd.DataFrame:
    """
    Filter dataframe by date range using year and month parameters.
    
    Args:
        df (pd.DataFrame): Input dataframe
        start_year (int, optional): Starting year for filter
        end_year (int, optional): Ending year for filter  
        start_month (int, optional): Starting month for filter
        end_month (int, optional): Ending month for filter
        date_column (str): Name of the date column to filter on
        
    Returns:
        pd.DataFrame: Filtered dataframe
    """
    filtered_df = df.copy()
    
    if date_column not in filtered_df.columns:
        print(f"Warning: Column {date_column} not found in dataframe")
        return filtered_df
    
    # Ensure date column is datetime
    if not pd.api.types.is_datetime64_any_dtype(filtered_df[date_column]):
        filtered_df[date_column] = pd.to_datetime(filtered_df[date_column])
    
    # Apply year filters
    if start_year is not None:
        filtered_df = filtered_df[filtered_df[date_column].dt.year >= start_year]
    
    if end_year is not None:
        filtered_df = filtered_df[filtered_df[date_column].dt.year <= end_year]
    
    # Apply month filters (only if both start and end year are the same)
    if (start_month is not None and end_month is not None and 
        start_year is not None and end_year is not None and 
        start_year == end_year):
        filtered_df = filtered_df[
            (filtered_df[date_column].dt.month >= start_month) &
            (filtered_df[date_column].dt.month <= end_month)
        ]
    
    return filtered_df


def add_delivery_metrics(sales_data: pd.DataFrame) -> pd.DataFrame:
    """
    Add delivery time and speed category metrics to sales data.
    
    Args:
        sales_data (pd.DataFrame): Sales dataset with delivery dates
        
    Returns:
        pd.DataFrame: Sales data with delivery metrics added
    """
    enhanced_data = sales_data.copy()
    
    # Ensure datetime columns
    if 'order_delivered_customer_date' in enhanced_data.columns:
        enhanced_data['order_delivered_customer_date'] = pd.to_datetime(
            enhanced_data['order_delivered_customer_date']
        )
    
    if 'order_purchase_timestamp' in enhanced_data.columns:
        enhanced_data['order_purchase_timestamp'] = pd.to_datetime(
            enhanced_data['order_purchase_timestamp']
        )
    
    # Calculate delivery time in days
    if ('order_delivered_customer_date' in enhanced_data.columns and 
        'order_purchase_timestamp' in enhanced_data.columns):
        
        enhanced_data['delivery_days'] = (
            enhanced_data['order_delivered_customer_date'] - 
            enhanced_data['order_purchase_timestamp']
        ).dt.days
        
        # Categorize delivery speed
        def categorize_delivery_speed(days):
            if pd.isna(days):
                return 'Unknown'
            elif days <= 3:
                return '1-3 days'
            elif days <= 7:
                return '4-7 days'
            else:
                return '8+ days'
        
        enhanced_data['delivery_speed_category'] = enhanced_data['delivery_days'].apply(
            categorize_delivery_speed
        )
    
    return enhanced_data


def get_data_summary(datasets: Dict[str, pd.DataFrame]) -> None:
    """
    Print summary information about loaded datasets.
    
    Args:
        datasets (Dict[str, pd.DataFrame]): Dictionary of datasets to summarize
    """
    print("=== E-COMMERCE DATASETS SUMMARY ===\n")
    
    for name, df in datasets.items():
        print(f"{name.upper()} DATASET:")
        print(f"  Shape: {df.shape}")
        print(f"  Columns: {list(df.columns)}")
        
        # Show date range for time-based datasets
        if name == 'orders' and 'order_purchase_timestamp' in df.columns:
            df_temp = df.copy()
            df_temp['order_purchase_timestamp'] = pd.to_datetime(df_temp['order_purchase_timestamp'])
            print(f"  Date range: {df_temp['order_purchase_timestamp'].min()} to {df_temp['order_purchase_timestamp'].max()}")
        
        print(f"  Missing values: {df.isnull().sum().sum()}")
        print("")