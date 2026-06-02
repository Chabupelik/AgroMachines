<template>
  <div class="min-h-screen bg-bg text-text-main flex flex-col items-center justify-center p-6 font-sans">
    <div class="text-center space-y-6 max-w-sm">
      <div class="text-8xl select-none">🚜💨</div>
      <h1 class="text-5xl font-extrabold text-primary tracking-widest">404</h1>
      <p class="text-text-muted text-sm leading-relaxed">
        Похоже, этот трактор уехал в другое поле. Запрашиваемая страница не существует.
      </p>
      <router-link to="/">
        <button class="bg-primary text-surface px-6 py-3 rounded-lg font-bold text-xs uppercase tracking-widest hover:brightness-110 active:scale-95 transition-all cursor-pointer">
          Вернуться на главную
        </button>
      </router-link>
    </div>
  </div>
</template>