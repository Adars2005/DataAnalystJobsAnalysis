import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Page config
st.set_page_config(
    page_title="Data Analyst Job Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📊"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .stAlert {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">📊 Data Analyst Jobs Dashboard (2023)</h1>', unsafe_allow_html=True)

# Load dataset with error handling
@st.cache_data
def load_data():
    try:
        # Try multiple possible file names
        possible_files = [
            "DataAnalystjobs2023.xlsx",
            "dataanalystjobs2023.xlsx", 
            "data_analyst_jobs_2023.xlsx",
            "DataAnalystJobs2023.xlsx"
        ]
        
        df = None
        for file_name in possible_files:
            try:
                df = pd.read_excel(file_name, engine="openpyxl")
                break
            except FileNotFoundError:
                continue
        
        if df is None:
            # Create sample data if file not found
            st.warning("⚠️ Data file not found. Using sample data for demonstration.")
            return create_sample_data()
        
        # Data preprocessing
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['City'] = df['Job Location'].str.split(',').str[0] if 'Job Location' in df.columns else 'Unknown'
        
        # Clean and standardize data
        df['Job Title'] = df['Job Title'].str.strip() if 'Job Title' in df.columns else 'Data Analyst'
        df['Hired'] = df['Hired'].astype(str) if 'Hired' in df.columns else 'No'
        df['Easy Apply'] = df['Easy Apply'].astype(str) if 'Easy Apply' in df.columns else 'No'
        
        # Remove rows with missing critical data
        df = df.dropna(subset=['Date', 'Job Title'])
        
        return df
    
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        return create_sample_data()

def create_sample_data():
    """Create sample data for demonstration purposes"""
    np.random.seed(42)
    
    job_titles = [
        'Data Analyst', 'Business Analyst', 'Data Scientist', 
        'Business Intelligence Analyst', 'Marketing Analyst',
        'Financial Analyst', 'Research Analyst', 'Operations Analyst'
    ]
    
    cities = [
        'New York', 'San Francisco', 'Chicago', 'Boston', 'Seattle',
        'Los Angeles', 'Austin', 'Denver', 'Atlanta', 'Miami'
    ]
    
    companies = [
        'Google', 'Microsoft', 'Amazon', 'Meta', 'Apple',
        'Netflix', 'Uber', 'Airbnb', 'Spotify', 'Tesla'
    ]
    
    # Generate sample data
    n_jobs = 1000
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 12, 31)
    
    sample_data = {
        'Job Title': np.random.choice(job_titles, n_jobs),
        'Company': np.random.choice(companies, n_jobs),
        'City': np.random.choice(cities, n_jobs),
        'Job Location': [f"{city}, {np.random.choice(['NY', 'CA', 'TX', 'FL', 'WA'])}" 
                        for city in np.random.choice(cities, n_jobs)],
        'Date': pd.date_range(start=start_date, end=end_date, periods=n_jobs),
        'Hired': np.random.choice(['Yes', 'No'], n_jobs, p=[0.15, 0.85]),
        'Easy Apply': np.random.choice(['Yes', 'No'], n_jobs, p=[0.6, 0.4]),
        'Salary_Min': np.random.randint(50000, 120000, n_jobs),
        'Salary_Max': np.random.randint(70000, 150000, n_jobs)
    }
    
    return pd.DataFrame(sample_data)

# Load data
try:
    df = load_data()
    data_loaded = True
except Exception as e:
    st.error(f"❌ Failed to load data: {str(e)}")
    data_loaded = False

if data_loaded and not df.empty:
    # Sidebar Filters
    st.sidebar.markdown("## 🔍 Filter Jobs")
    
    # Advanced filters
    with st.sidebar.expander("📅 Date Range", expanded=True):
        min_date = df['Date'].min().date()
        max_date = df['Date'].max().date()
        
        date_range = st.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
    
    # Job Title Filter
    job_titles = sorted(df['Job Title'].unique())
    selected_title = st.sidebar.multiselect(
        "🎯 Job Title", 
        job_titles,
        help="Select one or more job titles to filter"
    )
    
    # City Filter
    cities = sorted(df['City'].unique())
    selected_city = st.sidebar.multiselect(
        "🏙️ City", 
        cities,
        help="Select one or more cities to filter"
    )
    
    # Company Filter (if available)
    if 'Company' in df.columns:
        companies = sorted(df['Company'].unique())
        selected_company = st.sidebar.multiselect(
            "🏢 Company", 
            companies,
            help="Select one or more companies to filter"
        )
    else:
        selected_company = []
    
    # Status Filters
    col1, col2 = st.sidebar.columns(2)
    with col1:
        hired_filter = st.selectbox("✅ Hired?", ["All", "Yes", "No"])
    with col2:
        easy_filter = st.selectbox("⚡ Easy Apply?", ["All", "Yes", "No"])
    
    # Apply filters
    filtered_df = df.copy()
    
    # Date filter
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df['Date'].dt.date >= start_date) & 
            (filtered_df['Date'].dt.date <= end_date)
        ]
    
    # Other filters
    if selected_title:
        filtered_df = filtered_df[filtered_df['Job Title'].isin(selected_title)]
    if selected_city:
        filtered_df = filtered_df[filtered_df['City'].isin(selected_city)]
    if selected_company:
        filtered_df = filtered_df[filtered_df['Company'].isin(selected_company)]
    if hired_filter != "All":
        filtered_df = filtered_df[filtered_df['Hired'] == hired_filter]
    if easy_filter != "All":
        filtered_df = filtered_df[filtered_df['Easy Apply'] == easy_filter]
    
    # Reset button
    if st.sidebar.button("🔄 Reset Filters"):
        st.rerun()
    
    # Main Dashboard
    if len(filtered_df) == 0:
        st.warning("⚠️ No data matches your selected filters. Please adjust your criteria.")
    else:
        # KPIs Section
        st.markdown("## 📊 Key Performance Indicators")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_jobs = len(filtered_df)
            st.metric(
                "Total Jobs",
                f"{total_jobs:,}",
                delta=f"{total_jobs - len(df)}" if total_jobs != len(df) else None
            )
        
        with col2:
            hired_pct = filtered_df['Hired'].value_counts(normalize=True).get('Yes', 0) * 100
            st.metric(
                "Hired Rate",
                f"{hired_pct:.1f}%",
                delta=f"{hired_pct - (df['Hired'].value_counts(normalize=True).get('Yes', 0) * 100):.1f}%" if total_jobs != len(df) else None
            )
        
        with col3:
            easy_pct = filtered_df['Easy Apply'].value_counts(normalize=True).get('Yes', 0) * 100
            st.metric(
                "Easy Apply Rate",
                f"{easy_pct:.1f}%",
                delta=f"{easy_pct - (df['Easy Apply'].value_counts(normalize=True).get('Yes', 0) * 100):.1f}%" if total_jobs != len(df) else None
            )
        
        with col4:
            avg_jobs_per_day = len(filtered_df) / max(1, (filtered_df['Date'].max() - filtered_df['Date'].min()).days)
            st.metric(
                "Jobs/Day",
                f"{avg_jobs_per_day:.1f}",
                help="Average number of jobs posted per day"
            )
        
        st.divider()
        
        # Charts Section
        st.markdown("## 📈 Visual Insights")
        
        # Create tabs for different chart categories
        tab1, tab2, tab3, tab4 = st.tabs(["🎯 Job Analysis", "📍 Geographic", "📊 Hiring Insights", "📅 Time Series"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                # Top Job Titles
                job_counts = filtered_df['Job Title'].value_counts().head(10)
                fig1 = px.bar(
                    x=job_counts.values,
                    y=job_counts.index,
                    orientation='h',
                    title="🎯 Top 10 Job Titles",
                    labels={'x': 'Number of Jobs', 'y': 'Job Title'},
                    color=job_counts.values,
                    color_continuous_scale='viridis'
                )
                fig1.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                # Company distribution (if available)
                if 'Company' in filtered_df.columns:
                    company_counts = filtered_df['Company'].value_counts().head(10)
                    fig2 = px.bar(
                        x=company_counts.values,
                        y=company_counts.index,
                        orientation='h',
                        title="🏢 Top 10 Companies",
                        labels={'x': 'Number of Jobs', 'y': 'Company'},
                        color=company_counts.values,
                        color_continuous_scale='plasma'
                    )
                    fig2.update_layout(height=400, showlegend=False)
                    st.plotly_chart(fig2, use_container_width=True)
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                # Top Cities
                city_counts = filtered_df['City'].value_counts().head(10)
                fig3 = px.bar(
                    x=city_counts.values,
                    y=city_counts.index,
                    orientation='h',
                    title="🏙️ Top 10 Cities",
                    labels={'x': 'Number of Jobs', 'y': 'City'},
                    color=city_counts.values,
                    color_continuous_scale='blues'
                )
                fig3.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig3, use_container_width=True)
            
            with col2:
                # Geographic distribution pie chart
                fig4 = px.pie(
                    values=city_counts.values,
                    names=city_counts.index,
                    title="📍 Geographic Distribution",
                    hole=0.3
                )
                fig4.update_layout(height=400)
                st.plotly_chart(fig4, use_container_width=True)
        
        with tab3:
            col1, col2 = st.columns(2)
            
            with col1:
                # Hiring Distribution
                hired_counts = filtered_df['Hired'].value_counts()
                fig5 = px.pie(
                    values=hired_counts.values,
                    names=hired_counts.index,
                    title="✅ Hiring Distribution",
                    color_discrete_map={'Yes': '#00CC96', 'No': '#EF553B'}
                )
                st.plotly_chart(fig5, use_container_width=True)
            
            with col2:
                # Easy Apply Distribution
                easy_counts = filtered_df['Easy Apply'].value_counts()
                fig6 = px.pie(
                    values=easy_counts.values,
                    names=easy_counts.index,
                    title="⚡ Easy Apply Distribution",
                    color_discrete_map={'Yes': '#AB63FA', 'No': '#FF6692'}
                )
                st.plotly_chart(fig6, use_container_width=True)
            
            # Easy Apply vs Hired Analysis
            st.markdown("### 📊 Easy Apply vs Hiring Success Rate")
            if len(filtered_df) > 0:
                crosstab = pd.crosstab(filtered_df['Easy Apply'], filtered_df['Hired'], normalize='index') * 100
                
                fig7 = px.bar(
                    crosstab.reset_index(),
                    x='Easy Apply',
                    y=['No', 'Yes'],
                    title="Hiring Success Rate by Easy Apply Status",
                    labels={'value': 'Percentage', 'variable': 'Hired Status'},
                    color_discrete_map={'Yes': '#00CC96', 'No': '#EF553B'}
                )
                fig7.update_layout(barmode='stack', height=400)
                st.plotly_chart(fig7, use_container_width=True)
        
        with tab4:
            # Time series analysis
            st.markdown("### 📅 Job Posting Trends Over Time")
            
            # Monthly trend
            monthly_data = filtered_df.groupby(filtered_df['Date'].dt.to_period('M')).size().reset_index()
            monthly_data['Date'] = monthly_data['Date'].dt.to_timestamp()
            monthly_data.columns = ['Date', 'Job_Count']
            
            fig8 = px.line(
                monthly_data,
                x='Date',
                y='Job_Count',
                title="Monthly Job Posting Trends",
                markers=True
            )
            fig8.update_layout(height=400)
            st.plotly_chart(fig8, use_container_width=True)
            
            # Weekly pattern
            filtered_df['DayOfWeek'] = filtered_df['Date'].dt.day_name()
            daily_pattern = filtered_df['DayOfWeek'].value_counts().reindex([
                'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
            ])
            
            fig9 = px.bar(
                x=daily_pattern.index,
                y=daily_pattern.values,
                title="Job Postings by Day of Week",
                labels={'x': 'Day of Week', 'y': 'Number of Jobs'},
                color=daily_pattern.values,
                color_continuous_scale='viridis'
            )
            fig9.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig9, use_container_width=True)
        
        st.divider()
        
        # Data Table Section
        st.markdown("## 📋 Detailed Job Listings")
        
        # Display options
        col1, col2, col3 = st.columns(3)
        with col1:
            show_all = st.checkbox("Show All Columns", value=False)
        with col2:
            rows_to_show = st.selectbox("Rows to Display", [10, 25, 50, 100], index=1)
        with col3:
            sort_by = st.selectbox("Sort By", ['Date', 'Job Title', 'City', 'Company'] if 'Company' in filtered_df.columns else ['Date', 'Job Title', 'City'])
        
        # Display filtered data
        display_df = filtered_df.sort_values(by=sort_by, ascending=False).head(rows_to_show)
        
        if not show_all:
            # Show only key columns
            key_columns = ['Date', 'Job Title', 'City', 'Hired', 'Easy Apply']
            if 'Company' in display_df.columns:
                key_columns.insert(2, 'Company')
            display_df = display_df[key_columns]
        
        st.dataframe(display_df, use_container_width=True)
        
        # Export Section
        st.markdown("## 📥 Export Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # CSV Download
            csv_data = filtered_df.to_csv(index=False)
            st.download_button(
                label="📄 Download as CSV",
                data=csv_data,
                file_name=f"filtered_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                help="Download the filtered dataset as CSV file"
            )
        
        with col2:
            # Excel Download
            excel_buffer = pd.ExcelWriter('buffer', engine='openpyxl')
            filtered_df.to_excel(excel_buffer, index=False, sheet_name='Jobs')
            excel_buffer.close()
            
            st.download_button(
                label="📊 Download as Excel",
                data=excel_buffer.getvalue() if hasattr(excel_buffer, 'getvalue') else b'',
                file_name=f"filtered_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Download the filtered dataset as Excel file"
            )
        
        # Summary Statistics
        with st.expander("📊 Summary Statistics"):
            st.markdown("### Dataset Overview")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Basic Statistics:**")
                st.write(f"• Total Records: {len(filtered_df):,}")
                st.write(f"• Date Range: {filtered_df['Date'].min().strftime('%Y-%m-%d')} to {filtered_df['Date'].max().strftime('%Y-%m-%d')}")
                st.write(f"• Unique Job Titles: {filtered_df['Job Title'].nunique()}")
                st.write(f"• Unique Cities: {filtered_df['City'].nunique()}")
                if 'Company' in filtered_df.columns:
                    st.write(f"• Unique Companies: {filtered_df['Company'].nunique()}")
            
            with col2:
                st.markdown("**Hiring Statistics:**")
                st.write(f"• Hired: {filtered_df['Hired'].value_counts().get('Yes', 0):,} ({(filtered_df['Hired'].value_counts(normalize=True).get('Yes', 0) * 100):.1f}%)")
                st.write(f"• Not Hired: {filtered_df['Hired'].value_counts().get('No', 0):,} ({(filtered_df['Hired'].value_counts(normalize=True).get('No', 0) * 100):.1f}%)")
                st.write(f"• Easy Apply: {filtered_df['Easy Apply'].value_counts().get('Yes', 0):,} ({(filtered_df['Easy Apply'].value_counts(normalize=True).get('Yes', 0) * 100):.1f}%)")
                st.write(f"• Regular Apply: {filtered_df['Easy Apply'].value_counts().get('No', 0):,} ({(filtered_df['Easy Apply'].value_counts(normalize=True).get('No', 0) * 100):.1f}%)")

else:
    st.error("❌ Unable to load data. Please check if the data file exists and is properly formatted.")
    st.info("💡 Expected file: 'DataAnalystjobs2023.xlsx' in the same directory as this script.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.9em; margin-top: 2rem;'>
        📊 Data Analyst Jobs Dashboard | Built with Streamlit & Plotly<br>
        💡 Use the sidebar filters to explore different aspects of the job market
    </div>
    """,
    unsafe_allow_html=True
)