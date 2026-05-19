def test_alertas_retorna_produtos_abaixo_do_minimo(client):
    client.post(
        "/estoque/produtos/",
        json={
            "nome": "Produto Alerta",
            "sku": "AL-1",
            "unidade": "un",
            "saldoAtual": 5,
            "estoqueMinimo": 10,
        },
    )

    resp = client.get("/estoque/alertas")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["total"] == 1
    assert data["produtos"][0]["sku"] == "AL-1"
    assert data["produtos"][0]["saldoAtual"] == 5
    assert data["produtos"][0]["estoqueMinimo"] == 10


def test_inventario_ajusta_saldo_com_justificativa(client):
    produto = client.post(
        "/estoque/produtos/",
        json={
            "nome": "Produto Inventário",
            "sku": "INV-1",
            "unidade": "un",
            "saldoAtual": 10,
            "estoqueMinimo": 0,
        },
    ).json()

    resp = client.post(
        f"/estoque/inventario/{produto['id']}",
        json={"saldoAjustado": 7, "justificativa": "contagem física"},
    )
    assert resp.status_code == 201, resp.text
    mov = resp.json()
    assert mov["tipo"] == "inventario"
    assert mov["saldoAjustado"] == 7
    assert mov["produtoId"] == produto["id"]

    resp = client.get("/estoque/produtos/")
    assert resp.status_code == 200, resp.text
    assert resp.json()[0]["saldoAtual"] == 7
