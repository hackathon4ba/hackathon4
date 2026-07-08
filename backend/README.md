# Backend Template

Backend Flask simples para servir como base no hackathon.

## Requisitos

- Python 3.11+
- `pip`

## Instalação

Crie e ative um ambiente virtual:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Instale as dependencias:

```powershell
pip install -r requirements.txt
```

## Variáveis de ambiente

Crie um arquivo `.env` com base em `.env.example`

## Banco de dados

O projeto usa SQLite por padrão e grava o banco em `app.db`.

Aplicar as migrations existentes:

```powershell
python -m flask --app main db upgrade
```

Criar uma nova migration apos alterar os models:

```powershell
flask --app main db migrate -m "describe your change"
flask --app main db upgrade
```

## Popular banco com usuário admin

O script abaixo cria ou atualiza um usuário administrador inicial.

Valores padrão:

- `ADMIN_EMAIL=admin@hackathon.local`
- `ADMIN_PASSWORD=admin123`
- `RESTAURANT_ADMIN_NAME=Empresa Admin Demo`
- `RESTAURANT_ADMIN_EMAIL=admin@empresa-demo.com`
- `RESTAURANT_ADMIN_PASSWORD=admin123`

Voce pode sobrescrever esses valores definindo as variáveis de ambiente `ADMIN_EMAIL` e `ADMIN_PASSWORD`. Para executar:

```powershell
python populate_database.py
```

O script tambem cria a empresa seed usada na demo do dashboard:

- email: `admin@empresa-demo.com`
- senha: `admin123`

Para popular os pedidos dessa empresa com `deliveries_train.csv`:

```powershell
python seed_admin_orders.py
```

## Autenticação de restaurantes

Cadastrar restaurante:

```http
POST /auth/restaurants/register
```

```json
{
  "name": "Restaurante Sabor da Casa",
  "email": "contato@restaurante.com",
  "password": "senha123",
  "phone": "+5511999999999",
  "address": "Rua Exemplo, 123",
  "cuisine_type": "brasileira"
}
```

Login de restaurante:

```http
POST /auth/restaurants/login
```

```json
{
  "email": "contato@restaurante.com",
  "password": "senha123"
}
```

Buscar restaurante logado:

```http
GET /restaurants/me
Authorization: Bearer <access_token>
```

Cadastrar item no cardápio do restaurante autenticado:

```http
POST /restaurants/menu/items
Authorization: Bearer <access_token>
```

```json
{
  "name": "Parmegiana",
  "price": 54.9,
  "ingredients": ["Arroz", "Filé de frango", "Molho de tomate", "Queijo"]
}
```

Listar cardápio do restaurante autenticado:

```http
GET /restaurants/menu/items
Authorization: Bearer <access_token>
```

Atualizar item do cardápio:

```http
PATCH /restaurants/menu/items/{item_id}
Authorization: Bearer <access_token>
```

Remover item do cardápio:

```http
DELETE /restaurants/menu/items/{item_id}
Authorization: Bearer <access_token>
```

## Pedidos do restaurante

Listar pedidos:

```http
GET /restaurants/orders
Authorization: Bearer <access_token>
```

Criar pedido:

```http
POST /restaurants/orders
Authorization: Bearer <access_token>
```

```json
{
  "customer_name": "Ana Paula",
  "main_dish": "Parmegiana",
  "price": 54.9,
  "status": "pending",
  "notes": "Sem cebola"
}
```

Buscar pedido:

```http
GET /restaurants/orders/{order_id}
Authorization: Bearer <access_token>
```

Atualizar pedido:

```http
PATCH /restaurants/orders/{order_id}
Authorization: Bearer <access_token>
```

Excluir pedido:

```http
DELETE /restaurants/orders/{order_id}
Authorization: Bearer <access_token>
```

## Executando a aplicação

Modo desenvolvimento:

```powershell
python main.py
```

A aplicação sobe em `http://localhost:5000` e a documentação da API fica em `http://localhost:5000/docs`.
