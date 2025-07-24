import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime, timedelta

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

# ---------- ACTUALIZAR PROCESADO ----------
def actualizar_procesado(id_valor, estado):
    conn = get_connection()
    cursor = conn.cursor()
    query = "UPDATE inventario SET procesado = %s, proc_ts = NOW() WHERE id = %s"
    cursor.execute(query, (estado, id_valor))
    conn.commit()
    cursor.close()
    conn.close()

# ---------- CARGA DE DATOS ----------
@st.cache_data(ttl=60)
def load_data():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM inventario LIMIT 10", conn)
    conn.close()
    return df

df = load_data()
total_registros = len(df)

# ---------- SEPARAR REGISTROS ----------
df_pendientes = df[df["procesado"] == 0]
df_procesados = df[df["procesado"] == 1]

# ---------- ESTILO ----------
st.markdown("""
<style>
.registro-scroll {
    display: flex;
    overflow-x: auto;
    padding: 8px 0;
    border-bottom: 1px solid #ddd;
    font-family: monospace;
    font-size: 14px;
}
.registro-scroll div {
    flex: 0 0 auto;
    padding-right: 16px;
    white-space: nowrap;
}
.fade-out {
    opacity: 0.2;
}
</style>
""", unsafe_allow_html=True)

# ---------- TABS ----------
tab1, tab2 = st.tabs([
    f"🔄 Pendientes ({len(df_pendientes)})",
    f"✅ Procesados ({len(df_procesados)})"
])

# ---------- TAB 1 ----------
with tab1:
    st.subheader("Registros no marcados como 'Sí'")
    for _, row in df_pendientes.iterrows():
        key_flag = f"flag_{row['id']}"
        if key_flag not in st.session_state:
            st.session_state[key_flag] = False

        fade_class = "fade-out" if st.session_state[key_flag] else ""

        with st.container():
            cols = st.columns([10, 1, 1, 0.5])
            with cols[0]:
                st.markdown(
                    f"<div class='registro-scroll {fade_class}'>" +
                    "".join([f"<div><b>{col}:</b> {row[col]}</div>" for col in df.columns]) +
                    "</div>", unsafe_allow_html=True
                )
            with cols[1]:
                if st.button("Sí", key=f"btn_si_{row['id']}"):
                    actualizar_procesado(row["id"], 1)
                    st.session_state[key_flag] = True
                    if "hora_inicio" not in st.session_state:
                        st.session_state["hora_inicio"] = datetime.now()
                    st.rerun()
            with cols[2]:
                if st.button("No", key=f"btn_no_{row['id']}"):
                    actualizar_procesado(row["id"], 0)
                    st.session_state[key_flag] = False
                    st.rerun()
            with cols[3]:
                if st.session_state[key_flag]:
                    st.markdown("<span style='font-size:1.5rem; color:green;'>✓</span>", unsafe_allow_html=True)

# ---------- TAB 2 ----------
with tab2:
    st.subheader("Registros ya marcados como 'Sí'")
    for _, row in df_procesados.iterrows():
        with st.container():
            cols = st.columns([10, 1, 1, 0.5])
            with cols[0]:
                st.markdown(
                    "<div class='registro-scroll'>" +
                    "".join([f"<div><b>{col}:</b> {row[col]}</div>" for col in df.columns]) +
                    "</div>", unsafe_allow_html=True
                )
            with cols[1]:
                st.button("Sí", key=f"btn_si_{row['id']}")
            with cols[2]:
                if st.button("No", key=f"btn_no_{row['id']}"):
                    actualizar_procesado(row["id"], 0)
                    st.rerun()
            with cols[3]:
                st.markdown("<span style='font-size:1.5rem; color:green;'>✓</span>", unsafe_allow_html=True)

# ---------- MÉTRICAS ----------
st.markdown("---")
subtotal_local = len(df_procesados)
total_local = len(df_procesados) + len(df_pendientes)
porcentaje_local = round((subtotal_local / total_local) * 100, 1) if total_local > 0 else 0.0

st.markdown("### 📊 Estado de los registros visibles")
col1, col2 = st.columns([1, 3])
with col1:
    st.metric(label="✅ Porcentaje marcado como 'Sí'", value=f"{porcentaje_local} %")
with col2:
    st.progress(int(porcentaje_local))

st.success(f"🔢 Subtotal de registros visibles marcados como 'Sí': **{subtotal_local}** de {total_local}")

# ---------- ESTIMACIÓN TEMPORAL ----------
st.markdown("---")
st.markdown("### ⏱️ Estimación temporal")

if "hora_inicio" in st.session_state:
    hora_inicio = st.session_state["hora_inicio"]
    ahora = datetime.now()
    tiempo_transcurrido = ahora - hora_inicio
    minutos = tiempo_transcurrido.total_seconds() / 60

    if subtotal_local > 0:
        estimado_total_min = (minutos / subtotal_local) * total_registros
        hora_fin_estimada = hora_inicio + timedelta(minutes=estimado_total_min)

        st.info(f"🕒 Hora de inicio: **{hora_inicio.strftime('%H:%M:%S')}**")
        st.info(f"⏳ Tiempo transcurrido: **{str(tiempo_transcurrido).split('.')[0]}**")
        st.info(f"📅 Estimación de finalización: **{hora_fin_estimada.strftime('%H:%M:%S')}**")
    else:
        st.warning("Aún no se marcó ningún registro como 'Sí'.")
else:
    st.info("La hora de inicio se registrará al marcar el primer registro como 'Sí'.")

# ---------- ESTADO GENERAL ----------
st.markdown("---")
subtotal_global = len(df[df["procesado"] == 1])
porcentaje = round((subtotal_global / total_registros) * 100, 1) if total_registros > 0 else 0.0

st.markdown("### 📊 Estado general del inventario")
col1, col2 = st.columns([1, 3])
with col1:
    st.metric(label="✅ Porcentaje marcado como 'Sí'", value=f"{porcentaje} %")
with col2:
    st.progress(int(porcentaje))

st.success(f"🔢 Subtotal de registros marcados como 'Sí': **{subtotal_global}** de {total_registros}")

# ---------- REFRESCO MANUAL ----------
st.markdown("#### 🔄")
if st.button("Actualizar estimaciones"):
    st.rerun()
