import random
from flask import Flask, render_template, request, redirect, url_for
from db_connection import create_connection, close_connection

app = Flask(__name__)


# Rota para a página inicial (home.html)
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        id_lista = request.form.get("search_text")
        return redirect(url_for("lista", id_lista=id_lista))
    return render_template("home.html")


# Função para gerar um ID de lista único (6 dígitos)
def gerar_id_unico():
    conn = create_connection()
    cursor = conn.cursor()

    def id_existe(id_lista):
        query = "SELECT COUNT(*) FROM Lista WHERE idlista = %s"
        cursor.execute(query, (id_lista,))
        result = cursor.fetchone()
        return result[0] > 0

    # Gerar um ID de 6 dígitos que não exista na tabela
    id_lista_aleatorio = random.randint(100000, 999999)
    while id_existe(id_lista_aleatorio):
        id_lista_aleatorio = random.randint(100000, 999999)

    cursor.close()
    close_connection(conn)

    return id_lista_aleatorio


# Rota para criar uma nova lista
@app.route("/criar_lista", methods=["POST"])
def criar_lista():
    conn = create_connection()
    cursor = conn.cursor()

    # Gera um ID único de 6 dígitos
    id_lista_aleatorio = gerar_id_unico()

    # Define um nome padrão para a nova lista (pode ser NULL se preferir)
    nome_lista_padrao = "Minha Lista"

    # Inserir a nova lista no banco de dados
    sql = "INSERT INTO Lista (idlista, nome_lista) VALUES (%s, %s)"
    cursor.execute(sql, (id_lista_aleatorio, nome_lista_padrao))
    conn.commit()

    cursor.close()
    close_connection(conn)

    # Redireciona para a página da nova lista
    return redirect(url_for("lista", id_lista=id_lista_aleatorio))


# Rota para exibir a lista
@app.route("/lista/<int:id_lista>", methods=["GET", "POST"])
def lista(id_lista):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)

    # Consulta o id_lista e nome_lista da tabela
    query = "SELECT idlista, nome_lista FROM Lista WHERE idlista = %s"
    cursor.execute(query, (id_lista,))
    resultado = cursor.fetchone()

    cursor.close()
    close_connection(conn)

    if resultado:
        # Renderiza a página da lista passando o resultado do banco de dados
        return render_template("lista.html", lista=resultado)
    else:
        return render_template("not_found.html")


@app.route("/atualizar_nome_lista/<int:id_lista>", methods=["POST"])
def atualizar_nome_lista(id_lista):
    novo_nome = request.form.get("novo_nome_lista")

    conn = create_connection()
    cursor = conn.cursor()

    # Atualizar o nome da lista no banco de dados
    sql = "UPDATE Lista SET nome_lista = %s WHERE idlista = %s"
    cursor.execute(sql, (novo_nome, id_lista))
    conn.commit()

    cursor.close()
    close_connection(conn)

    return "Nome atualizado com sucesso", 200


if __name__ == "__main__":
    app.run(debug=True)
