# Brief — Session 2: System architecture

You are the **architecture agent** of a project to build a mobile
wealth-management app prototype. You start cold.

## Repository

- You work in the new public repository **`Johnfrancis6/GOLDENPIECE`**
  (created by Franco). All project documents live in its `docs/` folder.
- **First step, if `docs/` does not yet hold the Session 1 files:** copy
  them from `Johnfrancis6/Channel`, branch `claude/funny-volta-y8xamm`,
  folder `docs/patrimoine/` (attach that repo read-only with `add_repo`):
  `MEMOIRE.md`, `BRIEF_01_TECH_ANALYSIS.md`, `TECH_ANALYSIS.md`,
  `TOOLS.md`, `CHALLENGES.md`, `SETUP.md`, `BRIEF_02_ARCHITECTURE.md`
  → `GOLDENPIECE/docs/` unchanged, one commit "Import Session 1
  documents". Links between them are relative and keep working.
- Work on a branch, never directly on `main`; `git fetch` before every
  push; `main` changes only through a pull request Franco merges.
- Public repository: **no secrets, no real personal data**, ever. Add a
  `.gitignore` covering `.env*` in your first commit.

## Read, in this order

1. [MEMOIRE.md](MEMOIRE.md) (in French): the 11 ideas Franco (project
   owner) validated on 2026-11-22.
2. [TECH_ANALYSIS.md](TECH_ANALYSIS.md): screens, flows, budgets,
   security, computation placement.
3. [TOOLS.md](TOOLS.md): the chosen tool per block, free limits with
   sources and dates.
4. [CHALLENGES.md](CHALLENGES.md): decisions questioned by Session 1
   (C1-C9 **validated** by Franco on 2026-11-22), C10 (bank-card OCR) and
   **Franco's answers to the Session 1 questions** (end of the file).
5. [SETUP.md](SETUP.md): what Franco measures and creates by hand
   (region RTT test, reference phone specs, free accounts).

## Pipeline

1. Technical analysis + tools (done, Session 1).
2. **You:** system architecture.
3. Design agent: design system, interactions, motion, mock-ups, guided
   tutorials. Your output must let them know every screen, state and
   data field without guessing.

No app code in this session. SQL schema sketches, API contracts and
diagrams are expected.

## The project in short

React Native (Expo SDK 58) app for personal wealth in French-speaking
Africa (XOF/XAF, fixed peg 1 EUR = 655.957): bank + mobile-money accounts
(fake database imitating UEMOA IBAN, ISO 20022, mobile-money operations,
security events), multi-asset portfolio and net worth, delayed market
data, spending analysis, investment risk (vol, beta, historical VaR/CVaR
95 % 1 day and 1 month), performance attribution (contribution + currency
effect, TWR and IRR), anomaly detection (active after 30 days AND 30
operations), coded fraud rules with official sources, combined 0-100
score (< 40 nothing, 40-70 ask the user, > 70 alert the simulated bank),
and a web analyst dashboard. The app never blocks a payment. Free tools
only. Prototype for a client.

## Validated decisions (subject to CHALLENGES.md answers)

- Mobile: React Native + Expo SDK 58, development builds (not Expo Go),
  Android first (C3), Hermes, i18n French first.
- Charts: Victory Native XL; custom Skia candlestick; Sankey with
  `d3-sankey` layout drawn in Skia. Charts drawn on the device only.
- Backend: Supabase Free (Postgres, Auth, RLS, Realtime, Edge Functions,
  pg_cron), EU region to be chosen by an RTT measurement.
- Compute (C1): Python batch on GitHub Actions (vol, beta, VaR/CVaR,
  drawdown, TWR/IRR, attribution, Isolation Forest training) writing to
  Supabase; live scoring in an Edge Function (thresholds + IF inference
  from exported JSON trees + fraud rules + context).
- Market data (C4): Twelve Data (daily history, FX, US ETFs/stocks),
  Finnhub (intraday quotes), FRED (oil daily; cocoa/coffee monthly),
  CoinGecko Demo (crypto, attribution), Frankfurter (FX reference),
  ETF proxies for indices/metals. Server cache only; phones never call
  vendors.
- Categorisation (C6): rules → keywords → Groq `openai/gpt-oss-20b`
  batched, pseudonymised labels → "Non classé".
- Fraud: coded rules, each with its official source, versioned table.
- Bank dashboard (C2): React SPA on Cloudflare Pages, Supabase Realtime.
- Push: Expo Push Service + FCM v1. Widgets: phase 2 (C9).
- Auth (C7): email + password, biometric/PIN unlock, optional TOTP,
  demo accounts.
- Monitoring: Sentry Developer, UptimeRobot, Supabase logs.
- Bank-card OCR at sign-up (C10): on-device Vision Camera + ML Kit,
  parser + Luhn, user confirms; store first 6 + last 4, brand, expiry,
  name only; never the CVV or the image.

## Franco's product answers (2026-11-22) — binding

- The client is an **ordinary person** who **installs the app himself**;
  first launch = language → **country of residence (required)** →
  **guided demo tour** → sign-up (or continue in demo).
- Reference currency **XOF by default for every country**, changeable
  manually (EUR, USD, XAF).
- **French and English only.** No read-aloud. No demo console in the
  bank dashboard: alerts in demo accounts come from scheduled
  fake-data scenarios.
- 40-70 prompt unanswered: one reminder, then the alert stays open in
  the app; **never auto-sent to the bank**.
- Amounts **hidden** in notifications by default.
- **Adaptive device security:** each device uses its own level (strong
  biometric, weak biometric, phone PIN/pattern/password, or app PIN when
  the phone has none) — matrix in TECH_ANALYSIS §1.2b; the level is a
  score context factor.
- Reference device: **Tecno Spark 50**, Android only.
- Code in the **new public repository `GOLDENPIECE`**: GitHub
  Actions minutes are free, but scheduled workflows stop after 60 days
  without activity → trigger jobs by `workflow_dispatch` from `pg_cron`.
  No secrets or real data in the repo.
- No accounts exist yet; SETUP.md lists them. Design the order in which
  build sessions need them.
- **You set the deadline and the build plan** (sessions, scope of each,
  order), since Franco gave no demo date.
- Fake data: own Python generator, deterministic seed, scenario files to
  inject anomalies/fraud.

## Budgets to respect (from TECH_ANALYSIS §6)

APK ≤ 30 MB per ABI; cold start ≤ 3 s p50 on a 3 GB-RAM Android 12-14
device; memory ≤ 200 MB steady; charts ≥ 45 fps, ≤ 500 points per series;
data ≤ 1 MB/day, first sync ≤ 2 MB; usable on 3G and offline (read-only
cache + queued edits); Android 7+ / iOS 16.4+. Live score event → push
sent ≤ 5 s p95. Free-tier quotas in TOOLS.md must hold with a margin of
≥ 50 % at demo load (state your load assumption).

## Your scope

1. **Components and boundaries:** app, Supabase (schemas, RLS roles),
   Edge Functions, batch jobs, simulated provider, bank dashboard,
   external vendors. One diagram + a responsibility table.
2. **Data model:** tables for users, consents, accounts, wallets,
   transactions (ISO 20022 fields), mobile-money operations, security
   events, positions/trades, real estate, debts, market cache, FX,
   categories/rules, budgets, profiles (anomaly), model artefacts, scores,
   alerts, analyst decisions, fraud-rule catalogue, snapshots and metric
   tables. Keys, indexes, retention, size estimate vs 500 MB.
3. **Provider adapter:** the internal contract the simulated provider
   implements so the MTN MoMo sandbox can replace it without app changes.
4. **API contracts:** each screen of TECH_ANALYSIS §2 → one RPC/view;
   payload size per call.
5. **Event flows** (sequence diagrams): new transaction → categorise →
   score → alert/push → user answer → bank decision → threshold tuning;
   market refresh; nightly batch; first sync; offline queue replay.
6. **Card OCR:** packages, permission flow, parser, storage fields, tests on real cards vs test numbers.
7. **Scoring design:** feature list, threshold method, IF export format
   and parity test, combination formula to 0-100, how analyst feedback
   changes thresholds (bounded, logged), learning phase.
8. **Offline and sync:** local DB schema, conflict rules, cache expiry.
9. **Security:** RLS policies per table, secrets map, key rotation,
   pseudonymisation before Groq, audit log.
10. **Environments and repos:** dev/demo, migrations, seed, CI (tests,
   builds), keep-alive, GitHub Actions minutes budget (public vs private
   repo).
11. **Observability:** what is logged and alerted, with free limits.
12. **Aspects G1-G15** of TECH_ANALYSIS §9 (distribution and updates, emails, money arithmetic, time zones, corporate actions, FX history, detection evaluation, tests, device integrity, sensitive input, rate limiting, account lifecycle, legal texts, analytics, battery): a decision for each.
13. **Risks:** each free-tier catch in TOOLS.md with its mitigation.

## Open questions you must carry

- Answered by Franco: the scanned card serves **only to identify the
  user's bank** (first 6 digits → bank); **all countries** are offered
  at first launch. Yours to design: what each country changes (phone
  format, operators, privacy-law notice, fake-data profile) and the
  generic fallback for countries without a dedicated profile.
- Supabase region: from the RTT results in SETUP.md.
- Reference phone specs: from SETUP.md.
- Technical (yours): custom-period performance computation; minimum data
  thresholds for risk figures; frequency of replayed fraud scenarios in
  demo accounts; analyst-feedback bounds on thresholds.

## Authority to challenge

You may challenge any decision, including Franco's and Session 1's, if
you judge it underperforming. Format: decision → problem → alternative →
trade-off → recommendation. Do not apply it yourself: Franco decides.
Record challenges and answers in `docs/CHALLENGES.md` (new section
"Session 2").

## How to work with Franco

- He writes in French: answer in French; deliverables in English.
- Ask questions a few at a time; for an ambiguous point state your
  understanding in ≤ 5 lines and wait for validation.
- Explain any key technical concept in ≤ 10 sentences with impact and
  alternatives. Say what is verified vs assumed. Never ask for secrets in
  the chat.

## Deliverables

In `docs/` of `GOLDENPIECE`, on your work branch, committed and pushed, then a pull request to `main` for Franco:

1. `ARCHITECTURE.md` — items 1-13 above.
2. `DATA_MODEL.md` — tables, fields, RLS, size estimate.
3. `API.md` — RPC/view contracts per screen and event flows.
4. `BUILD_PLAN.md` — the build sessions, their order, scope and the
   deadline you propose.
5. `BRIEF_03_DESIGN.md` — brief for the design agent (Franco asked that
   you write it): every screen,
   state (loading, empty, error, offline, learning phase), data field,
   accessibility and performance constraint, the same right to
   challenge.

Done when Franco has validated the five files.
