<script setup lang="ts">
import { customerRows } from '../data/mock'

useHead({ title: 'Clientes' })
</script>

<template>
  <div>
    <header class="page-header">
      <div>
        <span class="eyebrow">Relacionamento</span>
        <h1>Clientes</h1>
        <p>Ranking mockado de clientes, gastos, pedidos e pontos acumulados.</p>
      </div>
      <button class="primary-button" type="button">
        <Icon name="lucide:send" aria-hidden="true" />
        Enviar campanha
      </button>
    </header>

    <section class="filters">
      <label><span>Segmento</span><select><option>Todos</option><option>VIP</option><option>Recorrente</option></select></label>
      <label><span>Último pedido</span><select><option>Últimos 30 dias</option><option>Hoje</option></select></label>
      <label><span>Buscar cliente</span><input type="search" placeholder="Nome do cliente"></label>
      <button class="primary-button filter-button" type="button">Consultar</button>
    </section>

    <section class="panel table-panel">
      <div class="panel-header">
        <div>
          <h2>Top clientes</h2>
          <p>Base para ações de fidelidade.</p>
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr><th>Cliente</th><th>Pedidos</th><th>Gasto total</th><th>Pontos</th><th>Segmento</th></tr>
          </thead>
          <tbody>
            <tr v-for="customer in customerRows" :key="customer.name">
              <td><a href="#">{{ customer.name }}</a></td>
              <td>{{ customer.orders }}</td>
              <td>{{ customer.spent }}</td>
              <td>{{ customer.points }}</td>
              <td>{{ customer.segment }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>
