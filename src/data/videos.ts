import type { Locale } from '../i18n/utils';

export interface VideoResource {
  slug: string;
  youtubeId: string;
  videoPath: string;
  title: Record<Locale, string>;
  description: Record<Locale, string>;
  sourcePath: string;
}

export const VIDEO_RESOURCES: VideoResource[] = [
  {
    slug: 'polst',
    youtubeId: '42r5f9uf-0U',
    videoPath: '/videos/polst.mp4',
    title: { en: 'Understanding POLST', ko: 'POLST에 관하여' },
    description: {
      en: 'A Korean-language introduction to POLST and documenting serious-illness care wishes.',
      ko: 'POLST와 중증 질환 치료 의사를 기록하는 방법을 소개하는 한국어 영상입니다.',
    },
    sourcePath: '/hospice-laws',
  },
  {
    slug: 'hospice-core-services',
    youtubeId: 'K0bgtz2gV40',
    videoPath: '/videos/hospice-core-services.mp4',
    title: { en: 'FAQ: What Services Does Hospice Provide?', ko: 'FAQ: 호스피스에서 제공하는 서비스' },
    description: {
      en: 'A Korean-language overview of the services patients and families can expect from hospice.',
      ko: '환자와 가족이 호스피스에서 받을 수 있는 주요 서비스를 소개합니다.',
    },
    sourcePath: '/services',
  },
  {
    slug: 'hospice-myths',
    youtubeId: 'v9-onN7EsWo',
    videoPath: '/videos/hospice-myths.mp4',
    title: { en: 'FAQ: Does Hospice Make Death Come Sooner?', ko: 'FAQ: 호스피스를 하면 빨리 돌아가시나요?' },
    description: {
      en: 'A Korean-language discussion of a common hospice misconception.',
      ko: '호스피스에 대한 흔한 오해를 설명하는 한국어 영상입니다.',
    },
    sourcePath: '/understanding-hospice',
  },
  {
    slug: 'after-death-hospice',
    youtubeId: 'XeGjlf7fILA',
    videoPath: '/videos/after-death-hospice.mp4',
    title: { en: 'After Death: Hospice Patient', ko: '임종 후 절차: 호스피스 환자' },
    description: {
      en: 'Korean-language guidance about what families should do after a hospice patient dies.',
      ko: '호스피스 환자가 임종한 뒤 가족이 해야 할 일을 안내합니다.',
    },
    sourcePath: '/for-families',
  },
  {
    slug: 'after-death-non-hospice-polst',
    youtubeId: 'SNGsCjicC8E',
    videoPath: '/videos/after-death-non-hospice-polst.mp4',
    title: { en: 'After Death: Patient Not Enrolled in Hospice', ko: '임종 후 절차: 호스피스 환자가 아닌 경우' },
    description: {
      en: 'Korean-language guidance for a death that occurs when the person is not enrolled in hospice.',
      ko: '호스피스를 이용하지 않는 상황에서 임종이 발생했을 때의 절차를 안내합니다.',
    },
    sourcePath: '/hospice-laws',
  },
  {
    slug: 'end-of-life-timing',
    youtubeId: '3mgBE6CaI4I',
    videoPath: '/videos/end-of-life-timing.mp4',
    title: { en: 'FAQ: Estimating Time Near the End of Life', ko: 'FAQ: 임종 시기 이해하기' },
    description: {
      en: 'Korean-language guidance for families wondering when the end of life may be approaching.',
      ko: '임종이 가까워지는 시기에 대해 가족에게 안내하는 한국어 영상입니다.',
    },
    sourcePath: '/for-families',
  },
  {
    slug: 'nebulizer',
    youtubeId: 'edmwae3Iglk',
    videoPath: '/videos/nebulizer.mp4',
    title: { en: 'How to Use a Nebulizer', ko: '네뷸라이저 사용법' },
    description: {
      en: 'A Korean-language demonstration of setting up and using a nebulizer.',
      ko: '네뷸라이저를 준비하고 사용하는 방법을 보여주는 한국어 영상입니다.',
    },
    sourcePath: '/for-families',
  },
  {
    slug: 'oxygen-concentrator',
    youtubeId: 'Vq5rIpelzhk',
    videoPath: '/videos/oxygen-concentrator.mp4',
    title: { en: 'How to Use an Oxygen Concentrator', ko: '산소발생기 사용법' },
    description: {
      en: 'A Korean-language demonstration of the oxygen equipment used in hospice care.',
      ko: '호스피스에서 사용하는 산소 장비의 사용법을 보여주는 한국어 영상입니다.',
    },
    sourcePath: '/for-families',
  },
  {
    slug: 'suction-machine',
    youtubeId: '9g98EDnOAUI',
    videoPath: '/videos/suction-machine.mp4',
    title: { en: 'How to Use a Suction Machine', ko: '흡인기 사용법' },
    description: {
      en: 'A Korean-language demonstration of using a suction machine.',
      ko: '흡인기를 사용하는 방법을 보여주는 한국어 영상입니다.',
    },
    sourcePath: '/for-families',
  },
  {
    slug: 'hospice-aide-perspective',
    youtubeId: 'qWl3XdJ4rck',
    videoPath: '/videos/hospice-aide-perspective.mp4',
    title: { en: 'A Hospice Aide Explains Hospice', ko: '호스피스 도우미가 이야기하는 호스피스' },
    description: {
      en: 'A Korean-language staff perspective on supporting hospice patients and families.',
      ko: '호스피스 도우미가 환자와 가족을 지원하는 경험을 이야기합니다.',
    },
    sourcePath: '/about',
  },
  {
    slug: 'hospice-nurse-perspective',
    youtubeId: 'jsPCywsMe5Y',
    videoPath: '/videos/hospice-nurse-perspective.mp4',
    title: { en: 'A Nurse Explains Hospice', ko: '간호사가 이야기하는 호스피스' },
    description: {
      en: 'A Korean-language nurse perspective on hospice care.',
      ko: '간호사가 호스피스 돌봄에 대해 설명하는 한국어 영상입니다.',
    },
    sourcePath: '/about',
  },
  {
    slug: 'american-hospice-nurse',
    youtubeId: 'xnI28GlZwZI',
    videoPath: '/videos/american-hospice-nurse.mp4',
    title: { en: 'A Nurse Answers Questions About Hospice in the United States', ko: '간호사가 이야기하는 궁금한 미국의 호스피스' },
    description: {
      en: 'A Korean-language nurse discussion about how hospice works in the United States.',
      ko: '간호사가 미국의 호스피스 제도에 관한 궁금증을 설명합니다.',
    },
    sourcePath: '/about',
  },
  {
    slug: 'emergency-medications',
    youtubeId: 'Rv1Cbnb4QDA',
    videoPath: '/videos/emergency-medications.mp4',
    title: { en: 'Hospice Comfort and Emergency Medications', ko: '호스피스 응급약 소개' },
    description: {
      en: 'A Korean-language introduction to comfort and emergency medications used in hospice.',
      ko: '호스피스에서 사용하는 편안함 및 응급 약물을 소개합니다.',
    },
    sourcePath: '/for-families',
  },
  {
    slug: 'chaplain-perspective',
    youtubeId: '2Ci1inVJrrc',
    videoPath: '/videos/chaplain-perspective.mp4',
    title: { en: 'A Chaplain Explains Hospice', ko: '채플린이 이야기하는 호스피스' },
    description: {
      en: 'A Korean-language chaplain perspective on spiritual care and hospice support.',
      ko: '채플린이 영적 돌봄과 호스피스 지원에 대해 이야기합니다.',
    },
    sourcePath: '/about',
  },
];

export const getVideo = (slug: string) =>
  VIDEO_RESOURCES.find((video) => video.slug === slug);
