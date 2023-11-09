# -*- coding: utf-8 -*-
###############################################################################
# FINANCIAL DASHBOARD EXAMPLE - v3
###############################################################################

#==============================================================================
# Initiating
#==============================================================================

# Libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from datetime import datetime, timedelta
import yfinance as yf
import streamlit as st

#==============================================================================
# Header
#==============================================================================

def render_header():
    """
    This function render the header of the dashboard with the following items:
        - Title
        - Dashboard description
        - 3 selection boxes to select: Ticker, Start Date, End Date
    """
    
    # Add dashboard title and description
    st.title("MY FINANCIAL DASHBOARD ⭐")
    col1, col2 = st.columns([1,5])
    col1.write("Data source:")
    col2.image('./img/yahoo_finance.png', width=100)
    
    # Add the ticker selection on the sidebar
    # Get the list of stock tickers from S&P500
    ticker_list = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol']
    
    # Add the selection boxes
    col1, col2, col3 = st.columns(3)  # Create 3 columns
    # Ticker name
    global ticker  # Set this variable as global, so the functions in all of the tabs can read it
    ticker = col1.selectbox("Ticker", ticker_list)
    # Begin and end dates
    global start_date, end_date  # Set this variable as global, so all functions can read it
    start_date = col2.date_input("Start date", datetime.today().date() - timedelta(days=30))
    end_date = col3.date_input("End date", datetime.today().date())
    
#==============================================================================
# Tab 1
#==============================================================================

def render_tab1():
    """
    This function render the Tab 1 - Company Profile of the dashboard.
    """
       
    # Show to stock image
    col1, col2, col3 = st.columns([1, 3, 1])
    col2.image('./img/stock_market.jpg', use_column_width=True,
               caption='Company Stock Information')
    
    # Get the company information
    @st.cache_data
    def GetCompanyInfo(ticker):
        """
        This function get the company information from Yahoo Finance.
        """
        return yf.Ticker(ticker).info
    
    # If the ticker is already selected
    if ticker != '':
        # Get the company information in list format
        info = GetCompanyInfo(ticker)
        
        # Show the company description using markdown + HTML
        st.write('**1. Business Summary:**')
        st.markdown('<div style="text-align: justify;">' + \
                    info['longBusinessSummary'] + \
                    '</div><br>',
                    unsafe_allow_html=True)
        
        # Show some statistics as a DataFrame
        st.write('**2. Key Statistics:**')
        info_keys = {'previousClose':'Previous Close',
                     'open'         :'Open',
                     'bid'          :'Bid',
                     'ask'          :'Ask',
                     'marketCap'    :'Market Cap',
                     'volume'       :'Volume'}
        company_stats = {}  # Dictionary
        for key in info_keys:
            company_stats.update({info_keys[key]:info[key]})
        company_stats = pd.DataFrame({'Value':pd.Series(company_stats)})  # Convert to DataFrame
        st.dataframe(company_stats)

#==============================================================================
# Tab 2
#==============================================================================

def render_tab2():
    """
    This function render the Tab 2 - Chart of the dashboard.
    """
        
    # Add table to show stock data
    @st.cache_data
    def GetStockData(ticker, start_date, end_date):
        stock_df = yf.Ticker(ticker).history(start=start_date, end=end_date)
        stock_df.reset_index(inplace=True)  # Drop the indexes
        stock_df['Date'] = stock_df['Date'].dt.date  # Convert date-time to date
        return stock_df
    
    # Add a check box to show/hid data
    # If the ticker name is selected and the check box is checked, show data
    show_data = st.checkbox("Show data table")
    if ticker != '':
        stock_price = GetStockData(ticker, start_date, end_date)
        if show_data:
            st.write('**Stock price data**')
            st.dataframe(stock_price, hide_index=True, use_container_width=True)
        
    # Add a candle stick chart using plotly
    # If the ticker name is selected show plot
    if ticker != '':
        st.write('**Candlestick Chart**')       
        fig = go.Figure(data=[go.Candlestick(
            x=stock_price['Date'],
            open=stock_price['Open'],
            high=stock_price['High'],
            low=stock_price['Low'],
            close=stock_price['Close'])])
        st.plotly_chart(fig, use_container_width=True)
        
#==============================================================================
# Main body
#==============================================================================
      
# Render the header
render_header()

# Render the tabs
tab1, tab2 = st.tabs(["Company profile", "Chart"])
with tab1:
    render_tab1()
with tab2:
    render_tab2()
    
# Customize the dashboard with CSS
st.markdown(
    """
    <style>
        .stApp {
            background: #F0F8FF;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
    
###############################################################################
# END
###############################################################################