import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

# Добавляем путь к родительской директории
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.app_client import get_available_stocks, get_visualization_data

st.set_page_config(
    page_title="Визуализация", page_icon="📊", layout="wide"
)

st.title("📊 Визуализация данных")
plt.style.use("ggplot")

# Боковая панель
with st.sidebar:
    st.header("Параметры визуализации")
    available_stocks = get_available_stocks()
    stock_options = {
        stock["symbol"]: f"{stock['symbol']} - {stock['name']}"
        for stock in available_stocks
    }
    chart_type = st.selectbox(
        "Тип графика",
        options=["price", "returns", "correlation"],
        format_func=lambda x: {
            "price": "График цен",
            "returns": "График доходности",
            "correlation": "Корреляционная матрица",
        }.get(x, x),
    )
    selected_symbols = st.multiselect(
        "Выберите акции",
        options=list(stock_options.keys()),
        format_func=lambda x: stock_options[x],
        default=[available_stocks[0]["symbol"]],
    )
    period_options = {"1 год": "1y", "2 года": "2y", "5 лет": "5y"}
    selected_period_display = st.selectbox(
        "Выберите период", options=list(period_options.keys()), index=0
    )
    selected_period = period_options[selected_period_display]
    visualize_button = st.button("Создать визуализацию")

# Основная часть
if visualize_button and selected_symbols:
    with st.spinner("Создание визуализации..."):
        visualization_data = get_visualization_data(
            selected_symbols, chart_type, selected_period, "1d"
        )

    if visualization_data and "error" not in visualization_data:
        if chart_type == "price":
            st.subheader("График цен и объемов")
            fig, (ax1, ax2) = plt.subplots(
                2,
                1,
                figsize=(12, 8),
                sharex=True,
                gridspec_kw={"height_ratios": [3, 1]},
            )
            fig.suptitle(f"Цены акций - {selected_period_display}", fontsize=16)

            for stock_data in visualization_data["data"]:
                symbol = stock_data["symbol"]
                df = pd.DataFrame(
                    {
                        "Date": pd.to_datetime(stock_data["dates"]),
                        "Price": stock_data["prices"],
                        "Volume": stock_data["volumes"],
                    }
                )
                ax1.plot(df["Date"], df["Price"], label=symbol)
                ax2.bar(df["Date"], df["Volume"], label=symbol, alpha=0.5)

            ax1.set_ylabel("Цена ($)")
            ax1.legend()
            ax1.grid(True)
            ax2.set_ylabel("Объем")
            ax2.legend()
            ax2.grid(True)
            plt.xlabel("Дата")
            plt.tight_layout(rect=[0, 0, 1, 0.96])
            st.pyplot(fig)

        elif chart_type == "returns":
            st.subheader("График доходности акций")
            fig, (ax1, ax2) = plt.subplots(
                2, 1, figsize=(12, 8), sharex=True
            )
            fig.suptitle(
                f"Доходность акций - {selected_period_display}", fontsize=16
            )

            for stock_data in visualization_data["data"]:
                symbol = stock_data["symbol"]
                df = pd.DataFrame(
                    {
                        "Date": pd.to_datetime(stock_data["dates"]),
                        "Daily": stock_data["daily_returns"],
                        "Cumulative": stock_data["cumulative_returns"],
                    }
                )
                ax1.plot(df["Date"], df["Daily"], label=symbol, alpha=0.7)
                ax2.plot(df["Date"], df["Cumulative"], label=symbol)

            ax1.set_title("Дневная доходность")
            ax1.set_ylabel("Доходность")
            ax1.legend()
            ax1.grid(True)
            ax2.set_title("Кумулятивная доходность")
            ax2.set_ylabel("Доходность")
            ax2.legend()
            ax2.grid(True)
            plt.xlabel("Дата")
            plt.tight_layout(rect=[0, 0, 1, 0.96])
            st.pyplot(fig)

        elif chart_type == "correlation":
            st.subheader("Корреляционная матрица доходности акций")
            if len(selected_symbols) < 2:
                st.warning("Выберите не менее двух акций.")
            else:
                corr_matrix = pd.DataFrame(
                    index=selected_symbols, columns=selected_symbols
                )
                for item in visualization_data["data"]:
                    corr_matrix.loc[item["x"], item["y"]] = item["value"]
                corr_matrix = corr_matrix.astype(float)

                fig, ax = plt.subplots(figsize=(8, 6))
                im = ax.imshow(corr_matrix, cmap="coolwarm", vmin=-1, vmax=1)

                fig.colorbar(im, ax=ax)
                ax.set_xticks(np.arange(len(selected_symbols)))
                ax.set_yticks(np.arange(len(selected_symbols)))
                ax.set_xticklabels(selected_symbols)
                ax.set_yticklabels(selected_symbols)
                plt.setp(
                    ax.get_xticklabels(),
                    rotation=45,
                    ha="right",
                    rotation_mode="anchor",
                )

                for i in range(len(selected_symbols)):
                    for j in range(len(selected_symbols)):
                        ax.text(
                            j,
                            i,
                            f"{corr_matrix.iloc[i, j]:.2f}",
                            ha="center",
                            va="center",
                            color="w",
                        )

                ax.set_title("Корреляционная матрица доходности")
                plt.tight_layout()
                st.pyplot(fig)
    else:
        st.error("Не удалось получить данные для визуализации.")
else:
    st.info("Выберите акции и тип графика, затем нажмите 'Создать визуализацию'.")
