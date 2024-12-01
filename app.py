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


@app.route('/pedido', methods=['POST'])
def criar_pedido():
    try:
        # Extrair dados da requisição
        data = request.get_json()
        cliente_id = data.get('cliente_id')
        sabor_id = data.get('sabor_id')

        if not cliente_id or not sabor_id:
            return jsonify({"error": "cliente_id e sabor_id são obrigatórios"}), 400

        # Obter dados dos microsserviços
        clientes = requests.get(URL_CLIENTES).json()
        sabores = requests.get(URL_SABORES).json()

        # Validar cliente
        cliente = next((c for c in clientes if clientes.index(c) + 1 == cliente_id), None)
        if not cliente:
            return jsonify({"error": "Cliente não encontrado"}), 404

        # Validar sabor
        sabor = next((s for s in sabores if s['id'] == sabor_id), None)
        if not sabor:
            return jsonify({"error": "Sabor não encontrado"}), 404

        # Criar pedido
        pedido = {
            "pedido_id": len(pedidos) + 1,
            "cliente_nome": cliente["nome"],
            "sabor_nome": sabor["nome"]
        }
        pedidos.append(pedido)

        return jsonify({"message": "Pedido criado com sucesso", "pedido": pedido}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

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



if __name__ == "_main_":
    app.run(debug=True)