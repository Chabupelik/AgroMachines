<template>
  <div class="min-h-screen bg-bg text-text-main flex flex-col md:flex-row">
    <Sidebar :is-open="isSidebarOpen" @close="isSidebarOpen = false" />
    
    <div class="flex-grow flex flex-col min-h-screen md:pl-[240px]">
      <Topbar @toggle-sidebar="isSidebarOpen = !isSidebarOpen" />
      
      <main class="flex-grow p-4 sm:p-6 md:p-8">
        <slot />
      </main>
    </div>
    
    <BaseToast />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Sidebar from '@/components/admin/Sidebar.vue'
import Topbar from '@/components/admin/Topbar.vue'
import BaseToast from '@/components/ui/BaseToast.vue'

const isSidebarOpen = ref(false)
</script>