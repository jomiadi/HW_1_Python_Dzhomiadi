import streamlit as st
import pandas as pd
import requests
import numpy as np
import matplotlib.pyplot as plt

st.title("Анализ температурных данных")

uploaded_file = st.file_uploader("Выберите CSV-файл", type=['csv'])
if uploaded_file:
    data = pd.read_csv(uploaded_file)
    st.dataframe(data.head())

    if "city" in data.columns:
        cities_list = data['city'].unique()
        selected_option = st.selectbox("Выберите город:", cities_list)
        if selected_option:
            api_input = st.text_input("Введите API-ключ Open Weather:")
            if api_input:
                url = f"https://api.openweathermap.org/data/2.5/weather?q={selected_option}&appid={api_input}&units=metric"
                response = requests.get(url)
                if response.status_code == 200:
                    data['timestamp'] = pd.to_datetime(data['timestamp'])
                    st.title("Анализ температурных данных")

                    st.header("Описательная статистика")
                    city_data = data[data['city'] == selected_option]
                    st.subheader(f"Погода в {selected_option}")
                    st.write(city_data['temperature'].describe())

                    def detect_anomalies(df, threshold=2):
                        mean = df['temperature'].mean()
                        std = df['temperature'].std()
                        df['is_anomaly'] = (np.abs(df['temperature'] - mean) > threshold * std)
                        return df

                    city_data_with_anomalies = detect_anomalies(city_data)

                    st.header("Временной ряд температур с аномалиями")
                    fig, ax = plt.subplots(figsize=(14, 7))
                    ax.plot(city_data_with_anomalies['timestamp'], city_data_with_anomalies['temperature'], label=selected_option)
                    anomalies = city_data_with_anomalies[city_data_with_anomalies['is_anomaly']]
                    ax.scatter(anomalies['timestamp'], anomalies['temperature'], color='red',label=f"Аномалии ({selected_option})")

                    ax.set_title("Временной ряд температур с аномалиями")
                    ax.set_xlabel("Дата")
                    ax.set_ylabel("Температура")
                    ax.legend()
                    st.pyplot(fig)

                    st.header("Сезонные профили температуры")
                    season_stats = data.groupby(['city', 'season'])['temperature'].agg(['mean', 'std']).reset_index()

                    fig, ax = plt.subplots(figsize=(14, 7))
                    city_season_stats = season_stats[season_stats['city'] == selected_option]
                    ax.errorbar(
                            city_season_stats['season'],
                            city_season_stats['mean'],
                            yerr=city_season_stats['std'],
                            label=selected_option,
                            fmt='-o'
                    )

                    ax.set_title("Сезонные профили температуры")
                    ax.set_xlabel("Сезон")
                    ax.set_ylabel("Средняя температура")
                    ax.legend()
                    st.pyplot(fig)

                    st.header(f"Погода в {selected_option} сейчас: {response.json()['main']['temp']}°C")

                else:
                    print('{"cod": 401,"message": "Invalid API key. Please see https://openweathermap.org/faq#error401 for more info."}')

    else:
        print("Столбец 'city' отсутствует. Загрузите корректный CSV-файл.")

else:
    st.write("Пожалуйста, загрузите CSV-файл с историческими погодными данными.")