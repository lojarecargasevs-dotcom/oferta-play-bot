# Oferta Play v2

Loja Flask com:
- catálogo de produtos
- carrinho
- checkout
- registro de pedidos
- envio do pedido para WhatsApp
- painel administrativo
- cadastro/ativação/exclusão de produtos
- atualização do status dos pedidos
- métricas básicas

## Render
Build Command:
`pip install -r requirements.txt`

Start Command:
`gunicorn app:app`

Variáveis recomendadas:
- `SECRET_KEY`
- `ADMIN_USER`
- `ADMIN_PASSWORD`
- `WHATSAPP_NUMBER`

Observação: SQLite no plano Free do Render não é adequado como armazenamento permanente. Para produção, configure PostgreSQL usando `DATABASE_URL` ou outro banco persistente antes de depender do histórico de vendas.
