import pandas as pd
import mysql.connector as sql
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
import numpy as np
import altair as alt

st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")
st.sidebar.title("Stock Analysis")

page = st.sidebar.radio(
    "Navigation",
    ("Market Summary", "Top Performing Stocks", "Least Performing Stocks", "Daily Returns", "Volatile Stocks", "Sector wise performance", "Stock price correlation", "Stock Daily Price")
)

# Full-page background image
st.markdown(
    """
    <style>
    /* Background for full main page */
    .stApp {
            background-color: #ADD8E6;
        }
    

    /* Make main block transparent */
    [data-testid="stAppViewContainer"] .main {
        background-color: rgba(255, 255, 255, 0.75) !important;
        border-radius: 10px;
    }

    /* Sidebar background */
    [data-testid="stSidebar"] > div:first-child {
        background-image: url("https://img.freepik.com/premium-vector/business-candle-stick-graph-chart-stock-market-investment-trading-white-background-design-bullish-point-trend-graph-vector-illustration_41981-1777.jpg?w=900");
        background-size: cover;
        background-position: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🏠 Home Page")

st.markdown(f"""
        <div style='font-size:20px; padding-top:30px; padding-bottom:30px; font-weight:bold;'>Welcome to Stock analysis of top 50 stocks in NSE</div>
    """, unsafe_allow_html=True)

# MySQL Connection
def dbconnect():
    return sql.connect(
    host="localhost",
    user="root",
    password="welcome1",
    database="ddsa"
    )

conn = dbconnect()
cursor = conn.cursor()

query = """SELECT
    ticker,
    price_date,
    close_price,
    COALESCE(
        ((close_price - LAG(close_price) OVER (PARTITION BY ticker ORDER BY price_date)) /
         LAG(close_price) OVER (PARTITION BY ticker ORDER BY price_date)) * 100,
        0
    ) AS daily_return
FROM ddsa.stock_price
ORDER BY ticker, price_date;
"""

df = pd.read_sql(query, conn)
conn.close()

# Calculate annualized volatility
volatility = df.groupby('ticker')['daily_return'].std() * np.sqrt(249)

# Convert to dataframe
vol_df = volatility.reset_index()
vol_df.columns = ['ticker', 'annual_volatility']

# Sort descending
vol_df = vol_df.sort_values(by='annual_volatility', ascending=False).reset_index(drop=True)
conn.close()


if page == "Market Summary":
    
    conn = dbconnect()
    df = pd.read_sql("""
        select ticker,price_date,open_price,close_price,volume 
        from ddsa.stock_price order by price_date,ticker asc;
    """, conn)
    conn.close()

    annual_return = df.groupby('ticker').apply(
        lambda x: round((((x['close_price'].iloc[-1] - x['close_price'].iloc[0]) / x['close_price'].iloc[0])) * 100,2)
    ).reset_index(name='annual_return')

    annual_return = annual_return.sort_values(by='annual_return', ascending=False).reset_index(drop=True)
    annual_return.rename(columns={'annual_return': 'Annual Return (%)'}, inplace=True)

    total_stocks = len(df['ticker'].unique())
    green_stocks = (annual_return['Annual Return (%)'] > 0).sum()
    red_stocks = (annual_return['Annual Return (%)'] <= 0).sum()
    avg_price = df['close_price'].mean()
    avg_volume = df['volume'].mean()
    
    st.subheader("Market Summary")
    st.metric("Total Stocks", total_stocks)
    st.metric("Green Stocks", green_stocks)
    st.metric("Red Stocks", red_stocks)
    st.metric("Average Price", round(avg_price,2))
    st.metric("Average Volume", int(avg_volume))

    st.subheader("Annual Return of All Stocks")

    fig, ax = plt.subplots(figsize=(4, 10))
    sns.heatmap(
        annual_return.set_index('ticker'),
        annot=True,
        cmap="RdYlGn",
        fmt=".2f",
        linewidths=.3,
        cbar_kws={"shrink": 1, "aspect": 40},
        annot_kws={"size": 4, "weight": "bold"},
        ax=ax
    )
    ax.set_ylabel("Stock", fontsize=5, fontweight="bold")
    ax.tick_params(axis='y', labelsize=5)
    plt.tight_layout()

    st.pyplot(fig)

if page == "Least Performing Stocks":
    st.subheader("Least Performing Stocks")

    conn = dbconnect()
    df = pd.read_sql("""
        select ticker,price_date,open_price,close_price 
        from ddsa.stock_price order by price_date,ticker asc;
    """, conn)
    conn.close()

    annual_return = df.groupby('ticker').apply(
        lambda x: round((((x['close_price'].iloc[-1] - x['close_price'].iloc[0]) / x['close_price'].iloc[0])) * 100,2)
    ).reset_index(name='Annual Return')

    annual_return = annual_return.sort_values(by='Annual Return', ascending=True).reset_index(drop=True)


    top10 = annual_return.head(10)  

    styled_df = top10.style.applymap(
        lambda x: 'color: red; font-weight: bold',
        subset=['Annual Return']
    )

    st.dataframe(styled_df, hide_index=True)
    st.subheader("Bar chart of Least 10 Stock performance")


    chart = alt.Chart(top10).mark_bar().encode(
        x=alt.X('ticker:N', sort='-y', title='Stock'),
        y=alt.Y('Annual Return:Q'),
        tooltip=['ticker', 'Annual Return']
    ).interactive().properties(width=800, height=400)

    st.altair_chart(chart, use_container_width=True)

if page == "Top Performing Stocks":
    st.title("Top Performing Stocks")

    conn = dbconnect()
    df = pd.read_sql("""
        select ticker,price_date,open_price,close_price 
        from ddsa.stock_price order by price_date,ticker asc;
    """, conn)
    conn.close()

    annual_return = df.groupby('ticker').apply(
        lambda x: round((((x['close_price'].iloc[-1] - x['close_price'].iloc[0]) / x['close_price'].iloc[0])) * 100,2)
    ).reset_index(name='Annual Return')

    annual_return = annual_return.sort_values(by='Annual Return', ascending=False).reset_index(drop=True)

    styled_df = annual_return.style.applymap(
        lambda x: 'color: green; font-weight: bold' if x > 0 else 'color: red; font-weight: bold',
        subset=['Annual Return']
    )
    st.subheader("Stock performance")
    st.dataframe(styled_df, hide_index=True)

    st.subheader("Bar chart of Stock performance")

    chart = alt.Chart(annual_return).mark_bar().encode(
        x=alt.X('ticker:N', sort='-y', title='Stock'),
        y=alt.Y('Annual Return:Q'),
        tooltip=['ticker', 'Annual Return']
    ).interactive().properties(width=800, height=400)

    st.altair_chart(chart, use_container_width=True)

    top10 = annual_return.head(10)  

    topstock = top10.style.applymap(
        lambda x: 'color: green; font-weight: bold',
        subset=['Annual Return']
    )

    st.subheader("Top 10 stock performance")

    st.dataframe(topstock, hide_index=True)
    
    st.subheader("Bar chart of Top 10 Stock performance")

    chart = alt.Chart(top10).mark_bar().encode(
        x=alt.X('ticker:N', sort='-y', title='Stock'),
        y=alt.Y('Annual Return:Q'),
        tooltip=['ticker', 'Annual Return']
    ).interactive().properties(width=800, height=400)

    st.altair_chart(chart, use_container_width=True)

if page == "Daily Returns":
    conn = dbconnect()
    query = """select * from (
    SELECT
    ticker,
    price_date,
    close_price,
    COALESCE(
        ((close_price - LAG(close_price) OVER (PARTITION BY ticker ORDER BY price_date)) /
         LAG(close_price) OVER (PARTITION BY ticker ORDER BY price_date)) * 100,
        0
    ) AS daily_return
FROM ddsa.stock_price) as t where t.daily_return != 0
ORDER BY t.ticker, t.price_date;
"""
    df= pd.read_sql(query, conn)
    conn.close()

    df1 = df.sort_values(by='daily_return', ascending=False)
    df1 = df1.rename(columns={'daily_return': 'Daily Return'})

    st.subheader("Top 10 Daily Returns")
    styled_df = df1.head(10).style.applymap(
        lambda x: 'color: red; font-weight: bold' if x < 0 else 'color: green; font-weight: bold',
        subset=['Daily Return']
    )
    st.dataframe(styled_df, hide_index=True)

    df2 = df1.sort_values(by=['ticker', 'price_date'], ascending=True)
    df2['Cumulative Return'] = df2.groupby('ticker')['Daily Return'].cumsum()
    df2 = df2.rename(columns={'ticker': 'Stock', 'price_date': 'Date'})

    st.subheader("Cumulative return of stocks")
    selected = st.selectbox("Choose Stock", df2['Stock'].unique())
    st.dataframe(df2[df2['Stock'] == selected], hide_index=True)


    top5 = (
        df2.groupby('Stock')['Cumulative Return'].max().sort_values(ascending=False).head(5).index
    )
    top5_df = df2[df2['Stock'].isin(top5)]

    st.subheader("📈 Top 5 Cumulative Performing Stocks")

    chart = alt.Chart(top5_df).mark_line().encode(
    x='Date:T',
    y='Cumulative Return:Q',
    color='Stock:N',
    tooltip=['Stock', 'Date', 'Cumulative Return']
    ).interactive().properties(width=900, height=400)

    st.altair_chart(chart, use_container_width=True)

    # Stock volatility 
if page == "Volatile Stocks":
    st.subheader("Stock Volatility Analysis")

    chart = alt.Chart(vol_df).mark_bar().encode(
        x=alt.X('ticker:N', sort='-y', title='Stock'),
        y=alt.Y('annual_volatility:Q', title='Annual Volatility'),
        tooltip=['ticker','annual_volatility']
    ).interactive().properties(width=800, height=400)

    st.altair_chart(chart, use_container_width=True)
    
    st.subheader("Top 10 volatile stocks")

    chart = alt.Chart(vol_df.head(10)).mark_bar().encode(
        x=alt.X('ticker:N', sort='-y', title='Stock'),
        y=alt.Y('annual_volatility:Q', title='Annual Volatility'),
        tooltip=['ticker','annual_volatility']
    ).interactive().properties(width=800, height=400)

    st.altair_chart(chart, use_container_width=True)


if page == "Sector wise performance":

    conn = dbconnect()
    sector_df = pd.read_sql("""
        select * from (
    SELECT
    ticker,
    sector,
    price_date,
    close_price,
    DATE_FORMAT(price_date, '%Y-%m') as price_month,
    COALESCE(
        ((close_price - LAG(close_price) OVER (PARTITION BY ticker ORDER BY price_date)) /
         LAG(close_price) OVER (PARTITION BY ticker ORDER BY price_date)) * 100,
        0
    ) AS daily_return
FROM ddsa.stock_price) as t where t.daily_return != 0
ORDER BY t.ticker, t.price_date;
    """, conn)
    conn.close()

    sector_df['Cumulative Return'] = sector_df.groupby(['ticker'])['daily_return'].cumsum()


    sector_df=sector_df.groupby(['sector','price_month']).agg({
    'daily_return': 'mean',
    'Cumulative Return': 'mean',
    'ticker': 'count'
}).reset_index()

    sector_monthly = sector_df.rename(columns={
    'daily_return': 'Avg Daily Return',
    'Cumulative Return': 'Avg Cumulative Return',
    'ticker': 'Stock Count'
    })
    st.subheader("Sector-wise Monthly Performance")
    st.dataframe(sector_monthly, hide_index=True)

    st.subheader("📈 Sector-wise Monthly Cumulative Return")
    sector_monthly['Month_str'] = sector_monthly['price_month'].astype(str)

    bar_chart = alt.Chart(sector_monthly).mark_bar().encode(
    x=alt.X('Month_str:N', title='Month'),
    xOffset='sector:N',
    y=alt.Y('Avg Cumulative Return:Q', title='Avg Cumulative Return'),
    color=alt.Color('sector:N', title='Sector'),
    tooltip=['sector', 'Avg Daily Return', 'Avg Cumulative Return', 'Stock Count']
).properties(
    width=900,
    height=400
).interactive()

    st.altair_chart(bar_chart, use_container_width=True)


    # Yearly return 

    conn = dbconnect()
    df = pd.read_sql("""
    select ticker,price_date,open_price,close_price,volume,sector 
        from ddsa.stock_price order by price_date,ticker asc;
    """, conn)
    conn.close()

    df['price_date'] = pd.to_datetime(df['price_date'])

    # Sort by stock and date
    df_sorted = df.sort_values(['ticker', 'price_date'])

    first_last = df_sorted.groupby('ticker').agg(
    first_close=('close_price', 'first'),
    last_close=('close_price', 'last')
    ).reset_index()

    first_last['Yearly Return (%)'] = ((first_last['last_close'] - first_last['first_close']) / 
                                   first_last['first_close']) * 100

    # Merge sector info if available
    first_last = first_last.merge(df[['ticker', 'sector']].drop_duplicates(), on='ticker')
    
    avg_yearly_sector = first_last.groupby('sector')['Yearly Return (%)'].mean().reset_index()
    avg_yearly_sector = avg_yearly_sector.rename(columns={'Yearly Return (%)': 'Avg Yearly Return (%)'})

    st.subheader("Average Yearly Return by Sector")
    st.dataframe(avg_yearly_sector, hide_index=True)

    chart = alt.Chart(avg_yearly_sector).mark_bar().encode(
        x='sector:N',
        y='Avg Yearly Return (%):Q',
        color='sector:N',
        tooltip=['sector', 'Avg Yearly Return (%)']
    ).properties(width=900, height=400)

    st.altair_chart(chart, use_container_width=True)
    

if page == 'Stock price correlation':
    conn = dbconnect()
    query = """
    SELECT ticker, price_date, close_price
    FROM ddsa.stock_price
    ORDER BY price_date ASC;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    
    # --- Pivot Data: Rows = Dates, Columns = Tickers, Values = Close Price ---
    price_pivot = df.pivot(index='price_date', columns='ticker', values='close_price')
    
    # --- Calculate Daily Percentage Change ---
    price_pct_change = price_pivot.pct_change() * 100
    
    # --- Compute Correlation Matrix ---
    corr_matrix = price_pct_change.corr()
        
    # --- Display Correlation Table ---
    st.subheader("Correlation Matrix")
    st.dataframe(corr_matrix, height=400)
    
    st.subheader("Correlation")

    fig = px.imshow(
    corr_matrix,
    text_auto=True,  # show correlation values on cells
    aspect="auto",
    color_continuous_scale="RdYlGn",
    zmin=-1, zmax=1
)
    fig.update_layout(
    width=900,
    height=700,
    xaxis_title="Stock",
    yaxis_title="Stock"
)
    st.plotly_chart(fig, use_container_width=True)

if page == "Stock Daily Price":
    conn = dbconnect()
    df = pd.read_sql("""
        select ticker,price_date,open_price,close_price,high,low,volume 
        from ddsa.stock_price order by price_date,ticker asc;
    """, conn)
    conn.close()

    st.subheader("Stock Daily Price Trend")

    # Convert date to datetime (important for filtering)
    df['price_date'] = pd.to_datetime(df['price_date'])

    # Sidebar filters / Main filters
    tickers = st.multiselect("Select Stock(s):", df['ticker'].unique(), default=df['ticker'].unique()[:2])

    start_date = st.date_input("Start Date", value=df['price_date'].min())
    end_date = st.date_input("End Date", value=df['price_date'].max())

    # Apply filters
    filtered_df = df[
        (df['ticker'].isin(tickers)) &
        (df['price_date'] >= pd.to_datetime(start_date)) &
        (df['price_date'] <= pd.to_datetime(end_date))
    ]

    # Create line chart
    line_chart = (
        alt.Chart(filtered_df)
        .mark_line(point=True)
        .encode(
            x=alt.X('price_date:T', title='Date'),
            y=alt.Y('close_price:Q', title='Close Price'),
            color='ticker:N',
            tooltip=['price_date:T', 'ticker:N', 'close_price:Q']
        )
        .properties(width=850, height=450)
        .interactive()
    )

    st.altair_chart(line_chart, use_container_width=True)






