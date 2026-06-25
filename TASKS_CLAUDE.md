# Production Tasks - Track A: Assets & Media (Claude)

Working dir: `eminent-astro/` · Branch: `astro-rewrite`
Run alongside Track B (Codex) - see `TASKS_CODEX.md`.

## File ownership (avoid merge conflicts)

**This track edits ONLY:**
- `public/images/**` (add/replace image files)
- `src/data/images.ts`

**DO NOT TOUCH** (owned by Track B): `public/robots.txt`, `astro.config.mjs`,
`src/data/site-config.ts`, `src/layouts/BaseLayout.astro`.

---

## Task 1 - Self-host the photography (HIGH PRIORITY)

All 11 image slots in `src/data/images.ts` currently hotlink
`images.unsplash.com`. Download each, commit it under `public/images/photos/`,
and rewrite the `src` to the local path. This removes the external dependency,
gives us caching/control, and is safer than hotlinking on a live hospice site.

Slots (key → target dimensions, save as `public/images/photos/<key>.jpg`):

| key | w × h |
|-----|-------|
| homeHero | 1500×2000 |
| homePhilosophyPortrait | 1200×1500 |
| homeLevelRoutine | 1000×750 |
| homeLevelContinuous | 1000×750 |
| homeLevelInpatient | 1000×750 |
| homeLevelRespite | 1000×750 |
| aboutHero | 1600×1000 |
| servicesHero | 1600×1000 |
| familiesHero | 1600×1000 |
| contactHero | 1600×1000 |
| griefHero | 1600×1000 |

Steps:
1. `mkdir -p public/images/photos`
2. For each slot, `curl -L` the existing Unsplash URL (already sized via query
   params) to `public/images/photos/<key>.jpg`. Verify each file is a real JPEG
   (`file <path>`) and non-trivial size (>20KB).
3. Rewrite each `src:` in `src/data/images.ts` from the `https://images.unsplash.com/...`
   URL to `/images/photos/<key>.jpg`. Keep `alt`, `width`, `height`, `blurDataURL` as-is.
4. Remove the now-stale top-of-file comment about "Swap src values with real
   photography URLs before launch" / Unsplash, and the 3 `// TODO: client photo`
   comments (the slots are now self-hosted; a real client-photo swap is a
   separate later task and noted in PLACEHOLDERS.md).

> NOTE: these are still stock images, just self-hosted. If the client provides
> real photos later, drop them in at the same paths/dimensions - no code change.

## Task 2 - Optimize the logo (MEDIUM)

`public/images/logo.svg` is **1.5 MB** and loads in the header on every page.
Investigate why it's so large (likely an embedded raster or un-minified paths).
- If it embeds a bitmap, that's the bug - extract/recompress or replace with a
  true vector.
- Otherwise minify (e.g. `npx svgo public/images/logo.svg`).
Target: well under 100 KB. Confirm it still renders identically in the header.

---

## Verify before done
```
npm run build          # must succeed, 32 pages
```
- `grep -rn "images.unsplash.com" src` → no matches
- Spot-check `dist/` references the local `/images/photos/...` paths
- Optional: `npx astro dev` and eyeball home + a hero page

Mark each task done by checking it off here as you go.
