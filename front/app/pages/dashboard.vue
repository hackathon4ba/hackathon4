<script setup lang="ts">
import { bestDishes as fallbackBestDishes, chartHeight, chartWidth, formatBRL, metrics as fallbackMetrics, ordersByPeriod as fallbackOrdersByPeriod, revenueByDay as fallbackRevenueByDay } from '../data/mock'

useHead({ title: 'Visao geral' })

type MetricTone = 'positive' | 'neutral' | 'warning' | 'danger'

type DashboardMetric = {
  label: string
  value: string
  detail: string
  tone: MetricTone
}

type ChartDatum = {
  label: string
  value: number
  date?: string
  kind?: 'historical' | 'current' | 'forecast'
  isForecast?: boolean
  topDishLabel?: string
  topDishOrders?: number
}

type DashboardInsight = {
  title: string
  text: string
  severity: string
  confidence: number
}

type DashboardPayload = {
  restaurantId: number
  referenceDate: string
  totalOrdersToday: number
  revenueToday: number
  revenueTodayCents: number
  topDishToday: {
    name: string
    orders: number
  }
  revenueByDay: Array<{
    date: string
    label: string
    value: number
    valueCents: number
    kind?: 'historical' | 'current' | 'forecast'
    isForecast?: boolean
  }>
  ordersByPeriod: Array<{
    period: string
    label: string
    value: number
  }>
  bestDishes: Array<{
    label: string
    value: number
  }>
  aiInsight: DashboardInsight
}

const config = useRuntimeConfig()
const auth = useRestaurantAuth()

const pending = ref(true)
const usingFallback = ref(false)
const errorMessage = ref('')
const referenceDate = ref('')
const hoveredRevenueIndex = ref<number | null>(null)

const filters = reactive({
  period: 'last_7_days',
  startDate: '',
  endDate: ''
})

const metrics = ref<DashboardMetric[]>([])
const revenueByDay = ref<ChartDatum[]>([])
const ordersByPeriod = ref<ChartDatum[]>([])
const bestDishes = ref<ChartDatum[]>([])
const insight = ref<DashboardInsight>({
  title: '',
  text: '',
  severity: 'neutral',
  confidence: 0
})

function getFallbackTopDish(index = 0) {
  const fallbackDish = fallbackBestDishes[index % fallbackBestDishes.length]
  return {
    label: fallbackDish?.label ?? 'Sem destaque',
    orders: fallbackDish?.value ?? 0
  }
}

function buildRevenueDetails(
  items: Array<{
    date?: string
    label: string
    value: number
    kind?: 'historical' | 'current' | 'forecast'
    isForecast?: boolean
  }>,
  topDishes: Array<{ label: string, value: number }>,
  topDishToday?: { name: string, orders: number }
) {
  return items.map((item, index) => {
    const rankedDish = topDishes[index % topDishes.length]
    const fallbackDish = getFallbackTopDish(index)
    const selectedDish = rankedDish
      ? { label: rankedDish.label, orders: rankedDish.value }
      : topDishToday
        ? { label: topDishToday.name, orders: topDishToday.orders }
        : fallbackDish

    return {
      label: item.label,
      value: item.value,
      date: item.date,
      kind: item.kind,
      isForecast: item.isForecast,
      topDishLabel: selectedDish.label,
      topDishOrders: selectedDish.orders
    }
  })
}

function formatRevenueDate(item: ChartDatum) {
  if (!item.date) {
    return item.label
  }

  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: '2-digit'
  }).format(new Date(`${item.date}T00:00:00`))
}

function setHoveredRevenue(index: number | null) {
  hoveredRevenueIndex.value = index
}

function formatPeriodLabel(period: string) {
  if (period === 'today') {
    return 'Hoje'
  }
  if (period === 'last_30_days') {
    return 'Ultimos 30 dias'
  }
  return 'Ultimos 7 dias'
}

function applyFallbackDashboard(message = 'API indisponivel. Exibindo dados mockados para a demo.') {
  usingFallback.value = true
  errorMessage.value = message
  referenceDate.value = 'mock'
  metrics.value = fallbackMetrics.slice(0, 4)
  revenueByDay.value = buildRevenueDetails(
    fallbackRevenueByDay.map((item) => ({
      ...item,
      kind: 'historical',
      isForecast: false
    })),
    fallbackBestDishes
  )
  ordersByPeriod.value = fallbackOrdersByPeriod
  bestDishes.value = fallbackBestDishes
  insight.value = {
    title: 'Insight do Copilot',
    text: 'Seu pico de pedidos acontece no jantar. Reforce a operacao entre 19h e 21h.',
    severity: 'green',
    confidence: 0.76
  }
}

function buildMetrics(payload: DashboardPayload): DashboardMetric[] {
  return [
    {
      label: 'Pedidos do dia',
      value: String(payload.totalOrdersToday),
      detail: `Baseado em ${payload.referenceDate}`,
      tone: 'positive'
    },
    {
      label: 'Faturamento do dia',
      value: formatBRL(payload.revenueToday),
      detail: `Recorte ${formatPeriodLabel(filters.period)}`,
      tone: 'positive'
    },
    {
      label: 'Prato mais pedido',
      value: payload.topDishToday.name,
      detail: `${payload.topDishToday.orders} pedidos no dia`,
      tone: 'neutral'
    },
    {
      label: 'Confianca da IA',
      value: `${Math.round(payload.aiInsight.confidence * 100)}%`,
      detail: payload.aiInsight.title,
      tone: payload.aiInsight.severity === 'red' ? 'warning' : 'positive'
    }
  ]
}

function getRequestErrorMessage(error: unknown, fallback: string) {
  if (error && typeof error === 'object' && 'data' in error) {
    const message = (error as { data?: { msg?: string } }).data?.msg
    if (message) {
      return message
    }
  }

  if (error instanceof Error && error.message) {
    return error.message
  }

  return fallback
}

function getAuthHeaders() {
  return {
    Authorization: `Bearer ${auth.token.value}`
  }
}

async function ensureRestaurantSession() {
  if (!auth.token.value) {
    return false
  }

  if (auth.restaurant.value?.id) {
    return true
  }

  let profile = await auth.fetchProfile()
  if (!profile?.id) {
    await new Promise((resolve) => setTimeout(resolve, 250))
    profile = await auth.fetchProfile()
  }

  return Boolean(profile?.id)
}

async function fetchDashboard() {
  if (!auth.token.value) {
    applyFallbackDashboard('Sessao do restaurante indisponivel. Exibindo mock.')
    pending.value = false
    return
  }

  pending.value = true
  usingFallback.value = false
  errorMessage.value = ''
  hoveredRevenueIndex.value = null

  try {
    const hasRestaurantSession = await ensureRestaurantSession()
    if (!hasRestaurantSession || !auth.restaurant.value?.id) {
      applyFallbackDashboard('Nao foi possivel confirmar a sessao do restaurante. Exibindo mock.')
      return
    }

    const query: Record<string, string> = {
      period: filters.period
    }

    if (filters.startDate && filters.endDate) {
      query.startDate = filters.startDate
      query.endDate = filters.endDate
    }

    const payload = await $fetch<DashboardPayload>(
      `/api/v1/restaurants/${auth.restaurant.value.id}/dashboard`,
      {
        baseURL: config.public.apiBase,
        headers: getAuthHeaders(),
        query
      }
    )

    referenceDate.value = payload.referenceDate
    metrics.value = buildMetrics(payload)
    revenueByDay.value = buildRevenueDetails(
      payload.revenueByDay,
      payload.bestDishes,
      payload.topDishToday
    )
    ordersByPeriod.value = payload.ordersByPeriod.map((item) => ({
      label: item.label,
      value: item.value
    }))
    bestDishes.value = payload.bestDishes
    insight.value = payload.aiInsight
  } catch (error) {
    applyFallbackDashboard(getRequestErrorMessage(error, 'API indisponivel. Exibindo dados mockados para a demo.'))
  } finally {
    pending.value = false
  }
}

await auth.initialize()
await fetchDashboard()
</script>

<template>
  <div>
    <header class="page-header">
      <div>
        <span class="eyebrow">Painel do restaurante</span>
        <h1>Visao geral</h1>
        <p>Resumo real da operacao e insight gerado a partir do dataset do notebook.</p>
      </div>

      <button class="primary-button" type="button" :disabled="pending" @click="fetchDashboard">
        <Icon name="lucide:refresh-cw" aria-hidden="true" />
        {{ pending ? 'Carregando...' : 'Atualizar' }}
      </button>
    </header>

    <section class="filters" aria-label="Filtros do dashboard">
      <label>
        <span>Periodo</span>
        <select v-model="filters.period">
          <option value="today">Hoje</option>
          <option value="last_7_days">Ultimos 7 dias</option>
          <option value="last_30_days">Ultimos 30 dias</option>
        </select>
      </label>

      <label>
        <span>Data inicial</span>
        <input v-model="filters.startDate" type="date">
      </label>

      <label>
        <span>Data final</span>
        <input v-model="filters.endDate" type="date">
      </label>

      <button class="primary-button filter-button" type="button" @click="fetchDashboard">
        <Icon name="lucide:search" aria-hidden="true" />
        Consultar
      </button>
    </section>

    <p v-if="usingFallback" class="dashboard-feedback warning-feedback">
      {{ errorMessage }}
    </p>

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
        <span>Insight da IA</span>
        <strong>{{ insight.title }}</strong>
        <p class="dashboard-insight-text">
          {{ insight.text }}
        </p>
        <small class="dashboard-confidence">
          Confianca: {{ Math.round(insight.confidence * 100) }}% • Base {{ referenceDate }}
        </small>
      </div>
    </section>

    <section class="charts-grid" aria-label="Graficos do dashboard">
      <article class="panel">
        <div class="panel-header">
          <div>
            <h2>Faturamento por dia</h2>
            <p>Receita bruta do recorte atual</p>
          </div>
        </div>

        <div class="column-chart">
          <div
            v-for="(item, index) in revenueByDay"
            :key="item.label"
            :class="['column-item', hoveredRevenueIndex === index ? 'column-item-active' : '']"
            @mouseenter="setHoveredRevenue(index)"
            @mouseleave="setHoveredRevenue(null)"
          >
            <div class="column-track">
              <span
                :class="[
                  'column-bar',
                  hoveredRevenueIndex === index ? 'column-bar-active' : '',
                  item.kind === 'forecast' ? 'forecast-bar' : '',
                  item.kind === 'current' ? 'current-bar' : ''
                ]"
                :style="{ height: chartHeight(item.value, revenueByDay) }"
              />

              <div
                v-if="hoveredRevenueIndex === index"
                class="column-tooltip"
                role="status"
              >
                <strong>{{ formatRevenueDate(item) }}</strong>
                <span>Faturamento: {{ formatBRL(item.value) }}</span>
                <span>Produto mais vendido: {{ item.topDishLabel }}</span>
                <span v-if="item.topDishOrders">Pedidos do destaque: {{ item.topDishOrders }}</span>
              </div>
            </div>
            <small>{{ item.label }}</small>
          </div>
        </div>
      </article>

      <article class="panel">
        <div class="panel-header">
          <div>
            <h2>Pedidos por periodo</h2>
            <p>Distribuicao da demanda ao longo do dia</p>
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
    </section>

    <section class="panel">
      <div class="panel-header">
        <div>
          <h2>Pratos com mais pedidos</h2>
          <p>Ranking do recorte selecionado</p>
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
            <strong>{{ item.value }} pedidos</strong>
          </div>
          <div class="bar-track">
            <span :style="{ width: chartWidth(item.value, bestDishes) }" />
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.dashboard-feedback {
  margin-bottom: 18px;
  padding: 14px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 700;
}

.warning-feedback {
  border: 1px solid #fed7aa;
  background: #fff7ed;
  color: #b45309;
}

.dashboard-insight-text {
  margin-top: 8px;
  color: var(--color-gray-700);
}

.dashboard-confidence {
  display: block;
  margin-top: 10px;
  color: var(--color-gray-500);
  font-size: 12px;
  font-weight: 700;
}

.column-bar {
  background: var(--color-red);
  transition:
    transform 0.18s ease,
    filter 0.18s ease,
    box-shadow 0.18s ease;
  transform-origin: center bottom;
}

.column-item {
  position: relative;
}

.column-item-active {
  z-index: 2;
}

.column-track {
  position: relative;
  overflow: visible;
}

.column-bar-active {
  filter: brightness(1.08);
  box-shadow: 0 14px 24px rgba(127, 29, 29, 0.22);
  transform: scale(1.08);
}

.column-tooltip {
  position: absolute;
  left: 50%;
  bottom: calc(100% + 12px);
  transform: translateX(-50%);
  min-width: 188px;
  padding: 12px 14px;
  border: 1px solid rgba(127, 29, 29, 0.12);
  border-radius: 12px;
  background: #fff;
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.14);
  display: grid;
  gap: 4px;
  text-align: left;
  pointer-events: none;
}

.column-tooltip strong {
  color: #7f1d1d;
  font-size: 13px;
}

.column-tooltip span {
  color: var(--color-gray-700);
  font-size: 12px;
  line-height: 1.4;
}

.forecast-bar {
  background: repeating-linear-gradient(
    135deg,
    rgba(214, 62, 62, 0.16) 0,
    rgba(214, 62, 62, 0.16) 6px,
    rgba(214, 62, 62, 0.52) 6px,
    rgba(214, 62, 62, 0.52) 12px
  );
  border: 1px dashed rgba(214, 62, 62, 0.9);
}

.current-bar {
  background: #7f1d1d;
}
</style>
