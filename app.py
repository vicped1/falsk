import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# URLs dos microsserviços
URL_CLIENTES = "https://sorveteriamicroservice.onrender.com/clientes/get"
URL_SABORES = "https://menu-yqkj.onrender.com/menu"

# Lista simulada de pedidosc
pedidos = []

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
    return jsonify({"pedidos": pedidos})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)