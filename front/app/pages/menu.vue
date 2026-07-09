<script setup lang="ts">
useHead({ title: 'Cardapio' })

type RecipeEntry = {
  id: number
  menu_item_id: number
  inventory_item_id: number
  inventory_item_name: string
  inventory_item_unit: string
  quantity_required: number
}

type MenuItem = {
  id: number
  restaurant_id: number
  name: string
  price_cents: number
  ingredients: string[]
  recipe: RecipeEntry[]
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

type RecipePayload = {
  entries: Array<{
    inventory_item_id: number
    quantity_required: number
  }>
}

type InventoryItem = {
  id: number
  restaurant_id: number
  name: string
  unit: string
  quantity_available: number
  minimum_quantity: number
  is_low_stock?: boolean
}

type InventoryItemsResponse = {
  data: InventoryItem[]
  msg: string
}

const config = useRuntimeConfig()
const auth = useRestaurantAuth()

const items = ref<MenuItem[]>([])
const inventoryItems = ref<InventoryItem[]>([])
const loading = ref(true)
const inventoryLoading = ref(true)
const saving = ref(false)
const recipeSaving = ref(false)
const deletingId = ref<number | null>(null)
const errorMessage = ref('')
const successMessage = ref('')
const searchTerm = ref('')
const ingredientFilter = ref('')
const editingItemId = ref<number | null>(null)
const selectedRecipeItemId = ref<number | null>(null)
const dishModalOpen = ref(false)

const form = reactive({
  name: '',
  price: '',
  ingredients: [] as string[]
})

const recipeDraft = ref<Array<{ inventory_item_id: string, quantity_required: string }>>([])

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

const selectedRecipeItem = computed(() => {
  if (selectedRecipeItemId.value === null) {
    return null
  }

  return items.value.find((item) => item.id === selectedRecipeItemId.value) ?? null
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

function resetFeedback() {
  errorMessage.value = ''
  successMessage.value = ''
}

function sortMenuItems(value: MenuItem[]) {
  return value.slice().sort((left, right) => left.name.localeCompare(right.name))
}

function resetMenuForm() {
  form.name = ''
  form.price = ''
  form.ingredients = []
  editingItemId.value = null
}

function resetRecipeDraft() {
  recipeDraft.value = []
}

function loadRecipeDraft(item: MenuItem) {
  recipeDraft.value = item.recipe.map((entry) => ({
    inventory_item_id: String(entry.inventory_item_id),
    quantity_required: String(entry.quantity_required)
  }))
}

function fillForm(item: MenuItem) {
  form.name = item.name
  form.price = (item.price_cents / 100).toFixed(2)
  form.ingredients = item.ingredients.slice()
  editingItemId.value = item.id
  selectedRecipeItemId.value = item.id
  loadRecipeDraft(item)
  resetFeedback()
}

function openCreateDishModal() {
  resetMenuForm()
  selectedRecipeItemId.value = null
  resetRecipeDraft()
  resetFeedback()
  dishModalOpen.value = true
}

function openEditDishModal(item: MenuItem) {
  fillForm(item)
  dishModalOpen.value = true
}

function openRecipeModal(item: MenuItem) {
  resetMenuForm()
  selectedRecipeItemId.value = item.id
  loadRecipeDraft(item)
  resetFeedback()
  dishModalOpen.value = true
}

function closeDishModal() {
  dishModalOpen.value = false
  resetMenuForm()
  selectedRecipeItemId.value = null
  resetRecipeDraft()
}

const availableIngredientNames = computed(() => {
  return inventoryItems.value.map((item) => item.name)
})

const selectedIngredientsMissingFromInventory = computed(() => {
  return form.ingredients.filter((ingredient) => !availableIngredientNames.value.includes(ingredient))
})

function selectRecipeItem(item: MenuItem) {
  selectedRecipeItemId.value = item.id
  loadRecipeDraft(item)
  resetFeedback()
}

watch(selectedRecipeItemId, (nextId) => {
  if (nextId === null) {
    resetRecipeDraft()
    return
  }

  const item = items.value.find((candidate) => candidate.id === nextId)
  if (item) {
    loadRecipeDraft(item)
  }
})

function addRecipeRow() {
  recipeDraft.value.push({
    inventory_item_id: '',
    quantity_required: ''
  })
}

function removeRecipeRow(index: number) {
  recipeDraft.value.splice(index, 1)
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

  try {
    const response = await $fetch<MenuItemsResponse>('/restaurants/menu/items', {
      baseURL: config.public.apiBase,
      headers: getAuthHeaders()
    })

    items.value = sortMenuItems(response.data)

    if (selectedRecipeItemId.value !== null) {
      const refreshedItem = items.value.find((item) => item.id === selectedRecipeItemId.value)
      if (refreshedItem) {
        loadRecipeDraft(refreshedItem)
      }
    }
  } catch (error) {
    errorMessage.value = getRequestErrorMessage(error, 'Nao foi possivel carregar o cardapio.')
  } finally {
    loading.value = false
  }
}

async function fetchInventoryItems() {
  if (!auth.token.value) {
    return
  }

  inventoryLoading.value = true

  try {
    const response = await $fetch<InventoryItemsResponse>('/restaurants/inventory/items', {
      baseURL: config.public.apiBase,
      headers: getAuthHeaders()
    })

    inventoryItems.value = response.data
      .slice()
      .sort((left, right) => left.name.localeCompare(right.name))
  } catch (error) {
    errorMessage.value = getRequestErrorMessage(error, 'Nao foi possivel carregar o estoque para montar a receita.')
  } finally {
    inventoryLoading.value = false
  }
}

async function refreshAll() {
  resetFeedback()
  await Promise.all([fetchMenuItems(), fetchInventoryItems()])
}

async function submitForm() {
  const price = Number(form.price.replace(',', '.'))

  if (!form.name.trim()) {
    errorMessage.value = 'Informe o nome do item.'
    return
  }

  if (!Number.isFinite(price) || price <= 0) {
    errorMessage.value = 'Informe um preco valido.'
    return
  }

  if (form.ingredients.length === 0) {
    errorMessage.value = 'Informe pelo menos um ingrediente.'
    return
  }

  saving.value = true
  resetFeedback()

  const payload: MenuItemPayload = {
    name: form.name.trim(),
    price,
    ingredients: form.ingredients.slice()
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

      items.value = sortMenuItems(items.value.map((item) => {
        return item.id === updatedItem.id ? updatedItem : item
      }))

      selectedRecipeItemId.value = updatedItem.id
      loadRecipeDraft(updatedItem)
      successMessage.value = 'Item atualizado com sucesso.'
    } else {
      const createdItem = await $fetch<MenuItem>('/restaurants/menu/items', {
        method: 'POST',
        baseURL: config.public.apiBase,
        headers: getAuthHeaders(),
        body: payload
      })

      items.value = sortMenuItems([...items.value, createdItem])
      selectedRecipeItemId.value = createdItem.id
      loadRecipeDraft(createdItem)
      successMessage.value = 'Item criado com sucesso. Agora configure a receita de estoque.'
    }

    resetMenuForm()
  } catch (error) {
    errorMessage.value = getRequestErrorMessage(error, 'Nao foi possivel salvar o item.')
  } finally {
    saving.value = false
  }
}

async function saveRecipe() {
  if (!selectedRecipeItem.value) {
    errorMessage.value = 'Selecione um prato para configurar a receita.'
    return
  }

  if (recipeDraft.value.length === 0) {
    errorMessage.value = 'Adicione ao menos um item de estoque na receita.'
    return
  }

  const entries = recipeDraft.value.map((entry) => ({
    inventory_item_id: Number(entry.inventory_item_id),
    quantity_required: Number(entry.quantity_required.replace(',', '.'))
  }))

  if (entries.some((entry) => !Number.isInteger(entry.inventory_item_id) || entry.inventory_item_id <= 0)) {
    errorMessage.value = 'Selecione um item de estoque valido em cada linha da receita.'
    return
  }

  if (entries.some((entry) => !Number.isFinite(entry.quantity_required) || entry.quantity_required <= 0)) {
    errorMessage.value = 'Informe quantidades validas em toda a receita.'
    return
  }

  if (new Set(entries.map((entry) => entry.inventory_item_id)).size !== entries.length) {
    errorMessage.value = 'Nao repita o mesmo item de estoque na receita.'
    return
  }

  recipeSaving.value = true
  resetFeedback()

  const payload: RecipePayload = { entries }

  try {
    await $fetch(`/restaurants/menu/items/${selectedRecipeItem.value.id}/recipe`, {
      method: 'PUT',
      baseURL: config.public.apiBase,
      headers: getAuthHeaders(),
      body: payload
    })

    successMessage.value = 'Receita de estoque atualizada com sucesso.'
    await fetchMenuItems()
  } catch (error) {
    errorMessage.value = getRequestErrorMessage(error, 'Nao foi possivel salvar a receita.')
  } finally {
    recipeSaving.value = false
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
      resetMenuForm()
    }

    if (selectedRecipeItemId.value === itemId) {
      selectedRecipeItemId.value = null
      resetRecipeDraft()
    }

    successMessage.value = 'Item removido com sucesso.'
  } catch (error) {
    errorMessage.value = getRequestErrorMessage(error, 'Nao foi possivel remover o item.')
  } finally {
    deletingId.value = null
  }
}

await auth.initialize()
await Promise.all([fetchMenuItems(), fetchInventoryItems()])
</script>

<template>
  <div>
    <header class="page-header">
      <div>
        <span class="eyebrow">Produtos</span>
        <h1>Cardapio</h1>
        <p>Cadastre pratos e configure a receita de estoque que sera debitada a cada pedido.</p>
      </div>

      <div class="page-header-actions">
        <button class="secondary-button" type="button" :disabled="loading || inventoryLoading" @click="refreshAll">
          <Icon name="lucide:refresh-cw" aria-hidden="true" />
          Atualizar
        </button>

        <button class="primary-button" type="button" @click="openCreateDishModal">
          <Icon name="lucide:plus" aria-hidden="true" />
          Adicionar novo prato
        </button>
      </div>
    </header>

    <p v-if="errorMessage" class="menu-feedback danger-feedback">
      {{ errorMessage }}
    </p>

    <p v-if="successMessage" class="menu-feedback success-feedback">
      {{ successMessage }}
    </p>

    <section class="panel">
      <div class="panel-header">
        <div>
          <h2>Filtros do cardapio</h2>
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
    </section>

    <section class="panel table-panel">
      <div class="panel-header">
        <div>
          <h2>Itens do cardapio</h2>
          <p>Os pratos ja mostram se possuem receita de estoque configurada.</p>
        </div>
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
              <th>Receita</th>
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
                  <span
                    v-for="ingredient in item.ingredients"
                    :key="`${item.id}-${ingredient}`"
                    class="ingredient-chip"
                  >
                    {{ ingredient }}
                  </span>
                </div>
              </td>

              <td>
                <span class="status-chip" :class="item.recipe.length > 0 ? 'status-ok' : 'status-warn'">
                  {{ item.recipe.length > 0 ? `${item.recipe.length} insumo(s)` : 'Sem receita' }}
                </span>
              </td>

              <td>{{ new Date(item.updated_at).toLocaleDateString('pt-BR') }}</td>

              <td>
                <div class="table-actions">
                  <button class="secondary-button action-button" type="button" @click="openEditDishModal(item)">
                    <Icon name="lucide:pencil-line" aria-hidden="true" />
                    Editar
                  </button>

                  <button class="secondary-button action-button" type="button" @click="openRecipeModal(item)">
                    <Icon name="lucide:chef-hat" aria-hidden="true" />
                    Receita
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

    <div v-if="dishModalOpen" class="modal-overlay" @click.self="closeDishModal">
      <article class="dish-modal-card">
        <div class="dish-modal-header">
          <div>
            <span class="eyebrow">Cardapio</span>
            <h2>{{ isEditing ? 'Editar prato e receita' : 'Adicionar novo prato' }}</h2>
            <p>Cadastre o prato e configure os insumos que serao baixados do estoque.</p>
          </div>

          <button class="secondary-button modal-close-button" type="button" @click="closeDishModal">
            <Icon name="lucide:x" aria-hidden="true" />
          </button>
        </div>

        <p v-if="errorMessage" class="menu-feedback danger-feedback">
          {{ errorMessage }}
        </p>

        <p v-if="successMessage" class="menu-feedback success-feedback">
          {{ successMessage }}
        </p>

        <div class="dish-modal-grid">
          <section class="panel modal-inner-panel">
            <div class="panel-header">
              <div>
                <h2>{{ isEditing ? 'Editar prato' : 'Cadastrar prato' }}</h2>
                <p>Informe nome, preco e os ingredientes que descrevem o produto.</p>
              </div>

              <button class="secondary-button" type="button" @click="resetMenuForm">
                <Icon :name="isEditing ? 'lucide:x' : 'lucide:eraser'" aria-hidden="true" />
                {{ isEditing ? 'Cancelar edicao' : 'Limpar' }}
              </button>
            </div>

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

              <div class="form-field">
                <span>Ingredientes</span>

                <div v-if="inventoryLoading" class="menu-empty compact-empty">
                  Carregando ingredientes disponiveis...
                </div>

                <div v-else-if="availableIngredientNames.length === 0" class="menu-empty compact-empty">
                  Nenhum ingrediente cadastrado no estoque.
                  <NuxtLink to="/inventory">Cadastre os insumos em Estoque</NuxtLink>.
                </div>

                <div v-else class="ingredient-selector">
                  <label
                    v-for="ingredientName in availableIngredientNames"
                    :key="ingredientName"
                    class="ingredient-option"
                  >
                    <input v-model="form.ingredients" type="checkbox" :value="ingredientName">
                    <span>{{ ingredientName }}</span>
                  </label>
                </div>

                <div v-if="selectedIngredientsMissingFromInventory.length > 0" class="ingredient-missing-list">
                  <span
                    v-for="ingredient in selectedIngredientsMissingFromInventory"
                    :key="`missing-${ingredient}`"
                    class="status-chip status-warn"
                  >
                    {{ ingredient }} fora do estoque atual
                  </span>
                </div>
              </div>

              <div class="form-actions menu-form-actions">
                <button class="primary-button" type="submit" :disabled="saving">
                  <Icon :name="isEditing ? 'lucide:save' : 'lucide:plus'" aria-hidden="true" />
                  {{ saving ? 'Salvando...' : isEditing ? 'Salvar prato' : 'Cadastrar prato' }}
                </button>
              </div>
            </form>
          </section>

          <section class="panel modal-inner-panel">
            <div class="panel-header">
              <div>
                <h2>Receita de estoque por prato</h2>
                <p>Configure os insumos usados em cada venda do prato.</p>
              </div>
            </div>

            <div class="recipe-toolbar">
              <label class="form-field">
                <span>Prato</span>
                <select v-model="selectedRecipeItemId">
                  <option :value="null" disabled>Selecione um prato</option>
                  <option v-for="item in items" :key="item.id" :value="item.id">
                    {{ item.name }}
                  </option>
                </select>
              </label>

              <NuxtLink class="secondary-button inventory-link-button" to="/inventory">
                <Icon name="lucide:boxes" aria-hidden="true" />
                Estoque
              </NuxtLink>
            </div>

            <div v-if="selectedRecipeItem" class="recipe-editor">
              <div class="recipe-header-card">
                <strong>{{ selectedRecipeItem.name }}</strong>
                <span>{{ formatBRLFromCents(selectedRecipeItem.price_cents) }}</span>
              </div>

              <div v-if="recipeDraft.length === 0" class="recipe-empty">
                Nenhum item de estoque configurado. Adicione linhas abaixo.
              </div>

              <div v-for="(entry, index) in recipeDraft" :key="`recipe-${index}`" class="recipe-row">
                <label class="form-field">
                  <span>Item de estoque</span>
                  <select v-model="entry.inventory_item_id" :disabled="inventoryLoading">
                    <option value="" disabled>Selecione um item</option>
                    <option
                      v-for="inventoryItem in inventoryItems"
                      :key="inventoryItem.id"
                      :value="String(inventoryItem.id)"
                    >
                      {{ inventoryItem.name }} • {{ inventoryItem.quantity_available }} {{ inventoryItem.unit }}
                    </option>
                  </select>
                </label>

                <label class="form-field">
                  <span>Quantidade usada</span>
                  <input v-model="entry.quantity_required" type="text" inputmode="decimal" placeholder="1 ou 0,15">
                </label>

                <button class="secondary-button recipe-remove-button" type="button" @click="removeRecipeRow(index)">
                  <Icon name="lucide:trash-2" aria-hidden="true" />
                  Remover
                </button>
              </div>

              <div class="form-actions recipe-actions">
                <button class="secondary-button" type="button" @click="addRecipeRow">
                  <Icon name="lucide:plus" aria-hidden="true" />
                  Adicionar insumo
                </button>

                <button class="primary-button" type="button" :disabled="recipeSaving" @click="saveRecipe">
                  <Icon name="lucide:save" aria-hidden="true" />
                  {{ recipeSaving ? 'Salvando...' : 'Salvar receita' }}
                </button>
              </div>
            </div>

            <div v-else class="recipe-empty">
              Cadastre ou selecione um prato para configurar a baixa automatica de estoque.
            </div>
          </section>
        </div>
      </article>
    </div>
  </div>
</template>

<style scoped>
.page-header-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.menu-form {
  display: grid;
  gap: 16px;
}

.menu-form-grid {
  grid-template-columns: 1fr 1fr;
}

.menu-form-actions,
.recipe-actions {
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

.menu-empty,
.recipe-empty {
  padding: 18px 0 8px;
  color: var(--color-gray-500);
}

.compact-empty {
  padding: 6px 0 0;
}

.ingredient-selector {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-top: 10px;
  max-height: 220px;
  overflow: auto;
  padding-right: 4px;
}

.ingredient-option {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 42px;
  padding: 10px 12px;
  border: 1px solid var(--color-gray-200);
  border-radius: 8px;
  background: #fff;
  color: var(--color-gray-700);
  cursor: pointer;
}

.ingredient-option input {
  width: 16px;
  height: 16px;
  margin: 0;
}

.ingredient-missing-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.recipe-toolbar {
  display: flex;
  gap: 16px;
  align-items: end;
  margin-bottom: 18px;
}

.recipe-toolbar .form-field {
  flex: 1 1 auto;
}

.inventory-link-button {
  min-height: 44px;
}

.recipe-editor {
  display: grid;
  gap: 16px;
}

.recipe-header-card {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px;
  border: 1px solid var(--color-gray-200);
  border-radius: 8px;
  background: var(--color-gray-50);
}

.recipe-row {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(0, 0.9fr);
  gap: 12px;
  align-items: end;
}

.recipe-remove-button {
  min-height: 44px;
  grid-column: 1 / -1;
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

.status-warn {
  background: #fff7ed;
  color: #b45309;
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

.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: grid;
  place-items: center;
  padding: 24px;
  background: rgba(15, 23, 42, 0.46);
  backdrop-filter: blur(8px);
}

.dish-modal-card {
  width: min(1180px, 100%);
  max-height: 92vh;
  overflow: auto;
  padding: 24px;
  border: 1px solid var(--color-gray-200);
  border-radius: 20px;
  background: #ffffff;
  box-shadow: 0 28px 80px rgba(15, 23, 42, 0.24);
}

.dish-modal-header {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: flex-start;
  margin-bottom: 18px;
}

.dish-modal-header h2 {
  margin-top: 4px;
  font-size: 28px;
}

.dish-modal-header p {
  margin-top: 6px;
  color: var(--color-gray-500);
}

.modal-close-button {
  min-width: 44px;
  min-height: 44px;
  padding: 0;
}

.dish-modal-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.05fr);
  gap: 18px;
  align-items: start;
}

.modal-inner-panel {
  height: 100%;
  box-shadow: none;
}

@media (max-width: 1100px) {
  .dish-modal-grid {
    grid-template-columns: 1fr;
  }

  .dish-modal-card {
    width: min(760px, 100%);
  }
}

@media (max-width: 980px) {
  .page-header-actions,
  .menu-form-grid,
  .recipe-row {
    grid-template-columns: 1fr;
  }

  .page-header-actions,
  .recipe-toolbar,
  .menu-form-actions,
  .recipe-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .ingredient-selector {
    grid-template-columns: 1fr;
  }

  .page-header-actions .primary-button,
  .page-header-actions .secondary-button,
  .menu-form-actions .primary-button,
  .recipe-actions .primary-button,
  .recipe-actions .secondary-button,
  .inventory-link-button {
    width: 100%;
  }
}

@media (max-width: 720px) {
  .modal-overlay {
    padding: 12px;
  }

  .dish-modal-card {
    max-height: 94vh;
    padding: 18px;
    border-radius: 16px;
  }

  .dish-modal-header {
    flex-direction: column;
  }

  .modal-close-button {
    width: 100%;
  }
}
</style>