# Arquitetura e Funcionamento do Sistema

## Visao geral

Este projeto e uma plataforma para operacao de restaurante com foco em:

- gestao de cardapio
- controle de estoque
- registro e acompanhamento de pedidos
- painel de dashboard com faturamento e insights
- uso de IA para previsao e analise operacional

A aplicacao e dividida em dois blocos principais:

- `backend/`: API Flask com banco SQLite, JWT, SQLAlchemy e migrations
- `front/`: interface Nuxt 3/Vue para o restaurante operar o sistema

Existe ainda um conjunto de scripts e dados em `ia/` e `backend/datasets/` usados para seed, analise e previsao.

## Arquitetura Geral

O fluxo principal funciona assim:

1. O restaurante faz login no frontend.
2. O frontend armazena o token JWT e carrega o perfil do restaurante.
3. As telas consomem a API Flask para listar cardapio, pedidos, estoque e dashboard.
4. Ao criar ou atualizar pedidos, o backend valida o prato, controla estoque e registra os dados no banco.
5. O dashboard le os pedidos reais e o historico diario persistido para exibir faturamento, insights e previsao.

## Backend

### Tecnologias

- Flask
- Flask-JWT-Extended
- Flask-SQLAlchemy
- Flask-Migrate/Alembic
- Pydantic e Spectree para validacao e documentacao
- SQLite como banco local em `backend/app.db`

### Inicializacao

O app e criado em `backend/factory.py` e exposto por `backend/main.py`.

### Modelos principais

- `Restaurant`: empresa logada, com credenciais e relacoes com cardapio, estoque e pedidos.
- `MenuItem`: prato do cardapio, com preco e lista de ingredientes.
- `InventoryItem`: item de estoque com quantidade disponivel e minimo.
- `MenuItemRecipe`: liga um prato aos itens de estoque e define quanto cada item consume.
- `Order`: pedido do restaurante.
- `RevenueDaily`: tabela materializada com faturamento diario por restaurante.

### Regras de negocio

#### Cardapio

O cardapio e gerenciado por restaurante autenticado. Cada prato pode ter:

- nome
- preco
- ingredientes visiveis na interface
- receita de estoque vinculada

#### Estoque

O estoque e controlado por itens cadastrados pelo restaurante. A receita de um prato informa quais itens sao consumidos quando o prato sai.

#### Pedidos

Ao criar um pedido:

- o backend valida se o prato existe no cardapio do restaurante
- o backend exige que a receita de estoque do prato esteja configurada
- itens de estoque sao debitados automaticamente quando o pedido exige consumo de estoque

Se o pedido e cancelado ou alterado para um estado que nao exige baixa, o estoque pode ser devolvido conforme a regra do servico de inventario.

#### Faturamento diario

O sistema grava o faturamento por dia em `RevenueDaily`.

Essa tabela serve para:

- historico completo do dashboard
- paginação de faturamento
- leitura rapida sem precisar reprocessar todos os pedidos toda vez

### Endpoints relevantes

- `POST /auth/restaurants/login`
- `POST /auth/restaurants/register`
- `GET /restaurants/me`
- `GET /restaurants/menu/items`
- `POST /restaurants/menu/items`
- `PATCH /restaurants/menu/items/{id}`
- `PUT /restaurants/menu/items/{id}/recipe`
- `GET /restaurants/inventory/items`
- `POST /restaurants/inventory/items`
- `GET /restaurants/orders`
- `POST /restaurants/orders`
- `PATCH /restaurants/orders/{id}`
- `DELETE /restaurants/orders/{id}`
- `GET /api/v1/restaurants/{restaurant_id}/dashboard`
- `GET /api/v1/restaurants/{restaurant_id}/dashboard/revenue-history`
- `GET /api/v1/restaurants/{restaurant_id}/ai/insights`

### Dashboard no backend

O controlador de dashboard expoe os dados consolidados do restaurante:

- total de pedidos do periodo
- faturamento do dia
- prato mais vendido
- faturamento por dia
- pedidos por periodo
- ranking de pratos
- insights da IA

O faturamento por dia agora e montado a partir da tabela `revenue_daily`, e nao recalculando tudo em memoria.

### Services

#### `dashboard_ai_service.py`

Responsavel por:

- carregar pedidos e faturamento
- construir serie historica
- gerar previsao de faturamento
- montar insights operacionais

#### `revenue_daily_service.py`

Responsavel por:

- sincronizar a tabela `RevenueDaily`
- recalcular dias afetados por criacao, edicao ou exclusao de pedidos
- reconstruir o historico diario quando necessario

#### `inventory_service.py`

Responsavel por:

- validar e consumir estoque
- restaurar estoque quando necessario
- garantir consistencia entre pedido e receita do prato

## IA e Analise Preditiva

### Origem dos dados

O sistema usa os dados de pedidos e o dataset `deliveries_train.csv` para alimentar o comportamento analitico do dashboard e os scripts de seed.

Os dados de treino ficam em:

- `backend/datasets/deliveries_train.csv`
- `ia/datasets/deliveries_train.csv`

### O que a IA faz

O servico de IA do dashboard faz duas coisas:

1. cria uma previsao de faturamento para os proximos dias
2. gera insights operacionais baseados no historico real

### Previsao de faturamento

O modelo usa uma RNN simples para prever a serie de receita por produto e consolidar a projeecao diaria.

Parametros principais:

- janela historica de 30 dias (`LOOK_BACK`)
- horizonte de previsao de 7 dias (`FORECAST_HORIZON`)

O fluxo e:

1. os pedidos sao agrupados por prato e dia
2. cada prato vira uma serie temporal de faturamento
3. a RNN aprende o comportamento historico
4. a previsao individual por prato e somada para formar a previsao total

### Insights

A IA tambem gera insights com base em:

- distribuiçao de pedidos por periodo
- taxa de cancelamento
- ticket medio
- comparacao entre o dia de referencia e a previsao
- volume de pedidos entregues

Esses insights aparecem no card de IA da dashboard e no endpoint de insights.

## Frontend

### Tecnologias

- Nuxt 3
- Vue 3 com `script setup`
- TypeScript
- composables para auth e chamadas de API

### Autenticacao no frontend

O composable `useRestaurantAuth.ts` centraliza:

- token JWT
- identidade do restaurante
- login
- registro
- logout
- recarga de perfil

Ele persiste o estado em cookies para manter a sessao entre recarregamentos.

### Páginas principais

#### `dashboard.vue`

Mostra:

- indicadores principais
- grafico de faturamento
- pedidos por periodo
- pratos mais vendidos
- insights de IA
- modal de historico completo com paginação

No grafico de faturamento:

- os 2 dias anteriores, o dia atual e 7 dias futuros sao exibidos
- pontos de previsao usam estilo transparente para diferenciar do real
- ao passar o mouse, o usuario ve data, faturamento e produto mais vendido do dia

#### `orders.vue`

Modal de novo pedido:

- seleciona prato a partir do cardapio real
- a ultima opcao leva para cadastrar item no cardapio
- integra pedido com estoque e valida receita

#### `menu.vue`

Cadastro de prato:

- ingredientes sao escolhidos entre os itens de estoque disponiveis
- o prato pode ser vinculado a uma receita de estoque

#### `inventory.vue`

Gerencia itens de estoque do restaurante:

- nome
- unidade
- quantidade
- minimo de alerta

### UX de dashboard

O grafico do dashboard foi desenhado para:

- destacar a barra ao passar o mouse
- mostrar tooltip com informacoes do dia
- diferenciar previsao com transparncia e padrao visual distinto
- manter o historico completo em modal paginado

## Scripts de Seed e Base de Dados

### `populate_database.py`

Cria o usuario admin e o restaurante seed.

### `seed_admin_orders.py`

Popula pedidos de exemplo para a conta admin.

### `seed_admin_revenue_and_menu.py`

Recria:

- cardapio
- estoque
- receitas
- pedidos
- faturamento diario

com base em `deliveries_train.csv`.

Esse script e importante para a demo porque alinha o banco ao comportamento esperado pela dashboard.

## Persistencia e Migrations

O projeto usa Alembic/Flask-Migrate para evolucao de schema.

As migrations cobrem:

- restaurantes
- pedidos
- cardapio
- estoque
- receitas de estoque
- faturamento diario

## Fluxo de Dados Resumido

1. O usuario entra no frontend e autentica.
2. O frontend carrega o perfil do restaurante.
3. A dashboard consulta o backend.
4. O backend monta os dados do periodo usando pedidos, estoque e faturamento diario.
5. A IA gera a previsao e os insights.
6. O frontend exibe graficos, tabelas e modais com esses dados.

## Como Executar

Backend:

```powershell
python -m flask --app main db upgrade
python main.py
```

Frontend:

```bash
npm install
npm run dev
```

## Observacoes de Implementacao

- O banco local e SQLite em `backend/app.db`.
- O dashboard depende da tabela `revenue_daily` para historico consistente.
- O frontend tem fallback de dados mockados para demonstracao.
- O historico completo do faturamento usa paginacao para nao sobrecarregar a interface.

