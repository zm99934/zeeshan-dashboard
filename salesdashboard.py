import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px # Plotly for more interactive charts in web apps

# --- 1. Data Loading and Preparation (Replace with your actual data loading) ---
# Using a dummy mergedata for demonstration
np.random.seed(42)
# CORRECTED: Ensure all arrays have the same length (e.g., 500 elements)
num_records = 500 # Define a variable for the number of records
mergedata = pd.DataFrame({
    'Order Number': np.arange(100, 100 + num_records), # Now creates 500 elements
    'Category': np.random.choice([
        'Very Long Electronics Category Name',
        'Peripherals & Accessories',
        'Fiction & Non-Fiction Books',
        'Apparel & Footwear',
        'Home Goods & Decor',
        'Sports & Outdoors'
    ], num_records), # Uses num_records
    'Country': np.random.choice(['USA', 'Canada', 'Mexico', 'Germany', 'Japan', 'France', 'UK', 'Australia'], num_records), # Uses num_records
    'TotalRevenue': np.random.rand(num_records) * 1000 + 50, # Uses num_records
    'Quantity': np.random.randint(1, 10, num_records), # Added Quantity for scatter plot
    'Order Date': pd.to_datetime(pd.date_range(start='2023-01-01', periods=num_records, freq='D')) # Uses num_records
})

# --- 2. Streamlit App Layout ---

st.set_page_config(layout="wide") # Use wide layout for better dashboard space

st.title("Sales Performance Dashboard") # Main title of your dashboard

# Sidebar for filters
st.sidebar.header("Filter Options")

# Get unique countries for the dropdown
unique_countries = sorted(mergedata['Country'].unique().tolist())
country_options = ["All Countries"] + unique_countries

# Create a dropdown in the sidebar
selected_country = st.sidebar.selectbox(
    "Select a Country:",
    options=country_options,
    index=0 # Default to "All Countries"
)

# --- 3. Data Filtering based on selection ---
if selected_country == "All Countries":
    df_filtered = mergedata.copy()
    chart_title_country_suffix = "All Countries"
else:
    df_filtered = mergedata[mergedata['Country'] == selected_country].copy()
    chart_title_country_suffix = selected_country

# --- 4. Data Aggregation for the Charts ---
if df_filtered.empty:
    st.warning(f"No data available for {selected_country} with the current filters.")
else:
    # --- Data for Bar Chart ---
    plot_data_bar = df_filtered.groupby("Category").agg(
        TotalOrder=('Order Number', 'count'),
        TotalRevenue=('TotalRevenue', 'sum')
    ).reset_index()
    plot_data_bar.sort_values(by="TotalOrder", ascending=False, inplace=True)

    # --- Data for Pie Chart ---
    # Aggregate TotalRevenue by Category for the pie chart
    plot_data_pie = df_filtered.groupby("Category").agg(
        TotalRevenue=('TotalRevenue', 'sum')
    ).reset_index()
    # Sort for consistent pie slice order (largest first)
    plot_data_pie.sort_values(by="TotalRevenue", ascending=False, inplace=True)

    # --- Data for Scatter Plot ---
    # For scatter plot, we can use the filtered data directly (individual transactions)
    # or aggregate if too many points. Let's use individual transactions for now.
    # Ensure relevant columns exist for the scatter plot (e.g., 'TotalRevenue', 'Quantity')
    if 'TotalRevenue' not in df_filtered.columns or 'Quantity' not in df_filtered.columns:
        st.warning("Cannot create Scatter Plot: 'TotalRevenue' or 'Quantity' column missing.")
        plot_scatter = pd.DataFrame() # Empty DataFrame to skip scatter plot creation
    else:
        plot_scatter = df_filtered.copy()


    # --- 5. Chart Creation and Display ---

    # Create columns for side-by-side charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"Total Orders by Category in {chart_title_country_suffix}")
        fig_bar = px.bar(
            plot_data_bar,
            x='TotalOrder',
            y='Category',
            orientation='h',
            title='Orders by Category', # Sub-chart title
            color='TotalOrder',
            color_continuous_scale=px.colors.sequential.Magma
        )
        fig_bar.update_layout(
            yaxis={'categoryorder':'total ascending'},
            margin=dict(l=200, r=20, t=50, b=50), # Adjusted margins for subplot
            xaxis_title="Total Orders (Count)",
            yaxis_title="Product Category"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.subheader(f"Revenue Distribution in {chart_title_country_suffix}")
        fig_pie = px.pie(
            plot_data_pie,
            values='TotalRevenue',
            names='Category',
            title='Revenue Distribution by Category', # Sub-chart title
            hole=0.4, # Creates a donut chart
            color_discrete_sequence=px.colors.sequential.RdBu # Example color sequence
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

    # Scatter Plot (below the two columns)
    if not plot_scatter.empty:
        st.subheader(f"Revenue vs. Quantity by Category in {chart_title_country_suffix}")
        fig_scatter = px.scatter(
            plot_scatter,
            x='Quantity',
            y='TotalRevenue',
            color='Category', # Color points by Category
            size='TotalRevenue', # Size points by TotalRevenue
            hover_name='Category', # Show Category on hover
            title='Revenue vs. Quantity per Transaction', # Sub-chart title
            labels={'Quantity': 'Quantity Sold', 'TotalRevenue': 'Total Revenue (USD)'}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("Scatter plot not generated due to missing data or columns.")


    # You can add more charts or data tables here
    st.subheader(f"Top Categories by Orders in {chart_title_country_suffix}")
    st.dataframe(plot_data_bar.head(5)) # Display top 5 categories in a table
