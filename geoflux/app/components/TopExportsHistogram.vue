<!--
  TopExportsHistogram
  Shows the top-10 exports for a selected year as a horizontal bar chart.
  A range input (scrollbar) at the bottom lets the user scrub through years.
-->
<template>
  <section class="top-exports-histogram">
    <h3>Top 10 Exports — {{ selectedYear }}</h3>
 
    <svg
      :viewBox="`0 0 ${svgWidth} ${svgHeight}`"
      class="top-exports-histogram__svg"
      role="img"
      :aria-label="`Top 10 exports for ${selectedYear}`"
    >
      <!-- X-axis gridlines + labels -->
      <g class="top-exports-histogram__gridlines">
        <template v-for="tick in xTicks" :key="tick.value">
          <line
            :x1="tick.x"
            :y1="padding.top"
            :x2="tick.x"
            :y2="svgHeight - padding.bottom"
            class="top-exports-histogram__gridline"
          />
          <text
            :x="tick.x"
            :y="svgHeight - padding.bottom + 16"
            class="top-exports-histogram__axis-label"
            text-anchor="middle"
          >
            {{ formatValue(tick.value) }}
          </text>
        </template>
      </g>
 
      <!-- Bars -->
      <g class="top-exports-histogram__bars">
        <g
          v-for="(bar, i) in bars"
          :key="bar.label"
          class="top-exports-histogram__bar-group"
          @mouseenter="hoveredIndex = i"
          @mouseleave="hoveredIndex = null"
        >
          <!-- Category label on the left -->
          <text
            :x="padding.left - 8"
            :y="bar.y + bar.height / 2 + 4"
            class="top-exports-histogram__bar-label"
            text-anchor="end"
          >
            {{ bar.label }}
          </text>
 
          <rect
            :x="padding.left"
            :y="bar.y"
            :width="bar.width"
            :height="bar.height"
            :class="['top-exports-histogram__bar', { 'top-exports-histogram__bar--hovered': hoveredIndex === i }]"
          />
 
          <!-- Value tooltip on hover -->
          <text
            v-if="hoveredIndex === i"
            :x="padding.left + bar.width + 6"
            :y="bar.y + bar.height / 2 + 4"
            class="top-exports-histogram__tooltip-text"
          >
            {{ formatValue(bar.rawValue) }}
          </text>
        </g>
      </g>
 
      <!-- Y axis -->
      <line
        :x1="padding.left"
        :y1="padding.top"
        :x2="padding.left"
        :y2="svgHeight - padding.bottom"
        class="top-exports-histogram__axis-line"
      />
      <!-- X axis -->
      <line
        :x1="padding.left"
        :y1="svgHeight - padding.bottom"
        :x2="svgWidth - padding.right"
        :y2="svgHeight - padding.bottom"
        class="top-exports-histogram__axis-line"
      />
    </svg>
 
    <!-- Year scrubber -->
    <div class="top-exports-histogram__scrubber">
      <span>{{ years[0] }}</span>
      <input
        type="range"
        :min="0"
        :max="years.length - 1"
        :value="selectedYearIndex"
        @input="selectedYearIndex = Number($event.target.value)"
        class="top-exports-histogram__range"
        :aria-label="`Select year, currently ${selectedYear}`"
      />
      <span>{{ years[years.length - 1] }}</span>
    </div>
  </section>
</template>
 
<script>
const TICK_COUNT = 5
const BAR_GAP = 4 // px between bars
 
export default {
  name: 'TopExportsHistogram',
 
  props: {
    data: {
      type: Array,
      required: true,
      // Array of { year, exports: [[label, value], ...] }
    },
  },
 
  data() {
    return {
      selectedYearIndex: 0,
      svgWidth: 640,
      svgHeight: 340,
      padding: { top: 16, right: 120, bottom: 36, left: 160 },
      hoveredIndex: null,
    }
  },
 
  computed: {
    years() {
      return this.data.map((d) => d.year)
    },
 
    selectedYear() {
      return this.years[this.selectedYearIndex]
    },
 
    currentExports() {
      const entry = this.data.find((d) => d.year === this.selectedYear)
      return entry ? entry.exports : []
    },
 
    chartWidth() {
      return this.svgWidth - this.padding.left - this.padding.right
    },
 
    chartHeight() {
      return this.svgHeight - this.padding.top - this.padding.bottom
    },
 
    maxValue() {
      return Math.max(...this.currentExports.map(([, v]) => v))
    },
 
    xTicks() {
      const step = this.maxValue / TICK_COUNT
      return Array.from({ length: TICK_COUNT + 1 }, (_, i) => {
        const value = step * i
        return {
          value,
          x: this.padding.left + (value / this.maxValue) * this.chartWidth,
        }
      })
    },
 
    bars() {
      const count = this.currentExports.length
      if (count === 0) return []
 
      const slotHeight = this.chartHeight / count
      const barHeight = Math.max(slotHeight - BAR_GAP, 4)
 
      return this.currentExports.map(([label, value], i) => ({
        label,
        rawValue: value,
        y: this.padding.top + i * slotHeight + (slotHeight - barHeight) / 2,
        width: (value / this.maxValue) * this.chartWidth,
        height: barHeight,
      }))
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

<style scoped>
.top-exports-histogram h3 {
  margin: 0 0 0.6rem;
  font-size: 0.68rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #5a5a6a;
}

.top-exports-histogram__svg {
  width: 100%;
  height: auto;
  display: block;
}

.top-exports-histogram__gridline {
  stroke: rgba(255, 255, 255, 0.06);
  stroke-width: 1;
}

.top-exports-histogram__axis-label {
  fill: #4a4a5a;
  font-size: 11px;
  font-family: inherit;
}

.top-exports-histogram__bar-label {
  fill: #8888a0;
  font-size: 11px;
  font-family: inherit;
}

.top-exports-histogram__bar {
  fill: #3b82f6;
  transition: fill 0.15s ease;
}

.top-exports-histogram__bar--hovered {
  fill: #60a5fa;
}

.top-exports-histogram__tooltip-text {
  fill: #e8e8f0;
  font-size: 11px;
  font-family: inherit;
}

.top-exports-histogram__axis-line {
  stroke: rgba(255, 255, 255, 0.15);
  stroke-width: 1;
}

.top-exports-histogram__scrubber {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.5rem;
  color: #4a4a5a;
  font-size: 0.78rem;
}

.top-exports-histogram__range {
  flex: 1;
  accent-color: #3b82f6;
  cursor: pointer;
}
</style>