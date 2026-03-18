import streamlit as st
import requests
import urllib.parse

st.set_page_config(
    layout="wide",
)

URL = "http://localhost:8000/"

tab1, tab2, tab3, tab4 = st.tabs(["Создание и удаление", "Поиск по оригинальной ссылке", "Просмотр статистики по ссылке", "Изменить код ссылки"])

with tab1:

    if 'short_code' not in st.session_state:
        st.session_state.short_code = None
    if 'original_url' not in st.session_state:
        st.session_state.original_url = None

    original_url = st.text_input("Ваша ссылка")
    alias_input = st.text_input("Введите свой желаемый alias") 

    if st.button("Нажми на кнопку, получишь результат"):
        alias_valid = True
        if original_url:
            if not(alias_input):
                response = requests.post(
                        "http://127.0.0.1:8000/links/shorten",
                        json={
                            "original_url": original_url,
                        }
                )
                st.session_state.short_code = response.json()
                print(st.session_state.short_code)
                st.text_input("Ваша ссылка:", f"{URL}{st.session_state.short_code}")

            else:
                for i in alias_input:
                    if  not((ord(i) <= 57 and ord(i) >= 48) or (ord(i) >= 97 and ord(i) <= 122)):                    
                        st.write("В алиасе недопустимый знак")
                        alias_valid = False
                        break
            
                if alias_valid:
                    response = requests.post(
                            "http://127.0.0.1:8000/links/shorten",
                            json={
                                "original_url": original_url,
                                "custom_alias": alias_input,
                            },
                    )
                    st.session_state.short_code = response.json()
                    if st.session_state.short_code == 0:
                        st.text_input("Такой ALIAS существует")
                    else:         
                        st.text_input("Ваша ссылка:", f"{URL}{st.session_state.short_code}")

        else:
            st.session_state.short_code = None
            st.write("Поле пустое")
            

    if st.session_state.short_code:
        if st.button("Удалить ссылку"):
            response = requests.delete(
                f"http://127.0.0.1:8000/links/{st.session_state.short_code}"
            )
            st.session_state.short_code = None
            st.rerun()

with tab2:
    original_url_search = st.text_input("Оригинальная ссылка")
    if st.button("Поиск по оригинальной ссылке"):
        if original_url_search:
            encoded_url = urllib.parse.quote(original_url_search, safe='')
            response = requests.get(
                    f"http://127.0.0.1:8000/links/search?original_url={encoded_url}"
            )
            if response.status_code == 200:
                st.write(response.json()['result'])

        else:
            st.write("Поле пустое")

with tab3:
    short_code_input = st.text_input("Код Вашей ссылки")
    if st.button("Отобразить данные"):
        if short_code_input:
            response = requests.get(
                    f"http://127.0.0.1:8000/links/{short_code_input}/stats"
            )
            if response.status_code == 200:
                st.write(response.json())
        else:
            st.write("Поле пустое")
    
with tab4:

    short_code_update = st.text_input("Ваш код ссылки")
    new_code_input = st.text_input("Ваш новый код ссылки")
    if st.button("Заменить код ссылки"):
        if short_code_update and new_code_input:
            response = requests.put(
                            f"http://127.0.0.1:8000/links/{short_code_update}",
                            json={
                                "new_code": new_code_input
                            },
                    )
            if response.status_code == 200:
                st.write(response.json()['result'])
        else:
            st.write("Поле(я) пустые(ое)")