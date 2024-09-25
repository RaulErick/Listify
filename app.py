import random
from flask import Flask, render_template, request, redirect, url_for, jsonify 
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
    nome_lista_padrao = "Minha Lista"

    # Inserir a nova lista no banco de dados
    sql = "INSERT INTO Lista (idlista, nome_lista) VALUES (%s, %s)"
    cursor.execute(sql, (id_lista_aleatorio, nome_lista_padrao))
    conn.commit()

    cursor.close()
    close_connection(conn)

    return redirect(url_for("lista", id_lista=id_lista_aleatorio))

# Rota para exibir a lista
@app.route("/lista/<int:id_lista>", methods=["GET"])
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

# CRUD para itens

@app.route('/lista/<int:lista_id>/item', methods=['POST'])
def adicionar_item(lista_id):
    nome_item = request.form.get('nome_item')
    anotacoes_item = request.form.get('anotacoes_item', '')

    conn = create_connection()
    cursor = conn.cursor()

    # Inserir o item na tabela Itens
    cursor.execute("INSERT INTO Itens (Nome_Item, Anotacoes_item) VALUES (%s, %s)", (nome_item, anotacoes_item))
    item_id = cursor.lastrowid

    # Inserir na tabela de associação
    cursor.execute("INSERT INTO Lista_has_Itens (Lista_idLista, Itens_idItens) VALUES (%s, %s)", (lista_id, item_id))
    conn.commit()

    cursor.close()
    close_connection(conn)

    return jsonify({'status': 'success', 'item_id': item_id}), 201

@app.route('/lista/<int:lista_id>/item', methods=['GET'])
def obter_itens(lista_id):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)

    # Obter todos os itens associados à lista
    query = """
        SELECT i.idItens, i.Nome_Item, i.Anotacoes_item
        FROM Lista_has_Itens lhi
        JOIN Itens i ON lhi.Itens_idItens = i.idItens
        WHERE lhi.Lista_idLista = %s
    """
    cursor.execute(query, (lista_id,))
    itens = cursor.fetchall()

    cursor.close()
    close_connection(conn)

    return jsonify(itens), 200

@app.route('/lista/<int:id_lista>', methods=['DELETE'])
def excluir_lista(id_lista):
    conn = create_connection()
    cursor = conn.cursor()

    # Excluir a lista da tabela Lista
    cursor.execute("DELETE FROM Lista WHERE idlista = %s", (id_lista,))
    
    # Excluir todos os itens associados à lista
    cursor.execute("DELETE FROM Lista_has_Itens WHERE Lista_idLista = %s", (id_lista,))
    
    conn.commit()
    cursor.close()
    close_connection(conn)

    return jsonify({'status': 'success', 'message': f'Lista com ID {id_lista} excluída com sucesso!'}), 200



@app.route('/item/<int:item_id>', methods=['PUT'])
def atualizar_item(item_id):
    nome_item = request.form.get('nome_item')
    anotacoes_item = request.form.get('anotacoes_item', '')

    conn = create_connection()
    cursor = conn.cursor()

    # Atualizar o item na tabela Itens
    cursor.execute("UPDATE Itens SET Nome_Item = %s, Anotacoes_item = %s WHERE idItens = %s", (nome_item, anotacoes_item, item_id))
    conn.commit()

    cursor.close()
    close_connection(conn)

    return jsonify({'status': 'success'}), 200

@app.route('/lista/<int:lista_id>/item/<int:item_id>', methods=['DELETE'])
def excluir_item(lista_id, item_id):
    conn = create_connection()
    cursor = conn.cursor()

    # Dissociar o item da lista
    cursor.execute("DELETE FROM Lista_has_Itens WHERE Lista_idLista = %s AND Itens_idItens = %s", (lista_id, item_id))

    # Verificar se o item está associado a outras listas
    cursor.execute("SELECT COUNT(*) FROM Lista_has_Itens WHERE Itens_idItens = %s", (item_id,))
    count = cursor.fetchone()[0]

    # Se o item não estiver associado a outras listas, excluí-lo
    if count == 0:
        cursor.execute("DELETE FROM Itens WHERE idItens = %s", (item_id,))

    conn.commit()
    cursor.close()
    close_connection(conn)

    return jsonify({'status': 'success'}), 200

if __name__ == "__main__":
    app.run(debug=True)
