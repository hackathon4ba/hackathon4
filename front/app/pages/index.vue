<script setup lang="ts">
useHead({ title: 'Início' })
</script>

<template>
  <div>
    <section class="home-hero">
      <div>
        <span class="eyebrow">Foodtech para gestão</span>
        <h1>iFood Copilot</h1>
        <p>Seu gerente de dados para vender mais, desperdiçar menos e entregar melhor.</p>
      </div>

      <div class="home-actions">
        <NuxtLink class="primary-button" to="/dashboard">
          <Icon name="lucide:layout-dashboard" aria-hidden="true" />
          Ver demo
        </NuxtLink>
        <NuxtLink class="secondary-button" to="/copilot">
          <Icon name="lucide:sparkles" aria-hidden="true" />
          Abrir Copilot
        </NuxtLink>
      </div>
    </section>

    <section class="cards-grid three" style="margin-top: 24px;">
      <article class="home-card">
        <h3>Operação</h3>
        <p>Acompanhe pedidos, entregas e gargalos em uma visão administrativa.</p>
      </article>
      <article class="home-card">
        <h3>Faturamento</h3>
        <p>Veja receita, ticket médio, repasses e oportunidades de venda.</p>
      </article>
      <article class="home-card">
        <h3>Fidelidade</h3>
        <p>Simule pontos, recompensas e clientes com maior potencial de retorno.</p>
      </article>
    </section>
  </div>
</template>
