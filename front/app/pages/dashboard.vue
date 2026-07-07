<script setup lang="ts">
import {
  bestDishes,
  chartHeight,
  chartWidth,
  deliveryByNeighborhood,
  formatBRL,
  metrics,
  ordersByPeriod,
  recentOrders,
  revenueByDay
} from '../data/mock'

useHead({ title: 'Visão geral' })
</script>

<template>
  <div>
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
          <NuxtLink to="/finance">Ver detalhes</NuxtLink>
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
        <NuxtLink to="/orders">Abrir pedidos</NuxtLink>
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
              <td><a href="#">{{ order.id }}</a></td>
              <td>{{ order.customer }}</td>
              <td>{{ order.dish }}</td>
              <td>{{ formatBRL(order.value) }}</td>
              <td>
                <span class="status-badge" :class="order.badge">{{ order.status }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>
