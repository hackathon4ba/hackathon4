<script setup lang="ts">
import { customerRows } from '../data/mock'

useHead({ title: 'Fidelidade' })
</script>

<template>
  <div>
    <header class="page-header">
      <div>
        <span class="eyebrow">Pontos</span>
        <h1>Fidelidade</h1>
        <p>Regra mockada: R$1 em pedidos gera 1 ponto para o cliente.</p>
      </div>
      <button class="primary-button" type="button">
        <Icon name="lucide:badge-plus" aria-hidden="true" />
        Ajustar regra
      </button>
    </header>

    <section class="metrics-grid">
      <article class="metric-card">
        <span>Regra ativa</span>
        <strong>R$1 = 1 ponto</strong>
        <small class="positive">Aplicada na demo</small>
      </article>
      <article class="metric-card">
        <span>Pontos gerados</span>
        <strong>2.228</strong>
        <small class="positive">Últimos 7 dias</small>
      </article>
      <article class="metric-card">
        <span>Clientes elegíveis</span>
        <strong>36</strong>
        <small class="neutral">Com mais de 120 pontos</small>
      </article>
    </section>

    <section class="panel table-panel">
      <div class="panel-header">
        <div>
          <h2>Ranking de pontos</h2>
          <p>Top clientes para campanha de recompra.</p>
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr><th>Cliente</th><th>Pedidos</th><th>Gasto total</th><th>Pontos</th><th>Ação sugerida</th></tr>
          </thead>
          <tbody>
            <tr v-for="customer in customerRows" :key="customer.name">
              <td><a href="#">{{ customer.name }}</a></td>
              <td>{{ customer.orders }}</td>
              <td>{{ customer.spent }}</td>
              <td>{{ customer.points }}</td>
              <td><a href="#">Oferecer recompensa</a></td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>
