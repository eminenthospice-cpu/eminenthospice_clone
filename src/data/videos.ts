import type { Locale } from '../i18n/utils';

export interface VideoResource {
  slug: string;
  title: Record<Locale, string>;
  description: Record<Locale, string>;
  videoSrc: string;
  captionSrc: string;
  sourcePath: string;
}

export const VIDEO_RESOURCES: VideoResource[] = [
  {
    slug: 'hospice-core-services',
    title: {
      en: 'FAQ: What Services Does Hospice Provide?',
      ko: '호스피스 핵심 서비스',
    },
    description: {
      en: 'An overview of the hospice services patients and families can expect from the care team.',
      ko: '환자와 가족이 호스피스 팀으로부터 받을 수 있는 주요 서비스를 소개합니다.',
    },
    videoSrc: '/videos/hospice-core-services-korean-english-subtitles.mp4',
    captionSrc: '/captions/hospice-core-services-korean-english-subtitles.en.vtt',
    sourcePath: '/services',
  },
  {
    slug: 'hospice-team-interview',
    title: {
      en: 'Hospice team interview',
      ko: '호스피스 팀 인터뷰',
    },
    description: {
      en: 'Younghee Kim discusses how hospice team members support patients and families.',
      ko: '김영희 님이 호스피스 팀이 환자와 가족을 어떻게 돕는지 설명합니다.',
    },
    videoSrc: '/videos/hospice-team-interview-younghee-kim-korean-english-subtitles.mp4',
    captionSrc: '/captions/hospice-team-interview-younghee-kim-korean-english-subtitles.en.vtt',
    sourcePath: '/about',
  },
  {
    slug: 'hospice-nurse-interview',
    title: {
      en: 'Hospice nurse interview',
      ko: '호스피스 간호사 인터뷰',
    },
    description: {
      en: 'A hospice nurse explains clinical support, comfort care, and family communication.',
      ko: '호스피스 간호사가 임상 지원, 편안한 돌봄, 가족과의 소통을 설명합니다.',
    },
    videoSrc: '/videos/hospice-nurse-interview-janice-korean-english-subtitles.mp4',
    captionSrc: '/captions/hospice-nurse-interview-janice-korean-english-subtitles.en.vtt',
    sourcePath: '/about',
  },
  {
    slug: 'spiritual-care-chaplain',
    title: {
      en: 'Spiritual care / chaplain interview',
      ko: '영적 돌봄 / 채플린 인터뷰',
    },
    description: {
      en: 'Peter Park shares how spiritual care and chaplain support help patients and families during hospice.',
      ko: '박피터 님이 호스피스에서 영적 돌봄과 채플린 지원이 환자와 가족을 어떻게 돕는지 소개합니다.',
    },
    videoSrc: '/videos/hospice-social-work-bereavement-interview-peter-park-korean-english-subtitles.mp4',
    captionSrc: '/captions/hospice-social-work-bereavement-interview-peter-park-korean-english-subtitles.en.vtt',
    sourcePath: '/about',
  },
  {
    slug: 'hospice-myths',
    title: {
      en: 'Most Frequently Asked Questions by Families',
      ko: '호스피스에 대한 오해',
    },
    description: {
      en: 'A plain-language discussion of common hospice misconceptions and what families should know.',
      ko: '호스피스에 대한 흔한 오해와 가족이 알아야 할 내용을 쉽게 설명합니다.',
    },
    videoSrc: '/videos/hospice-myths-korean-english-subtitles.mp4',
    captionSrc: '/captions/hospice-myths-korean-english-subtitles.en.vtt',
    sourcePath: '/understanding-hospice',
  },
  {
    slug: 'end-of-life-timing',
    title: {
      en: 'FAQ: What is your estimate of the remaining time?',
      ko: '임종 시기 이해하기',
    },
    description: {
      en: 'Guidance for families wondering when end of life may be approaching and when to ask for help.',
      ko: '임종이 가까워지는 시기와 도움을 요청해야 할 때를 가족에게 안내합니다.',
    },
    videoSrc: '/videos/end-of-life-timing-korean-english-subtitles.mp4',
    captionSrc: '/captions/end-of-life-timing-korean-english-subtitles.en.vtt',
    sourcePath: '/for-families',
  },
  {
    slug: 'after-death-hospice',
    title: {
      en: 'After death: hospice patient',
      ko: '임종 후 절차: 호스피스 환자',
    },
    description: {
      en: 'What families should do after a hospice patient dies, including who to call first.',
      ko: '호스피스 환자가 임종한 뒤 가족이 가장 먼저 해야 할 일과 연락 순서를 안내합니다.',
    },
    videoSrc: '/videos/after-death-hospice-korean-english-subtitles.mp4',
    captionSrc: '/captions/after-death-hospice-korean-english-subtitles.en.vtt',
    sourcePath: '/for-families',
  },
  {
    slug: 'polst',
    title: {
      en: 'POLST education',
      ko: 'POLST 안내',
    },
    description: {
      en: 'An introduction to POLST forms and how they can document serious-illness care wishes.',
      ko: 'POLST 양식과 중증 질환 치료 의사를 기록하는 방법을 소개합니다.',
    },
    videoSrc: '/videos/polst-korean-english-subtitles.mp4',
    captionSrc: '/captions/polst-korean-english-subtitles.en.vtt',
    sourcePath: '/hospice-laws',
  },
  {
    slug: 'after-death-non-hospice-polst',
    title: {
      en: 'After death: non-hospice and POLST',
      ko: '임종 후 절차: 비호스피스와 POLST',
    },
    description: {
      en: 'What families should know when death occurs outside hospice, especially when POLST is involved.',
      ko: '호스피스를 이용하지 않는 상황에서 임종이 발생했을 때, 특히 POLST와 관련해 알아야 할 내용을 설명합니다.',
    },
    videoSrc: '/videos/after-death-non-hospice-polst-korean-english-subtitles.mp4',
    captionSrc: '/captions/after-death-non-hospice-polst-korean-english-subtitles.en.vtt',
    sourcePath: '/hospice-laws',
  },
];
