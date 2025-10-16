# 🧱 SENATAI Project Board
*Operational tracker for October 2025 – June 2026*

---

## 🎯 Goal
Turn the working Senatai MVP — which already processes 1,900+ bills and generates contextual questions —  
into a **secure, cooperative civic engagement platform** with real MP communication and data reporting.

---

## 🗂️ Column Overview

| Column | Description |
|---------|--------------|
| 🧩 **To Do** | Planned features or tasks not yet started |
| 🚧 **In Progress** | Active development or testing |
| ✅ **Done** | Completed, validated, or deployed features |

---

## 🧩 TO DO

### 🔹 Phase 1 — Foundation & Trust (Oct–Dec 2025)
- [ ] **Incorporate Senatai as a Canadian cooperative**
- [ ] Draft cooperative bylaws & governance model  
- [ ] Conduct initial **security audit** of database and scripts  
- [ ] Write **Privacy Policy** and **Terms of Service**  
- [ ] Create **PIPEDA compliance checklist**  
- [ ] Build **postal code → riding lookup** using Elections Canada data  
- [ ] Gather **MP contact database** (email + riding info)  
- [ ] Implement **opt-in consent system** for sending data to MPs  
- [ ] Choose and configure **email delivery service** (SendGrid / AWS SES)  
- [ ] Begin **Next.js web interface prototype**  
- [ ] Write basic **API endpoint** for survey submission  

### 🔹 Phase 2 — Expansion & Data Depth (Jan–Mar 2026)
- [ ] Integrate **Ontario, BC, Quebec** provincial data sources  
- [ ] Add **bill status tracking** and **voting records**  
- [ ] Implement **user authentication & profile system**  
- [ ] Create **Policap MVP** (simple PostgreSQL points system)  
- [ ] Develop **anonymized reporting pipeline**  
- [ ] Draft **legal trust framework** for data ownership  
- [ ] Add **Democracy Score prototype** logic  

### 🔹 Phase 3 — Revenue & Scaling (Apr–Jun 2026)
- [ ] Build **data-product API** for client access  
- [ ] Implement **client portal** (secure login + report view)  
- [ ] Add **subscription & billing** integration (Stripe / open-source)  
- [ ] Launch **media / policy outreach campaign**  
- [ ] Develop **community features** (threads, user-submitted Qs)  
- [ ] Prepare **first dividend payment workflow**  

---

## 🚧 IN PROGRESS

| Task | Owner | Notes |
|------|--------|-------|
| MP contact system (Send to MP feature) | @deese-loeven | Building postal code → riding mapping and email templates |
| Next.js web prototype | — | Early layout testing, integrates with Python API |
| Bill processing automation | @deese-loeven | Continuous; 1,921 bills processed |
| Documentation (README + WISHLIST + ROADMAP) | @deese-loeven | Public-ready versions complete |
| Legal research (cooperative structure) | — | Identifying Canadian co-op lawyer |

---

## ✅ DONE

| Task | Completion | Notes |
|------|-------------|-------|
| NLP → Legislation pipeline | ✅ Jan 2025 | Proven via first real-user test |
| Adaptive survey system | ✅ Oct 2025 | Working MVP; validated by non-technical user |
| Keyword extraction + matching engine | ✅ Oct 2025 | 62,000 keywords indexed |
| PostgreSQL database architecture | ✅ Oct 2025 | Stable, efficient under light load |
| Documentation overhaul | ✅ Oct 2025 | README, WISHLIST, ROADMAP complete |
| GitHub repo cleanup | ✅ Oct 2025 | Removed heavy datasets, added usage note |

---

## 🧭 PRIORITY SNAPSHOT (Q4 2025)

| Rank | Task | Impact |
|------|------|--------|
| 1️⃣ | **Send to MP feature (email delivery)** | Core user request; essential for real-world impact |
| 2️⃣ | **Legal incorporation & data trust** | Enables public launch & compliance |
| 3️⃣ | **Security & privacy audit** | Required for safe user onboarding |
| 4️⃣ | **Web frontend MVP** | Allows open access & scaling |
| 5️⃣ | **MP database + postal lookup** | Supports all contact features |

---

## 🧰 Suggested Labels

Use these GitHub labels for issues and pull requests:

| Label | Description |
|--------|-------------|
| `priority:high` | Must complete this quarter |
| `priority:medium` | Next-phase work |
| `priority:low` | Nice-to-have |
| `type:feature` | New functionality |
| `type:bug` | Fix required |
| `type:legal` | Cooperative / privacy / licensing work |
| `type:data` | Legislative data or keyword extraction |
| `type:frontend` | Web UI or user interface |
| `type:backend` | Database, pipeline, or processing logic |
| `type:docs` | Documentation or writing |
| `help-wanted` | Ideal for open-source contributors |

---

## 🧑‍🤝‍🧑 Contributors Needed

| Role | Description |
|------|--------------|
| **Co-op / Privacy Lawyer** | Incorporation, bylaws, and compliance |
| **Web Developer (Next.js)** | Build frontend for surveys and dashboards |
| **Security Engineer** | Review encryption, auth, and data handling |
| **Data Engineer** | Anonymization pipeline and reporting tools |
| **Policy Researcher** | Help define valuable data metrics |
| **Community Manager** | Onboard early users and testers |

---

## 📅 Next Update Cycle

- **Next review:** November 2025  
- **Focus:** Finish MP contact prototype + legal incorporation draft  
- **Goal:** Public web MVP by December 2025  

---

> *This board evolves continuously.  
> Use it as the single source of truth for active work, open issues, and collaboration priorities.*

_Last updated: October 15 2025_
