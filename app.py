import streamlit as st
from ris_converter import RobustRISConverter
import datetime

st.title("📚 Bibliography ➔ RIS Converter")

st.markdown("""
Paste bibliographic entries (1 per line).  
Click Convert to see the RIS result and download the file.
""")

user_text = st.text_area("Paste your bibliography text here :", height=200, value='')

if 'ris_exp' not in st.session_state:
    st.session_state['ris_exp'] = ''

if st.button("🔄 Convert to RIS"):
    converter = RobustRISConverter()
    ris = converter.process_text_to_ris(user_text)
    st.session_state['ris_exp'] = ris.strip()
    if ris.strip() and "No valid bibliographic" not in ris:
        st.success(f"Converted {ris.count('TY  - JOUR')} bibliographic record(s).")
        st.text_area("RIS Output", value=st.session_state['ris_exp'], height=250)
    else:
        st.warning("No valid bibliographic entries found.")

if st.session_state['ris_exp']:
    st.download_button(
        label="💾 Download .RIS file",
        data=st.session_state['ris_exp'],
        file_name=f"bibliography_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.ris"
    )