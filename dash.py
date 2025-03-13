#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
file_path = "REG.csv"
df = pd.read_csv(file_path)
df.columns = df.columns.str.strip()  # Remove leading/trailing spaces

# Sidebar filters
st.sidebar.header("Filters")
selected_country = st.sidebar.multiselect("Select Country", df["Country"].dropna().unique())
selected_industry = st.sidebar.multiselect("Select Industry", df["Industry"].dropna().unique())
selected_year = st.sidebar.slider("Select Year", int(df["Year"].min()), int(df["Year"].max()), 
                                  (int(df["Year"].min()), int(df["Year"].max())))
selected_reg_type = st.sidebar.multiselect("Select Regulation Type", df["Regulation Type"].dropna().unique())

# Search Box for Regulation Name
st.sidebar.header("Search Regulation")
search_query = st.sidebar.text_input("Enter Regulation Name")

# Filter data
filtered_df = df.copy()
if selected_country:
    filtered_df = filtered_df[filtered_df["Country"].isin(selected_country)]
if selected_industry:
    filtered_df = filtered_df[filtered_df["Industry"].isin(selected_industry)]
if selected_reg_type:
    filtered_df = filtered_df[filtered_df["Regulation Type"].isin(selected_reg_type)]
filtered_df = filtered_df[(filtered_df["Year"] >= selected_year[0]) & (filtered_df["Year"] <= selected_year[1])]

# Title
st.markdown("<h1 style='text-align: center;'>Regulatory Dashboard</h1>", unsafe_allow_html=True)

# Calculate Counts
count_industry = df["Industry"].nunique()
count_country = df["Country"].nunique()
count_regulation = df["Regulation Name"].count()

# Create a 3-column layout
col1, col2, col3 = st.columns(3)

# Display Metrics
with col1:
    st.metric(label="Number of Industries", value=count_industry)

with col2:
    st.metric(label="Number of Countries", value=count_country)

with col3:
    st.metric(label="Number of Regulations", value=count_regulation)

# Bar Chart - Number of Regulations by Year with Trend Line
if not filtered_df.empty:
    reg_by_year = filtered_df["Year"].value_counts().reset_index()
    reg_by_year.columns = ["Year", "Count"]
    fig = px.bar(reg_by_year, x="Year", y="Count", title="Number of Regulations by Year", 
                 color="Count", color_continuous_scale="viridis", trendline="ols")
    st.plotly_chart(fig)

    # Pie Chart - Regulation Type Distribution
    fig_pie = px.pie(filtered_df, names="Regulation Type", title="Regulation Type Distribution")
    st.plotly_chart(fig_pie)

# World Map - Highlighted Countries with Regulations
if "Country" in df.columns:
    country_counts = df["Country"].value_counts().reset_index()
    country_counts.columns = ["Country", "Regulation Count"]
    
    # Ensure country names are valid
    country_counts["Country"] = country_counts["Country"].astype(str)

    fig_map = px.choropleth(
        country_counts, 
        locations="Country", 
        locationmode="country names", 
        color="Regulation Count", 
        title="Regulations by Country", 
        color_continuous_scale="plasma",
        template="plotly_dark"
    )
    st.plotly_chart(fig_map)

# User Input for Searching a Regulation
search_query = st.text_input("Search for a Regulation")

# Filter Data Based on Search Query
if search_query:
    search_results = df[df["Regulation Name"].str.contains(search_query, case=False, na=False)]
    
    if not search_results.empty:
        st.subheader("Regulation Description")
        st.write(search_results["Description"].values[0])

        # Display Impact on Cost if available
        if "Cost Impact" in search_results.columns:
            st.subheader("Impact on Cost")
            st.metric(label="Cost Impact", value=f"${search_results['Cost Impact'].values[0]:,.2f}")

            # Cost Impact Bar Chart
            fig = px.bar(search_results, x="Cost Impact", y="Regulation Name", orientation="h",
                         title="Cost Impact of Selected Regulation", color="Cost Impact", color_continuous_scale="reds")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No regulation found. Try another search term.")

# Regulation Comparison Feature
st.sidebar.header("Compare Regulations")
compare_reg1 = st.sidebar.selectbox("Select Regulation 1", df["Regulation Name"].dropna().unique())
compare_reg2 = st.sidebar.selectbox("Select Regulation 2", df["Regulation Name"].dropna().unique())

if compare_reg1 and compare_reg2:
    compare_df = df[df["Regulation Name"].isin([compare_reg1, compare_reg2])]
    
    # Ensure required columns exist before selecting
    required_columns = ["Regulation Name", "Country", "Industry", "Regulation Type", "Year", "Cost Impact"]
    available_columns = [col for col in required_columns if col in compare_df.columns]

    if available_columns:
        st.subheader("Regulation Comparison")
        st.write(compare_df[available_columns])
        
        # Comparison Bar Chart
        fig_comp = px.bar(compare_df, x="Regulation Name", y="Cost Impact", color="Regulation Name",
                          title="Comparison of Regulation Cost Impact")
        st.plotly_chart(fig_comp)
    else:
        st.error("No valid columns found for comparison.")

# Display Filtered Table
st.write("### Filtered Data")
st.dataframe(filtered_df)
