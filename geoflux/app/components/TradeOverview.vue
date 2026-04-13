<template>
  <section class="trade-overview">
    <img :src="flag" :alt="`${country} flag`" class="trade-overview__flag" />

    <div class="trade-overview__lists">
      <div class="trade-overview__exports">
        <h3>Top 3 Exports</h3>
        <ol>
          <li v-for="item in topExports.slice(0, 3)" :key="item">{{ item }}</li>
        </ol>
      </div>

      <div class="trade-overview__imports">
        <h3>Top 3 Imports</h3>
        <ol>
          <li v-for="item in topImports.slice(0, 3)" :key="item">{{ item }}</li>
        </ol>
      </div>
    </div>

    <div class="trade-overview__balance">
      <h3>Commercial Balance (10-year avg)</h3>
      <p :class="balanceClass">{{ formattedBalance }}</p>
      <p class="trade-overview__balance-desc">{{ balanceRatio.description }}</p>
    </div>
  </section>
</template>

<script>
export default {
  name: 'TradeOverview',

  props: {
    flag: {
      type: String,
      required: true,
    },
    topExports: {
      type: Array,
      required: true,
    },
    topImports: {
      type: Array,
      required: true,
    },
    balanceRatio: {
      type: Object,
      required: true,
      // shape: { description: String, value: Number }
    },
  },

  computed: {
    formattedBalance() {
      const value = this.balanceRatio.value
      const sign = value >= 0 ? '+' : '−'
      const abs = Math.abs(value)
      return `${sign}${this.formatBillions(abs)}`
    },

    balanceClass() {
      return this.balanceRatio.value >= 0
        ? 'trade-overview__balance-value trade-overview__balance-value--positive'
        : 'trade-overview__balance-value trade-overview__balance-value--negative'
    },
  },

  methods: {
    formatBillions(value) {
      if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`
      if (value >= 1e9) return `$${(value / 1e9).toFixed(1)}B`
      return `$${value.toLocaleString()}`
    },
  },
}
</script>

<style scoped>
.trade-overview {
  display: flex;
  flex-wrap: wrap;
  gap: 2rem;
  align-items: flex-start;
}

.trade-overview__flag {
  width: 72px;
  height: auto;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.trade-overview__lists {
  display: flex;
  gap: 2.5rem;
  flex: 1;
}

.trade-overview__exports h3,
.trade-overview__imports h3,
.trade-overview__balance h3 {
  margin: 0 0 0.5rem;
  font-size: 0.68rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #5a5a6a;
}

.trade-overview__exports ol,
.trade-overview__imports ol {
  margin: 0;
  padding-left: 1.25rem;
}

.trade-overview__exports li,
.trade-overview__imports li {
  color: #c8c8d8;
  font-size: 0.875rem;
  margin-bottom: 0.3rem;
}

.trade-overview__balance {
  min-width: 160px;
}

.trade-overview__balance-value {
  margin: 0;
  font-size: 1.9rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  line-height: 1;
}

.trade-overview__balance-value--positive {
  color: #22c55e;
}

.trade-overview__balance-value--negative {
  color: #ef4444;
}

.trade-overview__balance-desc {
  margin: 0.4rem 0 0;
  font-size: 0.8rem;
  color: #5a5a6a;
}
</style>