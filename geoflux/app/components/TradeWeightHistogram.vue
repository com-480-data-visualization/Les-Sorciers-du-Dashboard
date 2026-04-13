<template>
  <BaseHistogram
    :data="data"
    title="Trade Weight Over Time (tonnes)"
    :formatter="formatWeight"
  />
</template>
 
<script>
import BaseHistogram from './BaseHistogram.vue'
 
export default {
  name: 'TradeWeightHistogram',
 
  components: { BaseHistogram },
 
  props: {
    data: {
      type: Array,
      required: true,
      // Array of [year, weight_in_kg_or_tonnes]
    },
  },
 
  methods: {
    formatWeight(value) {
      if (value >= 1e9) return `${(value / 1e9).toFixed(2)}Gt`
      if (value >= 1e6) return `${(value / 1e6).toFixed(0)}Mt`
      if (value >= 1e3) return `${(value / 1e3).toFixed(0)}kt`
      return `${value.toLocaleString()} t`
    },
  },
}
</script>