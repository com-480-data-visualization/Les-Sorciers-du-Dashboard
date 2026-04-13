<!--
  BaseHistogram
  A generic SVG bar chart for a series of [year, value] pairs.
 
  Props:
    data      – Array of [year, value] tuples
    title     – Chart title
    formatter – Function(value) → display string for y-axis labels and tooltips
-->
<template>
  <section class="base-histogram">
    <h3>{{ title }}</h3>
 
    <div class="base-histogram__chart-wrapper">
      <svg
        :viewBox="`0 0 ${svgWidth} ${svgHeight}`"
        class="base-histogram__svg"
        role="img"
        :aria-label="title"
      >
        <!-- Y-axis gridlines + labels -->
        <g class="base-histogram__gridlines">
          <template v-for="tick in yTicks" :key="tick.value">
            <line
              :x1="padding.left"
              :y1="tick.y"
              :x2="svgWidth - padding.right"
              :y2="tick.y"
              class="base-histogram__gridline"
            />
            <text
              :x="padding.left - 6"
              :y="tick.y + 4"
              class="base-histogram__axis-label"
              text-anchor="end"
            >
              {{ formatter(tick.value) }}
            </text>
          </template>
        </g>
 
        <!-- Bars -->
        <g class="base-histogram__bars">
          <g
            v-for="(bar, i) in bars"
            :key="bar.year"
            class="base-histogram__bar-group"
            @mouseenter="hoveredIndex = i"
            @mouseleave="hoveredIndex = null"
          >
            <rect
              :x="bar.x"
              :y="bar.y"
              :width="bar.width"
              :height="bar.height"
              :class="['base-histogram__bar', { 'base-histogram__bar--hovered': hoveredIndex === i }]"
            />
 
            <!-- Tooltip on hover -->
            <g v-if="hoveredIndex === i" class="base-histogram__tooltip">
              <rect
                :x="tooltipX(bar)"
                :y="bar.y - 28"
                width="90"
                height="22"
                rx="3"
                class="base-histogram__tooltip-bg"
              />
              <text
                :x="tooltipX(bar) + 45"
                :y="bar.y - 12"
                class="base-histogram__tooltip-text"
                text-anchor="middle"
              >
                {{ formatter(bar.rawValue) }}
              </text>
            </g>
 
            <!-- X-axis label -->
            <text
              :x="bar.x + bar.width / 2"
              :y="svgHeight - padding.bottom + 16"
              class="base-histogram__axis-label"
              text-anchor="middle"
            >
              {{ bar.year }}
            </text>
          </g>
        </g>
 
        <!-- Axes -->
        <line
          :x1="padding.left"
          :y1="padding.top"
          :x2="padding.left"
          :y2="svgHeight - padding.bottom"
          class="base-histogram__axis-line"
        />
        <line
          :x1="padding.left"
          :y1="svgHeight - padding.bottom"
          :x2="svgWidth - padding.right"
          :y2="svgHeight - padding.bottom"
          class="base-histogram__axis-line"
        />
      </svg>
    </div>
  </section>
</template>
 
<script>
const TICK_COUNT = 5
const BAR_GAP_RATIO = 0.25 // fraction of slot width used as gap
 
export default {
  name: 'BaseHistogram',
 
  props: {
    data: {
      type: Array,
      required: true,
      // Array of [year, value]
    },
    title: {
      type: String,
      required: true,
    },
    formatter: {
      type: Function,
      default: (v) => v.toLocaleString(),
    },
  },
 
  data() {
    return {
      svgWidth: 600,
      svgHeight: 320,
      padding: { top: 20, right: 20, bottom: 30, left: 80 },
      hoveredIndex: null,
    }
  },
 
  computed: {
    chartWidth() {
      return this.svgWidth - this.padding.left - this.padding.right
    },
 
    chartHeight() {
      return this.svgHeight - this.padding.top - this.padding.bottom
    },
 
    maxValue() {
      return Math.max(...this.data.map(([, v]) => v))
    },
 
    yTicks() {
      const step = this.maxValue / TICK_COUNT
      return Array.from({ length: TICK_COUNT + 1 }, (_, i) => {
        const value = step * i
        const y = this.svgHeight - this.padding.bottom - (value / this.maxValue) * this.chartHeight
        return { value, y }
      })
    },
 
    bars() {
      const slotWidth = this.chartWidth / this.data.length
      const barWidth = slotWidth * (1 - BAR_GAP_RATIO)
 
      return this.data.map(([year, value], i) => {
        const barHeight = (value / this.maxValue) * this.chartHeight
        return {
          year,
          rawValue: value,
          x: this.padding.left + i * slotWidth + (slotWidth - barWidth) / 2,
          y: this.svgHeight - this.padding.bottom - barHeight,
          width: barWidth,
          height: barHeight,
        }
      })
    },
  },
 
  methods: {
    tooltipX(bar) {
      // Keep tooltip inside SVG boundaries
      const ideal = bar.x + bar.width / 2 - 45
      const max = this.svgWidth - this.padding.right - 90
      return Math.min(Math.max(ideal, this.padding.left), max)
    },
  },
}
</script>

<style scoped>
.base-histogram h3 {
  margin: 0 0 0.6rem;
  font-size: 0.68rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #5a5a6a;
}

.base-histogram__chart-wrapper {
  width: 100%;
}

.base-histogram__svg {
  width: 100%;
  height: auto;
  display: block;
}

.base-histogram__gridline {
  stroke: rgba(255, 255, 255, 0.06);
  stroke-width: 1;
}

.base-histogram__axis-label {
  fill: #4a4a5a;
  font-size: 11px;
  font-family: inherit;
}

.base-histogram__bar {
  fill: #3b82f6;
  transition: fill 0.15s ease;
}

.base-histogram__bar--hovered {
  fill: #60a5fa;
}

.base-histogram__tooltip-bg {
  fill: #1e1e26;
  stroke: rgba(255, 255, 255, 0.12);
  stroke-width: 1;
}

.base-histogram__tooltip-text {
  fill: #e8e8f0;
  font-size: 11px;
  font-family: inherit;
}

.base-histogram__axis-line {
  stroke: rgba(255, 255, 255, 0.15);
  stroke-width: 1;
}
</style>