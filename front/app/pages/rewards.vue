<script setup lang="ts">
import { rewardRows } from '../data/mock'

useHead({ title: 'Recompensas' })
</script>

<template>
  <div>
    <header class="page-header">
      <div>
        <span class="eyebrow">Resgates</span>
        <h1>Recompensas</h1>
        <p>Benefícios mockados para resgate com pontos de fidelidade.</p>
      </div>
      <button class="primary-button" type="button">
        <Icon name="lucide:gift" aria-hidden="true" />
        Nova recompensa
      </button>
    </header>

    <section class="cards-grid three">
      <article v-for="reward in rewardRows" :key="reward.reward" class="summary-card">
        <h3>{{ reward.reward }}</h3>
        <p>{{ reward.redemptions }} resgates no período</p>
        <div class="reward-foot" style="margin-top: 18px;">
          <strong>{{ reward.cost }}</strong>
          <span class="status-badge" :class="reward.badge">{{ reward.status }}</span>
        </div>
      </article>
    </section>

    <section class="insight-card">
      <div class="insight-icon"><Icon name="lucide:lightbulb" aria-hidden="true" /></div>
      <div>
        <span>Insight de recompensa</span>
        <strong>Frete grátis performa bem para clientes recorrentes com ticket acima de R$ 40.</strong>
      </div>
    </section>
  </div>
</template>
