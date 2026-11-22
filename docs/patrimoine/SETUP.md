# Setup — what Franco does by hand (Session 1, 2026-11-22)

Three tasks only Franco can do: measure the network from his phone,
read his reference phone's specs, and create the free accounts. **Never
paste a key, password or token in a chat.** Keys go only into Supabase
secrets or GitHub repository secrets, when a build session asks for them.

## 1. Server-region test (RTT) — before creating Supabase

Supabase runs on AWS; it has no Africa region. Candidates: eu-west-3
(Paris), eu-west-2 (London), eu-central-1 (Frankfurt), eu-west-1
(Ireland). Measuring the round-trip time from the phone to each AWS
region tells which is closest **for real** (submarine-cable routes, not
geography, decide).

1. On the **Tecno Spark 50**, Wi-Fi **off**, mobile data **on**.
2. Open **https://www.cloudping.info** in Chrome, tap **HTTP Ping**,
   wait for the table. (Third-party tool, not AWS; it pings AWS regions
   from the browser.)
3. Write the ms values for Paris, London, Frankfurt, Ireland.
4. Repeat 3 times at different hours (morning, evening, night). Space
   the runs (rate limits).
5. If possible, the same once on Wi-Fi, and from another operator's SIM.

Result table (Franco fills in):

| Run | Date/time | Network (operator, 3G/4G/Wi-Fi) | City | Paris | London | Frankfurt | Ireland |
|---|---|---|---|---|---|---|---|
| 1 | | | | | | | |
| 2 | | | | | | | |
| 3 | | | | | | | |

Rule: pick the region with the lowest **median**; if two are within
10 ms, prefer Paris (eu-west-3) [assumed tie-break: French-speaking
legal proximity, no technical difference].

## 2. Reference phone: Tecno Spark 50

Read in Settings → About phone, and fill in:

| Field | Value |
|---|---|
| Android version | |
| RAM (and "extended RAM" if any) | |
| Storage (total / free) | |
| Processor | |
| Screen resolution | |
| Operator / usual network | |

These numbers turn the "assumed" budgets of TECH_ANALYSIS §6 into
targets checked on a real device.

## 3. Free accounts to create (none exist yet)

Create them **when the build session needs them**, in this order. All
free plans; card needed nowhere in this list [assumed from the pricing
pages read on 2026-11-22; if a site asks for a card, stop and tell the
session].

| # | Service | What for | Sign-in tip | When |
|---|---|---|---|---|
| 1 | GitHub — **new public repository** | code, CI, batch jobs | your existing GitHub account; name to agree with the architecture session | architecture |
| 2 | Supabase | database, auth, realtime, functions | "Sign in with GitHub"; region from §1 | first build session |
| 3 | Expo (expo.dev) | Android builds, push service | email | first build session |
| 4 | Firebase (Google) | FCM credentials for Android push | Google account; Spark (free) plan | when push is built |
| 5 | Cloudflare | bank dashboard hosting (Pages) | email | when the dashboard is built |
| 6 | Groq | categorisation AI | email / Google | when categorisation is built |
| 7 | Twelve Data, Finnhub, CoinGecko (Demo), FRED | market data keys | email | when market data is built |
| 8 | Sentry, UptimeRobot | errors and uptime | email / GitHub | before the client test |

Frankfurter needs no account. Apple Developer: not needed (Android-only
prototype, C3).

Security rules for the public repository:
- `.env` files ignored by git from the first commit; secret scanning on.
- Only fake data in the repository; seeds are generated, never real
  exports.
- Every key added as a GitHub Actions secret or Supabase secret by
  Franco himself, through the website.
