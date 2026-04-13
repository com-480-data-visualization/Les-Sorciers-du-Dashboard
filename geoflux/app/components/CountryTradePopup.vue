<template>
  <div class="country-trade-popup">
    <div v-if="isLoading === false && err === false" class="big-popup-content">
      <TradeHeader :country="data.country" />
      <TradeOverview
        :flag="data.flag"
        :topExports="data.top_exports"
        :topImports="data.top_imports"
        :balanceRatio="data.commercial_balance_ratio"
      />
      <TradeValueHistogram :data="data.trade_value_time" />
      <TradeWeightHistogram :data="data.trade_weight_time" />
      <TopExportsHistogram :data="data.top10_time" />
    </div>
    <button class="close-btn" @click="emit('close')">X</button>

  </div>
</template>
 
<script setup>
import { ref, onMounted, watch } from 'vue'
import TradeHeader from './TradeHeader.vue'
import TradeOverview from './TradeOverview.vue'
import TradeValueHistogram from './TradeValueHistogram.vue'
import TradeWeightHistogram from './TradeWeightHistogram.vue'
import TopExportsHistogram from './TopExportsHistogram.vue'

  const isLoading = ref(true);
  const err = ref(false);
  const data = ref(null);

  const props = defineProps({
        country: {
        type: String,
        required: true,
      }
  });
  onMounted(async () => await loadData(props.country));

  const emit = defineEmits(['close'])

  
  watch(() => props.country, 
      async () => await loadData(props.country),
    );
 
  async function loadData(country) {
    // TODO: replace with HTTP call when backend is ready
    // e.g. const response = await fetch(`/api/trade/${country.toLowerCase()}`)
    const country_formatted = country.toLowerCase().replaceAll(" ", '_')
    try {
      const module = await import(`../../mocks/${country_formatted}.json`)
      data.value = module.default;
    }
    catch {
      err.value = true;
    } finally {
      isLoading.value = false;
    }
  }

</script>

<style scoped>
.big-popup-content {
  background: #111114;
  width: 80%;
  max-width: 960px;
  max-height: 85vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
  padding: 2rem 2.25rem 2.25rem;
  position: relative;
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 16px;
  box-shadow: 0 8px 80px rgba(0, 0, 0, 0.85), 0 0 0 1px rgba(255,255,255,0.04) inset;
  scrollbar-width: thin;
  scrollbar-color: rgba(255,255,255,0.12) transparent;
}

.close-btn {
  position: absolute;
  top: 18px;
  right: 22px;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.35);
  font-size: 1.1rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  cursor: pointer;
  line-height: 1;
  padding: 4px 8px;
  border-radius: 6px;
  transition: color 0.15s, background 0.15s;
}

.close-btn:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.08);
}
</style>