import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- Configuration and Setup ---
st.set_page_config(layout="wide", page_title="MedTech Market Adoption Dashboard")

# Define the data path (adjust as necessary)
HOME_DIR = os.path.expanduser("~")
FILE_PATH = os.path.join(HOME_DIR, "Desktop", "Simulated_device_adoption", "device_adoption_data.csv")

@st.cache_data
def load_data():
    """Loads and preprocesses the simulated data."""
    try:
        df = pd.read_csv(FILE_PATH)
        # Convert date column and create 'Month' Period
        df['Procedure_Date'] = pd.to_datetime(df['Procedure_Date'], errors='coerce')
        df.dropna(subset=['Procedure_Date'], inplace=True)
        df['Month'] = df['Procedure_Date'].dt.to_period('M')

        # Identify the month of first adoption for each physician
        first_adoption = df.groupby('Physician_ID')['Procedure_Date'].min().reset_index(name='Adoption_Date')
        
        # Merge the adoption date back to the main DataFrame (or use a simplified unique monthly count)
        
        return df, first_adoption
    except FileNotFoundError:
        st.error(f"Error: Data file not found at {FILE_PATH}. Please check the path.")
        return pd.DataFrame(), pd.DataFrame()
    except Exception as e:
        st.error(f"An error occurred during data loading: {e}")
        return pd.DataFrame(), pd.DataFrame()

# Load Data
device_adoption, first_adoption_df = load_data()

# Check if data loaded successfully
if device_adoption.empty:
    st.stop()

# --- Pre-calculate Adoption Data for Chart 1 ---
def get_monthly_adoption(df):
    """Calculates the count of unique physicians adopting for the first time each month."""
    
    # 1. Identify the first procedure date for each physician
    adopter_df = df.groupby('Physician_ID').agg(
        Adoption_Date=('Procedure_Date', 'min'),
        Geographic_Region=('Geographic_Region', 'first')
    ).reset_index()

    # 2. Count new unique physicians by the month of their adoption date
    adopter_df['Adoption_Month'] = adopter_df['Adoption_Date'].dt.to_period('M')

    monthly_growth = adopter_df.groupby(['Adoption_Month', 'Geographic_Region']).agg(
        New_Adopters=('Physician_ID', 'count')
    ).reset_index()

    # Convert Period to string for plotting
    monthly_growth['Month'] = monthly_growth['Adoption_Month'].astype(str)
    return monthly_growth

adoption_data = get_monthly_adoption(device_adoption)

# --- Dashboard Layout ---
st.title("AcuityMD MedTech Commercial Adoption Analysis")
st.markdown("""
    *Demonstrating data analytics and visualization skills for strategic customer insights.*
""")

# --- Filters ---
col1, col2 = st.columns([1, 1])

# Filter 1: Geographic Region
regions = sorted(device_adoption['Geographic_Region'].unique())
selected_region = col1.selectbox("Filter by Geographic Region (for Charts 1 & 3):", 
                                 options=["All Regions"] + regions)

# Filter 2: Specialty (Primary for Chart 3)
specialties = sorted(device_adoption['Specialty'].unique())
selected_specialty = col2.selectbox("Filter by Primary Specialty (for Chart 3 Analysis):", 
                                    options=["All Specialties"] + specialties)


# --- ROW 1: Adoption Over Time (Line Chart) ---
st.header("1. New Physician Adoption Velocity")
st.markdown("Shows the monthly volume of *new* unique physicians adopting the device.")

if selected_region != "All Regions":
    filtered_adoption = adoption_data[adoption_data['Geographic_Region'] == selected_region]
    title_suffix = f" in {selected_region}"
else:
    # If All Regions, sum the adopters across all regions for the line chart
    filtered_adoption = adoption_data.groupby('Month').agg(
        New_Adopters=('New_Adopters', 'sum')
    ).reset_index()
    filtered_adoption['Month'] = filtered_adoption['Month'].astype(str)
    title_suffix = " (Total Market)"

fig1 = px.line(filtered_adoption, 
               x='Month', 
               y='New_Adopters', 
               markers=True,
               title=f"Monthly New Adopting Physicians{title_suffix}",
               labels={'New_Adopters': 'New Unique Physicians', 'Month': 'Adoption Month'},
               color_discrete_sequence=px.colors.qualitative.Plotly
              )
fig1.update_layout(xaxis_title="", yaxis_title="New Unique Physicians")
st.plotly_chart(fig1, use_container_width=True)


# --- ROW 2: Market Penetration (Bar Chart by Region) ---
st.header("2. Geographic Market Penetration")
st.markdown("Total procedure volume by geographic region, regardless of adoption date.")

region_breakdown = device_adoption.groupby('Geographic_Region').agg(
    Total_Procedures=('Device_ID', 'count')
).reset_index().sort_values('Total_Procedures', ascending=False)

fig2 = px.bar(region_breakdown, 
              x='Geographic_Region', 
              y='Total_Procedures', 
              color='Geographic_Region',
              title="Total Procedure Volume by Geographic Region",
              labels={'Total_Procedures': 'Total Procedures', 'Geographic_Region': 'Region'},
              color_discrete_sequence=px.colors.sequential.Agsunset)
st.plotly_chart(fig2, use_container_width=True)


# --- ROW 3: Physician Segmentation & Actionable Insight ---
st.header("3. Specialty Segmentation and Commercial Insights")
col_chart, col_insight = st.columns([2, 1])

# --- Chart 3: Specialty Breakdown ---
col_chart.subheader("Procedures by Specialty")

if selected_region != "All Regions":
    chart3_data = device_adoption[device_adoption['Geographic_Region'] == selected_region]
    chart3_title = f"Specialty Breakdown in {selected_region}"
else:
    chart3_data = device_adoption
    chart3_title = "Overall Specialty Breakdown"

specialty_breakdown = chart3_data.groupby('Specialty').agg(
    Procedure_Count=('Device_ID', 'count'),
    Avg_Revenue=('Revenue_Impact', 'mean')
).reset_index().sort_values('Procedure_Count', ascending=False)


fig3 = px.bar(specialty_breakdown, 
              x='Specialty', 
              y='Procedure_Count',
              title=chart3_title,
              labels={'Procedure_Count': 'Total Procedures'},
              hover_data=['Avg_Revenue'],
              color='Specialty',
              color_discrete_sequence=px.colors.qualitative.Bold
             )
col_chart.plotly_chart(fig3, use_container_width=True)


# --- Actionable Insight Panel ---
col_insight.subheader("Actionable Insight")
col_insight.markdown("---")

def generate_insight(df, region, specialty):
    """Generates a dynamic, actionable insight based on the filter selection."""
    
    # Base Insight (Adoption Over Time)
    if not adoption_data.empty:
        latest_month = adoption_data['Month'].max()
        latest_count = adoption_data[adoption_data['Month'] == latest_month]['New_Adopters'].sum()
        
        # Simple MoM Growth calculation (assuming sorted data)
        adoption_sorted = adoption_data.groupby('Month')['New_Adopters'].sum().reset_index()
        adoption_sorted['MoM_Growth'] = adoption_sorted['New_Adopters'].pct_change()
        
        last_growth = adoption_sorted['MoM_Growth'].iloc[-1] * 100 if len(adoption_sorted) > 1 else 0

        insight = f"""
        **Market Velocity:** Last month ({latest_month}) saw **{latest_count}** new physician adopters, representing a **{last_growth:.1f}%** Month-over-Month change in market penetration.
        """
    else:
         insight = "Data is unavailable for analysis."
    
    # Region-Specific Insight (Growth vs. Volume)
    if region != "All Regions":
        regional_volume = region_breakdown[region_breakdown['Geographic_Region'] == region]['Total_Procedures'].iloc[0]
        market_share = regional_volume / region_breakdown['Total_Procedures'].sum() * 100
        
        insight += f"""
        \n\n**Regional Strategy ({region}):** This region accounts for **{market_share:.1f}%** of total market volume. The growth rate here is critical, but volume may be limited compared to other regions. Ensure sales efforts focus on quality account penetration over pure volume acquisition.
        """
        
    # Specialty-Specific Insight (Revenue vs. Volume)
    if specialty != "All Specialties":
        specialty_row = specialty_breakdown[specialty_breakdown['Specialty'] == specialty]
        if not specialty_row.empty:
            vol = specialty_row['Procedure_Count'].iloc[0]
            rev = specialty_row['Avg_Revenue'].iloc[0]
            
            # Find the specialty with the highest Avg_Revenue
            max_rev_specialty = specialty_breakdown.loc[specialty_breakdown['Avg_Revenue'].idxmax()]
            
            insight += f"""
            \n\n**Specialty Focus ({specialty}):** This segment has generated **{vol} procedures** with an **average revenue impact of ${rev:,.0f}** per procedure. The **{max_rev_specialty['Specialty'].iloc[0]}** specialty, however, shows the highest average revenue impact (${max_rev_specialty['Avg_Revenue'].iloc[0]:,.0f}). Consider targeting the highest revenue specialties for future high-value accounts.
            """

    return insight

# Display the Insight
insight_text = generate_insight(device_adoption, selected_region, selected_specialty)
col_insight.info(insight_text)