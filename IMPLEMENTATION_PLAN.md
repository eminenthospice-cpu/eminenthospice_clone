# Implementation Plan - Incorporate Business Info into the Website

## Context

The user consolidated real business data into [`BUSINESS_INFO.md`](BUSINESS_INFO.md): legal/operational contact details, a Google-Review testimonial, founding facts (year 2018, current owner Hanna Cha), compliance hotlines, the bilingual-staff messaging, and the official logo (SVG).

The site is a bilingual Astro 6 build with **all org data centralized in two surfaces**:

1. **`src/data/site-config.ts`** - typed constants (`SITE`, `CONTACT`, `BRAND`, `ACCREDITATIONS`) consumed by layouts, JSON-LD, and `tel:` links.
2. **`src/i18n/en.json` + `src/i18n/ko.json`** - mirrored translation dictionaries with footer values, testimonial copy, the founding story (`about.sections.story.body`), the cultural-competence bullets, and the compliance complaints block.

Currently these surfaces hold drafted placeholders (`(310) 555-1234`, `info@eminentHospice.com`, generic testimonial, no street address, missing logo file). The pre-launch checklist at [`PLACEHOLDERS.md`](PLACEHOLDERS.md) enumerates exactly the same gaps the user now has answers for. The goal is to flip every newly-confirmed value from placeholder to real - but **only** the values the user has actually confirmed. Two items the user explicitly deferred (production domain, final HIPAA Notice) stay placeholder.

Verified against the live site (`eminenthospice.com/about-us`) so the mission/values copy matches the official source.

---

## What changes

### A. Logo asset (new file)

- **Copy** `/Users/seonho_kim/Downloads/Eminent_Hospice_Logo_no_back_ground-.svg` → `public/images/logo.svg`.
- Decision: SVG-only (scales perfectly, smaller, no rasterization). No PNG export.
- `eminentSign.pdf` is a signature document, not a web asset - do not import.

### B. `src/data/site-config.ts` - single source of truth

Replace these fields (current line numbers shown):

| Line | Field | New value |
|---|---|---|
| 19 | `CONTACT.phone.display` | `(818) 824-3702` |
| 20 | `CONTACT.phone.tel` | `+18188243702` |
| 22 | `CONTACT.email` | `eminenthospice@gmail.com` |
| 24 | `CONTACT.address.street` | `10999 Riverside Dr., Ste 306` |
| 25 | `CONTACT.address.city` | `North Hollywood` (was `Los Angeles`) |
| 27 | `CONTACT.address.zip` | `91602` |
| 29 | `CONTACT.address.display` | `10999 Riverside Dr., Ste 306, North Hollywood, CA 91602` |
| 11 | `SITE.legalName` | `Eminent Hospice Care, Inc.` (add comma) |
| 36 | `BRAND.logo` | `/images/logo.svg` (was `.png`) |

**Not changing in this pass** (user-deferred):

- `SITE.url` - user said "ask Mr. Lee about domain" → leave the existing `https://www.eminenthospice.com`.
- `FORMS.contactEndpoint` / `referralEndpoint` / `careersEndpoint` - Formspree IDs not provided.

### C. `src/i18n/en.json` and `src/i18n/ko.json` - keep mirrored

Both files edited together so structure stays parity.

**Footer block** (en.json line 35–37 + ko.json same):

- `footer.address` → `10999 Riverside Dr., Ste 306, North Hollywood, CA 91602` (street stays English in both - existing pattern keeps US addresses untranslated)
- `footer.phone` → `(818) 824-3702`
- `footer.email` → `eminenthospice@gmail.com`

**Final CTA on home page** (en.json line 167–168 + ko.json):

- `home.finalCta.phoneNumberTel` → `+18188243702`
- `home.finalCta.phoneNumberDisplay` → `(818) 824-3702`

**Testimonial block** (en.json ~line 155–159 + ko.json):

- `home.testimonial.provenance` → EN: `Google Review` / KO: `구글 리뷰`
- `home.testimonial.quote` → full text of the Google Review (English). Quote stays in English in **both** locales - it is an authentic Google Review, and translating would misrepresent the source. KO version is the same English quote with a one-line Korean lead-in ("한 가족이 남긴 영문 리뷰입니다:").
- `home.testimonial.attributionName` → EN: `Daughter of patient` / KO: `환자 따님`
- `home.testimonial.attributionRelation` → EN: `Google Review` / KO: `구글 리뷰`

**About / story** (en.json ~line 567–569 + ko.json):

Rewrite `about.sections.story.body` using the official mission narrative pulled from eminenthospice.com/about-us + the new facts. Suggested EN body:

> Founded in 2018, Eminent Hospice Care provides an individualized program of physical, emotional, spiritual, and psychosocial care for people in the last phases of a life-limiting illness, with an emphasis on control of pain and other symptoms. Under the leadership of current owner Hanna Cha, our team works to alleviate as much pain, worry, and inconvenience as possible for patients and families facing serious illness - with a particular commitment to the Korean-American community of greater Los Angeles, whose families have long needed care delivered in their own language.

KO body: parallel translation, preserving the year and owner reference.

**Cultural competence - Korean staff bullet** (en.json line 590 + ko.json):

- EN: `Nearly all of our team members speak Korean - clinical, admissions, and on-call support - so families can have every conversation in their preferred language.`
- KO: `저희 팀 거의 모든 구성원이 한국어로 소통할 수 있습니다 - 임상, 입원 상담, 24시간 온콜 지원까지 모든 단계를 모국어로 진행하실 수 있습니다.`

(User said "all staff Korean available except a few" - no specific number, so messaging stays qualitative.)

**Compliance complaints block** (en.json line 398–401 + ko.json):

- `hospiceLaws.sections.complaints.paths.eminent.contact` → EN: `Direct line: (818) 824-3702 (24/7). Text-only: (213) 340-4429 (24/7). After business hours (Monday–Friday, 9 AM – 5 PM), our on-call nurse responds.` / KO: parallel translation with the same two numbers.

### D. Out of scope (explicitly deferred per user)

- **Production domain confirmation** → user is checking with Mr. Lee. `SITE.url` and `astro.config.mjs` `site:` field stay as-is.
- **HIPAA Notice of Privacy Practices** → user wrote "don't know what this means." No edits to `src/pages/en/hipaa-notice.astro`, `ko/hipaa-notice.astro`, or `hipaaNotice.*` i18n keys. Interim placeholder block stays in place.
- **`PLACEHOLDERS.md` cleanup** → at the end of execution, strike rows 1, 4 (testimonial + story + Korean staff), and 6 (compliance hotline). Leave rows 2 (domain), 3 (favicon/OG), 5 (HIPAA), 7–10 untouched.

---

## Critical files

- [`src/data/site-config.ts`](src/data/site-config.ts) - ~9 fields
- [`src/i18n/en.json`](src/i18n/en.json) - 6 key blocks updated
- [`src/i18n/ko.json`](src/i18n/ko.json) - same 6 blocks, mirrored
- [`public/images/logo.svg`](public/images/logo.svg) - new file (copied from Downloads)
- [`PLACEHOLDERS.md`](PLACEHOLDERS.md) - strike resolved rows
- [`BUSINESS_INFO.md`](BUSINESS_INFO.md) - already exists; no edit needed

---

## Verification

Dev server is already running at `http://localhost:4321` (Astro 6). After applying changes:

1. **Hot reload** the home page (`/en` and `/ko`) and confirm:
   - Header logo renders (the new SVG appears top-left)
   - Footer shows `(818) 824-3702`, `eminenthospice@gmail.com`, full North Hollywood address
   - Final CTA "Call Now" `tel:` link uses `+18188243702`
   - Testimonial reads the Google Review quote, attributed "Daughter of patient · Google Review"
2. **Navigate to `/en/about`** and `/ko/about`:
   - Founding story shows "Founded in 2018" + Hanna Cha + official mission language
   - Cultural-competence bullet says "Nearly all of our team members speak Korean…"
3. **Navigate to `/en/hospice-laws`** and `/ko/hospice-laws` → "How to File a Complaint" block shows the two compliance numbers + after-hours nurse note.
4. **Run `npm run build`** to confirm typed config still compiles and sitemap generates.
5. **Spot-check JSON-LD** on the home page via DevTools or `view-source:` - `OrganizationJsonLd.astro` should include `logo: "/images/logo.svg"` and the corrected address.
6. **Screenshot the home page** at desktop + mobile widths to confirm the SVG logo scales correctly.

If verification passes, the only remaining pre-launch unknowns are the four items the user/client still owe: production domain, Formspree endpoints, OG image, and final HIPAA Notice text.
