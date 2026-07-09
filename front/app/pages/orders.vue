<script setup lang="ts">
import { formatBRL } from '../data/mock'

useHead({ title: 'Pedidos' })

type OrderStatus =
  | 'pending'
  | 'preparing'
  | 'out_for_delivery'
  | 'delivered'
  | 'cancelled'

type OrderItem = {
  id: number
  restaurant_id: number
  customer_name: string
  menu_item_id?: number | null
  main_dish: string
  order_price_cents: number
  status: OrderStatus
  stock_deducted?: boolean
  notes?: string | null
  created_at: string
  updated_at: string
}

type MenuItem = {
  id: number
  restaurant_id: number
  name: string
  price_cents: number
  recipe: Array<{
    id: number
    quantity_required: number
  }>
}

type MenuItemsResponse = {
  data: MenuItem[]
  msg: string
}

type OrdersResponse = {
  data: OrderItem[]
  msg: string
  meta: {
    page: number
    pageSize: number
    total: number
    totalPages: number
  }
}

type OrderPayload = {
  customer_name: string
  main_dish: string
  price: number
  status: OrderStatus
  notes?: string
}

const config = useRuntimeConfig()
const auth = useRestaurantAuth()
const router = useRouter()

const orders = ref<OrderItem[]>([])
const menuItems = ref<MenuItem[]>([])
const loading = ref(true)
const saving = ref(false)
const menuLoading = ref(false)
const deletingId = ref<number | null>(null)
const editingOrderId = ref<number | null>(null)
const showOrderModal = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const filters = reactive({
  status: '',
  search: '',
  page: 1,
  pageSize: 10
})

const form = reactive({
  customer_name: '',
  main_dish: '',
  selected_dish: '',
  price: '49,90',
  status: 'pending' as OrderStatus,
  notes: ''
})

const isEditing = computed(() => editingOrderId.value !== null)
const ADD_MENU_ITEM_VALUE = '__add_menu_item__'

const statusOptions: Array<{ value: OrderStatus, label: string }> = [
  { value: 'pending', label: 'Pendente' },
  { value: 'preparing', label: 'Em preparo' },
  { value: 'out_for_delivery', label: 'Saiu para entrega' },
  { value: 'delivered', label: 'Entregue' },
  { value: 'cancelled', label: 'Cancelado' }
]

const pagination = reactive({
  total: 0,
  totalPages: 1
})

const filteredOrders = computed(() => {
  return orders.value
})

const orderableMenuItems = computed(() => {
  return menuItems.value.filter((item) => item.recipe.length > 0)
})

const dishOptions = computed(() => {
  const options = orderableMenuItems.value.map((item) => ({
    value: item.name,
    label: `${item.name} • ${formatBRL(item.price_cents / 100)}`
  }))

  if (
    form.main_dish
    && !orderableMenuItems.value.some((item) => item.name === form.main_dish)
  ) {
    options.unshift({
      value: form.main_dish,
      label: `${form.main_dish} • item nao encontrado ou sem receita`
    })
  }

  options.push({
    value: ADD_MENU_ITEM_VALUE,
    label: '+ Adicionar item no cardapio'
  })

  return options
})

const queueSummary = computed(() => {
  const total = pagination.total
  const preparing = orders.value.filter((order) => order.status === 'preparing').length
  const attention = orders.value.filter((order) => {
    return order.status === 'cancelled' || order.status === 'pending'
  }).length
  const averageTicket = total > 0
    ? orders.value.reduce((sum, order) => sum + order.order_price_cents, 0) / total / 100
    : 0

  return {
    total,
    preparing,
    attention,
    averageTicket
  }
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

function clearFormFields() {
  form.customer_name = ''
  form.main_dish = ''
  form.selected_dish = ''
  form.price = '49,90'
  form.status = 'pending'
  form.notes = ''
  editingOrderId.value = null
}

function resetForm() {
  clearFormFields()
  resetFeedback()
}

function fillForm(order: OrderItem) {
  form.customer_name = order.customer_name
  form.main_dish = order.main_dish
  form.selected_dish = order.main_dish
  form.price = (order.order_price_cents / 100).toFixed(2).replace('.', ',')
  form.status = order.status
  form.notes = order.notes || ''
  editingOrderId.value = order.id
  resetFeedback()
}

async function openCreateModal() {
  resetForm()
  await fetchMenuItems()
  if (orderableMenuItems.value.length === 0) {
    errorMessage.value = 'Cadastre um prato com receita de estoque antes de criar pedidos.'
  }
  showOrderModal.value = true
}

async function openEditModal(order: OrderItem) {
  fillForm(order)
  await fetchMenuItems()
  showOrderModal.value = true
}

function closeOrderModal() {
  showOrderModal.value = false
  resetForm()
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

function syncDishPrice(selectedDish: string) {
  const selectedItem = orderableMenuItems.value.find((item) => item.name === selectedDish)
  if (!selectedItem) {
    return
  }

  form.main_dish = selectedItem.name
  form.price = (selectedItem.price_cents / 100).toFixed(2).replace('.', ',')
}

async function handleDishSelection() {
  if (form.selected_dish === ADD_MENU_ITEM_VALUE) {
    closeOrderModal()
    await router.push('/menu')
    return
  }

  form.main_dish = form.selected_dish
  syncDishPrice(form.selected_dish)
}

function formatOrderStatus(status: OrderStatus) {
  const labels: Record<OrderStatus, string> = {
    pending: 'Pendente',
    preparing: 'Em preparo',
    out_for_delivery: 'Saiu para entrega',
    delivered: 'Entregue',
    cancelled: 'Cancelado'
  }

  return labels[status]
}

function toneForStatus(status: OrderStatus) {
  if (status === 'cancelled') {
    return 'red'
  }

  if (status === 'pending' || status === 'preparing') {
    return 'orange'
  }

  return 'green'
}

const isFirstPage = computed(() => filters.page <= 1)

const isLastPage = computed(() => filters.page >= pagination.totalPages)

function applyFilters() {
  filters.page = 1
  void fetchOrders()
}

function changePage(nextPage: number) {
  if (nextPage < 1 || nextPage > pagination.totalPages || nextPage === filters.page) {
    return
  }

  filters.page = nextPage
  void fetchOrders()
}

async function fetchOrders() {
  if (!auth.token.value) {
    return
  }

  loading.value = true
  resetFeedback()

  try {
    const query: Record<string, string> = {}
    if (filters.status) {
      query.status = filters.status
    }
    if (filters.search.trim()) {
      query.q = filters.search.trim()
    }
    query.page = String(filters.page)
    query.pageSize = String(filters.pageSize)

    const response = await $fetch<OrdersResponse>('/restaurants/orders', {
      baseURL: config.public.apiBase,
      headers: getAuthHeaders(),
      query
    })

    orders.value = response.data
    pagination.total = response.meta.total
    pagination.totalPages = response.meta.totalPages
    filters.page = response.meta.page
    filters.pageSize = response.meta.pageSize
  } catch (error) {
    errorMessage.value = getRequestErrorMessage(error, 'Nao foi possivel carregar os pedidos.')
  } finally {
    loading.value = false
  }
}

async function fetchMenuItems() {
  if (!auth.token.value) {
    return
  }

  menuLoading.value = true

  try {
    const response = await $fetch<MenuItemsResponse>('/restaurants/menu/items', {
      baseURL: config.public.apiBase,
      headers: getAuthHeaders()
    })

    menuItems.value = response.data
      .slice()
      .sort((left, right) => left.name.localeCompare(right.name))
  } catch (error) {
    errorMessage.value = getRequestErrorMessage(error, 'Nao foi possivel carregar o cardapio.')
  } finally {
    menuLoading.value = false
  }
}

async function submitForm() {
  const price = Number(form.price.replace(',', '.'))

  if (!form.customer_name.trim() || !form.main_dish.trim()) {
    errorMessage.value = 'Informe cliente e prato.'
    successMessage.value = ''
    return
  }

  if (!orderableMenuItems.value.some((item) => item.name === form.main_dish)) {
    errorMessage.value = 'Selecione um prato com receita de estoque configurada.'
    successMessage.value = ''
    return
  }

  if (!Number.isFinite(price) || price <= 0) {
    errorMessage.value = 'Informe um valor valido.'
    successMessage.value = ''
    return
  }

  saving.value = true
  resetFeedback()

  const payload: OrderPayload = {
    customer_name: form.customer_name.trim(),
    main_dish: form.main_dish.trim(),
    price,
    status: form.status,
    notes: form.notes.trim() || undefined
  }

  try {
    if (isEditing.value && editingOrderId.value !== null) {
      const updatedOrder = await $fetch<OrderItem>(
        `/restaurants/orders/${editingOrderId.value}`,
        {
          method: 'PATCH',
          baseURL: config.public.apiBase,
          headers: getAuthHeaders(),
          body: payload
        }
      )

      orders.value = orders.value.map((order) => {
        return order.id === updatedOrder.id ? updatedOrder : order
      })
      successMessage.value = 'Pedido atualizado com sucesso.'
    } else {
      await $fetch<OrderItem>('/restaurants/orders', {
        method: 'POST',
        baseURL: config.public.apiBase,
        headers: getAuthHeaders(),
        body: payload
      })

      filters.page = 1
      await fetchOrders()
      successMessage.value = 'Pedido criado com sucesso.'
    }

    showOrderModal.value = false
    clearFormFields()
  } catch (error) {
    errorMessage.value = getRequestErrorMessage(error, 'Nao foi possivel salvar o pedido.')
  } finally {
    saving.value = false
  }
}

async function removeOrder(orderId: number) {
  deletingId.value = orderId
  resetFeedback()

  try {
    await $fetch(`/restaurants/orders/${orderId}`, {
      method: 'DELETE',
      baseURL: config.public.apiBase,
      headers: getAuthHeaders()
    })

    const shouldGoToPreviousPage = orders.value.length === 1 && filters.page > 1
    if (shouldGoToPreviousPage) {
      filters.page -= 1
    }

    await fetchOrders()
    if (editingOrderId.value === orderId) {
      resetForm()
      showOrderModal.value = false
    }
    successMessage.value = 'Pedido removido com sucesso.'
  } catch (error) {
    errorMessage.value = getRequestErrorMessage(error, 'Nao foi possivel remover o pedido.')
  } finally {
    deletingId.value = null
  }
}

await auth.initialize()
await Promise.all([fetchOrders(), fetchMenuItems()])
</script>

<template>
  <div>
    <header class="page-header">
      <div>
        <span class="eyebrow">Operacao</span>
        <h1>Pedidos</h1>
        <p>Crie, atualize e remova pedidos reais do restaurante autenticado.</p>
      </div>
    </header>

    <section class="filters orders-filters">
      <label>
        <span>Status</span>
        <select v-model="filters.status">
          <option value="">Todos</option>
          <option v-for="option in statusOptions" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>
      </label>
      <label>
        <span>Buscar pedido</span>
        <input v-model="filters.search" type="search" placeholder="ID, cliente ou prato">
      </label>
      <div class="orders-filter-actions">
        <button class="primary-button filter-button" type="button" @click="applyFilters">
          <Icon name="lucide:search" aria-hidden="true" />
          Consultar
        </button>
        <button class="secondary-button filter-button" type="button" :disabled="loading" @click="fetchOrders">
          <Icon name="lucide:refresh-cw" aria-hidden="true" />
          Atualizar
        </button>
        <button class="primary-button filter-button" type="button" @click="openCreateModal">
          <Icon name="lucide:plus" aria-hidden="true" />
          Novo pedido
        </button>
      </div>
    </section>

    <p v-if="!showOrderModal && errorMessage" class="orders-feedback danger-feedback">
      {{ errorMessage }}
    </p>
    <p v-if="!showOrderModal && successMessage" class="orders-feedback success-feedback">
      {{ successMessage }}
    </p>

    <section class="panel">
      <div class="panel-header">
        <div>
          <h2>Resumo da fila</h2>
          <p>Indicadores em cima dos pedidos atuais carregados da API.</p>
        </div>
      </div>
      <div class="stack-list">
        <div class="summary-line">
          <span>Pedidos na lista</span>
          <strong>{{ queueSummary.total }}</strong>
        </div>
        <div class="summary-line">
          <span>Em preparo</span>
          <strong>{{ queueSummary.preparing }}</strong>
        </div>
        <div class="summary-line">
          <span>Ticket medio</span>
          <strong>{{ formatBRL(queueSummary.averageTicket) }}</strong>
        </div>
        <div class="summary-line">
          <span>Pedidos com atencao</span>
          <strong class="danger">{{ queueSummary.attention }}</strong>
        </div>
      </div>
    </section>

    <section class="panel table-panel">
      <div class="panel-header">
        <div>
          <h2>Lista de pedidos</h2>
          <p>Todos os pedidos pertencem ao restaurante autenticado.</p>
        </div>
      </div>

      <div v-if="loading" class="orders-empty">
        Carregando pedidos...
      </div>

      <div v-else-if="filteredOrders.length === 0" class="orders-empty">
        Nenhum pedido encontrado com os filtros atuais.
      </div>

      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Cliente</th>
              <th>Prato</th>
              <th>Valor</th>
              <th>Status</th>
              <th>Atualizado em</th>
              <th>Acoes</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in filteredOrders" :key="order.id">
              <td><strong>#{{ order.id }}</strong></td>
              <td>{{ order.customer_name }}</td>
              <td>{{ order.main_dish }}</td>
              <td>{{ formatBRL(order.order_price_cents / 100) }}</td>
              <td>
                <span class="status-badge" :class="toneForStatus(order.status)">
                  {{ formatOrderStatus(order.status) }}
                </span>
              </td>
              <td>{{ new Date(order.updated_at).toLocaleDateString('pt-BR') }}</td>
              <td>
                <div class="table-actions">
                  <button class="secondary-button action-button" type="button" @click="openEditModal(order)">
                    <Icon name="lucide:pencil-line" aria-hidden="true" />
                    Editar
                  </button>
                  <button
                    class="secondary-button action-button danger-button"
                    type="button"
                    :disabled="deletingId === order.id"
                    @click="removeOrder(order.id)"
                  >
                    <Icon name="lucide:trash-2" aria-hidden="true" />
                    {{ deletingId === order.id ? 'Removendo...' : 'Excluir' }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div class="pagination-bar">
          <div class="pagination-summary">
            <span>{{ pagination.total }} pedidos encontrados</span>
            <strong>Pagina {{ filters.page }} de {{ pagination.totalPages }}</strong>
          </div>
          <div class="pagination-actions">
            <button
              class="secondary-button action-button"
              type="button"
              :disabled="loading || isFirstPage"
              @click="changePage(filters.page - 1)"
            >
              <Icon name="lucide:chevron-left" aria-hidden="true" />
              Anterior
            </button>
            <button
              class="secondary-button action-button"
              type="button"
              :disabled="loading || isLastPage"
              @click="changePage(filters.page + 1)"
            >
              Proxima
              <Icon name="lucide:chevron-right" aria-hidden="true" />
            </button>
          </div>
        </div>
      </div>
    </section>

    <div v-if="showOrderModal" class="modal-overlay" @click.self="closeOrderModal">
      <article class="modal-card" role="dialog" aria-modal="true" aria-labelledby="order-modal-title">
        <div class="panel-header modal-header">
          <div>
            <h2 id="order-modal-title">
              {{ isEditing ? 'Editar pedido' : 'Adicionar novo pedido' }}
            </h2>
            <p>Cadastro real conectado ao backend do restaurante.</p>
          </div>

          <button class="secondary-button modal-close-button" type="button" aria-label="Fechar modal" @click="closeOrderModal">
            <Icon name="lucide:x" aria-hidden="true" />
          </button>
        </div>

        <p v-if="errorMessage" class="orders-feedback danger-feedback">
          {{ errorMessage }}
        </p>
        <p v-if="successMessage" class="orders-feedback success-feedback">
          {{ successMessage }}
        </p>

        <form class="orders-form" @submit.prevent="submitForm">
          <div class="form-grid orders-form-grid">
            <label class="form-field">
              <span>Cliente</span>
              <input v-model="form.customer_name" type="text" placeholder="Nome do cliente" required>
            </label>
            <label class="form-field">
              <span>Prato</span>
              <select v-model="form.selected_dish" :disabled="menuLoading" required @change="handleDishSelection">
                <option value="" disabled>
                  {{ menuLoading ? 'Carregando cardapio...' : 'Selecione um item do cardapio' }}
                </option>
                <option v-for="option in dishOptions" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
            </label>
            <label class="form-field">
              <span>Valor</span>
              <input v-model="form.price" type="text" inputmode="decimal" placeholder="54,90" required>
            </label>
            <label class="form-field">
              <span>Status</span>
              <select v-model="form.status">
                <option v-for="option in statusOptions" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
            </label>
          </div>

          <p class="dish-helper-text">
            So aparecem pratos com receita de estoque configurada. O valor pode ser ajustado antes de salvar, e a ultima opcao leva para o cadastro de itens.
          </p>

          <label class="form-field">
            <span>Observacoes</span>
            <textarea v-model="form.notes" placeholder="Sem cebola, entregar na portaria..." />
          </label>

          <div class="form-actions orders-form-actions">
            <button class="secondary-button" type="button" @click="closeOrderModal">
              Cancelar
            </button>
            <button class="primary-button" type="submit" :disabled="saving">
              <Icon :name="isEditing ? 'lucide:save' : 'lucide:plus'" aria-hidden="true" />
              {{ saving ? 'Salvando...' : isEditing ? 'Salvar pedido' : 'Adicionar pedido' }}
            </button>
          </div>
        </form>
      </article>
    </div>
  </div>
</template>

<style scoped>
.orders-form {
  display: grid;
  gap: 16px;
}

.orders-form-grid {
  grid-template-columns: 1fr 1fr;
}

.orders-form-actions {
  justify-content: space-between;
}

.orders-feedback {
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

.filters.orders-filters {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 16px;
  align-items: end;
  overflow: hidden;
}

.filters.orders-filters label {
  min-width: 0;
  max-width: 100%;
}

.filters.orders-filters input,
.filters.orders-filters select {
  width: 100%;
  max-width: 100%;
  min-width: 0;
  box-sizing: border-box;
}

.filters.orders-filters .orders-filter-actions {
  grid-column: 1 / -1;
  width: 100%;
  max-width: 100%;
  min-width: 0;
  box-sizing: border-box;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: flex-end;
  overflow: hidden;
}

.filters.orders-filters .orders-filter-actions .filter-button {
  flex: 0 1 auto;
  max-width: 100%;
  min-width: max-content;
  white-space: nowrap;
}

.orders-empty {
  padding: 18px 0 8px;
  color: var(--color-gray-500);
}

.dish-helper-text {
  margin-top: -6px;
  color: var(--color-gray-500);
  font-size: 13px;
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

.pagination-bar {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  padding-top: 16px;
}

.pagination-summary {
  display: grid;
  gap: 4px;
  color: var(--color-gray-500);
}

.pagination-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.danger-button {
  color: var(--color-red);
  border-color: #fecaca;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: rgba(15, 23, 42, 0.55);
}

.modal-card {
  width: 100%;
  max-width: 720px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 24px;
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 18px;
  background: #fff;
  box-shadow: 0 24px 80px rgba(15, 23, 42, 0.28);
}

.modal-header {
  align-items: flex-start;
  margin-bottom: 18px;
}

.modal-close-button {
  min-width: 42px;
  min-height: 42px;
  padding: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

@media (max-width: 760px) {
  .filters.orders-filters {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 980px) {
  .orders-form-grid {
    grid-template-columns: 1fr;
  }

  .filters.orders-filters .orders-filter-actions {
    flex-direction: column;
  }

  .filters.orders-filters .orders-filter-actions .filter-button,
  .orders-form-actions .primary-button,
  .orders-form-actions .secondary-button,
  .pagination-actions .action-button {
    width: 100%;
  }

  .orders-form-actions {
    flex-direction: column;
  }

  .pagination-bar,
  .pagination-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .filters.orders-filters .orders-filter-actions .filter-button {
    min-width: 0;
  }

  .modal-overlay {
    align-items: flex-start;
    padding: 12px;
  }

  .modal-card {
    padding: 18px;
    border-radius: 14px;
  }

  .modal-header {
    gap: 12px;
  }
}
</style>
