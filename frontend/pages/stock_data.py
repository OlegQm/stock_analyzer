import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
from datetime import datetime
import sys
import os
from io import BytesIO

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.app_client import get_available_stocks, get_stock_data

st.set_page_config(page_title="Stock Data", page_icon="📊", layout="wide")
st.title("📊 Stock Data")
plt.style.use('ggplot')

def format_number(x, pos):
    return f'{int(x):,}'

def plot_candlestick(df, title):
    fig, ax = plt.subplots(figsize=(12, 6))
    width = 0.6
    width2 = width * 0.8

    up = df[df.Close >= df.Open]
    down = df[df.Close < df.Open]

    ax.bar(up.index, up.Close - up.Open, width, bottom=up.Open, color='green', alpha=0.5)
    ax.bar(up.index, up.High - up.Close, width2, bottom=up.Close, color='green', alpha=0.8)
    ax.bar(up.index, up.Open - up.Low, width2, bottom=up.Low, color='green', alpha=0.8)

    ax.bar(down.index, down.Open - down.Close, width, bottom=down.Close, color='red', alpha=0.5)
    ax.bar(down.index, down.High - down.Open, width2, bottom=down.Open, color='red', alpha=0.8)
    ax.bar(down.index, down.Close - down.Low, width2, bottom=down.Low, color='red', alpha=0.8)

    ax.set_title(title, fontsize=14)
    ax.set_xlabel('Дата')
    ax.set_ylabel('Цена ($)')

    if len(df) > 30:
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    else:
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(df) // 10)))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))

    plt.xticks(rotation=45)
    plt.tight_layout()

    return fig

with st.sidebar:
    st.header("Parameters")
    available_stocks = get_available_stocks()
    stock_options = {f"{stock['symbol']} - {stock['name']}": stock['symbol'] for stock in available_stocks}
    selected_stock_display = st.selectbox(
        "Select a stock",
        options=list(stock_options.keys())
    )
    selected_stock = stock_options[selected_stock_display]
    period_options = {
        "1 day": "1d",
        "5 days": "5d",
        "1 month": "1mo",
        "3 months": "3mo",
        "6 months": "6mo",
        "1 year": "1y",
        "2 years": "2y",
        "5 years": "5y",
        "10 years": "10y",
        "Year to date": "ytd",
        "Max": "max"
    }
    selected_period_display = st.selectbox(
        "Select period",
        options=list(period_options.keys()),
        index=5
    )
    selected_period = period_options[selected_period_display]

    interval_options = {
        "1 day": "1d",
        "1 week": "1wk",
        "1 month": "1mo"
    }
    if selected_period in ["1d", "5d", "1mo"]:
        interval_options.update({
            "1 minute": "1m",
            "5 minutes": "5m",
            "15 minutes": "15m",
            "30 minutes": "30m",
            "1 hour": "1h"
        })

    selected_interval_display = st.selectbox(
        "Select interval",
        options=list(interval_options.keys()),
        index=0
    )
    selected_interval = interval_options[selected_interval_display]

    fetch_data = st.button("Get data")

if fetch_data or 'stock_data' in st.session_state:
    with st.spinner("Loading data..."):
        if fetch_data or 'stock_data' not in st.session_state:
            stock_data = get_stock_data(selected_stock, selected_period, selected_interval)
            if stock_data:
                st.session_state['stock_data'] = stock_data
        else:
            stock_data = st.session_state['stock_data']

    if stock_data:
        st.subheader(f"Information about {stock_data['symbol']}")
        info = stock_data['info']

        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Name:** {info.get('longName', '')}")
            st.write(f"**Sector:** {info.get('sector', '')}")
            st.write(f"**Industry:** {info.get('industry', '')}")
            st.write(f"**Website:** {info.get('website', '')}")
        with col2:
            st.write(f"**Market cap:** ${info.get('marketCap', 0):,}")
            st.write(f"**P/E (trailing):** {info.get('trailingPE', 'N/A')}")
            st.write(f"**P/E (forward):** {info.get('forwardPE', 'N/A')}")
            st.write(f"**Dividend yield:** {info.get('dividendYield', 'N/A')}%")

        st.write(f"**Current price:** ${info.get('regularMarketPrice', 0):.2f} ({info.get('regularMarketChangePercent', 0):.2f}%)")
        df = pd.DataFrame(stock_data['data'])
        df['Date'] = pd.to_datetime(df['Date'])
        df_plot = df.copy()
        df_plot.set_index('Date', inplace=True)
        st.subheader(f"Price chart {stock_data['symbol']}")
        fig_candle = plot_candlestick(df_plot, f"{stock_data['symbol']} - {selected_period_display}")
        st.pyplot(fig_candle)
        st.subheader(f"Trading volume {stock_data['symbol']}")
        fig_volume, ax_volume = plt.subplots(figsize=(12, 4))
        ax_volume.bar(df_plot.index, df_plot['Volume'], color='green', alpha=0.7)
        ax_volume.set_title(f"Trading volume {stock_data['symbol']} - {selected_period_display}")
        ax_volume.set_xlabel('Date')
        ax_volume.set_ylabel('Volume')

        volume_formatter = FuncFormatter(format_number)
        ax_volume.yaxis.set_major_formatter(volume_formatter)

        if len(df_plot) > 30:
            ax_volume.xaxis.set_major_locator(mdates.MonthLocator())
            ax_volume.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        else:
            ax_volume.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(df_plot) // 10)))
            ax_volume.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))

        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig_volume)

        st.subheader("Historical data")
        display_df = df.copy()
        display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')

        st.dataframe(display_df.sort_values('Date', ascending=False), use_container_width=True)

        csv = display_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"{stock_data['symbol']}_{selected_period}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

        st.subheader("Download charts")
        col1, col2 = st.columns(2)
        with col1:
            buf = BytesIO()
            fig_candle.savefig(buf, format="png", dpi=200)
            buf.seek(0)
            st.download_button(
                label="Download price chart",
                data=buf,
                file_name=f"{stock_data['symbol']}_price_{datetime.now().strftime('%Y%m%d')}.png",
                mime="image/png"
            )
        with col2:
            buf_volume = BytesIO()
            fig_volume.savefig(buf_volume, format="png", dpi=200)
            buf_volume.seek(0)
            st.download_button(
                label="Download volume chart",
                data=buf_volume,
                file_name=f"{stock_data['symbol']}_volume_{datetime.now().strftime('%Y%m%d')}.png",
                mime="image/png"
            )
else:
    st.info("Select a stock and click 'Get data' to start analysis.")
