Market Adoption Dashboard Prototype

This project is an interactive, single-page data visualization dashboard built using Streamlit and Plotly. 
  It serves as a proof-of-concept for the analytical and reporting capabilities required by a Professional Services / Data Analyst role in a MedTech company.

The goal is to transform simulated raw procedure data into actionable commercial
  insights regarding the adoption, growth, and market concentration of a new medical device.

  Technology Stack

Primary Language: Python

Web Framework: Streamlit (for quick prototyping and interactive UI)

Visualization: Plotly Express (for rich, interactive charts)

Data Handling: Pandas (for data ingestion, cleaning, and metric calculation)

 
 Setup and Running the Dashboard

1. Prerequisites

Ensure you have Python installed, then install the necessary libraries:

    pip install streamlit pandas plotly

2. Data File Placement

The application expects the simulated data file to be located in a specific folder structure:

File Name: device_adoption_data.csv

Required Path: ~/Desktop/Simulated_device_adoption/device_adoption_data.csv
(The script uses os.path.expanduser("~") to find your home directory dynamically.)

3. Execution

Save the dashboard code as market_adoption_dashboard.py and run it from your terminal:

    streamlit run market_adoption_dashboard.py

The application will automatically open in your web browser.

📊 Key Analytical Features

The dashboard allows users to slice the data to answer critical commercial questions:

Dashboard Feature

Analytical Question Answered

Metric/Data Source

1. Adoption Velocity (Line Chart)

How fast is the market growing and what is the current Month-over-Month trend?

New unique physician adopters per month.

2. Geographic Penetration (Bar Chart)

Which regions are contributing the most volume? Where should sales efforts be rebalanced?

Total procedures by Geographic_Region.

3. Specialty Segmentation (Bar Chart)

Which physician specialties are driving device usage, and does volume correlate with revenue value?

Procedures by Specialty, Hover data shows Average Revenue Impact.

4. Actionable Insight Panel

What is the strategic takeaway from the currently applied regional/specialty filters?

Dynamic text generated based on calculated growth rates and market share metrics.
