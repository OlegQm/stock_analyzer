import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

# Добавляем путь к родительской директории
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.app_client import (
    get_available_stocks,
    get_stock_data,
    get_technical_analysis,
)

st.set_page_config(
    page_title="Технический анализ", page_icon="📉", layout="wide"
)

st.title("📉 Технический анализ")

# Настройка стиля matplotlib
plt.style.use("ggplot")


# Функция для отрисовки свечного графика на определенной оси (ax)
def plot_candlestick(ax, df):
    width = 0.6
    width2 = width * 0.8
    up = df[df.Close >= df.Open]
    down = df[df.Close < df.Open]

    ax.bar(
        up.index,
        up.Close - up.Open,
        width,
        bottom=up.Open,
        color="green",
        alpha=0.5,
    )
    ax.bar(
        up.index,
        up.High - up.Close,
        width2,
        bottom=up.Close,
        color="green",
        alpha=0.8,
    )
    ax.bar(
        up.index,
        up.Open - up.Low,
        width2,
        bottom=up.Low,
        color="green",
        alpha=0.8,
    )
    ax.bar(
        down.index,
        down.Open - down.Close,
        width,
        bottom=down.Close,
        color="red",
        alpha=0.5,
    )
    ax.bar(
        down.index,
        down.High - down.Open,
        width2,
        bottom=down.Open,
        color="red",
        alpha=0.8,
    )
    ax.bar(
        down.index,
        down.Close - down.Low,
        width2,
        bottom=down.Low,
        color="red",
        alpha=0.8,
    )
    ax.set_ylabel("Цена ($)")


# Боковая панель
with st.sidebar:
    st.header("Параметры")
    available_stocks = get_available_stocks()
    stock_options = {
        f"{stock['symbol']} - {stock['name']}": stock["symbol"]
        for stock in available_stocks
    }
    selected_stock_display = st.selectbox(
        "Выберите акцию", options=list(stock_options.keys())
    )
    selected_stock = stock_options[selected_stock_display]
    period_options = {
        "3 месяца": "3mo",
        "6 месяцев": "6mo",
        "1 год": "1y",
        "2 года": "2y",
    }
    selected_period_display = st.selectbox(
        "Выберите период", options=list(period_options.keys()), index=2
    )
    selected_period = period_options[selected_period_display]

    st.subheader("Индикаторы")
    use_sma = st.checkbox("SMA", value=True)
    use_ema = st.checkbox("EMA", value=True)
    use_rsi = st.checkbox("RSI", value=True)
    use_macd = st.checkbox("MACD", value=True)
    use_bollinger = st.checkbox("Bollinger Bands", value=False)

    selected_indicators = []
    if use_sma:
        selected_indicators.append("sma")
    if use_ema:
        selected_indicators.append("ema")
    if use_rsi:
        selected_indicators.append("rsi")
    if use_macd:
        selected_indicators.append("macd")
    if use_bollinger:
        selected_indicators.append("bollinger")

    analyze_button = st.button("Выполнить анализ")

# Основная часть
if analyze_button:
    with st.spinner("Выполнение технического анализа..."):
        stock_data = get_stock_data(selected_stock, selected_period, "1d")
        tech_analysis = get_technical_analysis(
            selected_stock, selected_period, "1d", selected_indicators
        )

    if stock_data and tech_analysis:
        df = pd.DataFrame(stock_data["data"])
        df["Date"] = pd.to_datetime(df["Date"])
        df.set_index("Date", inplace=True)
        indicators = tech_analysis["indicators"]

        # Определяем количество подграфиков
        num_subplots = 1 + use_rsi + use_macd
        height_ratios = [0.6] + [0.2] * (num_subplots - 1)

        fig, axes = plt.subplots(
            num_subplots,
            1,
            figsize=(12, 3 * num_subplots),
            sharex=True,
            gridspec_kw={"height_ratios": height_ratios},
        )
        # Если только один подграфик, axes не будет массивом
        if num_subplots == 1:
            axes = [axes]

        # --- График цены и индикаторов на нем ---
        ax1 = axes[0]
        plot_candlestick(ax1, df)
        ax1.set_title(f"Цена {selected_stock}")

        if use_sma:
            if "sma_20" in indicators:
                ax1.plot(df.index, indicators["sma_20"], label="SMA 20")
            if "sma_50" in indicators:
                ax1.plot(df.index, indicators["sma_50"], label="SMA 50")
        if use_ema:
            if "ema_20" in indicators:
                ax1.plot(
                    df.index,
                    indicators["ema_20"],
                    label="EMA 20",
                    linestyle="--",
                )
        if use_bollinger:
            ax1.plot(
                df.index,
                indicators["bollinger_high"],
                label="Bollinger High",
                color="gray",
                linestyle=":",
            )
            ax1.plot(
                df.index,
                indicators["bollinger_low"],
                label="Bollinger Low",
                color="gray",
                linestyle=":",
            )
            ax1.fill_between(
                df.index,
                indicators["bollinger_high"],
                indicators["bollinger_low"],
                color="gray",
                alpha=0.1,
            )

        # --- Графики RSI и MACD ---
        current_ax_index = 1
        if use_rsi:
            ax_rsi = axes[current_ax_index]
            ax_rsi.plot(df.index, indicators["rsi_14"], label="RSI 14")
            ax_rsi.axhline(70, color="red", linestyle="--", linewidth=1)
            ax_rsi.axhline(30, color="green", linestyle="--", linewidth=1)
            ax_rsi.set_ylabel("RSI")
            ax_rsi.set_ylim(0, 100)
            current_ax_index += 1

        if use_macd:
            ax_macd = axes[current_ax_index]
            ax_macd.plot(
                df.index, indicators["macd_line"], label="MACD Line"
            )
            ax_macd.plot(
                df.index, indicators["macd_signal"], label="Signal Line"
            )
            colors = [
                "green" if val >= 0 else "red"
                for val in indicators["macd_histogram"]
            ]
            ax_macd.bar(
                df.index,
                indicators["macd_histogram"],
                label="Histogram",
                color=colors,
                alpha=0.5,
            )
            ax_macd.set_ylabel("MACD")
            current_ax_index += 1

        # Общая настройка
        fig.suptitle(
            f"Технический анализ {selected_stock} - {selected_period_display}",
            fontsize=16,
        )
        fig.legend(loc="upper right")
        plt.xlabel("Дата")
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        st.pyplot(fig)
        st.subheader("Интерпретация индикаторов")
        
        with st.expander("Показать интерпретацию"):
            # Получаем последние значения индикаторов
            last_close = df['Close'].iloc[-1]
            
            if use_sma:
                st.write("### SMA (Simple Moving Average)")
                
                if 'sma_20' in indicators and 'sma_50' in indicators:
                    sma_20_last = indicators['sma_20'][-1]
                    sma_50_last = indicators['sma_50'][-1]
                    
                    st.write(f"SMA 20: {sma_20_last:.2f}")
                    st.write(f"SMA 50: {sma_50_last:.2f}")
                    
                    if last_close > sma_20_last and last_close > sma_50_last:
                        st.write("📈 Цена выше SMA 20 и SMA 50 - **бычий** сигнал.")
                    elif last_close < sma_20_last and last_close < sma_50_last:
                        st.write("📉 Цена ниже SMA 20 и SMA 50 - **медвежий** сигнал.")
                    elif sma_20_last > sma_50_last:
                        st.write("📈 SMA 20 выше SMA 50 - потенциальный **бычий** тренд.")
                    else:
                        st.write("📉 SMA 20 ниже SMA 50 - потенциальный **медвежий** тренд.")
            
            if use_rsi and 'rsi_14' in indicators:
                st.write("### RSI (Relative Strength Index)")
                
                rsi_last = indicators['rsi_14'][-1]
                st.write(f"RSI (14): {rsi_last:.2f}")
                
                if rsi_last > 70:
                    st.write("📉 RSI выше 70 - актив может быть **перекуплен**.")
                elif rsi_last < 30:
                    st.write("📈 RSI ниже 30 - актив может быть **перепродан**.")
                else:
                    st.write("➡️ RSI в нейтральной зоне.")
            
            if use_macd and 'macd_line' in indicators and 'macd_signal' in indicators:
                st.write("### MACD (Moving Average Convergence Divergence)")
                
                macd_last = indicators['macd_line'][-1]
                signal_last = indicators['macd_signal'][-1]
                histogram_last = indicators['macd_histogram'][-1] if 'macd_histogram' in indicators else macd_last - signal_last
                
                st.write(f"MACD Line: {macd_last:.2f}")
                st.write(f"Signal Line: {signal_last:.2f}")
                st.write(f"Histogram: {histogram_last:.2f}")
                
                if macd_last > signal_last:
                    st.write("📈 MACD выше сигнальной линии - **бычий** сигнал.")
                else:
                    st.write("📉 MACD ниже сигнальной линии - **медвежий** сигнал.")
                
                if histogram_last > 0 and indicators['macd_histogram'][-2] <= 0:
                    st.write("📈 Гистограмма только что стала положительной - потенциальный **сигнал к покупке**.")
                elif histogram_last < 0 and indicators['macd_histogram'][-2] >= 0:
                    st.write("📉 Гистограмма только что стала отрицательной - потенциальный **сигнал к продаже**.")
            
            if use_bollinger and 'bollinger_high' in indicators and 'bollinger_low' in indicators:
                st.write("### Bollinger Bands")
                
                upper_last = indicators['bollinger_high'][-1]
                lower_last = indicators['bollinger_low'][-1]
                
                st.write(f"Верхняя полоса: {upper_last:.2f}")
                st.write(f"Нижняя полоса: {lower_last:.2f}")
                
                if last_close > upper_last:
                    st.write("📉 Цена выше верхней полосы Боллинджера - актив может быть **перекуплен**.")
                elif last_close < lower_last:
                    st.write("📈 Цена ниже нижней полосы Боллинджера - актив может быть **перепродан**.")
                else:
                    st.write("➡️ Цена внутри полос Боллинджера - **нейтральный** сигнал.")
            
            st.warning("Обратите внимание, что эти интерпретации являются упрощенными и не должны использоваться как единственное основание для принятия инвестиционных решений.")
else:
    st.info("Выберите акцию и индикаторы, затем нажмите 'Выполнить анализ'.")
