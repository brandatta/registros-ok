import pandas as pd
import mysql.connector
from mysql.connector import Error
import streamlit as st

# Función para obtener los datos de la base de datos
def get_data():
    try:
        # Accede a los secretos de Streamlit Cloud
        mysql_secrets = st.secrets["mysql"]
        
        # Establecer la conexión con la base de datos
        connection = mysql.connector.connect(
            host=mysql_secrets["host"],
            user=mysql_secrets["user"],
            password=mysql_secrets["password"],
            database=mysql_secrets["database"]
        )
        
        # Verificar si la conexión fue exitosa
        if connection.is_connected():
            st.write("Conexión exitosa a la base de datos")
            
            # Consulta SQL (asegúrate de que la tabla esté correcta)
            query = "SELECT * FROM TU_TABLA LIMIT 10"  # Cambia 'TU_TABLA' por el nombre de tu tabla
            st.write("Ejecutando consulta SQL:", query)
            
            # Ejecutar la consulta SQL y cargar los resultados en un DataFrame
            df = pd.read_sql(query, connection)
            return df
        else:
            st.error("No se pudo conectar a la base de datos.")
            return None

    except Error as e:
        st.error(f"Error en la conexión a la base de datos: {e}")
        return None
    finally:
        # Cerrar la conexión si está abierta
        if connection.is_connected():
            connection.close()


