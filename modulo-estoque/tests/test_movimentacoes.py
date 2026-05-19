def _criar_produto(client, *, sku: str, saldo_atual: int, estoque_minimo: int = 0):
    resp = client.post(
        "/estoque/produtos/",
        json={
            "nome": f"Produto {sku}",
            "sku": sku,
            "unidade": "un",
            "saldoAtual": saldo_atual,
            "estoqueMinimo": estoque_minimo,
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_entrada_soma_no_saldo_e_registra_historico(client):
    produto = _criar_produto(client, sku="P1", saldo_atual=10)

    resp = client.post(
        "/estoque/movimentacoes/entrada",
        json={"produtoId": produto["id"], "quantidade": 5},
    )
    assert resp.status_code == 201, resp.text
    mov = resp.json()
    assert mov["produtoId"] == produto["id"]
    assert mov["tipo"] == "entrada"
    assert mov["quantidade"] == 5

    resp = client.get("/estoque/produtos/")
    assert resp.status_code == 200, resp.text
    assert resp.json()[0]["saldoAtual"] == 15

    hist = client.get(f"/estoque/movimentacoes/{produto['id']}").json()
    assert len(hist) == 1
    assert hist[0]["tipo"] == "entrada"


def test_saida_diminui_e_nao_deixa_negativo(client):
    produto = _criar_produto(client, sku="P2", saldo_atual=3)

    resp = client.post(
        "/estoque/movimentacoes/saida",
        json={"produtoId": produto["id"], "quantidade": 2},
    )
    assert resp.status_code == 201, resp.text

    resp = client.post(
        "/estoque/movimentacoes/saida",
        json={"produtoId": produto["id"], "quantidade": 5},
    )
    assert resp.status_code == 422, resp.text

    resp = client.get("/estoque/produtos/")
    assert resp.status_code == 200, resp.text
    assert resp.json()[0]["saldoAtual"] == 1
