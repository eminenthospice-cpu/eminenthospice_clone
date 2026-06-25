# Production Tasks - Track B: Config, SEO & Deploy (Codex)

Working dir: `eminent-astro/` · Branch: `astro-rewrite`
Run alongside Track A (Claude) - see `TASKS_CLAUDE.md`.

## File ownership (avoid merge conflicts)

**This track edits ONLY:**
- `public/robots.txt` (new file)
- `astro.config.mjs`
- `src/data/site-config.ts`
- `src/layouts/BaseLayout.astro`

**DO NOT TOUCH** (owned by Track A): `public/images/**`, `src/data/images.ts`.

Current canonical URL everywhere: `https://eminenthospicewebsite.pages.dev`
(Cloudflare Pages, static Astro, no custom domain yet).

---

## Task 1 - Add robots.txt (HIGH, pure code)

There's no `public/robots.txt`. The sitemap IS generated at
`/sitemap-index.xml`. Create `public/robots.txt`:
```
User-agent: *
Allow: /

Sitemap: https://eminenthospicewebsite.pages.dev/sitemap-index.xml
```
(If Task 3's custom domain lands first, use that host instead.)
Verify it ends up at `dist/robots.txt` after build.

## Task 2 - Confirm service area (needs user input)

`src/data/site-config.ts` → `CONTACT.regions` is `'Los Angeles County, CA'`
with a `// TODO: confirm full service area`. Confirm the real coverage area
with the owner, update the string, and remove the TODO. If unknown, leave as-is
and flag it - don't invent regions for a healthcare provider.

## Task 2b - Flip logo path to PNG ✅ DONE (Track A)

`BRAND.logo` now points at `/images/logo.png` (40 KB, replaced the 1.5 MB SVG)
and the old `logo.svg` has been removed.

## Task 3 - Custom domain swap (BLOCKED on domain purchase)

When a real domain exists, update the canonical URL in **two** places (both in
this track's ownership):
- `astro.config.mjs` → `site: '...'`
- `src/data/site-config.ts` → `SITE.url`
Then rebuild + redeploy so canonical tags, OG tags, sitemap, and robots.txt all
update. Until the domain is bought, leave a note here and do nothing.

## Task 4 - Analytics scaffold (OPTIONAL, needs tracking ID)

No analytics currently. If the owner wants traffic data, add a privacy-friendly
snippet (Cloudflare Web Analytics is free + no cookie banner, or Plausible) to
the `<head>` of `src/layouts/BaseLayout.astro`. Needs an account/site token
first - if none, document the choice here and skip.

## Task 5 - Document/fix the deploy (INFRA, mostly dashboard)

Per project notes, the git-connected Cloudflare Pages CI build keeps deploying
empty (everything 404s); the working path is a direct upload:
```
npm run build
npx wrangler pages deploy dist --project-name=eminenthospicewebsite --branch=main --commit-dirty=true
```
The real fix is in the Cloudflare dashboard (build command/output dir for the
`eminenthospicewebsite` project - output dir must be `dist`, build cmd
`npm run build`). This needs dashboard access - investigate config, document
the correct settings here, and note whether CI builds succeed afterward.

---

## Verify before done
```
npm run build          # must succeed, 32 pages
```
- `dist/robots.txt` exists and references the right host
- `grep -rn "REPLACE\|TODO" src/data/site-config.ts` → only intentional ones remain
- If analytics added: confirm the snippet renders in built HTML `<head>`

Mark each task done by checking it off here as you go.
