import streamlit as st
import pandas as pd
import plotly.express as px

# App Configuration
st.set_page_config(page_title="Global Regulatory Insights", layout="wide")

# Load Data
file_path = "REG.csv"
df = pd.read_csv(file_path)
df.columns = df.columns.str.strip()
df.rename(columns={"Impact on Cost": "Cost Impact"}, inplace=True)

def convert_cost_impact(value):
    value = str(value).lower()
    if "increase" in value and "decrease" in value:
        return 0
    elif "increase" in value:
        return 1
    elif "decrease" in value:
        return -1
    return 0

df["Cost Impact"] = df["Cost Impact"].apply(convert_cost_impact)

# Sidebar - Filters
st.sidebar.header("🔍 Advanced Filters")
selected_country = st.sidebar.multiselect("🌍 Select Country", df["Country"].dropna().unique())
selected_industry = st.sidebar.multiselect("🏭 Select Industry", df["Industry"].dropna().unique())
selected_year = st.sidebar.slider("📅 Select Year Range", int(df["Year"].min()), int(df["Year"].max()), (int(df["Year"].min()), int(df["Year"].max())))
selected_reg_type = st.sidebar.multiselect("📜 Select Regulation Type", df["Regulation Type"].dropna().unique())

st.sidebar.header("🔎 Search Regulation")
search_query = st.sidebar.text_input("Enter Regulation Name")

# Data Filtering
filtered_df = df.copy()
if selected_country:
    filtered_df = filtered_df[filtered_df["Country"].isin(selected_country)]
if selected_industry:
    filtered_df = filtered_df[filtered_df["Industry"].isin(selected_industry)]
if selected_reg_type:
    filtered_df = filtered_df[filtered_df["Regulation Type"].isin(selected_reg_type)]
filtered_df = filtered_df[(filtered_df["Year"] >= selected_year[0]) & (filtered_df["Year"] <= selected_year[1])]

# Main Title
st.markdown("""
    <h1 style='text-align: center; font-size: 36px; color: #524585;'>🌍 Global Regulatory Insights Dashboard</h1>
""", unsafe_allow_html=True)

# Metrics Overview
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="🏭 Industries Covered", value=df["Industry"].nunique())
with col2:
    st.metric(label="🌍 Countries Impacted", value=df["Country"].nunique())
with col3:
    st.metric(label="📜 Total Regulations", value=df["Regulation Name"].count())

# Visualization - Trends
if not filtered_df.empty:
    trend_data = filtered_df.groupby("Year")["Regulation Name"].count().reset_index()
    trend_data.columns = ["Year", "Regulation Count"]
    fig_trend = px.line(trend_data, x="Year", y="Regulation Count", title="📈 Regulatory Trends Over Years", markers=True, template="plotly_dark")
    st.plotly_chart(fig_trend)

# Regulations per Country per Year
if not filtered_df.empty:
    country_year_data = filtered_df.groupby(["Year", "Country"]).size().reset_index(name="Regulation Count")
    fig_bar = px.bar(country_year_data, x="Year", y="Regulation Count", color="Country", barmode="stack", title="🌍 Regulations per Country per Year", template="plotly_dark")
    st.plotly_chart(fig_bar)

import plotly.graph_objects as go
import plotly.express as px

import pandas as pd
import plotly.express as px
import streamlit as st

# Load data
df = pd.read_csv("/mnt/data/REG.csv")

# Check if "Regulation Type" column exists
if "Regulation Type" in df.columns:
    # Count occurrences of each regulation type
    reg_counts = df["Regulation Type"].value_counts().reset_index()
    reg_counts.columns = ["Regulation Type", "Count"]
    
    # Calculate percentage
    reg_counts["Percentage"] = (reg_counts["Count"] / reg_counts["Count"].sum()) * 100

    # Group small categories under "Others"
    threshold = 2  # Define percentage threshold
    reg_counts["Regulation Type"] = reg_counts.apply(
        lambda x: x["Regulation Type"] if x["Percentage"] >= threshold else "Others", axis=1
    )

    # Aggregate "Others" category
    reg_counts = reg_counts.groupby("Regulation Type", as_index=False).sum()

    # Create a clean donut chart
    fig_donut = px.pie(
        reg_counts, 
        names="Regulation Type", 
        values="Count", 
        title="📜 Regulation Type Distribution",
        hole=0.4,  # Donut effect
        color_discrete_sequence=px.colors.sequential.Magma,  # Professional color palette
        template="plotly_dark"
    )

    # Improve readability
    fig_donut.update_traces(textinfo="percent+label", pull=[0.05] * len(reg_counts))

    fig_donut.update_layout(
        title=dict(
            font=dict(size=22, color="white"),
            x=0.5
        ),
        showlegend=True,
        legend=dict(
            title="Regulation Types",
            font=dict(size=12, color="white")
        ),
        margin=dict(l=50, r=50, t=100, b=50)
    )

    # Display in Streamlit
    st.plotly_chart(fig_donut)
# Global Regulatory Heatmap
if "Country" in df.columns:
    country_counts = df["Country"].value_counts().reset_index()
    country_counts.columns = ["Country", "Regulation Count"]
    fig_map = px.choropleth(
        country_counts, 
        locations="Country", 
        locationmode="country names", 
        color="Regulation Count", 
        title="🌍 Global Regulations by Country", 
        color_continuous_scale="viridis",
        template="plotly_dark"
    )
    st.plotly_chart(fig_map)

# Search Feature
if search_query:
    search_results = df[df["Regulation Name"].str.contains(search_query, case=False, na=False)]
    if not search_results.empty:
        st.subheader("📜 Regulation Details")
        st.write(search_results.iloc[0]["Description"])
    else:
        st.warning("⚠️ No matching regulations found. Try another search term.")

# Regulation Comparison
st.sidebar.header("⚖ Compare Regulations")
compare_reg1 = st.sidebar.selectbox("📌 Select Regulation 1", df["Regulation Name"].dropna().unique())
compare_reg2 = st.sidebar.selectbox("📌 Select Regulation 2", df["Regulation Name"].dropna().unique())

if compare_reg1 and compare_reg2:
    compare_df = df[df["Regulation Name"].isin([compare_reg1, compare_reg2])]
    if "Cost Impact" in compare_df.columns:
        st.subheader("⚖ Regulation Comparison")
        st.write(compare_df[["Regulation Name", "Country", "Industry", "Regulation Type", "Year", "Cost Impact"]])
        fig_comp = px.bar(
            compare_df,
            x="Regulation Name",
            y="Cost Impact",
            color="Regulation Name",
            title="💰 Comparison of Regulation Cost Impact",
            labels={"Cost Impact": "Impact on Cost"},
            template="plotly_dark"
        )
        st.plotly_chart(fig_comp)
    else:
        st.error("⚠️ Cost Impact column is missing. Cannot perform comparison.")

# Display Filtered Table
st.write("### 📊 Filtered Data")
st.dataframe(filtered_df)
