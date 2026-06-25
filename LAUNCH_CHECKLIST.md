# Pre-Launch Checklist - Eminent Hospice

**Status as of 2026-06-22.** Verified against the current code in `astro-rewrite`,
cross-referenced with `PLACEHOLDERS.md` and `QA_REPORT.md`. Items marked ❌ are
still open in the codebase.

---

## 🔴 Hard blockers (site is broken without these)

| # | Item | Status | Owner |
|---|------|--------|-------|
| 1 | **Forms go nowhere** - all 3 endpoints are still `https://formspree.io/f/REPLACE_ME_*` in `src/data/site-config.ts`. Contact, Referral, and Careers submissions are silently discarded. | ❌ open | Client: create Formspree forms (or another backend); then wire in the real IDs |
| 2 | **OG image 404s on every page** - `og-default.png` is referenced site-wide in `<meta og:image>` but the file does not exist in `public/`. Every social / text-message link preview is broken. | ❌ open | Generate a 1200×630 branded image |
| 3 | **Production domain unconfirmed** - `SITE.url` and `astro.config.mjs` assume `https://www.eminenthospice.com`. If that is not the live domain, canonical URLs, sitemap, and hreflang are all wrong. | ⏳ confirm | Client confirms domain |

---

## 🟡 Should-fix (wrong / embarrassing info shown to users)

| # | Item | Status |
|---|------|--------|
| 4 | **Literal `{retentionDays}` text** renders on the Privacy page - the token is never substituted (`src/pages/en/privacy.astro:94` outputs `s.retention.body` with no `.replace()`). Users see "for approximately {retentionDays} days." | ❌ open |
| 5 | **Inconsistent contact email** - footer / business info use `eminenthospice@gmail.com`, but the Contact, Careers, and Privacy pages still say `info@eminenthospice.com` (5 spots in `en.json`, same in `ko.json`). May point users at a dead inbox. | ❌ open |
| 6 | **About pages emit zero JSON-LD** - `about.astro` uses `<OrganizationJsonLd slot="head" />`, but `BaseLayout` has no `head` slot, so Astro silently drops it. | ❌ open |
| 7 | **FAQ pages missing FAQ structured data** - `FaqPageJsonLd.astro` exists but is never imported / used. Lost rich-result SEO on a key page. | ❌ open |
| 8 | **Resources dropdown a11y** - `aria-expanded` is hardcoded "false"; the menu is hover/focus-only, so touch users on large screens (e.g. iPad landscape) can't open it. | ❌ open |
| 9 | **Privacy copy claims Cloudflare Turnstile**, but the forms only use a honeypot. Either add Turnstile or correct the copy. | ❌ open |

---

## 🟢 Content / decisions needed from the client

- **HIPAA Notice** (`/hipaa-notice`) still renders an interim "document in preparation" block - needs the final Notice of Privacy Practices text.
- **Analytics** - none wired. Decide Plausible (cookieless, easy) vs GA4 (requires a cookie-consent banner + privacy-copy update).
- **Real photography** - several hero / section images are Unsplash placeholders (flagged `TODO: client photo` in `src/data/images.ts`).
- **Favicon / logo** - favicon is a placeholder SVG; `public/images/logo.png` (referenced by JSON-LD) is missing.
- **`robots.txt`** - missing from `public/`.

---

## ✅ Post-deploy steps

- [ ] Verify production domain resolves correctly.
- [ ] Run [securityheaders.com](https://securityheaders.com) scan on the production domain.
- [ ] Submit `sitemap-index.xml` to Google Search Console.
- [ ] Run Lighthouse on Home, Services, FAQ, Contact, HIPAA Notice (targets: Perf ≥ 90, A11y ≥ 95, Best Practices ≥ 95, SEO ≥ 95).
- [ ] Test all 3 forms end-to-end (submit → confirm email received).
- [ ] Confirm phone `tel:` link dials correctly on mobile.
- [ ] Check both locale switchers (`/en/` ↔ `/ko/`) on every page type.

---

## Quick triage

Items **2 and 4–9** are code fixes that can be done now. The items genuinely
requiring the client are **#1 (form backend), #3 (domain), HIPAA text, the
analytics decision, and real photos.**
