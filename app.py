from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# URLs externas
MENU_URL = 'https://menu-yqkj.onrender.com/menu'
CLIENTES_GET_URL = 'https://sorveteriamicroservice.onrender.com/clientes/get'
CLIENTES_POST_URL = 'https://sorveteriamicroservice.onrender.com/clientes/post'

pedidos = []

def obter_menu():
    try:
        response = requests.get(MENU_URL)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.exceptions.RequestException:
        return None


@app.route("/")
def home():
    return "Hello world!"


@app.route('/criar_pedido', methods=['POST'])
def criar_pedido():
    sabores_disponiveis = obter_menu()

    if sabores_disponiveis is None:
        return jsonify({"erro": "Não foi possível acessar o menu de sabores."}), 500

    data = request.json
    usuario_id = data.get("usuario_id")
    sabor_id = data.get("sabor_id")

    if not usuario_id or not sabor_id:
        return jsonify({"erro": "ID do usuário e do sabor são obrigatórios."}), 400

    if sabor_id not in sabores_disponiveis:
        return jsonify({"erro": "Sabor inválido."}), 400

    pedido = {
        "usuario_id": usuario_id,
        "sabor_id": sabor_id,
        "sabor": sabores_disponiveis[sabor_id]
    }
    pedidos.append(pedido)
    return jsonify({"mensagem": "Pedido criado com sucesso!", "pedido": pedido}), 201


@app.route('/pedidos', methods=['GET'])
def listar_pedidos():
    return jsonify({"pedidos": pedidos}), 200


@app.route('/pedido/<int:pedido_id>', methods=['GET'])
def obter_pedido(pedido_id):
    if pedido_id < 1 or pedido_id > len(pedidos):
        return jsonify({"erro": "Pedido não encontrado."}), 404
    return jsonify({"pedido": pedidos[pedido_id - 1]}), 200


@app.route('/menu', methods=['GET'])
def acessar_menu():
    menu = obter_menu()
    if menu:
        return jsonify(menu), 200
    else:
        return jsonify({"erro": "Não foi possível acessar o menu."}), 500


@app.route('/clientes', methods=['GET'])
def acessar_clientes():
    try:
        response = requests.get(CLIENTES_GET_URL)
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({"erro": "Não foi possível acessar os dados dos clientes."}), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"erro": f"Erro ao acessar os dados dos clientes: {str(e)}"}), 500


@app.route('/clientes', methods=['POST'])
def criar_cliente():
    data = request.json
    cpf = data.get("cpf")
    nome = data.get("nome")

    if not cpf or not nome:
        return jsonify({"erro": "CPF e nome são obrigatórios."}), 400

    try:
        response = requests.post(
            CLIENTES_POST_URL,
            json=data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 201:
            try:
                return jsonify({
                    "mensagem": "Cliente criado com sucesso!",
                    "cliente": response.json()
                }), 201
            except ValueError:
                return jsonify({
                    "mensagem": "Cliente criado com sucesso, mas a resposta do servidor está vazia."
                }), 201
        else:
            return jsonify({
                "erro": "Não foi possível criar o cliente.",
                "status_code": response.status_code,
                "detalhes": response.text
            }), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"erro": f"Erro ao criar cliente: {str(e)}"}), 500



if __name__ == "__main__":
    app.run(debug=True)