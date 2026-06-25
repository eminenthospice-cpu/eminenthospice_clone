/**
 * Cloudflare Pages Function — form submission proxy.
 *
 * Verifies the Cloudflare Turnstile token server-side, then forwards the
 * submission to the correct Formspree endpoint. The Turnstile secret never
 * reaches the browser. Forms POST here (multipart FormData) with a `form`
 * field naming which endpoint to use; the allowlist below prevents this from
 * acting as an open relay.
 *
 * Set the real secret with:
 *   npx wrangler pages secret put TURNSTILE_SECRET_KEY --project-name=eminenthospice-clone
 */

// Endpoint allowlist. Mirrors FORMS in src/data/site-config.ts (not secret).
const ENDPOINTS = {
  contact:  'https://formspree.io/f/mqevkdog',
  referral: 'https://formspree.io/f/mlgyewka',
};

const SITEVERIFY = 'https://challenges.cloudflare.com/turnstile/v0/siteverify';

function json(status, body) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'content-type': 'application/json' },
  });
}

export async function onRequestPost({ request, env }) {
  let form;
  try {
    form = await request.formData();
  } catch {
    return json(400, { error: 'bad-request' });
  }

  const target = ENDPOINTS[form.get('form')];
  if (!target) return json(400, { error: 'unknown-form' });

  // Honeypot: a real user never fills this. Pretend success and drop silently.
  if (form.get('_gotcha')) return json(200, { ok: true });

  const token = form.get('cf-turnstile-response');
  if (!token) return json(400, { error: 'turnstile-missing' });

  if (!env.TURNSTILE_SECRET_KEY) {
    return json(500, { error: 'turnstile-not-configured' });
  }

  // Verify the Turnstile token.
  const verify = await fetch(SITEVERIFY, {
    method: 'POST',
    headers: { 'content-type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      secret: env.TURNSTILE_SECRET_KEY,
      response: token,
      remoteip: request.headers.get('CF-Connecting-IP') || '',
    }),
  })
    .then((r) => r.json())
    .catch(() => ({ success: false }));

  if (!verify.success) return json(400, { error: 'turnstile-failed' });

  // Forward to Formspree, stripping routing/verification fields.
  form.delete('cf-turnstile-response');
  form.delete('form');

  const res = await fetch(target, {
    method: 'POST',
    headers: { Accept: 'application/json' },
    body: form,
  });

  if (res.ok) return json(200, { ok: true });

  const data = await res.json().catch(() => ({}));
  return json(res.status, { error: data?.errors?.[0]?.message || 'send-failed' });
}
