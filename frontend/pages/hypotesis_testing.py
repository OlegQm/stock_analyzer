import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import sys
import os

# Добавляем путь к родительской директории для импорта api_client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.app_client import (
    get_available_stocks,
    run_hypothesis_test,
    get_stock_data,  # Импортируем для получения данных для графика
)

st.set_page_config(
    page_title="Тестирование гипотез", page_icon="🧪", layout="wide"
)

st.title("🧪 Тестирование финансовых гипотез")

# Устанавливаем стиль для графиков Matplotlib
plt.style.use("ggplot")

# --- Боковая панель для выбора параметров ---
with st.sidebar:
    st.header("Параметры теста")

    # Получаем список доступных акций с бэкенда
    available_stocks = get_available_stocks()
    stock_options = {
        stock["symbol"]: f"{stock['symbol']} - {stock['name']}"
        for stock in available_stocks
    }

    # Выбор типа теста
    test_type = st.selectbox(
        "Тип теста",
        options=["normality", "correlation", "mean_comparison"],
        format_func=lambda x: {
            "normality": "Тест на нормальность",
            "correlation": "Тест на корреляцию",
            "mean_comparison": "Сравнение средней доходности",
        }.get(x, x),
    )

    # Выбор акций в зависимости от типа теста
    if test_type == "normality":
        # Для теста на нормальность нужна одна акция
        selected_symbol1 = st.selectbox(
            "Выберите акцию",
            options=list(stock_options.keys()),
            format_func=lambda x: stock_options[x],
        )
        selected_symbols = [selected_symbol1]
    else:
        # Для других тестов нужны две акции
        selected_symbol1 = st.selectbox(
            "Первая акция",
            options=list(stock_options.keys()),
            format_func=lambda x: stock_options[x],
        )
        # Исключаем первую акцию из списка для второй
        remaining_options = {
            k: v for k, v in stock_options.items() if k != selected_symbol1
        }
        selected_symbol2 = st.selectbox(
            "Вторая акция",
            options=list(remaining_options.keys()),
            format_func=lambda x: stock_options[x],
        )
        selected_symbols = [selected_symbol1, selected_symbol2]

    # Выбор периода
    period_options = {"1 год": "1y", "2 года": "2y", "5 лет": "5y"}
    selected_period_display = st.selectbox(
        "Выберите период", options=list(period_options.keys()), index=0
    )
    selected_period = period_options[selected_period_display]

    # Уровень значимости
    alpha = st.slider("Уровень значимости (alpha)", 0.01, 0.10, 0.05, 0.01)

    # Кнопка для выполнения теста
    test_button = st.button("Выполнить тест")

# --- Основная часть страницы ---
if test_button:
    with st.spinner("Выполнение статистического теста..."):
        # Выполняем тест гипотезы через API
        test_result = run_hypothesis_test(
            selected_symbols, test_type, selected_period, alpha
        )

    if test_result and "error" not in test_result:
        st.subheader("Результаты теста")

        # --- Отображение результатов для теста на нормальность ---
        if test_type == "normality":
            st.write(
                f"**Тест на нормальность распределения доходности для {selected_symbols[0]}**"
            )
            st.write(f"Статистика теста (Шапиро-Уилка): {test_result['statistic']:.4f}")
            st.write(f"P-значение: {test_result['p_value']:.4f}")
            st.write(f"Уровень значимости (alpha): {alpha}")

            # Вывод результата
            if test_result["p_value"] > alpha:
                st.success(
                    f"Распределение доходности акции {selected_symbols[0]} является нормальным."
                )
            else:
                st.warning(
                    f"Распределение доходности акции {selected_symbols[0]} не является нормальным."
                )
            st.write(test_result["conclusion"])

            # Добавляем визуализацию
            st.subheader("Визуализация распределения")
            with st.spinner("Загрузка данных для графика..."):
                data = get_stock_data(
                    selected_symbols[0], selected_period, "1d"
                )
                if data:
                    df = pd.DataFrame(data["data"])
                    df["Returns"] = df["Close"].pct_change().dropna()
                    returns = df["Returns"].fillna(0)

                    # Строим гистограмму и кривую нормального распределения
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.hist(
                        returns,
                        bins=50,
                        density=True,
                        alpha=0.6,
                        color="g",
                        label="Гистограмма доходности",
                    )

                    # Накладываем кривую нормального распределения
                    mu, std = stats.norm.fit(returns)
                    xmin, xmax = plt.xlim()
                    x = np.linspace(xmin, xmax, 100)
                    p = stats.norm.pdf(x, mu, std)
                    ax.plot(
                        x,
                        p,
                        "k",
                        linewidth=2,
                        label="Нормальное распределение",
                    )

                    ax.set_title(
                        f"Распределение доходности {selected_symbols[0]}"
                    )
                    ax.set_xlabel("Дневная доходность")
                    ax.set_ylabel("Плотность")
                    ax.legend()
                    st.pyplot(fig)

            # Добавляем пояснение
            st.info(
                """
            **Что это значит?**
            Тест на нормальность проверяет, соответствует ли распределение доходности акции нормальному распределению (колоколообразной кривой).
            - Если распределение нормальное, это означает, что доходность акции предсказуема и соответствует классическим финансовым моделям.
            - Если распределение не нормальное, это может указывать на наличие "толстых хвостов" (более частые экстремальные значения), что важно учитывать при оценке рисков.
            """
            )

        # --- Отображение результатов для теста на корреляцию ---
        elif test_type == "correlation":
            st.write(
                f"**Тест на корреляцию доходности акций {selected_symbols[0]} и {selected_symbols[1]}**"
            )
            st.write(
                f"Коэффициент корреляции (Пирсона): {test_result['statistic']:.4f}"
            )
            st.write(f"P-значение: {test_result['p_value']:.4f}")
            st.write(f"Уровень значимости (alpha): {alpha}")

            # Вывод результата
            if abs(test_result["statistic"]) > 0.7:
                if test_result["statistic"] > 0:
                    st.warning(
                        f"Акции {selected_symbols[0]} и {selected_symbols[1]} имеют сильную положительную корреляцию."
                    )
                else:
                    st.success(
                        f"Акции {selected_symbols[0]} и {selected_symbols[1]} имеют сильную отрицательную корреляцию."
                    )
            elif abs(test_result["statistic"]) > 0.3:
                st.info(
                    f"Акции {selected_symbols[0]} и {selected_symbols[1]} имеют умеренную корреляцию."
                )
            else:
                st.success(
                    f"Акции {selected_symbols[0]} и {selected_symbols[1]} имеют слабую корреляцию."
                )

            if test_result["p_value"] < alpha:
                st.write("Корреляция статистически значима.")
            else:
                st.write("Корреляция статистически не значима.")
            st.write(test_result["conclusion"])

            # Добавляем пояснение
            st.info(
                """
            **Что это значит?**
            Корреляция измеряет, насколько сильно связаны доходности двух акций:
            - **Положительная корреляция**: акции имеют тенденцию двигаться в одном направлении.
            - **Отрицательная корреляция**: акции имеют тенденцию двигаться в противоположных направлениях.
            - **Низкая корреляция**: движения акций слабо связаны.
            Для диверсификации портфеля обычно рекомендуется выбирать акции с низкой корреляцией.
            """
            )

        # --- Отображение результатов для сравнения средних ---
        elif test_type == "mean_comparison":
            st.write(
                f"**Сравнение средней доходности акций {selected_symbols[0]} и {selected_symbols[1]}**"
            )
            st.write(
                f"Средняя доходность {selected_symbols[0]}: {test_result.get('mean1', 0):.6f}"
            )
            st.write(
                f"Средняя доходность {selected_symbols[1]}: {test_result.get('mean2', 0):.6f}"
            )
            st.write(f"Статистика t-теста: {test_result['statistic']:.4f}")
            st.write(f"P-значение: {test_result['p_value']:.4f}")
            st.write(f"Уровень значимости (alpha): {alpha}")

            # Вывод результата
            if test_result["p_value"] < alpha:
                st.success("Средние доходности статистически различны.")
                if test_result.get("mean1", 0) > test_result.get("mean2", 0):
                    st.write(
                        f"Акция {selected_symbols[0]} показывает статистически более высокую доходность."
                    )
                else:
                    st.write(
                        f"Акция {selected_symbols[1]} показывает статистически более высокую доходность."
                    )
            else:
                st.info("Средние доходности статистически не различаются.")
            st.write(test_result["conclusion"])

            # Добавляем пояснение
            st.info(
                """
            **Что это значит?**
            Тест сравнивает среднюю доходность двух акций, чтобы определить, есть ли статистически значимая разница:
            - Если p-значение < alpha, то разница в средней доходности статистически значима.
            - Если p-значение >= alpha, то нет достаточных доказательств, чтобы утверждать, что средние доходности различаются.
            Этот тест может помочь при выборе между двумя акциями, но следует учитывать и другие факторы, такие как риск.
            """
            )

    else:
        if test_result and "error" in test_result:
            st.error(f"Ошибка при выполнении теста: {test_result['error']}")
        else:
            st.error("Не удалось выполнить тест. Проверьте соединение с API.")
else:
    st.info("Выберите параметры теста и нажмите 'Выполнить тест'.")
