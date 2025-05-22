import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

def show_top_10_employees_by_kpi(aggregated_df):
    st.subheader("🏆 Top 10 Employees by Selected KPI")
    employee_col1, employee_col2 = st.columns(2)
    
    # Step 1: Select Managers (Allow Multiple Selections)
    manager_options = aggregated_df['Manager'].dropna().unique()
    with employee_col1:
        selected_managers = st.multiselect("Select Managers", options=manager_options)

    # Step 2: Filter data by selected managers
    manager_df = aggregated_df[aggregated_df["Manager"].isin(selected_managers)]

    # Step 3: Select KPI
    kpi_options = [
        'Small Hours', 'Medium Hours', 'Large Hours', 'Total Hours',
        'Total Job', 'Small Units', 'Medium Units', 'Large Units',
        'Total Units', 'JPH', 'Small UPH', 'Medium UPH', 'Large UPH', 'Total UPH'
    ]
    with employee_col2:
        selected_kpi = st.selectbox("Select KPI to rank employees", options=kpi_options)

    # Step 4: Sort and get top 10 employees across selected managers
    top_10_df = manager_df.sort_values(by=selected_kpi, ascending=False).head(10)

    # Step 5: Display login IDs
    st.write(f"🔟 Top 10 employees for **{selected_kpi}** under **{', '.join(selected_managers)}**:")
    st.dataframe(top_10_df[['Login', 'Employee Name', selected_kpi]],use_container_width=True, hide_index=True)
    

st.set_page_config(page_title="Function Rollup Dashboard", layout="wide")
st.info('Developed for @opokumej by @aakalkri for LCY3. This dashboard is developed to assist managers in pre shift placement of the Quantity Stowers!',icon='ℹ️')
st.title("📊 Quantity Stower Aggregator")
with st.expander('Click here to open upload dialog!'):
    uploaded_file = st.file_uploader("Upload the 7_day_function_rollup.xlsx file", type=["xlsx"])

if uploaded_file:
    # Load the sheets
    raw_df = pd.read_excel(uploaded_file, sheet_name="Raw 14-Day Data")
    agg_df = pd.read_excel(uploaded_file, sheet_name="Aggregated by Login")

    # # Sidebar filters
    # with st.sidebar:
    st.header("📌 Filters")
    filter_column_1, filter_column_2 = st.columns(2)
    with filter_column_1:
        date_filter = st.multiselect("Select Date(s)", options=raw_df["Date"].unique(), default=raw_df["Date"].unique())
    with filter_column_2:
        manager_filter = st.multiselect("Select Manager(s)", options=raw_df["Manager"].dropna().unique(), default=raw_df["Manager"].dropna().unique())

    # Filter raw data
    filtered_raw = raw_df[(raw_df["Date"].isin(date_filter)) & (raw_df["Manager"].isin(manager_filter))]
    # ========== KPIs ==========
    st.subheader("📌 Key KPIs Summary")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Units", f"{filtered_raw['Total Units'].sum():,.0f}",border=True)
    # kpi2.metric("Total Jobs", f"{filtered_raw['Total Job'].sum():,.0f}",border=True)
    total_hours = filtered_raw["Total Hours"].sum()
    kpi2.metric("Total Hours", f"{total_hours:,.2f}",border=True)
    kpi3.metric("Overall UPH", f"{filtered_raw['Total Units'].sum() / total_hours:.2f}" if total_hours > 0 else "0",border=True)
    kpi4.metric('Total Number of Employees',len(agg_df[agg_df["Manager"].isin(manager_filter)]), border=True)

    
    Row1col1, Row1col2 = st.columns([0.6,0.4], border=True)
    with Row1col1:
        # ========== Aggregated KPIs Table ==========
        st.subheader("👤 Aggregated Employee-Level Data")
        filtered_agg = agg_df[agg_df["Manager"].isin(manager_filter)]
        st.dataframe(filtered_agg,hide_index=True,use_container_width=True)
    with Row1col2:
        st.subheader("🥧 Pie Chart - Total Units by Manager")
        # Group total units by manager
        units_by_manager = filtered_raw.groupby("Manager", as_index=False)["Total Units"].sum()
        # Create pie chart
        fig_pie = px.pie(units_by_manager, names="Manager", values="Total Units", 
                        title="Total Units by Manager", hole=0.4)  # hole=0.4 gives a donut-style pie

        # Display
        st.plotly_chart(fig_pie, use_container_width=True)
    Row2col1, Row2col2 = st.columns([0.5,0.5], border=True)
    with Row2col1:
        show_top_10_employees_by_kpi(filtered_agg)
    with Row2col2:
        st.subheader("🏆 Managers Level Data")

        # Step 1: KPI selection
        kpi_options = [
            'Small Hours', 'Medium Hours', 'Large Hours', 'Total Hours',
            'Total Job', 'Small Units', 'Medium Units', 'Large Units',
            'Total Units', 'JPH', 'Small UPH', 'Medium UPH', 'Large UPH', 'Total UPH'
        ]
        selected_kpi = st.selectbox("Select KPI to visualize by Manager", options=kpi_options)

        # Step 2: Barplot of selected KPI by Manager
        manager_kpi = filtered_agg.groupby("Manager", as_index=False)[selected_kpi].sum()
        fig_mgr_kpi = px.bar(manager_kpi, x="Manager", y=selected_kpi,
                            title=f"{selected_kpi} by Manager", color=selected_kpi)
        st.plotly_chart(fig_mgr_kpi, use_container_width=True)

    
    # ========== Plotly Visualizations ==========
    st.subheader("📊 Visualizations")

    # Barplot: Total UPH per employee
    fig_uph = px.bar(filtered_agg.sort_values("Total UPH", ascending=False),
                     x="Employee Name", y="Total UPH",
                     color="Manager", title="Total UPH per Employee",
                     labels={"Total UPH": "Units per Hour"})
    fig_uph.update_layout(xaxis_tickangle=-45, height=500)
    st.plotly_chart(fig_uph, use_container_width=True)

    st.subheader("📈 Daily Trend - Total UPH per Employee")

    # Group by Date and Name, sum Total Units and Total Hours
    daily_data = filtered_raw.groupby(["Date", "Name"], as_index=False)[["Total Units", "Total Hours"]].sum()

    # Calculate Total UPH (Units Per Hour)
    daily_data['Total UPH'] = daily_data['Total Units'] / daily_data['Total Hours'].replace(0, pd.NA)

    # Drop rows where Total Hours was zero (to avoid division by zero issues)
    daily_data = daily_data.dropna(subset=['Total UPH'])

    # Create dropdown of employees
    employee_options = daily_data["Name"].unique()
    selected_employees = st.multiselect("Select Employee(s) to display", options=employee_options)

    if selected_employees:
        # Filter for selected employees
        filtered_daily = daily_data[daily_data["Name"].isin(selected_employees)]
        fig_daily = px.line(filtered_daily, x="Date", y="Total UPH", color="Name", markers=True,
                            title="Daily UPH per Employee")

        # Set y-axis to start at 0
        fig_daily.update_yaxes(range=[0, None])

        st.plotly_chart(fig_daily, use_container_width=True)
    else:
        st.info("Please select one or more employees from the dropdown above to display the trend.")

    
    # Optional: Export filtered data
    st.download_button("📥 Download Filtered Aggregated Data",
                       data=filtered_agg.to_csv(index=False),
                       file_name="filtered_aggregated_data.csv")
else:
    st.info("Upload a `7_day_function_rollup.xlsx` file to begin.")
