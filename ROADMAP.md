# 🗺️ Senatai Roadmap — October 2025 to June 2026

*Building civic tech that works — from carpentry shop to cooperative.*

---

## 📍 Overview

Senatai has proven its foundation:  
- Real NLP matching user concerns to 1,900+ federal bills  
- Fully automated keyword extraction and question generation  
- Stable PostgreSQL backend running at 5% CPU on a 2017 laptop  
- User-tested prototype verified by non-technical participants  

Now the goal is to move from **working prototype → public cooperative platform**  
by focusing on legal structure, security, and accessibility.

---

## 🧩 Phase 1 — Foundation & Trust (Oct–Dec 2025)

| Goal | Description | Dependencies | Status |
|------|--------------|---------------|---------|
| **Send to MP Feature** | Allow users to forward survey results directly to their MP | Postal code → riding mapping, MP contact DB | 🟡 In Progress |
| **Legal Incorporation** | Register Senatai as a Canadian cooperative | Legal consultation, draft bylaws | ⚪ Not Started |
| **Security Audit** | Review data handling, storage, and encryption | Secure prototype database | ⚪ Planned |
| **Web Prototype** | Build minimal Next.js interface for survey use | Existing Python scripts | 🟡 In Progress |
| **Documentation** | Complete README, WISHLIST, and data usage notes | Current repo | 🟢 Done |

**Outcome by December 2025:**
- Web survey live  
- MP contact feature working  
- Legal structure in progress  
- Privacy policy drafted  
- First 100+ users onboarded  

---

## 🧠 Phase 2 — Expansion & Data Depth (Jan–Mar 2026)

| Goal | Description | Dependencies | Status |
|------|--------------|---------------|---------|
| **Provincial Integration** | Add Ontario, BC, Quebec bills | Open data ingestion pipeline | ⚪ Planned |
| **Bill Tracking System** | Track votes, passage dates, outcomes | Government vote data | ⚪ Planned |
| **User Accounts** | Secure login and profile system | Auth + database upgrade | ⚪ Planned |
| **Policap System (MVP)** | Implement internal point/reward logic | PostgreSQL wallet table | ⚪ Planned |
| **Anonymized Reporting** | Generate early constituency reports | Differential privacy module | ⚪ Planned |

**Outcome by March 2026:**
- 500+ active users  
- Provincial data integrated  
- First “Democracy Score” prototype  
- Cooperative legally incorporated  
- Data reporting pipeline ready for testing  

---

## 💰 Phase 3 — Revenue & Scaling (Apr–Jun 2026)

| Goal | Description | Dependencies | Status |
|------|--------------|---------------|---------|
| **Data Product Pilot** | Sell anonymized reports to pilot clients | Reporting pipeline | ⚪ Planned |
| **Client Portal** | Secure dashboard for paid access | Authentication system | ⚪ Planned |
| **Subscription System** | Billing and payments for data services | Stripe or open-source alternative | ⚪ Planned |
| **Community Features** | Discussions, user-submitted questions | Active web interface | ⚪ Planned |
| **Public Launch** | Media outreach, cooperative membership drive | Stable v1.0 release | ⚪ Planned |

**Outcome by June 2026:**
- 2,000+ users  
- Sustainable monthly revenue  
- First dividend to user/owners  
- Policy/media coverage achieved  
- Cooperative governance online  

---

## 🔐 Dependencies & Interlinking Tasks

| Dependency | Supports | Notes |
|-------------|-----------|-------|
| **Legal incorporation** | All public & financial activity | Must precede data monetization |
| **Security audit** | User accounts, MP contact feature | Required before large-scale onboarding |
| **Web frontend** | User expansion, community features | MVP can be minimal |
| **Data enrichment (provincial)** | Policap system, Democracy Score | Enables deeper engagement metrics |
| **Anonymization pipeline** | Data sales, research access | Must be validated before any monetization |

---

## ⚙️ Toolchain Overview

| Layer | Technology | Purpose |
|--------|-------------|----------|
| Backend | Python + PostgreSQL | Legislative data & Policap tracking |
| NLP | Custom keyword extraction + LLM | Bill analysis & question generation |
| Frontend (planned) | Next.js + Tailwind CSS | User interaction interface |
| Email / Notifications | SendGrid or AWS SES | MP contact & user summaries |
| Hosting | Lightweight VPS / containerized deployment | Affordable scalability |
| Legal | Canadian Cooperative model | Democratic ownership and data trust |

---

## 📈 Key Metrics & Targets

| Date | Users | Data Coverage | Feature Milestone |
|------|--------|---------------|-------------------|
| Dec 2025 | 100+ | Federal bills | MP contact system live |
| Mar 2026 | 500+ | Federal + 3 provinces | Democracy Score MVP |
| Jun 2026 | 2,000+ | National scope | Data monetization pilot + cooperative launch |

---

## 🧰 Resources Needed

| Role | Timeframe | Description |
|------|------------|-------------|
| **Cooperative Lawyer** | Q4 2025 | Incorporation & bylaws |
| **Privacy & Security Consultant** | Q4 2025 | PIPEDA compliance & audit |
| **Web Developer (Next.js)** | Q4 2025–Q1 2026 | Frontend implementation |
| **Data Engineer** | Q1–Q2 2026 | Anonymization pipeline & reporting |
| **Funding Partners** | Ongoing | $5k–$50k seed for operations |

---

## 🧭 Vision Beyond June 2026

- 🇨🇦 **National adoption** — every riding measurable  
- 📊 **Real-time Democracy Score** — track representation accuracy  
- 💸 **Data dividends** — users earn from civic engagement  
- 🌍 **Open infrastructure** — extend model to other democracies  
- 🪶 **Legacy impact** — prove that ordinary citizens can rebuild democratic feedback systems  

---

> *Senatai’s roadmap isn’t about chasing hype. It’s about proving that civic infrastructure can be built by citizens — not corporations — and that democracy can measure itself in real time.*

_Last updated: October 15, 2025_
