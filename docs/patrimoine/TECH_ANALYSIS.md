# Technical analysis — wealth-management app prototype (Session 1, Part A)

Input: [MEMOIRE.md](MEMOIRE.md) (11 validated ideas, 2026-11-22) and
[BRIEF_01_TECH_ANALYSIS.md](BRIEF_01_TECH_ANALYSIS.md).
Tools: [TOOLS.md](TOOLS.md). Questioned decisions: [CHALLENGES.md](CHALLENGES.md).

This document assumes the recommendations of CHALLENGES.md (C1-C9). Where
a screen depends on one, the tag (Cn) says so; if Franco rejects it, the
architecture agent follows the memo instead.

**Tags:** **[measured]** = read on an official page (date 2026-11-22);
**[assumed]** = my estimate, to measure on a device; **[decision]** =
from the memo.

---

## 0. System at a glance

```
 Phone (Expo app, Android first)                Analyst (browser)
   │  reads precomputed tables, writes edits       │ bank dashboard SPA (Cloudflare Pages)
   ▼                                               ▼
 Supabase (EU region): Postgres + Auth + Realtime + Edge Functions + pg_cron
   ▲            ▲                         │
   │ results    │ market cache            │ push via Expo Push Service → FCM
   │            │                         ▼
 GitHub Actions (Python batch)        Phone notification
   - VaR/CVaR, vol, beta, drawdown, TWR/IRR, attribution
   - Isolation Forest training → model JSON
   - fake-data generator, keep-alive
 Edge Functions (TypeScript, live)
   - ingest bank/mobile-money "API" (simulated provider)
   - categorise (rules → Groq), score (thresholds + IF + fraud rules + context)
   - market fetch (Finnhub, Twelve Data, CoinGecko, Frankfurter, FRED)
```

The simulated provider is a set of Edge Function endpoints shaped like a
real aggregator (accounts, balances, transactions in ISO 20022 fields,
mobile-money operations, security events). Replacing it by the MTN MoMo
sandbox later means writing one new adapter behind the same internal
schema [decision, idea 1].

---

## 1. Launch and onboarding

### 1.1 Cold start and splash

| Item | Spec |
|---|---|
| Splash | Native splash (`expo-splash-screen`), held until the local cache is open and the session token is read; never held for network. |
| First paint | From the local cache (last snapshot), with "Mis à jour il y a X min". Network refresh starts after first paint. |
| Budget | Cold start to interactive home ≤ **3 s** on the reference device (§6) [assumed target]; warm start ≤ 1 s. |
| First ever launch | No cache → language choice → welcome screen; nothing loads from the network before sign-in except a 1-request health check. |

### 1.2 Sign-up and login (C7)

| Step | Spec |
|---|---|
| Sign-up | Email + password (≥ 10 characters, breached-password check off-device not available free → length + common-list check) ; email confirmation by code (Supabase Auth). |
| Demo accounts | 3 pre-seeded profiles (salaried in Dakar, trader in Abidjan, diaspora investor) with months of history, so the anomaly engine is already "learned" [decision, idea 8]. |
| Login | Email + password once per device; then **biometric unlock** (`expo-local-authentication`) or 6-digit app PIN. |
| MFA | Optional TOTP (Supabase MFA). Required for the analyst dashboard. |
| Device registration | On first login, a random device id is created and stored in secure storage; a `security_event` "new_device" is written (used by fraud rules). |
| Session | Access token 1 h, refresh token rotated; app locks after 5 min in background (setting: 1/5/15 min); 5 failed PINs → full re-login. |

### 1.3 Consent screens (once, revisitable in Settings)

1. Data processing for the service (required) — states that this is a
   **prototype with fictitious data**.
2. Automatic categorisation by an external AI service (optional; off →
   rules only). Says what is sent (pseudonymised labels) and where.
3. Notifications (OS permission asked **in context**: when the user
   first enables alerts, not at launch; Android 13+ needs runtime
   permission).
4. Crash reports (optional, Sentry).
Each consent is stored with date and version (`consents` table).

### 1.4 One-time questionnaire [decision, idea 5]

- 4 short sections: income and fixed charges; goals; risk tolerance
  (5 questions → profile 1-5); spending habits. ≤ 3 min.
- Saved after each answer (resume later), skippable ("Plus tard"),
  editable in Settings. Answers drive budgets, the concentration
  threshold (idea 6) and the context part of the score (idea 10).
- Amounts entered with a numeric keypad, in the reference currency, with
  thousands separators ("250 000 F CFA").

### 1.5 Linking accounts (simulated)

- "Ajouter un compte": choose **Banque (démo)**, **Orange Money**,
  **Wave**, **MTN MoMo**. A consent screen imitating an aggregator
  (scopes: balances, transactions, 90 days history) → the simulated
  provider returns accounts. Clearly labelled "simulation".
- First sync: balances first, then transactions paginated (newest
  first). Budget ≤ 2 MB for 12 months of history [assumed].

### 1.6 Empty states

| Screen | Empty state |
|---|---|
| Home | "Ajoutez un compte pour voir votre patrimoine" + primary button. |
| Portfolio | "Aucun placement" + "Ajouter un achat" / "Ajouter un bien immobilier". |
| Spending | "Pas encore d'opérations ce mois-ci". |
| Alerts | Learning-phase card: "Apprentissage de vos habitudes : 12/30 jours, 18/30 opérations" with a progress bar [decision, idea 8]. |
| Risk / Performance | "Il faut au moins 1 placement coté et 30 jours d'historique" (thresholds to fix in architecture). |

---

## 2. Screens and flows

Common rules for every screen:
- **Loading:** skeletons from cache; never a blank spinner if a cached
  snapshot exists.
- **Error:** inline banner "Impossible de mettre à jour — données du
  [date]" + "Réessayer"; never lose cached data.
- **Offline:** read-only from cache; edits (category change, manual
  trade, real-estate value) queued and sent on reconnect; queued items
  marked "en attente".
- **Freshness label** on every number that comes from a market:
  "Cours différés (~15 min)" or "Prix mensuel de référence" [decision,
  idea 2].
- **Currency:** every amount stored in its original currency + converted
  at display into the reference currency (XOF default; EUR, USD, XAF)
  [decision, idea 3]. XOF/XAF have no decimals.

### 2.1 Home

| Block | Data | Source | Refresh | Offline |
|---|---|---|---|---|
| Net worth + change (day/month) | `networth_snapshots` | batch (C1) + live balances | on open + pull-to-refresh; batch every 15 min | last snapshot |
| Mini chart 30 days | daily net worth series (≤ 30 points) | batch | daily | cached |
| Alerts strip | open alerts count + top one | `alerts` via Realtime when app open | live | cached |
| Budget left this month | `budget_status` | SQL view | on open | cached |
| Market strip (5 tickers) | `market_quotes` | cache table | 15 min server; app reads on open | cached + age |

### 2.2 Accounts and transactions (idea 1)

- **Accounts list:** bank + mobile-money wallets, balance, last sync.
- **Account detail:** transactions (infinite list, 50 per page, FlashList
  for low memory), search, filters (category, amount, date).
- **Transaction detail:** ISO 20022 fields shown in plain French
  (counterparty, reference, type: dépôt, retrait, transfert, paiement
  marchand, frais), category with source ("règle", "IA", "vous"),
  "Modifier la catégorie" → creates a rule (idea 5) with a preview
  "Appliquer aux 7 opérations similaires ?".
- Refresh: pull-to-refresh calls the simulated provider sync; new
  transactions trigger categorisation and scoring server-side.

### 2.3 Portfolio (idea 3)

| View | Data | Notes |
|---|---|---|
| Positions | quantity, average cost (PRU), last price, value, unrealised P&L, realised P&L | value in reference currency; price age shown |
| Allocation | by class, currency, country | donut (Victory Pie) + list (accessible) |
| Add trade | buy/sell, date, quantity, price, fees, currency | offline-queued; validates that a sell ≤ held quantity |
| Real estate | name, value, currency, last update date | user-entered; "mis à jour il y a 8 mois" warning > 6 months |
| Debts | loans: balance, rate, monthly payment | reduce net worth |
| Asset detail | candlestick (daily, 3M/1Y/5Y), key stats, positions | candles from cache table, ≤ 260 points per view |

### 2.4 Markets (idea 2)

- Watchlist (indices via ETF proxies, metals, oil, cocoa/coffee monthly,
  crypto, FX incl. XOF computed from the peg) (C4).
- Server refresh: quotes every 15 min during the market's hours; crypto
  every 10 min; FX hourly (reference rates daily); commodities monthly
  for cocoa/coffee.
- The phone never calls a market vendor; it reads `market_quotes`
  (one request for the whole watchlist).

### 2.5 Spending analysis and budgets (idea 5)

| View | Data | Chart |
|---|---|---|
| Month overview | spending by category vs last month | bars |
| Flows | income → categories → savings | Sankey (Skia + d3-sankey) |
| Indicators | savings rate, "reste à vivre", share of fixed charges, month-on-month change | stat tiles |
| Budgets | per category, alerts at 80 % and 100 % | progress bars |
| Categories | editable tree with sub-categories; rule list | — |

Categorisation pipeline (server): user rules → keyword rules →
Groq batch (C6) → "Non classé". Budget alerts computed on each new
transaction (Edge Function) → push.

### 2.6 Risk (idea 6)

- Annualised volatility, beta vs each asset's market index (S&P 500 via
  SPY, Bitcoin for crypto; BRVM absent), historical VaR and CVaR 95 % at
  1 day and 1 month (C5), drawdown chart, exposures (class, currency,
  country, sector), concentration alerts (threshold from risk profile,
  editable).
- Real estate and monthly-priced assets excluded, shown in a separate
  line "Hors calcul de risque".
- Data: `risk_metrics` table, batch nightly + after each trade
  (on-demand job, results in ≤ 10 min) [assumed]. Each figure has a
  "?" opening a ≤ 3-sentence plain explanation.
- Minimum data: 60 daily returns for a figure to be shown; otherwise
  "Données insuffisantes" [assumed threshold].

### 2.7 Performance (idea 7)

- TWR and IRR side by side, each with a one-line explanation.
- Contribution per asset and per class (weight × return) + currency
  effect (return in reference currency − return in local currency).
- Periods: month, year, since inception, custom. Results precomputed for
  fixed periods; custom period computed on demand by the batch job or an
  Edge Function (SQL) [to decide in architecture].

### 2.8 Alerts centre (ideas 8, 9, 10)

- List of alerts: type (anomalie, fraude, budget, concentration), score,
  reasons in plain French ("Montant 6× plus élevé que vos paiements
  habituels chez ce bénéficiaire", "Nouvel appareil + retrait dans
  l'heure").
- Score 40-70: "Est-ce bien vous ?" — **Oui, c'est moi** (profile adapts)
  / **Non** (escalates to the bank as > 70). Score > 70: "Votre banque a
  été prévenue" + status updated live (en analyse / légitime / fraude).
- The app **never blocks a payment** [decision, idea 10].

### 2.9 Settings

Reference currency, language, categories and rules, budgets, alert
thresholds (concentration), notifications per type, security (PIN,
biometrics, lock delay, devices list, sign out everywhere), consents,
questionnaire, export my data (CSV/JSON), delete my account, about
("prototype — données fictives"), demo reset (demo accounts only).

### 2.10 Bank dashboard (web, analyst) (C2)

- Alert queue (live via Realtime), filters, alert detail (transaction,
  reasons, user history, device/security events), decision
  **fraude / légitime** with comment → feedback table used to tune
  thresholds (bounded change per decision, logged).
- **Demo console** (recommended): buttons to inject a scenario for a demo
  account (SIM swap + withdrawal, mule pattern, unusual merchant,
  large transfer at 3 a.m.), so the presenter can show the full chain
  live. (Question for Franco.)

---

## 3. Widgets (phase 2, C9)

| Widget | Data | Refresh | Feasibility |
|---|---|---|---|
| Net worth | last snapshot + day change | Android ≥ 30 min (`updatePeriodMillis` floor [measured]) or on app open / push; iOS budget ~40-70 reloads/day [measured via Apple talk] | `expo-widgets`, Android opt-in [measured] |
| Budget left | month budget left | same | same |
| Alerts | count of open alerts | refreshed by a data push when an alert is created | same |
| Market tickers | not recommended | data would be ≥ 30-45 min old | — |

Widgets read a small JSON written by the app to shared storage; they
never call the network themselves (data budget, battery). Privacy: an
option to hide amounts on widgets ("•••").

---

## 4. Notifications

| Type | Trigger | Content | Target latency |
|---|---|---|---|
| Confirm it's you (40-70) | new scored event | "Paiement de 450 000 F CFA chez X. C'est vous ?" + actions Oui / Non | event → push sent ≤ 5 s p95 [assumed]; delivery depends on FCM |
| Bank alerted (> 70) | score > 70 | "Opération suspecte signalée à votre banque" | ≤ 5 s sent |
| Bank decision | analyst decides | "Votre banque a confirmé : légitime" | ≤ 5 s sent |
| Budget 80/100 % | transaction | category + amount left | ≤ 1 min |
| Concentration | batch | asset + share | next batch |
| Learning finished | 30 days AND 30 ops | "Les alertes d'anomalies sont actives" | daily batch |

- Delivery: Expo Push Service → FCM (Android). Push delivery is not
  guaranteed: when the app is open, alerts also arrive by Realtime; on
  open, the app always fetches open alerts.
- Notification text never shows the full account number; amount shown
  by default with an option to hide it.
- Unanswered 40-70 question: reminder after 15 min, then the alert stays
  open in the app (escalation rule: question for Franco).
- Android channels: "Sécurité" (high importance), "Budgets", "Marchés".

---

## 5. Accessibility (WCAG 2.2 AA, mobile)

| Area | Target |
|---|---|
| Contrast | text ≥ 4.5:1 (large text ≥ 3:1); chart lines, icons, focus indicators ≥ 3:1 against background (1.4.3, 1.4.11). Both light and dark themes. |
| Colour not alone | gains/losses with sign and arrow, not only green/red (1.4.1); chart series distinguishable by pattern/label. |
| Touch targets | WCAG 2.5.8 minimum 24×24 px; we use platform sizes: 48 dp Android, 44 pt iOS. |
| Text size | every screen usable at 200 % system font (`allowFontScaling` on, no fixed-height text boxes); numbers abbreviate ("1,2 M F CFA") rather than truncate. |
| Screen readers | TalkBack and VoiceOver: every control has role + label in French; amounts read as words ("deux cent cinquante mille francs CFA"); charts have a summary label ("Patrimoine en hausse de 3 % sur 30 jours") and a "Voir en tableau" alternative. |
| Gestures | every chart gesture (scrub, pinch) has a button alternative (period selector, previous/next point) (2.5.1, 2.5.7 dragging). |
| Motion | respect "reduce motion" (Reanimated `useReducedMotion`); no auto-playing animation > 5 s. |
| Focus/order | logical reading order; modal focus trapped; errors announced. |
| Authentication | no cognitive test; biometrics or PIN; paste allowed in password fields (3.3.8). |
| Language | **French first**, English second (all strings in i18n files from day one). Wolof, Bambara, Dioula, Lingala: not in the prototype; architecture must allow it (question for Franco). |
| Low literacy | icons + short words; numbers big and formatted the local way; "Écouter" button reading key screens aloud (`expo-speech`, French TTS on device, no network) [assumed available on most Android devices]; one action per screen in onboarding; no jargon without a "?" explanation. |

Testing: Android Accessibility Scanner + manual TalkBack pass per
screen; contrast checked with a script on the design tokens (design
session).

---

## 6. Performance on real devices

Reference device for all budgets [assumed]: **Android 12-14, 3 GB RAM,
4-core 2.0 GHz class (e.g. Samsung Galaxy A0x/A1x, Tecno Spark, Infinix
Hot)**, 3G/4G unstable. Nothing here is measured yet: each budget comes
with its measurement method; the first dev build must be measured.

| Budget | Target | How to measure |
|---|---|---|
| Download size | ≤ 30 MB per-ABI APK (AAB split) | EAS build output; `bundletool get-size` |
| Installed size | ≤ 90 MB | Android settings on reference device |
| Cold start → interactive home | ≤ 3 s (p50), ≤ 5 s (p90) | `adb shell am start -W`, Sentry app-start |
| Memory | ≤ 200 MB PSS steady, ≤ 300 MB peak on charts | `adb shell dumpsys meminfo` |
| Chart frame rate | 60 fps target, ≥ 45 fps floor while scrubbing; ≤ 500 points per series (server downsampling, LTTB) | Perf monitor / Sentry frames |
| List scroll | no dropped frames > 5 % on 1,000 transactions | FlashList + perf monitor |
| Data per day (normal use) | ≤ 1 MB/day; first sync ≤ 2 MB | Android data usage per app over 7 days |
| JS bundle | ≤ 6 MB (Hermes bytecode) | build output |
| Offline | every screen opens from cache; edits queued | airplane-mode test script |
| Slow network | usable at 3G profile (≈ 750 kbps, 300 ms RTT, 2 % loss): first data ≤ 5 s; timeouts 15 s with 2 retries (backoff) | network link conditioner / emulator throttling |
| Minimum OS | Android 7 (API 24), iOS 16.4 (Expo SDK 58 [measured]); target API 36 for Play [measured] | — |

Data-saving rules: one aggregated request per screen (SQL views / RPC),
gzip, ETag/`If-None-Match` on market and snapshot endpoints, no images
from the network except logos (cached, ≤ 5 KB each), Realtime only while
the app is in foreground, "Économiseur de données" setting (no auto
refresh on mobile data).

Server side: Supabase region **eu-west-3 (Paris)** or **eu-west-2
(London)** — no Africa region [measured]; which is faster from Dakar,
Abidjan and Douala must be **measured** (RTT test from a phone) before
creating the project.

---

## 7. Security and privacy

| Topic | Spec |
|---|---|
| Tokens | Supabase session in `expo-secure-store` (Android Keystore / iOS Keychain); never in AsyncStorage. |
| Local data | cache in SQLite, **encrypted** (SQLCipher; key in secure store) [assumed: `expo-sqlite` SQLCipher option, to verify]; wiped on sign-out. |
| Secrets | no vendor key in the app (anything `EXPO_PUBLIC_*` is public). Market, Groq, Expo push keys live in Supabase secrets / GitHub secrets only. |
| Access control | Row-Level Security on every table; users see only their rows; `analyst` role for the dashboard; service role only in Edge Functions and GitHub Actions. |
| Transport | HTTPS only; certificate pinning not in the prototype (documented as a later step). |
| Screens | hide content in the app switcher and block screenshots on sensitive screens (`expo-screen-capture`). |
| Session | auto-lock, device list with remote sign-out, re-auth (biometric) before changing security settings. |
| Rooted devices | warning only (no free reliable detection) [assumed]. |
| Audit | `security_events` table: login, failed PIN, new device, sign-out, settings change (also used by fraud rules). |
| Leaving the device | Supabase (EU) holds all user data; Groq receives **pseudonymised** labels only (C6); Sentry receives crash data with PII scrubbing on; nothing else. |

**Data-protection law (what applies if real users join).** The prototype
uses fictitious data, so no real personal data is processed except
testers' emails. For real clients, at least: Senegal — law 2008-12,
authority CDP; Côte d'Ivoire — law 2013-450, authority ARTCI; Cameroon —
law 2024/017 of 23 Dec 2024 [secondary sources]; other UEMOA/CEMAC
countries have their own laws; ECOWAS Supplementary Act A/SA.1/01/10 and
the AU Malabo Convention [assumed in force since 2023]. Common points to
plan for: declaration/authorisation before processing, consent, rights of
access/deletion, and **restrictions on transfers outside the country**
(our servers are in the EU; Groq and Sentry in the US). Payment-side
rules: BCEAO Instruction 001-01-2024 on payment services (defines strong
authentication) [official text found, provisions not read]. **A lawyer
must confirm before any real data.**

---

## 8. Computation placement (C1)

| Computation | Where | Why |
|---|---|---|
| Chart drawing, Sankey layout, number formatting, currency conversion of displayed values (peg + cached rates) | **Device** | instant, offline |
| Budget status, spending aggregates, net worth from balances | **Postgres (SQL views/RPC)** | one request, small payload |
| Categorisation (rules, Groq) | **Edge Function** on new transaction | keys stay server-side |
| Live score: thresholds, Isolation Forest inference, fraud rules, context, combined 0-100, alert + push | **Edge Function** (≤ 1 s) | no cold start in the demo path |
| Volatility, beta, VaR/CVaR, drawdown, TWR/IRR, attribution, IF training, profile recompute | **Python batch (GitHub Actions)** → tables | needs pandas/numpy/scikit-learn; minutes are acceptable |
| Market fetch and cache | **Edge Function on pg_cron** | small HTTP jobs, no Python needed |

Challenge to the memo: "VaR, beta, IF, scoring on server" is kept, but
"server" becomes two places (batch + live) instead of one sleeping API.

---

## 9. What is measured vs assumed (summary)

Measured (official pages, 2026-11-22): all vendor limits in TOOLS.md
marked [official]; Expo SDK 58 minimum OS; Android widget 30-min floor;
Play target API 36; Supabase regions and 1-week pause; Render cold start.

Assumed (to measure in the first build): every performance budget in §6,
reference device, push latency, Supabase region choice, SQLCipher in
`expo-sqlite`, French TTS availability, SIM-change unavailability, the
law details in §7.
