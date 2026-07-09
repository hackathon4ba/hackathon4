<script setup lang="ts">
useHead({ title: 'Estoque' })

type InventoryItem = {
  id: number
  restaurant_id: number
  name: string
  unit: string
  quantity_available: number
  minimum_quantity: number
  is_low_stock?: boolean
  created_at: string
  updated_at: string
}

type InventoryItemsResponse = {
  data: InventoryItem[]
  msg: string
}

type InventoryPayload = {
  name: string
  unit: string
  quantity_available: number
  minimum_quantity: number
}

const config = useRuntimeConfig()
const auth = useRestaurantAuth()

const inventoryItems = ref<InventoryItem[]>([])
const loading = ref(true)
const saving = ref(false)
const deletingInventoryId = ref<number | null>(null)
const errorMessage = ref('')
const successMessage = ref('')
const inventorySearch = ref('')
const editingInventoryId = ref<number | null>(null)

const inventoryForm = reactive({
  name: '',
  unit: 'un',
  quantity_available: '',
  minimum_quantity: ''
})

const isEditingInventory = computed(() => editingInventoryId.value !== null)

const filteredInventoryItems = computed(() => {
  const search = inventorySearch.value.trim().toLowerCase()

  return inventoryItems.value.filter((item) => {
    return !search || item.name.toLowerCase().includes(search) || item.unit.toLowerCase().includes(search)
  })
})

const lowStockItems = computed(() => {
  return inventoryItems.value.filter((item) => item.is_low_stock)
})

function getAuthHeaders() {
  return {
    Authorization: `Bearer ${auth.token.value}`
  }
}

function resetFeedback() {
  errorMessage.value = ''
  successMessage.value = ''
}

function sortInventoryItems(value: InventoryItem[]) {
  return value.slice().sort((left, right) => left.name.localeCompare(right.name))
}

function resetInventoryForm() {
  inventoryForm.name = ''
  inventoryForm.unit = 'un'
  inventoryForm.quantity_available = ''
  inventoryForm.minimum_quantity = ''
  editingInventoryId.value = null
}

function fillInventoryForm(item: InventoryItem) {
  inventoryForm.name = item.name
  inventoryForm.unit = item.unit
  inventoryForm.quantity_available = String(item.quantity_available)
  inventoryForm.minimum_quantity = String(item.minimum_quantity)
  editingInventoryId.value = item.id
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

async function fetchInventoryItems() {
  if (!auth.token.value) {
    return
  }

  loading.value = true
  resetFeedback()

  try {
    const response = await $fetch<InventoryItemsResponse>('/restaurants/inventory/items', {
      baseURL: config.public.apiBase,
      headers: getAuthHeaders()
    })

    inventoryItems.value = sortInventoryItems(response.data)
  } catch (error) {
    errorMessage.value = getRequestErrorMessage(error, 'Nao foi possivel carregar o estoque.')
  } finally {
    loading.value = false
  }
}

async function submitInventoryForm() {
  const quantityAvailable = Number(inventoryForm.quantity_available.replace(',', '.'))
  const minimumQuantity = Number((inventoryForm.minimum_quantity || '0').replace(',', '.'))

  if (!inventoryForm.name.trim()) {
    errorMessage.value = 'Informe o nome do item de estoque.'
    return
  }

  if (!inventoryForm.unit.trim()) {
    errorMessage.value = 'Informe a unidade do item de estoque.'
    return
  }

  if (!Number.isFinite(quantityAvailable) || quantityAvailable < 0) {
    errorMessage.value = 'Informe uma quantidade disponivel valida.'
    return
  }

  if (!Number.isFinite(minimumQuantity) || minimumQuantity < 0) {
    errorMessage.value = 'Informe um estoque minimo valido.'
    return
  }

  saving.value = true
  resetFeedback()

  const payload: InventoryPayload = {
    name: inventoryForm.name.trim(),
    unit: inventoryForm.unit.trim(),
    quantity_available: quantityAvailable,
    minimum_quantity: minimumQuantity
  }

  try {
    if (isEditingInventory.value && editingInventoryId.value !== null) {
      const updatedItem = await $fetch<InventoryItem>(
        `/restaurants/inventory/items/${editingInventoryId.value}`,
        {
          method: 'PATCH',
          baseURL: config.public.apiBase,
          headers: getAuthHeaders(),
          body: payload
        }
      )

      inventoryItems.value = sortInventoryItems(inventoryItems.value.map((item) => {
        return item.id === updatedItem.id ? updatedItem : item
      }))
      successMessage.value = 'Item de estoque atualizado com sucesso.'
    } else {
      const createdItem = await $fetch<InventoryItem>('/restaurants/inventory/items', {
        method: 'POST',
        baseURL: config.public.apiBase,
        headers: getAuthHeaders(),
        body: payload
      })

      inventoryItems.value = sortInventoryItems([...inventoryItems.value, createdItem])
      successMessage.value = 'Item de estoque criado com sucesso.'
    }

    resetInventoryForm()
  } catch (error) {
    errorMessage.value = getRequestErrorMessage(error, 'Nao foi possivel salvar o item de estoque.')
  } finally {
    saving.value = false
  }
}

async function removeInventoryItem(itemId: number) {
  deletingInventoryId.value = itemId
  resetFeedback()

  try {
    await $fetch(`/restaurants/inventory/items/${itemId}`, {
      method: 'DELETE',
      baseURL: config.public.apiBase,
      headers: getAuthHeaders()
    })

    inventoryItems.value = inventoryItems.value.filter((item) => item.id !== itemId)

    if (editingInventoryId.value === itemId) {
      resetInventoryForm()
    }

    successMessage.value = 'Item de estoque removido com sucesso.'
  } catch (error) {
    errorMessage.value = getRequestErrorMessage(error, 'Nao foi possivel remover o item de estoque.')
  } finally {
    deletingInventoryId.value = null
  }
}

await auth.initialize()
await fetchInventoryItems()
</script>

<template>
  <div>
    <header class="page-header">
      <div>
        <span class="eyebrow">Operacao</span>
        <h1>Estoque</h1>
        <p>Cadastre insumos, acompanhe baixo estoque e mantenha os itens disponiveis para as receitas.</p>
      </div>
      <button class="secondary-button" type="button" :disabled="loading" @click="fetchInventoryItems">
        <Icon name="lucide:refresh-cw" aria-hidden="true" />
        Atualizar
      </button>
    </header>

    <p v-if="errorMessage" class="inventory-feedback danger-feedback">
      {{ errorMessage }}
    </p>
    <p v-if="successMessage" class="inventory-feedback success-feedback">
      {{ successMessage }}
    </p>

    <section class="cards-grid three inventory-summary-grid">
      <article class="summary-card">
        <h3>{{ inventoryItems.length }}</h3>
        <p>Itens cadastrados no estoque.</p>
      </article>
      <article class="summary-card summary-card-alert">
        <h3>{{ lowStockItems.length }}</h3>
        <p>Itens no limite minimo ou abaixo dele.</p>
      </article>
      <article class="summary-card">
        <h3>{{ filteredInventoryItems.length }}</h3>
        <p>Itens visiveis com o filtro atual.</p>
      </article>
    </section>

    <section class="two-column-grid inventory-grid">
      <section class="panel">
        <div class="panel-header">
          <div>
            <h2>{{ isEditingInventory ? 'Editar estoque' : 'Cadastrar estoque' }}</h2>
            <p>Crie os insumos que serao usados nas receitas dos pratos.</p>
          </div>
          <button class="secondary-button" type="button" @click="resetInventoryForm">
            <Icon :name="isEditingInventory ? 'lucide:x' : 'lucide:eraser'" aria-hidden="true" />
            {{ isEditingInventory ? 'Cancelar edicao' : 'Limpar formulario' }}
          </button>
        </div>

        <form class="inventory-form" @submit.prevent="submitInventoryForm">
          <div class="form-grid inventory-form-grid">
            <label class="form-field">
              <span>Item de estoque</span>
              <input v-model="inventoryForm.name" type="text" placeholder="File de frango" required>
            </label>
            <label class="form-field">
              <span>Unidade</span>
              <input v-model="inventoryForm.unit" type="text" placeholder="kg, un, l" required>
            </label>
            <label class="form-field">
              <span>Quantidade disponivel</span>
              <input v-model="inventoryForm.quantity_available" type="text" inputmode="decimal" placeholder="12" required>
            </label>
            <label class="form-field">
              <span>Estoque minimo</span>
              <input v-model="inventoryForm.minimum_quantity" type="text" inputmode="decimal" placeholder="2">
            </label>
          </div>

          <div class="form-actions inventory-form-actions">
            <button class="primary-button" type="submit" :disabled="saving">
              <Icon :name="isEditingInventory ? 'lucide:save' : 'lucide:package-plus'" aria-hidden="true" />
              {{ saving ? 'Salvando...' : isEditingInventory ? 'Salvar estoque' : 'Cadastrar estoque' }}
            </button>
          </div>
        </form>
      </section>

      <section class="panel">
        <div class="panel-header">
          <div>
            <h2>Filtros</h2>
            <p>Encontre insumos por nome ou unidade.</p>
          </div>
        </div>

        <label class="form-field">
          <span>Buscar estoque</span>
          <input v-model="inventorySearch" type="search" placeholder="Frango, kg, molho...">
        </label>

        <div class="low-stock-list">
          <div class="summary-line">
            <span>Itens em alerta</span>
            <strong class="danger">{{ lowStockItems.length }}</strong>
          </div>
          <div v-if="lowStockItems.length === 0" class="inventory-empty">
            Nenhum item em baixo estoque no momento.
          </div>
          <div v-else class="alert-chip-list">
            <span
              v-for="item in lowStockItems"
              :key="item.id"
              class="status-chip status-danger"
            >
              {{ item.name }}
            </span>
          </div>
        </div>
      </section>
    </section>

    <section class="panel table-panel">
      <div class="panel-header">
        <div>
          <h2>Itens de estoque</h2>
          <p>Monitore disponibilidade, unidade e alertas de estoque minimo.</p>
        </div>
      </div>

      <div v-if="loading" class="inventory-empty">
        Carregando estoque...
      </div>

      <div v-else-if="filteredInventoryItems.length === 0" class="inventory-empty">
        Nenhum item de estoque encontrado com os filtros atuais.
      </div>

      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Item</th>
              <th>Disponivel</th>
              <th>Minimo</th>
              <th>Status</th>
              <th>Atualizado em</th>
              <th>Acoes</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredInventoryItems" :key="item.id">
              <td><strong>{{ item.name }}</strong></td>
              <td>{{ item.quantity_available }} {{ item.unit }}</td>
              <td>{{ item.minimum_quantity }} {{ item.unit }}</td>
              <td>
                <span class="status-chip" :class="item.is_low_stock ? 'status-danger' : 'status-ok'">
                  {{ item.is_low_stock ? 'Baixo estoque' : 'Saudavel' }}
                </span>
              </td>
              <td>{{ new Date(item.updated_at).toLocaleDateString('pt-BR') }}</td>
              <td>
                <div class="table-actions">
                  <button class="secondary-button action-button" type="button" @click="fillInventoryForm(item)">
                    <Icon name="lucide:pencil-line" aria-hidden="true" />
                    Editar
                  </button>
                  <button
                    class="secondary-button action-button danger-button"
                    type="button"
                    :disabled="deletingInventoryId === item.id"
                    @click="removeInventoryItem(item.id)"
                  >
                    <Icon name="lucide:trash-2" aria-hidden="true" />
                    {{ deletingInventoryId === item.id ? 'Removendo...' : 'Excluir' }}
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
.inventory-grid {
  align-items: start;
}

.inventory-summary-grid {
  margin-bottom: 24px;
}

.summary-card h3 {
  font-size: 28px;
}

.summary-card-alert {
  background: #fff7ed;
  border-color: #fed7aa;
}

.inventory-form {
  display: grid;
  gap: 16px;
}

.inventory-form-grid {
  grid-template-columns: 1fr 1fr;
}

.inventory-form-actions {
  justify-content: space-between;
}

.inventory-feedback {
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

.inventory-empty {
  padding: 18px 0 8px;
  color: var(--color-gray-500);
}

.low-stock-list {
  display: grid;
  gap: 14px;
  margin-top: 20px;
}

.alert-chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.status-chip {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
}

.status-ok {
  background: #ecfdf3;
  color: #166534;
}

.status-danger {
  background: #fff1f2;
  color: #b42318;
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

@media (max-width: 980px) {
  .inventory-form-grid,
  .inventory-summary-grid {
    grid-template-columns: 1fr;
  }

  .inventory-form-actions {
    flex-direction: column;
  }

  .inventory-form-actions .primary-button,
  .inventory-form-actions .secondary-button {
    width: 100%;
  }
}
</style>
