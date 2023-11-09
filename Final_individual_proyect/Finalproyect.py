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
from plotly.subplots import make_subplots

#==============================================================================
# HOT FIX FOR YFINANCE .INFO METHOD
# Ref: https://github.com/ranaroussi/yfinance/issues/1729
#==============================================================================

import requests
import urllib

class YFinance:
    user_agent_key = "User-Agent"
    user_agent_value = ("Mozilla/5.0 (Windows NT 6.1; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/58.0.3029.110 Safari/537.36")
    
    def __init__(self, ticker):
        self.yahoo_ticker = ticker

    def __str__(self):
        return self.yahoo_ticker

    def _get_yahoo_cookie(self):
        cookie = None

        headers = {self.user_agent_key: self.user_agent_value}
        response = requests.get("https://fc.yahoo.com",
                                headers=headers,
                                allow_redirects=True)

        if not response.cookies:
            raise Exception("Failed to obtain Yahoo auth cookie.")

        cookie = list(response.cookies)[0]

        return cookie

    def _get_yahoo_crumb(self, cookie):
        crumb = None

        headers = {self.user_agent_key: self.user_agent_value}

        crumb_response = requests.get(
            "https://query1.finance.yahoo.com/v1/test/getcrumb",
            headers=headers,
            cookies={cookie.name: cookie.value},
            allow_redirects=True,
        )
        crumb = crumb_response.text

        if crumb is None:
            raise Exception("Failed to retrieve Yahoo crumb.")

        return crumb

    @property
    def info(self):
        # Yahoo modules doc informations :
        # https://cryptocointracker.com/yahoo-finance/yahoo-finance-api
        cookie = self._get_yahoo_cookie()
        crumb = self._get_yahoo_crumb(cookie)
        info = {}
        ret = {}

        headers = {self.user_agent_key: self.user_agent_value}

        yahoo_modules = ("assetProfile,"  # longBusinessSummary
                         "summaryDetail,"
                         "financialData,"
                         "indexTrend,"
                         "defaultKeyStatistics")

        url = ("https://query1.finance.yahoo.com/v10/finance/"
               f"quoteSummary/{self.yahoo_ticker}"
               f"?modules={urllib.parse.quote_plus(yahoo_modules)}"
               f"&ssl=true&crumb={urllib.parse.quote_plus(crumb)}")

        info_response = requests.get(url,
                                     headers=headers,
                                     cookies={cookie.name: cookie.value},
                                     allow_redirects=True)

        info = info_response.json()
        info = info['quoteSummary']['result'][0]

        for mainKeys in info.keys():
            for key in info[mainKeys].keys():
                if isinstance(info[mainKeys][key], dict):
                    try:
                        ret[key] = info[mainKeys][key]['raw']
                    except (KeyError, TypeError):
                        pass
                else:
                    ret[key] = info[mainKeys][key]

        return ret

    
#==============================================================================
# Tab 1
#==============================================================================

def tab1():
    st.title('Summary')
    st.header(ticker)    
    # Get the company information
    @st.cache_data
    def GetCompanyInfo(ticker):
        """
        This function get the company information from Yahoo Finance.
        """
        return YFinance(ticker).info

    

    # If the ticker is already selected
    if ticker != '':
        # Get the company information
        info = GetCompanyInfo(ticker)
        
        # Show the company description using markdown + HTML
        st.write('**1. Business Summary:**')
        st.markdown('<div style="text-align: justify;">' + \
                    info['longBusinessSummary'] + \
                    '</div><br>',
                    unsafe_allow_html=True)
        
        # Show the company major institutional holders
        st.write('**2. Major Holders:**')
        stocks=yf.Ticker(ticker) 
        st.write(stocks.institutional_holders)
        st.write(stocks.major_holders)
        
        st.write('**3. Chart:**')
        stock_data =yf.download(tickers = ticker,period = "3y")
        
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
        with col1: date1 = st.button('1M')
        with col2: date2 = st.button('3M')
        with col3: date3 = st.button('6M')
        with col4: date4 = st.button('YTD')
        with col5: date5 = st.button('1Y')
        with col6: date6 = st.button('3Y')
        with col7: date7 = st.button('5Y')
        with col8: date8 = st.button('MAX')
        
       # Create diferent if functions to give the possibility of choosing a period to show in the graph below
        if date1:
            stock_data=yf.download(tickers = ticker,period = "1mo")
        if date2:
            stock_data=yf.download(tickers = ticker,period = "3mo")
        if date3:
            stock_data=yf.download(tickers = ticker,period = "6mo")
        if date4:
            stock_data=yf.download(tickers = ticker,period = "ytd")
        if date5:
            stock_data=yf.download(tickers = ticker,period = "1y")
        if date6:
            stock_data=yf.download(tickers = ticker,period = "3y")
        if date7:
            stock_data=yf.download(tickers = ticker,period = "5y")
        if date8:
            stock_data=yf.download(tickers = ticker)
        
        # Create a grpah that show the close price of  a stock in a period of time with intervals per day
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Close'], fill='tozeroy',  name=ticker))

        fig.update_layout(
            title=f"{ticker} Stock Price",
            xaxis_title="Date",
            yaxis_title="Price",
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.write('**4. Business stats:**')
        # Create a dictionary with data you want to display (modify as needed)
        summary_data = {
            'Previous Close': info.get('previousClose'),
            'Open': info.get('open'),
            'Bid ': info.get('bid'),
            'Ask': info.get('ask'),
            'Volume': info.get('volume'),
            'Average Volume': info.get('averageVolume'),
            'Market Cap': info.get('marketCap'),
            'Enterprise Value': info.get('enterpriseValue'),
            'Forward P/E': info.get('forwardPE'),
            'Dividend Rate': info.get('dividendYield'),
            'Dividend Rate (%)': info.get('dividendRate'),
            }
         
         # Convert the data into a Pandas DataFrame for displaying as a table
        summary_df = pd.DataFrame.from_dict({'Value':pd.Series(summary_data)})
     
         # Display the summary data as a table
        st.table(summary_df)



  


        
#==============================================================================
# Tab 2
#==============================================================================

def tab2():
    if ticker != '':
        #
        graph=st.selectbox("Select the type of graph:", ['Line','Candle'])
        col1, col2= st.columns(2)
        start_date = col1.date_input("Start date", datetime.today().date() - timedelta(days=365))
        end_date = col2.date_input("End date", datetime.today().date()- timedelta(days=1))
        
        
        
        interval1 = st.selectbox("Select an interval:", ['Day','Week','Month'])
        if interval1 == 'Month':
            interval = '1mo'
        elif interval1 == 'Week':
            interval = '1wk'
        elif interval1 == 'Day':
            interval = '1d'
        
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
        with col1: date1 = st.button('1M')
        with col2: date2 = st.button('3M')
        with col3: date3 = st.button('6M')
        with col4: date4 = st.button('YTD')
        with col5: date5 = st.button('1Y')
        with col6: date6 = st.button('3Y')
        with col7: date7 = st.button('5Y')
        with col8: date8 = st.button('MAX')
        
        stock_data =yf.download(tickers = ticker,period = "1y",interval="1d")
        
        if date1:
            stock_data=yf.download(tickers = ticker,period = "1mo",interval='1d')
        elif date2:
            stock_data=yf.download(ticker,period = "3mo",interval=interval)
        elif date3:
            stock_data=yf.download(tickers = ticker,period = "6mo",interval=interval)
        elif date4:
            stock_data=yf.download(tickers = ticker,period = "ytd",interval=interval)
        elif date5:
            stock_data=yf.download(tickers = ticker,period = "1y",interval=interval)
        elif date6:
            stock_data=yf.download(tickers = ticker,period = "3y",interval=interval)
        elif date7:
            stock_data=yf.download(tickers = ticker,period = "5y",interval=interval)
        elif date8:
            stock_data=yf.download(tickers = ticker)
        else:
            stock_data = yf.download(ticker, start_date, end_date,interval=interval)
        
        
        if graph == 'Line':
            fig1 = make_subplots(specs=[[{"secondary_y": True}]])
            fig1.add_trace(go.Scatter(x=stock_data.index,y=stock_data['Close'],name='Close Price'),secondary_y=False)
            fig1.add_trace(go.Scatter(x=stock_data.index,y=stock_data['Close'].rolling(window=50).mean(),marker_color='black',name='Moving Average (50 Days)'))
            fig1.add_trace(go.Bar(x=stock_data.index,y=stock_data['Volume'],name='Volume'),secondary_y=True)
            fig1.update_layout(yaxis2=dict(range=[0, stock_data['Volume'].max() * 4]))
            fig1.update_yaxes(visible=False, secondary_y=True)
            fig1.update_layout(legend=dict(orientation="h",yanchor="bottom",y=1.02))
            st.plotly_chart(fig1, use_container_width=True)
        if graph == 'Candle':
            fig2 = make_subplots(specs=[[{"secondary_y": True}]])
            fig2.add_trace(go.Candlestick(x=stock_data.index,open=stock_data['Open'], high=stock_data['High'],low=stock_data['Low'], close=stock_data['Close']),secondary_y=False)
            fig2.add_trace(go.Scatter(x=stock_data.index,y=stock_data['Close'].rolling(window=50).mean(),marker_color='black',name='Moving Average (50 Days)'))
            fig2.add_trace(go.Bar(x=stock_data.index,y=stock_data['Volume'],name='Volume'),secondary_y=True)
            fig2.update_layout(legend=dict(orientation="h",yanchor="bottom",y=1.02))
            fig2.layout.yaxis2.showgrid = False
            fig2.update_yaxes(visible=False, secondary_y=True)
            fig2.update_layout(yaxis2=dict(range=[0, stock_data['Volume'].max() * 4]))
            st.plotly_chart(fig2, use_container_width=True)  

            

        
#==============================================================================
# Tab 3
#==============================================================================

def tab3():
    st.title(ticker)
    st.write("Data source: Yahoo Finance")
    st.header('Financial Statements')
    
    # To choose between the intervals and type of data
    view = st.selectbox("Choose intervals:", ['Yearly', 'Quarterly'])    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        FinOpt1 = st.button('Income Statement')
    with col2:
        FinOpt2 = st.button('Balance Sheet')
    with col3:
        FinOpt3 = st.button('Cash Flow')
        
        
    stock = yf.Ticker(ticker)
    
    if FinOpt1:
        if view == 'Quarterly':
            income_statement = stock.quarterly_financials
            st.write(income_statement)
        else:
            income_statement = stock.financials
            st.write(income_statement)
    elif FinOpt2:
        if view == 'Quarterly':
            balance_sheet=stock.quarterly_balancesheet
            st.write(balance_sheet)
        else:
            balance_sheet=stock.balancesheet
            st.write(balance_sheet)
    elif FinOpt3:
        if view == 'Quarterly':
            cash_flow=stock.quarterly_cashflow
            st.write(cash_flow)
        else:
            cash_flow=stock.cashflow
            st.write(cash_flow)




    
#==============================================================================
# Tab 4
#==============================================================================

    
def tab4():
    st.title(ticker)
    st.write("Data source: Yahoo Finance")
    st.header('Monte Carlo Simulation')

    
    if ticker != '-':
        
        info = yf.Ticker(ticker).history()
        close_price = info['Close']
        daily_return = close_price.pct_change()
        daily_volatility = np.std(daily_return)
        np.random.seed(123)

        simulations = st.selectbox("Select number of simulations:", [200,500,1000])
        time_predicted = st.selectbox("Select time predicted:", [30,60,90])
        

        simulated_df = pd.DataFrame()
        
        for r in range(simulations):
            
            # A list to store the stock prices
            stock_price_list = []
            current_price = close_price[-1]
            
            for i in range(time_predicted):
                # Generate daily return
                daily_return = np.random.normal(0, daily_volatility)
        
                # Calculate the stock price of next day
                future_price = current_price * (1 + daily_return)
        
                # Save the results
                stock_price_list.append(future_price)
                # Change the current price
                current_price = future_price
            
            # Store the simulation results
            simulated_col = pd.Series(stock_price_list)
            simulated_col.name = "Sim" + str(r)
            simulated_df = pd.concat([simulated_df, simulated_col], axis=1)
    
        # Plot the simulation
        fig, ax = plt.subplots()
        fig.set_size_inches(15, 10, forward=True)
        plt.plot(simulated_df)
        plt.title('Monte Carlo simulation')
        plt.xlabel('Day')
        plt.ylabel('Price')
        plt.axhline(y=close_price[-1], color='black')
        plt.legend(['Current stock price is: ' + str(np.round(close_price[-1], 2))+ ' USD'])
        ax.get_legend().legendHandles[0].set_color('black')
        st.pyplot(plt)
        
        ending_price = simulated_df.iloc[-1:, :].values[0, ]
        # Value at Risk 95% confidence
        future_price_95ci = np.percentile(ending_price, 5)
        lol = close_price[-1] - future_price_95ci
        st.subheader('Value at risk with a 95% confidence interval is: ' + str(np.round(lol, 2)) + ' USD')
        
#==============================================================================
# Tab 5
#==============================================================================       
        
def tab5():
    st.title("Stock Comparison")
    
    # Input for stock symbols
    stock_symbols = st.text_input("Enter stock symbols separated by a comma (e.g., AAPL, MSFT):")
    col1, col2= st.columns(2)
    start_date = col1.date_input("Start date", datetime.today().date() - timedelta(days=365))
    end_date = col2.date_input("End date", datetime.today().date()- timedelta(days=1))

    if stock_symbols:
        symbols = [s.strip() for s in stock_symbols.split(",")]
    
        # Fetch stock data for the specified symbols
        stock_data = yf.download(symbols, start_date,end_date)  # Adjust the period as needed
    
        if not stock_data.empty:
    
            fig = go.Figure()
            for symbol in symbols:
                fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Adj Close', symbol], mode='lines', name=symbol))
    
            fig.update_layout(
                title="Stock Price",
                xaxis_title="Date",
                yaxis_title="Adjusted Close Price",
            )
    
            st.plotly_chart(fig, use_container_width=True)
            
            returns = stock_data['Adj Close'].pct_change().dropna()
            
            fig = go.Figure()
            for symbol in symbols:
                fig.add_trace(go.Scatter(x=returns.index, y=returns[symbol], mode='lines', name=symbol))
    
            fig.update_layout(
                title="Stock Returns",
                xaxis_title="Date",
                yaxis_title="Daily Returns",
            )
    
            st.plotly_chart(fig, use_container_width=True)

            
            st.subheader("Stock Data Summary")
            st.write(stock_data.describe())
    
 


           
        

#==============================================================================
# Main body
#==============================================================================
      
# Render the header
def run():
    st.sidebar.title("Financial Dashboard")
    st.sidebar.write("Data source: Yahoo Finance")
    # Add the ticker selection on the sidebar
    # Get the list of stock tickers from S&P500
    ticker_list = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol']
    
    # Add selection box
    global ticker
    ticker = st.sidebar.selectbox("Select a ticker", ticker_list)
        
    run_button = st.sidebar.button('Update Data')
    if run_button:
        st.experimental_rerun()
    
    # Add a radio box
    select_tab = st.sidebar.radio("Select tab", ['Summary','Chart','Financials','Monte carlo simulation','Stock Comparison'])
    
    # Show the selected tab
    if select_tab == 'Summary':
        # Run tab 1
        tab1()
    elif select_tab == 'Chart':
        # Run tab 2
        tab2()
    elif select_tab == 'Financials':
        # Run tab 3
        tab3()
    elif select_tab == 'Monte carlo simulation':
        # Run tab 4
        tab4()
    elif select_tab == 'Stock Comparison':
        # Run tab 5
        tab5()

        
if __name__ == "__main__":
    run()
    
###############################################################################
# END
###############################################################################