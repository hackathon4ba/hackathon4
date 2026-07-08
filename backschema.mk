# Backend Schema - Rotas necessarias

Este documento descreve as rotas que um backend precisaria expor para substituir os dados mockados do frontend em `front/app`.

Estado atual observado:

- O frontend e um app Nuxt.
- Nao existem chamadas reais para API.
- Os dados vem de `front/app/data/mock.ts`.
- A unica mutacao atual e local, em `front/app/pages/orders.vue`, ao adicionar um pedido em memoria.
- A sidebar fixa a loja como aberta e o usuario como `gerente@restaurante.com`.

Objetivo do backend:

- Tornar dashboard, pedidos, financeiro, cardapio, entregas, clientes, fidelidade, recompensas, Copilot, desempenho e ajuda 100% funcionais.
- Persistir dados.
- Aplicar filtros visiveis na UI.
- Alimentar graficos, tabelas, cards, exportacoes e acoes dos botoes.
- Cumprir o desafio "Programa de Pontos e Recompensas": clientes criam conta, fazem login, acumulam pontos automaticamente a cada pedido finalizado e resgatam recompensas cadastradas pelo restaurante.
- Oferecer uma area/API de cliente, alem da area/API de gerente do restaurante.

## Requisitos do desafio

Lidos de `requisitos.PNG`.

Funcionais obrigatorios:

- Cliente cria conta, faz login e resgata recompensas.
- Restaurante cadastra recompensas com nome, descricao e quantidade de pontos necessarios para resgate.
- A cada pedido finalizado, o sistema adiciona pontos automaticamente ao saldo do cliente. Regra base: `R$ 1,00 = 1 ponto`.
- Cliente visualiza saldo atual de pontos.
- Cliente solicita resgate de recompensa se tiver pontos suficientes, e o saldo e descontado automaticamente.
- Backend integra um modelo de inteligencia artificial que gere valor ao produto.

Funcionais opcionais:

- Cliente visualiza historico completo de ganhos e resgates.
- Painel do restaurante exibe ranking dos 5 clientes com mais pontos acumulados.

Nao funcionais que impactam backend:

- Codigo organizado e com comentarios nos pontos de regra de negocio e decisoes arquiteturais.
- Tempo de resposta rapido nas acoes do usuario.
- Senhas armazenadas com hash forte, nunca em texto puro.

Datasets disponiveis:

- `orders.csv`: historico de pedidos dos clientes de um unico restaurante.
- `rewards_catalog.csv`: recompensa que cada cliente resgatou posteriormente.

## Convencoes gerais

Base sugerida:

```http
/api/v1
```

Autenticacao:

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

Permissoes:

- Token de gerente acessa rotas administrativas do restaurante.
- Token de cliente acessa apenas os proprios dados, saldo, historico e resgates.
- `accessToken` deve carregar `subjectType` (`manager` ou `customer`) e escopos/permissoes.
- Senhas devem ser armazenadas com Argon2id ou bcrypt, com salt unico por usuario.

Padroes:

- Datas em `YYYY-MM-DD`.
- Horarios em ISO 8601.
- Valores monetarios em centavos (`amountCents`) para evitar erro de ponto flutuante.
- Respostas paginadas usam `data` e `meta`.
- Todas as rotas com dados do restaurante devem ser escopadas por `restaurantId`.
- Campos de exibicao como `label`, `statusLabel` e `severity` podem ser enviados pelo backend para reduzir regra duplicada no frontend.

Resposta paginada padrao:

```json
{
  "data": [],
  "meta": {
    "page": 1,
    "pageSize": 20,
    "total": 0,
    "totalPages": 0
  }
}
```

Severidades para badges:

```ts
type Severity = "green" | "orange" | "red" | "neutral"
```

Status de pedido sugeridos:

```ts
type OrderStatus =
  | "preparing"
  | "out_for_delivery"
  | "delivered"
  | "delayed"
  | "cancelled"
```

## Autenticacao, usuarios e restaurante

### POST `/api/v1/auth/login`

Autentica o gerente do restaurante.

Body:

```json
{
  "email": "gerente@restaurante.com",
  "password": "senha"
}
```

Response `200`:

```json
{
  "accessToken": "jwt",
  "refreshToken": "jwt",
  "user": {
    "id": "usr_123",
    "name": "Gerente",
    "email": "gerente@restaurante.com"
  },
  "restaurant": {
    "id": "rst_123",
    "name": "Restaurante Sabor da Casa"
  }
}
```

### POST `/api/v1/auth/customers/register`

Cria a conta de um cliente final.

Body:

```json
{
  "name": "Ana Paula",
  "email": "ana@example.com",
  "password": "senha-segura",
  "phone": "+5511999999999"
}
```

Response `201`:

```json
{
  "accessToken": "jwt",
  "refreshToken": "jwt",
  "customer": {
    "id": "cus_123",
    "name": "Ana Paula",
    "email": "ana@example.com",
    "phone": "+5511999999999"
  }
}
```

### POST `/api/v1/auth/customers/login`

Autentica o cliente final para consultar pontos e resgatar recompensas.

Body:

```json
{
  "email": "ana@example.com",
  "password": "senha-segura"
}
```

Response `200`:

```json
{
  "accessToken": "jwt",
  "refreshToken": "jwt",
  "customer": {
    "id": "cus_123",
    "name": "Ana Paula",
    "email": "ana@example.com"
  }
}
```

### POST `/api/v1/auth/refresh`

Renova o token.

### POST `/api/v1/auth/logout`

Encerra a sessao.

### GET `/api/v1/me`

Substitui o usuario hard-coded da sidebar.

Response `200`:

```json
{
  "id": "usr_123",
  "name": "Gerente",
  "email": "gerente@restaurante.com",
  "restaurantId": "rst_123",
  "role": "manager"
}
```

### GET `/api/v1/customer/me`

Retorna dados do cliente logado.

Response `200`:

```json
{
  "id": "cus_123",
  "name": "Ana Paula",
  "email": "ana@example.com",
  "phone": "+5511999999999"
}
```

### GET `/api/v1/restaurants/{restaurantId}`

Retorna dados da loja.

Response `200`:

```json
{
  "id": "rst_123",
  "name": "Restaurante Sabor da Casa",
  "displayName": "Meu Restaurante",
  "isOpen": true,
  "statusLabel": "Loja aberta",
  "statusDetail": "Dentro do horario programado",
  "timezone": "America/Sao_Paulo"
}
```

### PATCH `/api/v1/restaurants/{restaurantId}/status`

Abre, fecha ou agenda status da loja.

Body:

```json
{
  "isOpen": true,
  "reason": "Dentro do horario programado"
}
```

## Dashboard

Usado por `dashboard.vue`.

### GET `/api/v1/restaurants/{restaurantId}/dashboard`

Retorna uma visao agregada para cards, graficos, insight e pedidos recentes.

Query:

- `period`: `today`, `last_7_days`, `last_30_days`, `custom`
- `startDate`: `YYYY-MM-DD`
- `endDate`: `YYYY-MM-DD`

Response `200`:

```json
{
  "metrics": [
    {
      "key": "orders_today",
      "label": "Pedidos hoje",
      "value": "128",
      "detail": "+12% vs. ontem",
      "tone": "positive"
    }
  ],
  "revenueByDay": [
    { "label": "Seg", "date": "2026-07-01", "valueCents": 360000 }
  ],
  "ordersByPeriod": [
    { "label": "Jantar", "period": "dinner", "value": 40 }
  ],
  "bestDishes": [
    { "label": "Parmegiana", "menuItemId": "itm_123", "value": 34 }
  ],
  "deliveryByNeighborhood": [
    { "label": "Centro", "neighborhood": "Centro", "valueMinutes": 27 }
  ],
  "recentOrders": [],
  "insight": {
    "title": "Insight do Copilot",
    "text": "Seu pico de pedidos acontece no jantar. Reforce a operacao entre 19h e 21h.",
    "severity": "green"
  }
}
```

### GET `/api/v1/restaurants/{restaurantId}/dashboard/export`

Exporta a visao geral filtrada.

Query:

- `period`
- `startDate`
- `endDate`
- `format`: `csv` ou `xlsx`

Response:

- `200` com arquivo, ou
- `202` com `jobId` se a exportacao for assincrona.

## Pedidos

Usado por `orders.vue` e pelo resumo de pedidos recentes no dashboard.

### GET `/api/v1/restaurants/{restaurantId}/orders`

Lista pedidos com filtros.

Query:

- `status`: `preparing`, `out_for_delivery`, `delivered`, `delayed`, `cancelled`
- `period`: `today`, `last_7_days`, `custom`
- `startDate`
- `endDate`
- `q`: busca por numero, cliente ou prato
- `page`
- `pageSize`

Response `200`:

```json
{
  "data": [
    {
      "id": "ord_8421",
      "displayId": "#8421",
      "customerId": "cus_123",
      "customerName": "Ana Paula",
      "items": [
        {
          "menuItemId": "itm_123",
          "name": "Parmegiana",
          "quantity": 1,
          "unitPriceCents": 5490
        }
      ],
      "mainDish": "Parmegiana",
      "period": "dinner",
      "periodLabel": "Jantar",
      "subtotalCents": 5490,
      "discountCents": 0,
      "totalCents": 5490,
      "pointsEarned": 54,
      "loyaltyProcessedAt": "2026-07-07T22:27:00-03:00",
      "status": "delivered",
      "statusLabel": "Entregue",
      "severity": "green",
      "createdAt": "2026-07-07T22:10:00-03:00"
    }
  ],
  "meta": {
    "page": 1,
    "pageSize": 20,
    "total": 1,
    "totalPages": 1
  }
}
```

### POST `/api/v1/restaurants/{restaurantId}/orders`

Cria pedido. Substitui o `addOrder()` local.

Body minimo compativel com a tela atual:

```json
{
  "customerName": "Ana Paula",
  "dishName": "Parmegiana",
  "period": "dinner",
  "totalCents": 5490,
  "status": "preparing"
}
```

Body ideal quando cardapio/clientes estiverem integrados:

```json
{
  "customerId": "cus_123",
  "items": [
    {
      "menuItemId": "itm_123",
      "quantity": 1
    }
  ],
  "period": "dinner",
  "redeemedRewardId": "red_123",
  "status": "preparing"
}
```

Se `redeemedRewardId` for enviado:

- Validar se o resgate pertence ao cliente do pedido e ao restaurante.
- Aceitar apenas resgates com status `issued`.
- Aplicar o beneficio no pedido (`discountCents`, `freeMenuItemId` ou frete gratis).
- Marcar o resgate como `used` quando o pedido for criado.

Response `201`:

```json
{
  "id": "ord_8422",
  "displayId": "#8422",
  "customerName": "Ana Paula",
  "mainDish": "Parmegiana",
  "periodLabel": "Jantar",
  "subtotalCents": 5490,
  "discountCents": 0,
  "totalCents": 5490,
  "pointsEarned": 0,
  "status": "preparing",
  "statusLabel": "Em preparo",
  "severity": "orange"
}
```

### GET `/api/v1/restaurants/{restaurantId}/orders/{orderId}`

Detalhe de um pedido clicado na tabela.

### PATCH `/api/v1/restaurants/{restaurantId}/orders/{orderId}`

Edita campos gerais de um pedido.

### PATCH `/api/v1/restaurants/{restaurantId}/orders/{orderId}/status`

Atualiza status operacional.

Regra de fidelidade:

- Ao mudar um pedido para `delivered`, creditar pontos automaticamente ao cliente do pedido.
- Regra padrao: `floor(totalCents / 100) * pointsPerReal`.
- O credito precisa ser idempotente: o mesmo pedido nao pode gerar pontos duas vezes.
- Pedidos `cancelled` nao geram pontos e devem reverter credito ainda pendente, se houver.

Body:

```json
{
  "status": "out_for_delivery"
}
```

Response `200` quando o pedido e finalizado:

```json
{
  "id": "ord_8421",
  "status": "delivered",
  "pointsEarned": 54,
  "loyaltyTransactionId": "lotx_123",
  "customerPointsBalance": 896
}
```

### POST `/api/v1/restaurants/{restaurantId}/orders/{orderId}/cancel`

Cancela pedido com motivo.

Body:

```json
{
  "reason": "Cliente solicitou cancelamento"
}
```

### GET `/api/v1/restaurants/{restaurantId}/orders/summary`

Alimenta o card "Resumo da fila".

Query:

- `period`
- `startDate`
- `endDate`

Response `200`:

```json
{
  "totalOrders": 5,
  "preparing": 1,
  "averageTicketCents": 4490,
  "attentionOrders": 1
}
```

## Financeiro

Usado por `finance.vue` e pelos graficos de faturamento.

### GET `/api/v1/restaurants/{restaurantId}/finance/summary`

Query:

- `period`: `today`, `last_7_days`, `last_30_days`, `custom`
- `startDate`
- `endDate`

Response `200`:

```json
{
  "grossRevenueCents": 3842000,
  "feesCents": 431200,
  "couponDiscountCents": 118600,
  "netRevenueCents": 3292200,
  "rows": [
    {
      "key": "gross_revenue",
      "label": "Receita bruta",
      "valueCents": 3842000,
      "formattedValue": "R$ 38.420",
      "detail": "+9,8% vs. semana anterior"
    }
  ]
}
```

### GET `/api/v1/restaurants/{restaurantId}/finance/revenue-by-day`

Query:

- `startDate`
- `endDate`

Response `200`:

```json
{
  "data": [
    {
      "date": "2026-07-01",
      "label": "Seg",
      "grossRevenueCents": 360000
    }
  ]
}
```

### GET `/api/v1/restaurants/{restaurantId}/finance/export`

Exporta relatorio financeiro.

Query:

- `startDate`
- `endDate`
- `format`: `csv`, `xlsx` ou `pdf`

## Cardapio

Usado por `menu.vue`, pelo ranking de pratos e pela criacao ideal de pedidos.

### GET `/api/v1/restaurants/{restaurantId}/menu/items`

Query:

- `categoryId`
- `categoryName`
- `status`: `active`, `inactive`, `low_stock`
- `q`
- `page`
- `pageSize`

Response `200`:

```json
{
  "data": [
    {
      "id": "itm_123",
      "name": "Parmegiana",
      "categoryId": "cat_1",
      "categoryName": "Pratos principais",
      "priceCents": 5490,
      "salesCount": 34,
      "status": "active",
      "statusLabel": "Ativo",
      "severity": "green",
      "isAvailable": true,
      "stockQuantity": 20
    }
  ],
  "meta": {
    "page": 1,
    "pageSize": 20,
    "total": 1,
    "totalPages": 1
  }
}
```

### POST `/api/v1/restaurants/{restaurantId}/menu/items`

Cria item para o botao "Novo item".

Body:

```json
{
  "name": "Parmegiana",
  "categoryId": "cat_1",
  "description": "Acompanha arroz e fritas",
  "priceCents": 5490,
  "isAvailable": true,
  "stockQuantity": 20
}
```

### GET `/api/v1/restaurants/{restaurantId}/menu/items/{itemId}`

Detalhe do item clicado.

### PATCH `/api/v1/restaurants/{restaurantId}/menu/items/{itemId}`

Edita nome, categoria, descricao, preco e estoque.

### PATCH `/api/v1/restaurants/{restaurantId}/menu/items/{itemId}/availability`

Pausa ou reativa item.

Body:

```json
{
  "isAvailable": false,
  "reason": "Baixo estoque"
}
```

### DELETE `/api/v1/restaurants/{restaurantId}/menu/items/{itemId}`

Remove ou arquiva item.

### GET `/api/v1/restaurants/{restaurantId}/menu/categories`

Lista categorias para filtros e formulario.

Response `200`:

```json
{
  "data": [
    { "id": "cat_1", "name": "Pratos principais" },
    { "id": "cat_2", "name": "Lanches" }
  ]
}
```

## Entregas

Usado por `deliveries.vue` e dashboard.

### GET `/api/v1/restaurants/{restaurantId}/deliveries/summary`

Retorna tempos medios por bairro e alerta operacional.

Query:

- `period`
- `startDate`
- `endDate`

Response `200`:

```json
{
  "averageByNeighborhood": [
    {
      "neighborhood": "Centro",
      "label": "Centro",
      "averageMinutes": 27
    }
  ],
  "alert": {
    "title": "Alerta operacional",
    "text": "Vila Nova esta acima da meta de entrega. Priorize moto e revise raio no jantar.",
    "severity": "red"
  }
}
```

### GET `/api/v1/restaurants/{restaurantId}/deliveries`

Lista rotas recentes.

Query:

- `status`: `delivered`, `on_route`, `attention`, `cancelled`
- `neighborhood`
- `q`: pedido ou entregador
- `page`
- `pageSize`

Response `200`:

```json
{
  "data": [
    {
      "id": "del_123",
      "orderId": "ord_8421",
      "orderDisplayId": "#8421",
      "courierId": "cou_123",
      "courierName": "Bruno Martins",
      "neighborhood": "Centro",
      "elapsedMinutes": 27,
      "status": "delivered",
      "statusLabel": "Entregue",
      "severity": "green",
      "startedAt": "2026-07-07T22:00:00-03:00",
      "deliveredAt": "2026-07-07T22:27:00-03:00"
    }
  ],
  "meta": {
    "page": 1,
    "pageSize": 20,
    "total": 1,
    "totalPages": 1
  }
}
```

### GET `/api/v1/restaurants/{restaurantId}/deliveries/{deliveryId}`

Detalhe da entrega.

### PATCH `/api/v1/restaurants/{restaurantId}/deliveries/{deliveryId}/status`

Atualiza status da entrega.

### GET `/api/v1/restaurants/{restaurantId}/deliveries/map`

Alimenta o botao "Ver mapa".

Response `200`:

```json
{
  "data": [
    {
      "deliveryId": "del_123",
      "orderDisplayId": "#8421",
      "courierName": "Bruno Martins",
      "status": "on_route",
      "lat": -23.55052,
      "lng": -46.633308,
      "destination": {
        "neighborhood": "Centro",
        "lat": -23.551,
        "lng": -46.634
      }
    }
  ]
}
```

## Clientes

Usado por `customers.vue`, `loyalty.vue` e acoes de campanha.

### GET `/api/v1/restaurants/{restaurantId}/customers`

Query:

- `segment`: `vip`, `recurring`, `new`
- `lastOrderPeriod`: `today`, `last_7_days`, `last_30_days`
- `q`
- `page`
- `pageSize`

Response `200`:

```json
{
  "data": [
    {
      "id": "cus_123",
      "name": "Ana Paula",
      "ordersCount": 18,
      "totalSpentCents": 84240,
      "points": 842,
      "currentPoints": 842,
      "lifetimePoints": 896,
      "rewardRedemptionsCount": 2,
      "segment": "vip",
      "segmentLabel": "VIP",
      "lastOrderAt": "2026-07-07T21:40:00-03:00"
    }
  ],
  "meta": {
    "page": 1,
    "pageSize": 20,
    "total": 1,
    "totalPages": 1
  }
}
```

### GET `/api/v1/restaurants/{restaurantId}/customers/{customerId}`

Detalhe do cliente clicado.

### GET `/api/v1/restaurants/{restaurantId}/customers/segments`

Lista segmentos disponiveis para filtro.

### POST `/api/v1/restaurants/{restaurantId}/campaigns`

Atende o botao "Enviar campanha".

Body:

```json
{
  "name": "Campanha clientes VIP",
  "segment": "vip",
  "message": "Voce ganhou uma recompensa especial.",
  "rewardId": "rew_123",
  "channel": "whatsapp"
}
```

Response `201`:

```json
{
  "id": "cmp_123",
  "status": "scheduled",
  "targetCount": 36
}
```

## Fidelidade

Usado por `loyalty.vue`, area do cliente e fluxo de resgate.

Regras de dominio:

- `currentPoints` e o saldo disponivel para resgate.
- `lifetimePoints` e o total historico ganho pelo cliente no restaurante, usado para ranking.
- Ganhos e resgates devem gerar lancamentos no livro de pontos (`LoyaltyTransaction`) para auditoria.
- Resgate de recompensa deve ser transacional: validar saldo, criar resgate, debitar pontos e retornar o novo saldo na mesma operacao.
- Recompensas pausadas, arquivadas ou expiradas nao podem ser resgatadas.

### GET `/api/v1/restaurants/{restaurantId}/loyalty/rule`

Retorna regra ativa.

Response `200`:

```json
{
  "id": "loy_rule_1",
  "pointsPerReal": 1,
  "minOrderCents": 0,
  "isActive": true,
  "label": "R$1 = 1 ponto"
}
```

### PUT `/api/v1/restaurants/{restaurantId}/loyalty/rule`

Atende o botao "Ajustar regra".

Body:

```json
{
  "pointsPerReal": 1,
  "minOrderCents": 0,
  "isActive": true
}
```

### GET `/api/v1/restaurants/{restaurantId}/loyalty/summary`

Query:

- `period`
- `startDate`
- `endDate`

Response `200`:

```json
{
  "activeRuleLabel": "R$1 = 1 ponto",
  "generatedPoints": 2228,
  "eligibleCustomers": 36,
  "eligibilityThreshold": 120
}
```

### GET `/api/v1/restaurants/{restaurantId}/loyalty/ranking`

Lista ranking de pontos.

Query:

- `minPoints`
- `segment`
- `limit`: usar `5` para o painel opcional do enunciado
- `page`
- `pageSize`

Response igual a `customers`, adicionando:

```json
{
  "suggestedAction": "offer_reward",
  "suggestedActionLabel": "Oferecer recompensa"
}
```

### POST `/api/v1/restaurants/{restaurantId}/loyalty/points-adjustments`

Ajuste manual de pontos, se necessario.

Body:

```json
{
  "customerId": "cus_123",
  "points": 120,
  "reason": "Compensacao de atendimento"
}
```

Response `201`:

```json
{
  "id": "lotx_456",
  "customerId": "cus_123",
  "type": "manual_adjustment",
  "points": 120,
  "balanceAfter": 962,
  "createdAt": "2026-07-08T14:00:00-03:00"
}
```

### GET `/api/v1/restaurants/{restaurantId}/loyalty/ledger`

Lista lancamentos de pontos para auditoria do restaurante.

Query:

- `customerId`
- `type`: `earn`, `redeem`, `manual_adjustment`, `reversal`
- `startDate`
- `endDate`
- `page`
- `pageSize`

### GET `/api/v1/restaurants/{restaurantId}/customer/loyalty`

Retorna o saldo do cliente logado nesse restaurante.

Autenticacao: token de cliente.

Response `200`:

```json
{
  "restaurantId": "rst_123",
  "customerId": "cus_123",
  "currentPoints": 842,
  "lifetimePoints": 896,
  "pointsToNextReward": 18,
  "nextReward": {
    "id": "rew_180",
    "name": "Frete gratis",
    "costPoints": 180
  },
  "activeRuleLabel": "R$1 = 1 ponto"
}
```

### GET `/api/v1/restaurants/{restaurantId}/customer/loyalty/history`

Historico completo de ganhos e resgates do cliente logado.

Autenticacao: token de cliente.

Query:

- `type`: `earn`, `redeem`, `manual_adjustment`, `reversal`
- `page`
- `pageSize`

Response `200`:

```json
{
  "data": [
    {
      "id": "lotx_123",
      "type": "earn",
      "points": 54,
      "balanceAfter": 896,
      "orderId": "ord_8421",
      "description": "Pedido #8421 finalizado",
      "createdAt": "2026-07-07T22:27:00-03:00"
    },
    {
      "id": "lotx_124",
      "type": "redeem",
      "points": -120,
      "balanceAfter": 776,
      "rewardRedemptionId": "red_123",
      "description": "Resgate: Sobremesa gratis",
      "createdAt": "2026-07-08T13:45:00-03:00"
    }
  ],
  "meta": {
    "page": 1,
    "pageSize": 20,
    "total": 2,
    "totalPages": 1
  }
}
```

### GET `/api/v1/restaurants/{restaurantId}/customer/rewards`

Lista recompensas ativas disponiveis para o cliente logado resgatar.

Autenticacao: token de cliente.

Query:

- `affordable`: `true` para retornar apenas recompensas que o cliente consegue resgatar com o saldo atual.
- `page`
- `pageSize`

### POST `/api/v1/restaurants/{restaurantId}/customer/rewards/{rewardId}/redeem`

Cliente solicita resgate de uma recompensa.

Autenticacao: token de cliente.

Body:

```json
{
  "source": "customer_app"
}
```

Response `201`:

```json
{
  "id": "red_123",
  "rewardId": "rew_123",
  "rewardName": "Sobremesa gratis",
  "costPoints": 120,
  "status": "issued",
  "code": "SOB-8F2K",
  "customerId": "cus_123",
  "pointsBefore": 896,
  "pointsAfter": 776,
  "expiresAt": "2026-08-08T23:59:59-03:00",
  "createdAt": "2026-07-08T13:45:00-03:00"
}
```

Erros esperados:

- `400 reward_not_active`
- `400 reward_expired`
- `409 insufficient_points`
- `409 redemption_limit_reached`

### POST `/api/v1/restaurants/{restaurantId}/customers/{customerId}/reward-offers`

Atende o link "Oferecer recompensa".

Body:

```json
{
  "rewardId": "rew_123",
  "message": "Oferta especial para voce voltar hoje."
}
```

## Recompensas

Usado por `rewards.vue` e pela fidelidade.

### GET `/api/v1/restaurants/{restaurantId}/rewards`

Query:

- `status`: `active`, `paused`, `archived`
- `page`
- `pageSize`

Response `200`:

```json
{
  "data": [
    {
      "id": "rew_123",
      "name": "Sobremesa gratis",
      "description": "Uma sobremesa da casa sem custo no proximo pedido",
      "type": "free_item",
      "costPoints": 120,
      "discountCents": 0,
      "freeMenuItemId": "itm_987",
      "redemptionsCount": 18,
      "status": "active",
      "statusLabel": "Ativa",
      "severity": "green",
      "expiresAt": "2026-08-31T23:59:59-03:00"
    }
  ],
  "meta": {
    "page": 1,
    "pageSize": 20,
    "total": 1,
    "totalPages": 1
  }
}
```

### POST `/api/v1/restaurants/{restaurantId}/rewards`

Atende o botao "Nova recompensa".

Body:

```json
{
  "name": "Frete gratis",
  "description": "Cupom de frete gratis para clientes recorrentes",
  "type": "free_delivery",
  "costPoints": 180,
  "discountCents": 0,
  "freeMenuItemId": null,
  "redemptionLimitPerCustomer": 1,
  "status": "active",
  "expiresAt": "2026-08-31T23:59:59-03:00"
}
```

### GET `/api/v1/restaurants/{restaurantId}/rewards/{rewardId}`

Detalhe da recompensa.

### PATCH `/api/v1/restaurants/{restaurantId}/rewards/{rewardId}`

Edita recompensa.

### PATCH `/api/v1/restaurants/{restaurantId}/rewards/{rewardId}/status`

Pausa, ativa ou arquiva.

Body:

```json
{
  "status": "paused"
}
```

### GET `/api/v1/restaurants/{restaurantId}/rewards/insights`

Alimenta o card de insight.

Response `200`:

```json
{
  "data": [
    {
      "title": "Insight de recompensa",
      "text": "Frete gratis performa bem para clientes recorrentes com ticket acima de R$ 40.",
      "severity": "green"
    }
  ]
}
```

### GET `/api/v1/restaurants/{restaurantId}/reward-redemptions`

Historico de resgates.

Query:

- `rewardId`
- `customerId`
- `status`: `issued`, `used`, `expired`, `cancelled`
- `startDate`
- `endDate`
- `page`
- `pageSize`

Response `200`:

```json
{
  "data": [
    {
      "id": "red_123",
      "rewardId": "rew_123",
      "rewardName": "Sobremesa gratis",
      "customerId": "cus_123",
      "customerName": "Ana Paula",
      "costPoints": 120,
      "status": "used",
      "code": "SOB-8F2K",
      "orderId": "ord_8422",
      "createdAt": "2026-07-08T13:45:00-03:00",
      "usedAt": "2026-07-08T14:10:00-03:00"
    }
  ],
  "meta": {
    "page": 1,
    "pageSize": 20,
    "total": 1,
    "totalPages": 1
  }
}
```

## Copilot

Usado por `copilot.vue`, `dashboard.vue` e `rewards.vue`.

O requisito de inteligencia artificial do desafio pode ser atendido por um modelo de recomendacao/analise que usa `orders.csv`, `rewards_catalog.csv`, pedidos reais e historico de resgates para gerar sugestoes acionaveis ao restaurante.

### GET `/api/v1/restaurants/{restaurantId}/copilot/insights`

Lista recomendacoes acionaveis.

Query:

- `date`
- `period`
- `scope`: `dashboard`, `operations`, `rewards`, `loyalty`, `performance`

Response `200`:

```json
{
  "data": [
    {
      "id": "ins_123",
      "title": "Reforce o jantar",
      "text": "Seu pico acontece entre 19h e 21h. Deixe a equipe e os insumos prontos antes das 18h40.",
      "severity": "green",
      "source": "orders_analysis"
    }
  ]
}
```

### GET `/api/v1/restaurants/{restaurantId}/copilot/loyalty-recommendations`

Recomendacoes de IA especificas para fidelidade e recompensas.

Query:

- `period`
- `startDate`
- `endDate`
- `limit`

Response `200`:

```json
{
  "model": {
    "name": "loyalty_recommender",
    "version": "2026-07-08",
    "trainedWith": ["orders", "reward_redemptions"]
  },
  "data": [
    {
      "id": "rec_123",
      "type": "reward_optimization",
      "title": "Reduzir custo do frete gratis para 160 pontos",
      "text": "Clientes recorrentes com ticket acima de R$ 40 resgatam frete gratis com maior chance de recompra em ate 7 dias.",
      "severity": "green",
      "confidence": 0.78,
      "expectedImpact": {
        "metric": "repeat_purchase_rate",
        "direction": "increase",
        "value": "6%"
      },
      "suggestedAction": {
        "action": "update_reward_cost",
        "rewardId": "rew_180",
        "costPoints": 160
      }
    },
    {
      "id": "rec_124",
      "type": "customer_targeting",
      "title": "Oferecer sobremesa para 12 clientes em risco",
      "text": "Clientes com alto historico de pontos e sem pedido nos ultimos 21 dias tendem a voltar com recompensa de baixo custo.",
      "severity": "orange",
      "confidence": 0.71,
      "customerIds": ["cus_123", "cus_456"]
    }
  ]
}
```

### POST `/api/v1/restaurants/{restaurantId}/copilot/loyalty-recommendations/{recommendationId}/apply`

Aplica uma recomendacao quando ela for automatizavel, por exemplo ajustar custo de pontos ou criar campanha segmentada.

Body:

```json
{
  "approvedByUserId": "usr_123"
}
```

Response `200`:

```json
{
  "status": "applied",
  "affectedResourceType": "reward",
  "affectedResourceId": "rew_180"
}
```

### POST `/api/v1/restaurants/{restaurantId}/copilot/plans/generate`

Atende o botao "Gerar plano".

Body:

```json
{
  "date": "2026-07-08",
  "focus": ["sales", "operations", "delivery"],
  "useLatestData": true
}
```

Response `201`:

```json
{
  "id": "plan_123",
  "date": "2026-07-08",
  "items": [
    {
      "id": "plan_item_1",
      "time": "19:00",
      "title": "Adicionar 1 pessoa no preparo de pratos quentes",
      "status": "pending"
    }
  ]
}
```

### GET `/api/v1/restaurants/{restaurantId}/copilot/plans/current`

Retorna o plano recomendado atual.

Query:

- `date`

### PATCH `/api/v1/restaurants/{restaurantId}/copilot/plans/{planId}/items/{itemId}`

Permite marcar acoes como pendentes, concluidas ou descartadas.

Body:

```json
{
  "status": "done"
}
```

## Desempenho

Usado por `performance.vue`.

### GET `/api/v1/restaurants/{restaurantId}/performance/summary`

Query:

- `period`
- `startDate`
- `endDate`

Response `200`:

```json
{
  "metrics": [
    {
      "key": "menu_conversion",
      "label": "Conversao do cardapio",
      "value": "18,4%",
      "detail": "+3,1 p.p.",
      "tone": "positive"
    },
    {
      "key": "completed_orders",
      "label": "Pedidos concluidos",
      "value": "96%",
      "detail": "Boa operacao",
      "tone": "positive"
    },
    {
      "key": "cancellations",
      "label": "Cancelamentos",
      "value": "2,1%",
      "detail": "Acompanhar",
      "tone": "warning"
    }
  ],
  "ordersByPeriod": [
    { "label": "Jantar", "period": "dinner", "value": 40 }
  ],
  "bestDishes": [
    { "label": "Parmegiana", "menuItemId": "itm_123", "value": 34 }
  ]
}
```

### GET `/api/v1/restaurants/{restaurantId}/performance/orders-by-period`

Endpoint especifico para o grafico de horarios de demanda.

### GET `/api/v1/restaurants/{restaurantId}/performance/best-items`

Endpoint especifico para ranking de itens fortes.

## Ajuda e suporte

Usado por `help.vue`.

### GET `/api/v1/help/articles`

Lista conteudos de ajuda.

Query:

- `q`
- `category`

Response `200`:

```json
{
  "data": [
    {
      "id": "hlp_123",
      "title": "Configurar cardapio",
      "text": "Revise disponibilidade, preco e categorias dos itens mais vendidos.",
      "category": "menu"
    }
  ]
}
```

### GET `/api/v1/restaurants/{restaurantId}/help/checklist`

Checklist contextual da demo ou onboarding.

Response `200`:

```json
{
  "data": [
    {
      "key": "dashboard",
      "label": "Dashboard",
      "text": "Indicadores e insight do Copilot",
      "completed": true
    }
  ]
}
```

### POST `/api/v1/support/tickets`

Atende o botao "Abrir chamado".

Body:

```json
{
  "restaurantId": "rst_123",
  "subject": "Duvida sobre cardapio",
  "message": "Preciso de ajuda para configurar itens.",
  "priority": "normal"
}
```

Response `201`:

```json
{
  "id": "tic_123",
  "status": "open",
  "createdAt": "2026-07-08T14:00:00-03:00"
}
```

### GET `/api/v1/support/tickets`

Lista chamados do usuario/restaurante.

## Importacao dos datasets

Usado para carregar os CSVs fornecidos no desafio e popular a base inicial do restaurante.

### POST `/api/v1/restaurants/{restaurantId}/datasets/import`

Importa `orders.csv` e `rewards_catalog.csv`.

Content-Type: `multipart/form-data`

Campos:

- `orders`: arquivo `orders.csv`
- `rewardRedemptions`: arquivo `rewards_catalog.csv`
- `mode`: `append` ou `replace_demo_data`

Regras:

- Criar ou atualizar clientes a partir dos pedidos.
- Importar pedidos historicos como `delivered`, quando aplicavel.
- Calcular pontos ganhos conforme a regra ativa, preservando idempotencia por identificador de pedido.
- Importar resgates historicos e debitar pontos correspondentes, sem deixar saldo negativo; divergencias devem ir para `warnings`.
- Gerar um resumo para conferencia do hackathon.

Response `202`:

```json
{
  "jobId": "imp_123",
  "status": "processing"
}
```

### GET `/api/v1/restaurants/{restaurantId}/datasets/imports/{jobId}`

Consulta o resultado da importacao.

Response `200`:

```json
{
  "id": "imp_123",
  "status": "done",
  "summary": {
    "ordersImported": 1280,
    "customersImported": 342,
    "rewardsImported": 3,
    "redemptionsImported": 91,
    "pointsGenerated": 38420
  },
  "warnings": [
    {
      "row": 42,
      "file": "rewards_catalog.csv",
      "message": "Cliente sem saldo suficiente no historico; resgate marcado para revisao."
    }
  ]
}
```

## Tempo real

Para a UI ficar realmente operacional sem depender apenas do botao "Atualizar fila", o backend deveria oferecer um canal de eventos.

### GET `/api/v1/restaurants/{restaurantId}/events`

SSE com eventos de pedidos, entregas, loja, alertas e Copilot.

Eventos sugeridos:

- `order.created`
- `order.updated`
- `order.status_changed`
- `loyalty.points_earned`
- `loyalty.points_redeemed`
- `reward.redeemed`
- `delivery.updated`
- `restaurant.status_changed`
- `copilot.insight_created`

Exemplo de evento:

```json
{
  "type": "order.status_changed",
  "occurredAt": "2026-07-08T14:00:00-03:00",
  "data": {
    "orderId": "ord_8421",
    "status": "out_for_delivery"
  }
}
```

## Modelos principais

### Metric

```ts
type Metric = {
  key: string
  label: string
  value: string
  detail: string
  tone: "positive" | "neutral" | "warning" | "danger"
}
```

### ChartDatum

```ts
type ChartDatum = {
  label: string
  value: number
}
```

### Order

```ts
type Order = {
  id: string
  displayId: string
  customerId?: string
  customerName: string
  mainDish: string
  period: "morning" | "lunch" | "afternoon" | "dinner"
  periodLabel: string
  subtotalCents: number
  discountCents: number
  totalCents: number
  redeemedRewardId?: string
  pointsEarned: number
  loyaltyTransactionId?: string
  loyaltyProcessedAt?: string
  status: OrderStatus
  statusLabel: string
  severity: Severity
  createdAt: string
}
```

### MenuItem

```ts
type MenuItem = {
  id: string
  name: string
  categoryId: string
  categoryName: string
  priceCents: number
  salesCount: number
  status: "active" | "inactive" | "low_stock"
  statusLabel: string
  severity: Severity
  isAvailable: boolean
  stockQuantity?: number
}
```

### Delivery

```ts
type Delivery = {
  id: string
  orderId: string
  orderDisplayId: string
  courierId?: string
  courierName: string
  neighborhood: string
  elapsedMinutes: number
  status: "delivered" | "on_route" | "attention" | "cancelled"
  statusLabel: string
  severity: Severity
}
```

### Customer

```ts
type Customer = {
  id: string
  name: string
  email?: string
  phone?: string
  ordersCount: number
  totalSpentCents: number
  points: number
  currentPoints: number
  lifetimePoints: number
  rewardRedemptionsCount: number
  segment: "vip" | "recurring" | "new"
  segmentLabel: string
  lastOrderAt?: string
}
```

### Reward

```ts
type Reward = {
  id: string
  name: string
  description?: string
  type: "discount_amount" | "discount_percent" | "free_item" | "free_delivery"
  costPoints: number
  discountCents?: number
  discountPercent?: number
  freeMenuItemId?: string
  redemptionLimitPerCustomer?: number
  redemptionsCount: number
  status: "active" | "paused" | "archived"
  statusLabel: string
  severity: Severity
  expiresAt?: string
}
```

### LoyaltyRule

```ts
type LoyaltyRule = {
  id: string
  restaurantId: string
  pointsPerReal: number
  minOrderCents: number
  isActive: boolean
  label: string
}
```

### LoyaltyBalance

```ts
type LoyaltyBalance = {
  restaurantId: string
  customerId: string
  currentPoints: number
  lifetimePoints: number
  activeRuleLabel: string
}
```

### LoyaltyTransaction

```ts
type LoyaltyTransaction = {
  id: string
  restaurantId: string
  customerId: string
  type: "earn" | "redeem" | "manual_adjustment" | "reversal"
  points: number
  balanceAfter: number
  orderId?: string
  rewardRedemptionId?: string
  description: string
  createdAt: string
}
```

### RewardRedemption

```ts
type RewardRedemption = {
  id: string
  restaurantId: string
  customerId: string
  rewardId: string
  rewardName: string
  costPoints: number
  status: "issued" | "used" | "expired" | "cancelled"
  code: string
  orderId?: string
  expiresAt?: string
  createdAt: string
  usedAt?: string
}
```

### CopilotInsight

```ts
type CopilotInsight = {
  id: string
  title: string
  text: string
  severity: Severity
  source?: string
}
```

## Ordem pratica de implementacao

1. Autenticacao de gerente e cliente, `GET /me`, `GET /customer/me` e `GET /restaurants/{restaurantId}`.
2. Clientes, regra de fidelidade, saldo de pontos e ledger de transacoes.
3. Recompensas: CRUD do restaurante, listagem para cliente e resgate transacional.
4. Pedidos: listar, criar, atualizar status e creditar pontos automaticamente ao finalizar.
5. Importacao de `orders.csv` e `rewards_catalog.csv`.
6. Ranking top 5 de clientes por pontos acumulados e historico de ganhos/resgates.
7. Dashboard agregado, cardapio, financeiro, entregas e mapa.
8. Copilot/IA para recomendacoes de fidelidade, desempenho e ajuda.
9. SSE em `/events` para atualizacoes em tempo real.

## Observacoes para integrar no frontend depois

- Substituir imports de `../data/mock` por composables ou stores que chamem a API.
- Manter `formatBRL` no frontend ou receber `formattedValue` do backend; preferivel manter os centavos como fonte da verdade.
- Os filtros ja existem visualmente, mas ainda nao tem estado reativo nem chamadas.
- Botoes hoje sem acao real que precisam de backend: `Exportar`, `Atualizar fila`, `Novo item`, `Ver mapa`, `Enviar campanha`, `Ajustar regra`, `Nova recompensa`, `Gerar plano`, `Abrir chamado`.
- Para a area de cliente, adicionar telas ou componentes para cadastro/login, saldo atual, catalogo de recompensas, acao de resgate e historico.
- Links nas tabelas (`href="#"`) devem apontar para telas/detalhes ou abrir modais consumindo os endpoints de detalhe.
