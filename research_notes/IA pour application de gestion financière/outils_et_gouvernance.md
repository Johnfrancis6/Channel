# Tools, services and governance principles for AI features in a small-team business finance application

Date checked for everything below: 2026-11-17. Verification labels used throughout:

- **[V]** = verified this session on the linked page or search result.
- **[V-3P]** = seen this session but only on a third-party / aggregator / competitor page, not the vendor's own page.
- **[M]** = from model knowledge (cutoff June 2026); the linked official URL was NOT opened this session. Treat as "to re-check before quoting", especially prices.

## 1. Open-source building blocks: maturity, licence, what each is good for

### Takeaway
A complete fraud/risk/forecasting/OCR stack exists in permissive open source (BSD/MIT/Apache); the points that need care are copyleft or non-commercial terms: Jube (AGPLv3), Neo4j Community (GPLv3), OpenSanctions data (free only for non-commercial use), and Marble (open core, licence text not confirmed). Licences for the mainstream ML libraries were not re-opened this session and are tagged [M].

### Cited Findings

**ML core, anomaly detection, explainability, MLOps (all [M] for licence; mature, widely used)**
- scikit-learn: BSD-3-Clause; baseline models (logistic regression, Isolation Forest, calibration, pipelines). [M] — [scikit-learn](https://github.com/scikit-learn/scikit-learn)
- XGBoost: Apache-2.0; LightGBM: MIT. Gradient-boosted trees are the standard for tabular fraud/credit scoring. [M] — [XGBoost](https://github.com/dmlc/xgboost), [LightGBM](https://github.com/microsoft/LightGBM)
- PyOD: BSD-2-Clause; 40+ unsupervised outlier detectors (useful when there are no fraud labels). [M] — [PyOD](https://github.com/yzhao062/pyod)
- River: BSD-3-Clause; online/streaming learning and drift detection. [M] — [River](https://github.com/online-ml/river)
- SHAP: MIT; per-decision feature attributions (reason codes for alerts and scores). [M] — [SHAP](https://github.com/shap/shap)
- Evidently: Apache-2.0; data/prediction drift reports and tests. [M] — [Evidently](https://github.com/evidentlyai/evidently)
- MLflow: Apache-2.0; experiment tracking and model registry (versioning = part of the audit trail). [M] — [MLflow](https://github.com/mlflow/mlflow)
- Feast: Apache-2.0; feature store (point-in-time correct features). Usually overkill for a small team at the start. [M] — [Feast](https://github.com/feast-dev/feast)

**Graph tools [M]**
- NetworkX: BSD-3-Clause, in-memory graph analysis (cycles, shared IBAN/phone/device between suppliers). — [NetworkX](https://github.com/networkx/networkx)
- PyTorch Geometric (PyG): MIT, graph neural networks; needs labelled data and ML expertise. — [PyG](https://github.com/pyg-team/pytorch_geometric)
- Neo4j: Community Edition GPLv3, Enterprise commercial; AuraDB has a free tier. — [Neo4j licensing](https://neo4j.com/licensing/)

**Rule / decision / transaction-monitoring engines**
- Marble (Checkmarble): "Open Source core" deployable on-premise or as SaaS, plus "a licensed option with Enterprise features"; covers transaction monitoring, AML screening and case investigation; 624 GitHub stars; self-hosting needs Docker, 4 GB RAM minimum, 10 GB disk; no prices on the page. [V] The exact licence name was NOT visible on the fetched page. — [checkmarble/marble](https://github.com/checkmarble/marble)
- Marble integrates OpenSanctions for screening (announced on the OpenSanctions forum as an open-source transaction-monitoring + screening combination). [V] — [OpenSanctions forum](https://discuss.opensanctions.org/t/marble-opensanctions-team-up-for-the-first-fully-open-source-transaction-monitoring-solution/71)
- Jube: open-source real-time AML and fraud transaction monitoring; "all features available under AGPLv3" per a third-party listing; AGPL means a modified version run as a network service must publish its source. [V-3P] — [Jube site](https://jube-home.github.io/aml-fraud-transaction-monitoring), [third-party listing](https://freedom251.com/apps/jube/), [repo](https://github.com/jube-home/jube)
- Tazama: Linux Foundation project (launched 28 Feb 2024 with Gates Foundation support), real-time transaction monitoring for fraud and AML; Apache-2.0; recognised as a Digital Public Good (Sept 2024). [V] — [DPG registry](https://www.digitalpublicgoods.net/r/tazama), [Linux Foundation press release](https://www.linuxfoundation.org/press/linux-foundation-launches-tazama-for-real-time-fraud-management)
- Tazama is reported to be working with the BCEAO (Central Bank of West African States) and rural banks in the Philippines — relevant for French-speaking West Africa. [V-3P] — [Dark Reading](https://www.darkreading.com/cyber-risk/anti-fraud-project-boosts-security-of-african-asian-financial-systems)
- Tazama code is under the `frmscoe` GitHub organisation; a `tazama-lf` organisation could not be confirmed. [V] — [frmscoe](https://redirect.github.com/frmscoe)
- GoRules Zen engine: MIT, embeddable business-rules engine (Rust core, Node/Python/Go bindings), JSON decision tables. [M] — [gorules/zen](https://github.com/gorules/zen)
- Drools: Apache-2.0, Java rules engine (Apache KIE); heavy for a small non-Java team. [M] — [Drools](https://github.com/apache/incubator-kie-drools)

**OCR / document tools [M]**
- Tesseract: Apache-2.0, classic OCR, weak on layout/tables. — [Tesseract](https://github.com/tesseract-ocr/tesseract)
- PaddleOCR: Apache-2.0, strong multilingual OCR + layout. — [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
- docTR (Mindee): Apache-2.0, deep-learning OCR. — [docTR](https://github.com/mindee/doctr)
- Docling (IBM, hosted by LF AI & Data): MIT, converts PDF/DOCX to structured Markdown/JSON incl. tables; good pre-processor for LLM extraction. — [Docling](https://github.com/docling-project/docling)

**Forecasting**
- Prophet: MIT; statsforecast (Nixtla): Apache-2.0, fast ARIMA/ETS/Theta baselines. [M] — [Prophet](https://github.com/facebook/prophet), [statsforecast](https://github.com/Nixtla/statsforecast)
- Nixtla TimeGPT (hosted foundation model, not open source): official docs show a 30-day free trial without credit card; the FAQ lists USD 99/month for up to 10,000 API calls; the marketing page says "Free plan available"; another FAQ passage mentions USD 1,000 in free credits and token-based billing. These pages do not agree with each other. [V] — [Nixtla pricing docs](https://docs.nixtla.io/docs/getting-started-timegpt_subscription_plans_and_pricing), [Nixtla FAQ](https://docs.nixtla.io/docs/getting-started-faq), [TimeGPT page](https://www.nixtla.io/timegpt)

**Sanctions / PEP data**
- OpenSanctions: data is free for non-commercial use (CC BY-NC 4.0 basis); for-profit business use requires a data licence. [V] — [Licensing](https://www.opensanctions.org/licensing/), [Free and non-commercial use](https://www.opensanctions.org/docs/commercial/exemption/)
- Three licence tiers; internal use at a flat rate; embedding bulk data in a product sold to customers needs a reseller/OEM licence; the API is pay-as-you-go, or bulk licence + self-hosted matching software; startup discounts exist. [V] — [Commercial FAQ](https://www.opensanctions.org/docs/commercial-faq), [Bulk licensing](https://www.opensanctions.org/sponsor)
- Bulk data price was EUR 595/month in a 2022 article (old figure; current price not confirmed). [V, dated] — [2022 SaaS API article](https://www.opensanctions.org/articles/2022-10-04-saas-api)

### Inferences
- Cheapest credible stack: PostgreSQL + scikit-learn/LightGBM + PyOD + SHAP + MLflow + Evidently, rules in GoRules Zen or plain code, NetworkX for supplier-graph checks, Docling/PaddleOCR + an LLM for documents, statsforecast for cash forecasts.
- Because the application is sold to customers, sanctions screening built on OpenSanctions is not free: budget a commercial/API licence.
- AGPL (Jube) and GPL (Neo4j Community) are usable as separate services, but need a licence review before embedding in a proprietary SaaS.
- Tazama's Apache licence and BCEAO link make it the most interesting open transaction-monitoring option for the UEMOA zone, but it is infrastructure built for payment-system operators (many microservices), likely heavy for a small team.

### Gaps
- Exact licence of Marble (LICENSE file not readable in the fetch) and primary-source confirmation of Jube's AGPLv3.
- All [M] licences and "maturity" (stars, release cadence) were not re-checked on GitHub this session.
- Current OpenSanctions prices (bulk and per-API-call).

## 2. Cloud and API services: what they do, published pricing or free tiers, regions

### Takeaway
Amazon Fraud Detector is closed to new customers since 7 November 2025. Most specialised vendors (Smile ID, Youverify, Trustpair, Sis ID, Bridge, Powens, Feedzai, Unit21, Sift, ComplyAdvantage) do not publish prices; only document-AI clouds, Sumsub (per third parties) and Stripe Radar show public figures, and several of those could not be read on the official page this session.

### Cited Findings

**Fraud / risk platforms**
- Amazon Fraud Detector: AWS "made the decision to no longer accept new customers as of November 7th, 2025"; existing customers continue as normal; AWS points to SageMaker AI, AutoGluon and AWS WAF Fraud Control (the WAF option is managed rules, not ML). No end-of-support date found. [V] — [AWS availability change](https://docs.aws.amazon.com/frauddetector/latest/ug/frauddetector-availability-change.html)
- Stripe Radar: the official pricing page fetched this session returned only plan-style figures ("Radar Standard from $10/month, Plus from $14/month, Pro from $20/month", plus a "pay as you go" option) and no per-transaction rate. This conflicts with the long-standing model I know of (about USD 0.05 per screened transaction, waived on standard Stripe pricing; Radar for Fraud Teams about USD 0.07, or 0.02 on standard pricing) [M]. Treat Radar pricing as unverified. Radar only screens payments processed by Stripe (card payments), not supplier bank transfers. — [Stripe Radar pricing](https://stripe.com/radar/pricing)
- Sift, Feedzai, Unit21: enterprise fraud/AML platforms, quote-only pricing; aimed at larger volumes. [M] — [Sift](https://sift.com), [Feedzai](https://www.feedzai.com), [Unit21](https://www.unit21.ai)
- Google Cloud AML AI: risk-scoring product for banks' AML transaction monitoring, designed for large retail/commercial banks. [M] — [Google Cloud AML AI](https://cloud.google.com/anti-money-laundering-ai)

**KYC / KYB / AML screening**
- Sumsub: third-party trackers (snapshot May 2026) list USD 1.35 per verification (Basic, USD 149/month minimum) and USD 1.85 (Compliance, USD 299/month minimum), Enterprise on quote; ongoing AML monitoring reported at USD 0.08 per check. [V-3P] — [CostBench Sumsub](https://www.costbench.com/software/kyc-aml/sumsub/)
- Veriff: sources conflict. A competitor's guide lists USD 0.80 (Essential) and USD 1.39 (Plus) per verification, USD 1.44 with PEP/sanctions; an aggregator lists 49/99/209 "per verification", which look like monthly plan fees mislabelled. [V-3P, conflicting] — [Didit guide (competitor)](https://didit.me/blog/sumsub-vs-veriff-vs-didit-the-ultimate-kyc-solution-showdown/); contradicted by [CostBench Veriff](https://www.costbench.com/software/kyc-aml/veriff/)
- Smile ID (Africa): pricing page shows no per-check rates. A secondary blog estimates USD 0.10-0.30 per document check, USD 0.30-1.00 for biometric KYC, AML screening from USD 0.05. Vendor claims links to 20+ African government databases in 7 countries; a market report says it supports KYC/AML across all 54 African countries. [V for absence of prices; V-3P for estimates] — [Smile ID pricing](https://usesmileid.com/pricing), [HelloDuty estimate](https://helloduty.com/blogs/what-is-smile-identity-and-how-its-revolutionizing-business-practices), [African RegTech 2026](https://allbusiness.africa/insights/african-regtech-2026)
- Youverify (Africa): no published prices found. Coverage figures disagree: Youverify says "over 40 countries"; CB Insights reports business verification in 48 countries and individual verification in 46; Smile ID's (competitor) page says government-database checks in 4 countries. [V, conflicting vendor claims] — [Youverify blog](https://youverify.co/en/blogs/youverify-vs-smileid-identity-verification-comparison), [CB Insights](https://www.cbinsights.com/company/youverify-1), [Smile ID comparison](https://usesmileid.com/why-smile-id/smile-id-vs-youverify-product-review)
- ComplyAdvantage (sanctions/PEP/adverse media, transaction monitoring), Onfido (now part of Entrust): quote-based. [M] — [ComplyAdvantage](https://complyadvantage.com), [Entrust identity verification](https://www.entrust.com)

**Supplier / IBAN verification and Verification of Payee**
- Trustpair: quote-only; vendor-stated account-validation coverage varies by country (France 95%, Poland 97%, United States 80%); a Dec 2025 press release claims verification coverage in 190+ countries. [V, vendor claims] — [Trustpair IBAN validation](https://trustpair.com/iban-validation/), [Business Wire](https://www.businesswire.com/news/home/20251209947330/en/)
- Sis ID: no standalone prices; checks that the bank account belongs to the declared beneficiary (ownership, not just IBAN format); integration claims IBAN validation for legal entities in 200+ countries. [V, vendor claims] — [Sis ID](https://sis-id.com/en/partenaires-supplhi/)
- SEPA Verification of Payee (VoP): euro-area PSPs had to offer it from 9 October 2025; PSPs in non-euro EU states from 9 July 2027. [V] — [PwC Legal](https://legal.pwc.de/en/news/articles/verification-of-payee-requirements-vop-under-the-eus-instant-payments-regulation-ipr), [ECB Instant Payments Regulation page](https://www.ecb.europa.eu/paym/retail/instant_payments/html/instant_payments_regulation.so.html)
- The EPC VoP scheme rulebook took effect 5 October 2025; scheme adherence is voluntary, the legal obligation is not; EPC expects more than 3,000 PSPs by July 2027. [V] — [The Paypers](https://thepaypers.com/regulations/news/epcs-verification-of-payee-scheme-rulebook-enters-into-effect)
- VoP is delivered by the payer's PSP (bank), free to the payer under the Instant Payments Regulation (EU) 2024/886 [M]; an application reaches it through its bank / banking-as-a-service provider (example of provider documentation: Modulr). — [Modulr VoP docs](https://modulr.readme.io/docs/eu-verification-of-payee-vop)

**Document extraction**
- Azure AI Document Intelligence: free F0 tier of 500 pages/month [V]. The page showed "$-" placeholders instead of prices in the fetch. From memory: Read about USD 1.50 per 1,000 pages, prebuilt models (invoice, receipt, layout, ID) about USD 10 per 1,000, custom extraction about USD 30 per 1,000 [M]. — [Azure pricing](https://azure.microsoft.com/en-us/pricing/details/ai-document-intelligence/)
- Google Document AI: Enterprise Document OCR USD 1.50 per 1,000 pages (up to 5M pages/month), USD 0.60 above; Form Parser and Custom Extractor USD 30 per 1,000 pages (USD 20 above 1M); Layout Parser USD 10 per 1,000. Invoice parser: sources conflict (USD 10 per 1,000 pages vs USD 0.10 per document of up to 10 pages). The official page could not be parsed directly; figures come from search snippets and third-party guides. [V-3P] — [Google Document AI pricing](https://cloud.google.com/document-ai/pricing), [third-party guide](https://invoicedataextraction.com/blog/google-document-ai-invoice-parser-pricing)
- Mindee (French vendor, invoice/receipt APIs): pricing not checked. — [Mindee](https://www.mindee.com/pricing)

**Open banking aggregators**
- Bridge and Powens (France): no published prices. Powens SAS is a payment institution registered with the ACPR. A tracker reports coverage of 62 countries for Bridge vs 44 for Powens (approximate). Main players in France: Powens, Bridge, Tink (Visa), TrueLayer, Fintecture. [V-3P] — [Open Banking Tracker comparison](https://openbankingtracker.com/api-aggregators/bridgeapi-io/vs/powens), [Powens tracker page](https://www.openbankingtracker.com/powens)
- Plaid (North America, UK, parts of EU), Tink (Europe, owned by Visa), Mono (Nigeria and a few anglophone African markets), Stitch (South Africa). [M] — [Plaid](https://plaid.com), [Tink](https://tink.com), [Mono](https://mono.co), [Stitch](https://stitch.money)

### Inferences
- No evidence was found of an open-banking aggregator covering banks in French-speaking Africa (UEMOA/CEMAC); expect file imports (bank statements, mobile-money exports) and direct mobile-money operator APIs instead. This is an inference from the coverage lists, not a verified statement.
- For a small team the only fraud services with entry prices near zero are those bundled with a payment processor (Stripe Radar) and the bank-side VoP; standalone fraud platforms are sales-led and sized for higher volumes.
- KYC cost order of magnitude: roughly USD 1-2 per verified person in Europe-style flows, possibly below USD 1 in Africa (third-party estimates only).

### Gaps
- Official prices not confirmed: Stripe Radar per-transaction, Azure DI, Google Document AI invoice parser, Mindee, Sumsub/Veriff (vendor pages), Google AML AI, ComplyAdvantage, Sift, Feedzai, Unit21, Onfido/Entrust, all open-banking aggregators.
- No reliable source on which KYC or open-banking vendors cover specific French-speaking African countries (Senegal, Côte d'Ivoire, Cameroon, Benin...) and with which ID documents.
- Whether VoP dates for non-bank PSPs (payment and e-money institutions) differ (the ECB table gives 9 April 2027 for euro-area PIs/EMIs under instant-payment obligations); to check in Regulation (EU) 2024/886.

## 3. Using LLMs (Claude, GPT, Gemini, Mistral, open-weight models) in finance features

### Takeaway
LLMs fit extraction, classification, explanation and assistant tasks; numbers must come from deterministic code (SQL/tools) and from schema-constrained outputs, never from free-text generation. At late-2026 list prices, extraction of one invoice costs from a fraction of a cent (small model) to about one cent (mid-tier model).

### Cited Findings
- Claude API list prices (reference cached 2026-11-03, per million tokens, input/output): Haiku 5.5 USD 0.10 / 0.50 (prompts up to 100K tokens); Sonnet 5.5 USD 2 / 10; Opus 5.5 USD 4 / 20; Fable 5.2 USD 8 / 40. — [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing) (figures from the Claude API reference bundled with this environment, not re-fetched from the web page)
- Message Batches run asynchronously at 50% of the cost; prompt caching bills cached prefix reads at a fraction of the input price (e.g. USD 0.10-0.20 per million on Sonnet 5.5 / Opus 5.5). — same reference, [Anthropic docs](https://platform.claude.com/docs/en/build-with-claude/batch-processing)
- Structured outputs constrain the response to a JSON schema (`output_config.format`), and `strict: true` on a tool guarantees schema-valid tool arguments. — [Anthropic structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
- PDFs can be sent directly (limits: 32 MB per request, 600 pages); a citations feature returns the cited text and page location for each claim, but cannot be combined with schema-constrained output in the same request. — [Anthropic PDF support](https://platform.claude.com/docs/en/build-with-claude/pdf-support), [Citations](https://platform.claude.com/docs/en/build-with-claude/citations)
- Data-residency / confidentiality controls on the Claude API: an `inference_geo` request parameter, zero-data-retention arrangements (not available for every model: Fable 5.2 requires 30-day retention), and availability through AWS Bedrock, Google Vertex AI and Microsoft Foundry under those clouds' terms. — [Anthropic docs](https://platform.claude.com/docs/en/build-with-claude/data-residency)
- OWASP Top 10 for LLM Applications (2025) lists prompt injection, sensitive information disclosure, excessive agency and misinformation among the top risks — directly relevant when an assistant reads supplier documents or emails. [M] — [OWASP GenAI](https://genai.owasp.org/llm-top-10/)
- NIST AI 600-1 (Generative AI Profile of the AI RMF, July 2024) lists confabulation, data privacy and information integrity among GenAI risks. [M] — [NIST AI 600-1](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)
- Mistral (French company, EU hosting) sells an OCR/document API; a third-party comparison of "Mistral OCR 4" against document-parsing APIs exists. [V-3P, not read in detail] — [Eden AI comparison](https://www.edenai.co/post/mistral-ocr-4-vs-top-document-parsing-apis-features-benchmarks-and-integration-guide)

### Inferences
- Cost order of magnitude (my arithmetic from the list prices above, assuming about 3,000 input tokens and 500 output tokens per invoice): Haiku 5.5 about USD 0.0006 per invoice; Sonnet 5.5 about USD 0.011; half of that through the Batch API. 10,000 invoices/month is therefore about USD 6 to USD 110, below the USD 100 that cloud prebuilt invoice models would cost at about USD 10 per 1,000 pages, and the LLM also handles unusual layouts. Image-heavy PDFs use more tokens; measure on real documents.
- Guardrails against wrong numbers: (1) schema-constrained extraction; (2) arithmetic checks in code (lines sum to total, VAT = base x rate, IBAN checksum, dates); (3) show the source snippet/page next to each extracted field; (4) confidence or disagreement routing to human review; (5) assistants answer questions through tool calls to read-only SQL/aggregations and quote the returned figures; (6) no payment or master-data change executed by the model without human approval; (7) treat document text as untrusted data (prompt injection); (8) a regression test set of real documents re-run at each prompt/model change.
- Self-hosting open-weight models (Mistral, Llama, Qwen class) gives full data control but needs a GPU server (several hundred EUR/month and up) and operations skills; at small volume an API with an EU region, a data-processing agreement and no-training terms is cheaper. Self-hosting becomes rational with strict residency requirements or high volume.

### Gaps
- Current prices of OpenAI, Google Gemini and Mistral models were not checked this session; no independent benchmark of invoice-extraction accuracy by model was retrieved.
- Latency/quality of API access from West and Central Africa, and whether local data-protection authorities require authorisation for transfers to EU/US LLM providers (see section 4).

## 4. Governance and compliance principles

### Takeaway
The EU high-risk AI obligations were postponed by the "AI Omnibus": Annex III systems (which include creditworthiness scoring of natural persons) now apply from 2 December 2027. GDPR, DORA (in force), the AML package (10 July 2027) and PSD3/PSR (texts agreed, formal adoption not confirmed) frame the rest; fraud detection itself is not classed high-risk, but automated decisions about people still fall under GDPR Article 22.

### Cited Findings

**EU AI Act**
- Regulation (EU) 2026/1744 ("AI Omnibus") was published in the Official Journal on 24 July 2026 and entered into force on 27 July 2026. [V] — [K&L Gates via Mondaq](https://www.mondaq.com/uk/new-technology/1825722/eu-digital-omnibus-on-ai-enters-into-force)
- New application dates: stand-alone high-risk systems (Annex III) from 2 December 2027 (was 2 August 2026); high-risk systems embedded in products (Annex I) from 2 August 2028 (was 2 August 2027). [V] — [Loyens & Loeff](https://www.loyensloeff.com/insights/news--events/news/eu-ai-act-key-amendments-adopted-under-digital-omnibus-package/), [Addleshaw Goddard](https://www.addleshawgoddard.com/en/insights/insights-briefings/2026/technology/eu-ai-act-ai-omnibus-formally-adopted/)
- Machine-readable marking of AI-generated content for certain systems moved to 2 December 2026; general-purpose AI model obligations (since 2 August 2025) unchanged. [V] — [Proskauer](https://www.proskauer.com/pub/eu-ai-act-update-provisional-deal-would-delay-high-risk-ai-rules)
- Already applicable since 2 February 2025: prohibited practices and the AI-literacy duty (Article 4). Annex III point 5(b) classes as high-risk AI used to evaluate the creditworthiness or credit score of natural persons, "with the exception of AI systems used for the purpose of detecting financial fraud". Chatbots must disclose they are AI (Article 50). [M] — [Regulation (EU) 2024/1689](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)

**GDPR**
- Article 22: right not to be subject to a decision based solely on automated processing with legal or similarly significant effect; Article 35: DPIA required for high-risk processing such as systematic profiling/scoring. In SCHUFA (C-634/21, 7 Dec 2023) the CJEU held that producing a credit score that a third party relies on heavily is itself an automated decision. [M] — [GDPR](https://eur-lex.europa.eu/eli/reg/2016/679/oj), [CJEU C-634/21](https://curia.europa.eu/juris/liste.jsf?num=C-634/21)

**DORA**
- Regulation (EU) 2022/2554 applies since 17 January 2025 to financial entities and, through contracts, to their ICT third-party providers (incident reporting, ICT risk management, register of providers, exit plans). A software vendor selling to banks/payment institutions meets it through contract clauses. [M] — [DORA](https://eur-lex.europa.eu/eli/reg/2022/2554/oj)

**PSD2 / PSD3 / PSR**
- Provisional political agreement 27 November 2025; COREPER endorsed the texts on 22 April 2026, published 23 April 2026; Official Journal publication was expected in the second half of 2026. No source found confirming final plenary adoption or publication as of this check. [V] — [William Fry](https://www.williamfry.com/knowledge/psr-psd3-eu-payment-services-legislation-is-agreed/), [Morrison Foerster](https://www.mofo.com/resources/insights/260430-psd3-and-the-payment-services-regulation-key-developments), [DLA Piper](https://www.dlapiper.com/en/insights/publications/2026/03/psd3-and-psr)
- Fraud provisions: PSPs that fail to implement adequate fraud-risk controls bear liability for customer losses; name/IBAN matching becomes mandatory. PSR applies 21 months after entry into force; payee-verification provisions (Articles 50 and 57) after 27 months; PSD3 transposed within 21 months. [V] — [PwC](https://www.pwc.com/cz/cs/blog/rizeni-rizik/psd-3-the-psr-payments-reform.html), [McCann FitzGerald](https://www.mccannfitzgerald.com/knowledge/financial-services-regulation/payment-services-directive-3-progress-on-updating-regulatory-regime)
- PSD2 strong customer authentication and transaction-risk-analysis rules remain the law in force until then. [M] — [PSD2](https://eur-lex.europa.eu/eli/dir/2015/2366/oj)

**AML package**
- AMLR (Regulation (EU) 2024/1624) applies directly from 10 July 2027; AMLD6 must be transposed by 10 July 2027 (some articles earlier: 10 July 2025 and 10 July 2026). [V] — [Deloitte](https://www.deloitte.com/global/en/services/consulting/perspectives/the-eu-aml-package.html), [HSF Kramer status 14 July 2026](https://www.hsfkramer.com/de/notes/fsrandcorpcrime/2026-posts/whats-done-whats-due-the-aml-countdown)
- AMLA selects directly supervised entities by 1 July 2027 (up to 40 expected); start of direct supervision is given as 1 January 2028 by some sources and "by July 2028" by another. [V, conflicting] — [Forvis Mazars](https://www.forvismazars.com/ch/en/insights/reports-studies-and-surveys/eu-aml-package-and-amlr); contradicted on date by [HSF Kramer](https://www.hsfkramer.com/de/notes/fsrandcorpcrime/2026-posts/whats-done-whats-due-the-aml-countdown)

**Frameworks and model risk**
- NIST AI RMF 1.0 (January 2023): four functions Govern, Map, Measure, Manage; voluntary and free. [M] — [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework)
- ISO/IEC 42001:2023: certifiable AI management system standard (paid standard). [M] — [ISO](https://www.iso.org/standard/42001)
- SR 11-7 (US Federal Reserve/OCC, 2011): model inventory, independent validation, ongoing monitoring, "effective challenge", documentation. Not binding in the EU but the reference vocabulary for model risk. [M] — [Federal Reserve SR 11-7](https://www.federalreserve.gov/supervisionreg/srletters/sr1107.htm)

**French-speaking Africa: data protection [M unless marked]**
- Senegal adopted a data-protection law in 2008 (authority: CDP); Côte d'Ivoire has a 2013 law, with protection handled inside the telecom regulator ARTCI rather than an independent authority; Benin's digital code is GDPR-inspired (authority: APDP); ECOWAS adopted a Supplementary Act in 2010 that served as the basis for several national laws. [V] — [OSIRIS overview](https://osiris.sn/Etat-des-lieux-des-legislations.html), [Leto guide](https://www.leto.legal/guides/rgpd-afrique)
- Other texts I know of, not verified this session: Senegal Law 2008-12; Côte d'Ivoire Law 2013-450; Benin Law 2017-20 (Code du numérique); Burkina Faso Law 001-2021 (CIL); Mali Law 2013-015; Togo Law 2019-014; Niger Law 2017-28; Cameroon Law 2024/017 of 23 December 2024; Morocco Law 09-08 (CNDP); Tunisia Organic Law 2004-63; African Union Malabo Convention in force since June 2023. Several of these laws require prior declaration or authorisation by the authority, including for transfers abroad. [M] — [AU Malabo Convention](https://au.int/en/treaties/african-union-convention-cyber-security-and-personal-data-protection)

### Inferences
- Design choice with large compliance effect: keep AI scoring on companies/suppliers and on transactions (fraud, anomaly) rather than on the creditworthiness of natural persons; the latter is Annex III high-risk from December 2027 and triggers Article 22 GDPR. Sole traders are natural persons — a grey area to raise with counsel.
- Minimum governance set a small team can actually run: model/prompt inventory with owner and version; data sheet per model; documented validation before release; logged inputs/outputs/model version for every score; human review of every adverse or blocking decision with a recorded reason; drift and alert-volume monitoring; periodic re-validation; DPIA for scoring/profiling features; AI-use notice to users. This maps to NIST AI RMF and SR 11-7 and prepares for ISO 42001 without paying for certification.
- The application vendor is normally not itself an AML "obliged entity"; its customers may be. Screening and monitoring features should therefore be presented as tools supporting the customer's obligations (legal qualification to confirm).

### Gaps
- Whether PSD3/PSR have been formally adopted and published since July 2026 (not confirmed).
- Exact AMLA direct-supervision start date (sources conflict).
- Whether SR 11-7 has been superseded or amended by US agencies in 2025-2026 (not checked).
- Up-to-date status of each French-speaking African data-protection law and authority (formalities, cross-border transfer rules, any AI-specific rules), and BCEAO/COBAC rules on outsourcing and cloud hosting for financial institutions: the search returned mostly old sources; Cameroon's 2024 law in particular is unverified.

## 5. Security-by-design principles and recognised standards

### Takeaway
The controls that stop most payment fraud in a finance application are procedural and cheap: strong authentication, least-privilege roles, dual approval for payments and for supplier bank-detail changes, payee verification, and tamper-evident logs. OWASP ASVS is the free build checklist; ISO 27001 and SOC 2 are the certifications buyers ask for; PCI DSS only bites if card data is handled.

### Cited Findings
- Marble's feature list illustrates what buyers expect of a compliance tool: role-based access control, SSO with OpenID Connect, IP whitelisting, SOC 2 Type II. [V] — [checkmarble/marble](https://github.com/checkmarble/marble)
- Verification of Payee (name/IBAN match before a credit transfer) has been mandatory for euro-area PSPs since 9 October 2025. [V] — [PwC Legal](https://legal.pwc.de/en/news/articles/verification-of-payee-requirements-vop-under-the-eus-instant-payments-regulation-ipr)
- OWASP ASVS 5.0 (released May 2025): free verification standard with chapters on authentication, session management, access control, cryptography, logging; three assurance levels. [M] — [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)
- NIST SP 800-63B-4 (2025) recognises phishing-resistant authenticators (passkeys/WebAuthn) for higher assurance levels. [M] — [NIST SP 800-63](https://pages.nist.gov/800-63-4/)
- ISO/IEC 27001:2022 (information-security management system, certifiable); SOC 2 (AICPA Trust Services Criteria attestation, Type II covers a period of operation). [M] — [ISO 27001](https://www.iso.org/standard/27001), [AICPA SOC 2](https://www.aicpa-cima.com/topic/audit-assurance/audit-and-assurance-greater-than-soc-2)
- PCI DSS v4.0.1 is the current version; its future-dated requirements became mandatory on 31 March 2025; scope is avoided by never touching card numbers (hosted fields / processor tokenisation). [M] — [PCI SSC](https://www.pcisecuritystandards.org/document_library/)

### Inferences
- Baseline control list for the application: passkeys or TOTP MFA for all users, step-up authentication for payments and bank-detail changes; role-based access with segregation of duties (the person who creates a supplier or changes an IBAN cannot approve the payment); dual approval above a threshold and on every first payment to a new or changed IBAN, with a cooling-off delay and out-of-band notification; append-only, hash-chained audit log (who, what, when, before/after values, model version and score for AI decisions) stored separately from the application database; encryption in transit (TLS 1.2+) and at rest, field-level encryption for IBANs and ID documents, managed keys (KMS); tenant isolation; anomaly alerts (new beneficiary, unusual amount/time, duplicate invoice, IBAN country mismatch, mass export); backups and tested restore; dependency and secret scanning; rate limiting.
- Sequence for a small budget: self-assess against OWASP ASVS Level 2 first (free), buy penetration testing once a year, pursue SOC 2 or ISO 27001 only when customers require it.

### Gaps
- No certification cost figures (ISO 27001, SOC 2, penetration tests) were retrieved this session.
- No source retrieved on security requirements specific to UEMOA/CEMAC regulators for software vendors.

## 6. Realistic phased build path and budget (buy vs build per feature)

### Takeaway
Everything in this section is my inference from the findings above; no source gives a budget for this exact case. The pattern: build rules, anomaly scoring, forecasting and LLM extraction in-house on open source; buy data and regulated checks (sanctions lists, identity verification, bank connectivity, payee verification).

### Cited Findings
- Building blocks for "build" are free and permissively licensed (section 1); OpenSanctions requires a paid licence for commercial use. — [OpenSanctions licensing](https://www.opensanctions.org/licensing/)
- Amazon Fraud Detector is not an option for new projects. — [AWS notice](https://docs.aws.amazon.com/frauddetector/latest/ug/frauddetector-availability-change.html)
- Entry price points seen: Azure Document Intelligence free 500 pages/month — [Azure](https://azure.microsoft.com/en-us/pricing/details/ai-document-intelligence/); Sumsub from about USD 149/month minimum (third party) — [CostBench](https://www.costbench.com/software/kyc-aml/sumsub/); TimeGPT USD 99/month for 10,000 calls — [Nixtla FAQ](https://docs.nixtla.io/docs/getting-started-faq); Claude Haiku 5.5 USD 0.10/0.50 per million tokens — [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing).
- High-risk AI Act obligations start 2 December 2027; AMLR 10 July 2027 — the roadmap has roughly a year before these apply. — [Loyens & Loeff](https://www.loyensloeff.com/insights/news--events/news/eu-ai-act-key-amendments-adopted-under-digital-omnibus-package/), [Deloitte](https://www.deloitte.com/global/en/services/consulting/perspectives/the-eu-aml-package.html)

### Inferences
Buy vs build, per feature:

| Feature | Recommendation | Why |
|---|---|---|
| Document extraction (invoices, receipts, statements) | Build on an LLM API with schema output + code checks; optional Docling/PaddleOCR pre-processing | Cents or less per document, handles varied layouts; cloud prebuilt models as fallback |
| Payment/supplier fraud rules | Build (plain code or GoRules Zen) | Rules are product-specific; no labels needed |
| Anomaly scoring | Build (PyOD / Isolation Forest, then LightGBM once labelled cases exist) + SHAP reasons | Needs the application's own data; supervised ML only after months of feedback |
| Supplier IBAN / payee verification | Buy: bank-side VoP in the euro area; Trustpair / Sis ID for larger customers | Requires bank data nobody can build |
| Sanctions / PEP screening | Buy data (OpenSanctions licence or API); matching can be self-hosted | Lists must be current and licensed |
| KYC / KYB identity verification | Buy (Sumsub, Veriff; Smile ID / Youverify in Africa) | Biometrics and government-database access |
| Transaction monitoring / case management | Start with own rules + review queue; evaluate Marble (open core) or Tazama if volume or regulation requires | Avoid heavy platforms early |
| Bank connectivity | Buy aggregator in EU (Bridge, Powens, Tink); file/mobile-money imports in French-speaking Africa | Licensed activity (AISP) in the EU |
| Cash-flow forecasting | Build (statsforecast/Prophet baselines); test TimeGPT only if baselines are insufficient | Free, explainable |
| Assistant / natural-language queries | Build on an LLM API with read-only tools | Guardrails matter more than model choice |
| Risk scoring of customers/suppliers | Build a transparent scorecard (rules + logistic regression/GBM + SHAP); avoid scoring natural persons' creditworthiness | Regulatory exposure |

Phases (assumed team of 2-4 developers):
1. Months 0-3 — foundation: MFA, roles, dual approval, audit log, encryption (section 5); LLM document extraction with human validation; deterministic rules (duplicate invoice, IBAN change, new beneficiary); event logging designed for later ML. Third-party spend: tens of EUR/month (LLM + hosting).
2. Months 3-6 — detection: unsupervised anomaly scores shown as alerts with reasons; review queue capturing analyst decisions as labels; sanctions screening; baseline cash forecasts; model inventory and DPIA.
3. Months 6-12 — learning and assistant: supervised model once enough labelled cases exist; drift monitoring (Evidently), model registry (MLflow); assistant with tool use; payee verification / KYC vendors integrated per market.
4. Months 12+ — scale and assurance: graph analysis across tenants' supplier data (where lawful), case-management platform if needed, SOC 2 / ISO 27001, ISO 42001 alignment, AI Act readiness before 2 December 2027.

Budget order of magnitude (assumption, excluding salaries): phase 1-2 under EUR 100-300/month in services; with KYC and sanctions vendors EUR 300-1,500/month depending on volumes and minimums; certifications and penetration tests are the first five-figure items. Salaries dominate everything.

### Gaps
- No independent source on real costs or timelines for comparable small-team projects; all figures here are assumptions to validate with vendor quotes.
- Minimum monthly commitments of KYC, sanctions and open-banking vendors (the real cost floor) are mostly unpublished.
