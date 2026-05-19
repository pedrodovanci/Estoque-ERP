def test_criar_e_listar_produtos(client):
    payload = {
        "nome": "Camiseta ERP Universitario",
        "sku": "CAM-001",
        "unidade": "un",
        "saldoAtual": 50,
        "estoqueMinimo": 10,
    }

    resp = client.post("/estoque/produtos/", json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()

    assert data["sku"] == "CAM-001"
    assert data["saldoAtual"] == 50
    assert data["estoqueMinimo"] == 10
    assert "saldo_atual" not in data
    assert "estoque_minimo" not in data

    resp = client.get("/estoque/produtos/")
    assert resp.status_code == 200, resp.text
    produtos = resp.json()
    assert len(produtos) == 1
    assert produtos[0]["sku"] == "CAM-001"


def test_nao_permite_sku_duplicado(client):
    payload = {
        "nome": "Camiseta",
        "sku": "CAM-001",
        "saldoAtual": 1,
        "estoqueMinimo": 0,
    }
    resp1 = client.post("/estoque/produtos/", json=payload)
    assert resp1.status_code == 201, resp1.text

    resp2 = client.post("/estoque/produtos/", json=payload)
    assert resp2.status_code == 400, resp2.text
