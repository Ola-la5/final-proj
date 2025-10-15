import streamlit as st  
import pandas as pd
import plotly.express as px
import sqlite3

# connect to db and load data
def load_data():
    with sqlite3.connect("db/mlb_history.db") as conn:
        stats = pd.read_sql_query("SELECT * FROM statistics WHERE league='American League';", conn)
        events = pd.read_sql_query("SELECT * FROM events;", conn)
    stats['year'] = pd.to_numeric(stats['year'], errors='coerce')
    stats['value'] = pd.to_numeric(stats['value'], errors='coerce')
    return stats, events

stats, events = load_data()

# sidebar filters
st.sidebar.header("filter options")

# year
years = sorted(stats['year'].dropna().unique())
selected_year = st.sidebar.selectbox("select year", ["all"] + list(map(int, years)))

# statistic
statistics = sorted(stats['statistic'].dropna().unique())
selected_stat = st.sidebar.selectbox("select statistic", ["all"] + statistics)

# filter data
filtered_df = stats.copy()
if selected_year != "all":
    filtered_df = filtered_df[filtered_df['year'] == selected_year]
if selected_stat != "all":
    filtered_df = filtered_df[filtered_df['statistic'] == selected_stat]

# main dashboard
st.title("MLB American League Statistics Dashboard")

# metric: number of records
st.metric("number of statistics records", len(filtered_df))

# bar chart: top players by selected statistic
st.subheader("top players by selected statistic")
if not filtered_df.empty:
    top_players = (
        filtered_df.groupby(['player', 'team'])['value']
        .sum()
        .reset_index()
        .nlargest(10, 'value')
    )
    fig_bar = px.bar(
        top_players,
        x='player',
        y='value',
        color='team',
        hover_data=['team'],
        labels={'value': 'stat value', 'player': 'player'}
    )
    st.plotly_chart(fig_bar)
else:
    st.write("no data for selected filters.")

# line chart: average statistic value per year
st.subheader("Average statistic value per year")

if selected_stat != "all":
    line_data = (
        stats[stats['statistic'] == selected_stat]
        .groupby('year')['value']
        .mean()
        .reset_index()
    )
    fig_line = px.line(
        line_data,
        x='year',
        y='value',
        title=f"average {selected_stat} value per year",
        markers=True
    )
else:
    line_data = (
        stats.groupby('year')['value']
        .mean()
        .reset_index()
    )
    fig_line = px.line(
        line_data,
        x='year',
        y='value',
        title="Average statistic value per year",
        markers=True
    )

st.plotly_chart(fig_line)

# table: show filtered data
st.subheader("filtered data")
st.dataframe(filtered_df.head(10))