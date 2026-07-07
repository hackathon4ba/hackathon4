export type ChartDatum = {
  label: string
  value: number
}

export type BadgeTone = 'green' | 'orange' | 'red'

export type MockOrder = {
  id: string
  customer: string
  dish: string
  period: string
  value: number
  status: string
  badge: BadgeTone
}

export const metrics = [
  { label: 'Pedidos hoje', value: '128', detail: '+12% vs. ontem', tone: 'positive' },
  { label: 'Faturamento hoje', value: 'R$ 5.842', detail: '+8,4% no período', tone: 'positive' },
  { label: 'Ticket médio', value: 'R$ 45,64', detail: 'Meta: R$ 48,00', tone: 'neutral' },
  { label: 'Prato mais vendido', value: 'Parmegiana', detail: '34 pedidos hoje', tone: 'neutral' },
  { label: 'Tempo médio de entrega', value: '31 min', detail: '2 min acima da meta', tone: 'warning' },
  { label: 'Avaliação média', value: '4,7', detail: '92 avaliações', tone: 'positive' }
]

export const revenueByDay: ChartDatum[] = [
  { label: 'Seg', value: 3600 },
  { label: 'Ter', value: 4200 },
  { label: 'Qua', value: 3880 },
  { label: 'Qui', value: 5100 },
  { label: 'Sex', value: 5842 },
  { label: 'Sáb', value: 6900 },
  { label: 'Dom', value: 5480 }
]

export const ordersByPeriod: ChartDatum[] = [
  { label: 'Manhã', value: 22 },
  { label: 'Almoço', value: 48 },
  { label: 'Tarde', value: 18 },
  { label: 'Jantar', value: 40 }
]

export const bestDishes: ChartDatum[] = [
  { label: 'Parmegiana', value: 34 },
  { label: 'Burger da Casa', value: 28 },
  { label: 'Strogonoff', value: 22 },
  { label: 'Marmita Fit', value: 19 }
]

export const deliveryByNeighborhood: ChartDatum[] = [
  { label: 'Centro', value: 27 },
  { label: 'Jardins', value: 31 },
  { label: 'Vila Nova', value: 36 },
  { label: 'Pinheiros', value: 29 }
]

export const recentOrders: MockOrder[] = [
  { id: '#8421', customer: 'Ana Paula', dish: 'Parmegiana', period: 'Jantar', value: 54.9, status: 'Entregue', badge: 'green' },
  { id: '#8420', customer: 'Rafael Lima', dish: 'Burger da Casa', period: 'Almoço', value: 42.5, status: 'Em preparo', badge: 'orange' },
  { id: '#8419', customer: 'Carla Souza', dish: 'Strogonoff', period: 'Jantar', value: 39.9, status: 'Saiu para entrega', badge: 'green' },
  { id: '#8418', customer: 'João Pedro', dish: 'Marmita Fit', period: 'Almoço', value: 32, status: 'Atrasado', badge: 'red' },
  { id: '#8417', customer: 'Marina Alves', dish: 'Parmegiana', period: 'Jantar', value: 54.9, status: 'Entregue', badge: 'green' }
]

export const menuRows = [
  { item: 'Parmegiana', category: 'Pratos principais', price: 'R$ 54,90', sales: 34, status: 'Ativo', badge: 'green' },
  { item: 'Burger da Casa', category: 'Lanches', price: 'R$ 42,50', sales: 28, status: 'Ativo', badge: 'green' },
  { item: 'Strogonoff', category: 'Pratos principais', price: 'R$ 39,90', sales: 22, status: 'Ativo', badge: 'green' },
  { item: 'Marmita Fit', category: 'Saudável', price: 'R$ 32,00', sales: 19, status: 'Baixo estoque', badge: 'orange' }
]

export const deliveryRows = [
  { id: '#8421', courier: 'Bruno Martins', neighborhood: 'Centro', time: '27 min', status: 'Entregue', badge: 'green' },
  { id: '#8420', courier: 'Paula Nunes', neighborhood: 'Jardins', time: '31 min', status: 'Em rota', badge: 'orange' },
  { id: '#8419', courier: 'Rafael Costa', neighborhood: 'Vila Nova', time: '36 min', status: 'Atenção', badge: 'red' },
  { id: '#8418', courier: 'Larissa Alves', neighborhood: 'Pinheiros', time: '29 min', status: 'Entregue', badge: 'green' }
]

export const customerRows = [
  { name: 'Ana Paula', orders: 18, spent: 'R$ 842,40', points: 842, segment: 'VIP' },
  { name: 'Rafael Lima', orders: 14, spent: 'R$ 611,20', points: 611, segment: 'Recorrente' },
  { name: 'Carla Souza', orders: 11, spent: 'R$ 498,30', points: 498, segment: 'Recorrente' },
  { name: 'João Pedro', orders: 7, spent: 'R$ 276,90', points: 277, segment: 'Novo' }
]

export const rewardRows = [
  { reward: 'Sobremesa grátis', cost: '120 pts', redemptions: 18, status: 'Ativa', badge: 'green' },
  { reward: 'Frete grátis', cost: '180 pts', redemptions: 12, status: 'Ativa', badge: 'green' },
  { reward: 'Combo executivo', cost: '260 pts', redemptions: 7, status: 'Pausada', badge: 'orange' }
]

export const financeRows = [
  { label: 'Receita bruta', value: 'R$ 38.420', detail: '+9,8% vs. semana anterior' },
  { label: 'Taxas e repasses', value: 'R$ 4.312', detail: '11,2% da receita' },
  { label: 'Cupons usados', value: 'R$ 1.186', detail: '42 pedidos com desconto' },
  { label: 'Receita líquida', value: 'R$ 32.922', detail: 'Previsão de repasse' }
]

export const copilotInsights = [
  { title: 'Reforce o jantar', text: 'Seu pico acontece entre 19h e 21h. Deixe a equipe e os insumos prontos antes das 18h40.' },
  { title: 'Proteja a avaliação', text: 'Pedidos atrasados em Vila Nova impactam a nota. Reduza o raio nesse bairro em dias de chuva.' },
  { title: 'Venda mais Parmegiana', text: 'O prato líder tem margem alta. Crie um combo com bebida para aumentar ticket médio.' }
]

export const helpItems = [
  { title: 'Configurar cardápio', text: 'Revise disponibilidade, preço e categorias dos itens mais vendidos.' },
  { title: 'Acompanhar pedidos', text: 'Use status operacionais para priorizar preparo e entrega.' },
  { title: 'Entender recomendações', text: 'O Copilot usa padrões mockados da demo para sugerir ações simples.' }
]

export function formatBRL(value: number) {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value)
}

export function chartHeight(value: number, data: ChartDatum[]) {
  const max = Math.max(...data.map((item) => item.value))
  return `${Math.max((value / max) * 100, 8)}%`
}

export function chartWidth(value: number, data: ChartDatum[]) {
  const max = Math.max(...data.map((item) => item.value))
  return `${Math.max((value / max) * 100, 8)}%`
}
