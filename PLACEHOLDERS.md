# Pre-Launch Placeholder Checklist

Every item below must be resolved before the site goes live.
Strike a row (or delete it) once the value is confirmed and updated.

---

## 1. Operational data (`src/data/site-config.ts`)

This is the **single file** to update for all contact / org data.
After editing, run `npm run build` to verify the build still passes.

| Field | Current value | Status |
|---|---|---|
| ~~`CONTACT.phone.display`~~ | ~~`(310) 555-1234`~~ | ✅ Updated to `(818) 824-3702` |
| ~~`CONTACT.phone.tel`~~ | ~~`+13105551234`~~ | ✅ Updated to `+18188243702` |
| ~~`CONTACT.email`~~ | ~~`info@eminentHospice.com`~~ | ✅ Updated to `eminenthospice@gmail.com` |
| ~~`CONTACT.address.street`~~ | ~~`''` (empty)~~ | ✅ Updated to `10999 Riverside Dr., Ste 306` |
| ~~`CONTACT.address.zip`~~ | ~~`''` (empty)~~ | ✅ Updated to `91602` |
| ~~`CONTACT.address.display`~~ | ~~`'Los Angeles, California'`~~ | ✅ Updated to full North Hollywood address |
| `SITE.url` | `https://www.eminenthospice.com` | ⏳ Pending - confirm with Mr. Lee |
| ~~`SITE.legalName`~~ | ~~`Eminent Hospice Care Inc.`~~ | ✅ Updated to `Eminent Hospice Care, Inc.` |
| `FORMS.contactEndpoint` | `…/REPLACE_ME_CONTACT` | ⏳ Pending - create form at formspree.io |
| `FORMS.referralEndpoint` | `…/REPLACE_ME_REFERRAL` | ⏳ Pending - same |
| `FORMS.careersEndpoint` | `…/REPLACE_ME_CAREERS` | ⏳ Pending - same |

---

## 2. Production domain (`astro.config.mjs`)

```js
site: 'https://www.eminenthospice.com',   // ← confirm / update
```

This value is used by `@astrojs/sitemap` and by canonical URL generation
in `BaseLayout.astro`. If it stays as `localhost` in production, Google will
reject the Search Console property.

---

## 3. Static assets (`public/`)

| File | Status | Notes |
|---|---|---|
| `public/favicon.svg` | Placeholder SVG | Replace with final branded favicon |
| `public/og-default.png` | Missing | Create a 1200×630 branded OG image; used as fallback for social sharing |
| `public/images/logo.png` | Missing | Drop any reasonable-size PNG here; referenced in `about` JSON-LD |

Once `public/images/logo.png` exists, add `"logo": "/images/logo.png"` to the
JSON-LD payload in `src/components/about/OrganizationJsonLd.astro` (if present)
or the `<script type="application/ld+json">` block on the About page.

---

## 4. Copy that needs client approval

### Testimonial (home page)

| Key (en.json + ko.json) | Status |
|---|---|
| ~~`home.testimonial.quote`~~ | ✅ Updated - real Google Review quote inserted |
| ~~`home.testimonial.attribution`~~ | ✅ Updated - "Daughter of patient · Google Review" |

### Founding story (About page)

~~`about.sections.story.body` (EN + KO) holds interim copy~~

✅ Updated - founding year 2018, current owner Hanna Cha, and official mission narrative from eminenthospice.com/about-us incorporated.

### Korean-speaking staff headcount (About page)

~~`about.sections.culturalCompetence.bullets.koreanStaff` currently says "Korean-speaking team members" without a count.~~

✅ Updated - "Nearly all of our team members speak Korean" (qualitative; no specific number per client guidance).

---

## 5. HIPAA Notice of Privacy Practices

The page at `/en/hipaa-notice` (and `/ko/hipaa-notice`) renders an interim
"document in preparation" block. When the client provides the final Notice text:

1. Replace `hipaaNotice.sections.interim.*` in `en.json` and `ko.json` with
   the canonical Notice sections:
   `uses`, `disclosures`, `patientRights`, `dutiesOfTheCoveredEntity`,
   `changesToNotice`, `complaints`, `contact`
2. Update the anchors array in `src/pages/en/hipaa-notice.astro` (and `ko/`).
3. Remove the `noIndex={true}` prop if the client wants the Notice indexed.

---

## 6. Complaint intake path (Hospice Laws page)

~~`hospiceLaws.sections.complaints.paths.eminent.contact` currently reads generically: "Call our office or use the Contact form."~~

✅ Updated - EN + KO now show:
- Direct line: (818) 824-3702 (24/7)
- Text-only: (213) 340-4429 (24/7)
- After-hours note: on-call nurse responds outside Monday–Friday 9 AM – 5 PM

**Verified values - do not change without re-verifying:**

| Key | Value | Source |
|---|---|---|
| `hospiceLaws.sections.complaints.paths.cdph.contact` | `(800) 228-1019` | CDPH Centralized Complaint Intake |
| `hospiceLaws.sections.complaints.paths.medicare.contact` | `1-800-MEDICARE (1-800-633-4227)` | Medicare Beneficiary Ombudsman |
| `hospiceLaws.sections.cops.cmsLinkUrl` | `https://www.ecfr.gov/…/part-418` | eCFR - 42 CFR Part 418 |
| `hospiceLaws.sections.patientRights.linkUrl` | `https://www.ecfr.gov/…/section-418.52` | eCFR - §418.52 |
| `insurance.sections.levels.aggregateCap.value` | `$35,361.44 per beneficiary` | CMS FY2026 Hospice Wage Index Final Rule |

---

## 7. Annual re-review dates

Medical / regulatory content pages carry a `lastReviewed` date.
Set a calendar reminder for **September each year** to re-verify these pages
against the new federal fiscal year (CMS updates publish in October).

| Page key | Current `lastReviewed` | Re-review by |
|---|---|---|
| `understandingHospice.lastReviewed` | `2026-05-01` | 2026-09 |
| `hospiceLaws.lastReviewed` | `2026-05-01` | 2026-09 |
| `insurance.lastReviewed` | `2026-05-01` | 2026-09 (FY2027 rates publish July–Aug) |
| `forFamilies.lastReviewed` | `2026-05-21` | 2027-09 |
| `faq.lastReviewed` | `2026-05-21` | 2027-09 |

---

## 8. Korean copy - native review pass

The Korean translations are drafted from the original Korean-language source
material using the hybrid convention `한국어 (English)` for regulated /
branded terms (Medicare, Medi-Cal, POLST, HIPAA, SNF, etc.).

A formal native-speaker review pass is recommended before launch. Particular
attention:

- `home.levels.respite.title` - `임시 위탁 케어` (regulatory meaning of
  short-term inpatient caregiver relief, not literal "rest care")
- Team role titles in `home.team.roles.*.name` - confirm against Korean-American
  healthcare provider usage in LA County
- `forFamilies.sections.basics.oxygen.safetyNote` - confirm 5-foot / no-flames
  wording matches Eminent's own admission training materials
- Day 3 regulatory terms: `룸 앤 보드`, `다학제`, `너싱홈/SNF`, `종말기`
- Testimonial Korean - update together with the English version

---

## 9. Analytics (decision required)

No analytics script is wired. Confirm with client before launch:

| Option | CCPA banner needed? | How to add |
|---|---|---|
| Plausible (cookieless) | No | Add `<script>` tag in `BaseLayout.astro` |
| Vercel Analytics (cookieless) | No | Add `@vercel/analytics/astro` integration |
| Google Analytics 4 | **Yes** | Add GA4 snippet + cookie consent banner; update `privacy.sections.dataCollected.cookies` |

---

## 10. Post-deploy steps

- [ ] Verify production domain resolves correctly
- [ ] Run [securityheaders.com](https://securityheaders.com) scan on production domain
- [ ] Submit `https://www.eminenthospice.com/sitemap-index.xml` to Google Search Console
- [ ] Run Lighthouse on at least: Home, Services, FAQ, Contact, HIPAA Notice
  - Target: Performance ≥ 90, Accessibility ≥ 95, Best Practices ≥ 95, SEO ≥ 95
- [ ] Test all three forms end-to-end (submit → confirm email received in Formspree inbox)
- [ ] Confirm phone `tel:` link dials correctly on mobile
- [ ] Check both locale switchers (`/en/` ↔ `/ko/`) on every page type

---

*Last updated: 2026-05-28*
