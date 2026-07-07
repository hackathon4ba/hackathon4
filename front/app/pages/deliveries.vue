<script setup lang="ts">
import { chartWidth, deliveryByNeighborhood, deliveryRows } from '../data/mock'

useHead({ title: 'Entregas' })
</script>

<template>
  <div>
    <header class="page-header">
      <div>
        <span class="eyebrow">Logística</span>
        <h1>Entregas</h1>
        <p>Tempo médio, bairros críticos e status das últimas rotas.</p>
      </div>
      <button class="primary-button" type="button">
        <Icon name="lucide:map-pinned" aria-hidden="true" />
        Ver mapa
      </button>
    </header>

    <section class="two-column-grid">
      <article class="panel">
        <div class="panel-header">
          <div>
            <h2>Tempo médio por bairro</h2>
            <p>Entrega em minutos.</p>
          </div>
        </div>
        <div class="bar-list">
          <div v-for="item in deliveryByNeighborhood" :key="item.label" class="bar-row delivery">
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

      <article class="insight-card" style="margin-bottom: 0;">
        <div class="insight-icon"><Icon name="lucide:triangle-alert" aria-hidden="true" /></div>
        <div>
          <span>Alerta operacional</span>
          <strong>Vila Nova está acima da meta de entrega. Priorize moto e revise raio no jantar.</strong>
        </div>
      </article>
    </section>

    <section class="panel table-panel">
      <div class="panel-header">
        <div>
          <h2>Rotas recentes</h2>
          <p>Resumo mockado das entregas.</p>
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr><th>Pedido</th><th>Entregador</th><th>Bairro</th><th>Tempo</th><th>Status</th></tr>
          </thead>
          <tbody>
            <tr v-for="row in deliveryRows" :key="row.id">
              <td><a href="#">{{ row.id }}</a></td>
              <td>{{ row.courier }}</td>
              <td>{{ row.neighborhood }}</td>
              <td>{{ row.time }}</td>
              <td><span class="status-badge" :class="row.badge">{{ row.status }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>
