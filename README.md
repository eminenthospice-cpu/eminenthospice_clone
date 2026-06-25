# Eminent Hospice Care - Website (Astro rebuild)

Static, bilingual (EN / KO) marketing site for Eminent Hospice Care, built with
**Astro 6 + Tailwind CSS v4**. No server runtime required - output is a folder of
plain HTML/CSS files that can be hosted anywhere.

---

## Prerequisites

| Tool | Minimum version |
|---|---|
| Node.js | **22.12.0** (see `engines` in `package.json`) |
| npm | 10+ (ships with Node 22) |

Check your version: `node -v`

---

## Install & run locally

```bash
# 1. Install dependencies
npm install

# 2. Start the dev server  (hot-reload, http://localhost:4321)
npm run dev

# 3. Build for production  (output → ./dist/)
npm run build

# 4. Preview the production build locally
npm run preview
```

The dev server address is always `http://localhost:4321`.
All pages are prefixed by locale - e.g. `/en/` and `/ko/`.
Visiting `/` redirects to `/en/`.

---

## Project structure

```
eminent-astro/
├── public/                   # Static assets served as-is
│   ├── favicon.svg
│   └── og-default.png        # TODO: replace with branded OG image
│
├── src/
│   ├── data/
│   │   └── site-config.ts    # ★ PRIMARY: phone, address, Formspree endpoints
│   │
│   ├── i18n/
│   │   ├── en.json           # All English copy
│   │   ├── ko.json           # All Korean copy (must mirror en.json structure)
│   │   └── utils.ts          # useTranslations(), localizedPath()
│   │
│   ├── layouts/
│   │   ├── BaseLayout.astro      # Head, header, footer, hreflang, skip-link
│   │   └── LongFormLayout.astro  # Prose + sticky sidebar for content/legal pages
│   │
│   ├── components/
│   │   ├── layout/           # Header, Footer, PageSidebar, …
│   │   ├── forms/            # ContactForm, ReferralCallbackForm, CareersForm
│   │   ├── ui/               # Icon, Button, …
│   │   └── motion/           # reveal.ts (IntersectionObserver, reduced-motion-aware)
│   │
│   ├── pages/
│   │   ├── index.astro       # Redirects / → /en/
│   │   ├── en/               # All English pages
│   │   └── ko/               # All Korean pages (mirrors en/ exactly)
│   │
│   └── styles/
│       └── global.css        # Tailwind v4 @theme tokens + base styles
│
├── astro.config.mjs          # Astro config - site URL, i18n, sitemap
├── PLACEHOLDERS.md           # Pre-launch content checklist
└── package.json
```

---

## Page inventory (33 pages total)

| Route (EN) | Korean equivalent | Notes |
|---|---|---|
| `/en/` | `/ko/` | Home |
| `/en/about` | `/ko/about` | |
| `/en/services` | `/ko/services` | |
| `/en/for-families` | `/ko/for-families` | |
| `/en/grief-support` | `/ko/grief-support` | |
| `/en/understanding-hospice` | `/ko/understanding-hospice` | noIndex: false |
| `/en/hospice-laws` | `/ko/hospice-laws` | noIndex: false |
| `/en/insurance` | `/ko/insurance` | noIndex: false |
| `/en/faq` | `/ko/faq` | noIndex: false |
| `/en/contact` | `/ko/contact` | |
| `/en/referral` | `/ko/referral` | |
| `/en/careers` | `/ko/careers` | |
| `/en/privacy` | `/ko/privacy` | noIndex: true |
| `/en/hipaa-notice` | `/ko/hipaa-notice` | noIndex: true |
| `/en/terms` | `/ko/terms` | noIndex: true |
| `/en/accessibility` | `/ko/accessibility` | |
| `/` | - | Redirects → `/en/` |

---

## Editing content

### 1. Org-wide data (phone, address, Formspree)

Open **`src/data/site-config.ts`** - this is the single source of truth for all
operational values that appear across multiple pages.

```ts
export const CONTACT = {
  phone: {
    display: '(310) 555-1234',   // ← replace
    tel:     '+13105551234',      // ← replace (E.164 format)
  },
  email: 'info@eminentHospice.com', // ← replace
  address: { street: '', zip: '', … },
};

export const FORMS = {
  contactEndpoint:  'https://formspree.io/f/REPLACE_ME_CONTACT',  // ← replace
  referralEndpoint: 'https://formspree.io/f/REPLACE_ME_REFERRAL', // ← replace
  careersEndpoint:  'https://formspree.io/f/REPLACE_ME_CAREERS',  // ← replace
};
```

### 2. Page copy (bilingual)

All copy lives in **`src/i18n/en.json`** and **`src/i18n/ko.json`**.
The two files must have identical key structures - every key in `en.json` must
exist in `ko.json`.

Leaf strings that contain `{phone}` are interpolated at build time in the
relevant `.astro` file using `.replace('{phone}', CONTACT.phone.display)`.

### 3. Adding a new page

1. Create `src/pages/en/my-page.astro` and `src/pages/ko/my-page.astro`.
2. Add i18n keys under a new top-level key in both JSON files.
3. Use `LongFormLayout` (for prose/legal) or `BaseLayout` (for anything else).
4. Add the route to the nav in `src/components/layout/Header.astro` if needed.

### 4. Production domain

Update **two** places before deploying:

- `astro.config.mjs` → `site: 'https://www.eminenthospice.com'`
- `src/data/site-config.ts` → `SITE.url`

---

## Forms (Formspree)

The site uses [Formspree](https://formspree.io) for form submissions - no server
required. Each form POSTs via `fetch()` to its endpoint URL.

**Setup:**
1. Create a free Formspree account.
2. Create three forms: Contact, Referral Callback, Careers.
3. Paste the endpoint IDs into `src/data/site-config.ts → FORMS.*`.

All three forms include:
- A hidden honeypot field (`_gotcha`) for bot filtering.
- Client-side validation with accessible error messages.
- AJAX submission with success / error state (no page reload).

---

## Sitemap & SEO

`@astrojs/sitemap` auto-generates `/sitemap-index.xml` at build time.
hreflang alternate links are injected by `BaseLayout.astro` on every page.

Pages flagged `noIndex={true}` (privacy, hipaa-notice, terms) emit
`<meta name="robots" content="noindex,nofollow">` and are excluded from the
sitemap automatically.

After deploying to production:
1. Go to [Google Search Console](https://search.google.com/search-console).
2. Verify the production domain.
3. Submit `https://www.eminenthospice.com/sitemap-index.xml`.

---

## Accessibility

- WCAG 2.1 AA target.
- Skip-to-main-content link (`.skip-link`) on every page.
- All interactive elements have ≥ 44×44 px tap targets.
- `prefers-reduced-motion: reduce` suppresses all CSS transitions and the
  IntersectionObserver reveal animations.
- `scroll-behavior: smooth` is gated behind `prefers-reduced-motion: no-preference`.
- Focus rings: 2px solid `primary-500`, 3px offset, on all `:focus-visible` elements.
- Korean text uses `word-break: keep-all` to prevent mid-syllable line breaks.

---

## Deployment

The build output (`./dist/`) is a folder of static files. Deploy to any static
host:

### Netlify (recommended)
```
Build command:  npm run build
Publish dir:    dist
Node version:   22
```

### Vercel
```
Framework:      Astro
Output dir:     dist
Node version:   22
```

### Other (Nginx, S3 + CloudFront, etc.)
Serve the `dist/` directory. Configure the server to return `dist/en/index.html`
for unknown routes (the `index.astro` redirect handles `/` → `/en/`).

---

## Pre-launch checklist

See **`PLACEHOLDERS.md`** for the full itemized list. Quick summary:

- [ ] Replace placeholder phone number in `src/data/site-config.ts`
- [ ] Replace placeholder address (street + ZIP) in `src/data/site-config.ts`
- [ ] Replace three Formspree endpoint IDs in `src/data/site-config.ts`
- [ ] Update production domain in `astro.config.mjs` and `site-config.ts`
- [ ] Drop `public/og-default.png` (1200×630 branded OG image)
- [ ] Drop `public/favicon.svg` (final branded favicon)
- [ ] Drop `public/images/logo.png` (for JSON-LD structured data)
- [ ] Replace illustrative testimonial copy in `en.json` / `ko.json`
- [ ] Replace `about.sections.story.body` with client-confirmed founding story
- [ ] Commission native Korean copy review pass
- [ ] Provide final HIPAA Notice of Privacy Practices text (replaces interim)
- [ ] Submit sitemap to Google Search Console
- [ ] Run Lighthouse on production (target: Perf ≥ 90, A11y ≥ 95, SEO ≥ 95)
