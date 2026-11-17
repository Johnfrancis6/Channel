# AI / ML fraud detection inside a business financial management application (state: November 2026)

Reading notes for the writer:
- "Verified on page" = I fetched the primary page. "Snippet" = taken from a search-result summary only, not opened; treat as lower confidence.
- "VENDOR CLAIM" = self-reported by the company selling or operating the system, not independently validated.
- Almost all published production results concern card / consumer payment fraud at very large scale. Evidence for B2B accounting fraud (invoices, vendors, journal entries) is mostly audit literature and academic papers, with far fewer production numbers.

## 1. Which approaches are used in production, and when?

### Takeaway
Production systems are layered: deterministic rules plus a supervised tabular model (gradient boosting at most companies; deep networks only at Stripe/Nubank/Revolut scale), with anomaly detection, graphs, sequence models and LLMs added as specialised layers. For a small team, rules + gradient boosting + simple anomaly scoring is the proven core; foundation models, GNNs and behavioural biometrics need data volumes or sensor access a mid-sized accounting app does not have.

### Cited Findings
**Supervised tabular models (gradient boosting vs deep learning)**
- Stripe Radar ran a "Wide & Deep" ensemble (XGBoost + deep neural network) until mid-2022, then moved to a DNN-only, ResNeXt-inspired multi-branch model; simply removing XGBoost would have cost 1.5% recall; training time fell by over 85% to under two hours (post dated 29 March 2023, verified on page; VENDOR CLAIM) — [Stripe, "How we built it: Stripe Radar"](https://stripe.dev/blog/how-we-built-it-stripe-radar)
- Stripe reported that a 10x increase in training transaction data produced significant model improvements, with a 100x experiment in progress (March 2023, verified on page) — i.e. the DNN advantage is tied to very large data — [Stripe](https://stripe.dev/blog/how-we-built-it-stripe-radar)
- Revolut's "Sherlock" card-fraud system is described as based on CatBoost gradient boosting, running on Google Cloud, with Couchbase as the in-memory profile/cache store (snippet; secondary source attributing to Revolut, and a Couchbase vendor case study) — [Couchbase customer page](https://www.couchbase.com/customers/revolut/); [Advisori summary](https://www.advisori.de/en/blog/revolut-s-ai-strategy-roadmap-key-takeways-learnings)
- Booking.com (Krutikov et al., arXiv 2405.13692, 2024) tested tabular Transformers against gradient-boosted decision trees on e-commerce fraud; finding as summarised: Transformers become a viable alternative only with pre-training, notably under selection bias and limited labels (snippet) — [arXiv 2405.13692](https://arxiv.org/pdf/2405.13692)
- A University of Coimbra master's thesis on payments-industry data examines why tree-based methods tend to beat deep learning on tabular data, attributing the gap to a mismatch between deep-learning priors and tabular data properties (snippet) — [Estudo Geral, Univ. Coimbra](https://estudogeral.sib.uc.pt/handle/10316/110585?mode=full)
- A comparison of Logistic Regression, Random Forest, LightGBM and a GRU on the public IEEE-CIS dataset (590,000+ anonymised online payment transactions, fraud under 4% of rows) exists as arXiv 2505.22521; I could not retrieve its metric values (snippet) — [review page](https://www.themoonlight.io/review/evaluating-supervised-learning-models-for-fraud-detection-a-comparative-study-of-classical-and-deep-architectures-on-imbalanced-transaction-data)

**Sequence / transformer / foundation models on transactions (large-data only)**
- Stripe announced a "Payments Foundation Model" at Stripe Sessions in May 2025: a self-supervised network producing a general-purpose vector per transaction, trained on tens of billions of transactions (snippet; VENDOR CLAIM) — [TechCrunch, 7 May 2025](https://techcrunch.com/2025/05/07/stripe-unveils-ai-foundation-model-for-payments-reveals-deeper-partnership-with-nvidia)
- Stripe's ML lead Gautam Kedia stated that detection of card-testing attacks on large users rose from 59% to 97% "overnight" with this model; TechCrunch phrased the same gain as "by 64%". Earlier models had reduced card-testing attacks by 80% gradually over two years. The figure applies to card testing on large businesses, not to all fraud (2025, snippet; VENDOR CLAIM, sources phrase the number differently) — [Analytics India Magazine](https://analyticsindiamag.com/global-tech/how-stripe-used-ai-to-boost-fraud-detection-from-59-97-overnight/); [TechCrunch](https://techcrunch.com/2025/05/07/stripe-unveils-ai-foundation-model-for-payments-reveals-deeper-partnership-with-nvidia); [Stripe blog, ML flywheel / card testing](https://stripe.com/de/blog/the-ml-flywheel-how-we-continually-improve-our-models-to-reduce-card-testing)
- Nubank's "nuFormer" (Braithwaite et al., arXiv 2507.23267, July 2025; blog series March-May 2025) pre-trains a causal transformer from scratch on raw transaction sequences with next-token prediction, then fine-tunes jointly with a tabular blending model ("joint fusion"). Nubank cites 100M+ customers and trillions of transactions/events (snippet) — [arXiv 2507.23267](https://arxiv.org/html/2507.23267v1); [Building Nubank](https://building.nubank.com/understanding-our-customers-finances-through-foundation-models/); [Building Nubank, fine-tuning](https://building.nubank.com/fine-tuning-transaction-user-models/)
- Revolut describes a tabular foundation model for credit-risk and fraud tasks (named STRIDER in its blog; a later "PRAGMA" model family is described in a Nebius customer story), scoring from an event timeline plus profile snapshot of up to ~1,300 tokens per channel (snippet; dates not confirmed) — [Revolut blog](https://www.revolut.com/blog/post/fromresearchtorealtime/); [Nebius customer story (vendor)](https://nebius.com/customer-stories/revolut)
- Monzo published multi-task representation learning across fraud subtypes, evaluated on unauthorised card fraud and on generalisation to rare/unseen behaviours (snippet; date not confirmed) — [Monzo, "Representation Learning for Enhanced Fraud Detection"](https://monzo.com/blog/representation-learning-for-enhanced-fraud-detection)

**Graph analytics / GNNs**
- Cheng et al., "Graph Neural Networks for Financial Fraud Detection: A Review" (arXiv 2411.05815, posted 1 Nov 2024; later in Frontiers of Computer Science, 2025) reviews over 100 studies and names managing large-scale financial graph data and adapting to dynamic patterns as the practical hurdles (snippet) — [arXiv 2411.05815](https://arxiv.org/abs/2411.05815v1)
- A 2021 paper on graph computing for financial crime states that size, speed, complexity and adversarial behaviour make deployment hard, with real-time processing and multi-channel updates as ongoing obstacles (snippet) — [arXiv 2103.01854](https://arxiv.org/pdf/2103.01854)
- Practitioner overviews list camouflage/disguise, scalability and label scarcity as the key GNN-fraud challenges (snippet) — [DataFunSummit summary](https://besthub.dev/articles/applying-graph-neural-networks-to-fraud-detection-background-research-progress-methods-and-resources-d9d4a5d864db)
- Mastercard says Decision Intelligence Pro "assesses relationships between multiple entities involved in a transaction" in under 50 ms (Feb 2024; VENDOR CLAIM) — [PYMNTS, Feb 2024](https://www.pymnts.com/artificial-intelligence-2/2024/mastercard-says-new-ai-model-ups-fraud-detection-by-20percent/)

**Unsupervised anomaly detection (autoencoders) — the one family with accounting-specific evidence**
- Schreyer, Sattarov, Borth, Dengel, Reimer (DFKI / PwC), arXiv 1709.05254 (Sept 2017, revised Aug 2018): journal entries scored by deep-autoencoder reconstruction error adjusted by the probability of each entry's attribute values; evaluated on two real-world journal-entry datasets; reported fewer false positives than baseline anomaly detectors, with accountants' feedback supporting relevance. Precision figures differ between arXiv versions (snippet) — [arXiv 1709.05254](https://arxiv.org/abs/1709.05254v2)
- Follow-up: adversarial autoencoders learning an interpretable latent space of journal entries for audit sampling (arXiv 1908.00734, KDD 2019 Workshop on Anomaly Detection in Finance) (snippet) — [arXiv 1908.00734](https://ar5iv.labs.arxiv.org/html/1908.00734)

**LLMs for document / invoice forgery**
- "Can Multi-modal (reasoning) LLMs detect document manipulation?" (arXiv 2508.11021, Aug 2025) benchmarks multimodal LLMs on a receipt-forgery dataset: top models generalise better out of distribution than conventional detectors, but several vision LLMs are inconsistent, and model size / reasoning ability correlate only weakly with accuracy; authors conclude task-specific fine-tuning is critical (snippet) — [arXiv 2508.11021](https://arxiv.org/html/2508.11021v1)
- AIForge-Doc (arXiv 2602.20569, Feb 2026): 4,061 images where numeric fields of real receipts/forms were forged with two AI inpainting APIs; in zero-shot tests GPT-4o scored 0.509, "essentially at chance" (snippet; metric name not confirmed) — [AIForge-Doc summary](https://www.opentrain.ai/papers/aiforge-doc-a-benchmark-for-detecting-ai-forged-tampering-in-financial-and-form--arxiv-2602.20569/)
- DocForge-Bench (arXiv 2603.01433, March 2026): zero-shot benchmark of 14 methods over eight datasets (text tampering, receipt forgery, ID documents); notes all eight datasets predate generative-AI editing, so diffusion/LLM forgeries remain a benchmark gap (snippet) — [arXiv 2603.01433](https://arxiv.org/pdf/2603.01433)
- Monzo uses a multimodal reasoning LLM live in the payment path, but only to turn customer questionnaire answers and evidence into structured semantic features; a supervised model and a meta-stacking ensemble produce the score. Quote: "we do not ask the LLM to decide whether a payment is fraudulent"; supervised models are kept for quantitative predictions because LLMs are weaker at calibrated probabilities (verified on page; publication date not shown in my fetch, reported as a 2025 post) — [Monzo, "Combining generative AI and predictive modelling to fight financial crime"](https://monzo.com/blog/combining-generative-ai-and-predictive-modelling-to-fight-financial-crime)

**Deepfakes / liveness**
- Arup case: a finance worker in Hong Kong joined a video call where the CFO and colleagues were deepfakes and transferred HK$200 million (about US$25.6 million) in 15 transactions to five accounts; widely reported in February 2024 (one source's "September 2025" date appears to be an error) (snippet) — [VentureBeat](https://venturebeat.com/security/25-million-deepfake-that-human-review-mfa-and-liveness-detection-all-missed); [AI Incident Database](https://incidentdatabase.ai/reports/5422)
- Liveness detection protects onboarding/login, not a live meeting; camera-injection attacks feed synthetic media directly into the camera stream to bypass liveness checks (snippet; partly vendor blogs) — [VentureBeat](https://venturebeat.com/security/25-million-deepfake-that-human-review-mfa-and-liveness-detection-all-missed)
- Entrust's 2026 identity fraud report, as relayed by a secondary blog: deepfakes in one in five biometric fraud attempts, deepfake selfies up 58%, injection attacks up 40% (snippet; VENDOR CLAIM via secondary source) — [DeepStrike](https://deepstrike.io/blogs/deepfake-statistics-2025)
- Pindrop figures on 2024 deepfake growth are quoted inconsistently (1,300% vs 680%) by secondary sources and measure different things; do not use as a single statistic (snippet) — [DeepStrike](https://deepstrike.io/blogs/deepfake-statistics-2025)

### Inferences
- Gradient boosting (XGBoost/LightGBM/CatBoost) is the right first supervised model for a small team: it was Stripe's own production component until 2022 and reportedly is Revolut's, and the published cases where deep/transformer models win all involve tens of billions of transactions or pre-training on huge corpora.
- LLMs are currently best used as feature extractors and consistency checkers on documents and free text (does the IBAN country match the supplier, do totals add up, is the invoice number format consistent), not as pixel-level forgery detectors: 2026 benchmarks show near-chance zero-shot results on AI-inpainted numeric fields. Monzo's production pattern (LLM produces structured features, supervised model decides) is the transferable design.
- For deepfake CEO/CFO fraud, the effective control inside a finance app is procedural (out-of-band call-back, dual approval, cooling-off on new beneficiaries), not a detection model.
- Graph methods are usable at small scale as simple link analysis (shared IBAN, address, phone, email domain, device between vendors/employees/clients) without a GNN.

### Gaps
- Behavioural biometrics and device fingerprinting: I found no primary, non-vendor source with production results in my searches. Not covered beyond this note.
- PayPal: no primary source retrieved on its methods (graph/GNN, real-time) or results.
- Isolation Forest specifically: no production case study retrieved; only the autoencoder accounting papers.
- Feedzai: only its research papers on explainability were retrieved (section 6), no platform performance figures.
- No independent benchmark compares LLM invoice-forgery detection on real B2B invoices (the benchmarks are receipts/forms/IDs).

## 2. Recommended layered architecture, real-time vs batch, feature stores, feedback loops, latency

### Takeaway
The reference architecture is: feature computation in three freshness tiers, detectors that only output a fraud type and confidence, a separate policy/action layer, then case management and human review whose outcomes feed back as labels. Card-payment latency budgets (under 50-100 ms) are published; an accounting app mostly does not need them, since most of its decisions (invoice approval, payment run, vendor change) tolerate seconds to hours.

### Cited Findings
- Monzo's platform runs each transaction through four steps: choose which controls to run, load features, run detectors (mostly ML models), apply the decision. Detectors output fraud type and confidence but take no position on the response; a separate "Action Applier" enforces decisions and safeguards such as rate limits (snippet; InfoQ summary dated Nov 2025) — [Monzo, "Build a reactive fraud prevention platform"](https://monzo.com/blog/build-a-reactive-fraud-prevention-platform); [InfoQ](https://www.infoq.com/news/2025/11/monzo-real-time-fraud-detection)
- Monzo splits features into just-in-time (computed from the current transaction), near-real-time (precomputed, cached, read at payment time) and batch (refreshed periodically), organised as a DAG; every control's inputs, decisions and metadata are stored in BigQuery for observability (snippet) — [Monzo](https://monzo.com/blog/build-a-reactive-fraud-prevention-platform)
- Monzo's stack: real-time inference in its AWS/Go/Cassandra stack with features from NSQ event streams or on-demand RPC; training on GCP (2022 post, snippet) — [Monzo's machine learning stack](https://monzo.com/blog/2022/04/26/monzos-machine-learning-stack)
- Stripe Radar: decisions in under 100 ms, evaluating "more than 1,000 characteristics" per transaction (March 2023, verified on page; VENDOR CLAIM) — [Stripe](https://stripe.dev/blog/how-we-built-it-stripe-radar)
- Stripe's feature platform Shepherd (an adaptation of Airbnb's open-source Chronon) uses Flink streaming and reports p99 feature freshness of 150 ms (snippet; VENDOR CLAIM) — [Stripe, Shepherd](https://stripe.com/blog/shepherd-how-stripe-adapted-chronon-to-scale-ml-feature-development)
- Revolut Sherlock: transactions evaluated in under 50 ms (Couchbase case study; VENDOR CLAIM). Revolut's general scoring platform targets a double-digit-millisecond p99 feature-read SLA within a sub-second end-to-end inference budget (snippet) — [Couchbase](https://www.couchbase.com/customers/revolut/); [Revolut blog](https://www.revolut.com/blog/post/fromresearchtorealtime/)
- Mastercard Decision Intelligence Pro: score produced in less than 50 ms (Feb 2024; VENDOR CLAIM) — [PYMNTS](https://www.pymnts.com/artificial-intelligence-2/2024/mastercard-says-new-ai-model-ups-fraud-detection-by-20percent/)
- Stripe's guidance: scoring sits inside the checkout authorisation window, so added latency lowers conversion and models must be light enough to score in real time (snippet) — [Stripe guide](https://stripe.com/resources/more/payment-fraud-detection-and-approval-rates)
- Monzo's LLM step is a second, slower stage triggered only on high-risk payments: the whole "Fraud Prevent agent" process takes under 10 seconds; its final score decides whether the payment proceeds or goes to human investigation (verified on page) — [Monzo](https://monzo.com/blog/combining-generative-ai-and-predictive-modelling-to-fight-financial-crime)
- Monzo's agent library has three parts: core library (LLM reasoning steps, logical guardrails, supervised ML models), a backtesting harness over many thousands of recent historical cases, and a real-time backend using an internal AI gateway to several LLM vendors (verified on page) — [Monzo](https://monzo.com/blog/combining-generative-ai-and-predictive-modelling-to-fight-financial-crime)
- Uber's Project RADAR (post dated 1 Feb 2022) is batch-style time-series anomaly detection over aggregated payment streams, not per-transaction scoring; it proposes rules that analysts review and approve, with hand-off through Jira; Uber states fraud "cannot be stopped by some black-box AI algorithms" (snippet) — [Uber Engineering](https://www.uber.com/en-DK/blog/project-radar-intelligent-early-fraud-detection)
- Dal Pozzolo et al. (2015): investigator feedback on alerts and delayed labels (e.g. chargebacks arriving later) should be handled separately; training two classifiers, one on each, and aggregating them substantially improved alert precision in their experiments (snippet) — [Dal Pozzolo et al., IJCNN 2015](https://boracchi.faculty.polimi.it/docs/2015_04_Credit_Card_Fraud_Detection_DalPozzolo_Boracchi_Caelen_Alippi_Bontempi.pdf)

### Inferences
- For an accounting/invoicing/treasury app, only outgoing payment initiation and login/session events need synchronous scoring; a budget of a few hundred milliseconds to a few seconds is acceptable because there is no card-authorisation window. Invoice ingestion, vendor-master changes and journal entries can be scored asynchronously (seconds to minutes) or in nightly batch (ledger-wide tests).
- A small team does not need a feature-store product initially: Monzo's three-tier idea can be implemented as SQL views/materialised aggregates (batch), a cache table updated on events (near-real-time) and in-request computation (just-in-time). The non-negotiable part is logging the exact feature values used at decision time, to avoid training/serving skew and to make decisions auditable.
- Keep "detector" and "action" separate from day one (Monzo pattern): the same score can then drive different policies per tenant (warn, require second approver, hold payment), which matters in a multi-tenant B2B app.
- A two-stage design (cheap score on everything, expensive LLM/document analysis only on the risky slice) controls LLM cost and latency.

### Gaps
- No published architecture for fraud detection in an SMB accounting/ERP SaaS (multi-tenant, small data per tenant) was found; the above is transposed from payment companies.
- No source retrieved on case-management tooling choices (build vs buy) or on open-source rule engines / feature stores suitable for small teams.
- Latency figures are all vendor self-reports; none is independently measured.

## 3. Cold start: starting with little or no labelled fraud data

### Takeaway
Start with deterministic controls on the highest-loss scenarios (vendor bank-detail changes, duplicate invoices/payments, three-way-match discrepancies), add statistical tests and unsupervised scoring to rank items for review, and collect reviewer outcomes as labels from day one. Benford's law is a weak, population-level screen, not a per-transaction detector.

### Cited Findings
**Where the losses are (to prioritise rules)**
- AFP 2025 Payments Fraud and Control Survey (covering 2024): 79% of organisations were victims of attempted or actual payments fraud; business email compromise was the top avenue, cited by 63% of respondents; vendor impersonation cited by 60%; spoofed emails the most prevalent BEC type at 79%. A bank page quoting 45% for vendor impersonation conflicts with AFP-sourced summaries (snippet; full report is members-only) — [AFP press release](https://www.financialprofessionals.org/about/learn-more/press-releases/Details/survey-79-percent-of-organizations-were-victims-of-attempted-or-actual-payments-fraud-activity-in-2024); [Truist key-highlights PDF](https://truist.com/content/dam/truist-bank/us/en/documents/info/cci/2025-afp-payments-fraud-control-survey-report-key-highlights.pdf); conflicting figure at [First Business Bank](https://firstbusiness.bank/resource-center/how-to-prevent-payment-fraud/)
- ACFE Report to the Nations 2024: median loss per occupational fraud case US$145,000, average US$1.7 million; billing schemes in 22% of cases with median loss US$100,000; 43% of frauds detected by tip (52% of tips from employees); detection took about 12 months on average (snippet from summaries of the report) — [NYSSCPA](https://nysscpa.org/news/1052118-report-worldwide-organizations-lose-billions-to-fraud-2024-03-21); [Mondaq](https://www.mondaq.com/canada/white-collar-crime-anticorruption-fraud/1486950/the-cost-of-occupational-fraud-from-the-2024-acfe-report); [Anchin](https://anchin.com/wp-content/uploads/2024/08/2024-ACFE-Occupational-Fraud-Report.pdf); [report PDF copy](https://www.ivey.uwo.ca/media/kjljj5cy/2024-report-to-the-nations.pdf)

**Duplicate invoices / payments**
- APQC benchmark data as quoted by Corpay: duplicate and erroneous payments run about 0.8% (top quartile) to above 2% (bottom quartile) of total disbursements, median 1.5%; IOFM estimate up to 1.5% of outgoing cash; another vendor blog says 1-5% of AP spend. Corpay itself cautions these are estimates across very different control environments and a company should measure its own rate (snippet; VENDOR blog relaying benchmarks, not verified at APQC) — [Corpay](https://www.corpay.com/en-IE/resources/blog/duplicate-payment-detection); [Dost](https://www.dost.io/blog/duplicate-payments-in-accounts-payable-how-to-detect-and-prevent-them)
- Exact-match ERP checks miss "fuzzy duplicates" that match on amount but differ on an identifier (e.g. "INV-5521" vs "5521-OPS"); the fix is normalising fields before comparison (snippet; vendor blog) — [Corpay](https://www.corpay.com/en-IE/resources/blog/duplicate-payment-detection)
- Claim that "Deloitte's AP Controls Benchmark 2025" shows AI duplicate detection catching 98% of duplicates before payment vs 63% for manual review comes from a secondary vendor blog and could not be verified at Deloitte: treat as unverified (snippet) — [Everworker](https://everworker.ai/blog/ai_automation_reduce_ap_errors_cfo)

**Vendor master / bank-detail changes**
- Vendor-master hygiene is described as the root cause behind more duplicate payments than any matching-rule gap; recommended controls are validating banking details before they go active, restricting who can create/edit vendors, and treating every bank change as a control event with enforced dual approval and independent validation (snippet; vendor blogs) — [Corpay](https://www.corpay.com/en-IE/resources/blog/duplicate-payment-detection)

**Benford's law**
- ISACA Journal: Benford analysis on fewer than about 1,000 entries produces too many spikes and false positives; it should be applied only to large data sets, assumes non-constrained numbers and fails when data spans only one or two orders of magnitude (2011 article, snippet) — [ISACA Journal](https://www.isaca.org/resources/isaca-journal/past-issues/2011/understanding-and-applying-benfords-law)
- Journal of Accountancy (Sept 2022): journal-entry and AP data naturally spike at multiples of 10 because people price and estimate in round numbers, so spikes can look anomalous when nothing is wrong; duplicates and human error often explain deviations; Benford testing can still direct auditors to clusters just under an approval threshold (HealthSouth: fictitious entries kept below a US$5,000 testing threshold) (snippet) — [Journal of Accountancy](https://www.journalofaccountancy.com/issues/2022/sep/using-benfords-law-reveal-journal-entry-irregularities/)
- A fraudster who falsifies only one or two entries is unlikely to be caught by Benford analysis (advisory-firm article, snippet) — [Miller Kaplan](https://www.millerkaplan.com/knowledge-center/how-auditors-use-benfords-law-to-assess-transactions/)

**Unsupervised and synthetic data**
- Autoencoder reconstruction error on journal entries works without labels and was validated on two real datasets (Schreyer et al., 2017/2018) (snippet) — [arXiv 1709.05254](https://arxiv.org/abs/1709.05254v2)
- ERP-RiskBench (Mishra, arXiv 2603.06671, 3 March 2026) combines the real BPI 2019 procure-to-pay event log, the public credit-card fraud dataset, the PaySim simulator and a new synthetic procurement set "ERP-Synth"; it reports that procurement-control features, especially three-way-matching discrepancies, rank as the most informative predictors, and that leakage-safe evaluation protocols lower previously inflated accuracy estimates (snippet; single-author preprint) — [arXiv 2603.06671](https://arxiv.org/abs/2603.06671)
- Booking.com's result that pre-trained tabular Transformers help most under limited labels and selection bias is the main published evidence for self-supervised pre-training as a label-scarcity remedy, at Booking's data scale (snippet) — [arXiv 2405.13692](https://arxiv.org/pdf/2405.13692)

### Inferences
- Suggested build order for a small team, by expected loss prevented per unit of effort: (1) bank-detail change control (hold + out-of-band verification + dual approval + first-payment-to-new-account flag), because BEC/vendor impersonation hits 60-63% of surveyed organisations; (2) fuzzy duplicate invoice/payment detection, since duplicates are a measurable percentage of disbursements; (3) three-way match and approval-threshold rules; (4) per-tenant anomaly scores (amount vs vendor history, new payee, timing); (5) supervised model once a few hundred confirmed positives exist across tenants.
- Benford tests belong in a periodic, per-tenant "ledger health" report for tenants with thousands of entries, not in real-time alerting.
- In a multi-tenant SaaS, pooled cross-tenant signals (same IBAN appearing as a new bank account for different vendors across tenants; IBANs previously confirmed fraudulent) are the realistic small-scale equivalent of consortium data, subject to privacy/contract constraints. This is my inference, not a sourced practice.
- Synthetic data (PaySim, ERP-Synth) is useful to test pipelines and rules end to end, but ERP-RiskBench's own leakage finding implies results on synthetic/benchmark data overstate real performance.

### Gaps
- No source found quantifying how many labelled fraud cases are needed before a supervised model beats rules.
- No primary source retrieved on consortium data sharing, or on bank-account verification services (UK Confirmation of Payee, EU Verification of Payee, etc.) and their measured effect.
- APQC and Deloitte figures were not verified at the original publisher.
- No retrieved source evaluates Isolation Forest on accounting data.

## 4. Evaluation: imbalance, precision/recall, false positives, drift, realistic figures

### Takeaway
Fraud is roughly 1 in 1,000 to 1 in 10,000 events, so accuracy and ROC-AUC mislead; evaluate with precision-recall metrics, precision among the top-k alerts that reviewers can actually handle, time-ordered validation, and monitoring for drift and delayed labels. Published headline numbers are almost all vendor self-reports on card fraud and are not transferable targets.

### Cited Findings
- Base rates: Stripe says fraud is roughly 1 in 1,000 payments (March 2023, verified on page); Monzo cites about 1 in 10,000 transactions (snippet) — [Stripe](https://stripe.dev/blog/how-we-built-it-stripe-radar); [Monzo](https://monzo.com/blog/representation-learning-for-enhanced-fraud-detection)
- Stripe Radar incorrectly blocks about 0.1% of legitimate payments (March 2023, verified on page; VENDOR CLAIM) — [Stripe](https://stripe.dev/blog/how-we-built-it-stripe-radar)
- Stripe's worked example of the false-positive problem: if 0.1% of transactions are fraudulent and the system wrongly blocks 1.0% of legitimate ones, it blocks ten times as many legitimate customers as fraudsters (snippet) — [Stripe guide](https://stripe.com/resources/more/payment-fraud-detection-and-approval-rates)
- The open "Fraud Detection Handbook" (Université Libre de Bruxelles / Worldline) recommends repeated hold-out and prequential (time-ordered) validation and reports ROC AUC, Average Precision and "Card Precision@100", a top-k precision metric matched to investigator capacity (snippet) — [Fraud Detection Handbook, validation strategies](https://fraud-detection-handbook.github.io/fraud-detection-handbook/Chapter_5_ModelValidationAndSelection/ValidationStrategies.html)
- Dal Pozzolo et al. (2015): alert precision is the investigators' primary concern; labels arrive late and only for alerted items (feedback), which biases training; delayed labelling causes longer periods of poor accuracy per a separate delayed-label study (snippet) — [Dal Pozzolo et al.](https://boracchi.faculty.polimi.it/docs/2015_04_Credit_Card_Fraud_Detection_DalPozzolo_Boracchi_Caelen_Alippi_Bontempi.pdf); [survey on delayed partially labelled streams, arXiv 2106.09170](https://arxiv.org/pdf/2106.09170)
- ERP-RiskBench (March 2026): accuracy is misleading at extreme imbalance, and leakage-safe protocols notably reduce previously inflated estimates (snippet) — [arXiv 2603.06671](https://arxiv.org/abs/2603.06671)
- Reported results (all VENDOR CLAIMS unless noted):
  - Mastercard Decision Intelligence Pro: "initial modeling" shows fraud detection rates up 20% on average and up to 300% in some instances; Mastercard's own analysis reports false positives reduced by more than 85%; announced Feb 2024 as preliminary, with no independent validation found — [PYMNTS](https://www.pymnts.com/artificial-intelligence-2/2024/mastercard-says-new-ai-model-ups-fraud-detection-by-20percent/); [Fintech Global, 2 Feb 2024](https://fintech.global/2024/02/02/mastercard-launches-genai-tool-to-combat-fraud/)
  - Visa: "in 2024 alone, Visa helped block $40 billion in fraudulent activity" using hundreds of AI models; the same US$40 billion figure was also reported for 2023 (80 million transactions) and mislabelled as 2025 by some outlets; it refers to attempted fraud blocked, not confirmed losses — [Visa](https://corporate.visa.com/en/sites/visa-perspectives/security-trust/ai-and-trust-at-scale.html); [ThePrint/Reuters, 2024](https://theprint.in/tech/visa-prevented-40-billion-worth-of-fraudulent-transactions-in-2023-official/2188132)
  - Revolut Sherlock: 96% fraud catch rate and savings above US$3 million per Couchbase materials; one secondary source calls the 96% "accuracy", conflating metrics (date not confirmed) — [Couchbase case study PDF](https://info.couchbase.com/rs/302-GJY-034/images/Revolut_Case_Study.pdf)
  - Stripe foundation model: card-testing detection on large users 59% to 97% (2025) — [Analytics India Magazine](https://analyticsindiamag.com/global-tech/how-stripe-used-ai-to-boost-fraud-detection-from-59-97-overnight/)
  - Monzo LLM-assisted agent: over 20% increase in both the £ value and number of authorised (APP) fraud cases prevented, and fewer legitimate payments diverted to human review (no figure) (verified on page; baseline not disclosed) — [Monzo](https://monzo.com/blog/combining-generative-ai-and-predictive-modelling-to-fight-financial-crime)
- Resampling: one practitioner blog on IEEE-CIS trained with SMOTE and evaluated on an unsampled validation set, with gradient boosting leading; this is a single non-peer-reviewed result (snippet) — [blog post](https://cloudflare-blog-27j.pages.dev/machine-learning/data-science/2026/06/04/credit-card-fraud-detection.html)

### Inferences
- Define the operating point from reviewer capacity: if a tenant's finance team can review N items per week, the metric that matters is precision and recall (ideally value-weighted) within the top N, analogous to Card Precision@100.
- Value-weight everything: Monzo reports both count and £ value; in B2B a single diverted supplier payment can exceed a year of small anomalies.
- With a base rate near 0.01-0.1%, even a 1% false-positive rate yields 10-100 false alerts per true one (Stripe's arithmetic); alert volume must be budgeted before thresholds are set.
- Because labels exist only for reviewed items, keep a small random sample of non-alerted items for review to estimate missed fraud and to de-bias training (follows from Dal Pozzolo's feedback/delayed-label distinction; the random-sample practice itself is my inference).
- Always split train/test by time, and in a multi-tenant app also hold out whole tenants, to avoid the leakage ERP-RiskBench describes.

### Gaps
- No source retrieved quantifies alert fatigue (e.g. typical false-positive ratios per true alert in AP or transaction monitoring, or reviewer-performance decay).
- No peer-reviewed source retrieved showing whether SMOTE helps or harms versus class weighting/threshold tuning.
- No published precision/recall figures for accounting-specific detections (duplicates, ghost vendors, journal-entry tests) in production.
- No retrieved source on concrete drift-monitoring methods (PSI, score-distribution alerts) or retraining cadence; Stripe's post does not state its retraining cadence.

## 5. Accounting-specific detections

### Takeaway
The audit literature supplies a catalogue of cheap, explainable tests (duplicates, threshold-hugging and round amounts, unusual timing, vendor-master anomalies, three-way-match breaks); the strongest published ML evidence is autoencoder anomaly scoring of journal entries and the finding that three-way-match discrepancies are the most informative procurement features.

### Cited Findings
- Billing schemes (which include shell/ghost vendors and personal purchases) were tied for the most common asset-misappropriation scheme in ACFE's 2024 report: 22% of cases, median loss US$100,000 (snippet) — [Mondaq summary of ACFE 2024](https://www.mondaq.com/canada/white-collar-crime-anticorruption-fraud/1486950/the-cost-of-occupational-fraud-from-the-2024-acfe-report)
- Occupational fraud is detected by tip in 43% of cases and runs about 12 months before detection, which is the baseline that continuous analytics is meant to shorten (ACFE 2024, snippet) — [NYSSCPA](https://nysscpa.org/news/1052118-report-worldwide-organizations-lose-billions-to-fraud-2024-03-21); [Anchin](https://anchin.com/wp-content/uploads/2024/08/2024-ACFE-Occupational-Fraud-Report.pdf)
- Threshold avoidance: clusters of entries just below an approval/testing limit (HealthSouth, below US$5,000) are a documented pattern that digit analysis can surface (snippet) — [Journal of Accountancy, Sept 2022](https://www.journalofaccountancy.com/issues/2022/sep/using-benfords-law-reveal-journal-entry-irregularities/)
- Round amounts: natural spikes at multiples of 10 in journal-entry and AP data mean a round-amount test produces many innocent hits and needs context (snippet) — [Journal of Accountancy](https://www.journalofaccountancy.com/issues/2022/sep/using-benfords-law-reveal-journal-entry-irregularities/)
- Duplicate payments: fuzzy matching on normalised invoice number + vendor + amount catches cases exact-match ERP checks miss; vendor-master duplicates are a root cause (snippet; vendor blog) — [Corpay](https://www.corpay.com/en-IE/resources/blog/duplicate-payment-detection)
- Journal-entry anomaly detection with deep autoencoders flags both "global" anomalies (rare attribute values) and "local" anomalies (unusual attribute combinations) — framing from Schreyer et al.; evaluated on two real journal-entry datasets with accountant feedback (snippet) — [arXiv 1709.05254](https://ar5iv.arxiv.org/html/1709.05254)
- Three-way-matching discrepancies (PO vs goods receipt vs invoice) ranked as the most informative predictors in ERP-RiskBench, which uses the real BPI 2019 procurement log (March 2026 preprint, snippet) — [arXiv 2603.06671](https://arxiv.org/abs/2603.06671)

### Inferences
- A practical first catalogue for the app (standard audit tests; items without a citation above are my synthesis of common practice and should be presented as such): fuzzy duplicate invoices/payments; new or changed vendor bank account followed by payment within N days; vendor sharing IBAN/address/phone with an employee or another vendor; vendors with no tax ID or only round-amount invoices; invoices just under an approval threshold or split across the threshold; sequential invoice numbers from one vendor; entries posted out of hours, on weekends/holidays or backdated into a closed period; manual entries to rarely used accounts or unusual debit/credit pairs; same user creating a vendor and approving its payment (segregation-of-duties violation); credit notes/refunds to an account different from the original payer.
- Segregation-of-duties checks are pure access-log/rule logic and require no ML; they are also preventive when enforced in the workflow.
- Each test should produce a named reason so that several weak signals can be combined into one ranked item instead of separate alerts.

### Gaps
- I did not retrieve the text of ISA 240 / AU-C 240 or IIA/ISACA guidance listing journal-entry test criteria (weekend/out-of-hours postings, round amounts, unusual users); these criteria are widely used but are uncited here.
- No sourced evidence found for ghost-vendor detection performance, segregation-of-duties analytics results, or out-of-hours tests' hit rates.
- No data on how these tests perform in small companies where one person legitimately holds several roles.

## 6. Explainability and human-in-the-loop

### Takeaway
Production systems expose reasons to users and keep humans on ambiguous or high-impact decisions, but controlled studies show that SHAP-style explanations alone do not reliably improve analysts' decisions; reason codes tied to concrete, checkable facts and related-record views are better supported.

### Cited Findings
- Stripe launched "risk insights" in 2020 showing which transaction features contributed to a decline, later adding maps of purchase/shipping locations and views of related transactions (verified on page) — [Stripe](https://stripe.dev/blog/how-we-built-it-stripe-radar)
- Weerts et al. (arXiv 1907.03324, 2019, with Rabobank): in a human-grounded experiment with analysts processing alerts with and without SHAP explanations, results suggest SHAP explanations alone are possibly not that useful for alert processing, although they did affect the reasoning process (snippet) — [arXiv 1907.03324](https://arxiv.org/pdf/1907.03324)
- Weerts et al. companion paper: even calibrated confidence scores can be inaccurate and misleading for alert processing; proposes case-based reasoning (showing similar past cases) (snippet) — [arXiv 1907.03334](https://web3.arxiv.org/pdf/1907.03334)
- Feedzai (Jesus et al., arXiv 2101.08758, 2021): application-grounded evaluation of LIME, SHAP and TreeInterpreter with real fraud analysts, real data and a deployed model, measuring accuracy, recall, false-positive rate and decision time; LIME was the least preferred (snippet; vendor research paper) — [arXiv 2101.08758](https://ar5iv.labs.arxiv.org/html/2101.08758)
- Feedzai TimeSHAP (Bento et al., arXiv 2012.00073, 2020): extends KernelSHAP to sequence models, validated on a real account-takeover model (GRU + classifier); an attribution pointed to potentially discriminatory reasoning, later confirmed as higher false-positive rates for older clients (snippet) — [arXiv 2012.00073](https://ar5iv.labs.arxiv.org/html/2012.00073)
- Uber RADAR: analysts review and approve system-proposed rules; Uber argues fraud cannot be stopped by black-box algorithms (Feb 2022, snippet) — [Uber Engineering](https://www.uber.com/en-DK/blog/project-radar-intelligent-early-fraud-detection)
- Monzo: human expert investigators resolve cases with no definitive automated decision and high-complexity escalations; outputs are governed by thresholds calibrated to risk appetite, operating cost and customer impact; LLM steps are wrapped in logical guardrails and backtested on thousands of historical cases (verified on page) — [Monzo](https://monzo.com/blog/combining-generative-ai-and-predictive-modelling-to-fight-financial-crime)

### Inferences
- For a finance app, the most useful explanation is a checkable statement ("bank account changed 2 days ago; first payment to this IBAN; amount 4x this vendor's median") plus the related records, rather than raw SHAP bars. SHAP on a gradient-boosting model is still a cheap way to generate candidate reason codes, which should be mapped to plain-language templates.
- Explanations double as a fairness/bias audit tool (TimeSHAP finding), relevant if the app scores clients or employees.
- Human-in-the-loop should be asymmetric: automatic holds are acceptable for reversible actions (delay a payment pending a second approval), while accusations or account closures need a person.

### Gaps
- No retrieved source on legal requirements for explanation/human review (e.g. GDPR Art. 22, EU AI Act classification of fraud detection); this needs a dedicated legal check.
- No study found on explanation usefulness for accountants/AP clerks (the studies involve bank fraud analysts).

## 7. Published case studies (summary table of what is actually reported)

### Takeaway
Case studies agree on the pattern (network-scale data, layered rules + ML, fast scoring, human review, steady move toward learned representations) but their numbers are self-reported, on card/consumer payments, and at volumes thousands of times beyond an SMB finance app.

### Cited Findings
- Stripe Radar (VENDOR CLAIM, March 2023): 1,000+ characteristics, under 100 ms, about 0.1% of legitimate payments wrongly blocked, XGBoost+DNN replaced by DNN-only in mid-2022, in development almost seven years — [Stripe](https://stripe.dev/blog/how-we-built-it-stripe-radar)
- Stripe Payments Foundation Model (VENDOR CLAIM, May 2025): trained on tens of billions of transactions; card-testing detection for large users 59% to 97% — [TechCrunch](https://techcrunch.com/2025/05/07/stripe-unveils-ai-foundation-model-for-payments-reveals-deeper-partnership-with-nvidia); [Analytics India Magazine](https://analyticsindiamag.com/global-tech/how-stripe-used-ai-to-boost-fraud-detection-from-59-97-overnight/)
- Revolut Sherlock (VENDOR/secondary, date not confirmed): CatBoost-based, under 50 ms, 96% catch rate, over US$3 million saved; later tabular foundation-model work — [Couchbase](https://www.couchbase.com/customers/revolut/); [Revolut blog](https://www.revolut.com/blog/post/fromresearchtorealtime/)
- Monzo (primary engineering posts, 2022-2025): reactive platform with feature tiers and detector/action separation; multi-task representation learning; LLM as feature extractor in the payment path with over 20% more authorised fraud prevented — [Monzo platform](https://monzo.com/blog/build-a-reactive-fraud-prevention-platform); [Monzo gen-AI post](https://monzo.com/blog/combining-generative-ai-and-predictive-modelling-to-fight-financial-crime)
- Nubank (primary posts and arXiv, 2025): transformer pre-trained on transaction sequences plus joint fusion with tabular features; the retrieved material is about general customer modelling, not fraud-specific results — [arXiv 2507.23267](https://arxiv.org/html/2507.23267v1)
- Mastercard Decision Intelligence Pro (VENDOR CLAIM, Feb 2024, preliminary modelling): +20% average detection, up to +300%, false positives down over 85%, under 50 ms, described as scanning about one trillion data points — [PYMNTS](https://www.pymnts.com/artificial-intelligence-2/2024/mastercard-says-new-ai-model-ups-fraud-detection-by-20percent/); [Fintech Global](https://fintech.global/2024/02/02/mastercard-launches-genai-tool-to-combat-fraud/)
- Visa (VENDOR CLAIM): US$40 billion of attempted fraud blocked in a year (attributed to 2023 and to 2024 in different statements); more than US$10 billion (later about US$12 billion) technology investment over five years — [Visa](https://corporate.visa.com/en/sites/visa-perspectives/security-trust/ai-and-trust-at-scale.html); [Benzinga](https://benzinga.com/z/39913436)
- Uber RADAR (primary, Feb 2022): human-in-the-loop, batch anomaly detection that proposes rules — [Uber Engineering](https://www.uber.com/en-DK/blog/project-radar-intelligent-early-fraud-detection)
- Booking.com (arXiv, 2024): tabular Transformers vs GBDT under selection bias — [arXiv 2405.13692](https://arxiv.org/pdf/2405.13692)

### Inferences
- None of these companies publishes precision, recall and base rate together on a fixed dataset, so the figures cannot be compared with one another or used as targets.
- The transferable lessons are architectural (layering, feature tiers, detector/action split, LLM-as-feature-extractor, human escalation, backtesting harness), not numerical.

### Gaps
- PayPal, Feedzai (platform results), Airbnb (only a 2014 high-level post surfaced) and current Visa model details: no primary engineering material retrieved.
- No case study found from an accounting/ERP/AP-automation vendor with independently verifiable results.
- Several items rest on search snippets (marked) rather than fetched pages; the only pages fully fetched and checked were Stripe's Radar post and Monzo's gen-AI post.
