<template>
  <PublicLayout>
    <div class="max-w-[800px] mx-auto px-6 py-16">
      <div v-html="compiledMarkdown" class="markdown-body"></div>
    </div>
  </PublicLayout>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { marked } from 'marked'
import { config } from '@/config'  // Импортируем наш конфиг
import PublicLayout from '@/layouts/PublicLayout.vue'

const route = useRoute()
const rawMarkdownText = ref('')

async function loadDocument() {
  const docName = route.meta.document
  try {
    const file = await import(`../../content/${docName}.md?raw`)
    rawMarkdownText.value = file.default
  } catch (err) {
    rawMarkdownText.value = '# Ошибка\nНе удалось загрузить документ.'
  }
}

const compiledMarkdown = computed(() => {
  let text = rawMarkdownText.value

  Object.keys(config).forEach((key) => {
    const placeholder = `{{${key}}}`
    text = text.replaceAll(placeholder, config[key])
  })

  return marked(text)
})

onMounted(loadDocument)
watch(() => route.meta.document, loadDocument)
</script>

<style>
.markdown-body h1 {
  font-size: 1.875rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--color-primary);
  margin-bottom: 1.5rem;
}
.markdown-body h3 {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--color-accent);
  margin-top: 1.5rem;
  margin-bottom: 0.5rem;
}
.markdown-body p {
  font-size: 0.875rem;
  line-height: 1.625;
  color: var(--color-text-main);
  margin-bottom: 1rem;
}
.markdown-body ul {
  list-style-type: disc;
  padding-left: 1.5rem;
  margin-bottom: 1rem;
  font-size: 0.875rem;
  color: var(--color-text-main);
}
.markdown-body li {
  margin-bottom: 0.25rem;
}
</style>