# Visao Geral da Arquitetura do Sistema

## 1. Resumo Executivo

Este sistema foi desenvolvido para operar a rotina de um restaurante com foco em tres frentes principais:

- operacao comercial, com cardapio, pedidos e autenticacao
- controle interno, com estoque e receitas por prato
- inteligencia operacional, com dashboard, historico de faturamento e IA para previsao

A solucao e dividida em dois componentes centrais:

- `backend/`, responsavel por API, regras de negocio e persistencia
- `front/`, responsavel pela experiencia do usuario e consumo da API

O projeto utiliza SQLite como banco local e uma camada de IA para analise e previsao de faturamento.

## 2. Arquitetura Macro

O fluxo funcional e o seguinte:

1. O restaurante autentica no frontend.
2. O frontend salva token e identidade da sessao.
3. O frontend consulta a API Flask.
4. O backend processa regras de negocio e grava os dados no banco.
5. O dashboard exibe metricas, historico, previsao e insights.

Em termos de desenho tecnico, o sistema segue uma arquitetura de tres camadas:

- apresentacao: Nuxt/Vue
- aplicacao: Flask com controllers e services
- persistencia: SQLAlchemy + SQLite

## 3. Backend

### 3.1 Base Tecnologica

O backend e construido com:

- Flask
- Flask-SQLAlchemy
- Flask-JWT-Extended
- Flask-Migrate / Alembic
- Pydantic
- Spectree para validacao e documentacao da API

O ponto de entrada fica em `backend/main.py`, que instancia a aplicacao a partir de `backend/factory.py`.

### 3.2 Modelos de Dados

Os principais modelos sao:

- `Restaurant`: entidade de conta do restaurante
- `MenuItem`: pratos do cardapio
- `InventoryItem`: itens de estoque
- `MenuItemRecipe`: associacao entre prato e item de estoque
- `Order`: pedidos realizados
- `RevenueDaily`: faturamento diario consolidado

### 3.3 Regras de Negocio

#### Cardapio

Cada prato do cardapio pertence a um restaurante e possui:

- nome
- preco
- lista de ingredientes
- receita de estoque associada

#### Estoque

O sistema controla itens de estoque por restaurante. Cada item possui:

- nome
- unidade
- quantidade disponivel
- quantidade minima de alerta

A receita de um prato informa quanto de cada item sera consumido quando um pedido for efetivado.

#### Pedidos

Ao registrar um pedido, o backend:

- valida se o prato existe no cardapio do restaurante
- valida se existe receita de estoque para o prato
- consome automaticamente os itens de estoque quando necessario
- registra o pedido com status, observacoes e preco

Quando um pedido e alterado ou removido, o estoque e ajustado para manter consistencia.

#### Faturamento Diario

O sistema mantem a tabela `RevenueDaily` para materializar o faturamento por dia. Isso permite:

- historico completo no dashboard
- paginação rapida
- consulta consistente sem reprocessar todos os pedidos a cada requisição

### 3.4 Controllers

Os controllers organizam os endpoints por dominio:

- `auth_controller.py`: login e cadastro
- `restaurant_controller.py`: perfil do restaurante
- `menu_controller.py`: operacoes do cardapio
- `inventory_controller.py`: operacoes de estoque
- `order_controller.py`: pedidos
- `dashboard_controller.py`: dashboard e insights

### 3.5 Services

#### `inventory_service.py`

Gerencia:

- validacao da receita
- consumo de estoque
- restauracao de estoque
- verificacao de disponibilidade

#### `revenue_daily_service.py`

Gerencia:

- sincronizacao do faturamento diario
- recalculo de dias afetados por pedidos
- reconstrucao do historico consolidado

#### `dashboard_ai_service.py`

Gerencia:

- consolidacao dos dados do dashboard
- montagem do grafico de faturamento
- previsao de faturamento
- geracao de insights operacionais

## 4. Inteligencia Artificial

### 4.1 Objetivo

A camada de IA existe para transformar dados operacionais em informacao util para decisao. Ela atua em dois niveis:

- previsao de faturamento
- geracao de insights explicativos

### 4.2 Previsao

A previsao usa uma RNN simples para estimar a evolucao do faturamento.

Parametros principais:

- janela historica: 30 dias
- horizonte previsto: 7 dias

O processo:

1. os pedidos sao agrupados por prato e por data
2. cada prato vira uma serie temporal de receita
3. a RNN aprende o padrao historico
4. a projeção por prato e agregada para formar o faturamento previsto

### 4.3 Insights

Os insights do dashboard usam heuristicas sobre:

- periodo com maior demanda
- taxa de cancelamento
- ticket medio
- volume entregue
- comparacao entre dia atual e previsao

Esses insights ajudam o operador a entender o comportamento do restaurante sem ler tabelas cruas.

## 5. Frontend

### 5.1 Base Tecnologica

O frontend usa:

- Nuxt 3
- Vue 3 com `script setup`
- TypeScript
- composables para autenticacao e acesso a API

### 5.2 Autenticacao

O composable `useRestaurantAuth.ts` centraliza o fluxo de sessao:

- guarda token e identidade do restaurante em cookies
- revalida perfil quando necessario
- expõe login, cadastro, logout e estado autenticado

### 5.3 Paginas Principais

#### `dashboard.vue`

E a tela principal de operacao. Exibe:

- metrica do dia
- grafico de faturamento
- pedidos por periodo
- pratos mais pedidos
- insight da IA
- modal com historico completo do faturamento

O grafico foi desenhado para mostrar:

- 2 dias passados
- dia atual
- 7 dias futuros previstos

Os pontos previstos sao visivelmente diferenciados com transparencia, e o hover continua exibindo detalhes do dia.

#### `orders.vue`

Organiza o cadastro e a edicao de pedidos. O modal de novo pedido:

- usa o cardapio real como fonte de selecao
- permite ir para o cadastro de item quando necessario
- respeita a integracao com estoque

#### `menu.vue`

Permite cadastrar e editar pratos. A definicao de ingredientes usa os itens de estoque disponiveis, o que conecta cardapio e inventario.

#### `inventory.vue`

Tela de gestao dos insumos:

- cadastro de item
- controle de unidade
- quantidade disponivel
- alerta de minimo

## 6. Base de Dados e Seed

O banco principal e `backend/app.db`.

### 6.1 Scripts de populacao

- `populate_database.py`: cria a base inicial e o restaurante admin
- `seed_admin_orders.py`: popula pedidos de exemplo
- `seed_admin_revenue_and_menu.py`: reconstrói cardapio, estoque, receitas, pedidos e faturamento diario

### 6.2 Dataset

O dataset principal de apoio fica em:

- `backend/datasets/deliveries_train.csv`
- `ia/datasets/deliveries_train.csv`

Ele e usado para montar a base de demo e alimentar o comportamento do dashboard.

## 7. Dashboard e Fluxo de Dados

O dashboard usa dados reais do banco com a seguinte logica:

1. busca os pedidos e o faturamento consolidado
2. calcula o periodo selecionado
3. carrega o historico diario da tabela `RevenueDaily`
4. monta a serie do grafico com historico e previsao
5. combina os resultados com insights da IA

O modal de historico completo usa paginação para navegar pelo faturamento dia a dia.

## 8. Padrões de Integracao

### Frontend -> Backend

O frontend envia:

- header `Authorization: Bearer <token>`
- filtros de periodo quando aplicavel

O backend responde com:

- dados normalizados
- metadados de paginação
- indicadores prontos para renderizacao

### Backend -> Banco

As operacoes de escrita acontecem de forma consistente:

- pedidos atualizam estoque e faturamento
- mudanca de pedido recalcula os agregados do dia
- seed recria o estado da demo quando necessario

## 9. Como Executar

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

## 10. Conclusao

O sistema une operacao de restaurante, controle de estoque, acompanhamento de pedidos e dashboard analitico em uma unica plataforma. A maior diferenca em relacao a uma aplicacao comum de CRUD e a presenca de uma camada de IA e de uma base consolidada de faturamento diario, que tornam a dashboard mais rapida, consistente e util para tomada de decisao.

