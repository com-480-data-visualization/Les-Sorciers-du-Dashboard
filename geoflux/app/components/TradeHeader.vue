<template>
  <header class="trade-header">
    <h1>{{ country }} — Trade Overview</h1>
  </header>
</template>
 
<script>
export default {
  name: 'TradeHeader',
 
  props: {
    country: {
      type: String,
      required: true,
    },
  },
}
</script>

<style scoped>
.trade-header {
  padding-bottom: 1.25rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.07);
}

.trade-header h1 {
  margin: 0;
  font-size: 1.45rem;
  font-weight: 600;
  color: #e8e8f0;
  letter-spacing: 0.01em;
}
</style>