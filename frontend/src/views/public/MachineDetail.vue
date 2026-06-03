<template>
  <PublicLayout>
    <div v-if="isLoading" class="max-w-[1200px] mx-auto px-6 py-16 sm:py-24 space-y-12 animate-pulse">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-12">
        <BaseSkeleton height="xl" class="rounded-2xl aspect-[4/3]" />
        <div class="space-y-6">
          <BaseSkeleton height="sm" class="w-1/3" />
          <BaseSkeleton height="lg" class="w-full" />
          <BaseSkeleton height="md" class="w-3/4" />
        </div>
      </div>
    </div>

    <div v-else-if="error" class="max-w-[1200px] mx-auto px-6 py-20 text-center">
      <div class="p-8 bg-danger/5 border border-danger/20 rounded-2xl text-danger font-medium max-w-2xl mx-auto">
        {{ error }}
      </div>
    </div>

    <div v-else-if="machine" class="max-w-[1200px] mx-auto px-6 py-16 sm:py-24 space-y-16">
      
      <div class="text-left">
        <router-link 
          to="/machines" 
          class="group inline-flex items-center gap-2.5 px-4 py-2 rounded-xl border border-border/60 bg-surface/50 text-[10px] font-mono uppercase tracking-widest text-text-muted hover:text-primary hover:border-primary/40 hover:bg-surface transition-all duration-200 select-none shadow-sm"
        >
          <svg class="w-4 h-4 transition-transform duration-200 group-hover:-translate-x-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="19" y1="12" x2="5" y2="12"></line>
            <polyline points="12 19 5 12 12 5"></polyline>
          </svg>
          Назад в каталог
        </router-link>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-start">
        
        <div class="space-y-4 max-w-[550px] lg:max-w-none mx-auto w-full">
          <div class="relative w-full aspect-[4/3] bg-surface border border-border/60 rounded-2xl overflow-hidden flex items-center justify-center group/main shadow-md">
            <img 
              v-if="machine.image_urls && machine.image_urls.length > 0" 
              :src="activeImage || machine.image_urls[0]" 
              :alt="machine.title"
              class="w-full h-full object-cover transition-all duration-300"
            >
            <div v-else class="text-border/40">
              <svg class="w-24 h-24 stroke-current" viewBox="0 0 24 24" fill="none" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="18" cy="18" r="3" />
                <circle cx="6" cy="18" r="2" />
                <path d="M6 16h12" />
                <path d="M8 16V10h6v6" />
                <path d="M14 10l2 3h2v3" />
                <path d="M10 10V8h1" />
              </svg>
            </div>

            <button 
              v-if="machine.image_urls && machine.image_urls.length > 1"
              @click.stop.prevent="prevImage"
              class="absolute left-4 w-10 h-10 rounded-full bg-surface/85 border border-border/50 flex items-center justify-center cursor-pointer opacity-0 group-hover/main:opacity-100 select-none shadow-md group/btn hover:bg-surface active:scale-95 transition-all duration-200"
            >
              <svg class="w-5 h-5 text-primary group-hover/btn:text-accent transition-colors" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <polyline points="15 18 9 12 15 6"/>
              </svg>
            </button>

            <button 
              v-if="machine.image_urls && machine.image_urls.length > 1"
              @click.stop.prevent="nextImage"
              class="absolute right-4 w-10 h-10 rounded-full bg-surface/85 border border-border/50 flex items-center justify-center cursor-pointer opacity-0 group-hover/main:opacity-100 select-none shadow-md group/btn hover:bg-surface active:scale-95 transition-all duration-200"
            >
              <svg class="w-5 h-5 text-primary group-hover/btn:text-accent transition-colors" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <polyline points="9 18 15 12 9 6"/>
              </svg>
            </button>
          </div>
          
          <div v-if="machine.image_urls && machine.image_urls.length > 1" class="flex gap-3 overflow-x-auto pb-2 select-none">
            <div 
              v-for="(img, idx) in machine.image_urls" 
              :key="idx" 
              @click="activeImage = img"
              class="w-20 h-16 rounded-lg border overflow-hidden cursor-pointer shrink-0 transition-all duration-200"
              :class="[(activeImage === img || (!activeImage && idx === 0)) ? 'border-accent shadow-[0_0_15px_rgba(176,141,87,0.2)] scale-102' : 'border-border hover:border-text-muted']"
            >
              <img :src="img" class="w-full h-full object-cover">
            </div>
          </div>
        </div>

        <div class="space-y-6 text-left lg:pl-4">
          <div 
            class="inline-block px-3.5 py-1.5 rounded-full text-[10px] font-bold uppercase tracking-widest font-mono border transition-colors select-none"
            :class="[
              machine.is_available 
                ? 'bg-primary/5 border-primary/20 text-primary' 
                : 'bg-orange-500/5 border-orange-500/20 text-orange-600'
            ]"
          >
            {{ machine.is_available ? 'В наличии' : 'Под заказ' }}
          </div>
          
          <h1 class="text-3xl sm:text-4xl font-extrabold text-primary uppercase tracking-wider leading-tight">
            {{ machine.title }}
          </h1>
          
          <div v-if="machine.price" class="text-3xl font-black text-accent font-mono border-b border-border/50 pb-4">
            {{ formatPrice(machine.price) }}
          </div>
          <div v-else class="text-lg font-bold text-text-muted border-b border-border/50 pb-4">
            Цена по запросу
          </div>

          <p class="text-text-main text-sm sm:text-base leading-relaxed normal-case whitespace-pre-wrap">
            {{ machine.description || 'Описание техники временно отсутствует.' }}
          </p>

          <div class="pt-4">
            <BaseButton @click="openLeadModal" variant="primary" class="w-full sm:w-auto">
              Заказать консультацию
            </BaseButton>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-6 border-t border-border/40 text-xs text-text-muted">
            <div class="flex items-center gap-2.5">
              <svg class="w-4 h-4 text-accent shrink-0" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              <span>Официальная гарантия 2 года</span>
            </div>
            <div class="flex items-center gap-2.5">
              <svg class="w-4 h-4 text-accent shrink-0" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              <span>Ввод в эксплуатацию за 48ч</span>
            </div>
            <div class="flex items-center gap-2.5">
              <svg class="w-4 h-4 text-accent shrink-0" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              <span>Лизинг и Trade-in программы</span>
            </div>
            <div class="flex items-center gap-2.5">
              <svg class="w-4 h-4 text-accent shrink-0" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              <span>Пожизненный сервис 24/7</span>
            </div>
          </div>
        </div>

      </div>

      <div v-if="hasSpecifications" class="space-y-6 text-left border-t border-border/50 pt-12">
        <div class="space-y-2">
          <div class="inline-flex items-center gap-2 text-accent font-bold uppercase tracking-widest font-mono text-[10px]">
            <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
            </svg>
            Спецификация
          </div>
          <h3 class="text-xl sm:text-2xl font-extrabold text-primary uppercase tracking-widest">
            Технические характеристики
          </h3>
          <div class="w-12 h-0.5 bg-accent"></div>
        </div>
        
        <div class="border border-border/80 rounded-2xl overflow-hidden bg-surface max-w-2xl font-mono text-xs shadow-md">
          <table class="w-full text-left border-collapse">
            <tbody>
              <tr 
                v-for="(val, key) in machine.specifications" 
                :key="key" 
                class="border-b border-border/30 last:border-0 odd:bg-primary/[0.01] hover:bg-primary/[0.04] transition-colors"
              >
                <td class="p-4 text-text-muted font-bold w-1/2 uppercase tracking-wider border-r border-border/30">{{ key }}</td>
                <td class="p-4 text-text-main w-1/2 font-semibold">{{ val }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>

    <!-- Модальное окно заказа -->
    <BaseModal :show="isLeadModalVisible" @close="closeLeadModal">
      <LeadForm flat />
    </BaseModal>
  </PublicLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { config } from '@/config'
import { useApi } from '@/composables/useApi'
import { useModal } from '@/composables/useModal'

import PublicLayout from '@/layouts/PublicLayout.vue'
import BaseSkeleton from '@/components/ui/BaseSkeleton.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import LeadForm from '@/components/forms/LeadForm.vue'

const route = useRoute()
const machine = ref(null)
const activeImage = ref(null)

const { isVisible: isLeadModalVisible, open: openLeadModal, close: closeLeadModal } = useModal()

const { execute, isLoading, error } = useApi(async (id) => {
  const res = await fetch(`${config.apiUrl}/api/v1/machines/${id}`)
  if (!res.ok) throw new Error("Не удалось загрузить детальную карточку техники")
  return await res.json() // вернет { status: "ok", data: Machine }
})

async function fetchMachineDetail() {
  const machineId = route.params.id
  const res = await execute(machineId)
  if (res?.status === 'ok') {
    machine.value = res.data
    if (res.data.image_urls && res.data.image_urls.length > 0) {
      activeImage.value = res.data.image_urls[0]
    }
  }
}

function prevImage() {
  if (!machine.value || !machine.value.image_urls.length) return
  const urls = machine.value.image_urls
  const currentIdx = urls.indexOf(activeImage.value)
  const newIdx = (currentIdx - 1 + urls.length) % urls.length
  activeImage.value = urls[newIdx]
}

function nextImage() {
  if (!machine.value || !machine.value.image_urls.length) return
  const urls = machine.value.image_urls
  const currentIdx = urls.indexOf(activeImage.value)
  const newIdx = (currentIdx + 1) % urls.length
  activeImage.value = urls[newIdx]
}

const hasSpecifications = computed(() => {
  return machine.value?.specifications && Object.keys(machine.value.specifications).length > 0
})

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB', maximumFractionDigits: 0 }).format(price)
}

onMounted(fetchMachineDetail)
</script>