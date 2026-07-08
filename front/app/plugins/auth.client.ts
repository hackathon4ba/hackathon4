export default defineNuxtPlugin(async () => {
  const auth = useRestaurantAuth()
  await auth.initialize()
})
