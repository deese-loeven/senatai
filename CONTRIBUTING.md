
# 🏛️ Contributing to Senatai: High-Fidelity Representation

We are thrilled that you are contributing to Senatai\!

Our vision is to transform every citizen's everyday frustration—like **"the price of Cheerios"—into actionable political insights** by connecting it to specific legislation. We are building the **"Industrial Marina Architecture"** for democratic data, where citizens are paid for their opinions and collectively own their political capital (Policaps).

By contributing, you are helping us challenge opaque political systems and uphold the project's philosophy and the terms of the **AGPL-3.0 License**.

-----

## How to Get Started: Prerequisites & Local Setup

A full setup guide is in the **[README.md](README.md)**. Here are the essentials for developers:

### 1\. Prerequisites

  * **Python 3.8+**
  * **Git**
  * **PostgreSQL** (Our core database for legislative data and user trusts).

### 2\. Local Setup Commands

1.  **Fork and Clone:** Fork the `deese-loeven/senatai` repository and clone your fork locally.
    ```bash
    git clone https://github.com/YOUR_USERNAME/senatai.git
    cd senatai
    ```
2.  **Virtual Environment & Dependencies:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
3.  **NLP Setup (spaCy):**
    ```bash
    python -m spacy download en_core_web_sm
    ```
4.  **Database Setup (PostgreSQL):** Follow the steps in **[SETUP.md](SETUP.md)** to install and create the `openparliament` database and the Senatai user.
5.  **Run the Application:**
    The main survey application is currently **`survey_app_improved.py`**.
    ```bash
    python3 survey_app_improved.py
    ```

-----

## The Contribution Process: Modularizing Diversity

The current large set of `question_maker*.py` files contains primitive but valuable logic that reflects diverse methods (e.g., scale-based, yes/no, moral framing, economic focus). Our goal is to **extract this core diversity** into stable, named modules and integrate them into a selectable system for bias cross-referencing.

Your contributions should focus on two key areas:

1.  **Refactoring for Stability:** Creating a stable core set of modules (scrapers-any program to extract laws from the web or extract keywords and phrases or other info while referencing legal texts, authentication, database) to deploy for the public.
2.  **Modularizing Diversity:** Isolating the best and most diverse logic from the existing question maker files and giving them a stable, descriptive file name.

### Workflow: Fork & Pull Request (PR)

1.  **Fork** the repository and **Create a New Branch** that clearly references the issue and the relevant module (e.g., `feat/nlp-add-moral-dilemma-qm-52`, `fix/policap-reward-logic-12`).
2.  **Commit Your Changes** locally.
3.  **Test Locally:** Ensure your changes don't break the core user loop (Authentication, Questioning, Policap Reward).
4.  **Open a Pull Request** against the `main` branch.

-----

## 🎯 High-Impact Contribution Areas

### 1\. NLP Modules (High Priority)

| Goal | Actionable Task | Key Files |
| :--- | :--- | :--- |
| **Upgrade the Core System** | Modify **`adaptive_survey8.py`** to import and dynamically select different named Question Maker modules. | `adaptive_survey8.py` |
| **Isolate Diversity** | **Do NOT create new numbered prototype files.** Instead, identify 3-5 unique and functional methods/styles from wherever you find good questions or the primitive `question_maker*.py` files and refactor them into stable, descriptive files (e.g., `qm_economic_focus.py`, `qm_scale_moral_dilemma.py`) within the `senatai/nlp_modules/` directory. | `question_maker*.py` |
| **Law Linking** | Ensure all new modules successfully reference the law or bill text in the database (like the `adaptive_survey` series does). | `adaptive_survey8.py` |

### 2\. Core Refactoring & Localization

  * **Refactor Prototypes:** Consolidate files related to scraping and keyword extraction into their respective modules.
  * **Localization:** **Try running this on local law databases wherever you are.** This is essential to test the flexibility and jurisdiction handling of the scrapers.
  * **Testing:** We need unit tests\! Contributions focused on building out the `tests/` directory are highly welcome.

-----

## Style & Conventions

  * **Prototyping:** **The practice of creating new numbered prototype files (e.g., `question_maker11.py`) is now discouraged.** New ideas should be immediately implemented as named modules (e.g., `qm_new_method_v1.py`) and placed under a development flag for testing.
  * **Old Prototypes:** The 99% of non-functional, redundant LLM output files in the root directory should be **removed** in a separate, clean Pull Request once the core diversity is secured.
  * **Python Code Style:** All Python code must adhere strictly to **PEP 8 standards**. Use a linter (like Black or Flake8) to ensure compliance.
  * **Commit Messages:** Commit messages must be detailed, descriptive, and **reference the issue number** they address.
      * *Good Example:* `feat(nlp_modules): Add qm_economic_focus.py module for issue #52`

## Code of Conduct

All contributors must abide by the **Senatai Code of Conduct**. Please review the rules of engagement and the reporting procedure found in:
[CODE\_OF\_CONDUCT.md](https://www.google.com/search?q=CODE_OF_CONDUCT.md)
