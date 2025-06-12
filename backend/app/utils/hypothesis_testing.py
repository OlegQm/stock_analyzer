import pandas as pd
import numpy as np
from scipy import stats
from app.utils.data_collector import get_stock_data

def run_hypothesis_test(symbols, test_type, period="1y", alpha=0.05):
    """Выполнить статистический тест гипотезы"""
    # Получаем данные для всех запрошенных символов
    all_data = {}
    for symbol in symbols:
        data = get_stock_data(symbol, period)
        df = pd.DataFrame(data)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        # Рассчитываем дневную доходность
        df['Returns']  =  df['Close'].pct_change().fillna(0)
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
            # Проверка на нормальность распределения доходности
            if len(symbols) != 1:
                raise ValueError("Для теста на нормальность требуется один символ")

            symbol = symbols[0]
            returns = all_data[symbol]['Returns'].dropna().values

            # Тест Шапиро-Уилка
            statistic, p_value = stats.shapiro(returns)

            result["result"] = "normal" if p_value > alpha else "not_normal"
            result["p_value"] = p_value
            result["statistic"] = statistic
            result["conclusion"] = (
                f"Распределение доходности акции {symbol} {'является нормальным' if p_value > alpha else 'не является нормальным'} "
                f"с уровнем значимости {alpha}."
            )

        elif test_type == "correlation":
            # Проверка корреляции между двумя акциями
            if len(symbols) != 2:
                raise ValueError("Для теста на корреляцию требуется два символа")

            symbol1, symbol2 = symbols
            returns1 = all_data[symbol1]['Returns'].values
            returns2 = all_data[symbol2]['Returns'].values

            # Корреляция Пирсона
            correlation, p_value = stats.pearsonr(returns1, returns2)

            result["result"] = correlation
            result["p_value"] = p_value
            result["statistic"] = correlation
            result["conclusion"] = (
                f"Корреляция между доходностями акций {symbol1} и {symbol2} составляет {correlation:.4f}. "
                f"Эта корреляция {'статистически значима' if p_value < alpha else 'статистически не значима'} "
                f"с уровнем значимости {alpha}."
            )

        elif test_type == "mean_comparison":
            # Сравнение средней доходности двух акций
            if len(symbols) != 2:
                raise ValueError("Для сравнения средних требуется два символа")

            symbol1, symbol2 = symbols
            returns1 = all_data[symbol1]['Returns'].dropna().values
            returns2 = all_data[symbol2]['Returns'].dropna().values

            # t-тест для независимых выборок
            statistic, p_value = stats.ttest_ind(returns1, returns2, equal_var=False)

            mean1 = returns1.mean()
            mean2 = returns2.mean()

            result["result"] = "different" if p_value < alpha else "not_different"
            result["p_value"] = p_value
            result["statistic"] = statistic
            result["mean1"] = mean1
            result["mean2"] = mean2
            result["conclusion"] = (
                f"Средняя доходность акции {symbol1} ({mean1:.4f}) и акции {symbol2} ({mean2:.4f}) "
                f"{'статистически различна' if p_value < alpha else 'статистически не различна'} "
                f"с уровнем значимости {alpha}."
            )

        else:
            raise ValueError(f"Неизвестный тип теста: {test_type}")

    except Exception as e:
        result["error"] = str(e)

    return result
