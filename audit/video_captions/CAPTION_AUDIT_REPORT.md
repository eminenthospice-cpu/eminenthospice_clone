# Video Caption Audit

Date: 2026-06-22

## Scope

Audited all 9 MP4 files in `public/videos`.

Method:
- Generated timestamped Whisper translation transcripts for spoken audio.
- Generated 16-sample subtitle-area contact sheets per video.
- Compared visible burned-in English captions against the spoken-audio timing windows and basic meaning/wording quality.

Important limitation: this is an automated ASR/visual audit, not a certified Korean medical/legal translation review. The results are still strong enough to show the current burned-in English captions are not publication-ready.

## Overall Result

Fail. The captions are generally present and often appear near the correct speaking moment, but the English text is frequently incomplete, mistranslated, grammatically broken, or contextually wrong. Because the captions are burned into the MP4s and there are no separate `.srt` or `.vtt` files in the repo, fixes require re-captioning and re-rendering the videos.

## Per-Video Findings

| Video | Result | Representative Issues |
| --- | --- | --- |
| `after-death-hospice-korean-english-subtitles.mp4` | Fail | Fragmented/mistranslated captions such as "patient's fault," "There is a nurse I know," and incomplete procedural captions. |
| `after-death-non-hospice-polst-korean-english-subtitles.mp4` | Fail | Contextually wrong terms such as "prosecutor's office" for coroner-related content; odd phrases like "pre-healing order" and incomplete procedure descriptions. |
| `end-of-life-timing-korean-english-subtitles.mp4` | Fail | Fragmented captions such as "will of life," "Some people may not be able to live for a," and "go back in a few hours if." |
| `hospice-core-services-korean-english-subtitles.mp4` | Fail | Incomplete captions and clear nonsense ending: "Thank you for your hard work in 2014." |
| `hospice-myths-korean-english-subtitles.mp4` | Fail | Awkward/inaccurate captions such as "keep the vaccination," "too many drugs," and "medicine for sure even if they can't eat." |
| `hospice-nurse-interview-janice-korean-english-subtitles.mp4` | Fail | Korean question banners are clear, but English captions are fragmented: "We help patients with various reasons to," "looked at the patient's head," "we were not accept the patient." |
| `hospice-social-work-bereavement-interview-peter-park-korean-english-subtitles.mp4` | Fail | Name mismatch: visible caption says "Peter Bang" while the site/lower-third identify Peter Park; other captions are fragmentary. |
| `hospice-team-interview-younghee-kim-korean-english-subtitles.mp4` | Fail | Awkward/incomplete captions such as "equipment and equipment provided," "hair cut or if they need a massage," and "need help." |
| `polst-korean-english-subtitles.mp4` | Fail | Medical-form wording issues such as "Part D is the last name"; several sampled moments show no English caption while speaker appears active. |

## Generated Evidence

- Manifest: `audit/video_captions/manifest.json`
- Contact sheets: `audit/video_captions/sheets/`
- Whisper transcripts: `audit/video_captions/transcripts/`
- Full-frame samples: `audit/video_captions/frames/`
- Editable WebVTT drafts: `public/captions/`

## Fix Applied

Added editable English WebVTT caption files for all 9 videos and wired every video embed in both `/en` and `/ko` routes to its matching track with the label `Corrected English`.

Build verification passed with `pnpm run build` after adding the bundled Node runtime to `PATH`.

Second fix pass: clean source videos from `C:\Users\emine\Downloads` were mapped by duration, rendered with the generated captions burned in, and copied over all 9 files in `public/videos`.

Source mapping:
- `videoplayback (1).mp4` -> `hospice-core-services-korean-english-subtitles.mp4`
- `videoplayback (2).mp4` -> `hospice-myths-korean-english-subtitles.mp4`
- `videoplayback (3).mp4` -> `after-death-hospice-korean-english-subtitles.mp4`
- `videoplayback (4).mp4` -> `after-death-non-hospice-polst-korean-english-subtitles.mp4`
- `videoplayback (5).mp4` -> `end-of-life-timing-korean-english-subtitles.mp4`
- `videoplayback (6).mp4` -> `hospice-team-interview-younghee-kim-korean-english-subtitles.mp4`
- `videoplayback (7).mp4` -> `hospice-nurse-interview-janice-korean-english-subtitles.mp4`
- `videoplayback (8).mp4` -> `hospice-social-work-bereavement-interview-peter-park-korean-english-subtitles.mp4`
- `videoplayback.mp4` -> `polst-korean-english-subtitles.mp4`

The previous burned-caption videos were backed up to `audit/caption_render/previous_burned_caption_videos/`. Rendered working copies and visual QA sheets are under `audit/caption_render/`.

The WebVTT tracks remain in the page markup for accessibility/editability, but they are no longer marked `default` so they do not duplicate the burned-in captions during normal playback.

Important remaining limitation: the English text is derived from automated speech translation plus terminology cleanup. Placement and timing have been applied, but a Korean-English medical/hospice reviewer should still review the caption wording before treating these as final clinical translations.

## Recommendation

Have the WebVTT/ASS text reviewed by a Korean-English reviewer familiar with hospice/medical terminology, then rerun `tools/render_captioned_videos.py` if wording changes are needed.

## 2026-06-23 Seekability and Burned-Caption QA

Implemented a follow-up QA pass for the current rendered MP4s.

Artifacts:
- Exhaustive review manifest: `audit/seek_caption_qa/review_manifest.json`
- Human-readable QA report: `audit/seek_caption_qa/REPORT.md`
- Browser seek results: `audit/seek_caption_qa/browser_seek_results.json`
- Per-video review sheets and timestamped frame evidence: `audit/seek_caption_qa/sheets/` and `audit/seek_caption_qa/frames/`

Seekability result: Pass. Browser automation checked all 18 embedded video instances across the 10 English/Korean routes with video embeds. Every embed had native controls, loaded metadata duration, allowed keyboard seeking forward and backward, and had no default/showing VTT track that would duplicate the burned-in captions. The browser harness could not directly call media `play()` or assign `currentTime` because the in-app browser exposes media elements through a read-only wrapper, so the seek check used native focus plus ArrowRight/ArrowLeft keyboard interaction.

Caption timing result: Pass for cue coverage. The QA script checked 1,062 detected speech intervals and 3,181 timestamped frame samples. The editable VTT timing covered all detected speech intervals with 0 timing gaps.

Burned-caption visual/wording result: Needs human review before treating the captions as final. The generated sheets show captions are generally visible and not cut off, but 199 sampled frames were flagged for low caption-region contrast or very short rolling fragments during continuous speech. The most affected videos were:
- `after-death-hospice-korean-english-subtitles.mp4` - 53 visibility/continuity flags.
- `after-death-non-hospice-polst-korean-english-subtitles.mp4` - 99 visibility/continuity flags.
- `end-of-life-timing-korean-english-subtitles.mp4` - 19 visibility/continuity flags.
- `hospice-core-services-korean-english-subtitles.mp4` - 4 visibility/continuity flags.
- `hospice-myths-korean-english-subtitles.mp4` - 24 visibility/continuity flags.

Manual visual inspection of the generated flagged sheets found captions present in the reviewed frames, but several moments show only one-word or very short English fragments while the speaker is visibly still talking. These should be reviewed for caption continuity and translation quality by a Korean-English reviewer familiar with hospice/medical terminology.

## 2026-06-23 Caption Remediation Pass

Implemented a master-caption pipeline and re-rendered all 9 videos from the clean source MP4s in `C:\Users\emine\Downloads`.

What changed:
- Added phrase-level master caption files under `audit/caption_master/`.
- Updated `tools/render_captioned_videos.py` so each master caption source generates both the burned-in `.ass` captions and the matching WebVTT accessibility track.
- Re-rendered all 9 MP4s into `audit/caption_render/rendered_master/` and copied them into `public/videos/`.
- Regenerated all 9 WebVTT files in `public/captions/`.
- Kept VTT tracks available in the page markup without marking them `default`, so they do not duplicate the burned-in captions during normal playback.

Final QA result: Pass for technical timing, visual presence, and browser seekability.
- Caption QA checked 1,062 detected speech intervals and 3,181 timestamped frame samples.
- Timing gaps: 0 across all videos.
- Visibility flags: 0 across all videos.
- Browser seek QA checked 18 embedded video instances across 10 English/Korean routes with 0 failures.
- Production build passed with `pnpm run build`.

Final artifacts:
- Caption masters: `audit/caption_master/`
- Rendered MP4 working copies: `audit/caption_render/rendered_master/`
- ASS render files: `audit/caption_render/ass/`
- QA manifest: `audit/seek_caption_qa/review_manifest.json`
- QA report: `audit/seek_caption_qa/REPORT.md`
- Browser seek results: `audit/seek_caption_qa/browser_seek_results.json`

Remaining editorial limitation: the master caption text is still based on machine translation plus automated cleanup. It now looks and times correctly, but the English wording should still be approved by a fluent Korean-English reviewer familiar with hospice and medical terminology before it is treated as final clinical translation.
