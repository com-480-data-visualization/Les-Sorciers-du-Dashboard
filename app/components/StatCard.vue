<template>
  <div
    :class="[
      'rounded-xl p-5 flex flex-col gap-3 transition-colors',
      clickable
        ? 'bg-zinc-100 dark:bg-zinc-800 cursor-pointer hover:bg-zinc-200 dark:hover:bg-zinc-700'
        : 'bg-zinc-100 dark:bg-zinc-800',
    ]"
    @click="clickable ? toggle() : undefined"
  >
    <!-- Title row -->
    <div class="flex items-center justify-between">
      <h3 class="text-sm font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wide">{{ title }}</h3>
      <div class="flex items-center gap-2">
        <slot name="badge" />
        <UIcon
          v-if="expandable"
          :name="expanded ? 'i-heroicons-chevron-up' : 'i-heroicons-chevron-down'"
          class="size-4 text-zinc-400"
        />
      </div>
    </div>

    <!-- Primary value -->
    <div v-if="value" :class="['text-3xl font-bold', colorClass]">{{ value }}</div>

    <!-- Subtitle -->
    <p v-if="subtitle" class="text-xs text-zinc-500 dark:text-zinc-400">{{ subtitle }}</p>

    <!-- Always-visible body content -->
    <slot name="body" />

    <!-- Expanded content -->
    <Transition name="expand">
      <div v-if="expanded || !expandable" class="mt-1">
        <slot />
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  title: string
  value?: string
  subtitle?: string
  color?: 'blue' | 'orange' | 'green' | 'red' | 'default'
  expandable?: boolean
  clickable?: boolean
}>()

const expanded = ref(false)

function toggle() {
  if (props.expandable) expanded.value = !expanded.value
}

const colorClass = computed(() => {
  switch (props.color) {
    case 'blue':   return 'text-blue-600 dark:text-blue-400'
    case 'orange': return 'text-orange-600 dark:text-orange-400'
    case 'green':  return 'text-green-600 dark:text-green-400'
    case 'red':    return 'text-red-600 dark:text-red-400'
    default:       return 'text-zinc-800 dark:text-zinc-100'
  }
})
</script>

<style scoped>
.expand-enter-active,
.expand-leave-active {
  transition: max-height 0.3s ease, opacity 0.3s ease;
  max-height: 600px;
  overflow: hidden;
}
.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
}
</style>
