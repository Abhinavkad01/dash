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
st.title("Regulatory Dashboard")

# Calculate Counts
count_industry = df["Industry"].nunique()
count_country = df["Country"].nunique()
count_regulation = df["Regulation Name"].nunique()

# Create a 3-column layout
col1, col2, col3 = st.columns(3)

# Display Metrics
with col1:
    st.metric(label="Count of Industry", value=count_industry)

with col2:
    st.metric(label="Count of Country", value=count_country)

with col3:
    st.metric(label="Count of Regulation Name", value=count_regulation)

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


# Display regulation description if searched
def display_regulation_description(search_query):
    if search_query:
        search_result = df[df["Regulation Name"].str.contains(search_query, case=False, na=False)]
        if not search_result.empty:
            st.write("### Regulation Details")
            st.markdown(f'<div style="background-color: black; color: white; padding: 10px; border-radius: 5px;">{search_result.iloc[0]["Description"]}</div>', unsafe_allow_html=True)
        else:
            st.write("No matching regulation found.")

display_regulation_description(search_query)


# In[7]:


# Display Filtered Table
st.write("### Filtered Data")
st.dataframe(filtered_df)


# In[ ]:




