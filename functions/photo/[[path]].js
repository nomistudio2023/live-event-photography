/**
 * Cloudflare Pages Function - R2 Photo Proxy
 * 
 * 此 Function 用於代理 Cloudflare R2 存儲的照片
 * 路徑: /photo/* 或 /photo/2026-01-20/*.jpg
 * 
 * R2 綁定配置 (wrangler.toml):
 * [[r2_buckets]]
 * binding = "GALLERY"
 * bucket_name = "nomilivegallery"
 */

export async function onRequest(context) {
  const { request, env } = context;
  const url = new URL(request.url);
  
  // 取得路徑參數 (例如: "2026-01-20/IMG_1234.jpg" 或 "manifest.json")
  const path = context.params.path || '';
  
  // 構建 R2 中的完整路徑
  // 如果路徑是 "photo/2026-01-20/IMG_1234.jpg"，需要移除 "photo/" 前綴
  let r2Path = path;
  if (r2Path.startsWith('photo/')) {
    r2Path = r2Path.substring(6); // 移除 "photo/" 前綴
  }
  
  try {
    // 從 R2 取得物件
    const object = await env.GALLERY.get(r2Path);
    
    if (!object) {
      return new Response('Photo not found', { status: 404 });
    }
    
    // 取得物件內容
    const headers = new Headers();
    
    // 設定 Content-Type
    if (r2Path.endsWith('.jpg') || r2Path.endsWith('.jpeg')) {
      headers.set('Content-Type', 'image/jpeg');
    } else if (r2Path.endsWith('.png')) {
      headers.set('Content-Type', 'image/png');
    } else if (r2Path.endsWith('.webp')) {
      headers.set('Content-Type', 'image/webp');
    } else if (r2Path.endsWith('.json')) {
      headers.set('Content-Type', 'application/json');
    } else {
      headers.set('Content-Type', 'application/octet-stream');
    }
    
    // 設定緩存策略
    // 照片: 長期緩存（1年）
    // manifest.json: 短期緩存（5分鐘），但前端會加時間戳繞過
    if (r2Path.endsWith('.json')) {
      headers.set('Cache-Control', 'public, max-age=300, must-revalidate');
    } else {
      headers.set('Cache-Control', 'public, max-age=31536000, immutable');
    }
    
    // CORS 標頭（如果需要）
    headers.set('Access-Control-Allow-Origin', '*');
    headers.set('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS');
    
    // 返回物件內容
    return new Response(object.body, {
      status: 200,
      headers: headers
    });
    
  } catch (error) {
    console.error('R2 Error:', error);
    return new Response('Internal Server Error', { status: 500 });
  }
}
