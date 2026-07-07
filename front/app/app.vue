<script setup lang="ts">
useHead({
  titleTemplate: (title) => title ? `${title} | iFood Copilot` : 'iFood Copilot',
  meta: [
    {
      name: 'description',
      content: 'Painel administrativo mockado para restaurante acompanhar pedidos, faturamento, cardápio, entregas e clientes.'
    }
  ]
})

const route = useRoute()

const menuItems = [
  { label: 'Início', icon: 'lucide:home', to: '/' },
  { label: 'Dashboard', icon: 'lucide:layout-dashboard', to: '/dashboard' },
  { label: 'Pedidos', icon: 'lucide:receipt-text', to: '/orders' },
  { label: 'Financeiro', icon: 'lucide:dollar-sign', to: '/finance' },
  { label: 'Cardápio', icon: 'lucide:book-open', to: '/menu' },
  { label: 'Entregas', icon: 'lucide:bike', to: '/deliveries' },
  { label: 'Clientes', icon: 'lucide:users', to: '/customers' },
  { label: 'Fidelidade', icon: 'lucide:badge-check', to: '/loyalty' },
  { label: 'Recompensas', icon: 'lucide:gift', to: '/rewards' },
  { label: 'Copilot', icon: 'lucide:sparkles', to: '/copilot' },
  { label: 'Desempenho', icon: 'lucide:trending-up', to: '/performance' },
  { label: 'Ajuda', icon: 'lucide:circle-help', to: '/help' }
]

function isActive(path: string) {
  if (path === '/') {
    return route.path === '/'
  }

  return route.path === path || route.path.startsWith(`${path}/`)
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
        <NuxtLink
          v-for="item in menuItems"
          :key="item.to"
          :to="item.to"
          class="menu-link"
          :class="{ active: isActive(item.to) }"
          :aria-current="isActive(item.to) ? 'page' : undefined"
        >
          <Icon :name="item.icon" aria-hidden="true" />
          <span>{{ item.label }}</span>
        </NuxtLink>
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
      <NuxtPage />
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
select,
textarea {
  font: inherit;
}

button {
  cursor: pointer;
}

a {
  color: var(--color-red);
  text-decoration: none;
}

h1,
h2,
h3,
p {
  margin: 0;
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
  letter-spacing: 0;
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

h1 {
  font-size: clamp(32px, 4vw, 44px);
  line-height: 1.08;
  letter-spacing: 0;
}

.page-header p,
.panel-header p,
.muted {
  margin-top: 8px;
  color: var(--color-gray-500);
}

.primary-button,
.secondary-button {
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 0 18px;
  border-radius: 6px;
  font-weight: 700;
}

.primary-button {
  border: 0;
  background: var(--color-red);
  color: #ffffff;
}

.primary-button:hover {
  background: var(--color-red-dark);
}

.secondary-button {
  border: 1px solid var(--color-gray-300);
  background: #ffffff;
  color: var(--color-gray-900);
}

.primary-button svg,
.secondary-button svg {
  width: 18px;
  height: 18px;
}

.filters {
  display: grid;
  grid-template-columns: repeat(3, minmax(180px, 1fr)) auto;
  gap: 16px;
  align-items: end;
  margin-bottom: 24px;
  padding: 20px;
  border: 1px solid var(--color-gray-200);
  border-radius: 8px;
  background: var(--color-gray-25);
}

.filters label,
.form-field {
  display: grid;
  gap: 8px;
}

.filters span,
.form-field span {
  color: var(--color-gray-700);
  font-size: 13px;
  font-weight: 700;
}

.filters input,
.filters select,
.form-field input,
.form-field select,
.form-field textarea {
  width: 100%;
  min-height: 44px;
  padding: 0 12px;
  border: 1px solid var(--color-gray-300);
  border-radius: 6px;
  background: #ffffff;
  color: var(--color-gray-900);
}

.form-field textarea {
  min-height: 104px;
  padding: 12px;
  resize: vertical;
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
.insight-card,
.summary-card,
.home-card {
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

.danger {
  color: var(--color-red);
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

.charts-grid,
.two-column-grid,
.cards-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.cards-grid.three {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.panel,
.summary-card,
.home-card {
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

.bar-list,
.stack-list {
  display: grid;
  gap: 18px;
}

.bar-row {
  display: grid;
  gap: 8px;
}

.bar-row > div:first-child,
.summary-line,
.reward-foot {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  color: var(--color-gray-700);
  font-size: 14px;
}

.bar-row strong,
.summary-line strong {
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

.delivery .bar-track span,
.orange-bar .bar-track span {
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

.home-hero {
  min-height: 420px;
  display: grid;
  align-content: center;
  gap: 28px;
  padding: 48px;
  border: 1px solid var(--color-gray-200);
  border-radius: 8px;
  background: linear-gradient(135deg, #ffffff 0%, #fff4f5 100%);
}

.home-hero h1 {
  max-width: 680px;
  font-size: clamp(42px, 6vw, 72px);
}

.home-hero p {
  max-width: 620px;
  color: var(--color-gray-700);
  font-size: 18px;
  line-height: 1.6;
}

.home-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.summary-card h3,
.home-card h3 {
  margin-bottom: 10px;
  font-size: 18px;
}

.summary-card p,
.home-card p {
  color: var(--color-gray-500);
  line-height: 1.5;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
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
  .charts-grid,
  .two-column-grid,
  .cards-grid,
  .cards-grid.three {
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

  .page-header .primary-button,
  .home-actions .primary-button,
  .home-actions .secondary-button {
    width: 100%;
  }

  .metrics-grid,
  .form-grid {
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

  .panel,
  .summary-card,
  .home-card,
  .home-hero {
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
