# E-commerce Business Performance Analysis

A comprehensive, configurable analysis framework for e-commerce business performance metrics including revenue trends, product categories, geographic distribution, and customer experience.

## Project Structure

```
├── EDA_Refactored.ipynb          # Main analysis notebook
├── data_loader.py                # Data loading and preprocessing
├── business_metrics.py           # Business metrics calculations
├── requirements.txt              # Python dependencies
├── README.md                     # This file
└── ecommerce_data/              # Data directory
    ├── orders_dataset.csv
    ├── order_items_dataset.csv
    ├── products_dataset.csv
    ├── customers_dataset.csv
    └── order_reviews_dataset.csv
```

## Features

### Configurable Analysis Framework
- **Flexible Date Ranges:** Analyze any year, month, or custom date range
- **Modular Design:** Reusable functions for different datasets and time periods
- **Scalable Architecture:** Easy to extend with new metrics and visualizations

### Business Metrics Included
- **Revenue Analysis:** Total revenue, growth rates, average order value
- **Product Performance:** Category analysis, market concentration
- **Geographic Distribution:** State-level performance analysis
- **Customer Experience:** Delivery times, satisfaction scores, operational metrics

### Enhanced Visualizations
- Monthly revenue trend charts with proper formatting
- Product category performance bar charts
- Geographic choropleth maps using Plotly
- Customer satisfaction distribution charts
- Professional styling with business-oriented color schemes

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Analysis Parameters

Open `EDA_Refactored.ipynb` and modify the configuration section:

```python
# ANALYSIS CONFIGURATION
ANALYSIS_YEAR = 2023        # Primary analysis year
COMPARISO_YEAR = 2022       # Comparison year for growth
START_MONTH = None          # Optional: specific month range
END_MONTH = None            # Optional: specific month range
DATA_PATH = 'ecommerce_data' # Path to data files
```

### 3. Run the Analysis

Execute all cells in the notebook or run specific sections:
- Revenue Performance Analysis
- Product Category Analysis  
- Geographic Performance Analysis
- Customer Experience Analysis

## Module Documentation

### data_loader.py

Handles all data loading and preprocessing operations:

```python
from data_loader import (
    load_ecommerce_datasets,     # Load all CSV files
    preprocess_orders_data,      # Add date components
    create_sales_dataset,        # Merge orders and items
    filter_data_by_date_range,   # Apply date filters
    add_delivery_metrics         # Calculate delivery times
)

# Example usage
datasets = load_ecommerce_datasets('ecommerce_data')
sales_data = create_sales_dataset(datasets['orders'], datasets['order_items'])
```

### business_metrics.py

Provides business metrics calculation and visualization classes:

```python
from business_metrics import (
    BusinessMetricsCalculator,   # Main metrics class
    MetricsVisualizer,          # Visualization class
    print_metrics_summary       # Summary reports
)

# Example usage
calc = BusinessMetricsCalculator(sales_data)
revenue_metrics = calc.calculate_revenue_metrics(2023, 2022)
visualizer = MetricsVisualizer()
visualizer.plot_monthly_revenue_trend(monthly_data, 2023)
```

## Key Analysis Sections

### 1. Revenue Performance Analysis
- Year-over-year revenue comparison
- Monthly growth trends and seasonality
- Average order value analysis
- Order volume trends

### 2. Product Category Analysis
- Revenue by product category
- Market concentration analysis
- Category performance rankings
- Revenue share distribution

### 3. Geographic Performance Analysis
- State-level revenue distribution
- Geographic concentration metrics
- Choropleth map visualizations
- Market penetration analysis

### 4. Customer Experience Analysis
- Delivery time performance
- Customer satisfaction scores
- Review score distribution
- Correlation between delivery speed and satisfaction

## Customization Examples

### Analyze Specific Quarter
```python
ANALYSIS_YEAR = 2023
START_MONTH = 1
END_MONTH = 3  # Q1 analysis
```

### Compare Different Years
```python
ANALYSIS_YEAR = 2023
COMPARISO_YEAR = 2021  # Skip 2022 comparison
```

### Filter by Order Status
```python
ORDER_STATUS_FILTER = None  # Include all orders
# or
ORDER_STATUS_FILTER = 'shipped'  # Only shipped orders
```

## Business Insights Generated

The analysis automatically generates insights on:
- Revenue growth patterns and trends
- Product category performance leaders
- Geographic market concentration
- Customer satisfaction drivers
- Operational efficiency metrics
- Seasonal patterns and opportunities

## Data Requirements

The analysis expects the following CSV files in the `ecommerce_data/` directory:

1. **orders_dataset.csv** - Order information with timestamps and status
2. **order_items_dataset.csv** - Individual items within orders with pricing
3. **products_dataset.csv** - Product catalog with categories
4. **customers_dataset.csv** - Customer geographic information
5. **order_reviews_dataset.csv** - Customer reviews and satisfaction scores

## Performance Considerations

- **Memory Usage:** Large datasets may require additional memory
- **Processing Time:** Geographic visualizations may take longer to render
- **Data Quality:** Missing values are handled gracefully with warnings

## Extending the Analysis

### Adding New Metrics
1. Add calculation methods to `BusinessMetricsCalculator` class
2. Create corresponding visualization methods in `MetricsVisualizer`
3. Update the notebook with new analysis sections

### Supporting New Data Sources
1. Extend `load_ecommerce_datasets()` function
2. Update preprocessing functions for new data formats
3. Modify merge operations in `create_sales_dataset()`

## Troubleshooting

### Common Issues
- **File not found errors:** Check data file paths and names
- **Date parsing errors:** Verify timestamp column formats
- **Memory errors:** Consider analyzing smaller date ranges
- **Visualization errors:** Ensure Plotly is properly installed

### Performance Tips
- Use specific date ranges for large datasets
- Filter by order status to reduce data size
- Consider sampling for initial exploratory analysis

## Contributing

To contribute to this analysis framework:
1. Follow the existing code structure and naming conventions
2. Add comprehensive docstrings to new functions
3. Test with different date ranges and data scenarios
4. Update documentation for new features

## License

This analysis framework is designed for educational and business analysis purposes.