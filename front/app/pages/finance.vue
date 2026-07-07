<script setup lang="ts">
import { financeRows, revenueByDay, chartHeight } from '../data/mock'

useHead({ title: 'Financeiro' })
</script>

<template>
  <div>
    <header class="page-header">
      <div>
        <span class="eyebrow">Receita e repasses</span>
        <h1>Financeiro</h1>
        <p>Acompanhe faturamento, taxas, cupons e previsão de repasse.</p>
      </div>
      <button class="primary-button" type="button">
        <Icon name="lucide:file-down" aria-hidden="true" />
        Exportar relatório
      </button>
    </header>

    <section class="filters">
      <label><span>Período</span><select><option>Últimos 7 dias</option><option>Hoje</option></select></label>
      <label><span>Data inicial</span><input type="date" value="2026-07-01"></label>
      <label><span>Data final</span><input type="date" value="2026-07-07"></label>
      <button class="primary-button filter-button" type="button">Consultar</button>
    </section>

    <section class="cards-grid">
      <article v-for="row in financeRows" :key="row.label" class="summary-card">
        <h3>{{ row.label }}</h3>
        <p>{{ row.detail }}</p>
        <strong style="display: block; margin-top: 18px; font-size: 28px;">{{ row.value }}</strong>
      </article>
    </section>

    <section class="panel">
      <div class="panel-header">
        <div>
          <h2>Faturamento por dia</h2>
          <p>Evolução mockada da receita bruta.</p>
        </div>
      </div>
      <div class="column-chart">
        <div v-for="item in revenueByDay" :key="item.label" class="column-item">
          <div class="column-track">
            <span :style="{ height: chartHeight(item.value, revenueByDay) }" />
          </div>
          <small>{{ item.label }}</small>
        </div>
      </div>
    </section>
  </div>
</template>
