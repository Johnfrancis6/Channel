# Tools — best free option per block (Session 1, Part B)

All limits below were read on **2026-11-22**. Each fact is tagged:

- **[official]**: read on the vendor's own pricing/limits/docs page.
- **[official, via search]**: quoted from the vendor's page by a search
  result; the page itself could not be loaded here (JavaScript page,
  403, truncated).
- **[secondary]**: third-party source only. Re-check before relying on it.
- **[assumed]**: my estimate, not measured.

Rule used for every pick: free without a card if possible, works for a
prototype shown to a client (commercial use), no cold start in the demo
path, and the fewest moving parts.

> **Key finding.** Three provisional choices of idea 11 do not hold as
> written: Render (cold start of about one minute in the live demo path),
> Vercel Hobby (personal, non-commercial use only) and Groq "open
> models" (the Llama models moved to Enterprise-only). Twelve Data's free
> plan has no commodity prices. The replacements are in the tables and
> in [CHALLENGES.md](CHALLENGES.md).

---

## Summary of picks

| Block | Provisional (memo) | **Pick** | Status |
|---|---|---|---|
| Mobile framework | React Native + Expo | **React Native + Expo SDK 58** (dev builds, not Expo Go) | confirmed |
| Charts | Victory Native (+ Sankey) | **Victory Native XL** + custom Skia candlestick + `d3-sankey` layout drawn in Skia | confirmed, extended |
| Database + auth | Supabase | **Supabase Free** (Postgres, Auth, Realtime, Edge Functions, pg_cron) | confirmed, keep-alive needed |
| Compute (VaR, beta, ML, score) | FastAPI + scikit-learn on Render | **Split:** batch analytics in Python on **GitHub Actions** (scheduled) → results in Supabase; live scoring in a **Supabase Edge Function** | changed (C1, validated) |
| Market data | Finnhub + Twelve Data | **Twelve Data** (daily history, FX, US stocks/ETFs) + **Finnhub** (intraday quotes, US) + **FRED** (oil daily, cocoa/coffee monthly) ; commodities via ETF proxies | changed (C4, validated) |
| Crypto | CoinGecko demo | **CoinGecko Demo** (attribution required) | confirmed |
| FX | Frankfurter + CFA peg | **Frankfurter** + fixed peg | confirmed |
| LLM categorisation | Groq (open models) | **Groq Free, `openai/gpt-oss-20b`**, batched, labels pseudonymised; fallback rules only | model changed (C6, validated) |
| Bank-card OCR (new, C10) | — | **`react-native-vision-camera` v4 + ML Kit text recognition** (on-device) + regex + Luhn | new |
| Fraud rules | coded rules | **Coded rules** (TypeScript, in the scoring Edge Function), each citing its source | confirmed |
| Simulated bank dashboard | Next.js on Vercel | **React (Vite) SPA on Cloudflare Pages**, reading Supabase Realtime | changed (C2, validated) |
| Push notifications | — | **Expo Push Service** + FCM v1 (Android) | new |
| Widgets | — | **`expo-widgets`** (Android opt-in), phase 2 | new |
| Fake-data generation | — | **Own Python generator** (Faker + African-French lists), deterministic seed, run in GitHub Actions | new |
| Monitoring | — | **Sentry Developer** (app + Edge Functions) + **UptimeRobot Free** + Supabase logs | new |
| App build/distribution | — | **Expo free plan**: 15 Android builds/month, APK sideload for the demo | new; Android only (C3, validated) |

---

## 1. Mobile framework

| Option | What it gives here | Free limits | Catch | Pick |
|---|---|---|---|---|
| **React Native + Expo SDK 58** | One codebase Android/iOS, OTA updates, config plugins for widgets/notifications | Free plan: 15 Android + 15 iOS cloud builds/month, low-priority queue, 45-min timeout; updates to 1,000 MAU; 25 projects [official, expo.dev/pricing] | Push and widgets do **not** work in Expo Go → development builds required [official, docs.expo.dev push FAQ / widgets]. SDK 58 = RN 0.88, Android 7+, iOS 16.4+ [official, docs.expo.dev/versions/latest] | **Yes** |
| Bare React Native | Full native control | Free, local builds | Builds on our own machine; Franco has no Mac → no iOS build | No |
| Flutter | Good performance on low-end Android | Free | Memo decision is React Native; would discard nothing yet but changes the language | No (no reason strong enough) |

Setup effort: low. Local Android builds are also possible (`eas build --local`) if the 15/month quota runs out [assumed: needs a Linux machine with Android SDK].

## 2. Charts

| Option | Chart types | Engine | Catch | Pick |
|---|---|---|---|---|
| **Victory Native XL** (`victory-native` v41) | Line, Area, Bar, Pie [official, nearform.com]; press/tooltip gestures | Skia + Reanimated + Gesture Handler (peer deps) [secondary, npm README] | No built-in Sankey; candlestick not listed on the official page (one secondary index claims one exists — unverified) | **Yes**, base library |
| react-native-gifted-charts | Bar, Line, Area, Pie, Donut, Stacked bar, Radar, Bubble, Scatter, **Candlestick** [official, GitHub README] | SVG | SVG is slower with many points and gestures on low-end Android [assumed]; no Sankey | Fallback if Skia is too heavy |
| ECharts for RN / WebView charts | Everything incl. Sankey | WebView | WebView memory and start cost on low-end phones; not "native fluidity" (memo) | No |

**Sankey:** compute the layout with `d3-sankey` (pure JS, MIT) on the device from server-side aggregates, draw nodes/links as Skia paths inside the same canvas. **Candlestick:** draw with Skia inside Victory's `CartesianChart` render function (same scale, same press state). Both are ~1-2 days of work each [assumed].

## 3. Database + auth + realtime

| Option | Free limits | Catch | Pick |
|---|---|---|---|
| **Supabase Free** | 500 MB DB per project, 50,000 MAU, 5 GB egress, 1 GB storage, 500,000 Edge Function invocations, Realtime 200 concurrent / 2 M messages, **2 active projects**, logs 1 day, no automatic backups [official, supabase.com/pricing] | **Paused after 1 week of inactivity** [official]. No Africa region; nearest are eu-west-3 Paris, eu-west-2 London, eu-central-1 Frankfurt [official, regions doc]. Phone (SMS) OTP needs a paid SMS provider [assumed from Supabase's provider model; to confirm] | **Yes** |
| Firebase (Spark) | Firestore, Auth incl. phone | NoSQL fits ISO 20022 history and SQL analytics poorly; phone auth SMS quota limited | No |
| Neon + own auth | Postgres free | No auth, no realtime → more to build | No |

Mitigations: the daily GitHub Actions job writes to the DB → never 7 days idle. Backups: the fake data is regenerable from the seeded generator; schema in migrations in git.

## 4. Compute (VaR, beta, Isolation Forest, score) — see CHALLENGES C1

| Option | Free limits | Catch | Pick |
|---|---|---|---|
| Render Free (FastAPI) | 512 MB RAM, 0.1 CPU [official via search, compute-plans]; 750 h/month/workspace; spins down after **15 min** idle, spin-up **about one minute**; "Do not use them for production" [official, render.com/docs/free] | One-minute cold start in the middle of a client demo; 0.1 CPU is slow for pandas | Not in the live path |
| Hugging Face Spaces | CPU Basic 2 vCPU / 16 GB free | **Docker and Gradio Spaces now require a paid plan to create** (PRO $9/month) [official, HF spaces overview] | No |
| Koyeb | — | No free web-service instance on the pricing page today [official] | No |
| Fly.io | $1 one-time credit without card (7 days); $5/month with a card [official, docs.fly.io] | Card required for anything durable | No |
| Google Cloud Run | 2 M requests/month free [official via search] | Billing account (card) very likely required [assumed] | No |
| **GitHub Actions (scheduled Python)** | Public repo: standard runners free; private: $12/month of compute included ≈ 2,000 Linux minutes [official, GitHub billing docs]; schedule min every 5 min, may be delayed [official via summary] | Not real-time; schedules can run late; in a **public** repo, scheduled workflows are disabled after 60 days without activity [official via summary] | **Yes, batch analytics** |
| **Supabase Edge Functions** (Deno/TS) | 500,000 invocations/month [official] | No scikit-learn: Isolation Forest must be exported (trees as JSON) and scored in TS; two languages to keep in sync (parity test) | **Yes, live scoring** |

Repository: **new public repository** (Franco, 2026-11-22) → standard runners are free with no minute cap [official]. Catch: in a public repo, *scheduled* workflows are disabled after 60 days without repository activity → trigger the jobs with `workflow_dispatch` from Supabase `pg_cron` (GitHub token in Supabase secrets) and keep `schedule` only as a backup. Never commit secrets or real data to the public repo.

Expected usage [assumed, now non-binding]: batch every 15 min during market hours + nightly full run ≈ 40 runs/day × 1-2 min ≈ 1,500-2,500 min/month → fits only in a **public** repo, or in a private repo if the intraday batch is light (only market snapshot, ~30 s) and the heavy run is nightly. Decision for the architecture agent, with this constraint.

## 5. Market data — see CHALLENGES C4

| Option | Free limits | Coverage on free | Catch | Role |
|---|---|---|---|---|
| **Twelve Data Basic** | 8 credits/min, 800/day [official] | Real-time US equities/ETFs, forex, crypto; 3 markets; commodities: reference data yes, **market data no**; indices not listed [official] | Credits are per symbol; commercial terms on a separate page not read | **Daily history (2+ years) + daily closes for US stocks/ETFs** |
| **Finnhub Free** | 60 calls/min [official via search] | US coverage [official via search] | Pricing page is JS-rendered; **stock candles likely premium** on free (403 reported) [secondary, conflicting] | **Intraday quotes (`/quote`) only** |
| **FRED (St. Louis Fed)** | Free key; ~120 req/min [secondary] | WTI/Brent daily; IMF monthly cocoa and coffee prices [assumed series ids: DCOILWTICO, DCOILBRENTEU, PCOCOUSDM, PCOFFOTMUSDM — to verify] | Cocoa/coffee only **monthly** | **Oil daily, cocoa/coffee monthly** |
| Alpha Vantage | 25 requests/day [official] | Majority of endpoints | Far too low | No |
| EODHD Free | 20 calls/day, 1-year history [official] | Global EOD incl. commodities, 15-min delayed | Too low for anything but a one-off backfill | Backup for a one-off backfill |
| Tiingo Starter | 50/hour, 1,000/day, 500 symbols/month [official] | 30+ years EOD | "Internal use only": **no display to another person** [official] → not allowed in a client demo | No |
| API Ninjas (commodities) | Free tier | Cocoa/coffee daily settlements | **No commercial use on free** [secondary] | No (unless Franco accepts the risk) |
| Stooq CSV | — | Daily CSV historically free without key | Could not be loaded from here [unverified] | No |

**Indices and commodities on a free budget:** use liquid US ETFs as proxies, labelled as such on screen: S&P 500 → SPY, Nasdaq → QQQ, Euro Stoxx → FEZ, emerging → EEM, gold → GLD, silver → SLV, oil → USO (or FRED daily WTI), broad agriculture → DBA. Cocoa and coffee: FRED monthly, shown as "monthly reference price", **excluded from VaR** like real estate. [assumed: tickers available on Twelve Data/Finnhub free US coverage]

**Call budget [assumed universe: 25 symbols]:** backfill 25 credits once (5,000 daily points per call); daily close 25/day; intraday Finnhub `/quote` every 15 min during US hours ≈ 26 × 25 = 650 calls/day spread at ≤ 25/min → inside 60/min. Twelve Data FX (EUR/USD, USD/XOF via EUR) once per hour ≈ 24/day. Total Twelve Data ≈ 50-100/day of 800. All calls server-side, cached in Supabase; phones never call vendors.

## 6. Crypto

| Option | Free limits | Catch | Pick |
|---|---|---|---|
| **CoinGecko Demo** | 10,000 calls/month; 30/min (some pages say 100/min) [official via search]; **attribution required** | Pricing page returned 403 here | **Yes** |
| CoinGecko keyless | ~5 calls/min shared by IP [official via search, docs] | Unreliable from shared server IPs | No |
| Twelve Data crypto | Included in Basic credits | Uses the same 800/day | Fallback |

Budget: 1 call `/simple/price` for 10 coins every 10 min = 4,320/month + 10 history calls/day = 300/month → ~4,600 of 10,000.

## 7. FX

| Option | Limits | Catch | Pick |
|---|---|---|---|
| **Frankfurter** | No key; no daily/monthly cap, abuse rate-limiting only; 219 currencies; reference rates, history back to 1948; commercial use allowed; attribution appreciated [official, frankfurter.dev] | Reference (daily) rates, not live | **Yes** |
| Twelve Data forex | In the 800/day | Uses credits | Intraday fallback |

XOF and XAF: always computed from EUR with **1 EUR = 655.957** (exact, fixed). Never fetched.

## 8. LLM categorisation — see CHALLENGES C6

| Option | Free limits | Catch | Pick |
|---|---|---|---|
| **Groq Free, `openai/gpt-oss-20b`** | 30 RPM, 1,000 RPD, 8K TPM, 200K TPD [official page, but the table is labelled "base limits for the Developer plan"; secondary sources give the same numbers for Free] | `llama-3.1-8b-instant` and `llama-3.3-70b-versatile` are now **Enterprise-only** [official, models page]. Country restrictions: not found in Groq's terms (calls are server-side from the EU anyway) | **Yes** |
| Gemini API free tier | Limits shown per project in AI Studio [official]; Senegal, Côte d'Ivoire, Cameroon are supported countries [official] | Free-tier prompts may be used to improve Google products [assumed, not verified on this run] | Second fallback |
| OpenRouter `:free` models | 20 RPM, 50 RPD under $10 credits [official] | Too low | No |

Batching 40 labels per request: a new user with 500 unknown labels → 13 requests. The 1,000 RPD is far above prototype needs.

## 9. Fraud rules

Coded rules in TypeScript inside the scoring Edge Function (same runtime as the score). Rule catalogue as a versioned table (`fraud_rules`: id, scheme, condition, weight, official source URL, date). Tazama stays excluded (memo, idea 11). No tool to buy.

## 10. Simulated bank dashboard — see CHALLENGES C2

| Option | Free limits | Catch | Pick |
|---|---|---|---|
| Vercel Hobby | 1 M function invocations, 100 GB transfer… [official] | Terms: Hobby only for "personal or non-commercial use"; fair-use guide: "non-commercial personal use only" [official via search] → a client prototype is commercial | No |
| **Cloudflare Pages** (static SPA) | 500 builds/month, 1 build at a time, 20,000 files [official]; Workers 100,000 requests/day if needed [official] | No commercial-use restriction found on the limits pages (terms not read) | **Yes** |
| Netlify Free | — | Not checked this run | Alternative |
| Expo web (same codebase) | Free | Mixes analyst UI into the mobile app codebase | No |

The dashboard is a static React SPA: it reads Supabase directly (RLS role `analyst`) and listens to Realtime for new alerts. Next.js is not needed.

## 11. Push notifications

| Option | Limits | Catch | Pick |
|---|---|---|---|
| **Expo Push Service** | Free, 600 notifications/s per project [official] | Dev build needed; Android needs FCM v1 credentials (Firebase project, free); iOS needs APNs key → **paid Apple Developer Program** (see C3) | **Yes** |
| OneSignal free | — | Extra SDK and account; no gain | No |
| FCM direct | Free | Two code paths (FCM + APNs) | No |

Notification actions ("Oui, c'est moi" / "Non") use notification categories in `expo-notifications`.

## 12. Widgets

| Option | Status | OS limits | Pick |
|---|---|---|---|
| **`expo-widgets`** (SDK 58) | Android + iOS; Android is opt-in (`enableAndroid`); not in Expo Go; interactive/configurable widgets need iOS 17+ [official] | Android: `updatePeriodMillis` ≥ 30 min [official, developer.android.com]; iOS: WidgetKit budget, typically **40-70 reloads/day** for a frequently viewed widget [official via search: WWDC21 / Apple forum quote] | **Yes, phase 2** |
| react-native-android-widget | Android only, Expo config plugin, MIT, RN 0.76+ → v0.15+ [official] | Same 30-min floor | Fallback if `expo-widgets` Android is unstable |

## 13. Fake-data generation

| Option | Catch | Pick |
|---|---|---|
| **Own Python generator** (Faker + curated lists of West/Central African names, merchants, operators, fee schedules) | We write the UEMOA IBAN, ISO 20022 (camt.053 as JSON) and mobile-money formats ourselves; Faker locale `fr_FR` page could not be loaded [unverified, but widely used] | **Yes** |
| Mockaroo | Row caps on free [unverified]; no domain logic (learning phase, injected anomalies) | No |
| SDV / synthetic from real data | Needs real data | No |

Deterministic seed → the same demo every time; a "scenario" file injects anomalies and fraud patterns on demand.

## 14. Monitoring

| Option | Free limits | Pick |
|---|---|---|
| **Sentry Developer** | 1 user, 5k errors, 5M spans, 50 replays, 30-day lookback [official]; RN/Deno support not on the pricing page [unverified] | **Yes** (crashes, JS errors, slow screens) |
| Expo Observe | 100K events/month on Free [official] | Optional (startup metrics) |
| **UptimeRobot Free** | 50 monitors, 5-min interval [official] | **Yes** (Supabase REST, Edge Functions, dashboard) |
| Supabase logs | 1-day retention [official] | Built-in |

## 15. Bank-card OCR at sign-up (C10)

| Option | What it is | Catch | Pick |
|---|---|---|---|
| **Vision Camera v4 + ML Kit text recognition** (`react-native-vision-camera-mlkit` or `react-native-vision-camera-text-recognition` frame processor) | Free, on-device, offline OCR; needs Vision Camera ≥ 4 and `react-native-worklets-core` [secondary: package READMEs] | Dev build only; we write the card parser (regex + Luhn) ourselves; package versions to confirm for RN 0.88 | **Yes** |
| `rn-executorch-card-scanner` | On-device EasyOCR via ExecuTorch, extracts number, expiry, name, bank [secondary: npm] | Young package, larger model [assumed] | Fallback |
| Scanbot SDK | Turnkey card scanner | **Commercial** (trial licence) | No |
| Cloud OCR (Google Vision, etc.) | Accurate | Sends the card image to a third party → PCI and privacy risk | No |

Rules (PCI DSS, PCI SSC FAQ via search): never store the CVV; display at
most first 6 + last 4; store only the truncated number. Check the
current PCI DSS v4.0.1 text before any real card.

## 16. Real mobile money later

MTN MoMo developer portal is a "Test environment" with Collections, Disbursements… [official]; free status and sandbox currency not confirmed on the pages read (the common knowledge that the sandbox uses EUR is **unverified**). Orange Money and Wave: no official sandbox found (memo).

---

## Sources (all read 2026-11-22)

Official pages read: supabase.com/pricing · supabase.com/docs/guides/platform/billing-on-free-plan · supabase.com/docs/guides/platform/regions · render.com/docs/free · render.com/pricing · huggingface.co/docs/hub/spaces-overview · huggingface.co/pricing · koyeb.com/pricing · docs.fly.io/about/pricing · docs.fly.io/about/free-plan · vercel.com/pricing · vercel.com/docs/limits/fair-use-guidelines · vercel.com/docs/plans/hobby · developers.cloudflare.com/workers/platform/limits · developers.cloudflare.com/pages/platform/limits · twelvedata.com/pricing · alphavantage.co/premium · frankfurter.dev · tiingo.com/about/pricing · eodhd.com/pricing · expo.dev/pricing · docs.expo.dev/versions/latest · docs.expo.dev/push-notifications/overview · docs.expo.dev/push-notifications/faq · docs.expo.dev/versions/latest/sdk/widgets · github.com/sAleksovski/react-native-android-widget · developer.android.com/develop/ui/views/appwidgets/advanced · developer.apple.com/support/compare-memberships · nearform.com/open-source/victory-native · github.com/Abhinandan-Kushwaha/react-native-gifted-charts · support.google.com/googleplay/android-developer/answer/11926878 · console.groq.com/docs/rate-limits · console.groq.com/docs/models · groq.com/terms-of-use · aistudio.google.com/docs/rate-limits · aistudio.google.com/docs/available-regions · openrouter.ai/docs/api-reference/limits · sentry.io/pricing · uptimerobot.com/pricing · GitHub Actions billing docs · momodeveloper.mtn.com

Via search (page not loadable here): finnhub.io/pricing · coingecko.com/en/api/pricing and docs.coingecko.com · vercel.com/terms · cloud.google.com/run/pricing · render.com/docs/compute-plans · developer.apple.com WidgetKit "Keeping a widget up to date" + WWDC21 session 10048 · fred.stlouisfed.org/docs/api.

Not loadable, unverified: Finnhub candle access on free, Stooq, FMP, Faker locale docs, MTN sandbox terms.
