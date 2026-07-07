<script setup lang="ts">
import { copilotInsights } from '../data/mock'

useHead({ title: 'Copilot' })
</script>

<template>
  <div>
    <header class="page-header">
      <div>
        <span class="eyebrow">O que fazer hoje?</span>
        <h1>Copilot</h1>
        <p>Recomendações acionáveis mockadas para aumentar venda e melhorar operação.</p>
      </div>
      <button class="primary-button" type="button">
        <Icon name="lucide:sparkles" aria-hidden="true" />
        Gerar plano
      </button>
    </header>

    <section class="cards-grid three">
      <article v-for="insight in copilotInsights" :key="insight.title" class="summary-card">
        <h3>{{ insight.title }}</h3>
        <p>{{ insight.text }}</p>
      </article>
    </section>

    <section class="panel">
      <div class="panel-header">
        <div>
          <h2>Plano recomendado</h2>
          <p>Ações curtas para executar ainda hoje.</p>
        </div>
      </div>
      <div class="stack-list">
        <div class="summary-line"><span>19h00</span><strong>Adicionar 1 pessoa no preparo de pratos quentes</strong></div>
        <div class="summary-line"><span>19h30</span><strong>Destacar combo Parmegiana + bebida no cardápio</strong></div>
        <div class="summary-line"><span>20h00</span><strong>Pausar entregas longas se SLA passar de 38 min</strong></div>
      </div>
    </section>
  </div>
</template>
