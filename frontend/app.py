import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Financial Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("📈 Yahoo Finance Data Analyzer")

    st.markdown(
        """
        This application allows you to analyze stock market data from Yahoo Finance.

        ### Features:
        - Retrieve historical stock data
        - Perform technical analysis using various indicators
        - Analyze data with natural language
        - Visualize data and trends
        - Test financial hypotheses

        Select a section from the menu on the left.
        """
    )

    st.info(
        """
        **Getting started:**
        1. Go to the "Stock Data" page to view historical data
        2. Use "Technical Analysis" to calculate indicators
        3. Visualize data on the "Visualization" page
        4. Check hypotheses on the "Hypothesis Testing" page
        """
    )

if __name__ == "__main__":
    main()
