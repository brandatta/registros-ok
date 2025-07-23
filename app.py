import streamlit as st
import pandas as pd
import mysql.connector

# ---------- CONFIGURACIÓN DE LA PÁGINA ----------
st.set_page_config(page_title="Revisión de inventario", layout="wide")
st.title("✅ Selección de registros de inventario")

# ---------- CONEXIÓN A MySQL ----------
def get_connection():
    return mysql.connector.connect(
        host=st.secrets["app_marco_new"]["host"],
        user=st.secrets["app_marco_new"]["user"],
        password=st.secrets["app_marco_new"]["password"],
        database=st.secrets["app_marco_new"]["database"],
        port=3306,
    )

# ---------- CARGA DE DATOS ----------
@st.cache_data(show_spinner="Cargando registros…", ttl=60)
def load_data():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM inventario LIMIT 10", conn)
    conn.close()
    return df

df = load_data()
st.subheader("Primeros 10 registros de la tabla **inventario**")

# ---------- MOSTRAR CON BOTONES ----------
for idx, row in df.iterrows():
    col_data, col_action = st.columns([4, 1], gap="small")

    with col_data:
        st.table(pd.DataFrame(row).T.reset_index(drop=True))

    with col_action:
        key_flag = f"flag_{idx}"
        key_btn = f"btn_{idx}"

        if st.session_state.get(key_flag, False):
            st.markdown("<span style='font-size:2rem; color:green;'>✔️</span>", unsafe_allow_html=True)
        else:
            if st.button("Sí", key=key_btn):
                st.session_state[key_flag] = True
                st.experimental_rerun()

st.info("Pulsa **Sí** en los registros que corresponda. El tilde verde indica selección.")

