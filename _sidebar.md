<!-- _sidebar.md -->

* **[🏠 Home / Overview](README.md)**
  * [The Core Dilemma](README.md#the-core-dilemma)
  * [3-Phase Architecture](README.md#the-3-phase-architecture)
  * [Strategy Comparison Matrix](README.md#strategy-comparison-on-30000-gross-salary)
  * [Statutory Certainty Matrix](README.md#statutory-certainty-matrix)

* **[📖 Full Technical Design Document](TECHNICAL_DESIGN_DOCUMENT.md)**
  * [1. Executive Summary](TECHNICAL_DESIGN_DOCUMENT.md#executive-summary)
  * [2. Context & Scope](TECHNICAL_DESIGN_DOCUMENT.md#context-and-scope)
  * [3. System Architecture](TECHNICAL_DESIGN_DOCUMENT.md#system-architecture)
  * [4. Preconditions & Certainty](TECHNICAL_DESIGN_DOCUMENT.md#system-preconditions-statutory-certainty--assumptions)
  * [5. Detailed Design](TECHNICAL_DESIGN_DOCUMENT.md#detailed-design)
    * [Phase 1: Ingestion & Match](TECHNICAL_DESIGN_DOCUMENT.md#1-ingestion--match-capture-years--t_0--all-us-working-years)
    * [Phase 2: RNOR Conversions](TECHNICAL_DESIGN_DOCUMENT.md#2-paced-roth-conversions-during-rnor-years-t_1-to-t_3--us-nra--india-rnor)
    * [Phase 3: 5-Year FIFO Unlock](TECHNICAL_DESIGN_DOCUMENT.md#3-five-year-seasoning--fifo-dequeue-year-t5--india-ror)
  * [6. Production Gotchas](TECHNICAL_DESIGN_DOCUMENT.md#production-constraints-gotchas--guardrails)
    * [The 3 Custodian Paths](TECHNICAL_DESIGN_DOCUMENT.md#1-custodian--plan-routing-gotchas-the-3-execution-paths)
    * [60-Day Top-Up Protocol](TECHNICAL_DESIGN_DOCUMENT.md#2-path-2-if-funds-are-already-in-a-traditional-ira-traditional-ira--roth-ira-via-charles-schwab-international--30-withholding-top-up)
    * [Taxable Basis Reset](TECHNICAL_DESIGN_DOCUMENT.md#2-taxable-brokerage-cost-basis-step-up-the-rnor-basis-reset-gotcha)
  * [7. Alternatives Considered](TECHNICAL_DESIGN_DOCUMENT.md#alternatives-considered)
  * [8. Sensitivity Analysis](TECHNICAL_DESIGN_DOCUMENT.md#sensitivity-analysis-boundary-conditions--failure-modes)
  * [9. Quality Attributes](TECHNICAL_DESIGN_DOCUMENT.md#quality-attributes)
  * [10. Project Management](TECHNICAL_DESIGN_DOCUMENT.md#project-management)
  * [11. Operations & Checklist](TECHNICAL_DESIGN_DOCUMENT.md#operations)
  * [12. Appendix: Statutory Sources](TECHNICAL_DESIGN_DOCUMENT.md#appendix-statutory-references--primary-sources)

* **[⚖️ Legal Disclaimer](README.md#legal--tax-disclaimer)**
* **[🤝 Community RFC & Issues](https://github.com/mradityagoyal/us-india-401k-blueprint/issues)**
