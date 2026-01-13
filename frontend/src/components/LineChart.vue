<script setup>
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Filler,
} from 'chart.js';
import { Line } from 'vue-chartjs';
import { computed } from 'vue';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Filler
);

const props = defineProps({
  chartData: { type: Object, required: true },
  isDark: { type: Boolean, default: false }
});

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  animation: {
    duration: 2000, // 2秒慢速绘制，优雅
    easing: 'easeOutQuart', // 苹果风格的缓动
  },
  interaction: {
    intersect: false,
    mode: 'index',
  },
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: props.isDark ? 'rgba(30,30,30,0.9)' : 'rgba(255,255,255,0.9)',
      titleColor: props.isDark ? '#fff' : '#000',
      bodyColor: props.isDark ? '#ccc' : '#666',
      borderColor: props.isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
      borderWidth: 1,
      padding: 10,
      cornerRadius: 12, // 更圆润的 Tooltip
      displayColors: false,
      titleFont: { family: '-apple-system', size: 11 },
      bodyFont: { family: '-apple-system', size: 13, weight: 'bold' },
      callbacks: {
        label: (context) => ` ${context.parsed.y} 在线`
      }
    }
  },
  scales: {
    x: { display: false }, // 彻底隐藏 X 轴
    y: { display: false, beginAtZero: true } // 彻底隐藏 Y 轴
  },
  elements: {
    line: {
      tension: 0.5, // 贝塞尔曲线更圆润，像液态一样
      borderWidth: 2
    },
    point: {
      radius: 0, // 平常不显示点，极致简约
      hitRadius: 20,
      hoverRadius: 6, // 悬停时显示一个小点
      hoverBorderWidth: 3
    }
  }
}));
</script>

<template>
  <div class="w-full h-full">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>
