export default defineNuxtPlugin(() => {
  const auth = useRestaurantAuth()
  void auth.initialize()
})
