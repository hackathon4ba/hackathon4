<script setup lang="ts">
useHead({ title: 'Acesso do restaurante' })

type AuthMode = 'login' | 'register'

const auth = useRestaurantAuth()
const router = useRouter()

const mode = ref<AuthMode>('login')
const pending = ref(false)
const errorMessage = ref('')

const loginForm = reactive({
  email: 'admin@empresa-demo.com',
  password: 'admin123'
})

const registerForm = reactive({
  name: '',
  email: '',
  password: '',
  phone: '',
  address: '',
  cuisine_type: ''
})

function setMode(nextMode: AuthMode) {
  mode.value = nextMode
  errorMessage.value = ''
}

function getRequestErrorMessage(error: unknown) {
  const fallback = 'Nao foi possivel concluir a autenticacao.'

  if (error && typeof error === 'object' && 'data' in error) {
    const message = (error as { data?: { msg?: string } }).data?.msg
    if (message) {
      return message
    }
  }

  return fallback
}

async function submitLogin() {
  pending.value = true
  errorMessage.value = ''

  try {
    await auth.login({
      email: loginForm.email,
      password: loginForm.password
    })
    await router.push('/dashboard')
  } catch (error) {
    errorMessage.value = getRequestErrorMessage(error)
  } finally {
    pending.value = false
  }
}

async function submitRegister() {
  pending.value = true
  errorMessage.value = ''

  try {
    await auth.register({
      name: registerForm.name,
      email: registerForm.email,
      password: registerForm.password,
      phone: registerForm.phone || undefined,
      address: registerForm.address || undefined,
      cuisine_type: registerForm.cuisine_type || undefined
    })
    await router.push('/dashboard')
  } catch (error) {
    errorMessage.value = getRequestErrorMessage(error)
  } finally {
    pending.value = false
  }
}
</script>

<template>
  <div class="auth-layout">
    <section class="auth-hero">
      <div>
        <span class="eyebrow">Painel do restaurante</span>
        <h1>Acesse e conecte seu restaurante ao backend real.</h1>
        <p>
          O frontend agora usa o cadastro e login do Flask para liberar o painel administrativo.
        </p>
      </div>

      <div class="auth-highlights">
        <article class="home-card">
          <h3>Conta do restaurante</h3>
          <p>Cadastro com nome, email, telefone, endereco e tipo de cozinha.</p>
        </article>
        <article class="home-card">
          <h3>JWT ativo</h3>
          <p>Sessao persistida no frontend e perfil carregado em `/restaurants/me`.</p>
        </article>
        <article class="home-card">
          <h3>Painel protegido</h3>
          <p>Rotas administrativas exigem autenticacao antes de abrir dashboard e modulos.</p>
        </article>
      </div>
    </section>

    <section class="auth-panel">
      <div class="auth-switch" role="tablist" aria-label="Modo de autenticacao">
        <button
          type="button"
          class="auth-switch-button"
          :class="{ active: mode === 'login' }"
          @click="setMode('login')"
        >
          Entrar
        </button>
        <button
          type="button"
          class="auth-switch-button"
          :class="{ active: mode === 'register' }"
          @click="setMode('register')"
        >
          Cadastrar restaurante
        </button>
      </div>

      <p v-if="errorMessage" class="auth-error">
        {{ errorMessage }}
      </p>

      <form v-if="mode === 'login'" class="panel auth-form" @submit.prevent="submitLogin">
        <div class="panel-header">
          <div>
            <h2>Login do restaurante</h2>
            <p>Use o email cadastrado no backend.</p>
          </div>
        </div>

        <div class="form-grid auth-form-grid">
          <label class="form-field">
            <span>Email</span>
            <input v-model="loginForm.email" type="email" autocomplete="email" required>
          </label>
          <label class="form-field">
            <span>Senha</span>
            <input
              v-model="loginForm.password"
              type="password"
              autocomplete="current-password"
              required
            >
          </label>
        </div>

        <div class="form-actions">
          <button type="submit" class="primary-button" :disabled="pending">
            <Icon name="lucide:log-in" aria-hidden="true" />
            {{ pending ? 'Entrando...' : 'Entrar no painel' }}
          </button>
        </div>
      </form>

      <form v-else class="panel auth-form" @submit.prevent="submitRegister">
        <div class="panel-header">
          <div>
            <h2>Cadastro do restaurante</h2>
            <p>Cria a conta e autentica no painel na mesma resposta do backend.</p>
          </div>
        </div>

        <div class="form-grid auth-form-grid">
          <label class="form-field">
            <span>Nome do restaurante</span>
            <input v-model="registerForm.name" type="text" autocomplete="organization" required>
          </label>
          <label class="form-field">
            <span>Email</span>
            <input v-model="registerForm.email" type="email" autocomplete="email" required>
          </label>
          <label class="form-field">
            <span>Senha</span>
            <input
              v-model="registerForm.password"
              type="password"
              autocomplete="new-password"
              minlength="6"
              required
            >
          </label>
          <label class="form-field">
            <span>Telefone</span>
            <input v-model="registerForm.phone" type="text" autocomplete="tel">
          </label>
          <label class="form-field">
            <span>Tipo de cozinha</span>
            <input v-model="registerForm.cuisine_type" type="text" placeholder="Brasileira">
          </label>
          <label class="form-field">
            <span>Endereco</span>
            <input v-model="registerForm.address" type="text" autocomplete="street-address">
          </label>
        </div>

        <div class="form-actions">
          <button type="submit" class="primary-button" :disabled="pending">
            <Icon name="lucide:store" aria-hidden="true" />
            {{ pending ? 'Cadastrando...' : 'Criar conta e entrar' }}
          </button>
        </div>
      </form>
    </section>
  </div>
</template>

<style scoped>
.auth-layout {
  min-height: calc(100vh - 96px);
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(420px, 0.9fr);
  gap: 24px;
  align-items: stretch;
}

.auth-hero {
  display: grid;
  gap: 24px;
  align-content: start;
  padding: 36px;
  border: 1px solid #ffd5d8;
  border-radius: 8px;
  background:
    radial-gradient(circle at top right, rgb(234 29 44 / 14%), transparent 36%),
    linear-gradient(180deg, #ffffff 0%, #fff5f5 100%);
}

.auth-hero h1 {
  max-width: 640px;
  font-size: clamp(38px, 6vw, 62px);
}

.auth-hero p {
  max-width: 560px;
  margin-top: 12px;
  color: var(--color-gray-700);
  font-size: 18px;
  line-height: 1.6;
}

.auth-highlights {
  display: grid;
  gap: 16px;
}

.auth-panel {
  display: grid;
  align-content: start;
  gap: 16px;
}

.auth-switch {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  padding: 8px;
  border: 1px solid var(--color-gray-200);
  border-radius: 8px;
  background: var(--color-gray-50);
}

.auth-switch-button {
  min-height: 44px;
  border: 0;
  border-radius: 6px;
  background: transparent;
  color: var(--color-gray-700);
  font-weight: 700;
}

.auth-switch-button.active {
  background: #ffffff;
  color: var(--color-red);
  box-shadow: var(--shadow-soft);
}

.auth-form {
  padding: 24px;
}

.auth-form-grid {
  grid-template-columns: 1fr 1fr;
}

.auth-error {
  padding: 14px 16px;
  border: 1px solid #fecaca;
  border-radius: 8px;
  background: #fff1f2;
  color: #b42318;
  font-size: 14px;
  font-weight: 700;
}

@media (max-width: 1100px) {
  .auth-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .auth-hero,
  .auth-form {
    padding: 20px;
  }

  .auth-form-grid {
    grid-template-columns: 1fr;
  }

  .auth-switch {
    grid-template-columns: 1fr;
  }
}
</style>
