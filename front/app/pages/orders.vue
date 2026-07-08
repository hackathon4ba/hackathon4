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
  main_dish: string
  order_price_cents: number
  status: OrderStatus
  notes?: string | null
  created_at: string
  updated_at: string
}

type OrdersResponse = {
  data: OrderItem[]
  msg: string
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

const orders = ref<OrderItem[]>([])
const loading = ref(true)
const saving = ref(false)
const deletingId = ref<number | null>(null)
const editingOrderId = ref<number | null>(null)
const errorMessage = ref('')
const successMessage = ref('')

const filters = reactive({
  status: '',
  search: ''
})

const form = reactive({
  customer_name: '',
  main_dish: '',
  price: '49,90',
  status: 'pending' as OrderStatus,
  notes: ''
})

const isEditing = computed(() => editingOrderId.value !== null)

const statusOptions: Array<{ value: OrderStatus, label: string }> = [
  { value: 'pending', label: 'Pendente' },
  { value: 'preparing', label: 'Em preparo' },
  { value: 'out_for_delivery', label: 'Saiu para entrega' },
  { value: 'delivered', label: 'Entregue' },
  { value: 'cancelled', label: 'Cancelado' }
]

const filteredOrders = computed(() => {
  const search = filters.search.trim().toLowerCase()
  const status = filters.status

  return orders.value.filter((order) => {
    const matchesStatus = !status || order.status === status
    const matchesSearch = !search
      || order.customer_name.toLowerCase().includes(search)
      || order.main_dish.toLowerCase().includes(search)
      || String(order.id).includes(search)

    return matchesStatus && matchesSearch
  })
})

const queueSummary = computed(() => {
  const total = orders.value.length
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

function resetForm() {
  form.customer_name = ''
  form.main_dish = ''
  form.price = '49,90'
  form.status = 'pending'
  form.notes = ''
  editingOrderId.value = null
  resetFeedback()
}

function fillForm(order: OrderItem) {
  form.customer_name = order.customer_name
  form.main_dish = order.main_dish
  form.price = (order.order_price_cents / 100).toFixed(2).replace('.', ',')
  form.status = order.status
  form.notes = order.notes || ''
  editingOrderId.value = order.id
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

    const response = await $fetch<OrdersResponse>('/restaurants/orders', {
      baseURL: config.public.apiBase,
      headers: getAuthHeaders(),
      query
    })

    orders.value = response.data
  } catch (error) {
    errorMessage.value = getRequestErrorMessage(error, 'Nao foi possivel carregar os pedidos.')
  } finally {
    loading.value = false
  }
}

async function submitForm() {
  const price = Number(form.price.replace(',', '.'))

  if (!form.customer_name.trim() || !form.main_dish.trim()) {
    errorMessage.value = 'Informe cliente e prato.'
    return
  }

  if (!Number.isFinite(price) || price <= 0) {
    errorMessage.value = 'Informe um valor valido.'
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
      const createdOrder = await $fetch<OrderItem>('/restaurants/orders', {
        method: 'POST',
        baseURL: config.public.apiBase,
        headers: getAuthHeaders(),
        body: payload
      })

      orders.value = [createdOrder, ...orders.value]
      successMessage.value = 'Pedido criado com sucesso.'
    }

    resetForm()
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

    orders.value = orders.value.filter((order) => order.id !== orderId)
    if (editingOrderId.value === orderId) {
      resetForm()
    }
    successMessage.value = 'Pedido removido com sucesso.'
  } catch (error) {
    errorMessage.value = getRequestErrorMessage(error, 'Nao foi possivel remover o pedido.')
  } finally {
    deletingId.value = null
  }
}

await auth.initialize()
await fetchOrders()
</script>

<template>
  <div>
    <header class="page-header">
      <div>
        <span class="eyebrow">Operacao</span>
        <h1>Pedidos</h1>
        <p>Crie, atualize e remova pedidos reais do restaurante autenticado.</p>
      </div>

      <button class="secondary-button" type="button" @click="resetForm">
        <Icon :name="isEditing ? 'lucide:plus' : 'lucide:eraser'" aria-hidden="true" />
        {{ isEditing ? 'Novo pedido' : 'Limpar formulario' }}
      </button>
    </header>

    <section class="filters">
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
        <button class="primary-button filter-button" type="button" @click="fetchOrders">
          <Icon name="lucide:search" aria-hidden="true" />
          Consultar
        </button>
        <button class="secondary-button filter-button" type="button" :disabled="loading" @click="fetchOrders">
          <Icon name="lucide:refresh-cw" aria-hidden="true" />
          Atualizar
        </button>
      </div>
    </section>

    <section class="two-column-grid">
      <article class="panel">
        <div class="panel-header">
          <div>
            <h2>{{ isEditing ? 'Editar pedido' : 'Adicionar novo pedido' }}</h2>
            <p>Cadastro real conectado ao backend do restaurante.</p>
          </div>
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
              <input v-model="form.main_dish" type="text" placeholder="Ex: Parmegiana" required>
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

          <label class="form-field">
            <span>Observacoes</span>
            <textarea v-model="form.notes" placeholder="Sem cebola, entregar na portaria..." />
          </label>

          <div class="form-actions orders-form-actions">
            <button v-if="isEditing" class="secondary-button" type="button" @click="resetForm">
              Cancelar edicao
            </button>
            <button class="primary-button" type="submit" :disabled="saving">
              <Icon :name="isEditing ? 'lucide:save' : 'lucide:plus'" aria-hidden="true" />
              {{ saving ? 'Salvando...' : isEditing ? 'Salvar pedido' : 'Adicionar pedido' }}
            </button>
          </div>
        </form>
      </article>

      <article class="panel">
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
      </article>
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
                  <button class="secondary-button action-button" type="button" @click="fillForm(order)">
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
      </div>
    </section>
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

.orders-filter-actions {
  display: flex;
  gap: 12px;
}

.orders-empty {
  padding: 18px 0 8px;
  color: var(--color-gray-500);
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
  .orders-form-grid {
    grid-template-columns: 1fr;
  }

  .orders-filter-actions {
    flex-direction: column;
  }

  .orders-filter-actions .filter-button,
  .orders-form-actions .primary-button,
  .orders-form-actions .secondary-button {
    width: 100%;
  }

  .orders-form-actions {
    flex-direction: column;
  }
}
</style>
