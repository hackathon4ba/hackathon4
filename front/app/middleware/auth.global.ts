export default defineNuxtRouteMiddleware(async (to) => {
  const auth = useRestaurantAuth()

  if (!auth.initialized.value) {
    await auth.initialize()
  }

  const isPublicRoute = to.path === '/'

  if (!auth.isAuthenticated.value && !isPublicRoute) {
    return navigateTo('/')
  }

  if (auth.isAuthenticated.value && to.path === '/') {
    return navigateTo('/dashboard')
  }
})
