/**
 * Eminent Hospice - i18n utilities
 * Provides a dot-notation t() function backed by en.json / ko.json.
 */
import en from './en.json';
import ko from './ko.json';
import { SITE } from '../data/site-config';

export type Locale = 'en' | 'ko';

const translations: Record<Locale, Record<string, unknown>> = { en, ko };

/** Extract locale from Astro URL (e.g. /en/about to 'en', /ko/about to 'ko') */
export function getLangFromUrl(url: URL): Locale {
  const [, lang] = url.pathname.split('/');
  if (lang === 'ko') return 'ko';
  return 'en';
}

/** Returns a t() function scoped to the given locale. */
export function useTranslations(lang: Locale) {
  return function t(key: string, fallback?: string): string {
    const keys = key.split('.');

    // Try requested locale first
    let value: unknown = translations[lang];
    for (const k of keys) {
      if (value && typeof value === 'object') {
        value = (value as Record<string, unknown>)[k];
      } else {
        value = undefined;
        break;
      }
    }

    // Fallback to English
    if (value === undefined) {
      value = translations['en'];
      for (const k of keys) {
        if (value && typeof value === 'object') {
          value = (value as Record<string, unknown>)[k];
        } else {
          value = undefined;
          break;
        }
      }
    }

    if (typeof value === 'string') return value;
    return fallback ?? key;
  };
}

/** Localized path helper - prepends /en or /ko */
export function localizedPath(path: string, lang: Locale): string {
  const clean = path.startsWith('/') ? path : `/${path}`;
  if (clean === '/') return `/${lang}`;
  return `/${lang}${clean}`;
}

/** hreflang alternate links for SEO */
export function buildAlternates(path: string): Array<{ lang: string; href: string }> {
  const base = SITE.url; // single source of truth; must match astro.config.mjs `site`
  const p = path === '/' ? '' : path;
  return [
    { lang: 'en',       href: `${base}/en${p}` },
    { lang: 'ko',       href: `${base}/ko${p}` },
    { lang: 'x-default', href: `${base}/en${p}` },
  ];
}
