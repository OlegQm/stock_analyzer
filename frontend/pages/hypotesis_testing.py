import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.app_client import (
    get_available_stocks,
    run_hypothesis_test,
    get_stock_data,  
)

st.set_page_config(
    page_title="Hypothesis Testing", page_icon="🧪", layout="wide"
)

st.title("🧪 Financial Hypothesis Testing")

plt.style.use("ggplot")

with st.sidebar:
    st.header("Test parameters")

    
    available_stocks = get_available_stocks()
    stock_options = {
        stock["symbol"]: f"{stock['symbol']} - {stock['name']}"
        for stock in available_stocks
    }

    
    test_type = st.selectbox(
        "Test type",
        options=["normality", "correlation", "mean_comparison"],
        format_func=lambda x: {
            "normality": "Normality test",
            "correlation": "Correlation test",
            "mean_comparison": "Mean comparison",
        }.get(x, x),
    )

    
    if test_type == "normality":
        selected_symbol1 = st.selectbox(
            "Select a stock",
            options=list(stock_options.keys()),
            format_func=lambda x: stock_options[x],
        )
        selected_symbols = [selected_symbol1]
    else:
        selected_symbol1 = st.selectbox(
            "First stock",
            options=list(stock_options.keys()),
            format_func=lambda x: stock_options[x],
        )
        remaining_options = {k: v for k, v in stock_options.items() if k != selected_symbol1}
        selected_symbol2 = st.selectbox(
            "Second stock",
            options=list(remaining_options.keys()),
            format_func=lambda x: stock_options[x],
        )
        selected_symbols = [selected_symbol1, selected_symbol2]

    
    period_options = {"1 year": "1y", "2 years": "2y", "5 years": "5y"}
    selected_period_display = st.selectbox(
        "Select period", options=list(period_options.keys()), index=0
    )
    selected_period = period_options[selected_period_display]

    
    alpha = st.slider("Significance level (alpha)", 0.01, 0.10, 0.05, 0.01)

    
    test_button = st.button("Run test")

if test_button:
    with st.spinner("Running statistical test..."):
        
        test_result = run_hypothesis_test(
            selected_symbols, test_type, selected_period, alpha
        )

    if test_result and "error" not in test_result:
        st.subheader("Test results")

        
        if test_type == "normality":
            st.write(
                f"**Normality test for returns of {selected_symbols[0]}**"
            )
            st.write(f"Shapiro-Wilk statistic: {test_result['statistic']:.4f}")
            st.write(f"P-value: {test_result['p_value']:.4f}")
            st.write(f"Significance level (alpha): {alpha}")

            
            if test_result["p_value"] > alpha:
                st.success(
                    f"Return distribution of {selected_symbols[0]} is normal."
                )
            else:
                st.warning(
                    f"Return distribution of {selected_symbols[0]} is not normal."
                )
            st.write(test_result["conclusion"])

            
            st.subheader("Distribution visualization")
            with st.spinner("Loading data for chart..."):
                data = get_stock_data(
                    selected_symbols[0], selected_period, "1d"
                )
                if data:
                    df = pd.DataFrame(data["data"])
                    df["Returns"] = df["Close"].pct_change().dropna()
                    returns = df["Returns"].fillna(0)

                    
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.hist(
                        returns,
                        bins=50,
                        density=True,
                        alpha=0.6,
                        color="g",
                        label="Return histogram",
                    )

                    
                    mu, std = stats.norm.fit(returns)
                    xmin, xmax = plt.xlim()
                    x = np.linspace(xmin, xmax, 100)
                    p = stats.norm.pdf(x, mu, std)
                    ax.plot(
                        x,
                        p,
                        "k",
                        linewidth=2,
                        label="Normal distribution",
                    )

                    ax.set_title(
                        f"Return distribution {selected_symbols[0]}"
                    )
                    ax.set_xlabel("Daily return")
                    ax.set_ylabel("Density")
                    ax.legend()
                    st.pyplot(fig)

            
            st.info(
                """
            **What does this mean?**
            The normality test checks whether the return distribution follows a bell curve.
            - If it is normal, returns are predictable and align with classic financial models.
            - If not, heavy tails may be present, which is important for risk assessment.
            """
            )

        
        elif test_type == "correlation":
            st.write(
                f"**Correlation test for returns of {selected_symbols[0]} and {selected_symbols[1]}**"
            )
            st.write(
                f"Pearson correlation coefficient: {test_result['statistic']:.4f}"
            )
            st.write(f"P-value: {test_result['p_value']:.4f}")
            st.write(f"Significance level (alpha): {alpha}")

            
            if abs(test_result["statistic"]) > 0.7:
                if test_result["statistic"] > 0:
                    st.warning(
                        f"{selected_symbols[0]} and {selected_symbols[1]} have strong positive correlation."
                    )
                else:
                    st.success(
                        f"{selected_symbols[0]} and {selected_symbols[1]} have strong negative correlation."
                    )
            elif abs(test_result["statistic"]) > 0.3:
                st.info(
                    f"{selected_symbols[0]} and {selected_symbols[1]} have moderate correlation."
                )
            else:
                st.success(
                    f"{selected_symbols[0]} and {selected_symbols[1]} have weak correlation."
                )

            if test_result["p_value"] < alpha:
                st.write("Correlation is statistically significant.")
            else:
                st.write("Correlation is not statistically significant.")
            st.write(test_result["conclusion"])

            
            st.info(
                """
            **What does this mean?**
            Correlation measures how closely the returns of two stocks move together:
            - **Positive correlation**: stocks tend to move in the same direction.
            - **Negative correlation**: stocks tend to move in opposite directions.
            - **Low correlation**: movements are weakly related.
            For diversification it is usually better to choose stocks with low correlation.
            """
            )

        
        elif test_type == "mean_comparison":
            st.write(
                f"**Mean return comparison for {selected_symbols[0]} and {selected_symbols[1]}**"
            )
            st.write(
                f"Mean return {selected_symbols[0]}: {test_result.get('mean1', 0):.6f}"
            )
            st.write(
                f"Mean return {selected_symbols[1]}: {test_result.get('mean2', 0):.6f}"
            )
            st.write(f"t-test statistic: {test_result['statistic']:.4f}")
            st.write(f"P-value: {test_result['p_value']:.4f}")
            st.write(f"Significance level (alpha): {alpha}")

            
            if test_result["p_value"] < alpha:
                st.success("Mean returns are significantly different.")
                if test_result.get("mean1", 0) > test_result.get("mean2", 0):
                    st.write(
                        f"{selected_symbols[0]} shows a statistically higher return."
                    )
                else:
                    st.write(
                        f"{selected_symbols[1]} shows a statistically higher return."
                    )
            else:
                st.info("Mean returns are not significantly different.")
            st.write(test_result["conclusion"])

            
            st.info(
                """
            **What does this mean?**
            This test compares the mean returns of two stocks to see if the difference is statistically significant:
            - If the p-value < alpha, the difference is significant.
            - If the p-value >= alpha, there is insufficient evidence to claim the means differ.
            Use this test along with other factors such as risk when choosing between stocks.
            """
            )

    else:
        if test_result and "error" in test_result:
            st.error(f"Error running test: {test_result['error']}")
        else:
            st.error("Could not run the test. Check API connection.")
else:
    st.info("Select parameters and click 'Run test'.")
