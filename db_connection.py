import mysql.connector
from mysql.connector import Error

# Configurações de conexão ao MySQL
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "Listfy",
    "port": 3306,
}


def create_connection():
    """
    Cria e retorna uma conexão ao banco de dados MySQL.
    """
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        if conn.is_connected():
            print("Conexão com o MySQL estabelecida com sucesso!")
        return conn
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None


def close_connection(conn):
    """
    Fecha a conexão com o banco de dados MySQL.
    """
    if conn and conn.is_connected():
        conn.close()
        print("Conexão com o MySQL encerrada.")
