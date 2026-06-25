# QA Report - Eminent Hospice (Astro site)

**Date:** 2026-06-14
**Scope:** All 16 page types × EN/KO (32 pages) + shared nav/footer/forms. Verification only - no code changes made.
**Method:** Production build, static HTML analysis of all 32 built pages, runtime checks in the browser, interactive feature testing, responsive + accessibility checks.

---

## Summary

The site is **functionally healthy** - it builds, every page loads, navigation / language-switching / forms / mobile menu all work, and EN/KO parity is perfect. **No crashes, broken routes, or console-breaking errors were found.**

The real defects are concentrated in: two launch blockers (form delivery, OG image), a couple of visible data bugs (`{retentionDays}` token, inconsistent email), and structured-data / ARIA gaps (about & FAQ JSON-LD, Resources dropdown). Fixing items 1–9 would get this launch-ready from a UI/UX-correctness standpoint.

---

## ✅ What's working (verified)

- **Build is clean** - 33 pages compile, sitemap generates, no errors/warnings.
- **All 32 routes return 200**, each with exactly **one `<h1>`** and a populated `<title>`.
- **EN/KO translation parity is perfect** - 0 missing keys in either direction (no blank text from missing translations).
- **Language switcher preserves the page** - e.g. `/en/privacy` → `/ko/privacy`, not just home. Verified on subpages.
- **Contact form client validation works** - empty submit produces proper `role="alert"` errors and blocks submission.
- **Mobile drawer works** - opens/closes, `aria-expanded` toggles, body scroll-locks, closes on Escape & link click.
- **Responsive: no horizontal overflow at 375px**; hamburger correctly replaces desktop nav.
- **All 20 `<img>` have alt text.** Home images load (10/10).
- **SEO basics solid** - every page has title, description, canonical, OG tags; `hreflang` (en/ko/x-default) correct; `noindex` correctly limited to privacy/hipaa/terms.
- Astro's own dev audit reported no a11y/perf issues on the pages checked.

---

## 🔴 Blockers (must fix before launch)

| # | Issue | Where | Detail |
|---|-------|-------|--------|
| 1 | **Forms don't deliver** | Contact, Referral, Careers | All 3 endpoints are `https://formspree.io/f/REPLACE_ME_*`. Client-side validation works, but every submission goes nowhere. *(Known client task - needs real Formspree IDs or another backend.)* |
| 2 | **OG image 404s on every page** | all 32 pages | `og-default.png` is referenced in `<meta og:image>` site-wide but the file doesn't exist in `public/` or `dist/`. Social/link previews will be broken. |

---

## 🟡 Should-fix (real, mostly user-visible)

| # | Issue | Where | Detail |
|---|-------|-------|--------|
| 3 | **Literal `{retentionDays}` shown to users** | `/en/privacy`, `/ko/privacy` | The retention paragraph renders "…retained… for approximately **{retentionDays} days**…". The token is never substituted (`privacy.astro` outputs `s.retention.body` with no `.replace()`). Visually confirmed. |
| 4 | **Inconsistent contact email** | Contact, Careers, Privacy pages | These show **`info@eminenthospice.com`** while the footer and business info use **`eminenthospice@gmail.com`**. On the Contact page this is especially risky - it may point users at a non-existent inbox. |
| 5 | **About pages emit no structured data** | `/en/about`, `/ko/about` | `about.astro` uses `<OrganizationJsonLd slot="head" />`, but `BaseLayout` has **no `name="head"` slot** - so Astro silently drops it. About pages ship zero JSON-LD. |
| 6 | **FAQ pages missing FAQ structured data** | `/en/faq`, `/ko/faq` | A `FaqPageJsonLd.astro` component exists but is **never imported/used**. Missed rich-result SEO on a key page. |
| 7 | **Resources dropdown `aria-expanded` always "false"** | header (all pages) | Hardcoded; never updates when the menu opens. Screen readers always announce it collapsed. |
| 8 | **Resources dropdown is hover/focus-only** | header (desktop ≥1024px) | No click handler (`cursor-default`). Touch users on large screens (e.g. iPad landscape) can't open it. Mitigation: those 6 links also exist in the footer and are keyboard-reachable. |
| 9 | **Privacy policy claims Turnstile, but forms don't use it** | forms vs privacy copy | Privacy page says "Cloudflare Turnstile… prevents bot submissions," but the Astro forms only have a honeypot. Either add Turnstile or correct the copy. |

---

## 🟢 Minor / polish

| # | Issue | Detail |
|---|-------|--------|
| 10 | Stale data in i18n (currently unused) | `common.phone` = `(310) 555-1234` and `aboutJsonLd.telephone` = `+13105551234` are dead data today, but will surface as wrong info if ever wired up. |
| 11 | Resources button missing `aria-controls` | Panel has no `id` to reference. |
| 12 | Mobile drawer has no focus trap | Focus isn't moved into the drawer on open and can escape to background content. |
| 13 | Home depends on 10 external Unsplash images | Runtime dependency on a third-party CDN; these are placeholder photos, not owned assets. |
| 14 | `logo.svg` is ~1.5 MB | Looks like an export artifact; heavy for a header logo. |

---

## Known pre-launch placeholders (not new bugs)

These are intentional gaps from the project's own checklist, not QA defects: HIPAA Notice interim page, no analytics wired, production domain placeholder, and pending Korean native-copy review.

---

## Bottom line

No crashes, broken routes, or console-breaking errors. The actionable defects are items **1–9**; fixing them gets the site launch-ready from a UI/UX-correctness standpoint. Items 3, 4, 5, 6, 7, 8 are code-only fixes that do not require client input.
