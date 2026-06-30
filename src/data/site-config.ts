/**
 * Eminent Hospice - Centralized Site Configuration
 *
 * All org-specific placeholders live here.
 * Update these values before going live.
 * See also: PLACEHOLDERS.md (ported from Next.js app)
 */

export const SITE = {
  name:     'Eminent Hospice Care',
  legalName:'Eminent Hospice Care, Inc.',
  tagline:  'Comfort. Dignity. Compassion.',
  url:      'https://eminenthospice-clone.pages.dev', // Cloudflare Pages URL (swap to custom domain when acquired)
  locale:   'en-US',
} as const;

export const CONTACT = {
  phone: {
    display: '(818) 824-3702',
    tel:     '+18188243702',
  },
  email:   'eminenthospice@gmail.com',
  address: {
    street:   '10999 Riverside Dr., Ste 306',
    city:     'North Hollywood',
    state:    'CA',
    zip:      '91602',
    country:  'US',
    display:  '10999 Riverside Dr., Ste 306, North Hollywood, CA 91602',
  },
  hours:   'Available 24 hours a day, 7 days a week',
  regions: 'Greater Los Angeles and Orange County',
} as const;

export const BRAND = {
  logo:          '/images/logo.png',
  favicon:       '/favicon.svg',
  ogImageDefault:'/og-default.png',
} as const;

export const FORMS = {
  contactEndpoint:  'https://formspree.io/f/mqevkdog',
  referralEndpoint: 'https://formspree.io/f/mlgyewka',
} as const;

export const TURNSTILE = {
  /**
   * Cloudflare Turnstile site key (public, safe to commit).
   *
   * Production uses the real widget key below. Also set the matching secret on
   * the Pages project (NOT committed):
   *   npx wrangler pages secret put TURNSTILE_SECRET_KEY --project-name=eminenthospice-clone
   * The server-side check lives in functions/api/submit.js.
   */
  siteKey: '0x4AAAAAADpPbjFtS1-557HJ',
} as const;

export const ACCREDITATIONS = [
  'Medicare Certified',
  'Available 24/7',
  'English & Korean',
] as const;

export const SOCIAL = {
  // Add when social profiles are created
} as const;
