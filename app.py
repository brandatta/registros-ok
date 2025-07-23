import streamlit as st
import pandas as pd
import mysql.connector

# ---------- CONFIGURACIÓN ----------
st.set_page_config(page_title="Revisión de inventario", layout="wide")
st.title("✅ Revisión de inventario")

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

# ---------- MOSTRAR TABLA CON ACCIÓN ----------
st.subheader("Primeros 10 registros")

# Agregamos una columna nueva para la acción (botón o tick)
acciones = []
for i in range(len(df)):
    key_flag = f"flag_{i}"
    key_btn = f"btn_{i}"

    if st.session_state.get(key_flag, False):
        acciones.append("✔️")
    else:
        if st.button("Sí", key=key_btn):
            st.session_state[key_flag] = True
            st.experimental_rerun()
        acciones.append("")

# Añadir la columna "Acción" a la tabla
df_con_accion = df.copy()
df_con_accion["Acción"] = acciones

# Mostrar la tabla completa
st.dataframe(df_con_accion, use_container_width=True)
