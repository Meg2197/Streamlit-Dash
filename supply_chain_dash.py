import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Supply Chain Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    h1 {
        color: #1f77b4;
        text-align: center;
        padding: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('supply_chain_data.csv')

    # Clean currency columns
    def clean_currency(value):
        if isinstance(value, str):
            return float(value.replace('$', '').replace(',', ''))
        return value

    currency_cols = ['Price', 'Revenue generated', 'Shipping costs', 'Manufacturing costs', 'Costs']
    for col in currency_cols:
        df[col] = df[col].apply(clean_currency)

    return df

df = load_data()

# Title and description
st.title("📦 Supply Chain Analytics Dashboard")
st.markdown("---")

# Sidebar filters
st.sidebar.header("🔍 Filters")
selected_product_type = st.sidebar.multiselect(
    "Product Type",
    options=df['Product Type'].unique(),
    default=df['Product Type'].unique()
)

selected_location = st.sidebar.multiselect(
    "Location",
    options=df['Location'].unique(),
    default=df['Location'].unique()
)

selected_transport = st.sidebar.multiselect(
    "Transportation Mode",
    options=df['Transportation modes'].unique(),
    default=df['Transportation modes'].unique()
)

# Filter data
df_filtered = df[
    (df['Product Type'].isin(selected_product_type)) &
    (df['Location'].isin(selected_location)) &
    (df['Transportation modes'].isin(selected_transport))
]

# Key Metrics Row
st.header("📊 Key Performance Indicators")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_revenue = df_filtered['Revenue generated'].sum()
    st.metric("Total Revenue", f"${total_revenue:,.2f}")

with col2:
    total_products_sold = df_filtered['Number of products sold'].sum()
    st.metric("Products Sold", f"{total_products_sold:,}")

with col3:
    avg_defect_rate = df_filtered['Defect rates'].mean()
    st.metric("Avg Defect Rate", f"{avg_defect_rate:.2f}%")

with col4:
    avg_lead_time = df_filtered['Lead times'].mean()
    st.metric("Avg Lead Time", f"{avg_lead_time:.1f} days")

with col5:
    total_shipping_cost = df_filtered['Shipping costs'].sum()
    st.metric("Total Shipping Cost", f"${total_shipping_cost:,.2f}")

st.markdown("---")

# Row 1: Revenue and Sales Analysis
st.header("💰 Revenue & Sales Analysis")
col1, col2 = st.columns(2)

with col1:
    # Revenue by Product Type (Bar Chart)
    revenue_by_product = df_filtered.groupby('Product Type')['Revenue generated'].sum().reset_index()
    fig1 = px.bar(
        revenue_by_product,
        x='Product Type',
        y='Revenue generated',
        title='Revenue by Product Type',
        color='Product Type',
        color_discrete_sequence=px.colors.qualitative.Set2,
        text='Revenue generated'
    )
    fig1.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
    fig1.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    # Products Sold by Location (Horizontal Bar Chart)
    products_by_location = df_filtered.groupby('Location')['Number of products sold'].sum().reset_index()
    products_by_location = products_by_location.sort_values('Number of products sold')
    fig2 = px.bar(
        products_by_location,
        y='Location',
        x='Number of products sold',
        title='Products Sold by Location',
        orientation='h',
        color='Number of products sold',
        color_continuous_scale='Viridis',
        text='Number of products sold'
    )
    fig2.update_traces(texttemplate='%{text:,}', textposition='outside')
    fig2.update_layout(height=400)
    st.plotly_chart(fig2, use_container_width=True)

# Row 2: Transportation and Logistics
st.header("🚚 Transportation & Logistics")
col1, col2, col3 = st.columns(3)

with col1:
    # Transportation Mode Distribution (Pie Chart)
    transport_dist = df_filtered['Transportation modes'].value_counts().reset_index()
    transport_dist.columns = ['Transportation modes', 'Count']
    fig3 = px.pie(
        transport_dist,
        values='Count',
        names='Transportation modes',
        title='Transportation Mode Distribution',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig3.update_traces(textposition='inside', textinfo='percent+label')
    fig3.update_layout(height=400)
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    # Shipping Costs by Route (Donut Chart)
    shipping_by_route = df_filtered.groupby('Routes')['Shipping costs'].sum().reset_index()
    fig4 = px.pie(
        shipping_by_route,
        values='Shipping costs',
        names='Routes',
        title='Shipping Costs by Route',
        hole=0.5,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig4.update_traces(textposition='inside', textinfo='percent+label')
    fig4.update_layout(height=400)
    st.plotly_chart(fig4, use_container_width=True)

with col3:
    # Average Shipping Time by Carrier (Bar Chart)
    avg_shipping_time = df_filtered.groupby('Shipping carriers')['Shipping times'].mean().reset_index()
    avg_shipping_time = avg_shipping_time.sort_values('Shipping times', ascending=False)
    fig5 = px.bar(
        avg_shipping_time,
        x='Shipping carriers',
        y='Shipping times',
        title='Avg Shipping Time by Carrier',
        color='Shipping times',
        color_continuous_scale='Reds',
        text='Shipping times'
    )
    fig5.update_traces(texttemplate='%{text:.1f} days', textposition='outside')
    fig5.update_layout(height=400)
    st.plotly_chart(fig5, use_container_width=True)

# Row 3: Production and Quality
st.header("🏭 Production & Quality Control")
col1, col2 = st.columns(2)

with col1:
    # Production Volumes by Location (Stacked Bar Chart)
    production_location = df_filtered.groupby(['Location', 'Product Type'])['Production volumes'].sum().reset_index()
    fig6 = px.bar(
        production_location,
        x='Location',
        y='Production volumes',
        color='Product Type',
        title='Production Volumes by Location & Product Type',
        barmode='stack',
        color_discrete_sequence=px.colors.qualitative.Bold,
        text='Production volumes'
    )
    fig6.update_traces(texttemplate='%{text:,}', textposition='inside')
    fig6.update_layout(height=400)
    st.plotly_chart(fig6, use_container_width=True)

with col2:
    # Inspection Results Distribution (Funnel Chart)
    inspection_counts = df_filtered['Inspection results'].value_counts().reset_index()
    inspection_counts.columns = ['Inspection results', 'Count']
    inspection_counts = inspection_counts.sort_values('Count', ascending=False)

    fig7 = go.Figure(go.Funnel(
        y=inspection_counts['Inspection results'],
        x=inspection_counts['Count'],
        textposition="inside",
        textinfo="value+percent initial",
        marker=dict(color=["#28a745", "#ffc107", "#dc3545"])
    ))
    fig7.update_layout(title='Inspection Results Funnel', height=400)
    st.plotly_chart(fig7, use_container_width=True)

# Row 4: Scatter and Correlation Analysis
st.header("📈 Correlation & Scatter Analysis")
col1, col2 = st.columns(2)

with col1:
    # Defect Rate vs Manufacturing Costs (Scatter Plot)
    fig8 = px.scatter(
        df_filtered,
        x='Manufacturing costs',
        y='Defect rates',
        color='Product Type',
        size='Production volumes',
        title='Defect Rate vs Manufacturing Costs',
        hover_data=['Location', 'Supplier name'],
        color_discrete_sequence=px.colors.qualitative.Vivid
    )
    fig8.update_layout(height=400)
    st.plotly_chart(fig8, use_container_width=True)

with col2:
    # Lead Time vs Order Quantities (Scatter Plot)
    fig9 = px.scatter(
        df_filtered,
        x='Lead times',
        y='Order quantities',
        color='Location',
        size='Stock levels',
        title='Lead Time vs Order Quantities',
        hover_data=['Product Type', 'Supplier name'],
        trendline="ols",
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    fig9.update_layout(height=400)
    st.plotly_chart(fig9, use_container_width=True)

# Row 5: Time-based Analysis
st.header("⏱️ Lead Time Analysis")
col1, col2 = st.columns(2)

with col1:
    # Lead Times Distribution (Histogram)
    fig10 = px.histogram(
        df_filtered,
        x='Lead times',
        nbins=20,
        title='Lead Times Distribution',
        color_discrete_sequence=['#636EFA'],
        marginal='box'
    )
    fig10.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig10, use_container_width=True)

with col2:
    # Manufacturing Lead Time by Product Type (Box Plot)
    fig11 = px.box(
        df_filtered,
        x='Product Type',
        y='Manufacturing lead time',
        color='Product Type',
        title='Manufacturing Lead Time Distribution by Product Type',
        color_discrete_sequence=px.colors.qualitative.Alphabet
    )
    fig11.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig11, use_container_width=True)

# Row 6: Stock and Inventory Analysis
st.header("📦 Stock & Inventory Management")
col1, col2 = st.columns(2)

with col1:
    # Stock Levels vs Availability (Scatter with Color)
    fig12 = px.scatter(
        df_filtered,
        x='Stock levels',
        y='Availability',
        color='Product Type',
        size='Number of products sold',
        title='Stock Levels vs Availability',
        hover_data=['SKU', 'Location'],
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    fig12.update_layout(height=400)
    st.plotly_chart(fig12, use_container_width=True)

with col2:
    # Top 10 Products by Revenue (Tree Map)
    top_products = df_filtered.nlargest(10, 'Revenue generated')
    fig13 = px.treemap(
        top_products,
        path=['Product Type', 'SKU'],
        values='Revenue generated',
        title='Top 10 Products by Revenue (TreeMap)',
        color='Defect rates',
        color_continuous_scale='RdYlGn_r',
        hover_data=['Number of products sold']
    )
    fig13.update_layout(height=400)
    st.plotly_chart(fig13, use_container_width=True)

# Row 7: Cost Analysis
st.header("💵 Cost Analysis")
col1, col2 = st.columns(2)

with col1:
    # Total Costs by Transportation Mode (Sunburst Chart)
    costs_by_transport = df_filtered.groupby(['Transportation modes', 'Routes']).agg({
        'Costs': 'sum',
        'Shipping costs': 'sum'
    }).reset_index()

    fig14 = px.sunburst(
        costs_by_transport,
        path=['Transportation modes', 'Routes'],
        values='Costs',
        title='Cost Breakdown by Transportation & Routes',
        color='Costs',
        color_continuous_scale='Blues'
    )
    fig14.update_layout(height=450)
    st.plotly_chart(fig14, use_container_width=True)

with col2:
    # Cost Components Comparison (Grouped Bar Chart)
    cost_data = pd.DataFrame({
        'Category': ['Manufacturing', 'Shipping', 'Transportation'],
        'Total Cost': [
            df_filtered['Manufacturing costs'].sum(),
            df_filtered['Shipping costs'].sum(),
            df_filtered['Costs'].sum()
        ]
    })

    fig15 = px.bar(
        cost_data,
        x='Category',
        y='Total Cost',
        title='Total Cost Comparison by Category',
        color='Category',
        color_discrete_sequence=px.colors.qualitative.Dark2,
        text='Total Cost'
    )
    fig15.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
    fig15.update_layout(showlegend=False, height=450)
    st.plotly_chart(fig15, use_container_width=True)

# Row 8: Heatmap and Advanced Visualizations
st.header("🔥 Correlation Heatmap")

# Correlation Heatmap
numeric_cols = ['Price', 'Availability', 'Number of products sold', 'Revenue generated',
                'Stock levels', 'Lead times', 'Order quantities', 'Shipping times',
                'Production volumes', 'Manufacturing lead time', 'Defect rates']

correlation_matrix = df_filtered[numeric_cols].corr()

fig16 = px.imshow(
    correlation_matrix,
    labels=dict(color="Correlation"),
    x=correlation_matrix.columns,
    y=correlation_matrix.columns,
    color_continuous_scale='RdBu_r',
    aspect="auto",
    title='Correlation Matrix of Key Metrics'
)
fig16.update_layout(height=600)
st.plotly_chart(fig16, use_container_width=True)

# Row 9: Multi-metric Analysis
st.header("📊 Multi-Metric Comparison")
col1, col2 = st.columns(2)

with col1:
    # Radar Chart for Average Metrics by Product Type
    metrics_by_product = df_filtered.groupby('Product Type').agg({
        'Price': 'mean',
        'Stock levels': 'mean',
        'Lead times': 'mean',
        'Defect rates': 'mean',
        'Shipping times': 'mean'
    }).reset_index()

    # Normalize values for radar chart
    for col in ['Price', 'Stock levels', 'Lead times', 'Defect rates', 'Shipping times']:
        metrics_by_product[col] = (metrics_by_product[col] - metrics_by_product[col].min()) / (metrics_by_product[col].max() - metrics_by_product[col].min()) * 100

    fig17 = go.Figure()

    for idx, product in enumerate(metrics_by_product['Product Type'].unique()):
        product_data = metrics_by_product[metrics_by_product['Product Type'] == product]
        fig17.add_trace(go.Scatterpolar(
            r=product_data[['Price', 'Stock levels', 'Lead times', 'Defect rates', 'Shipping times']].values[0],
            theta=['Price', 'Stock levels', 'Lead times', 'Defect rates', 'Shipping times'],
            fill='toself',
            name=product
        ))

    fig17.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title='Product Type Performance Radar',
        height=450
    )
    st.plotly_chart(fig17, use_container_width=True)

with col2:
    # Revenue and Defect Rate by Supplier (Bubble Chart)
    supplier_metrics = df_filtered.groupby('Supplier name').agg({
        'Revenue generated': 'sum',
        'Defect rates': 'mean',
        'Number of products sold': 'sum'
    }).reset_index()

    fig18 = px.scatter(
        supplier_metrics,
        x='Revenue generated',
        y='Defect rates',
        size='Number of products sold',
        color='Supplier name',
        title='Supplier Performance: Revenue vs Defect Rate',
        hover_data=['Supplier name'],
        size_max=60
    )
    fig18.update_layout(height=450, showlegend=False)
    st.plotly_chart(fig18, use_container_width=True)

# Row 10: Demographics and Customer Insights
st.header("👥 Customer Demographics")
col1, col2 = st.columns(2)

with col1:
    # Customer Demographics Distribution
    demographics_dist = df_filtered['Customer demographics'].value_counts().reset_index()
    demographics_dist.columns = ['Demographics', 'Count']

    fig19 = px.bar(
        demographics_dist,
        x='Demographics',
        y='Count',
        title='Customer Demographics Distribution',
        color='Demographics',
        color_discrete_sequence=px.colors.qualitative.Pastel1,
        text='Count'
    )
    fig19.update_traces(textposition='outside')
    fig19.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig19, use_container_width=True)

with col2:
    # Revenue by Demographics
    revenue_demographics = df_filtered.groupby('Customer demographics')['Revenue generated'].sum().reset_index()

    fig20 = px.pie(
        revenue_demographics,
        values='Revenue generated',
        names='Customer demographics',
        title='Revenue Distribution by Customer Demographics',
        hole=0.3,
        color_discrete_sequence=px.colors.qualitative.Set1
    )
    fig20.update_traces(textposition='inside', textinfo='percent+label')
    fig20.update_layout(height=400)
    st.plotly_chart(fig20, use_container_width=True)

# Data Table
st.header("📋 Detailed Data Table")
st.dataframe(
    df_filtered.style.format({
        'Price': '${:.2f}',
        'Revenue generated': '${:,.2f}',
        'Shipping costs': '${:.2f}',
        'Manufacturing costs': '${:.2f}',
        'Costs': '${:.2f}',
        'Defect rates': '{:.2f}%'
    }),
    use_container_width=True,
    height=400
)

# Summary Statistics
st.header("📊 Summary Statistics")
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Revenue Metrics")
    st.write(f"**Total Revenue:** ${df_filtered['Revenue generated'].sum():,.2f}")
    st.write(f"**Average Revenue:** ${df_filtered['Revenue generated'].mean():,.2f}")
    st.write(f"**Max Revenue:** ${df_filtered['Revenue generated'].max():,.2f}")

with col2:
    st.subheader("Quality Metrics")
    st.write(f"**Average Defect Rate:** {df_filtered['Defect rates'].mean():.2f}%")
    st.write(f"**Pass Rate:** {(df_filtered['Inspection results'] == 'Pass').sum() / len(df_filtered) * 100:.1f}%")
    st.write(f"**Fail Rate:** {(df_filtered['Inspection results'] == 'Fail').sum() / len(df_filtered) * 100:.1f}%")

with col3:
    st.subheader("Operational Metrics")
    st.write(f"**Average Lead Time:** {df_filtered['Lead times'].mean():.1f} days")
    st.write(f"**Total Stock:** {df_filtered['Stock levels'].sum():,} units")
    st.write(f"**Total Products Sold:** {df_filtered['Number of products sold'].sum():,}")

st.markdown("---")
st.markdown("**Dashboard created with Streamlit & Plotly** | Data updated: Feb 2026")