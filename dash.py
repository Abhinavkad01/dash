import streamlit as st
import pandas as pd
import plotly.express as px

# Set page config
st.set_page_config(page_title="Regulatory Dashboard", layout="wide")

# Title
st.markdown("<h1 style='text-align: center;'>📊 Regulatory Dashboard</h1>", unsafe_allow_html=True)

# Load Data
file_path = "REG.csv"
df = pd.read_csv(file_path)
df.columns = df.columns.str.strip()  # Remove spaces from column names

# Rename column for consistency
df.rename(columns={"Impact on Cost": "Cost Impact"}, inplace=True)

# Convert "Cost Impact" to numeric and handle errors
df["Cost Impact"] = pd.to_numeric(df["Cost Impact"], errors="coerce").fillna(0)

# Sidebar Filters
st.sidebar.header("🔍 Filters")
selected_country = st.sidebar.multiselect("Select Country", df["Country"].dropna().unique())
selected_industry = st.sidebar.multiselect("Select Industry", df["Industry"].dropna().unique())
selected_year = st.sidebar.slider("Select Year", int(df["Year"].min()), int(df["Year"].max()), 
                                  (int(df["Year"].min()), int(df["Year"].max())))
selected_reg_type = st.sidebar.multiselect("Select Regulation Type", df["Regulation Type"].dropna().unique())

# Search Box
st.sidebar.header("🔎 Search Regulation")
search_query = st.sidebar.text_input("Enter Regulation Name")

# **Filter Data Based on Sidebar Inputs**
filtered_df = df.copy()
if selected_country:
    filtered_df = filtered_df[filtered_df["Country"].isin(selected_country)]
if selected_industry:
    filtered_df = filtered_df[filtered_df["Industry"].isin(selected_industry)]
if selected_reg_type:
    filtered_df = filtered_df[filtered_df["Regulation Type"].isin(selected_reg_type)]
filtered_df = filtered_df[(filtered_df["Year"] >= selected_year[0]) & (filtered_df["Year"] <= selected_year[1])]

# **Display Key Metrics**
count_industry = df["Industry"].nunique()
count_country = df["Country"].nunique()
count_regulation = df["Regulation Name"].count()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="📌 Number of Industries", value=count_industry)
with col2:
    st.metric(label="🌍 Number of Countries", value=count_country)
with col3:
    st.metric(label="📜 Number of Regulations", value=count_regulation)

# **Trend Analysis - Line Chart**
if not filtered_df.empty:
    trend_data = filtered_df.groupby("Year")["Regulation Name"].count().reset_index()
    trend_data.columns = ["Year", "Regulation Count"]
    fig_trend = px.line(trend_data, x="Year", y="Regulation Count", 
                         title="📈 Trend of Regulations Over Years", markers=True)
    st.plotly_chart(fig_trend)

# **Corrected Bar Chart - Cost Impact Comparison**
if not filtered_df.empty:
    top_regulations = filtered_df.sort_values(by="Cost Impact", ascending=False).head(10)
    
    fig_comp = px.bar(
        top_regulations,
        x="Regulation Name",
        y="Cost Impact",
        color="Cost Impact",
        color_continuous_scale="RdBu",
        title="🏆 Top 10 Regulations by Cost Impact",
        labels={"Cost Impact": "Impact on Cost ($)"},
    )
    st.plotly_chart(fig_comp)

# **Pie Chart - Regulation Type Distribution**
if not filtered_df.empty:
    fig_pie = px.pie(filtered_df, names="Regulation Type", title="📊 Regulation Type Distribution")
    st.plotly_chart(fig_pie)

# **World Map - Regulations by Country**
if "Country" in df.columns:
    country_counts = df["Country"].value_counts().reset_index()
    country_counts.columns = ["Country", "Regulation Count"]
    fig_map = px.choropleth(
        country_counts, 
        locations="Country", 
        locationmode="country names", 
        color="Regulation Count", 
        title="🌍 Regulations by Country", 
        color_continuous_scale="plasma",
        template="plotly_dark"
    )
    st.plotly_chart(fig_map)

# **Search for a Regulation**
if search_query:
    search_results = df[df["Regulation Name"].str.contains(search_query, case=False, na=False)]
    if not search_results.empty:
        st.subheader("📜 Regulation Description")
        st.write(search_results["Description"].values[0])
        
        if "Cost Impact" in search_results.columns:
            st.subheader("💰 Impact on Cost")
            st.metric(label="Cost Impact", value=search_results["Cost Impact"].values[0])
    else:
        st.warning("⚠️ No regulation found. Try another search term.")

# **Regulation Comparison Feature**
st.sidebar.header("🔄 Compare Regulations")
compare_reg1 = st.sidebar.selectbox("Select Regulation 1", df["Regulation Name"].dropna().unique())
compare_reg2 = st.sidebar.selectbox("Select Regulation 2", df["Regulation Name"].dropna().unique())

if compare_reg1 and compare_reg2:
    compare_df = df[df["Regulation Name"].isin([compare_reg1, compare_reg2])]
    
    if "Cost Impact" in compare_df.columns:
        st.subheader("⚖️ Regulation Comparison")
        st.write(compare_df[["Regulation Name", "Country", "Industry", "Regulation Type", "Year", "Cost Impact"]])
        
        fig_comp = px.bar(
            compare_df,
            x="Regulation Name",
            y="Cost Impact",
            color="Regulation Name",
            title="⚖️ Comparison of Regulation Cost Impact",
            labels={"Cost Impact": "Impact on Cost ($)"},
        )
        st.plotly_chart(fig_comp)
    else:
        st.error("⚠️ Cost Impact column is missing. Cannot perform comparison.")

# **Filtered Data Table**
st.write("📋 **Filtered Data**")
st.dataframe(filtered_df)
