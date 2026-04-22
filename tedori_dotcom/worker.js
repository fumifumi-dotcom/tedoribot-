export default {
  async fetch(request) {
    const url = new URL(request.url);

    // www → 非www リダイレクト
    if (url.hostname === 'www.tedori-keisan.com') {
      url.hostname = 'tedori-keisan.com';
      return Response.redirect(url.toString(), 301);
    }

    // Pages.devにプロキシ
    const target = new URL('https://tedori-keisan.pages.dev' + url.pathname + url.search);
    const response = await fetch(target.toString(), {
      method: request.method,
      headers: request.headers,
    });

    // レスポンスヘッダーにセキュリティヘッダーを追加
    const newHeaders = new Headers(response.headers);
    newHeaders.set('X-Content-Type-Options', 'nosniff');
    newHeaders.set('X-Frame-Options', 'DENY');
    newHeaders.set('Referrer-Policy', 'strict-origin-when-cross-origin');

    return new Response(response.body, {
      status: response.status,
      headers: newHeaders,
    });
  },
};
