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

# Key Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Industries", df["Industry"].nunique())
col2.metric("Countries", df["Country"].nunique())
col3.metric("Total Regulations", df["Regulation Name"].count())

# Line Chart - Trends Over Time
if not filtered_df.empty:
    fig_trend = px.line(filtered_df, x="Year", y="Regulation Name", title="Regulatory Trends Over Time", markers=True)
    st.plotly_chart(fig_trend)

# Comparison Feature
st.sidebar.header("Compare Regulations")
compare_options = st.sidebar.multiselect("Select Regulations to Compare", df["Regulation Name"].dropna().unique(), default=df["Regulation Name"].dropna().unique()[:2])
if len(compare_options) == 2:
    comp_df = df[df["Regulation Name"].isin(compare_options)]
    st.subheader("Regulation Comparison")
    st.dataframe(comp_df)

# Download Filtered Data
if not filtered_df.empty:
    st.download_button(label="Download Filtered Data", data=filtered_df.to_csv(index=False), file_name="filtered_data.csv", mime="text/csv")

# Display Filtered Table
st.write("### Filtered Data")
st.dataframe(filtered_df)

# Additional Insights Section
st.write("### Additional Insights")
if "Impact Score" in df.columns:
    avg_impact = df["Impact Score"].mean()
    st.metric(label="Average Regulatory Impact Score", value=f"{avg_impact:.2f}")

# Industry-Wise Impact
if "Industry" in df.columns and "Impact Score" in df.columns:
    impact_by_industry = df.groupby("Industry")["Impact Score"].mean().reset_index()
    fig_industry = px.bar(impact_by_industry, x="Industry", y="Impact Score", title="Industry-wise Average Impact Score", color="Impact Score", color_continuous_scale="blues")
    st.plotly_chart(fig_industry)

# Regulation Cost Analysis
if "Cost Impact" in df.columns:
    fig_cost = px.histogram(df, x="Cost Impact", title="Distribution of Regulation Costs", nbins=20, color_discrete_sequence=["#EF553B"])
    st.plotly_chart(fig_cost)
