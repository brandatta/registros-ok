import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime, timedelta
import pytz

# ---------- CONFIGURACIÓN ----------
st.set_page_config(page_title="Revisión de inventario", layout="wide")
st.title("✅ Revisión de inventario")
TZ = pytz.timezone("America/Argentina/Buenos_Aires")

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

# ---------- VARIABLES DE ESTADO ----------
if "hora_inicio" not in st.session_state:
    st.session_state["hora_inicio"] = None
if "mensaje_exito" not in st.session_state:
    st.session_state["mensaje_exito"] = None
if "ultimo_tick" not in st.session_state:
    st.session_state["ultimo_tick"] = None
if "procesados_ids" not in st.session_state:
    st.session_state["procesados_ids"] = set()
if "pendientes_ids" not in st.session_state:
    st.session_state["pendientes_ids"] = set()

# ---------- FUNCIÓN DE CARGA ----------
def load_data():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM inventario ORDER BY id", conn)
    conn.close()
    return df

# ---------- FUNCIÓN PRINCIPAL ----------
def main():
    df = load_data()

    # Separar registros
    df_pendientes = df[df["procesado"] == 0]
    df_procesados = df[df["procesado"] == 1]

    # IDs visibles para control interno
    st.session_state["pendientes_ids"] = set(df_pendientes["id"])
    st.session_state["procesados_ids"] = set(df_procesados["id"])

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
    </style>
    """, unsafe_allow_html=True)

    # ---------- MENSAJE TEMPORAL ----------
    if st.session_state["mensaje_exito"]:
        st.success(st.session_state["mensaje_exito"])
        st.session_state["mensaje_exito"] = None

    # ---------- PESTAÑAS ----------
    tab1, tab2 = st.tabs([
        f"🔄 Pendientes ({len(df_pendientes)})",
        f"✅ Procesados ({len(df_procesados)})"
    ])

    with tab1:
        st.subheader("Registros no marcados como 'Sí'")
        for _, row in df_pendientes.iterrows():
            if row["id"] not in st.session_state["procesados_ids"]:  # Ocultar si ya se procesó
                with st.container():
                    cols = st.columns([10, 1, 0.5])
                    with cols[0]:
                        st.markdown(
                            "<div class='registro-scroll'>" +
                            "".join([f"<div><b>{col}:</b> {row[col]}</div>" for col in df.columns]) +
                            "</div>", unsafe_allow_html=True
                        )
                    with cols[1]:
                        if st.button("Sí", key=f"btn_si_{row['id']}"):
                            actualizar_procesado(row["id"], 1)
                            if not st.session_state["hora_inicio"]:
                                st.session_state["hora_inicio"] = datetime.now(TZ)
                            st.session_state["ultimo_tick"] = row["id"]
                            st.session_state["procesados_ids"].add(row["id"])
                            st.session_state["pendientes_ids"].discard(row["id"])
                            st.session_state["mensaje_exito"] = f"✅ Registro {row['id']} marcado como 'Sí'."
                            st.experimental_rerun()
                    with cols[2]:
                        if st.session_state.get("ultimo_tick") == row["id"]:
                            st.markdown("<span style='font-size:1.5rem; color:green;'>✓</span>", unsafe_allow_html=True)

    with tab2:
        st.subheader("Registros ya marcados como 'Sí'")
        for _, row in df_procesados.iterrows():
            if row["id"] not in st.session_state["pendientes_ids"]:  # Ocultar si se revirtió
                with st.container():
                    cols = st.columns([10, 1])
                    with cols[0]:
                        st.markdown(
                            "<div class='registro-scroll'>" +
                            "".join([f"<div><b>{col}:</b> {row[col]}</div>" for col in df.columns]) +
                            "</div>", unsafe_allow_html=True
                        )
                    with cols[1]:
                        if st.button("No", key=f"btn_no_{row['id']}"):
                            actualizar_procesado(row["id"], 0)
                            st.session_state["procesados_ids"].discard(row["id"])
                            st.session_state["pendientes_ids"].add(row["id"])
                            st.session_state["mensaje_exito"] = f"↩️ Registro {row['id']} revertido a pendiente."
                            st.experimental_rerun()

    # ---------- MÉTRICAS ----------
    st.markdown("---")
    subtotal_local = len(st.session_state["procesados_ids"])
    total_local = subtotal_local + len(st.session_state["pendientes_ids"])
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
    if st.button("🔁 Actualizar estimación temporal"):
        pass  # No hace nada porque se recalcula igual en cada ejecución

    st.markdown("### ⏱️ Estimación temporal")
    if st.session_state["hora_inicio"]:
        ahora = datetime.now(TZ)
        tiempo_transcurrido = ahora - st.session_state["hora_inicio"]
        minutos = tiempo_transcurrido.total_seconds() / 60
        if subtotal_local > 0:
            estimado_total_min = (minutos / subtotal_local) * total_local
            hora_fin_estimada = st.session_state["hora_inicio"] + timedelta(minutes=estimado_total_min)
            st.info(f"🕒 Hora de inicio: **{st.session_state['hora_inicio'].strftime('%H:%M:%S')}**")
            st.info(f"⏳ Tiempo transcurrido: **{str(tiempo_transcurrido).split('.')[0]}**")
            st.info(f"📅 Estimación de finalización: **{hora_fin_estimada.strftime('%H:%M:%S')}**")
        else:
            st.warning("Aún no se marcó ningún registro como 'Sí'.")
    else:
        st.info("La hora de inicio se registrará al marcar el primer registro como 'Sí'.")

# ---------- EJECUTAR ----------
main()
