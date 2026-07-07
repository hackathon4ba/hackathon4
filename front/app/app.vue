<script setup lang="ts">
useHead({
  title: 'Visão geral | iFood Copilot',
  meta: [
    {
      name: 'description',
      content: 'Dashboard administrativo para restaurante acompanhar pedidos, faturamento, entregas e insights.'
    }
  ]
})

const menuItems = [
  { label: 'Início', icon: 'lucide:home' },
  { label: 'Dashboard', icon: 'lucide:layout-dashboard', active: true },
  { label: 'Pedidos', icon: 'lucide:receipt-text' },
  { label: 'Financeiro', icon: 'lucide:dollar-sign' },
  { label: 'Cardápio', icon: 'lucide:book-open' },
  { label: 'Entregas', icon: 'lucide:bike' },
  { label: 'Clientes', icon: 'lucide:users' },
  { label: 'Fidelidade', icon: 'lucide:badge-check' },
  { label: 'Recompensas', icon: 'lucide:gift' },
  { label: 'Copilot', icon: 'lucide:sparkles' },
  { label: 'Desempenho', icon: 'lucide:trending-up' },
  { label: 'Ajuda', icon: 'lucide:circle-help' }
]

const metrics = [
  { label: 'Pedidos hoje', value: '128', detail: '+12% vs. ontem', tone: 'positive' },
  { label: 'Faturamento hoje', value: 'R$ 5.842', detail: '+8,4% no período', tone: 'positive' },
  { label: 'Ticket médio', value: 'R$ 45,64', detail: 'Meta: R$ 48,00', tone: 'neutral' },
  { label: 'Prato mais vendido', value: 'Parmegiana', detail: '34 pedidos hoje', tone: 'neutral' },
  { label: 'Tempo médio de entrega', value: '31 min', detail: '2 min acima da meta', tone: 'warning' },
  { label: 'Avaliação média', value: '4,7', detail: '92 avaliações', tone: 'positive' }
]

const revenueByDay = [
  { label: 'Seg', value: 3600 },
  { label: 'Ter', value: 4200 },
  { label: 'Qua', value: 3880 },
  { label: 'Qui', value: 5100 },
  { label: 'Sex', value: 5842 },
  { label: 'Sáb', value: 6900 },
  { label: 'Dom', value: 5480 }
]

const ordersByPeriod = [
  { label: 'Manhã', value: 22 },
  { label: 'Almoço', value: 48 },
  { label: 'Tarde', value: 18 },
  { label: 'Jantar', value: 40 }
]

const bestDishes = [
  { label: 'Parmegiana', value: 34 },
  { label: 'Burger da Casa', value: 28 },
  { label: 'Strogonoff', value: 22 },
  { label: 'Marmita Fit', value: 19 }
]

const deliveryByNeighborhood = [
  { label: 'Centro', value: 27 },
  { label: 'Jardins', value: 31 },
  { label: 'Vila Nova', value: 36 },
  { label: 'Pinheiros', value: 29 }
]

const recentOrders = [
  { id: '#8421', customer: 'Ana Paula', dish: 'Parmegiana', value: 'R$ 54,90', status: 'Entregue', badge: 'green' },
  { id: '#8420', customer: 'Rafael Lima', dish: 'Burger da Casa', value: 'R$ 42,50', status: 'Em preparo', badge: 'orange' },
  { id: '#8419', customer: 'Carla Souza', dish: 'Strogonoff', value: 'R$ 39,90', status: 'Saiu para entrega', badge: 'green' },
  { id: '#8418', customer: 'João Pedro', dish: 'Marmita Fit', value: 'R$ 32,00', status: 'Atrasado', badge: 'red' },
  { id: '#8417', customer: 'Marina Alves', dish: 'Parmegiana', value: 'R$ 54,90', status: 'Entregue', badge: 'green' }
]

function chartHeight(value: number, data: Array<{ value: number }>) {
  const max = Math.max(...data.map((item) => item.value))
  return `${Math.max((value / max) * 100, 8)}%`
}

function chartWidth(value: number, data: Array<{ value: number }>) {
  const max = Math.max(...data.map((item) => item.value))
  return `${Math.max((value / max) * 100, 8)}%`
}
</script>

<template>
  <div class="app-shell">
    <NuxtRouteAnnouncer />

    <aside class="sidebar" aria-label="Navegação principal">
      <div class="brand">
        <div class="brand-mark">if</div>
        <div>
          <strong>iFood Copilot</strong>
          <span>Meu Restaurante</span>
        </div>
      </div>

      <div class="store-status">
        <Icon name="lucide:check-circle-2" aria-hidden="true" />
        <div>
          <strong>Loja aberta</strong>
          <span>Dentro do horário programado</span>
        </div>
      </div>

      <nav class="menu">
        <a
          v-for="item in menuItems"
          :key="item.label"
          href="#"
          class="menu-link"
          :class="{ active: item.active }"
        >
          <Icon :name="item.icon" aria-hidden="true" />
          <span>{{ item.label }}</span>
        </a>
      </nav>

      <div class="sidebar-user">
        <Icon name="lucide:user-round" aria-hidden="true" />
        <div>
          <strong>gerente@restaurante.com</strong>
          <span>Usuário logado</span>
        </div>
      </div>
    </aside>

    <main class="main-content">
      <header class="page-header">
        <div>
          <span class="eyebrow">Painel do restaurante</span>
          <h1>Visão geral</h1>
          <p>Resumo de vendas, pedidos e operação do Restaurante Sabor da Casa.</p>
        </div>

        <button class="primary-button" type="button">
          <Icon name="lucide:download" aria-hidden="true" />
          Exportar
        </button>
      </header>

      <section class="filters" aria-label="Filtros do dashboard">
        <label>
          <span>Período</span>
          <select>
            <option>Hoje</option>
            <option>Últimos 7 dias</option>
            <option>Últimos 30 dias</option>
          </select>
        </label>

        <label>
          <span>Data inicial</span>
          <input type="date" value="2026-07-07">
        </label>

        <label>
          <span>Data final</span>
          <input type="date" value="2026-07-07">
        </label>

        <button class="primary-button filter-button" type="button">
          <Icon name="lucide:search" aria-hidden="true" />
          Consultar
        </button>
      </section>

      <section class="metrics-grid" aria-label="Indicadores principais">
        <article
          v-for="metric in metrics"
          :key="metric.label"
          class="metric-card"
        >
          <span>{{ metric.label }}</span>
          <strong>{{ metric.value }}</strong>
          <small :class="metric.tone">{{ metric.detail }}</small>
        </article>
      </section>

      <section class="insight-card">
        <div class="insight-icon">
          <Icon name="lucide:sparkles" aria-hidden="true" />
        </div>
        <div>
          <span>Insight do Copilot</span>
          <strong>Seu pico de pedidos acontece no jantar. Reforce a operação entre 19h e 21h.</strong>
        </div>
      </section>

      <section class="charts-grid" aria-label="Gráficos do dashboard">
        <article class="panel">
          <div class="panel-header">
            <div>
              <h2>Faturamento por dia</h2>
              <p>Receita bruta dos últimos dias</p>
            </div>
            <a href="#">Ver detalhes</a>
          </div>

          <div class="column-chart">
            <div
              v-for="item in revenueByDay"
              :key="item.label"
              class="column-item"
            >
              <div class="column-track">
                <span :style="{ height: chartHeight(item.value, revenueByDay) }" />
              </div>
              <small>{{ item.label }}</small>
            </div>
          </div>
        </article>

        <article class="panel">
          <div class="panel-header">
            <div>
              <h2>Pedidos por período</h2>
              <p>Distribuição por faixa do dia</p>
            </div>
          </div>

          <div class="bar-list">
            <div
              v-for="item in ordersByPeriod"
              :key="item.label"
              class="bar-row"
            >
              <div>
                <span>{{ item.label }}</span>
                <strong>{{ item.value }} pedidos</strong>
              </div>
              <div class="bar-track">
                <span :style="{ width: chartWidth(item.value, ordersByPeriod) }" />
              </div>
            </div>
          </div>
        </article>

        <article class="panel">
          <div class="panel-header">
            <div>
              <h2>Pratos mais vendidos</h2>
              <p>Itens com maior saída</p>
            </div>
          </div>

          <div class="bar-list">
            <div
              v-for="item in bestDishes"
              :key="item.label"
              class="bar-row"
            >
              <div>
                <span>{{ item.label }}</span>
                <strong>{{ item.value }} vendas</strong>
              </div>
              <div class="bar-track">
                <span :style="{ width: chartWidth(item.value, bestDishes) }" />
              </div>
            </div>
          </div>
        </article>

        <article class="panel">
          <div class="panel-header">
            <div>
              <h2>Tempo médio por bairro</h2>
              <p>Entrega em minutos</p>
            </div>
          </div>

          <div class="bar-list">
            <div
              v-for="item in deliveryByNeighborhood"
              :key="item.label"
              class="bar-row delivery"
            >
              <div>
                <span>{{ item.label }}</span>
                <strong>{{ item.value }} min</strong>
              </div>
              <div class="bar-track">
                <span :style="{ width: chartWidth(item.value, deliveryByNeighborhood) }" />
              </div>
            </div>
          </div>
        </article>
      </section>

      <section class="panel table-panel">
        <div class="panel-header">
          <div>
            <h2>Resumo de pedidos recentes</h2>
            <p>Últimas movimentações da operação</p>
          </div>
          <a href="#">Abrir pedidos</a>
        </div>

        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Pedido</th>
                <th>Cliente</th>
                <th>Prato</th>
                <th>Valor</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="order in recentOrders"
                :key="order.id"
              >
                <td>
                  <a href="#">{{ order.id }}</a>
                </td>
                <td>{{ order.customer }}</td>
                <td>{{ order.dish }}</td>
                <td>{{ order.value }}</td>
                <td>
                  <span class="status-badge" :class="order.badge">{{ order.status }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </main>
  </div>
</template>

<style>
:root {
  --color-red: #ea1d2c;
  --color-red-dark: #c91623;
  --color-green: #3aa76d;
  --color-orange: #f59e0b;
  --color-gray-25: #fbfbfb;
  --color-gray-50: #f7f7f7;
  --color-gray-100: #f1f1f1;
  --color-gray-200: #e5e5e5;
  --color-gray-300: #d4d4d4;
  --color-gray-500: #737373;
  --color-gray-700: #404040;
  --color-gray-900: #171717;
  --shadow-soft: 0 10px 28px rgb(23 23 23 / 8%);
}

* {
  box-sizing: border-box;
}

html {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: #ffffff;
  color: var(--color-gray-900);
}

body {
  margin: 0;
}

button,
input,
select {
  font: inherit;
}

a {
  color: var(--color-red);
  text-decoration: none;
}

.app-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 268px minmax(0, 1fr);
  background: #ffffff;
}

.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  display: flex;
  flex-direction: column;
  gap: 22px;
  padding: 24px 16px;
  background: var(--color-gray-100);
  border-right: 1px solid var(--color-gray-200);
  overflow-y: auto;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 10px;
}

.brand-mark {
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  border-radius: 8px;
  background: var(--color-red);
  color: #ffffff;
  font-size: 18px;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.brand strong,
.sidebar-user strong {
  display: block;
  font-size: 14px;
  color: var(--color-gray-900);
}

.brand span,
.store-status span,
.sidebar-user span {
  display: block;
  margin-top: 2px;
  font-size: 12px;
  color: var(--color-gray-500);
}

.store-status {
  display: flex;
  gap: 10px;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  background: #ffffff;
  border: 1px solid var(--color-gray-200);
}

.store-status svg {
  width: 20px;
  height: 20px;
  color: var(--color-green);
  flex: 0 0 auto;
}

.store-status strong {
  display: block;
  font-size: 13px;
  color: var(--color-green);
}

.menu {
  display: grid;
  gap: 4px;
}

.menu-link {
  min-height: 40px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 6px;
  color: var(--color-gray-700);
  font-size: 14px;
  font-weight: 600;
}

.menu-link svg {
  width: 18px;
  height: 18px;
}

.menu-link.active {
  color: var(--color-red);
  background: #ffffff;
  box-shadow: inset 3px 0 0 var(--color-red);
}

.sidebar-user {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: auto;
  padding: 14px 10px 0;
  border-top: 1px solid var(--color-gray-200);
}

.sidebar-user svg {
  width: 18px;
  height: 18px;
  color: var(--color-gray-500);
  flex: 0 0 auto;
}

.main-content {
  width: 100%;
  max-width: 1240px;
  padding: 40px 48px 56px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
  margin-bottom: 28px;
}

.eyebrow {
  display: block;
  margin-bottom: 8px;
  color: var(--color-red);
  font-size: 13px;
  font-weight: 700;
}

h1,
h2,
p {
  margin: 0;
}

h1 {
  font-size: clamp(32px, 4vw, 44px);
  line-height: 1.08;
  letter-spacing: 0;
}

.page-header p,
.panel-header p {
  margin-top: 8px;
  color: var(--color-gray-500);
}

.primary-button {
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 0 18px;
  border: 0;
  border-radius: 6px;
  background: var(--color-red);
  color: #ffffff;
  font-weight: 700;
  cursor: pointer;
}

.primary-button:hover {
  background: var(--color-red-dark);
}

.primary-button svg {
  width: 18px;
  height: 18px;
}

.filters {
  display: grid;
  grid-template-columns: minmax(180px, 1fr) minmax(180px, 1fr) minmax(180px, 1fr) auto;
  gap: 16px;
  align-items: end;
  margin-bottom: 24px;
  padding: 20px;
  border: 1px solid var(--color-gray-200);
  border-radius: 8px;
  background: var(--color-gray-25);
}

.filters label {
  display: grid;
  gap: 8px;
}

.filters span {
  color: var(--color-gray-700);
  font-size: 13px;
  font-weight: 700;
}

.filters input,
.filters select {
  width: 100%;
  min-height: 44px;
  padding: 0 12px;
  border: 1px solid var(--color-gray-300);
  border-radius: 6px;
  background: #ffffff;
  color: var(--color-gray-900);
}

.filter-button {
  min-width: 132px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 18px;
}

.metric-card,
.panel,
.insight-card {
  border: 1px solid var(--color-gray-200);
  border-radius: 8px;
  background: #ffffff;
}

.metric-card {
  min-height: 132px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 18px;
}

.metric-card span {
  color: var(--color-gray-500);
  font-size: 13px;
  font-weight: 700;
}

.metric-card strong {
  margin-top: 14px;
  color: var(--color-gray-900);
  font-size: 26px;
  line-height: 1.1;
}

.metric-card small {
  margin-top: 12px;
  font-size: 12px;
  font-weight: 700;
}

.positive {
  color: var(--color-green);
}

.neutral {
  color: var(--color-gray-500);
}

.warning {
  color: var(--color-orange);
}

.insight-card {
  display: flex;
  gap: 16px;
  align-items: center;
  margin-bottom: 24px;
  padding: 18px 20px;
  background: #fff7f7;
  border-color: #ffd5d8;
}

.insight-icon {
  width: 44px;
  height: 44px;
  display: grid;
  place-items: center;
  border-radius: 8px;
  background: var(--color-red);
  color: #ffffff;
  flex: 0 0 auto;
}

.insight-card span {
  display: block;
  margin-bottom: 4px;
  color: var(--color-red);
  font-size: 13px;
  font-weight: 800;
}

.insight-card strong {
  color: var(--color-gray-900);
  font-size: 16px;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.panel {
  padding: 22px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 22px;
}

.panel-header h2 {
  font-size: 20px;
  line-height: 1.2;
}

.panel-header a {
  font-size: 13px;
  font-weight: 800;
  white-space: nowrap;
}

.column-chart {
  height: 240px;
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 14px;
  align-items: end;
}

.column-item {
  height: 100%;
  display: grid;
  grid-template-rows: 1fr auto;
  gap: 10px;
  text-align: center;
}

.column-track {
  height: 100%;
  display: flex;
  align-items: end;
  border-radius: 6px;
  background: var(--color-gray-100);
  overflow: hidden;
}

.column-track span {
  width: 100%;
  display: block;
  border-radius: 6px 6px 0 0;
  background: linear-gradient(180deg, #ff6470, var(--color-red));
}

.column-item small {
  color: var(--color-gray-500);
  font-weight: 700;
}

.bar-list {
  display: grid;
  gap: 18px;
}

.bar-row {
  display: grid;
  gap: 8px;
}

.bar-row > div:first-child {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  color: var(--color-gray-700);
  font-size: 14px;
}

.bar-row strong {
  color: var(--color-gray-900);
}

.bar-track {
  height: 10px;
  border-radius: 999px;
  background: var(--color-gray-100);
  overflow: hidden;
}

.bar-track span {
  height: 100%;
  display: block;
  border-radius: inherit;
  background: var(--color-red);
}

.delivery .bar-track span {
  background: var(--color-orange);
}

.table-panel {
  padding-bottom: 8px;
}

.table-wrap {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 760px;
}

th,
td {
  padding: 18px 14px;
  border-top: 1px solid var(--color-gray-200);
  text-align: left;
  font-size: 14px;
}

th {
  color: var(--color-gray-500);
  font-size: 12px;
  text-transform: uppercase;
}

td {
  color: var(--color-gray-700);
}

td a {
  font-weight: 800;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  border: 1px solid currentColor;
  font-size: 12px;
  font-weight: 800;
}

.status-badge.green {
  color: var(--color-green);
  background: #f0faf4;
}

.status-badge.orange {
  color: #d97706;
  background: #fff7ed;
}

.status-badge.red {
  color: var(--color-red);
  background: #fff7f7;
}

@media (max-width: 1180px) {
  .metrics-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 980px) {
  .app-shell {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: static;
    height: auto;
    padding: 16px;
  }

  .menu {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }

  .menu-link {
    justify-content: center;
  }

  .menu-link span {
    display: none;
  }

  .sidebar-user {
    display: none;
  }

  .main-content {
    padding: 28px 20px 40px;
  }

  .filters,
  .charts-grid {
    grid-template-columns: 1fr;
  }

  .filter-button {
    width: 100%;
  }
}

@media (max-width: 680px) {
  .page-header {
    flex-direction: column;
  }

  .page-header .primary-button {
    width: 100%;
  }

  .metrics-grid {
    grid-template-columns: 1fr;
  }

  .brand,
  .store-status {
    padding-left: 0;
    padding-right: 0;
  }

  .menu {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .panel {
    padding: 18px;
  }

  .panel-header {
    flex-direction: column;
  }

  .column-chart {
    height: 190px;
    gap: 8px;
  }
}
</style>
