<template>
  <div class="min-h-screen bg-bg text-text-main flex flex-col items-center justify-center p-6 font-sans">
    <div class="text-center space-y-6 max-w-sm">
      <div class="text-8xl select-none">🚧</div>
      <h1 class="text-5xl font-extrabold text-accent tracking-widest">403</h1>
      <p class="text-text-muted text-sm leading-relaxed">
        Доступ ограничен. У вашей учетной записи недостаточно прав для просмотра этого секретного терминала.
      </p>
      <router-link to="/">
        <button class="bg-transparent border border-border hover:border-accent text-accent px-6 py-3 rounded-lg font-bold text-xs uppercase tracking-widest active:scale-95 transition-all cursor-pointer">
          Эвакуация на главную
        </button>
      </router-link>
    </div>
  </div>
</template>