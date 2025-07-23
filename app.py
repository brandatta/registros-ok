import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error

# Obtener credenciales de los secretos de Streamlit Cloud
def get_data():
    try:
        # Accede a los secretos almacenados en Streamlit Cloud
        mysql_secrets = st.secrets["mysql"]
        
        # Conectar a la base de datos usando los secretos
        connection = mysql.connector.connect(
            host=mysql_secrets["host"],
            user=mysql_secrets["user"],
            password=mysql_secrets["password"],
            database=mysql_secrets["database"]
        )
        
        # Verificar la conexión
        if connection.is_connected():
            st.write("Conexión exitosa a la base de datos")
            query = "SELECT * FROM TU_TABLA LIMIT 10"  # Cambia 'TU_TABLA' por el nombre de tu tabla
            df = pd.read_sql(query, connection)
            return df
    except Error as e:
        st.error(f"Error en la conexión a la base de datos: {e}")
        return None
    finally:
        # Asegurarse de cerrar la conexión
        if connection.is_connected():
            connection.close()

# Función para mostrar los registros con un diseño limpio
def display_table(df):
    if df is not None and not df.empty:
        for index, row in df.iterrows():
            st.write(f"### Registro {index + 1}")
            # Asegúrate de cambiar 'columna1', 'columna2', etc. por los nombres reales de tus columnas
            st.markdown(f"**Columna1**: {row['columna1']} - **Columna2**: {row['columna2']} - **Columna3**: {row['columna3']}")
            
            confirm_button = st.button(f"✔ Confirmar {index + 1}", key=f"btn_{index}")
            if confirm_button:
                st.success(f"✔ Confirmado: Registro {index + 1}")
    else:
        st.write("No se encontraron registros o hubo un error al obtener los datos.")

# Interfaz de Streamlit
st.title("Aplicación de Confirmación de Registros")

# Llamamos a la función para obtener los datos de la base de datos
df = get_data()
display_table(df)
