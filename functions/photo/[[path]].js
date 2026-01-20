export async function onRequest(context) {
  const { request, env } = context;
  const path = context.params.path.join('/');

  try {
    // Get the object from R2
    const object = await env.PHOTOS.get(`nomilivegallery/${path}`);

    if (!object) {
      return new Response('Photo not found', { status: 404 });
    }

    // Return the object with appropriate headers
    const headers = new Headers();
    headers.set('Content-Type', object.httpMetadata?.contentType || 'image/jpeg');
    headers.set('Cache-Control', 'public, max-age=31536000'); // Cache for 1 year
    headers.set('Access-Control-Allow-Origin', '*');
    headers.set('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS');

    return new Response(object.body, {
      headers: headers,
    });
  } catch (error) {
    console.error('Error fetching from R2:', error);
    return new Response('Error fetching photo', { status: 500 });
  }
}
