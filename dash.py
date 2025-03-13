#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
file_path = "REG.csv"  # Ensure this is the correct path
df = pd.read_csv(file_path)
df.columns = df.columns.str.strip()  # Remove leading/trailing spaces

# Sidebar filters
st.sidebar.header("Filters")
selected_country = st.sidebar.multiselect("Select Country", df["Country"].dropna().unique())
selected_industry = st.sidebar.multiselect("Select Industry", df["Industry"].dropna().unique())
selected_year = st.sidebar.slider("Select Year", int(df["Year"].min()), int(df["Year"].max()), (int(df["Year"].min()), int(df["Year"].max())))
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

# Create a 3-column layout for Metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Number of Industries", value=count_industry)
with col2:
    st.metric(label="Number of Countries", value=count_country)
with col3:
    st.metric(label="Number of Regulations", value=count_regulation)

# Bar Chart - Number of Regulations by Year
if not filtered_df.empty:
    reg_by_year = filtered_df["Year"].value_counts().reset_index()
    reg_by_year.columns = ["Year", "Count"]
    fig = px.bar(reg_by_year, x="Year", y="Count", title="Number of Regulations by Year", color="Count", color_continuous_scale="viridis")
    st.plotly_chart(fig)

    # Pie Chart - Regulation Type Distribution
    fig_pie = px.pie(filtered_df, names="Regulation Type", title="Regulation Type Distribution")
    st.plotly_chart(fig_pie)

# World Map - Regulations by Country
if "Country" in df.columns:
    country_counts = df["Country"].value_counts().reset_index()
    country_counts.columns = ["Country", "Regulation Count"]
    
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
    filtered_df = df[df["Regulation Name"].str.contains(search_query, case=False, na=False)]

    if not filtered_df.empty:
        st.subheader("Regulation Description")
        st.write(filtered_df["Description"].values[0])

        # Display Impact on Cost
        if "Cost Impact" in filtered_df.columns:
            st.subheader("Impact on Cost")
            st.metric(label="Cost Impact", value=f"${filtered_df['Cost Impact'].values[0]:,.2f}")

            # Horizontal Bar Chart for Cost Impact
            fig = px.bar(filtered_df, 
                         x="Cost Impact", 
                         y="Regulation Name", 
                         orientation="h",
                         title="Cost Impact of Selected Regulation",
                         color="Cost Impact",
                         color_continuous_scale="reds")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No regulation found. Try another search term.")

# 📌 **NEW FEATURE: Trend Analysis - Line Chart**
if not filtered_df.empty:
    trend_data = filtered_df.groupby("Year")["Regulation Name"].count().reset_index()
    trend_data.columns = ["Year", "Regulation Count"]

    fig_trend = px.line(trend_data, x="Year", y="Regulation Count", title="Trend of Regulations Over Years", markers=True)
    st.plotly_chart(fig_trend)

# 📌 **NEW FEATURE: Regulation Comparison Tool**
st.sidebar.header("Compare Two Regulations")
reg1 = st.sidebar.selectbox("Select First Regulation", df["Regulation Name"].dropna().unique())
reg2 = st.sidebar.selectbox("Select Second Regulation", df["Regulation Name"].dropna().unique())

if reg1 and reg2:
    compare_df = df[df["Regulation Name"].isin([reg1, reg2])]

    if not compare_df.empty:
        st.subheader(f"Comparison: {reg1} vs {reg2}")
        st.write(compare_df[["Regulation Name", "Country", "Industry", "Regulation Type", "Year", "Cost Impact"]])

        if "Cost Impact" in compare_df.columns:
            fig_compare = px.bar(compare_df, x="Regulation Name", y="Cost Impact", title="Cost Impact Comparison", color="Regulation Name")
            st.plotly_chart(fig_compare)

# 📌 **NEW FEATURE: Download Filtered Data**
if not filtered_df.empty:
    st.subheader("Download Filtered Data")
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "filtered_data.csv", "text/csv")

# Display Filtered Table
st.write("### Filtered Data")
st.dataframe(filtered_df)
