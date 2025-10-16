# 🧭 Senatai Development Wishlist — October 2025

## Where We Are Now

**Working Components:**

- ✅ NLP keyword extraction matching user concerns to legislation  
- ✅ 1,921 bills processed with 62,740 keywords  
- ✅ Contextual question generation using actual bill text  
- ✅ PostgreSQL database architecture  
- ✅ User-tested interface (validated by non-technical users)  
- ✅ GitHub repo with professional documentation  

**What This Means:**  
We’ve already built the hardest parts of Phase 1 — the legislative data pipeline, basic question generation, and user interface.  
We skipped past a lot of the original roadmap by building what actually matters first.

---

## 🚀 Critical Path: What We Need Next

### 1. Send Survey Results to MPs (**Top Priority**)

**Why:**  
First user request. People want their representatives to see this data immediately.

**What We Need:**

- Database of current Canadian MPs with contact information  
- Riding boundary data mapped to postal codes / area codes  
- User location capture (postal code input during signup)  
- Automated email/message formatting system  
- Template system: “Your constituent [Anonymous ID] responded to questions about Bill C-227. Here are their views…”

**Legal / Privacy Considerations:**

- Users must explicitly opt-in to contact their MP  
- We need to anonymize while still proving authenticity  
- Email delivery system that doesn’t get flagged as spam  
- Clear disclaimers about what MPs will receive  

**Tech Stack:**

- Riding boundary data → Elections Canada geographic data  
- Email service → SendGrid or AWS SES  
- Postal code → Riding lookup → Canadian postal code database  

**MVP Version:**

- User enters postal code → identify their MP  
- After completing survey → prompt: “Send your responses to [MP Name]?”  
- If yes → send formatted summary with anonymized results  

---

### 2. Security & Legal Infrastructure

**Why:**  
Before we can responsibly collect user data and contact MPs, we need proper legal structure and security.

#### Incorporation

- Register Senatai as a **cooperative in Canada**  
- Draft cooperative bylaws and governance structure  
- Establish the **data trust** legal framework  
- Get legal review of our data collection and usage  

#### Database Security

- Encryption for user data at rest  
- SSL/TLS for all data in transit  
- Secure authentication system (beyond prototype)  
- Access logging and audit trails  
- Regular security audits  

#### Privacy Compliance

- PIPEDA compliance for Canadian data  
- Clear privacy policy and terms of service  
- Data retention and deletion policies  
- User consent management system  

**Immediate Help Needed:**

- Cooperative law attorney (Canadian)  
- Privacy law consultation  
- Security audit of current system  
- Proper user authentication implementation  

---

### 3. Web Interface (For Broader Access)

**Why:**  
Currently running as Python scripts. We need an accessible web interface for public use.

**What We Need:**

- Simple web frontend (Next.js or similar)  
- Mobile-responsive design  
- User accounts and authentication  
- Survey presentation interface  
- Results visualization dashboard  

**Key Features:**

- Clean, fast question interface  
- Real-time bill matching as user types concerns  
- Progress tracking through survey  
- Personal response history  
- Aggregate results display  

**Design Principles:**

- If my wife can use it easily, anyone can  
- No unnecessary complexity  
- Fast loading on slow connections  
- Works on mobile phones  

---

### 4. Enhanced Legislative Data

**Current State:**  
1,921 federal bills with strong keyword extraction

**What We Want:**

- **Provincial legislation:** Ontario, BC, Quebec first  
- **Municipal bylaws:** Major cities (Toronto, Vancouver, Montreal)  
- **Bill status tracking:** Did it pass? When? How did MPs vote?  
- **Historical votes:** Link bills to actual MP voting records  
- **Committee hearings:** Testimony and expert input data  

**Why This Matters:**

- Users care more about local issues (housing, transit, schools)  
- Enables calculation of a “**Democracy Score**” — how often MPs vote against constituent preferences  
- Richer data → more valuable to sell  

---

### 5. Policap System (Simplified Version)

**Original Roadmap:**  
Blockchain, smart contracts, complex token economics

**What We Actually Need Now:**

- Simple point system in PostgreSQL  
- Daily participation rewards (10 questions = 1 Policap)  
- Track user engagement over time  
- Basic “wallet” showing accumulated Policap  

**Why Simpler Is Better:**

- Blockchain adds massive complexity we don’t need yet  
- PostgreSQL can handle everything for now  
- Can migrate to blockchain later if needed  
- Focus on user experience, not technical complexity  

**Future Use Cases for Policap:**

- Voting weight on platform governance decisions  
- Share of data trust dividends when monetized  
- Proof of sustained civic engagement  

---

### 6. Data Monetization Preparation

**Why:**  
We need revenue to sustain development and pay dividends to users.

#### Data Products to Sell

- **Riding-level consensus reports:** “Here’s what 500 constituents think about Bill C-227.”  
- **Trend analysis:** “Support for housing legislation shifted 15% in 3 months.”  
- **Predictive insights:** “Here’s likely public reaction to proposed policy X.”  
- **Comparative analysis:** “How Ontario differs from BC on environmental policy.”  

#### Target Clients

- Political campaigns and strategists  
- Policy research organizations  
- Media companies (alternative to Gallup/Ekos)  
- Government agencies  
- Think tanks and advocacy groups  

#### What We Need Built

- Anonymization pipeline (differential privacy)  
- Client portal for data access  
- Reporting dashboard and API  
- Subscription and billing system  
- Audit trail proving data legitimacy  

---

### 7. Question Quality & Bias Detection

**Current State:**  
Questions generated from bill text, manually reviewed

**What We Need:**

- Bias detection system for generated questions  
- Community rating of question quality  
- A/B testing framework for question formats  
- Expert review for high-stakes bills  
- Multiple question generation modules users can choose from  

**Why:**

- Credibility depends on fair, unbiased questions  
- Different question styles suit different topics  
- Users should be able to pick question generators they trust  
- Transparency about methodology builds trust  

---

### 8. Community Features (Lower Priority But Valuable)

**What Would Help:**

- User discussion threads on specific bills  
- “Expert explainers” — verified subject matter experts add context  
- Source citation for bill summaries  
- User-submitted questions (moderated)  
- Local community groups within platform  

---

## 🧱 What We’re *Not* Worried About Yet

### Things From Original Roadmap We Can Delay

1. Mobile apps — Web works fine for now  
2. International expansion — Canada first  
3. Alternative input methods (paper/SMS) — Later  
4. Advanced AI — Current NLP is good enough  
5. Blockchain — Database is plenty for now  

---

## 💼 Resource Reality Check

**What I Have:**

- Working code and proven concept  
- Time and determination  
- Carpentry income to sustain development  
- One validated user (and counting)  

**What I Need:**

### Immediate (Next 3 Months)

- Legal consultation (10–20 hours)  
- Security audit (professional review)  
- Web developer (frontend help — volunteer/contributor welcome)  
- DevOps help (deployment and hosting setup)  

### Medium-Term (3–6 Months)

- 2–3 part-time contributors on key features  
- Data engineer (for anonymization and client portal)  
- Legal incorporation (register the cooperative)  

### Funding Requirements

- **Months 1–3:** $5,000–10,000 (legal, hosting, security)  
- **Months 4–6:** $10,000–20,000 (development help, scaling)  
- **Months 7–12:** $30,000–50,000 (part-time team, first data sales)  

---

## 📊 Success Metrics

### By December 2025

- ✅ Web interface live and public  
- ✅ 100+ registered users  
- ✅ “Send to MP” feature working  
- ✅ Basic security audit complete  
- ✅ Legal structure in progress  

### By March 2026

- ✅ 500+ active users  
- ✅ Provincial legislation integrated  
- ✅ First data monetization pilot  
- ✅ Cooperative legally incorporated  
- ✅ Democracy Score prototype working  

### By June 2026

- ✅ 2,000+ users  
- ✅ Sustainable revenue from data sales  
- ✅ First dividend payment to user-owners  
- ✅ Multiple jurisdictions using platform  
- ✅ Media coverage and policy impact  

---

## 🧠 The Real Goal

This isn’t about following a roadmap. It’s about:

1. **Making democracy measurable** — Can we prove laws don’t have consent?  
2. **Giving people voice** — Can we make legislatures listen?  
3. **Creating value for users** — Can civic participation actually pay?  
4. **Building sustainable infrastructure** — Can this fund itself?  

The original roadmap was just a guess.  
Nine months of real building taught me what matters:

- **Users don’t care about blockchain** — they care if their MP sees their views  
- **Perfect code doesn’t matter** — working code that people use does  
- **Complex AI is overrated** — good NLP and clear questions work fine  
- **Scale comes later** — legal foundation and security come first  

---

## 🤝 How You Can Help

If you want to contribute:

1. **Lawyers:** Cooperative law & privacy law (Canada)  
2. **Developers:** [github.com/deese-loeven/senatai](https://github.com/deese-loeven/senatai) — Python, PostgreSQL, web  
3. **Security experts:** Please audit our system before public release  
4. **Policy researchers:** Help identify valuable data insights  
5. **Users:** Test the system, break it, and give feedback  
6. **Funders:** Provide runway to build this properly  

---

> **What we’re building is proof that a carpenter can create democratic infrastructure.**  
>
> If it works, it proves civic tech doesn’t need to come from Silicon Valley or government grants.  
> It can come from someone frustrated that democracy wasn’t good enough for their daughter.

---

*This wishlist is a living document. As we build and learn, priorities will shift. The goal isn’t to follow a plan — it’s to build something that works and matters.*

_Last updated: October 15, 2025_
