// R2 Photo Serving Function - Updated 2026-01-21
export async function onRequest(context) {
  const { request, env } = context;
  const path = context.params.path.join('/');

  // Debug: Check if PHOTOS binding exists
  if (!env.PHOTOS) {
    console.error('R2 binding PHOTOS not found in env');
    return new Response('R2 binding not configured. Please check Pages Functions settings.', {
      status: 500,
      headers: { 'Content-Type': 'text/plain' }
    });
  }

  try {
    // Get the object from R2
    const object = await env.PHOTOS.get(path);

    if (!object) {
      return new Response(`Photo not found: ${path}`, { status: 404 });
    }

    // Return the object with appropriate headers
    const headers = new Headers();
    headers.set('Content-Type', object.httpMetadata?.contentType || 'image/jpeg');
    headers.set('Cache-Control', 'public, max-age=31536000');
    headers.set('Access-Control-Allow-Origin', '*');
    headers.set('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS');

    return new Response(object.body, { headers });
  } catch (error) {
    console.error('Error fetching from R2:', error);
    return new Response(`Error: ${error.message}`, { status: 500 });
  }
}
