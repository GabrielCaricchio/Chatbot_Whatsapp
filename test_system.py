import asyncio
import httpx

BASE_BOT_URL = "http://localhost:8000"
WAHA_URL = "http://localhost:3000"

async def test_bot():
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("1. Testando endpoint de saúde do bot...")
        res = await client.get(f"{BASE_BOT_URL}/health")
        assert res.status_code == 200, f"Health check falhou: {res.text}"
        print("   [OK] /health -> 200")

        print("2. Testando rota raiz com info do modelo...")
        res = await client.get(f"{BASE_BOT_URL}/")
        assert res.status_code == 200
        data = res.json()
        print(f"   [OK] Modelo configurado: {data.get('model')}")

        print("3. Testando acesso ao WAHA (sem bloqueio de chave)...")
        res = await client.get(f"{WAHA_URL}/api/sessions?all=true")
        assert res.status_code == 200, f"Falha no acesso ao WAHA: {res.text}"
        print("   [OK] WAHA acessível diretamente sem erros de autenticação")

        print("4. Testando abertura do Dashboard...")
        res_dash = await client.get(f"{WAHA_URL}/dashboard/")
        assert res_dash.status_code == 200, f"Falha no dashboard: {res_dash.status_code}"
        print("   [OK] Dashboard abre livremente (200 OK)")

        print("5. Simulando mensagem de webhook recebida pelo bot...")
        fake_msg_id = "TEST_MSG_88888"
        webhook_payload = {
            "event": "message",
            "session": "default",
            "payload": {
                "id": fake_msg_id,
                "timestamp": 1700000000,
                "from": "5511999999999@c.us",
                "fromMe": False,
                "body": "Olá! Quem é você e o que você faz?",
                "hasMedia": False
            }
        }
        res = await client.post(f"{BASE_BOT_URL}/webhook", json=webhook_payload)
        assert res.status_code == 200
        print(f"   [OK] Webhook processado pelo bot: {res.json()}")

        print("6. Testando deduplicação de mensagem...")
        res_dup = await client.post(f"{BASE_BOT_URL}/webhook", json=webhook_payload)
        assert res_dup.json().get("reason") == "Duplicate message"
        print("   [OK] Deduplicação funcionou perfeitamente")

        print("\nAguardando processamento assíncrono da resposta pela IA Groq...")
        await asyncio.sleep(4)
        print("Testes concluídos com 100% de sucesso! 🎉")

if __name__ == "__main__":
    asyncio.run(test_bot())
