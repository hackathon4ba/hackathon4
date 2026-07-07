<script setup lang="ts">
import { formatBRL, recentOrders, type BadgeTone, type MockOrder } from '../data/mock'

useHead({ title: 'Pedidos' })

const orders = ref<MockOrder[]>(recentOrders.map((order) => ({ ...order })))
const form = reactive({
  customer: '',
  dish: '',
  period: 'Jantar',
  value: 49.9,
  status: 'Em preparo'
})

function toneForStatus(status: string): BadgeTone {
  if (status === 'Atrasado' || status === 'Cancelado') {
    return 'red'
  }

  if (status === 'Em preparo') {
    return 'orange'
  }

  return 'green'
}

function addOrder() {
  if (!form.customer.trim() || !form.dish.trim() || !form.value) {
    return
  }

  const nextNumber = 8422 + orders.value.length

  orders.value.unshift({
    id: `#${nextNumber}`,
    customer: form.customer.trim(),
    dish: form.dish.trim(),
    period: form.period,
    value: Number(form.value),
    status: form.status,
    badge: toneForStatus(form.status)
  })

  form.customer = ''
  form.dish = ''
  form.period = 'Jantar'
  form.value = 49.9
  form.status = 'Em preparo'
}
</script>

<template>
  <div>
    <header class="page-header">
      <div>
        <span class="eyebrow">Operação</span>
        <h1>Pedidos</h1>
        <p>Registro local mockado para criar e acompanhar pedidos da demo.</p>
      </div>

      <button class="primary-button" type="button">
        <Icon name="lucide:refresh-cw" aria-hidden="true" />
        Atualizar fila
      </button>
    </header>

    <section class="filters">
      <label>
        <span>Status</span>
        <select>
          <option>Todos</option>
          <option>Em preparo</option>
          <option>Saiu para entrega</option>
          <option>Entregue</option>
        </select>
      </label>
      <label>
        <span>Período</span>
        <select>
          <option>Hoje</option>
          <option>Últimos 7 dias</option>
        </select>
      </label>
      <label>
        <span>Buscar pedido</span>
        <input type="search" placeholder="#8421 ou nome do cliente">
      </label>
      <button class="primary-button filter-button" type="button">
        <Icon name="lucide:search" aria-hidden="true" />
        Consultar
      </button>
    </section>

    <section class="two-column-grid">
      <article class="panel">
        <div class="panel-header">
          <div>
            <h2>Adicionar novo pedido</h2>
            <p>Pedido mockado aparece imediatamente na tabela.</p>
          </div>
        </div>

        <form @submit.prevent="addOrder">
          <div class="form-grid">
            <label class="form-field">
              <span>Cliente</span>
              <input v-model="form.customer" type="text" placeholder="Nome do cliente">
            </label>
            <label class="form-field">
              <span>Prato</span>
              <input v-model="form.dish" type="text" placeholder="Ex: Parmegiana">
            </label>
            <label class="form-field">
              <span>Período</span>
              <select v-model="form.period">
                <option>Manhã</option>
                <option>Almoço</option>
                <option>Tarde</option>
                <option>Jantar</option>
              </select>
            </label>
            <label class="form-field">
              <span>Valor</span>
              <input v-model.number="form.value" type="number" min="1" step="0.01">
            </label>
            <label class="form-field">
              <span>Status</span>
              <select v-model="form.status">
                <option>Em preparo</option>
                <option>Saiu para entrega</option>
                <option>Entregue</option>
                <option>Atrasado</option>
                <option>Cancelado</option>
              </select>
            </label>
          </div>

          <div class="form-actions">
            <button class="primary-button" type="submit">
              <Icon name="lucide:plus" aria-hidden="true" />
              Adicionar pedido
            </button>
          </div>
        </form>
      </article>

      <article class="panel">
        <div class="panel-header">
          <div>
            <h2>Resumo da fila</h2>
            <p>Indicadores mockados de operação atual.</p>
          </div>
        </div>
        <div class="stack-list">
          <div class="summary-line">
            <span>Pedidos na lista</span>
            <strong>{{ orders.length }}</strong>
          </div>
          <div class="summary-line">
            <span>Em preparo</span>
            <strong>{{ orders.filter((order) => order.status === 'Em preparo').length }}</strong>
          </div>
          <div class="summary-line">
            <span>Ticket médio local</span>
            <strong>{{ formatBRL(orders.reduce((sum, order) => sum + order.value, 0) / orders.length) }}</strong>
          </div>
          <div class="summary-line">
            <span>Pedidos com atenção</span>
            <strong class="danger">{{ orders.filter((order) => order.badge === 'red').length }}</strong>
          </div>
        </div>
      </article>
    </section>

    <section class="panel table-panel">
      <div class="panel-header">
        <div>
          <h2>Lista de pedidos</h2>
          <p>Dados mockados com inserção local na página.</p>
        </div>
      </div>

      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Pedido</th>
              <th>Cliente</th>
              <th>Prato</th>
              <th>Período</th>
              <th>Valor</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in orders" :key="order.id">
              <td><a href="#">{{ order.id }}</a></td>
              <td>{{ order.customer }}</td>
              <td>{{ order.dish }}</td>
              <td>{{ order.period }}</td>
              <td>{{ formatBRL(order.value) }}</td>
              <td><span class="status-badge" :class="order.badge">{{ order.status }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>
