<template>
  <form @submit.prevent="submitForm" class="flex flex-col max-h-[80vh] sm:max-h-[85vh]">
    
    <h2 class="text-lg sm:text-xl font-black text-primary uppercase tracking-widest border-b border-border/40 pb-4 shrink-0 select-none">
      {{ machine ? 'Редактировать технику' : 'Новая карточка техники' }}
    </h2>

    <div class="flex-grow overflow-y-auto py-4 pr-1.5 space-y-6">
      
      <!-- Основные поля -->
      <div class="space-y-4">
        <BaseInput v-model="formData.title" label="Название *" placeholder="Трактор Belarus 82.1" required />
        
        <div class="flex flex-col gap-1.5">
          <label class="text-[10px] text-text-muted uppercase tracking-widest font-extrabold">Описание</label>
          <textarea 
            v-model="formData.description" 
            rows="3" 
            placeholder="Укажите подробное описание модели, её назначение и особенности..."
            class="w-full bg-bg border border-border/60 text-text-main px-4 py-3 rounded-xl text-sm font-sans outline-none focus:border-accent focus:bg-surface transition-all placeholder:text-text-muted/40"
          ></textarea>
        </div>

        <BaseInput v-model="formData.price" type="number" label="Цена (в рублях)" placeholder="2000000" />
      </div>

      <!-- Характеристики (JSONB) -->
      <div class="space-y-3 border border-border/50 bg-bg/50 p-4 rounded-2xl">
        <div class="flex justify-between items-center">
          <label class="text-[10px] text-text-muted uppercase tracking-widest font-extrabold">Характеристики (Спецификации)</label>
          <button 
            type="button" 
            @click="addSpec" 
            class="inline-flex items-center gap-1 text-[10px] text-accent hover:text-primary font-bold uppercase tracking-wider font-mono transition-colors"
          >
            <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
            Добавить поле
          </button>
        </div>
        
        <div v-for="(spec, index) in specList" :key="index" class="flex gap-3 items-center">
          <BaseInput v-model="spec.key" placeholder="Напр. Мощность" class="w-1/2" />
          <BaseInput v-model="spec.value" placeholder="Напр. 81 л.с." class="w-1/2" />
          <button 
            type="button" 
            @click="removeSpec(index)" 
            class="mt-4 text-danger hover:text-red-600 hover:scale-110 p-2 flex items-center justify-center rounded-lg hover:bg-danger/5 transition-all cursor-pointer"
            title="Удалить строку"
          >
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <div v-if="specList.length === 0" class="text-xs text-text-muted opacity-50 italic text-center py-2">
          Характеристики не добавлены
        </div>
      </div>

      <div v-if="machine && existingUrls.length" class="space-y-2">
        <label class="text-[10px] text-text-muted uppercase tracking-widest font-extrabold block">Текущие фотографии в облаке ({{ existingUrls.length }})</label>
        <div class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-3">
          <div v-for="(url, idx) in existingUrls" :key="idx" class="group/thumb relative aspect-[4/3] rounded-xl overflow-hidden border border-border/40 shadow-sm shrink-0">
            <img :src="url" @click="openLightbox(url)" class="w-full h-full object-cover cursor-zoom-in hover:scale-105 transition-transform duration-200">
            
            <button 
              type="button" 
              @click="removeExistingUrl(idx)"
              class="absolute top-1 right-1 w-6 h-6 rounded-lg bg-black/60 text-white flex items-center justify-center hover:bg-danger transition-colors cursor-pointer"
              title="Удалить из облака"
            >
              <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <div class="space-y-4">
        <label class="text-[10px] text-text-muted uppercase tracking-widest font-extrabold block">
          {{ machine ? 'Добавить новые фотографии' : 'Фотографии галереи' }}
        </label>
        
        <div class="relative group/upload border border-dashed border-border/60 hover:border-accent rounded-2xl p-6 bg-bg/40 text-center transition-all duration-200 cursor-pointer">
          <input 
            type="file" 
            multiple 
            accept="image/*" 
            @change="handleFileSelect" 
            class="absolute inset-0 opacity-0 cursor-pointer w-full h-full z-10"
          >
          <div class="flex flex-col items-center gap-2 select-none">
            <svg class="w-8 h-8 text-text-muted/60 group-hover/upload:text-accent transition-colors duration-200" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
              <path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242M12 12v9m-4-4l4-4 4 4" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <p class="text-xs text-text-main font-bold">Выберите новые изображения</p>
            <p class="text-[10px] text-text-muted">JPEG, PNG или WEBP до 10MB</p>
          </div>
        </div>

        <div class="flex items-center justify-between bg-surface/80 border border-border/30 rounded-2xl p-4 transition-all duration-300">
          <div>
            <span class="block text-xs font-bold text-text-main">Доступность техники</span>
            <span class="block text-[10px] text-text-muted mt-0.5">
              {{ formData.is_available ? 'В наличии (Зеленый индикатор)' : 'Под заказ (Оранжевый индикатор)' }}
            </span>
          </div>
          
          <!-- Кнопка-тумблер (type="button" важен, чтобы форма не отправлялась по клику) -->
          <button 
            type="button" 
            @click="formData.is_available = !formData.is_available"
            class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none"
            :class="[formData.is_available ? 'bg-primary' : 'bg-orange-500']"
          >
            <span 
              class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-md ring-0 transition duration-200 ease-in-out"
              :class="[formData.is_available ? 'translate-x-5' : 'translate-x-0']"
            />
          </button>
        </div>

        <div v-if="filePreviews.length" class="space-y-2">
          <div class="text-[10px] text-text-muted uppercase tracking-widest font-extrabold">Новые фото к загрузке ({{ filePreviews.length }})</div>
          <div class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-3">
            <div v-for="(item, idx) in filePreviews" :key="idx" class="group/thumb relative aspect-[4/3] rounded-xl overflow-hidden border border-border/40 shadow-sm shrink-0">
              <img :src="item.url" @click="openLightbox(item.url)" class="w-full h-full object-cover cursor-zoom-in hover:scale-105 transition-transform duration-200">
              
              <button 
                type="button" 
                @click="removeNewFile(idx)"
                class="absolute top-1 right-1 w-6 h-6 rounded-lg bg-black/60 text-white flex items-center justify-center hover:bg-danger transition-colors cursor-pointer"
                title="Отменить загрузку"
              >
                <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="pt-4 border-t border-border/40 flex justify-end gap-3 shrink-0 select-none">
      <BaseButton type="button" variant="secondary" @click="$emit('cancel')">Отмена</BaseButton>
      <BaseButton type="submit" :loading="isExecuting">Сохранить</BaseButton>
    </div>

    <transition 
      enter-active-class="transition duration-200 ease-out" 
      enter-from-class="opacity-0 scale-95" 
      enter-to-class="opacity-100 scale-100" 
      leave-active-class="transition duration-150 ease-in" 
      leave-from-class="opacity-100 scale-100" 
      leave-to-class="opacity-0 scale-95"
    >
      <div v-if="activeLightboxUrl" class="fixed inset-0 z-[1100] flex items-center justify-center bg-black/80 backdrop-blur-md p-4" @click="closeLightbox">
        <div class="relative max-w-4xl w-full max-h-[85vh] flex items-center justify-center" @click.stop>
          <img :src="activeLightboxUrl" class="max-w-full max-h-[80vh] rounded-2xl shadow-2xl border border-white/10 object-contain select-none">
          
          <button 
            type="button" 
            @click="closeLightbox"
            class="absolute -top-12 right-0 w-10 h-10 rounded-full bg-surface/10 border border-white/20 text-white flex items-center justify-center hover:bg-white/20 transition-colors cursor-pointer"
          >
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
      </div>
    </transition>
  </form>
</template>

<script setup>
import { ref, onMounted, computed, onBeforeUnmount } from 'vue'
import { machinesApi } from '@/services/machines.api'
import { useApi } from '@/composables/useApi'
import { useToast } from '@/composables/useToast'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'

const props = defineProps({
  machine: { type: Object, default: null }
})

const emit = defineEmits(['success', 'cancel'])
const toast = useToast()

const { execute: executeCreate, isLoading: isCreating } = useApi(machinesApi.createMachine)
const { execute: executeUpdate, isLoading: isUpdating } = useApi(machinesApi.updateMachine)

const isExecuting = computed(() => isCreating.value || isUpdating.value)

const formData = ref({ title: '', description: '', price: '', is_available: true })
const specList = ref([]) 

const existingUrls = ref([])
const selectedFiles = ref([])
const filePreviews = ref([])

const activeLightboxUrl = ref(null)

onMounted(() => {
  if (props.machine) {
    formData.value = {
      title: props.machine.title || '',
      description: props.machine.description || '',
      price: props.machine.price || '',
      is_available: props.machine.is_available !== false // Восстанавливаем сохраненное значение
    }
    
    existingUrls.value = props.machine.image_urls ? [...props.machine.image_urls] : []
    
    if (props.machine.specifications) {
      specList.value = Object.entries(props.machine.specifications).map(([key, value]) => ({
        key,
        value
      }))
    }
  }
})

onBeforeUnmount(() => {
  filePreviews.value.forEach(item => URL.revokeObjectURL(item.url))
})

function addSpec() { specList.value.push({ key: '', value: '' }) }
function removeSpec(index) { specList.value.splice(index, 1) }

function removeExistingUrl(index) {
  existingUrls.value.splice(index, 1)
}

function handleFileSelect(event) {
  const files = Array.from(event.target.files)
  files.forEach(file => {
    selectedFiles.value.push(file)
    filePreviews.value.push({
      file,
      url: URL.createObjectURL(file)
    })
  })
}

function removeNewFile(index) {
  URL.revokeObjectURL(filePreviews.value[index].url)
  filePreviews.value.splice(index, 1)
  selectedFiles.value.splice(index, 1)
}

function openLightbox(url) {
  activeLightboxUrl.value = url
}
function closeLightbox() {
  activeLightboxUrl.value = null
}

async function submitForm() {
  if (!formData.value.title.trim()) return toast.error('Название техники обязательно')

  const specsObject = {}
  specList.value.forEach(s => {
    if (s.key.trim() && s.value.trim()) specsObject[s.key.trim()] = s.value.trim()
  })

  formData.value.specifications = specsObject
  formData.value.image_urls = existingUrls.value

  try {
    if (props.machine) {
      await executeUpdate(props.machine.id, formData.value, selectedFiles.value)
      toast.success('Карточка техники успешно обновлена!')
    } else {
      await executeCreate(formData.value, selectedFiles.value)
      toast.success('Карточка техники успешно создана!')
    }
    emit('success')
  } catch (err) {
    // Ошибки перехватывает useApi
  }
}
</script>