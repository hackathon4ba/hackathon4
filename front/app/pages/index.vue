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
  <div class="auth-page">
    <section class="auth-layout">
      <aside class="auth-hero">
        <div class="hero-glow hero-glow-one" />
        <div class="hero-glow hero-glow-two" />

        <div class="hero-content">
          <div class="brand-chip">
            <Icon name="lucide:utensils" aria-hidden="true" />
            Painel do restaurante
          </div>

          <h1>Gerencie seu restaurante com mais controle e velocidade.</h1>

          <p>
            Acesse seu painel administrativo, acompanhe pedidos, dashboard e recursos inteligentes
            conectados ao backend real.
          </p>

          <div class="hero-actions">
            <button class="hero-button primary" type="button" @click="setMode('login')">
              Entrar agora
              <Icon name="lucide:arrow-right" aria-hidden="true" />
            </button>

            <button class="hero-button secondary" type="button" @click="setMode('register')">
              Criar restaurante
            </button>
          </div>
        </div>

        <div class="hero-preview">
          <div class="preview-header">
            <span />
            <span />
            <span />
          </div>

          <div class="preview-card main">
            <div>
              <small>Pedidos hoje</small>
              <strong>128</strong>
            </div>
            <Icon name="lucide:shopping-bag" aria-hidden="true" />
          </div>

          <div class="preview-grid">
            <div class="preview-card">
              <small>Receita</small>
              <strong>R$ 4.890</strong>
            </div>
            <div class="preview-card">
              <small>Avaliação</small>
              <strong>4.8</strong>
            </div>
          </div>

          <div class="preview-list">
            <div>
              <span class="status-dot" />
              Pedido #1042 em preparo
            </div>
            <div>
              <span class="status-dot green" />
              Pedido #1041 entregue
            </div>
            <div>
              <span class="status-dot orange" />
              Pedido #1040 pendente
            </div>
          </div>
        </div>

        <div class="auth-highlights">
          <article class="highlight-card">
            <Icon name="lucide:store" aria-hidden="true" />
            <div>
              <h3>Conta do restaurante</h3>
              <p>Cadastro com nome, email, telefone, endereço e tipo de cozinha.</p>
            </div>
          </article>

          <article class="highlight-card">
            <Icon name="lucide:shield-check" aria-hidden="true" />
            <div>
              <h3>JWT ativo</h3>
              <p>Sessão persistida no frontend e perfil carregado em `/restaurants/me`.</p>
            </div>
          </article>

          <article class="highlight-card">
            <Icon name="lucide:lock-keyhole" aria-hidden="true" />
            <div>
              <h3>Painel protegido</h3>
              <p>Dashboard e módulos administrativos exigem autenticação.</p>
            </div>
          </article>
        </div>
      </aside>

      <main class="auth-panel">
        <div class="auth-card">
          <div class="auth-card-header">
            <div>
              <span class="eyebrow">Acesso seguro</span>
              <h2>{{ mode === 'login' ? 'Entrar no painel' : 'Cadastrar restaurante' }}</h2>
              <p>
                {{
                  mode === 'login'
                    ? 'Entre com sua conta para acessar o dashboard.'
                    : 'Crie sua conta e acesse o painel automaticamente.'
                }}
              </p>
            </div>
          </div>

          <div class="auth-switch" role="tablist" aria-label="Modo de autenticação">
            <button
              type="button"
              class="auth-switch-button"
              :class="{ active: mode === 'login' }"
              @click="setMode('login')"
            >
              <Icon name="lucide:log-in" aria-hidden="true" />
              Entrar
            </button>

            <button
              type="button"
              class="auth-switch-button"
              :class="{ active: mode === 'register' }"
              @click="setMode('register')"
            >
              <Icon name="lucide:user-plus" aria-hidden="true" />
              Cadastrar
            </button>
          </div>

          <p v-if="errorMessage" class="auth-error">
            <Icon name="lucide:circle-alert" aria-hidden="true" />
            {{ errorMessage }}
          </p>

          <form v-if="mode === 'login'" class="auth-form" @submit.prevent="submitLogin">
            <label class="form-field modern-field">
              <span>Email</span>
              <div class="input-shell">
                <Icon name="lucide:mail" aria-hidden="true" />
                <input v-model="loginForm.email" type="email" autocomplete="email" required>
              </div>
            </label>

            <label class="form-field modern-field">
              <span>Senha</span>
              <div class="input-shell">
                <Icon name="lucide:lock" aria-hidden="true" />
                <input
                  v-model="loginForm.password"
                  type="password"
                  autocomplete="current-password"
                  required
                >
              </div>
            </label>

            <div class="demo-box">
              <Icon name="lucide:sparkles" aria-hidden="true" />
              <div>
                <strong>Conta demo</strong>
                <span>admin@empresa-demo.com / admin123</span>
              </div>
            </div>

            <button type="submit" class="submit-button" :disabled="pending">
              <Icon :name="pending ? 'lucide:loader-circle' : 'lucide:log-in'" aria-hidden="true" />
              {{ pending ? 'Entrando...' : 'Entrar no painel' }}
            </button>
          </form>

          <form v-else class="auth-form" @submit.prevent="submitRegister">
            <div class="form-grid auth-form-grid">
              <label class="form-field modern-field">
                <span>Nome do restaurante</span>
                <div class="input-shell">
                  <Icon name="lucide:store" aria-hidden="true" />
                  <input v-model="registerForm.name" type="text" autocomplete="organization" required>
                </div>
              </label>

              <label class="form-field modern-field">
                <span>Email</span>
                <div class="input-shell">
                  <Icon name="lucide:mail" aria-hidden="true" />
                  <input v-model="registerForm.email" type="email" autocomplete="email" required>
                </div>
              </label>

              <label class="form-field modern-field">
                <span>Senha</span>
                <div class="input-shell">
                  <Icon name="lucide:lock" aria-hidden="true" />
                  <input
                    v-model="registerForm.password"
                    type="password"
                    autocomplete="new-password"
                    minlength="6"
                    required
                  >
                </div>
              </label>

              <label class="form-field modern-field">
                <span>Telefone</span>
                <div class="input-shell">
                  <Icon name="lucide:phone" aria-hidden="true" />
                  <input v-model="registerForm.phone" type="text" autocomplete="tel">
                </div>
              </label>

              <label class="form-field modern-field">
                <span>Tipo de cozinha</span>
                <div class="input-shell">
                  <Icon name="lucide:chef-hat" aria-hidden="true" />
                  <input v-model="registerForm.cuisine_type" type="text" placeholder="Brasileira">
                </div>
              </label>

              <label class="form-field modern-field">
                <span>Endereço</span>
                <div class="input-shell">
                  <Icon name="lucide:map-pin" aria-hidden="true" />
                  <input v-model="registerForm.address" type="text" autocomplete="street-address">
                </div>
              </label>
            </div>

            <button type="submit" class="submit-button" :disabled="pending">
              <Icon :name="pending ? 'lucide:loader-circle' : 'lucide:store'" aria-hidden="true" />
              {{ pending ? 'Cadastrando...' : 'Criar conta e entrar' }}
            </button>
          </form>
        </div>
      </main>
    </section>
  </div>
</template>

<style scoped>
.auth-page {
  height: 100vh;
  max-height: 100vh;
  display: grid;
  align-items: start;
  justify-items: center;
  padding: 16px 28px 0;
  box-sizing: border-box;
  overflow: hidden;
}

.auth-layout {
  width: 100%;
  max-width: 1180px;
  height: calc(100vh - 16px);
  max-height: calc(100vh - 16px);
  display: grid;
  grid-template-columns: minmax(0, 1.08fr) minmax(360px, 0.82fr);
  gap: 22px;
  align-items: stretch;
}

.auth-hero {
  position: relative;
  overflow: hidden;
  display: grid;
  gap: 20px;
  align-content: space-between;
  height: 100%;
  min-height: 0;
  padding: 30px;
  border: 1px solid #ffd1d6;
  border-radius: 28px;
  background:
    radial-gradient(circle at 20% 15%, rgba(234, 29, 44, 0.22), transparent 28%),
    radial-gradient(circle at 90% 20%, rgba(255, 122, 89, 0.24), transparent 32%),
    linear-gradient(135deg, #fff 0%, #fff6f6 44%, #ffecef 100%);
  box-shadow: 0 24px 80px rgba(234, 29, 44, 0.12);
}

.hero-glow {
  position: absolute;
  border-radius: 999px;
  filter: blur(8px);
  opacity: 0.8;
  pointer-events: none;
}

.hero-glow-one {
  width: 210px;
  height: 210px;
  right: -70px;
  top: 90px;
  background: rgba(234, 29, 44, 0.14);
}

.hero-glow-two {
  width: 180px;
  height: 180px;
  left: 44%;
  bottom: 120px;
  background: rgba(255, 178, 119, 0.22);
}

.hero-content,
.hero-preview,
.auth-highlights {
  position: relative;
  z-index: 1;
}

.brand-chip {
  width: fit-content;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border: 1px solid rgba(234, 29, 44, 0.18);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.72);
  color: var(--color-red);
  font-size: 13px;
  font-weight: 800;
  box-shadow: 0 12px 30px rgba(234, 29, 44, 0.08);
}

.auth-hero h1 {
  max-width: 640px;
  margin-top: 18px;
  font-size: clamp(36px, 4.8vw, 58px);
  line-height: 0.95;
  letter-spacing: -0.06em;
  color: #18181b;
}

.auth-hero p {
  max-width: 560px;
  margin-top: 14px;
  color: var(--color-gray-700);
  font-size: 16px;
  line-height: 1.6;
}

.hero-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 22px;
}

.hero-button {
  min-height: 46px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 0 18px;
  border-radius: 999px;
  font-weight: 800;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

.hero-button:hover {
  transform: translateY(-2px);
}

.hero-button.primary {
  border: 0;
  background: var(--color-red);
  color: white;
  box-shadow: 0 16px 32px rgba(234, 29, 44, 0.28);
}

.hero-button.secondary {
  border: 1px solid #ffd1d6;
  background: rgba(255, 255, 255, 0.76);
  color: #18181b;
}

.hero-preview {
  max-width: 460px;
  padding: 14px;
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.72);
  box-shadow: 0 28px 80px rgba(24, 24, 27, 0.12);
  backdrop-filter: blur(18px);
}

.preview-header {
  display: flex;
  gap: 7px;
  margin-bottom: 12px;
}

.preview-header span {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: #fecaca;
}

.preview-card {
  display: grid;
  gap: 4px;
  padding: 14px;
  border: 1px solid #f1f1f1;
  border-radius: 18px;
  background: #ffffff;
}

.preview-card.main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #ea1d2c 0%, #ff5a66 100%);
  color: white;
}

.preview-card small {
  color: inherit;
  opacity: 0.72;
  font-weight: 700;
}

.preview-card strong {
  font-size: 23px;
  letter-spacing: -0.03em;
}

.preview-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 10px;
}

.preview-list {
  display: grid;
  gap: 8px;
  margin-top: 10px;
}

.preview-list div {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 11px;
  border-radius: 14px;
  background: #fff8f8;
  color: var(--color-gray-700);
  font-size: 13px;
  font-weight: 700;
}

.status-dot {
  width: 9px;
  height: 9px;
  border-radius: 999px;
  background: var(--color-red);
}

.status-dot.green {
  background: #16a34a;
}

.status-dot.orange {
  background: #f97316;
}

.auth-highlights {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.highlight-card {
  display: flex;
  gap: 10px;
  padding: 14px;
  border: 1px solid rgba(234, 29, 44, 0.12);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.66);
  backdrop-filter: blur(12px);
}

.highlight-card svg {
  flex: 0 0 auto;
  color: var(--color-red);
}

.highlight-card h3 {
  font-size: 14px;
  color: #18181b;
}

.highlight-card p {
  margin-top: 4px;
  color: var(--color-gray-600);
  font-size: 12px;
  line-height: 1.4;
}

.auth-panel {
  display: grid;
  align-items: center;
  min-height: 0;
}

.auth-card {
  width: 100%;
  padding: 24px;
  border: 1px solid var(--color-gray-200);
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 24px 80px rgba(24, 24, 27, 0.10);
  box-sizing: border-box;
}

.auth-card-header {
  margin-bottom: 16px;
}

.auth-card-header h2 {
  margin-top: 6px;
  font-size: 30px;
  letter-spacing: -0.04em;
}

.auth-card-header p {
  margin-top: 8px;
  color: var(--color-gray-600);
  line-height: 1.5;
}

.auth-switch {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  padding: 8px;
  border: 1px solid var(--color-gray-200);
  border-radius: 18px;
  background: var(--color-gray-50);
}

.auth-switch-button {
  min-height: 46px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: 0;
  border-radius: 14px;
  background: transparent;
  color: var(--color-gray-700);
  font-weight: 800;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease, box-shadow 0.2s ease;
}

.auth-switch-button.active {
  background: #ffffff;
  color: var(--color-red);
  box-shadow: 0 10px 24px rgba(24, 24, 27, 0.08);
}

.auth-error {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 14px;
  padding: 14px 16px;
  border: 1px solid #fecaca;
  border-radius: 16px;
  background: #fff1f2;
  color: #b42318;
  font-size: 14px;
  font-weight: 800;
}

.auth-form {
  display: grid;
  gap: 14px;
  margin-top: 16px;
}

.auth-form-grid {
  grid-template-columns: 1fr 1fr;
}

.modern-field {
  display: grid;
  gap: 8px;
}

.modern-field span {
  color: #27272a;
  font-size: 13px;
  font-weight: 800;
}

.input-shell {
  min-height: 48px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 14px;
  border: 1px solid var(--color-gray-200);
  border-radius: 16px;
  background: #ffffff;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.input-shell:focus-within {
  border-color: rgba(234, 29, 44, 0.5);
  box-shadow: 0 0 0 4px rgba(234, 29, 44, 0.10);
}

.input-shell svg {
  flex: 0 0 auto;
  color: var(--color-gray-500);
}

.input-shell input {
  width: 100%;
  min-width: 0;
  border: 0;
  outline: 0;
  background: transparent;
  color: #18181b;
  font-size: 15px;
}

.input-shell input::placeholder {
  color: var(--color-gray-400);
}

.demo-box {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  border: 1px dashed rgba(234, 29, 44, 0.28);
  border-radius: 16px;
  background: #fff7f7;
  color: var(--color-gray-700);
}

.demo-box svg {
  color: var(--color-red);
}

.demo-box div {
  display: grid;
  gap: 2px;
}

.demo-box strong {
  color: #18181b;
  font-size: 14px;
}

.demo-box span {
  font-size: 13px;
}

.submit-button {
  min-height: 50px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  margin-top: 4px;
  border: 0;
  border-radius: 16px;
  background: var(--color-red);
  color: #ffffff;
  font-weight: 900;
  cursor: pointer;
  box-shadow: 0 18px 36px rgba(234, 29, 44, 0.26);
  transition: transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease;
}

.submit-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 22px 42px rgba(234, 29, 44, 0.32);
}

.submit-button:disabled {
  cursor: not-allowed;
  opacity: 0.72;
}

@media (max-width: 1180px) {
  .auth-page {
    height: auto;
    min-height: 100vh;
    max-height: none;
    overflow: visible;
    padding: 20px;
  }

  .auth-layout {
    max-width: 760px;
    height: auto;
    max-height: none;
    grid-template-columns: 1fr;
  }

  .auth-hero {
    height: auto;
    min-height: auto;
  }

  .auth-highlights {
    grid-template-columns: 1fr;
  }

  .auth-panel {
    align-items: stretch;
  }
}

@media (max-width: 720px) {
  .auth-page {
    padding: 14px;
  }

  .auth-layout {
    gap: 16px;
  }

  .auth-hero,
  .auth-card {
    padding: 18px;
    border-radius: 22px;
  }

  .auth-hero h1 {
    font-size: clamp(32px, 11vw, 44px);
  }

  .auth-hero p {
    font-size: 15px;
  }

  .hero-actions,
  .hero-button {
    width: 100%;
  }

  .preview-grid,
  .auth-form-grid,
  .auth-switch {
    grid-template-columns: 1fr;
  }

  .auth-card-header h2 {
    font-size: 26px;
  }
}
</style>