// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  site: 'https://eminenthospice.com', // Production custom domain (apex; www redirects here)
  trailingSlash: 'never',

  // Emit `en.html` instead of `en/index.html` so Cloudflare Pages serves
  // no-slash URLs (/en, /en/services) at 200 - matching trailingSlash:'never'
  // and the no-slash canonical tags, avoiding 308 redirect hops.
  build: {
    format: 'file',
  },

  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'ko'],
    routing: {
      prefixDefaultLocale: true, // /en and /ko both prefixed
    },
  },

  vite: {
    plugins: [tailwindcss()],
  },

  // Auto-hashes every inline script/style Astro emits and injects a per-page
  // <meta> CSP for script-src/style-src - avoids hand-maintained hashes that
  // would silently go stale (and break the page) on the next content edit.
  // frame-ancestors is intentionally NOT set here: the CSP spec ignores it
  // when delivered via <meta>, so it lives in public/_headers instead.
  security: {
    csp: {
      scriptDirective: {
        resources: ["'self'", 'https://challenges.cloudflare.com'],
      },
      directives: [
        "base-uri 'self'",
        "form-action 'self'",
        "img-src 'self' data: https:",
        "media-src 'self'",
        "connect-src 'self' https://challenges.cloudflare.com",
        "frame-src https://challenges.cloudflare.com https://www.youtube-nocookie.com",
      ],
    },
  },

  integrations: [
    sitemap({
      filter: (page) => ![
        'https://eminenthospice.com',
        'https://eminenthospice.com/',
      ].includes(page),
      i18n: {
        defaultLocale: 'en',
        locales: {
          en: 'en-US',
          ko: 'ko-KR',
        },
      },
    }),
  ],
});
