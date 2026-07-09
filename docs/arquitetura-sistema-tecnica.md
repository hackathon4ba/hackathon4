# Arquitetura Tecnica do Sistema

## 1. Objetivo

Este documento descreve a estrutura tecnica do sistema, com foco em:

- classes e modelos de dominio
- endpoints expostos pela API
- fluxo de persistencia no banco
- integracao entre frontend, backend e IA

O sistema foi projetado para operar um restaurante com:

- autenticacao por restaurante
- gerenciamento de cardapio
- controle de estoque por receita
- pedidos
- dashboard operacional com faturamento historico e previsao

## 2. Estrutura do Repositorio

### 2.1 Backend

Diretorio: `backend/`

Responsavel por:

- API Flask
- modelos SQLAlchemy
- controllers por dominio
- services de negocio
- migrations
- scripts de seed

### 2.2 Frontend

Diretorio: `front/`

Responsavel por:

- interface Nuxt 3/Vue
- autenticacao da sessao do restaurante
- dashboard
- pedido
- cardapio
- estoque

### 2.3 IA e datasets

Diretorios:

- `ia/`
- `backend/datasets/`

Responsaveis por:

- dataset de treino
- notebook de referencia
- seed de demo
- previsao de faturamento

## 3. Backend

### 3.1 Inicializacao

Arquivos principais:

- [backend/main.py](/abs/path/C:/Users/usuario/Downloads/hackathon4/backend/main.py)
- [backend/factory.py](/abs/path/C:/Users/usuario/Downloads/hackathon4/backend/factory.py)

O `create_app()` registra:

- extensoes Flask
- JWT
- migracoes
- blueprint de cada controller
- documentacao da API via Spectree

### 3.2 Configuracao do banco

O banco principal e SQLite, com arquivo em `backend/app.db`.

A evolucao de schema e feita com Flask-Migrate/Alembic, usando:

- [backend/migrations/env.py](/abs/path/C:/Users/usuario/Downloads/hackathon4/backend/migrations/env.py)
- [backend/migrations/versions/*.py](/abs/path/C:/Users/usuario/Downloads/hackathon4/backend/migrations/versions)

## 4. Modelos de Dados

### 4.1 `Restaurant`

Arquivo: [backend/models/restaurant.py](/abs/path/C:/Users/usuario/Downloads/hackathon4/backend/models/restaurant.py)

Campos principais:

- `id`
- `name`
- `email`
- `password_hash`
- `phone`
- `address`
- `cuisine_type`
- `is_active`
- `created_at`

Relacionamentos:

- `menu_items`
- `inventory_items`
- `daily_revenues`
- `orders`

### 4.2 `MenuItem`

Arquivo: [backend/models/menu_item.py](/abs/path/C:/Users/usuario/Downloads/hackathon4/backend/models/menu_item.py)

Campos principais:

- `id`
- `restaurant_id`
- `name`
- `price_cents`
- `ingredients`
- `created_at`
- `updated_at`

Relacionamentos:

- `restaurant`
- `recipe_entries`

### 4.3 `InventoryItem`

Arquivo: [backend/models/inventory.py](/abs/path/C:/Users/usuario/Downloads/hackathon4/backend/models/inventory.py)

Campos principais:

- `id`
- `restaurant_id`
- `name`
- `unit`
- `quantity_available`
- `minimum_quantity`
- `created_at`
- `updated_at`

### 4.4 `MenuItemRecipe`

Arquivo: [backend/models/inventory.py](/abs/path/C:/Users/usuario/Downloads/hackathon4/backend/models/inventory.py)

Relaciona pratos e itens de estoque.

Campos:

- `id`
- `menu_item_id`
- `inventory_item_id`
- `quantity_required`
- `created_at`
- `updated_at`

### 4.5 `Order`

Arquivo: [backend/models/order.py](/abs/path/C:/Users/usuario/Downloads/hackathon4/backend/models/order.py)

Campos principais:

- `id`
- `restaurant_id`
- `customer_name`
- `menu_item_id`
- `main_dish`
- `order_price_cents`
- `status`
- `stock_deducted`
- `notes`
- `created_at`
- `updated_at`

### 4.6 `RevenueDaily`

Arquivo: [backend/models/revenue_daily.py](/abs/path/C:/Users/usuario/Downloads/hackathon4/backend/models/revenue_daily.py)

Tabela materializada do faturamento diario.

Campos:

- `id`
- `restaurant_id`
- `revenue_date`
- `revenue_cents`
- `orders_count`
- `created_at`
- `updated_at`

Essa tabela e a fonte principal do historico completo do dashboard.

## 5. Controllers

### 5.1 `order_controller.py`

Arquivo: [backend/controllers/order_controller.py](/abs/path/C:/Users/usuario/Downloads/hackathon4/backend/controllers/order_controller.py)

Responsabilidade:

- listar pedidos
- criar pedido
- consultar pedido
- atualizar pedido
- deletar pedido

Regras aplicadas:

- o pedido precisa pertencer ao restaurante logado
- o prato precisa existir no cardapio do restaurante
- a receita de estoque precisa existir
- o consumo de estoque e automatico quando o status exige estoque
- o faturamento diario e sincronizado depois de cada alteracao

### 5.2 `menu_controller.py`

Arquivo: [backend/controllers/menu_controller.py](/abs/path/C:/Users/usuario/Downloads/hackathon4/backend/controllers/menu_controller.py)

Responsabilidade:

- listar pratos
- criar prato
- editar prato
- remover prato
- consultar receita do prato
- substituir receita do prato

Pontos importantes:

- a receita do prato referencia itens reais de estoque
- a validacao impede receita com itens duplicados
- a receita deve pertencer ao mesmo restaurante

### 5.3 `inventory_controller.py`

Arquivo: [backend/controllers/inventory_controller.py](/abs/path/C:/Users/usuario/Downloads/hackathon4/backend/controllers/inventory_controller.py)

Responsabilidade:

- listar itens de estoque
- criar item
- editar item
- remover item

### 5.4 `dashboard_controller.py`

Arquivo: [backend/controllers/dashboard_controller.py](/abs/path/C:/Users/usuario/Downloads/hackathon4/backend/controllers/dashboard_controller.py)

Responsabilidade:

- retornar os dados do dashboard
- retornar insights de IA
- retornar historico completo de faturamento com paginação

Rotas principais:

- `GET /api/v1/restaurants/{restaurant_id}/dashboard`
- `GET /api/v1/restaurants/{restaurant_id}/ai/insights`
- `GET /api/v1/restaurants/{restaurant_id}/dashboard/revenue-history`

## 6. Services

### 6.1 `inventory_service.py`

Arquivo: [backend/services/inventory_service.py](/abs/path/C:/Users/usuario/Downloads/hackathon4/backend/services/inventory_service.py)

Funcoes centrais:

- `get_menu_item_for_restaurant()`
- `consume_menu_item_stock()`
- `restore_menu_item_stock()`
- `status_requires_stock()`

Regras:

- prato sem receita gera erro
- estoque insuficiente gera erro
- consumo e restauracao sao feitos item a item

### 6.2 `revenue_daily_service.py`

Arquivo: [backend/services/revenue_daily_service.py](/abs/path/C:/Users/usuario/Downloads/hackathon4/backend/services/revenue_daily_service.py)

Funcoes centrais:

- `sync_revenue_daily_for_date()`
- `sync_revenue_daily_for_dates()`
- `rebuild_revenue_daily_for_restaurant()`
- `ensure_revenue_daily_for_restaurant()`

Responsabilidade:

- recalcular o faturamento de um dia
- recalcular multiplos dias afetados
- reconstruir o historico consolidado

### 6.3 `dashboard_ai_service.py`

Arquivo: [backend/services/dashboard_ai_service.py](/abs/path/C:/Users/usuario/Downloads/hackathon4/backend/services/dashboard_ai_service.py)

Responsabilidade:

- carregar pedidos
- carregar faturamento diario
- montar grafico
- executar previsao
- gerar insights

Elementos principais:

- `LOOK_BACK = 30`
- `FORECAST_HORIZON = 7`
- `ProductRNN`
- `RevenueScaler`

## 7. IA e Previsao

### 7.1 Origem dos dados

Os dados usados na IA vem de:

- pedidos do banco
- dataset `deliveries_train.csv`

### 7.2 Fluxo da previsao

1. os pedidos sao agrupados por prato e por dia
2. a receita por prato vira uma serie temporal
3. cada serie e treinada em uma RNN
4. a previsao por prato e somada em uma previsao total

### 7.3 Insights gerados

O dashboard usa os pedidos e a previsao para gerar:

- periodo de maior demanda
- taxa de cancelamento
- ticket medio
- comparacao entre dia atual e previsao
- volume de pedidos entregues

## 8. Frontend

### 8.1 Base

Arquivos principais:

- [front/app/app.vue](/abs/path/C:/Users/usuario/Downloads/hackathon4/front/app/app.vue)
- [front/app/composables/useRestaurantAuth.ts](/abs/path/C:/Users/usuario/Downloads/hackathon4/front/app/composables/useRestaurantAuth.ts)
- [front/app/pages/dashboard.vue](/abs/path/C:/Users/usuario/Downloads/hackathon4/front/app/pages/dashboard.vue)
- [front/app/pages/orders.vue](/abs/path/C:/Users/usuario/Downloads/hackathon4/front/app/pages/orders.vue)
- [front/app/pages/menu.vue](/abs/path/C:/Users/usuario/Downloads/hackathon4/front/app/pages/menu.vue)
- [front/app/pages/inventory.vue](/abs/path/C:/Users/usuario/Downloads/hackathon4/front/app/pages/inventory.vue)

### 8.2 Auth Composable

`useRestaurantAuth.ts` concentra:

- token JWT
- identidade do restaurante
- login
- cadastro
- logout
- carregamento de perfil

### 8.3 Dashboard

`dashboard.vue` exibe:

- cards de metricas
- grafico de faturamento
- pedidos por periodo
- ranking de pratos
- insight da IA
- modal com historico completo

O grafico de faturamento:

- mostra 2 dias passados
- mostra 1 dia atual
- mostra 7 dias previstos
- destaca previsao com transparencia
- preserva hover com tooltip de detalhes do dia

### 8.4 Pedidos

`orders.vue`:

- usa cardapio real para selecao de prato
- integra pedido com estoque
- inclui atalho para cadastrar item no cardapio

### 8.5 Cardapio

`menu.vue`:

- cadastra pratos
- vincula ingredientes aos itens de estoque
- permite editar receita do prato

### 8.6 Estoque

`inventory.vue`:

- cadastra itens
- altera quantidade
- monitora minimo
- serve como base para as receitas do cardapio

## 9. Endpoints Principais

Autenticacao:

- `POST /auth/restaurants/register`
- `POST /auth/restaurants/login`
- `GET /restaurants/me`

Cardapio:

- `GET /restaurants/menu/items`
- `POST /restaurants/menu/items`
- `PATCH /restaurants/menu/items/{id}`
- `DELETE /restaurants/menu/items/{id}`
- `GET /restaurants/menu/items/{id}/recipe`
- `PUT /restaurants/menu/items/{id}/recipe`

Estoque:

- `GET /restaurants/inventory/items`
- `POST /restaurants/inventory/items`
- `PATCH /restaurants/inventory/items/{id}`
- `DELETE /restaurants/inventory/items/{id}`

Pedidos:

- `GET /restaurants/orders`
- `POST /restaurants/orders`
- `GET /restaurants/orders/{id}`
- `PATCH /restaurants/orders/{id}`
- `DELETE /restaurants/orders/{id}`

Dashboard:

- `GET /api/v1/restaurants/{restaurant_id}/dashboard`
- `GET /api/v1/restaurants/{restaurant_id}/dashboard/revenue-history`
- `GET /api/v1/restaurants/{restaurant_id}/ai/insights`

## 10. Persistencia e Seeds

Scripts relevantes:

- [backend/populate_database.py](/abs/path/C:/Users/usuario/Downloads/hackathon4/backend/populate_database.py)
- [backend/seed_admin_orders.py](/abs/path/C:/Users/usuario/Downloads/hackathon4/backend/seed_admin_orders.py)
- [backend/seed_admin_revenue_and_menu.py](/abs/path/C:/Users/usuario/Downloads/hackathon4/backend/seed_admin_revenue_and_menu.py)

Uso:

- criar base inicial
- popular restaurante admin
- montar demo com pedidos, cardapio e estoque
- reconstruir historico diario de faturamento

## 11. Fluxo de Atualizacao de Dados

### Criacao de pedido

1. frontend envia payload do pedido
2. backend valida restaurante e prato
3. backend consome estoque
4. backend grava pedido
5. backend sincroniza `RevenueDaily`

### Edicao de pedido

1. frontend envia alteracao
2. backend recalcula regra de estoque
3. backend atualiza pedido
4. backend ressincroniza faturamento diario afetado

### Exclusao de pedido

1. backend remove pedido
2. backend recalcula o dia correspondente em `RevenueDaily`

## 12. Resumo Final

O sistema combina CRUD operacional com analise preditiva. A parte mais importante da arquitetura e a separacao entre:

- dados transacionais em `Order`, `MenuItem` e `InventoryItem`
- dados agregados em `RevenueDaily`
- processamento inteligente em `dashboard_ai_service.py`
- interface interativa em Nuxt/Vue

Essa separacao reduz custo de consulta, simplifica o dashboard e permite manter o historico completo de faturamento e a previsao de forma consistente.

