<script setup lang="ts">
import { menuRows } from '../data/mock'

useHead({ title: 'Cardápio' })
</script>

<template>
  <div>
    <header class="page-header">
      <div>
        <span class="eyebrow">Produtos</span>
        <h1>Cardápio</h1>
        <p>Itens, categorias, preços e disponibilidade para a demo.</p>
      </div>
      <button class="primary-button" type="button">
        <Icon name="lucide:plus" aria-hidden="true" />
        Novo item
      </button>
    </header>

    <section class="filters">
      <label><span>Categoria</span><select><option>Todas</option><option>Pratos principais</option><option>Lanches</option></select></label>
      <label><span>Status</span><select><option>Todos</option><option>Ativo</option><option>Baixo estoque</option></select></label>
      <label><span>Buscar item</span><input type="search" placeholder="Nome do prato"></label>
      <button class="primary-button filter-button" type="button">Consultar</button>
    </section>

    <section class="panel table-panel">
      <div class="panel-header">
        <div>
          <h2>Itens do cardápio</h2>
          <p>Mais vendidos e itens que precisam de atenção.</p>
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Item</th>
              <th>Categoria</th>
              <th>Preço</th>
              <th>Vendas</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in menuRows" :key="item.item">
              <td><a href="#">{{ item.item }}</a></td>
              <td>{{ item.category }}</td>
              <td>{{ item.price }}</td>
              <td>{{ item.sales }}</td>
              <td><span class="status-badge" :class="item.badge">{{ item.status }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>
