/**
 * Eminent Hospice — Image slot registry
 * Ported from EminentHospiceWebsite/src/lib/imageSlots.ts
 *
 * Photos are self-hosted under /public/images/photos/<key>.webp.
 * To use real client photography, drop a file at the same path (keep the
 * dimensions). See PLACEHOLDERS.md for the photography brief per slot.
 */

export interface ImageSlot {
  src: string;
  alt: { en: string; ko: string };
  blurDataURL?: string;
  credit?: string;
  width: number;
  height: number;
}

/** Neutral warm-cream 8×8 blur placeholder. Matches surface-paper. */
const DEFAULT_BLUR =
  'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAAIAAgDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAj/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFAEBAAAAAAAAAAAAAAAAAAAAAP/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/AKgAAB//2Q==';

export const imageSlots = {
  // ── Home ──────────────────────────────────────────────────
  homeHero: {
    src: '/images/photos/homeHero.webp',
    alt: { en: 'Doctor laughing with an older patient during a visit', ko: '진료 중 어르신 환자와 웃고 있는 의사' },
    blurDataURL: DEFAULT_BLUR, credit: 'Photo source: eminenthospice.com', width: 1600, height: 1000,
  },
  homePhilosophyPortrait: {
    src: '/images/photos/homePhilosophyPortrait.webp',
    alt: { en: 'Caregiver gently holding an older adult’s hand', ko: '어르신의 손을 부드럽게 잡고 있는 돌봄 제공자' },
    blurDataURL: DEFAULT_BLUR, credit: 'Photo source: eminenthospice.com', width: 1200, height: 1500,
  },
  homeLevelRoutine: {
    src: '/images/photos/homeLevelRoutine.webp',
    alt: { en: 'Older adult’s hands resting on a cane with support nearby', ko: '곁의 도움을 받으며 지팡이를 잡고 있는 어르신의 손' },
    blurDataURL: DEFAULT_BLUR, credit: 'Photo source: eminenthospice.com', width: 1000, height: 750,
  },
  homeLevelContinuous: {
    src: '/images/photos/homeLevelContinuous.webp',
    alt: { en: 'Hospice care team standing together in a clinic setting', ko: '진료 공간에서 함께 서 있는 호스피스 케어팀' },
    blurDataURL: DEFAULT_BLUR, credit: 'Photo source: eminenthospice.com', width: 1000, height: 750,
  },
  homeLevelInpatient: {
    src: '/images/photos/homeLevelInpatient.webp',
    alt: { en: 'Quiet inpatient room with hospital beds prepared for care', ko: '케어를 위해 준비된 조용한 입원실 침대' },
    blurDataURL: DEFAULT_BLUR, credit: 'Stock photo', width: 1000, height: 750,
  },
  // ── About ─────────────────────────────────────────────────
  aboutHero: {
    src: '/images/photos/aboutHero.webp',
    alt: { en: 'Four older adults sitting on indoor swings', ko: '실내 그네에 앉아 있는 네 명의 어르신' },
    blurDataURL: DEFAULT_BLUR, credit: 'Photo source: eminenthospice.com', width: 1600, height: 1000,
  },
  // ── Services ──────────────────────────────────────────────
  servicesHero: {
    src: '/images/photos/servicesHero.webp',
    alt: { en: 'Clinical staff member working in a medical lab', ko: '의료 실험실에서 일하는 임상 직원' },
    blurDataURL: DEFAULT_BLUR, credit: 'Stock photo', width: 1600, height: 1000,
  },
  // ── Families ──────────────────────────────────────────────
  familiesHero: {
    src: '/images/photos/familiesHero.webp',
    alt: { en: 'Older adult’s hands resting together in quiet light', ko: '조용한 빛 속에 모은 어르신의 손' },
    blurDataURL: DEFAULT_BLUR, credit: 'Stock photo', width: 1600, height: 1000,
  },
  // ── Contact ───────────────────────────────────────────────
  contactHero: {
    src: '/images/photos/contactHero.webp',
    alt: { en: 'Books, pencils, and small blocks arranged on a desk', ko: '책상 위에 놓인 책, 연필, 작은 블록' },
    blurDataURL: DEFAULT_BLUR, credit: 'Stock photo', width: 1600, height: 1000,
  },
  // ── Grief Support (new page) ──────────────────────────────
  griefHero: {
    src: '/images/photos/griefHero.webp',
    alt: { en: 'Yellow wildflowers blooming in bright daylight', ko: '밝은 햇살 속에 핀 노란 야생화' },
    blurDataURL: DEFAULT_BLUR, credit: 'Stock photo', width: 1600, height: 1000,
  },
} as const satisfies Record<string, ImageSlot>;

export type ImageSlotKey = keyof typeof imageSlots;

export function getImage(key: ImageSlotKey, lang: 'en' | 'ko' = 'en'): ImageSlot & { altText: string } {
  const slot = imageSlots[key];
  return { ...slot, altText: slot.alt[lang] };
}
