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
  kind?: 'historical' | 'current' | 'forecast'
  isForecast?: boolean
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
  revenueByDay.value = fallbackRevenueByDay.map((item) => ({
    ...item,
    kind: 'historical',
    isForecast: false
  }))
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

async function fetchDashboard() {
  if (!auth.restaurant.value?.id || !auth.token.value) {
    applyFallbackDashboard('Sessao do restaurante indisponivel. Exibindo mock.')
    pending.value = false
    return
  }

  pending.value = true
  usingFallback.value = false
  errorMessage.value = ''

  try {
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
    revenueByDay.value = payload.revenueByDay.map((item) => ({
      label: item.label,
      value: item.value,
      kind: item.kind,
      isForecast: item.isForecast
    }))
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
            v-for="item in revenueByDay"
            :key="item.label"
            class="column-item"
          >
            <div class="column-track">
              <span
                :class="[
                  'column-bar',
                  item.kind === 'forecast' ? 'forecast-bar' : '',
                  item.kind === 'current' ? 'current-bar' : ''
                ]"
                :style="{ height: chartHeight(item.value, revenueByDay) }"
              />
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
