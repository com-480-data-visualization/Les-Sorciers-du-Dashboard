<template>
  <div class="flex flex-col gap-2 pt-2">
    <input
      type="range"
      :min="MIN_YEAR"
      :max="MAX_YEAR"
      step="1"
      :value="modelValue"
      @input="$emit('update:modelValue', +($event.target as HTMLInputElement).value)"
      class="w-full accent-blue-500"
    />
    <div class="flex justify-between text-xs text-zinc-400">
      <span>{{ MIN_YEAR }}</span>
      <span class="font-semibold text-zinc-600 dark:text-zinc-300">{{ modelValue }}</span>
      <span>{{ MAX_YEAR }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { YEARS } from '~/utils/dummyData'

defineProps<{ modelValue: number }>()
defineEmits<{ (e: 'update:modelValue', v: number): void }>()

const MIN_YEAR = YEARS[0]
const MAX_YEAR = YEARS[YEARS.length - 1]
</script>
