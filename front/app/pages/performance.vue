<script setup lang="ts">
import { bestDishes, chartWidth, ordersByPeriod } from '../data/mock'

useHead({ title: 'Desempenho' })
</script>

<template>
  <div>
    <header class="page-header">
      <div>
        <span class="eyebrow">Performance</span>
        <h1>Desempenho</h1>
        <p>Conversão, itens vendidos e horários de maior demanda.</p>
      </div>
    </header>

    <section class="metrics-grid">
      <article class="metric-card"><span>Conversão do cardápio</span><strong>18,4%</strong><small class="positive">+3,1 p.p.</small></article>
      <article class="metric-card"><span>Pedidos concluídos</span><strong>96%</strong><small class="positive">Boa operação</small></article>
      <article class="metric-card"><span>Cancelamentos</span><strong>2,1%</strong><small class="warning">Acompanhar</small></article>
    </section>

    <section class="charts-grid">
      <article class="panel">
        <div class="panel-header"><div><h2>Horários de demanda</h2><p>Pedidos por período.</p></div></div>
        <div class="bar-list">
          <div v-for="item in ordersByPeriod" :key="item.label" class="bar-row">
            <div><span>{{ item.label }}</span><strong>{{ item.value }} pedidos</strong></div>
            <div class="bar-track"><span :style="{ width: chartWidth(item.value, ordersByPeriod) }" /></div>
          </div>
        </div>
      </article>
      <article class="panel">
        <div class="panel-header"><div><h2>Itens fortes</h2><p>Ranking de vendas.</p></div></div>
        <div class="bar-list">
          <div v-for="item in bestDishes" :key="item.label" class="bar-row">
            <div><span>{{ item.label }}</span><strong>{{ item.value }} vendas</strong></div>
            <div class="bar-track"><span :style="{ width: chartWidth(item.value, bestDishes) }" /></div>
          </div>
        </div>
      </article>
    </section>
  </div>
</template>
