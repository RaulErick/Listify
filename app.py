from flask import Flask, render_template, request, redirect, url_for
from db_connection import (
    create_connection,
    close_connection,
)  # Importando as funções de conexão

app = Flask(__name__)


# Rota para a página inicial (home.html)
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        id_lista = request.form.get("search_text")
        return redirect(url_for("lista", id_lista=id_lista))
    return render_template("home.html")


# Rota para buscar a lista pelo ID
@app.route("/lista/<int:id_lista>")
def lista(id_lista):
    conn = None
    cursor = None
    try:
        # Conectar ao banco de dados
        conn = create_connection()
        if conn is None:
            raise Exception("Não foi possível conectar ao banco de dados.")

        cursor = conn.cursor(dictionary=True)

        # Busca o id_lista na tabela
        query = "SELECT * FROM Lista WHERE idlista = %s"
        cursor.execute(query, (id_lista,))
        resultado = cursor.fetchone()

        if resultado:
            # Se o id_lista for encontrado, renderiza a página da lista
            return render_template("lista.html", lista=resultado)
        else:
            # Se o id_lista não for encontrado, exibe a página de erro
            return render_template("not_found.html")

    except Exception as e:
        print(f"Erro ao conectar ao banco de dados ou buscar a lista: {e}")
        return render_template("not_found.html")

    finally:
        # Fechar o cursor e a conexão, se foram abertos
        if cursor:
            cursor.close()
        if conn:
            close_connection(conn)  # Usar a função para fechar a conexão


if __name__ == "__main__":
    app.run(debug=True)
