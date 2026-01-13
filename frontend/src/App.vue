<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';
import axios from 'axios';
import LineChart from './components/LineChart.vue';

// --- 状态定义 ---
const serverAddress = ref('');
const status = ref('idle');
const resultData = ref(null);
const errorMessage = ref('');
const theme = ref('system');
const showThemeMenu = ref(false);
const history = ref([]); 
const favorites = ref([]); // 新增：收藏列表
const displayOnline = ref(0); 
const isInputFocused = ref(false); 

// 图表与主题状态
const chartData = ref(null);
const isDarkMode = ref(false);

// --- 方案一：聚光灯数据 ---
const mouseX = ref(0);
const mouseY = ref(0);

// --- 方案二：磁力像素数据 ---
const pixels = ref([]);
let animationFrameId = null;

// --- 3D 视差卡片逻辑 (保留) ---
const cardRef = ref(null);
const handleCardMouseMove = (e) => {
  if (!cardRef.value) return;
  const card = cardRef.value;
  const rect = card.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;
  const centerX = rect.width / 2;
  const centerY = rect.height / 2;
  const rotateX = ((y - centerY) / centerY) * -5;
  const rotateY = ((x - centerX) / centerX) * 5;
  const sheenY = (y / rect.height) * 100;
  card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
  card.style.setProperty('--sheen-y', `${sheenY}%`);
};
const resetCard = () => {
  if (!cardRef.value) return;
  const card = cardRef.value;
  card.style.transform = `perspective(1000px) rotateX(0deg) rotateY(0deg)`;
  card.style.setProperty('--sheen-y', `100%`);
};

// --- 全局鼠标监听 ---
const handleGlobalMouseMove = (e) => {
  mouseX.value = e.clientX;
  mouseY.value = e.clientY;
};

// --- 像素物理引擎 ---
const initPixels = () => {
  const pixelCount = 30;
  const newPixels = [];
  for (let i = 0; i < pixelCount; i++) {
    newPixels.push({
      id: i,
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight,
      baseY: Math.random() * window.innerHeight,
      speed: Math.random() * 0.5 + 0.2,
      size: Math.random() * 20 + 5,
      opacity: Math.random() * 0.05 + 0.02,
      vx: 0, vy: 0 
    });
  }
  pixels.value = newPixels;
};

const animatePixels = () => {
  pixels.value.forEach(p => {
    p.y -= p.speed;
    if (p.y < -50) {
      p.y = window.innerHeight + 50;
      p.x = Math.random() * window.innerWidth;
      p.vx = 0; p.vy = 0;
    }
    const dx = p.x - mouseX.value;
    const dy = p.y - mouseY.value;
    const distance = Math.sqrt(dx * dx + dy * dy);
    const maxDist = 200;
    if (distance < maxDist) {
      const force = (maxDist - distance) / maxDist;
      const angle = Math.atan2(dy, dx);
      const push = force * 2;
      p.vx += Math.cos(angle) * push;
      p.vy += Math.sin(angle) * push;
    }
    p.vx *= 0.95; p.vy *= 0.95;
    p.x += p.vx; p.y += p.vy;
  });
  animationFrameId = requestAnimationFrame(animatePixels);
};

// --- 黑客解码标题 ---
const titleText = ref("Server Status");
const originalTitle = "Server Status";
const letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789§#&";
let interval = null;
const runDecryptEffect = () => {
  let iteration = 0;
  clearInterval(interval);
  interval = setInterval(() => {
    titleText.value = originalTitle.split("").map((letter, index) => {
        if (index < iteration) return originalTitle[index];
        return letters[Math.floor(Math.random() * letters.length)];
      }).join("");
    if (iteration >= originalTitle.length) clearInterval(interval);
    iteration += 1 / 3;
  }, 30);
};

// --- 动画 ---
const animateNumber = (target) => {
  let start = 0;
  const duration = 1500;
  const startTime = performance.now();
  const tick = (currentTime) => {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 4);
    displayOnline.value = Math.floor(start + (target - start) * ease);
    if (progress < 1) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
};

// --- 生成 Apple 风格图表数据 ---
const generateMockHistory = (current, max) => {
  const labels = [];
  const data = [];
  const now = new Date();
  for (let i = 12; i >= 0; i--) {
    const d = new Date(now.getTime() - i * 60 * 60 * 1000);
    labels.push(d.getHours() + ':00');
    let variation = Math.random() * 0.2 - 0.1; 
    let timeFactor = 1;
    const hour = d.getHours();
    if (hour >= 18 && hour <= 22) timeFactor = 1.2; 
    else if (hour >= 2 && hour <= 7) timeFactor = 0.5; 
    let value = Math.floor(current * timeFactor * (1 + variation));
    if (i === 0) value = current; 
    if (value < 0) value = 0;
    if (value > max) value = max;
    data.push(value);
  }
  const colorRGB = isDarkMode.value ? '255, 255, 255' : '0, 0, 0'; 
  chartData.value = {
    labels,
    datasets: [{
      label: '在线人数',
      data,
      borderColor: `rgba(${colorRGB}, 1)`,
      backgroundColor: (context) => {
        const ctx = context.chart.ctx;
        const gradient = ctx.createLinearGradient(0, 0, 0, 100);
        gradient.addColorStop(0, `rgba(${colorRGB}, 0.15)`);
        gradient.addColorStop(1, `rgba(${colorRGB}, 0)`);
        return gradient;
      },
      fill: true,
      borderWidth: 2,
      pointRadius: 0, 
      pointHoverRadius: 5,
      pointBackgroundColor: `rgba(${colorRGB}, 1)`,
      pointBorderColor: isDarkMode.value ? '#000' : '#fff',
      pointBorderWidth: 2,
      tension: 0.5 
    }]
  };
};

// --- 查询逻辑 ---
const queryServer = async (addressOverride = null) => {
  const targetAddress = addressOverride || serverAddress.value;
  if (!targetAddress.trim()) return;
  if (addressOverride) serverAddress.value = addressOverride;
  status.value = 'loading';
  resultData.value = null;
  errorMessage.value = '';
  displayOnline.value = 0;
  chartData.value = null;

  const parts = targetAddress.split(':');
  const host = parts[0];
  const port = parts.length > 1 ? parseInt(parts[1]) : 25565;
  try {
    const response = await axios.post('/api/query', { host, port });
    if (response.data.status === 'success') {
      setTimeout(() => {
        resultData.value = response.data;
        status.value = 'success';
        addToHistory(targetAddress);
        nextTick(() => { 
          animateNumber(response.data.players.online); 
          generateMockHistory(response.data.players.online, response.data.players.max);
        });
      }, 800);
    } else {
      throw new Error(response.data.message);
    }
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || error.message || '无法连接到服务器';
    status.value = 'error';
  }
};

// --- 历史记录 & 收藏逻辑 (Local Storage) ---
const addToHistory = (addr) => {
  const newHistory = history.value.filter(h => h !== addr);
  newHistory.unshift(addr);
  if (newHistory.length > 5) newHistory.pop();
  history.value = newHistory;
  localStorage.setItem('queryHistory', JSON.stringify(newHistory));
};
const removeHistory = (addr) => {
  history.value = history.value.filter(h => h !== addr);
  localStorage.setItem('queryHistory', JSON.stringify(history.value));
}


// 1. 辅助函数：获取当前结果的完整地址 (IP:Port)
const getCurrentFullAddress = () => {
  if (!resultData.value) return '';
  let addr = resultData.value.host;
  // 如果端口存在且不是默认的25565，就拼上去
  if (resultData.value.port && resultData.value.port !== 25565) {
    addr += `:${resultData.value.port}`;
  }
  return addr;
};

// 2. 判断是否已收藏
const isFavorited = computed(() => {
  const addr = getCurrentFullAddress();
  if (!addr) return false;
  return favorites.value.includes(addr);
});

// 3. 切换收藏状态
const toggleFavorite = () => {
  const addr = getCurrentFullAddress();
  if (!addr) return;
  
  if (favorites.value.includes(addr)) {
    // 如果已存在，则删除
    favorites.value = favorites.value.filter(item => item !== addr);
  } else {
    // 如果不存在，则添加 (添加到最前)
    favorites.value.unshift(addr);
  }
  localStorage.setItem('serverFavorites', JSON.stringify(favorites.value));
};

// 4. 删除指定收藏 (用于列表上的 X 按钮)
const removeFavorite = (addr) => {
  favorites.value = favorites.value.filter(h => h !== addr);
  localStorage.setItem('serverFavorites', JSON.stringify(favorites.value));
};


const applyTheme = () => {
  localStorage.setItem('theme', theme.value);
  let isDark = false;
  if (theme.value === 'system') {
    isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  } else {
    isDark = theme.value === 'dark';
  }
  isDarkMode.value = isDark; 
  if (isDark) document.documentElement.classList.add('dark');
  else document.documentElement.classList.remove('dark');
  
  if (chartData.value && resultData.value) {
    generateMockHistory(resultData.value.players.online, resultData.value.players.max);
  }
};
const selectTheme = (t) => { theme.value = t; showThemeMenu.value = false; applyTheme(); };

onMounted(() => {
  initPixels();
  animatePixels();
  window.addEventListener('mousemove', handleGlobalMouseMove);

  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) theme.value = savedTheme;
  applyTheme();
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    if (theme.value === 'system') applyTheme();
  });
  
  // 加载数据
  const savedHistory = localStorage.getItem('queryHistory');
  if (savedHistory) history.value = JSON.parse(savedHistory);
  
  const savedFavorites = localStorage.getItem('serverFavorites');
  if (savedFavorites) favorites.value = JSON.parse(savedFavorites);
  
  runDecryptEffect();
});

onUnmounted(() => {
  cancelAnimationFrame(animationFrameId);
  window.removeEventListener('mousemove', handleGlobalMouseMove);
});

const parsedMotd = computed(() => {
  if (!resultData.value?.motd) return '';
  let raw = resultData.value.motd;
  let text = typeof raw === 'string' ? raw : (raw.text || (raw.extra ? raw.extra.map(e => e.text).join('') : ''));
  return text.replace(/§[0-9a-fklmnor]/g, '').replace(/\n/g, '<br>');
});

const getInitial = (host) => host ? host.charAt(0).toUpperCase() : '?';
</script>

<template>
  <div class="spotlight-overlay" :style="{ '--mouse-x': mouseX + 'px', '--mouse-y': mouseY + 'px' }"></div>
  <div class="pixel-canvas">
    <div v-for="p in pixels" :key="p.id" class="pixel" :style="{ transform: `translate(${p.x}px, ${p.y}px)`, width: p.size + 'px', height: p.size + 'px', opacity: p.opacity }"></div>
  </div>

  <main class="relative h-screen w-full flex flex-col justify-center items-center p-6" @click="showThemeMenu = false">
    
    <!-- 右上角主题按钮 -->
    <div class="absolute top-6 right-6 z-50" @click.stop>
      <div class="relative">
        <button @click="showThemeMenu = !showThemeMenu" class="theme-toggle">
          <span class="text-xl leading-none">{{ theme === 'light' ? '☀️' : theme === 'dark' ? '🌙' : '💻' }}</span>
        </button>
        <transition name="fade">
          <div v-if="showThemeMenu" class="absolute top-full right-0 mt-3 w-40 app-card p-2 flex flex-col origin-top-right z-50">
            <button v-for="t in ['light', 'dark', 'system']" :key="t" @click="selectTheme(t)" class="text-left px-4 py-3 rounded-xl hover:bg-gray-100 dark:hover:bg-white/10 text-[14px] font-bold flex items-center gap-3 text-main transition-colors">
              <span>{{ t === 'light' ? '☀️' : t === 'dark' ? '🌙' : '💻' }}</span>
              {{ t === 'light' ? '浅色模式' : t === 'dark' ? '深色模式' : '跟随系统' }}
            </button>
          </div>
        </transition>
      </div>
    </div>

    <!-- 主容器 -->
    <div class="w-full max-w-[460px] relative z-10">
      <Transition name="fade" mode="out-in">
        
        <!-- === 搜索页 === -->
        <div v-if="status === 'idle'" key="search" class="flex flex-col gap-8">
          <div class="text-center mb-2">
            <h1 class="text-[44px] font-bold tracking-tight text-main mb-2 leading-tight decrypt-title" @mouseover="runDecryptEffect">{{ titleText }}</h1>
            <p class="text-sub font-semibold text-[13px] tracking-widest uppercase">Minecraft 实时查询工具</p>
          </div>
          <form @submit.prevent="queryServer()" class="flex flex-col gap-4">
            <div class="glow-border-wrapper" :class="{ active: isInputFocused }">
              <div class="glow-inner">
                <input v-model="serverAddress" type="text" placeholder="输入服务器地址 (如 hypixel.net)" class="app-input" style="border: none; background: transparent;" @focus="isInputFocused = true" @blur="isInputFocused = false" />
              </div>
            </div>
            <button type="submit" class="app-btn">开始查询</button>
          </form>

          <!-- 新增：我的收藏 (优先显示) -->
          <div v-if="favorites.length > 0" class="mt-4">
            <div class="flex items-center justify-between px-2 mb-3">
               <div class="flex items-center gap-2">
                 <span class="text-[14px]">❤️</span>
                 <span class="text-[11px] font-bold text-sub uppercase tracking-widest">我的收藏</span>
               </div>
            </div>
            <div class="flex flex-wrap gap-2.5">
              <TransitionGroup name="fade">
                <div v-for="item in favorites" :key="item" class="fav-tag group" @click="queryServer(item)">
                  <span>{{ item }}</span>
                  <button @click.stop="removeFavorite(item)" class="text-tertiary hover:text-red-500 transition-colors w-4 h-4 flex items-center justify-center text-[16px] leading-none">×</button>
                </div>
              </TransitionGroup>
            </div>
          </div>

          <!-- 历史记录 -->
          <div v-if="history.length > 0" class="mt-2">
            <div class="flex items-center justify-between px-2 mb-3">
              <div class="flex items-center gap-2">
                 <span class="text-[14px]">🕒</span>
                 <span class="text-[11px] font-bold text-sub uppercase tracking-widest">最近访问</span>
              </div>
            </div>
            <div class="flex flex-wrap gap-2.5">
              <TransitionGroup name="fade">
                <div v-for="item in history" :key="item" class="history-tag group" @click="queryServer(item)">
                  <span>{{ item }}</span>
                  <button @click.stop="removeHistory(item)" class="text-tertiary hover:text-red-500 transition-colors w-4 h-4 flex items-center justify-center text-[16px] leading-none">×</button>
                </div>
              </TransitionGroup>
            </div>
          </div>
        </div>

        <!-- === 结果页 === -->
        <div 
          v-else 
          key="result" 
          class="holo-card p-8 min-h-[500px] flex flex-col justify-between relative overflow-hidden"
          ref="cardRef"
          @mousemove="handleCardMouseMove"
          @mouseleave="resetCard"
        >
          <!-- 收藏按钮 (右上角) -->
          <div class="absolute top-6 right-6 z-20 pointer-events-auto">
            <button 
              class="fav-btn" 
              :class="{ active: isFavorited }" 
              @click="toggleFavorite"
              title="收藏/取消收藏"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" :fill="isFavorited ? 'currentColor' : 'none'" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </button>
          </div>
          
          <div v-if="status === 'loading'" class="flex-1 flex flex-col items-center justify-center gap-10">
            <div class="cube-loader">
              <div class="cube-face"></div><div class="cube-face"></div><div class="cube-face"></div>
              <div class="cube-face"></div><div class="cube-face"></div><div class="cube-face"></div>
              <div class="cube-core"></div>
            </div>
            <p class="text-sub font-bold text-[13px] tracking-widest uppercase animate-pulse">建立神经连接...</p>
          </div>

          <div v-if="status === 'success'" class="flex flex-col h-full z-10 pointer-events-none">
            <div class="flex flex-col items-center text-center gap-6 mb-6 pointer-events-auto">
              <div class="relative group cursor-default">
                <img v-if="resultData.favicon" :src="resultData.favicon" class="w-[80px] h-[80px] rounded-[24px] shadow-lg image-pixelated bg-gray-100 dark:bg-gray-800" />
                <div v-else class="w-[80px] h-[80px] rounded-[24px] shadow-lg flex items-center justify-center text-5xl font-bold transition-transform duration-500" style="background-color: var(--bg-input); color: var(--text-tertiary);">{{ getInitial(resultData.host) }}</div>
                <div class="absolute -bottom-1 -right-1 w-7 h-7 bg-[#34C759] border-[5px] rounded-full z-10" style="border-color: var(--bg-card);"></div>
              </div>
              <div>
                <h2 class="text-3xl font-bold text-main truncate max-w-[280px] mb-1 tracking-tight">{{ resultData.host }}</h2>
                <div class="inline-flex items-center px-3 py-1 rounded-full text-[12px] font-bold" style="background-color: var(--bg-input); color: var(--text-secondary);">版本 {{ resultData.version }}</div>
              </div>
            </div>

            <div class="rounded-[20px] p-5 mb-6 border border-transparent" style="background-color: var(--bg-input);">
              <div class="text-[14px] font-medium leading-relaxed text-center text-main" v-html="parsedMotd"></div>
            </div>

            <div class="grid grid-cols-2 gap-4 mb-6">
              <div class="p-4 rounded-[20px] text-center" style="background-color: var(--bg-input);">
                <div class="text-[11px] font-bold uppercase tracking-[0.05em] text-sub mb-1">在线人数</div>
                <div class="text-2xl font-bold text-main tracking-tight">{{ displayOnline }}</div>
              </div>
              <div class="p-4 rounded-[20px] text-center relative overflow-hidden" style="background-color: var(--bg-input);">
                <div class="text-[11px] font-bold uppercase tracking-[0.05em] text-sub mb-1">网络延迟</div>
                <div class="flex items-center justify-center gap-2">
                  <div class="text-2xl font-bold" :class="resultData.latency < 100 ? 'text-[#34C759]' : 'text-[#FF9F0A]'">{{ resultData.latency }}</div>
                  <span class="text-xs text-sub font-bold mt-2">ms</span>
                  <div class="sonar-container mt-2" :class="resultData.latency < 100 ? 'text-[#34C759]' : 'text-[#FF9F0A]'">
                    <div class="sonar-dot"></div><div class="sonar-wave"></div><div class="sonar-wave"></div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 历史趋势图 -->
            <div class="mb-6 pointer-events-auto">
               <div class="flex items-center justify-between mb-2 px-1">
                 <div class="text-[11px] font-bold uppercase tracking-[0.05em] text-sub">24H 活跃趋势</div>
               </div>
               <div class="rounded-[20px] p-2 border border-black/5 dark:border-white/5" style="background-color: var(--bg-input); height: 140px;">
                 <LineChart v-if="chartData" :chartData="chartData" :isDark="isDarkMode" />
               </div>
               <div class="text-center mt-2 opacity-60">
                 <p class="text-[10px] text-tertiary tracking-wide font-medium">* 数据基于算法模拟，仅供趋势参考</p>
               </div>
            </div>

            <button @click="status = 'idle'" class="app-btn mt-auto pointer-events-auto">
              查询其他服务器
            </button>
          </div>

          <div v-if="status === 'error'" class="flex-1 flex flex-col items-center justify-center text-center z-10">
            <div class="w-20 h-20 rounded-full flex items-center justify-center text-4xl mb-6" style="background-color: var(--bg-input); color: #FF3B30;">!</div>
            <h3 class="text-xl font-bold text-main mb-2">连接失败</h3>
            <p class="text-sub text-[15px] max-w-[260px] mb-8 leading-relaxed">{{ errorMessage }}</p>
            <button @click="status = 'idle'" class="text-main font-bold hover:opacity-70 text-sm">重试</button>
          </div>

        </div>
      </Transition>
    </div>
  </main>
</template>
