# Challenges — decisions questioned by Session 1

Format: decision → problem → alternative → trade-off → recommendation →
**Franco's answer**. Nothing here is applied until Franco answers.
Sources and dates are in [TOOLS.md](TOOLS.md) (all checked 2026-11-22).

| # | Decision challenged | Recommendation | Franco's answer |
|---|---|---|---|
| C1 | Compute on FastAPI/Render | Batch Python on GitHub Actions + live scoring in Supabase Edge Function | _pending_ |
| C2 | Bank dashboard Next.js on Vercel | React SPA on Cloudflare Pages | _pending_ |
| C3 | Android + iOS for the prototype | Android-only demo; iOS later | _pending_ |
| C4 | Finnhub + Twelve Data cover markets | Add FRED; ETF proxies; cocoa/coffee monthly | _pending_ |
| C5 | Historical VaR at 1 month | Show 1-month VaR scaled from 1-day, overlapping as a check | _pending_ |
| C6 | Groq "open models" | `gpt-oss-20b`, labels pseudonymised | _pending_ |
| C7 | Login method (not decided) | Email + password + biometrics; no SMS | _pending_ |
| C8 | App detects SIM change | Simulated only; real source = operator API later | _pending_ |
| C9 | Widgets in the first version | Phase 2, Android first | _pending_ |

---

## C1 — Compute on Python FastAPI hosted free on Render (idea 11)

- **Decision:** VaR, beta, Isolation Forest and the 0-100 score run in a
  FastAPI service on Render Free.
- **Problem:** Render Free sleeps after 15 min idle and takes **about one
  minute** to wake (official). The alert flow (idea 10) is the heart of
  the client demo: "inject an anomaly → alert in seconds". A one-minute
  wait at that moment fails the demo. Also 512 MB / 0.1 CPU, and Render
  says free instances are not for production. The other free hosts
  failed: Hugging Face Docker Spaces now need PRO, Koyeb has no free
  instance, Fly.io and Cloud Run need a card.
- **Alternative:** split by timing need.
  - **Batch (minutes are fine):** volatility, beta, VaR/CVaR, drawdown,
    TWR/IRR, attribution, Isolation Forest training, user profiles →
    Python (pandas, numpy, scikit-learn) run by **GitHub Actions** on a
    schedule, writing results into Supabase tables.
  - **Live (seconds):** each new transaction or security event → a
    **Supabase Edge Function** (TypeScript) computes threshold scores,
    Isolation Forest score (model exported as JSON trees by the batch
    job), fraud rules, the combined score, then writes the alert and
    sends the push.
- **Trade-off:** + no cold start, no extra host, the app only reads
  precomputed tables (fast on 3G). − Isolation Forest inference exists
  in two languages (needs a parity test on fixed cases); schedules can
  start a few minutes late; a private repo has ~2,000 free Linux
  minutes/month (a public repo has no limit).
- **Recommendation:** adopt the split. Keep Render only as an optional
  "playground" API, not in the demo path.

## C2 — Bank dashboard in Next.js on Vercel (idea 11)

- **Problem:** Vercel's terms limit Hobby to personal or non-commercial
  use; its fair-use guide says "non-commercial personal use only". A
  prototype built for a client is commercial use.
- **Alternative:** a static React (Vite) app on **Cloudflare Pages**
  (free, 500 builds/month), reading Supabase directly with an `analyst`
  role and Supabase Realtime for live alerts.
- **Trade-off:** + free and allowed, no server code; − no Next.js server
  features (not needed here). Netlify is a second option (not checked).
- **Recommendation:** Cloudflare Pages.

## C3 — iOS in the prototype (implicit: "Android and iOS")

- **Problem:** push notifications on iOS, TestFlight and any iOS
  distribution need the **paid Apple Developer Program** (~99 USD/year
  [assumed price]). The free Apple account only installs on 3 devices
  from Xcode on a Mac, for 7 days (official). This breaks "free tools
  only" and needs a Mac. The target market is mostly Android [assumed].
- **Alternative:** the demo runs on **Android** (APK installed directly,
  15 free cloud builds/month). The code stays cross-platform; iOS is
  built when the client pays for the Apple account.
- **Trade-off:** + free, matches the market; − an iPhone-owning client
  cannot try it on their own phone.
- **Recommendation:** Android-only demo. **Question for Franco** (does
  the client need iOS?).

## C4 — Market data from Finnhub + Twelve Data (ideas 2, 6, 11)

- **Problem:** Twelve Data Basic has **no commodity market data** and no
  index data listed (official). Finnhub free is US-focused and its
  historical candles are likely premium (conflicting sources). So gold,
  oil, cocoa, coffee and world indices (memo idea 2) have no free
  official source in the provisional pair. VaR and beta need 1-2 years
  of daily history.
- **Alternative:** Twelve Data for daily history and FX; Finnhub for
  intraday quotes only; **FRED** for oil (daily) and cocoa/coffee
  (monthly IMF series); **US ETFs as proxies** for indices and metals
  (SPY, QQQ, FEZ, EEM, GLD, SLV, USO, DBA), labelled "proxy" on screen.
  Cocoa and coffee are shown as monthly reference prices and kept out of
  VaR (like real estate).
- **Trade-off:** + free and legal; − indices are ETF prices, not index
  points; cocoa/coffee are monthly. A paid plan later removes both.
- **Recommendation:** adopt. **Question for Franco:** are cocoa and
  coffee positions in the demo portfolios, or just market tickers?

## C5 — Historical VaR at 95 % over 1 month (idea 6)

- **Problem:** a historical 1-month VaR needs many independent 1-month
  returns. Two years of data give ~24 independent months; with
  overlapping 21-day windows the 5 % tail is estimated from very few
  independent events and moves a lot from day to day.
- **Alternative:** display 1-month VaR = 1-day historical VaR × √21
  (square-root-of-time, standard and stable), and compute the
  overlapping-window historical figure as a server-side check shown in a
  "details" panel.
- **Trade-off:** + stable, explainable number; − √21 assumes returns are
  independent (underestimates risk in trending markets).
- **Recommendation:** √21 scaling as the main figure, with the method
  written under it.

## C6 — Groq with "open models" (idea 5, 11)

- **Problem:** Groq's Llama models (`llama-3.1-8b-instant`,
  `llama-3.3-70b-versatile`) are now **Enterprise-only** (official
  models page). Also, transaction labels contain names and phone numbers
  ("Transfert à Awa Diop 77 123 45 67").
- **Alternative:** `openai/gpt-oss-20b` (open-weight, free: 30 RPM,
  1,000 RPD), 40 labels per request, JSON output constrained to the
  category list. Before sending: replace names, phone numbers and IBANs
  with placeholders. Fallback: rules only, then Gemini free tier.
- **Trade-off:** none against the memo; the model name changes.
- **Recommendation:** adopt.

## C7 — Login method (not decided in the memo)

- **Problem:** in the target market, phone-number login with SMS code is
  the norm, but SMS OTP needs a paid SMS provider. Free alternatives:
  email + password, magic link, TOTP MFA (free in Supabase).
- **Alternative:** prototype = **email + password**, then **biometric
  unlock** (fingerprint/face) and a 6-digit app PIN; optional TOTP MFA;
  pre-created **demo accounts** for the client. Phone number stored as a
  profile field (used by the fake data and fraud rules), not as a login.
- **Trade-off:** + free; − not the final UX for real users (phone + SMS
  later, paid).
- **Recommendation:** adopt for the prototype. **Question for Franco.**

## C8 — SIM-change detection (idea 9)

- **Problem:** a modern Android/iOS app cannot reliably read SIM changes
  (permissions removed or restricted) [assumed from OS policy, to
  verify]. Real SIM-swap signals come from the mobile operator.
- **Alternative:** SIM-change events exist **only in the fake database**
  (memo already says so); the app records only what it can see itself:
  new device id, new install, login time and place (coarse). Later: an
  operator SIM-swap API (e.g. GSMA Open Gateway) [assumed availability].
- **Recommendation:** state this clearly in the demo script so the
  client is not misled.

## C9 — Home-screen widgets in the first version (brief Part A.3)

- **Problem:** widgets need native targets, are not in Expo Go, refresh
  at most every 30 min on Android and 40-70 times/day on iOS, and add
  testing on many launchers.
- **Alternative:** ship the app first; add widgets (net worth, budget
  left, alerts count) in phase 2, Android first. Market tickers in a
  widget would be ≥ 30 min stale on top of the 15-min delay.
- **Recommendation:** phase 2, without a market-ticker widget.
