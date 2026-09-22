# A Place to Pause

A responsive React + TypeScript bench adoption app for Van Cortlandt Park. Leaflet provides the pannable geographic map. Supabase provides shared persistent records when configured.

## Run

```sh
npm install
npm run dev
```

The local app is connected to the **Bench Adoption Program** Supabase project (`rcjltddsnfcsdomluckl`) through the gitignored `.env.local`. The database currently contains 524 synthetic benches and 210 initial sample adoptions. New adoptions are shared between browsers. Browser-only adoptions from before this connection are not imported.

Keep `VITE_SAMPLE_INVENTORY=true` until verified inventory replaces the samples. For deployment, configure the same three `VITE_` variables in the hosting environment and rebuild; `.env.local` is not committed.

`npm run build` checks TypeScript and creates `dist/`. `npm run preview` serves that build.

## Included

- 524 clearly marked sample benches; green available and red adopted markers.
- Hover summaries with an adoption action, expanded details on selection.
- Search by bench number, donor, or area; status and park-area filters.
- Map/list switching retains selection and focuses the selected bench or row.
- Public names, dedication, duration, end dates, and remaining time.
- Adoption form with 6-, 12-, 24-, and 60-month terms. No payment.
- Browser-persistent demo mode, or shared Supabase persistence with 30-second refresh.
- Expired adoptions automatically become available.

## Connect Supabase

1. Create a Supabase project and execute `supabase/schema.sql` in its SQL editor.
2. Import the park’s verified bench inventory into `benches` (`id`, `area`, `lat`, `lng`). For development only, execute `supabase/demo-seed.sql` instead.
3. Copy `.env.example` to `.env.local`. Set `VITE_SUPABASE_URL` and `VITE_SUPABASE_PUBLISHABLE_KEY` to the project URL and publishable key. Never put a service-role key in the frontend.
4. Restart the dev server or rebuild the app.

The public view excludes contact emails. Row-level security and column grants allow public bench/adoption reads while denying email access and direct writes. The adoption RPC validates input and locks the bench row before checking availability and inserting an adoption, so simultaneous requests cannot double-book a bench. Existing records are retained for history. No Supabase credentials are committed.

Without environment variables, sample data and adoption changes are saved in localStorage on this browser only. Demo mode is not a shared source of truth or an official reservation. No email is stored in demo mode. Clear the `vcp-benches-v1` localStorage key to reset. Local demo mode does not offer database concurrency guarantees.

## Launch requirements

Configure Supabase and import verified inventory; confirm program durations, public naming consent, and park approval. The anonymous adoption endpoint should be protected with server-side rate limiting/CAPTCHA or an authenticated adoption workflow before public launch. A staff administration UI, notification emails, and payments are outside this implementation.

Map tiles use the standard OpenStreetMap tile service with visible attribution. No API key is required. Internet access is required; browser caching and referrer headers use their defaults. Follow the [tile usage policy](https://operations.osmfoundation.org/policies/tiles/): no bulk downloading or offline prefetching; service is best-effort. The woodland hero photograph is bundled locally from Unsplash. Fonts use Google Fonts with local fallbacks.

Implementation references: [Leaflet API](https://leafletjs.com/reference) and [Supabase RPC](https://supabase.com/docs/reference/javascript/rpc).

## Browser checks

Run `npx playwright install chromium` once, then `npm test`. The default tests run an isolated localStorage app on port 5174 and never change Supabase. They cover selection across views, adoption persistence, filtering, and mobile overflow. Optionally set `PLAYWRIGHT_CHROMIUM_EXECUTABLE` to use an existing Chromium installation.


### Live integration verification

`npx playwright test --config playwright.live.config.ts` runs against the configured Supabase app on port 5173. It requires a disposable bench with ID 900001. Create that test fixture first and remove its adoption and bench afterward. It checks adoption through the UI, persistence in a separate browser context, and rejection of a competing adoption. Do not run it against a real bench with this ID.

The Supabase security advisor flags the intentionally callable `SECURITY DEFINER` adoption RPC for [anonymous users](https://supabase.com/docs/guides/database/database-linter?lint=0028_anon_security_definer_function_executable) and [authenticated users](https://supabase.com/docs/guides/database/database-linter?lint=0029_authenticated_security_definer_function_executable). This is the narrow, validated write entry point for the no-account flow, with a fixed empty search path. Direct table writes and email reads are denied. Add abuse protection before a public production launch.

Sample bench positions follow illustrative winding corridors across the park instead of circular clusters. They are not surveyed locations. `python3 scripts/generate-sample-locations.py` regenerates the shared JSON coordinates, fresh database seed, and coordinate-only update SQL. The update preserves bench IDs and adoption records; local demo records also receive the revised positions without resetting their adoptions.
