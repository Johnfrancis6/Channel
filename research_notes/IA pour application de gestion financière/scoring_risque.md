# AI-based risk scoring for a business financial management application

Research date: 2026-11-17. Method note: most findings below come from web search summaries and secondary pages (law firms, vendor pages, compliance blogs); primary texts (Official Journal, CJEU judgment, FATF/EBA PDFs, BIS PDF) could not be opened in this session. Each finding says what kind of source it rests on. Items marked "vendor claim" are not independently audited.

## 1. Which risk scores are useful in a financial management tool?

### Takeaway
The scores with a clear, documented precedent are: (a) company failure / insolvency score at 12 months (the product Altares, Ellisphere, Creditsafe and Banque de France already sell or publish), (b) invoice late-payment prediction on the tool's own receivables data, (c) credit scoring of persons/SMEs (lending use, heavily regulated), (d) AML customer risk rating (obliged entities only), and (e) the Altman Z-family as a transparent financial-health baseline. For a non-lender tool, (a), (b) and (e) are the natural starting set.

### Cited Findings
- Company failure scores, 12-month horizon, are the market standard: the Altares insolvency score estimates the probability that a French company enters insolvency proceedings within twelve months, is updated daily, and combines Paydex payment-behaviour data, expert segmentation and "statistical and AI algorithms" (vendor description) — [Altares](https://www.altares.com/en/our-data/altares-scores-ratings/)
- Creditsafe scorecards map a probability of default to a 1-100 score (A-D for the international score); each score is a band of probabilities, e.g. in the French summary a score of 30 corresponds to a PD between 3.03% and 3.11% (vendor documentation) — [Creditsafe scorecards](https://www.creditsafe.com/cs/en/about-us/about-creditsafe/company-scorecards.html); [Creditsafe FR executive summary](https://www.creditsafe.com/content/dam/it/csfr_executive_summary_b2b_v2.pdf)
- Ellisphere's failure score gives a 12-month probability of default in 10 risk segments (Score 1 to 10), each tied to an expected one-year failure rate; Ellisphere states it is not a credit rating under EU Regulation 1060/2009 — [Ellisphere user guide](https://ellisphere.com/uploads/pdf/ScoreEllipro_Ellisphere_Anglais.pdf); [Ellisphere explainer](https://www.ellisphere.com/en/score-de-defaillance-des-entreprises-dellisphere-comment-ca-marche/)
- Banque de France company rating ("cotation"): new scale (NEC) in place since 8 January 2022 with 22 notches instead of 13, plus additional financial indicators and ratios — [L'Info Durable](https://www.linfodurable.fr/investir-durable/en-bref/banque-de-france-introduit-echelle-cotation-des-entreprises-30331); performance is published yearly — [Banque de France, Évaluation des performances de la cotation 2025](https://www.banque-france.fr/system/files/2025-12/FR_Eval_performances_cotation_2025_VClean.pdf)
- The Banque de France rating is recognised by the Eurosystem as an in-house credit assessment system (ICAS), used to assess the quality of bank claims on non-financial companies for monetary policy; since 2012 the reference event is "default" in the Basel II sense, not only legal failure — [Banque de France code de conduite](https://www.banque-france.fr/system/files/2024-12/Code-conduite-activite-cotation.pdf)
- The 2026 Banque de France rating guide says the one-year default risk assessment now integrates an environmental dimension (no figures seen) — [Guide de référence de la cotation 2026](https://www.banque-france.fr/system/files/2026-09/Guide-Ref-cotation_2026.pdf)
- Altman Z-score: original 1968 model for listed manufacturers, five ratios, coefficients estimated by multiple discriminant analysis on 33 bankrupt and 33 non-bankrupt manufacturing firms. Private-firm Z' uses book equity with weights 0.717, 0.847, 3.107, 0.420, 0.998 (distress below 1.23; safe above 2.9, another source says 2.99). Non-manufacturing Z'' = 3.25 + 6.56·X1 + 3.26·X2 + 6.72·X3 + 1.05·X4 (safe above 2.6, distress below 1.1). Secondary sources, with disagreement on dates of Z'/Z'' (1983 vs 1995) — [MetricGate docs](https://metricgate.com/docs/altman-z-score/); [Beancount.io guide](https://beancount.io/blog/2026/05/18/altman-z-score-five-ratio-bankruptcy-prediction-model-small-business-financial-distress-screen-customers-suppliers-credit-guide)
- Invoice late-payment prediction is an established use case: a 2007 IBM study predicted on-time payment and size of delay using invoice-level features and five delinquency classes — [Zeng et al., KDD 2007](https://prem-melville.com/publications/equitant-kdd07.pdf); a bank-partnered prototype reported about 77% accuracy (abstract; 81% in another summary of the same work) — [arXiv 1912.10828](https://arxiv.org/pdf/1912.10828v1.pdf); an MIT thesis on Fortune 500 invoice data found cost-sensitive learning improved results on imbalanced data — [MIT DSpace](https://dspace.mit.edu/handle/1721.1/104327)
- AML customer risk rating: FATF expects a methodology that builds a customer risk profile from customer, product and delivery-channel factors and updates it through monitoring; country risk is a recognised input (secondary summaries of FATF's 2014 banking RBA guidance) — [Comsure](https://comsuregroup.com/news/comsure-view-customer-risk-assessments-cras-as-articulated-by-the-wolfsberg-group-and-fatf); [Wolfsberg country risk FAQ](https://wolfsberg-group.org/resources/rba/155)

### Inferences
- A financial management tool sits on exactly the data the invoice-payment studies use (invoice amount, terms, customer payment history), so late-payment prediction is the score it can build itself; the failure score is better bought (Altares/Ellisphere/Creditsafe/Banque de France) than rebuilt, because it needs national insolvency and filing data.
- Supplier risk in practice is the same failure score applied to the purchase side plus dependency concentration; no separate methodology was found.
- A score shown about a company (legal person) is outside GDPR Article 22 and AI Act Annex III 5(b), which concern natural persons; sole traders are natural persons, so the line is not clean in an SME tool.

### Gaps
- No source found in this session on liquidity-risk or portfolio-risk scores inside SME tools, on transaction risk scores (fraud scoring), or on a dedicated supplier/third-party risk methodology.
- Published default rates per notch of the Banque de France scale were not extracted (the 2025 performance report exists and should be read directly).
- The 1-100 scale often attributed to the Altares/D&B failure score was not confirmed on Altares's own pages.

## 2. Which models and data are used, and what performance gains are measured?

### Takeaway
Logistic-regression scorecards remain the commercial default (Creditsafe states it outright); tree ensembles (random forest, gradient boosting) are the consistent winners in benchmarks and are in production at Ellisphere. Alternative data helps most where history is thin; where a lender already has rich transaction data, the extra lift is modest.

### Cited Findings
- Creditsafe: stepwise logistic regression is "the preferred methodology within Creditsafe" — [Creditsafe scorecard guide](https://www.creditsafe.com/content/dam/uk/pdfs/corporate/creditsafe-scorecard-guide-2019.pdf)
- Ellisphere: published model uses a Random Forest; company reports a Gini index of 80% (vendor claim) — [Ellisphere](https://www.ellisphere.com/en/score-de-defaillance-des-entreprises-dellisphere-comment-ca-marche/)
- Lessmann, Baesens, Seow, Thomas (EJOR 2015, 247(1), 124-136): benchmark of 41 classifiers on eight real credit-scoring data sets; ensemble selection and stacking ranked best on AUC, partial AUC and H-measure, closely followed by random forest and stochastic gradient boosting; authors recommend random forest as the benchmark for new models (secondary summaries of the paper) — [paper PDF, Edinburgh CRC](https://crc.business-school.ed.ac.uk/sites/crc/files/2023-10/Benchmarking-State-of-the-Art-Classification-Algorithms-for-Credit-Scoring-Lessmann-Seow-Baesens-and-Thomas.pdf); [summary chapter](https://mikenguyen13.github.io/credit_score/chapters/16-benchmarking.html)
- BIS Working Paper 834 (Gambacorta, Huang, Qiu, Wang, Dec 2019): on a Chinese fintech's data (May-Sept 2017), the ML model with non-traditional data predicted losses and defaults better than traditional models under a negative credit-supply shock; the advantage shrinks for borrowers with longer credit histories — [BIS WP 834](https://www.bis.org/publ/work834.htm)
- Banque de France Working Paper 809 (Fraisse and Laporte): pseudo-internal models of corporate default with neural networks, random forest, gradient boosting and ridge on data from the largest French banks; the result is framed in capital requirements, and gradient boosting leads to a capital charge higher than regulators expect when no model is in place — [Banque de France WP 809](https://www.banque-france.fr/en/publications-and-statistics/publications/return-investment-ai-case-capital-requirement)
- Open banking data: a Norwegian bank study (JRFM 2022) found models on open-banking data alone "surprisingly effective" and an ensemble with traditional data better than the conventional model for new customers — [IDEAS/RePEc](https://ideas.repec.org/a/gam/jjrfmx/v15y2022i12p597-d1000763.html)
- A Revolut study on Spain and France (Edinburgh Credit Research Centre conference, 2025) found only a modest AUC increase from open-banking data, because internal transaction data already carried similar information — [CRC paper](https://crc.business-school.ed.ac.uk/sites/crc/files/2025-11/Evaluating-the-Contribution-of-Open-Banking-Data-to-Credit-Scoring-Performance-in-the-Spanish-and-French-Markets-paper.pdf)
- Vendor case study (Monet/Belvo): AUC 73%, KS 34% on a test sample with open-finance data only — [Belvo case study](https://go.belvo.com/hubfs/Monet-technical-case-study-ENG.pdf). Vendor claim (Enable Banking): up to 30% lower portfolio credit risk for one client — [Enable Banking](https://enablebanking.com/success-stories/uc)
- Smartphone data: Tala states it uses Android device data and behavioural data; third parties cite about 250 data points and daily uploads (possibly dated) — [Tala data ethics](https://tala.co/data-ethics/); [Penser](https://www.penser.co.uk/article/credit-scoring-the-unbanked-alternative-solutions-used-in-global-markets/). Branch is described as using handset details, SMS logs, GPS, repayment history and contact lists — [Brankas](https://blog.brankas.com/credit-scoring-innovations)
- Cash-flow data: Kabbage combined traditional credit scores with real-time business data from accounting software, payment processors and bank accounts, and licensed its platform to ING and Santander — [HousingWire](https://www.housingwire.com/articles/41928-harnessing-the-power-of-alternative-data/); independent research on cash-flow underwriting — [FinRegLab](https://finreglab.org/research/the-use-of-alternative-data-in-underwriting-credit/)
- World Bank overview of alternative data in credit risk assessment (opportunities and risks) — [World Bank](https://documents1.worldbank.org/curated/en/099031325132018527/pdf/P179614-3e01b947-cbae-41e4-85dd-2905b6187932.pdf)
- ML vs Altman: studies report ML improving on the Z-score as a benchmark, while accounting-based models remain widely used; no AUC table was retrieved — [Samajova et al. 2025](https://ems.uniza.sk/pdf/2025_2/EMS_2_2025_05_Samajova_etal.pdf); vendor blog claims large gains (treat with caution) — [DistressSignal](https://distresssignal.vercel.app/blog/altman-z-score-vs-machine-learning/)

### Inferences
- Evidence pattern: the gain from ML and from new data is largest for thin-file borrowers and under stress, smallest where long histories exist (BIS 834, Revolut study). A small team should expect the data, not the algorithm, to drive most of the gain.
- Logistic scorecard first, gradient boosting as challenger, is consistent with both the benchmark literature and regulator expectations on explainability (section 4).

### Gaps
- Exact AUC/Gini numbers from BIS WP 834 and from Lessmann et al. (logistic vs random forest) were not retrieved: the pages opened gave only qualitative conclusions. Do not quote figures for these without reading the PDFs.
- No Bank of England study was found in this session; no study on deep learning for tabular credit data; nothing on telecom-only, mobile-money-only or e-invoicing-based scoring with measured AUC.

## 3. How are scores validated and monitored?

### Takeaway
Standard practice is three checks (discrimination, calibration, stability) plus back-testing by grade; PSI thresholds 0.10/0.25 are heuristics from Lewis (1994) that break down on small portfolios. This session found sources for stability and for published back-testing practice, but not for reject inference or fairness testing.

### Cited Findings
- PSI thresholds 0.10 and 0.25 trace to Lewis (1994); in small portfolios a single borrower moving can push PSI past the thresholds — [arXiv 2307.11878](https://arxiv.org/pdf/2307.11878v4)
- Common reading of PSI: below 0.1 no significant shift, 0.1-0.25 investigate, above 0.25 significant shift / consider retraining — [MathWorks](https://www.mathworks.com/help/risk/risk.validation.populationstabilityindex.html); thresholds should be tuned, they are heuristics — [Arize](https://arize.com/glossary/population-stability-index-psi/)
- One practitioner guide suggests holding out at least 30% of data for validation and keeping validation KS within 0.05 of training KS (single non-authoritative source) — [ScoreCardModel best practices](https://scorecardmodel.readthedocs.io/en/latest/best_practices/)
- Discrimination metrics used in benchmarks: AUC, partial AUC, H-measure — [Lessmann et al.](https://crc.business-school.ed.ac.uk/sites/crc/files/2023-10/Benchmarking-State-of-the-Art-Classification-Algorithms-for-Credit-Scoring-Lessmann-Seow-Baesens-and-Thomas.pdf); vendors report Gini and KS — [Ellisphere](https://www.ellisphere.com/en/score-de-defaillance-des-entreprises-dellisphere-comment-ca-marche/); [Belvo](https://go.belvo.com/hubfs/Monet-technical-case-study-ENG.pdf)
- Back-testing example: Banque de France publishes a yearly performance evaluation of its rating, including default rates observed per rating over one- and two-year horizons (2025 report on 2024 data mentions a two-year default rate computed on 2022 and 2023) — [Banque de France 2025](https://www.banque-france.fr/system/files/2025-12/FR_Eval_performances_cotation_2025_VClean.pdf)
- Calibration by band: Creditsafe publishes the PD band attached to each score value — [Creditsafe FR](https://www.creditsafe.com/content/dam/it/csfr_executive_summary_b2b_v2.pdf)
- Fairness evidence from one regulator-reported case: the CFPB's 2019 update on Upstart reported no disparities requiring further fair-lending analysis for minority, female or 62+ applicants (data supplied by Upstart) — [Regulatory Report](https://www.regreport.info/2019/08/06/bureau-asserts-use-of-alternative-data-by-one-firm-reaped-benefits-of-more-applicants-lower-interest-rates)
- Amended AI Act: new Article 4a gives a broader legal basis for processing special-category data to detect and correct bias (previously only Article 10(5)) (secondary source) — [euaiact.com](https://www.euaiact.com/digital-omnibus-ai)

### Inferences
- For a small tool, the Banque de France pattern (publish observed default/late rates per score band every year) is the simplest honest validation to copy.
- With few defaults, PSI and KS are noisy; monitoring should use wide bands and longer windows.

### Gaps
- No source retrieved on reject inference methods, on calibration tests (Hosmer-Lemeshow, binomial tests), or on fairness metrics (disparate impact ratio, equal opportunity). These are standard topics but unsourced here.
- Basel/IFRS 9 model validation texts (ECB guide to internal models, EBA PD/LGD guidelines, IFRS 9 expected credit loss) were not researched in this session.

## 4. What do regulations require?

### Takeaway
In the EU, AI credit scoring of natural persons stays high-risk under the AI Act, but the obligations were postponed by the Digital Omnibus (Regulation (EU) 2026/1744, in force 27 July 2026) from 2 August 2026 to 2 December 2027; GDPR Article 22 already applies now, and since SCHUFA (7 December 2023) the score itself can be the "automated decision". Scores about companies fall outside both. In WAEMU, credit information goes through BCEAO-supervised credit bureaus (BIC) under a uniform law.

### Cited Findings
- EU AI Act, postponement: amending Regulation (EU) 2026/1744, published in the Official Journal 24 July 2026, in force 27 July 2026; Annex III stand-alone high-risk obligations (including creditworthiness assessment and life/health insurance risk pricing) move from 2 August 2026 to 2 December 2027; Annex I product-embedded systems move from 2 August 2027 to 2 August 2028 (secondary sources, consistent with each other) — [euaiact.com](https://www.euaiact.com/digital-omnibus-ai); [Cloud Security Alliance note](https://labs.cloudsecurityalliance.org/research/csa-research-note-eu-ai-act-omnibus-vii-deadline-delay-20260/); [Usercentrics](https://usercentrics.com/knowledge-hub/eu-ai-act-high-risk-delay-article-50-transparency-consent/)
- Adoption dates conflict between sources: Parliament 16 June 2026 and Council 29 June 2026 in one, 8 July 2026 in another — [aiacto.eu](https://www.aiacto.eu/en/blog/digital-omnibus-ai-act-report-2027); [GlobalSuite](https://www.globalsuitesolutions.com/digital-omnibus-ai-regulation-2026-1744/)
- Not postponed: Article 50 transparency obligations stay at 2 August 2026; two new Article 5 prohibitions and a marking deadline for pre-existing generative systems apply 2 December 2026 — [euaiact.com](https://www.euaiact.com/digital-omnibus-ai); [Praxikon](https://www.praxikon.com/en/posts/digital-omnibus-high-risk-postponement-december-2027)
- Other Omnibus changes: Article 4 AI literacy softened from "shall ensure a sufficient level" to "shall take measures to support"; small mid-caps get the SME penalty treatment of Article 99(6) — [euaiact.com](https://www.euaiact.com/digital-omnibus-ai)
- GDPR Article 22 / SCHUFA: CJEU, 7 December 2023, C-634/21 (OQ v Land Hessen): a credit reference agency's calculation of a score is itself an automated decision under Article 22 when a third party "draws strongly" on it to establish, implement or terminate a contract; the "merely preparatory" argument was rejected; such decisions are prohibited unless an Article 22(2) exception applies. Companion ruling the same day (C-26/22 and C-64/22) on retention of insolvency data — [A&O Shearman](https://www.aoshearman.com/en/insights/ao-shearman-on-data/cjeu-rules-that-a-credit-score-constitutes-automated-decision-making-under-the-gdpr); [noyb](https://noyb.eu/en/cjeu-landmark-rulings-credit-ranking-and-review-dpas); [Bird & Bird](https://twobirds.com/en/insights/2023/global/key-takeaways-from-the-schufa-case-of-the-cjeu)
- Commentators caution against reading SCHUFA as covering every risk-scoring process; the test is the determining role of the score — [IAPP](https://iapp.org/news/a/key-takeaways-from-the-cjeus-recent-automated-decision-making-rulings)
- EBA Guidelines on loan origination and monitoring (EBA/GL/2020/06, applied from 30 June 2021): section 4.3.3 on technology-enabled innovation (para. 53) and models for creditworthiness assessment and credit decisions (paras. 54-55); models must be explainable and interpretable, with governance and model-risk management proportionate to the facility and borrower type (secondary summaries) — [EBA](https://www.eba.europa.eu/eba-seeks-future-proof-loan-origination-standards-taking-consideration-significant-transition); [McCann FitzGerald](https://mccannfitzgerald.com/knowledge/financial-services-regulation/eba-guidelines-on-loan-origination-and-monitoring); [Management Solutions](https://www.managementsolutions.com/en/node/1886)
- AML: FATF Recommendation 1 is the core risk-based obligation (2012 revision, updated since) — [Fluxforce](https://www.fluxforce.ai/regulations/fatf-recommendation-1-risk-based-approach); EBA ML/TF risk factors guidelines (2017, revised 1 March 2021, extended to crypto-asset providers January 2024) set factors for assessing each business relationship and say firms should not reject whole customer categories — [EBA guidelines PDF](https://www.eba.europa.eu/sites/default/documents/files/documents/10180/1890686/66ec16d9-0c02-428b-a294-ad1e3d659e70/Final%20Guidelines%20on%20Risk%20Factors%20%28JC%202017%2037%29.pdf); [Ecovis](https://ecovis.lt/?p=4547)
- EU AML Regulation (EU) 2024/1624 applies from 10 July 2027 and replaces Directive 2015/849 on that date; technical standards still in development in 2026 — [Forvis Mazars](https://www.forvismazars.com/lu/fr/insights/nos-publications/articles/amlr-2027); [Persona](https://withpersona.com/blog/what-is-amlr)
- US ECOA / Regulation B: CFPB Circular 2023-03 (September 2023): creditors using AI or complex models must give specific and accurate reasons for adverse action; reasons must "relate to and accurately describe the factors actually considered or scored"; the sample-form checklist cannot be used when it does not reflect the real reasons; no exemption for "black box" models — [CFPB press release](https://www.consumerfinance.gov/archive/newsroom/cfpb-issues-guidance-on-credit-denials-by-lenders-using-artificial-intelligence/); [Cooley](https://www.cooley.com/news/insight/2023/2023-09-25-cfpb-mandates-additional-specificity-in-adverse-action-communications-based-on-ai-or-complex-credit-models)
- WAEMU: credit bureaus (Bureaux d'Information sur le Crédit, BIC) are governed by a uniform law transposed in member states; BCEAO supervises, with the Banking Commission if needed; banks and microfinance institutions (SFD) transmit client credit data; Creditinfo West Africa (Creditinfo VoLo) is the approved operator (dates differ: approval 12 May 2015, operating since February 2016) — [BCEAO, promotion des BIC](https://www.bceao.int/fr/content/promotion-des-bureaux-dinformation-sur-le-credit-dans-lumoa); [BCEAO note d'information](https://edenpub.bceao.int/sites/default/files/2017-12/note_information_n4_strategie_inclusions_financiere_uemoa_1_.pdf); [BCEAO instruction 005-05-2015](https://www.bceao.int/sites/default/files/2017-12/instruction_no_005-05-2015_fixant_les_modalites_de_transmission_des_informations_sur_le_credit_aux_bic_f%20%282%29.pdf)
- WAEMU borrower rights and scoring: on a disputed item the BIC must investigate and correct or delete inaccurate or unverifiable information; scoring criteria are set by the lender; BCEAO includes scoring training in its BIC promotion programme — [Creditinfo UMOA glossary](https://uemoa.creditinfo.com/wp-content/uploads/sites/63/2022/04/UMOA-Glossaire-de-termes-de-la-finance-Fevrier-2021.pdf); [BCEAO](https://www.bceao.int/fr/content/promotion-des-bureaux-dinformation-sur-le-credit-dans-lumoa)
- Ten-year review of the WAEMU BIC and non-financial company rating — [Droit Médias Finance](https://droitmediasfinance.com/index.php/actualites/droit-bancaire/1123-uemoa-bureau-dinformation-sur-le-credit-bilan-dune-decennie-de-transformation-et-perspectives-a-lere-du-digital)

### Inferences
- For an EU product in November 2026: GDPR Article 22 and SCHUFA bind today; AI Act high-risk duties for person-level credit scoring bind from 2 December 2027. A tool that scores only companies and only advises (human decides) is outside both, but sole traders pull it back in.
- Under SCHUFA, a software vendor that computes a person-level score its customers rely on heavily may itself carry Article 22 duties, not only the customer.
- In WAEMU, a tool that scores from its own invoice data is not a BIC; sharing credit data on third parties across clients would move it toward BIC territory (approval required).

### Gaps
- Not verified against the Official Journal: the text of Regulation (EU) 2026/1744 (the EUR-Lex page did not load), its exact adoption date, and whether it changed Annex III point 5(b) or the Article 6(3) derogations. All dates above rest on secondary commentary sites.
- Not researched: the list of high-risk provider/deployer obligations (Articles 9-15, 26, 27 fundamental-rights impact assessment), the SME fraud-detection carve-out in Annex III 5(b), Commission high-risk guidelines, CNIL and ACPR positions, Basel/IFRS 9 model requirements, CJEU C-203/22 (Dun & Bradstreet Austria, 2025) on the right to explanation, the EU Consumer Credit Directive 2023/2225.
- Current status of CFPB Circular 2023-03 in 2025-2026 (possible withdrawal of guidance documents) not verified; the press release is now under the CFPB "archive" path.
- WAEMU: the uniform law's text and consent rules were not read; personal-data laws of member states, the 2024 BCEAO instructions on payment services/fintech licensing, and CEMAC/COBAC rules were not researched.

## 5. Explainability and reason codes

### Takeaway
The firm requirement found is that reasons shown must be specific and reflect the factors the model really used (US), and that models must be explainable and interpretable (EBA). No source in this session prescribes a technique.

### Cited Findings
- Reasons must "relate to and accurately describe the factors actually considered or scored"; vague or generic reasons fail ECOA; commentators advise mapping each model factor to an adverse-action reason and checking specificity — [Cooley](https://www.cooley.com/news/insight/2023/2023-09-25-cfpb-mandates-additional-specificity-in-adverse-action-communications-based-on-ai-or-complex-credit-models); [Kilpatrick Townsend](https://ktslaw.com/en/Blog/Consumer-Financial-Services/2023/9/Creditors-Using-AI-Underwriting-Must-Provide-Specific-Reasons-for-Adverse-Action)
- Heightened scrutiny of non-traditional variables, since consumers may not expect them to affect decisions — [Skadden](https://www.skadden.com/insights/publications/2024/01/cfpb-applies-adverse-action-notification-requirement)
- EBA: model outputs in credit granting should be explainable and interpretable — [McCann FitzGerald](https://mccannfitzgerald.com/knowledge/financial-services-regulation/eba-guidelines-on-loan-origination-and-monitoring)
- A 2024 paper proposes ML/deep-learning credit scoring designed to stay compliant with regulatory constraints — [arXiv 2412.20225](https://arxiv.org/abs/2412.20225v1)

### Inferences
- A points-based scorecard gives reason codes for free (the attributes that lost the most points); for a gradient-boosting model the usual route is per-prediction attributions (SHAP) mapped to a fixed list of plain-language reasons. This is standard practice but unsourced here.

### Gaps
- No source retrieved on SHAP/LIME, monotonic constraints, counterfactual explanations, or UX research on how scores and reasons should be displayed to business users.

## 6. Real examples

### Takeaway
Independent evidence exists mainly for Upstart (CFPB-reported, company-supplied) and M-Shwari (academic studies); most other figures are vendor statements. Nothing was found for Zest AI, October, Younited, Qonto or Pennylane.

### Cited Findings
- Upstart: first CFPB no-action letter (2017); the CFPB's 2019 update reported 27% more approvals than a traditional model, 16% lower average APR, and near-prime applicants (FICO 620-660) approved about twice as often; figures come from Upstart's own data — [Banking Dive](https://www.bankingdive.com/news/upstart-CFPB-alternativecredit-data-test/560426/); [Upstart](https://www.upstart.com/news/upstart-receives-first-no-action-letter-issued-consumer-financial-protection-bureau)
- M-Shwari (Kenya, via M-Pesa): 30-day loans at 7.5% monthly; the Suri-Bharadwaj-Jack study used a regression discontinuity at the credit-score cutoff and found no increase in savings or productive assets for eligible households — [VoxDev](https://www.voxdev.org/topic/finance/impact-digital-credit-low-income-countries); [IPA](https://poverty-action.org/node/36421/pdf)
- Digital credit outcomes: 12% of digital borrowers in Kenya and 31% in Tanzania have defaulted; 47% in Kenya have repaid late — [CEGA](https://cega.berkeley.edu/article/where-are-we-now-6-years-after-the-first-digital-consumer-credit-product-launched/); an industry blog's "2% default rate" for M-Shwari has no primary source and conflicts with this — [IDcentral](https://dev-idcentral.gridlines.io/?p=21431)
- 2026 NBER working paper (Narayanan, Suri, Bharadwaj) on rate caps: low-score borrowers would lose access entirely under a uniform cap — [NBER w35166](https://www.nber.org/system/files/working_papers/w35166/w35166.pdf)
- Tala, Branch, Kabbage: see section 2 — [Tala](https://tala.co/data-ethics/); [Brankas](https://blog.brankas.com/credit-scoring-innovations); [HousingWire](https://www.housingwire.com/articles/41928-harnessing-the-power-of-alternative-data/)
- Altares, Ellisphere, Creditsafe, Banque de France: see section 1.
- Overview of French business scoring providers for companies — [Stripe guide](https://stripe.com/resources/more/financial-scoring-france)

### Inferences
- The M-Shwari evidence separates two questions a product team tends to merge: a score can rank risk well and the product can still bring little measured benefit to users.

### Gaps
- No results for Zest AI, October, Younited Credit, Qonto or Pennylane payment-risk features; their documentation was not reached. Kabbage's later history (American Express acquisition, 2020) is unsourced here.

## 7. Building a first useful score with limited data

### Takeaway
No source retrieved gives a step-by-step method; the path below is an inference from the cited evidence: start with a transparent rule/points score and a bought failure score, log outcomes, then fit a logistic scorecard once enough late-payment events exist.

### Cited Findings
- Three invoice-level features and five delay classes were enough for a useful late-payment model in the IBM study — [Zeng et al.](https://prem-melville.com/publications/equitant-kdd07.pdf)
- Imbalanced outcomes need cost-sensitive learning — [MIT thesis](https://dspace.mit.edu/handle/1721.1/104327)
- Altman Z'/Z'' need only balance-sheet and income-statement ratios and have published cut-offs — [MetricGate](https://metricgate.com/docs/altman-z-score/)
- Logistic regression is the production choice of a major bureau; random forest is the recommended benchmark — [Creditsafe](https://www.creditsafe.com/content/dam/uk/pdfs/corporate/creditsafe-scorecard-guide-2019.pdf); [Lessmann et al.](https://crc.business-school.ed.ac.uk/sites/crc/files/2023-10/Benchmarking-State-of-the-Art-Classification-Algorithms-for-Credit-Scoring-Lessmann-Seow-Baesens-and-Thomas.pdf)
- PSI thresholds mislead on small portfolios — [arXiv 2307.11878](https://arxiv.org/pdf/2307.11878v4)
- ML's edge shrinks where histories are long, grows for thin files — [BIS WP 834](https://www.bis.org/publ/work834.htm)

### Inferences
- Suggested sequence: (1) expert points score on past payment delay, invoice size vs usual, customer age, disputes, plus Altman Z'' where accounts exist and an external failure score where affordable; (2) store every score with its inputs and the later outcome; (3) once a few hundred "late" events exist, fit a logistic scorecard and compare to the expert score on held-out time periods; (4) only then test gradient boosting as challenger; (5) publish observed late rates per score band, as Banque de France does.
- Keep scores on companies advisory and labelled as estimates; avoid person-level credit decisions unless ready for Article 22 and AI Act duties.

### Gaps
- No sourced rule of thumb on minimum number of bad events for a statistical scorecard, and no sourced guide on expert-scorecard construction (e.g. World Bank/IFC credit scoring handbooks) was retrieved.
