# Roth IRA Accounting Engine — Review & Implementation Action Plan

## 1. Existing Notes
- [ ] Compare with 401(k) and Traditional IRA (covered conceptually in Sections 1.1–1.2 & Section 4.3 Priority Queue vs. Pro-Rata Pools)

---

## 2. Validated Fixes from ChatGPT & Claude Reviews (Sections 1–3.5)

### A. Confirmed Numerical & Citation Fixes
- [x] **1. Fix 2026 401(k) Age 50+ Catch-Up Limit (`§3.3`)**:
  - Change `$32,000` (`age 50–59` / `64+`) to **`$32,500`** (`$24,500` base + `$8,000` standard catch-up under `IRC § 414(v)`). Keep `$35,750` for ages `60–63`.
  - Explicitly note in the `IRC § 415(c)` formula that catch-up contributions (`IRC § 414(v)(3)(A)`) sit **outside** the `$72,000` annual additions cap.
- [x] **2. Fix `Treas. Reg. § 1.408A-10` Citation Lettering (`§3 Intro`, `§3.3`, `§3.5`)**:
  - Replace `Treas. Reg. § 1.408A-10 Q&A-3(b)` with **`Treas. Reg. § 1.408A-10 Q&A-3(a)`** (which contains both the general non-qualified rollover allocation rule and the qualified rollover bonus rule; `Q&A-3(b)` is only for underwater accounts).
- [x] **3. Fix 2026 Retirement Limits IRS Citation (`§3.1`)**:
  - Cite **`IRS Notice 2025-67`** (which publishes the 2026 retirement plan & IRA limits/phaseouts) instead of `Rev. Proc. 2025-32`.
- [x] **4. Use Verbatim TCJA Conference Report Quote & Tighten Step-Transaction Wording (`§3.2`)**:
  - Quote **H.R. Rep. No. 115-466, Footnotes 268 & 269** verbatim:
    > *"Although an individual with AGI exceeding certain limits is not permitted to make a contribution directly to a Roth IRA, the individual can make a contribution to a traditional IRA and convert the traditional IRA to a Roth IRA."*
  - Replace the overbroad claim that Congress barred judicial anti-abuse doctrines with the exact legal conclusion: neither `IRC § 408A` nor Treasury Regulations impose a 30-day waiting period, and Congress explicitly recognized the contribution-and-conversion mechanism in the 2017 TCJA Conference Report.

### B. Conceptual & Precision Refinements
- [x] **5. Reframe the Pro-Rata Job-Hop Bug Outcome (`§3.2`)**:
  - Clarify that the `$6,937.50` taxable outcome does not "destroy" or double-tax your basis forever—instead, the IRS forces you to convert `$6,937.50` of your **pre-tax Rollover IRA** (taxing it now), while leaving `$6,937.50` of your **post-tax basis trapped inside the Rollover IRA**.
- [x] **6. Unify the 3-Clock Model (`§2.1`, `§2.3`, `§3.3`, `§3.5`)**:
  - **`Clock A` (`IRC § 408A(d)(3)(F)` & `§ 402A(c)(4)(D)`)**: Per-tranche 5-tax-year conversion recapture clock (applies to every taxable conversion tranche, whether in a Roth IRA or an in-plan 401(k) conversion, starting Jan 1 of the conversion tax year).
  - **`Clock B` (`IRC § 408A(d)(2)(B)`)**: Global Roth IRA 5-tax-year qualified maturity clock (starts Jan 1 of the earliest tax year for which a regular contribution, conversion, or rollover entered any Roth IRA owned by the taxpayer).
  - **`Clock C` (`IRC § 402A(d)(2)(B)`)**: Per-plan Designated Roth 401(k) 5-tax-year participation clock (governs whether a Roth 401(k) distribution is qualified before rollover—and **does not carry over** to `Clock B` upon rollover into a Roth IRA under `Treas. Reg. § 1.408A-10` Q&A-4).
- [x] **7. Precision Polish in `§1.1`, `§3 Intro`, & `§3.3`**:
  - **`§1.1`**: Specify that selling an *appreciated* position in a taxable brokerage triggers capital gains, qualify state conformity phrasing slightly, and mention the secondary qualified distribution triggers (`death`, `disability`, or up to `$10,000` lifetime `first-time homebuyer`) alongside `Age >= 59½`.
  - **`§3 Intro`**: Write *"FIFO by conversion tax year (and within each year's tranche, `2a` is drained before `2b`)"* so `2a > 2b` is unambiguously scoped within each tax year.
  - **`§3.3`**: Change *"often strictly superior"* to *"architecturally advantageous"*, qualify that Day-1 `Tier 1` liquidity applies *once rolled into a Roth IRA* (subject to plan rollover rules), and include a 1-sentence CPA note on `Form 8606` Line 22 (`§ 1.408A-10` Q&A-3(a)) vs. taxable in-plan conversion recapture (`§ 402A(c)(4)(D)`).

---

## 3. Items Deliberately Ignored (Avoiding Scope Creep)
- **Adding data-model schemas or formal invariants into Section 3**: That belongs in **Section 4 (The Formal Domain Model & Interactive Ledger)**, which immediately follows Section 3.
- **Excessive lawyerly hedging on every paragraph**: The document opens with a formal Legal & Tax Disclaimer; keeping the engineering prose crisp and readable is a priority.
