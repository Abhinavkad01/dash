#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
file_path = "REG.csv"
df = pd.read_csv(file_path)
df.columns = df.columns.str.strip()  # Remove leading/trailing spaces


# In[2]:


# Sidebar filters
st.sidebar.header("Filters")
selected_country = st.sidebar.multiselect("Select Country", df["Country"].dropna().unique())
selected_industry = st.sidebar.multiselect("Select Industry", df["Industry"].dropna().unique())
selected_year = st.sidebar.slider("Select Year", int(df["Year"].min()), int(df["Year"].max()), (int(df["Year"].min()), int(df["Year"].max())))
selected_reg_type = st.sidebar.multiselect("Select Regulation Type", df["Regulation Type"].dropna().unique())


# In[3]:


# Search Box for Regulation Name
st.sidebar.header("Search Regulation")
search_query = st.sidebar.text_input("Enter Regulation Name")


# In[4]:


# Filter data
filtered_df = df.copy()
if selected_country:
    filtered_df = filtered_df[filtered_df["Country"].isin(selected_country)]
if selected_industry:
    filtered_df = filtered_df[filtered_df["Industry"].isin(selected_industry)]
if selected_reg_type:
    filtered_df = filtered_df[filtered_df["Regulation Type"].isin(selected_reg_type)]
filtered_df = filtered_df[(filtered_df["Year"] >= selected_year[0]) & (filtered_df["Year"] <= selected_year[1])]


# In[5]:


# Title
# Centered Title
st.markdown("<h1 style='text-align: center;'>Regulatory Dashboard</h1>", unsafe_allow_html=True)

# Calculate Counts
count_industry = df["Industry"].nunique()
count_country = df["Country"].nunique()
count_regulation = df["Description"].nunique()

# Create a 3-column layout
col1, col2, col3 = st.columns(3)

# Display Metrics
with col1:
    st.metric(label="Number of Industry", value=count_industry)

with col2:
    st.metric(label="Number of Country", value=count_country)

with col3:
    st.metric(label="Number of Regulations", value=count_Description)

# Bar Chart - Number of Regulations by Year
if not filtered_df.empty:
    reg_by_year = filtered_df["Year"].value_counts().reset_index()
    reg_by_year.columns = ["Year", "Count"]
    fig = px.bar(reg_by_year, x="Year", y="Count", title="Number of Regulations by Year", color="Count", color_continuous_scale="viridis")
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


# In[6]:


# User Input for Searching a Regulation
search_query = st.text_input("Search for a Regulation")

# Filter Data Based on Search Query
if search_query:
    filtered_df = df[df["Regulation Name"].str.contains(search_query, case=False, na=False)]

    if not filtered_df.empty:
        # Display Regulation Description
        st.subheader("Regulation Description")
        st.write(filtered_df["Description"].values[0])

        # Display Impact on Cost
        if "Cost Impact" in filtered_df.columns:
            st.subheader("Impact on Cost")
            st.metric(label="Cost Impact", value=f"${filtered_df['Cost Impact'].values[0]:,.2f}")

            # Optional: Add a Horizontal Bar Chart for Visual Representation
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


# In[7]:


# Display Filtered Table
st.write("### Filtered Data")
st.dataframe(filtered_df)


# In[ ]:




