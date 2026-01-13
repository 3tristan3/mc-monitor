import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  // 本地开发代理
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    }
  },
  // 打包配置 (新增)
  build: {
    outDir: 'dist', // 确保输出目录叫 dist，与 vercel.json 对应
  }
})
