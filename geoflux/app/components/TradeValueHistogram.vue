<template>
  <BaseHistogram
    :data="data"
    title="Trade Value Over Time (USD)"
    :formatter="formatValue"
  />
</template>

<script>
import BaseHistogram from './BaseHistogram.vue'

export default {
  name: 'TradeValueHistogram',

  components: { BaseHistogram },

  props: {
    data: {
      type: Array,
      required: true,
      // Array of [year, usd_value]
    },
  },

  methods: {
    formatValue(value) {
      if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`
      if (value >= 1e9) return `$${(value / 1e9).toFixed(0)}B`
      return `$${value.toLocaleString()}`
    },
  },
}
</script>