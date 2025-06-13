import pandas as pd
import numpy as np
from scipy import stats
from app.utils.data_collector import get_stock_data

def run_hypothesis_test(symbols, test_type, period="1y", alpha=0.05):
    """Run a statistical hypothesis test"""
    all_data = {}
    for symbol in symbols:
        data = get_stock_data(symbol, period)
        df = pd.DataFrame(data)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        df['Returns'] = df['Close'].pct_change().fillna(0)
        all_data[symbol] = df

    result = {
        "test_type": test_type,
        "symbols": symbols,
        "period": period,
        "alpha": alpha,
        "result": None,
        "p_value": None,
        "statistic": None,
        "conclusion": None
    }

    try:
        if test_type == "normality":
            if len(symbols) != 1:
                raise ValueError("A normality test requires one symbol")

            symbol = symbols[0]
            returns = all_data[symbol]['Returns'].dropna().values

            statistic, p_value = stats.shapiro(returns)

            result["result"] = "normal" if p_value > alpha else "not_normal"
            result["p_value"] = p_value
            result["statistic"] = statistic
            result["conclusion"] = (
                f"Return distribution of {symbol} {'is normal' if p_value > alpha else 'is not normal'} "
                f"at significance level {alpha}."
            )

        elif test_type == "correlation":
            if len(symbols) != 2:
                raise ValueError("A correlation test requires two symbols")

            symbol1, symbol2 = symbols
            returns1 = all_data[symbol1]['Returns'].values
            returns2 = all_data[symbol2]['Returns'].values

            correlation, p_value = stats.pearsonr(returns1, returns2)

            result["result"] = correlation
            result["p_value"] = p_value
            result["statistic"] = correlation
            result["conclusion"] = (
                f"Correlation between returns of {symbol1} and {symbol2} is {correlation:.4f}. "
                f"This correlation is {'statistically significant' if p_value < alpha else 'not statistically significant'} "
                f"at significance level {alpha}."
            )

        elif test_type == "mean_comparison":
            if len(symbols) != 2:
                raise ValueError("A mean comparison test requires two symbols")

            symbol1, symbol2 = symbols
            returns1 = all_data[symbol1]['Returns'].dropna().values
            returns2 = all_data[symbol2]['Returns'].dropna().values

            statistic, p_value = stats.ttest_ind(returns1, returns2, equal_var=False)

            mean1 = returns1.mean()
            mean2 = returns2.mean()

            result["result"] = "different" if p_value < alpha else "not_different"
            result["p_value"] = p_value
            result["statistic"] = statistic
            result["mean1"] = mean1
            result["mean2"] = mean2
            result["conclusion"] = (
                f"The mean return of {symbol1} ({mean1:.4f}) and {symbol2} ({mean2:.4f}) "
                f"{'differs significantly' if p_value < alpha else 'does not differ significantly'} "
                f"at significance level {alpha}."
            )

        else:
            raise ValueError(f"Unknown test type: {test_type}")

    except Exception as e:
        result["error"] = str(e)

    return result
