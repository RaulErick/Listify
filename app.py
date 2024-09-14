from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Configurações de conexão ao MySQL
db_config = {
    "host": "localhost",  # Substitua pelo seu host
    "user": "seu_usuario",  # Substitua pelo seu usuário do MySQL
    "password": "sua_senha",  # Substitua pela sua senha do MySQL
    "database": "nome_do_banco",  # Substitua pelo nome do seu banco de dados
}


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
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Busca o id_lista na tabela
        query = "SELECT * FROM lista WHERE id_lista = %s"
        cursor.execute(query, (id_lista,))
        resultado = cursor.fetchone()

        if resultado:
            # Se o id_lista for encontrado, renderiza a página da lista
            return render_template("lista.html", lista=resultado)
        else:
            # Se o id_lista não for encontrado, exibe a página de erro
            return render_template("id_inexistente.html")

    except Exception as e:
        print(f"Erro ao conectar ao banco de dados ou buscar a lista: {e}")
        return render_template("id_inexistente.html")

    finally:
        # Fechar o cursor e a conexão, se foram abertos
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    app.run(debug=True)
