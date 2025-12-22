import { ImageResponse } from '@vercel/og';

// 告诉 Vercel 在 Edge 环境运行此函数，速度超快！
export const config = {
  runtime: 'edge',
};

// 主处理函数
export default async function handler(request) {
  try {
    // 1. 从 URL 中解析查询参数
    const { searchParams } = new URL(request.url);

    // 获取服务器 IP，如果不存在则提供一个默认值
    const ip = searchParams.get('ip') || 'mc.hypixel.net';
    
    // 获取 MOTD (服务器标语)，进行简单的颜色代码清理
    const motd = (searchParams.get('motd') || 'A Minecraft Server').replace(/§[0-9a-fk-or]/g, '');

    // 获取在线人数和最大人数
    const online = searchParams.get('online') || 'N/A';
    const max = searchParams.get('max') || 'N/A';

    // 2. 异步加载字体 (可选，但能让你的图片更好看)
    // 我们从 Google Fonts 加载一个开源字体
    const fontData = await fetch(
      'https://fonts.gstatic.com/s/notosanssc/v35/k3k_oo52o_wA2sOaxLM1PjM3-_0ncy_e8W-v.ttf',
    ).then((res) => res.arrayBuffer());

    // 3. 使用 ImageResponse 生成图片
    // 这里就像写 HTML 和 CSS 一样！我们用 Tailwind CSS 来快速设计样式。
    return new ImageResponse(
      (
        <div
          style={{
            height: '100%',
            width: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: '#222', // 深色背景
            color: 'white',
            fontFamily: '"Noto Sans SC"', // 使用加载的字体
            fontSize: 28,
          }}
        >
          <div style={{ fontSize: 48, marginBottom: 20, color: '#5EEAD4' }}>
            MC 服务器状态
          </div>
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            border: '2px solid #555',
            borderRadius: 12,
            padding: '20px 40px',
            alignItems: 'center',
            backgroundColor: '#333'
          }}>
            <div style={{ marginBottom: 15, fontSize: 32 }}>
              {ip}
            </div>
            <div style={{ marginBottom: 20, color: '#ccc' }}>
              {motd}
            </div>
            <div style={{ display: 'flex', alignItems: 'center', fontSize: 40 }}>
              <div style={{ 
                  width: 18, 
                  height: 18, 
                  backgroundColor: '#34D399', // 绿色状态点
                  borderRadius: '50%', 
                  marginRight: 15 
              }} />
              <span>{online}</span>
              <span style={{ color: '#888', margin: '0 10px' }}>/</span>
              <span>{max}</span>
            </div>
          </div>
          <div style={{ position: 'absolute', bottom: 20, right: 30, color: '#666', fontSize: 18 }}>
            由 mc-monitor 生成
          </div>
        </div>
      ),
      {
        width: 1200, // 标准 OG 图片宽度
        height: 630, // 标准 OG 图片高度
        fonts: [
          {
            name: 'Noto Sans SC', // 字体名称
            data: fontData,       // 字体文件数据
            style: 'normal',
          },
        ],
      },
    );
  } catch (e) {
    console.error(e);
    return new Response(`Failed to generate image`, { status: 500 });
  }
}
