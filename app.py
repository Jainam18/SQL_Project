import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
import plotly.graph_objects as go

def get_data(query):
    connection = mysql.connector.connect(
        host="localhost", user="root", password="@SqlProject", database="project"    )
    df = pd.read_sql(query, connection)
    connection.close()
    return df


st.set_page_config(page_title="Walmart Sales Analysis", layout="wide")


st.title("📊 Walmart Sales Analysis Dashboard")


query = """SELECT s2.Type as Store_Type, round(avg(s1.Weekly_Sales),2) as avg_weekly_sales 
from sales s1 JOIN stores s2 on s1.Store=s2.Store group by s2.Type order by s2.Type;"""
df = get_data(query)
fig1 = px.bar(df, x="Store_Type", y="avg_weekly_sales", color="avg_weekly_sales", color_continuous_scale=px.colors.qualitative.Set1, title="Sales Over Store Type")

query = """
with cte as (
SELECT s.store, s.Date, s.Weekly_Sales, f.MarkDown1+f.MarkDown2+f.MarkDown3+f.MarkDown4+f.MarkDown5 as Total_MarkDown, 
(CASE WHEN MarkDown1>0 or MarkDown2>0 or MarkDown3>0 or MarkDown4>0 or MarkDown5>0 THEN "Yes" else "No" end) as Discount
from sales s JOIN features f on s.Store=f.Store and s.Date=f.Date)
SELECT Discount, round(avg(Weekly_Sales),2) as Average_Sales from cte group by Discount;
"""
df = get_data(query)
fig2 = px.bar(df, x="Discount", y="Average_Sales", color="Average_Sales", color_continuous_scale=px.colors.qualitative.Set2, title="Comparison of Markdown Discount and Sales Performance")

query = """SELECT Type, count(Store) as number_of_stores from stores group by Type;"""
df = get_data(query)
fig3 = go.Figure(go.Pie(
    labels= df["Type"],
    values= df["number_of_stores"],
    hovertext=df["number_of_stores"],
    hole=0.3
))
fig3.update_layout(title_text="Distribution of Stores by Type")

query = """SELECT monthname(date) as "month", sum(Weekly_Sales) as total_sales from sales group by monthname(date) order by sum(Weekly_Sales) desc limit 5;"""
df = get_data(query)
fig4 = px.bar(df, x="month", y="total_sales", 
             color="total_sales", color_continuous_scale=px.colors.qualitative.Set1,
             title="Total Sales in top 5 Month")
fig4.update_traces(textposition="outside")
fig4.update_layout(
    xaxis_title="Month",
    yaxis_title="Total Revenue",
    coloraxis_showscale=False,
    plot_bgcolor="white",
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor="lightgrey")
)

col1, col2 = st.columns(2)
with col1:
    st.subheader("📉 How does many stores are there of each type?")
    st.plotly_chart(fig4, use_container_width=True)

with col2:
    st.subheader("📉 Which are top 5 months with highest performing sales?")
    st.plotly_chart(fig3, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    st.subheader("📉 What is the average weekly sales per store type?")
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.subheader("📉 Do markdowns significantly increase sales?")
    st.plotly_chart(fig1, use_container_width=True)

st.subheader("🔍 Run Your Own SQL Query")
custom_query = st.text_area("Enter your SQL query")
if st.button("Execute Query"):
    try:
        result = get_data(custom_query)
        st.write(result)
    except Exception as e:
        st.error(f"Error: {e}")

