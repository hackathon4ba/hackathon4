type RestaurantIdentity = {
  id: number
  name: string
  email: string
  phone?: string | null
  address?: string | null
  cuisine_type?: string | null
  is_active: boolean
  created_at: string
}

type RestaurantAuthPayload = {
  access_token: string
  restaurant: RestaurantIdentity
}

type RegisterRestaurantPayload = {
  name: string
  email: string
  password: string
  phone?: string
  address?: string
  cuisine_type?: string
}

type LoginRestaurantPayload = {
  email: string
  password: string
}

let initializePromise: Promise<void> | null = null

export function useRestaurantAuth() {
  const config = useRuntimeConfig()
  const tokenCookie = useCookie<string | null>('restaurant_token', {
    default: () => null,
    sameSite: 'lax'
  })
  const restaurantCookie = useCookie<RestaurantIdentity | null>('restaurant_identity', {
    default: () => null,
    sameSite: 'lax'
  })

  const token = useState<string | null>('restaurant-token', () => tokenCookie.value)
  const restaurant = useState<RestaurantIdentity | null>(
    'restaurant-identity',
    () => restaurantCookie.value
  )
  const initialized = useState<boolean>('restaurant-auth-initialized', () => false)

  function syncStorage() {
    tokenCookie.value = token.value
    restaurantCookie.value = restaurant.value
  }

  function clearSession() {
    token.value = null
    restaurant.value = null
    syncStorage()
  }

  async function fetchProfile() {
    if (!token.value) {
      clearSession()
      return null
    }

    try {
      const profile = await $fetch<RestaurantIdentity>('/restaurants/me', {
        baseURL: config.public.apiBase,
        headers: {
          Authorization: `Bearer ${token.value}`
        }
      })

      restaurant.value = profile
      syncStorage()
      return profile
    } catch (error) {
      const statusCode = typeof error === 'object' && error && 'statusCode' in error
        ? Number((error as { statusCode?: number }).statusCode)
        : undefined

      if (statusCode === 401 || statusCode === 403) {
        clearSession()
        return null
      }

      return restaurant.value
    }
  }

  async function applyAuthPayload(payload: RestaurantAuthPayload) {
    token.value = payload.access_token
    restaurant.value = payload.restaurant
    syncStorage()
    initialized.value = true
    return payload.restaurant
  }

  async function login(credentials: LoginRestaurantPayload) {
    const payload = await $fetch<RestaurantAuthPayload>('/auth/restaurants/login', {
      method: 'POST',
      baseURL: config.public.apiBase,
      body: credentials
    })

    return applyAuthPayload(payload)
  }

  async function register(data: RegisterRestaurantPayload) {
    const payload = await $fetch<RestaurantAuthPayload>('/auth/restaurants/register', {
      method: 'POST',
      baseURL: config.public.apiBase,
      body: data
    })

    return applyAuthPayload(payload)
  }

  async function initialize() {
    if (initialized.value) {
      return
    }

    if (initializePromise) {
      await initializePromise
      return
    }

    initializePromise = (async () => {
      if (token.value && !restaurant.value) {
        await fetchProfile()
      } else {
        syncStorage()
      }

      initialized.value = true
    })()

    try {
      await initializePromise
    } finally {
      initializePromise = null
    }
  }

  function logout() {
    clearSession()
    initialized.value = true
  }

  return {
    token,
    restaurant,
    initialized,
    isAuthenticated: computed(() => Boolean(token.value && restaurant.value)),
    initialize,
    fetchProfile,
    login,
    register,
    logout
  }
}
