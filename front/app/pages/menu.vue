<script setup lang="ts">
useHead({ title: 'Cardapio' })

type MenuItem = {
  id: number
  restaurant_id: number
  name: string
  price_cents: number
  ingredients: string[]
  created_at: string
  updated_at: string
}

type MenuItemsResponse = {
  data: MenuItem[]
  msg: string
}

type MenuItemPayload = {
  name: string
  price: number
  ingredients: string[]
}

const config = useRuntimeConfig()
const auth = useRestaurantAuth()

const items = ref<MenuItem[]>([])
const loading = ref(true)
const saving = ref(false)
const deletingId = ref<number | null>(null)
const errorMessage = ref('')
const successMessage = ref('')
const searchTerm = ref('')
const ingredientFilter = ref('')
const editingItemId = ref<number | null>(null)

const form = reactive({
  name: '',
  price: '',
  ingredients: ''
})

const isEditing = computed(() => editingItemId.value !== null)

const filteredItems = computed(() => {
  const search = searchTerm.value.trim().toLowerCase()
  const ingredient = ingredientFilter.value.trim().toLowerCase()

  return items.value.filter((item) => {
    const matchesSearch = !search || item.name.toLowerCase().includes(search)
    const matchesIngredient = !ingredient || item.ingredients.some((value) => {
      return value.toLowerCase().includes(ingredient)
    })

    return matchesSearch && matchesIngredient
  })
})

function getAuthHeaders() {
  return {
    Authorization: `Bearer ${auth.token.value}`
  }
}

function formatBRLFromCents(value: number) {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value / 100)
}

function normalizeIngredients(rawIngredients: string) {
  return rawIngredients
    .split(',')
    .map((ingredient) => ingredient.trim())
    .filter(Boolean)
}

function resetFeedback() {
  errorMessage.value = ''
  successMessage.value = ''
}

function resetForm() {
  form.name = ''
  form.price = ''
  form.ingredients = ''
  editingItemId.value = null
}

function fillForm(item: MenuItem) {
  form.name = item.name
  form.price = (item.price_cents / 100).toFixed(2)
  form.ingredients = item.ingredients.join(', ')
  editingItemId.value = item.id
  resetFeedback()
}

function getRequestErrorMessage(error: unknown, fallback: string) {
  if (error && typeof error === 'object' && 'data' in error) {
    const message = (error as { data?: { msg?: string } }).data?.msg
    if (message) {
      return message
    }
  }

  return fallback
}

async function fetchMenuItems() {
  if (!auth.token.value) {
    return
  }

  loading.value = true
  resetFeedback()

  try {
    const response = await $fetch<MenuItemsResponse>('/restaurants/menu/items', {
      baseURL: config.public.apiBase,
      headers: getAuthHeaders()
    })

    items.value = response.data
  } catch (error) {
    errorMessage.value = getRequestErrorMessage(error, 'Nao foi possivel carregar o cardapio.')
  } finally {
    loading.value = false
  }
}

async function submitForm() {
  const ingredients = normalizeIngredients(form.ingredients)
  const price = Number(form.price.replace(',', '.'))

  if (!form.name.trim()) {
    errorMessage.value = 'Informe o nome do item.'
    return
  }

  if (!Number.isFinite(price) || price <= 0) {
    errorMessage.value = 'Informe um preco valido.'
    return
  }

  if (ingredients.length === 0) {
    errorMessage.value = 'Informe pelo menos um ingrediente.'
    return
  }

  saving.value = true
  resetFeedback()

  const payload: MenuItemPayload = {
    name: form.name.trim(),
    price,
    ingredients
  }

  try {
    if (isEditing.value && editingItemId.value !== null) {
      const updatedItem = await $fetch<MenuItem>(
        `/restaurants/menu/items/${editingItemId.value}`,
        {
          method: 'PATCH',
          baseURL: config.public.apiBase,
          headers: getAuthHeaders(),
          body: payload
        }
      )

      items.value = items.value.map((item) => {
        return item.id === updatedItem.id ? updatedItem : item
      })
      successMessage.value = 'Item atualizado com sucesso.'
    } else {
      const createdItem = await $fetch<MenuItem>('/restaurants/menu/items', {
        method: 'POST',
        baseURL: config.public.apiBase,
        headers: getAuthHeaders(),
        body: payload
      })

      items.value = [...items.value, createdItem].sort((left, right) => {
        return left.name.localeCompare(right.name)
      })
      successMessage.value = 'Item criado com sucesso.'
    }

    resetForm()
  } catch (error) {
    errorMessage.value = getRequestErrorMessage(error, 'Nao foi possivel salvar o item.')
  } finally {
    saving.value = false
  }
}

async function removeItem(itemId: number) {
  deletingId.value = itemId
  resetFeedback()

  try {
    await $fetch(`/restaurants/menu/items/${itemId}`, {
      method: 'DELETE',
      baseURL: config.public.apiBase,
      headers: getAuthHeaders()
    })

    items.value = items.value.filter((item) => item.id !== itemId)

    if (editingItemId.value === itemId) {
      resetForm()
    }

    successMessage.value = 'Item removido com sucesso.'
  } catch (error) {
    errorMessage.value = getRequestErrorMessage(error, 'Nao foi possivel remover o item.')
  } finally {
    deletingId.value = null
  }
}

await auth.initialize()
await fetchMenuItems()
</script>

<template>
  <div>
    <header class="page-header">
      <div>
        <span class="eyebrow">Produtos</span>
        <h1>Cardapio</h1>
        <p>Cadastre, edite e remova os itens do cardapio do seu restaurante.</p>
      </div>
      <button class="secondary-button" type="button" @click="resetForm">
        <Icon :name="isEditing ? 'lucide:plus' : 'lucide:eraser'" aria-hidden="true" />
        {{ isEditing ? 'Novo item' : 'Limpar formulario' }}
      </button>
    </header>

    <section class="two-column-grid menu-grid">
      <section class="panel">
        <div class="panel-header">
          <div>
            <h2>{{ isEditing ? 'Editar item' : 'Cadastrar item' }}</h2>
            <p>Informe nome, preco e ingredientes usados em cada produto.</p>
          </div>
        </div>

        <p v-if="errorMessage" class="menu-feedback danger-feedback">
          {{ errorMessage }}
        </p>
        <p v-if="successMessage" class="menu-feedback success-feedback">
          {{ successMessage }}
        </p>

        <form class="menu-form" @submit.prevent="submitForm">
          <div class="form-grid menu-form-grid">
            <label class="form-field">
              <span>Nome do item</span>
              <input v-model="form.name" type="text" placeholder="Parmegiana" required>
            </label>

            <label class="form-field">
              <span>Preco</span>
              <input
                v-model="form.price"
                type="text"
                inputmode="decimal"
                placeholder="54,90"
                required
              >
            </label>
          </div>

          <label class="form-field">
            <span>Ingredientes</span>
            <textarea
              v-model="form.ingredients"
              placeholder="Arroz, File de frango, Molho de tomate, Queijo"
              required
            />
          </label>

          <div class="form-actions menu-form-actions">
            <button v-if="isEditing" class="secondary-button" type="button" @click="resetForm">
              Cancelar edicao
            </button>
            <button class="primary-button" type="submit" :disabled="saving">
              <Icon :name="isEditing ? 'lucide:save' : 'lucide:plus'" aria-hidden="true" />
              {{ saving ? 'Salvando...' : isEditing ? 'Salvar item' : 'Cadastrar item' }}
            </button>
          </div>
        </form>
      </section>

      <section class="panel">
        <div class="panel-header">
          <div>
            <h2>Filtros</h2>
            <p>Busque por nome do prato ou ingrediente.</p>
          </div>
        </div>

        <div class="form-grid menu-form-grid">
          <label class="form-field">
            <span>Buscar item</span>
            <input v-model="searchTerm" type="search" placeholder="Nome do prato">
          </label>
          <label class="form-field">
            <span>Ingrediente</span>
            <input v-model="ingredientFilter" type="search" placeholder="Queijo, arroz, molho">
          </label>
        </div>

        <div class="menu-summary">
          <article class="summary-card">
            <h3>{{ items.length }}</h3>
            <p>Itens cadastrados no cardapio.</p>
          </article>
          <article class="summary-card">
            <h3>{{ filteredItems.length }}</h3>
            <p>Itens visiveis com os filtros atuais.</p>
          </article>
        </div>
      </section>
    </section>

    <section class="panel table-panel">
      <div class="panel-header">
        <div>
          <h2>Itens do cardapio</h2>
          <p>Todos os itens pertencem ao restaurante autenticado.</p>
        </div>
        <button class="secondary-button" type="button" :disabled="loading" @click="fetchMenuItems">
          <Icon name="lucide:refresh-cw" aria-hidden="true" />
          Atualizar lista
        </button>
      </div>

      <div v-if="loading" class="menu-empty">
        Carregando itens do cardapio...
      </div>

      <div v-else-if="filteredItems.length === 0" class="menu-empty">
        Nenhum item encontrado com os filtros atuais.
      </div>

      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Item</th>
              <th>Preco</th>
              <th>Ingredientes</th>
              <th>Atualizado em</th>
              <th>Acoes</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredItems" :key="item.id">
              <td>
                <strong>{{ item.name }}</strong>
              </td>
              <td>{{ formatBRLFromCents(item.price_cents) }}</td>
              <td>
                <div class="ingredient-list">
                  <span v-for="ingredient in item.ingredients" :key="`${item.id}-${ingredient}`" class="ingredient-chip">
                    {{ ingredient }}
                  </span>
                </div>
              </td>
              <td>{{ new Date(item.updated_at).toLocaleDateString('pt-BR') }}</td>
              <td>
                <div class="table-actions">
                  <button class="secondary-button action-button" type="button" @click="fillForm(item)">
                    <Icon name="lucide:pencil-line" aria-hidden="true" />
                    Editar
                  </button>
                  <button
                    class="secondary-button action-button danger-button"
                    type="button"
                    :disabled="deletingId === item.id"
                    @click="removeItem(item.id)"
                  >
                    <Icon name="lucide:trash-2" aria-hidden="true" />
                    {{ deletingId === item.id ? 'Removendo...' : 'Excluir' }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<style scoped>
.menu-grid {
  align-items: start;
}

.menu-form {
  display: grid;
  gap: 16px;
}

.menu-form-grid {
  grid-template-columns: 1fr 1fr;
}

.menu-form-actions {
  justify-content: space-between;
}

.menu-feedback {
  margin-bottom: 16px;
  padding: 14px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 700;
}

.danger-feedback {
  border: 1px solid #fecaca;
  background: #fff1f2;
  color: #b42318;
}

.success-feedback {
  border: 1px solid #bbf7d0;
  background: #f0fdf4;
  color: #166534;
}

.menu-summary {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  margin-top: 20px;
}

.menu-summary .summary-card h3 {
  font-size: 28px;
}

.menu-empty {
  padding: 18px 0 8px;
  color: var(--color-gray-500);
}

.ingredient-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.ingredient-chip {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  background: var(--color-gray-100);
  color: var(--color-gray-700);
  font-size: 12px;
  font-weight: 700;
}

.table-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.action-button {
  min-height: 36px;
  padding: 0 12px;
}

.danger-button {
  color: var(--color-red);
  border-color: #fecaca;
}

@media (max-width: 920px) {
  .menu-form-grid,
  .menu-summary {
    grid-template-columns: 1fr;
  }

  .menu-form-actions {
    flex-direction: column;
  }

  .menu-form-actions .primary-button,
  .menu-form-actions .secondary-button {
    width: 100%;
  }
}
</style>
