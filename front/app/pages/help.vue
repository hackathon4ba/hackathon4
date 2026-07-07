<script setup lang="ts">
import { helpItems } from '../data/mock'

useHead({ title: 'Ajuda' })
</script>

<template>
  <div>
    <header class="page-header">
      <div>
        <span class="eyebrow">Suporte</span>
        <h1>Ajuda</h1>
        <p>Conteúdos mockados para orientar o uso da demo administrativa.</p>
      </div>
      <button class="primary-button" type="button">
        <Icon name="lucide:message-circle" aria-hidden="true" />
        Abrir chamado
      </button>
    </header>

    <section class="cards-grid three">
      <article v-for="item in helpItems" :key="item.title" class="summary-card">
        <h3>{{ item.title }}</h3>
        <p>{{ item.text }}</p>
      </article>
    </section>

    <section class="panel">
      <div class="panel-header">
        <div>
          <h2>Checklist da demo</h2>
          <p>Fluxos principais para apresentar.</p>
        </div>
      </div>
      <div class="stack-list">
        <div class="summary-line"><span>Dashboard</span><strong>Indicadores e insight do Copilot</strong></div>
        <div class="summary-line"><span>Pedidos</span><strong>Adicionar pedido localmente</strong></div>
        <div class="summary-line"><span>Fidelidade</span><strong>Regra R$1 = 1 ponto</strong></div>
      </div>
    </section>
  </div>
</template>
