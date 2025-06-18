import streamlit as st
from ris_converter import RobustRISConverter
import datetime

st.title("📚 ЦМБ Каталог статии ➔ RIS конвертиране")

st.markdown("""
1. Каталог на ЦМБ: http://nt-cmb.mu-sofia.bg """)
st.markdown("""
2. В Комбинирано търсене въведете автор: напр. "Pancheva, R." """)
st.markdown("""
2. Каталог на ЦМБ: http://nt-cmb.mu-sofia.bg """)

user_text = st.text_area("Копирайте записите тук :", height=400, value='')

if 'ris_exp' not in st.session_state:
    st.session_state['ris_exp'] = ''

if st.button("🔄 Конвертиране в RIS"):
    converter = RobustRISConverter()
    ris = converter.process_text_to_ris(user_text)
    st.session_state['ris_exp'] = ris.strip()
    if ris.strip() and "No valid bibliographic" not in ris:
        st.success(f"Конвертирани са {ris.count('TY  - JOUR')} запис(а) ")
        st.text_area("RIS Output", value=st.session_state['ris_exp'], height=250)
    else:
        st.warning("Не са открити валидни записи.")

if st.session_state['ris_exp']:
    st.download_button(
        label="💾 Изтегли .RIS файла",
        data=st.session_state['ris_exp'],
        file_name=f"bibliography_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.ris"
    )
