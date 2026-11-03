
# Review: The Roth IRA Accounting Engine (v0.1)

My overall assessment: the systems architecture is compelling, but I would not publish this version as a technically validated tax specification yet.

You've got a genuinely useful abstraction here: a taxpayer-level ledger, typed capital based on tax provenance, ordered withdrawals, and independent statutory clocks.

The strongest part is that you're not merely explaining how to execute a Backdoor or Mega Backdoor Roth. You're trying to build a unified accounting model that explains what happens to the money after it enters the Roth ecosystem.

That's a much more interesting engineering problem.

However, I see several discrepancies that go beyond wording. Some affect the core ledger architecture, particularly the distinction between:

- Regular Roth IRA contribution basis.
- Taxable and nontaxable Roth IRA conversion amounts.
- Designated Roth 401(k) rollover amounts.
- The ordering of conversion tranches.
- The distinction between Roth IRA and Roth 401(k) distribution rules.

I would separate the review into three categories:

1. Correctness defects: Statements or calculations that need correction.
2. Modeling defects: The legal rule may be directionally correct, but the abstraction is inaccurate or incomplete.
3. Presentation defects: Overgeneralizations that could cause readers to misunderstand an otherwise valid rule.

## 1. Critical discrepancies — fix before community review

These are the ones I would treat as blockers rather than editorial suggestions.

### 1.1 The Tier 2 FIFO ordering is not specified precisely enough

High priority · Core accounting logic

This is probably the most important defect in the current specification.

You repeatedly describe the ordering as:

> Tier 2 (FIFO by calendar year, with 2a drained before 2b)

This is directionally correct, but the ordering needs a more precise definition.

Under Treasury Regulation §1.408A-6, Q&A-8:

1. Conversion contributions are distributed FIFO by conversion year.
2. Within each conversion year's tranche, the taxable portion is distributed before the nontaxable portion.

The second rule is not a global priority rule across every conversion year.

Consider this example:

| Conversion year | Type                     | Amount  |
| --------------- | ------------------------ | ------- |
| 2024            | 2b — nontaxable basis   | $10,000 |
| 2025            | 2a — taxable conversion | $20,000 |
| 2026            | 2b — nontaxable basis   | $7,500  |

The withdrawal sequence is:

1. 2024 2b — $10,000
2. 2025 2a — $20,000
3. 2026 2b — $7,500

The older 2024 nontaxable conversion is not pushed behind a newer taxable conversion from 2025.

Your current description could lead someone implementing the ledger to create a global priority queue with `2a > 2b`, which would be wrong.

Suggested replacement:

> Tier 2 is ordered chronologically by conversion tax year (FIFO). Within each tax-year tranche, the taxable portion (2a) is dequeued before the nontaxable portion (2b). Consequently, a taxable conversion can block nontaxable basis from the same year, but cannot jump ahead of nontaxable conversion basis from an earlier year.

This should become an explicit invariant in your eventual data model.

Source:&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.law.cornell.edu\&sz=32)

LII / Legal Information Institute+1

### 1.2 The Mega Backdoor rollover classification needs a more precise statutory explanation

High priority · Core ledger architecture

Your central assertion is:

> 100% of your Mega Backdoor Basis maps directly into Tier 1: Regular Contribution Basis.

This is substantially correct for the contribution basis, but your regulatory reference needs fixing.

You cite:

`Treas. Reg. § 1.408A-10 Q&A-3(b)`

The general rule is actually in Q&A-3(a).

Q&A-3(a) establishes that:

- The portion treated as investment in the contract (basis) becomes regular contribution basis for Roth IRA ordering.
- The remainder is treated as earnings.
- If the designated Roth account distribution is qualified, the entire rollover amount is treated as regular contribution basis.

Q&A-3(b) addresses a narrower situation involving distribution of the entire account balance, a partial rollover, and investment in the contract exceeding the account balance.

That distinction matters.

There are three cases your model should distinguish:

| Designated Roth 401(k) distribution                               | Roth IRA classification                                              |
| ----------------------------------------------------------------- | -------------------------------------------------------------------- |
| Nonqualified distribution                                         | Investment-in-contract portion → Tier 1; earnings portion → Tier 3 |
| Qualified distribution                                            | Entire rollover → Tier 1                                            |
| Nonqualified distribution with the special excess-basis situation | Apply Q&A-3(b) adjustment                                            |

The first case is particularly important for someone under 59½ who has not satisfied the plan's five-year participation requirement.

Your current outcome is largely right, but the legal reasoning and citation are not.

There is another subtlety: a qualified distribution from a designated Roth account requires the five-year participation period AND an applicable qualifying event, such as attaining 59½, death, or disability. It isn't simply a five-year-old Roth 401(k).

Also, the designated Roth account's five-year clock and the Roth IRA's five-year qualified-distribution clock are independently determined. The Roth IRA clock begins under its own rules, taking into account the year of the rollover where applicable.

Sources:&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.law.cornell.edu\&sz=32)

LII / Legal Information Institute+2

### 1.3 Your 2026 catch-up contribution number is wrong

High priority · Numerical error

Section 3.3 states:

> $32,000 for age 50–59 / 64+

The correct figures are:

| Age      | 2026 elective deferral capacity |
| -------- | ------------------------------- |
| Under 50 | $24,500                         |
| 50–59   | $32,500                         |
| 60–63   | $35,750                         |
| 64+      | $32,500                         |

The general catch-up is $8,000, not $7,500, for 2026.

The age 60–63 enhanced catch-up is $11,250.

There is also a modeling issue here: catch-up contributions are excluded from the §415(c) annual additions calculation.

That means your Mega Backdoor capacity formula should explicitly exclude catch-up deferrals from the amount consuming the $72,000 limit.

For example, an employee aged 52 who contributes $32,500 (including $8,000 catch-up) does not consume $32,500 of the §415(c) limit. The amount consuming that limit is $24,500.

This is important when implementing the calculator.

Sources:&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.irs.gov\&sz=32)

Internal Revenue Service+2

### 1.4 Your three-clock model needs refinement

High priority · Architecture

You introduce:

- Clock A: conversion recapture.
- Clock B: Roth IRA qualified distribution maturity.
- Clock C: designated Roth 401(k) maturity.

The existence of these three distinct five-year periods is a useful abstraction.

However, the way you currently describe Clock C is misleading:

> One overlay clock for taxable in-plan 401k rollovers.

The designated Roth 401(k) five-year participation clock determines whether a distribution from that workplace account is qualified.

It does not simply overlay the Roth IRA's qualified-distribution clock.

The Roth IRA has its own five-year period. Under §1.408A-10 Q&A-4, the year of a designated Roth account rollover can establish the start of the Roth IRA period if that is earlier than the period otherwise established by the IRA's own contributions.

These clocks should therefore be modeled as independent state variables with explicit relationships at rollover boundaries.

I would also make the following distinction:

| Clock | What it governs                                           | Scope                        |
| ----- | --------------------------------------------------------- | ---------------------------- |
| A     | 10% conversion recapture penalty                          | Each taxable conversion year |
| B     | Qualified Roth IRA distribution eligibility               | Taxpayer's Roth IRAs         |
| C     | Qualified designated Roth 401(k) distribution eligibility | Applicable workplace plan    |

And don't describe Clock A as five full years after the transaction. It is a five-taxable-year period beginning on January 1 of the conversion year.

For example, a 2026 conversion's five-taxable-year period runs from January 1, 2026, through December 31, 2030.

Source:&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.law.cornell.edu\&sz=32)

LII / Legal Information Institute+2

### 1.5 The 401(k) annual additions formula is incomplete

Your formula:

\\[ \text{Mega Backdoor Capacity} = \min(100\\%\text{ Comp},72,000) -\text{Employee Deferrals} -\text{Employer Contributions} \\]

Needs two qualifications.

First, employee elective deferrals that count toward §415(c) exclude catch-up contributions.

Second, annual additions include employer matching contributions, nonelective contributions and allocations of forfeitures, not just the match.

Also, the $72,000 limit applies to plans maintained by one employer and related employers, not necessarily to every individual plan viewed in isolation.

I'd change the formula to:

\\[ \begin{aligned} \text{MBD Capacity} = \max(0,\min(&\text{Eligible Compensation},\\\ &72,000)\\\ &-\text{Regular Elective Deferrals}\\\ &-\text{Employer Annual Additions}\\\ &-\text{Other Annual Additions}) \end{aligned} \\]

Where catch-up contributions are excluded from regular elective deferrals for this calculation.

Actual available capacity can be lower because of plan terms and nondiscrimination testing.

The IRS confirms the $72,000 limit and the components of annual additions.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.irs.gov\&sz=32)

Internal Revenue Service+1

## 2. Other substantive legal and accounting discrepancies

### 2.1 The 30-day step-transaction discussion overstates the legal conclusion

Your statement:

> Because Congress expressly recognized and affirmed the multi-step transaction, the IRS cannot apply judicial anti-abuse doctrines to override statutory intent.

I would not publish that sentence.

The 2017 conference report does recognize the contribution-then-conversion strategy. However, that does not establish that Congress immunized every conceivable implementation from judicial anti-abuse doctrines.

There is an important distinction:

- There is no statutory 30-day waiting period for a Backdoor Roth.
- There is no general IRS requirement to wait 30 days before converting a nondeductible Traditional IRA contribution.
- The conference report acknowledges the contribution-and-conversion mechanism.
- That does not establish that the IRS is categorically barred from applying general anti-abuse principles to any transaction.

Your practical recommendation to convert promptly after the contribution settles is reasonable.

But I'd replace the absolute legal assertion with:

> Neither IRC §408A nor the applicable Treasury Regulations prescribe a 30-day waiting period between a nondeductible Traditional IRA contribution and its conversion to a Roth IRA. The 2017 TCJA Conference Report also expressly discusses the contribution-then-conversion mechanism. Therefore, the commonly repeated 30-day waiting requirement has no identified statutory or regulatory basis.

This is more defensible and still makes your point.

### 2.2 Your Pro-Rata example is correct, but the formula needs to be identified as a simplified Form 8606 model

Your $7,500 / $100,000 example is correct.

The resulting calculation:

- Nontaxable: $562.50
- Taxable: $6,937.50

is right under the assumptions you specify.

However, I would explicitly tie the formula to Form 8606, Part I.

The denominator isn't simply a generic pool of IRA assets. It is constructed from the year-end value of applicable traditional IRAs, relevant distributions, and conversions, subject to the form's specific adjustments.

Also, the numerator is the taxpayer's applicable cumulative nondeductible IRA basis, not necessarily just the contribution made that year.

The current presentation is fine as an introductory example, but your eventual implementation should model the actual Form 8606 computation rather than this simplified equation.

Sources:&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.irs.gov\&sz=32)

Internal Revenue Service+1

### 2.3 The Roth 401(k) pro-rata description needs one additional distinction

Your statement that a nonqualified Roth 401(k) distribution is pro-rata between basis and earnings is correct.

However, a direct rollover introduces additional allocation rules.

For example, if a nonqualified designated Roth account distribution is $14,000, consisting of $11,000 basis and $3,000 earnings, and $7,000 is rolled into a Roth IRA, the rollover is generally deemed to consist first of the $3,000 earnings and then $4,000 of basis.

That can result in a tax-free rollover without current income inclusion.

This is an important distinction if your engine is eventually going to simulate rollover transactions.

Source:&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.law.cornell.edu\&sz=32)

LII / Legal Information Institute+1

### 2.4 Your claim about state tax immunity is too absolute

Section 1.1 says:

> Every US state with an income tax (including California and New York) grants permanent tax immunity.

I would avoid making a universal state-law assertion without examining state conformity and residency circumstances.

The federal treatment is well established:

- Roth IRA earnings are not currently taxable to the owner merely because investments generate dividends, interest or gains inside the account.
- Qualified Roth IRA distributions are federally tax-free.

But state treatment should be expressed with appropriate qualifications.

I'd write:

> Roth IRA earnings generally receive corresponding tax-deferred or tax-free treatment under state income tax systems that conform to the relevant federal provisions. State-specific rules and residency circumstances should be evaluated separately.

Also, your taxable brokerage comparison needs a small correction:

- Selling an appreciated investment can trigger capital gains tax.
- Selling at a loss does not trigger capital gains tax.
- Reinvested dividends can still be taxable in the year received.

You currently imply that every rebalance creates a tax liability, which isn't true.

### 2.5 The claim that Mega Backdoor principal is unconditionally liquid needs a qualification

Your explanation is fundamentally sound, but there's a distinction between:

- The tax classification of the money after it reaches a Roth IRA.
- The ability to access the money while it remains inside the employer plan.

You do explain the distinction in Section 3.3, but some of the earlier tables say simply:

> 100% Liquid

I'd use:

> 100% liquid under Roth IRA distribution ordering once the rollover is completed; subject to plan distribution and rollover restrictions before that point.

Also, the special treatment of the designated Roth account rollover is not limited to the original after-tax contributions in all circumstances. A qualified distribution can make the entire rolled-over amount regular contribution basis, including earnings.

That is actually an interesting feature of your accounting model and deserves more prominence.

### 2.6 The Backdoor Roth contribution and conversion years need separate timestamps

This is an important omission for the eventual domain model.

A taxpayer can:

- Make a Traditional IRA contribution in January 2027 designated for tax year 2026.
- Convert that money to a Roth IRA in January 2027.

The contribution belongs to tax year 2026.

The conversion belongs to tax year 2027.

These are separate tax events.

Your current architecture talks about conversion years and calendar-year ordering, but doesn't explicitly introduce the distinction between:

`contribution_tax_year`

and

`conversion_tax_year`

That distinction is essential for a real accounting engine, particularly when dealing with Form 8606, basis carryforwards, and the five-year conversion recapture clock.

I'd make it an explicit property of every transaction.

### 2.7 The earnings classification in Section 3.4 needs more careful wording

You say:

> 100% of the converted amount is added to your taxable income.

That is true when the source capital is entirely pre-tax.

But a Traditional IRA can contain nondeductible basis. In that case, the conversion is not necessarily 100% taxable because of the IRA aggregation and pro-rata rules.

Similarly, an eligible workplace plan distribution can contain after-tax basis.

I'd change this to:

> The taxable portion of the conversion is included in ordinary income for the conversion year. For entirely pre-tax source capital, this generally means the full converted amount. Where the source contains after-tax basis, the taxable portion must be calculated under the applicable basis-allocation rules.

This avoids accidentally teaching readers that every conversion is fully taxable.

### 2.8 The qualified distribution definition needs to mention its exceptions

Section 1.1 defines qualified maturity as:

> Age >= 59½ and the 5-tax-year holding period.

That is the most common route, but not the complete statutory definition.

The other qualifying events include:

- Death.
- Disability.
- Certain first-time homebuyer distributions, subject to the statutory $10,000 lifetime limit.

The first-time homebuyer exception is particularly relevant because it's available under Roth IRA rules, but not as a qualifying event for a designated Roth 401(k) distribution.

I would introduce the general definition once, then use age 59½ as the common retirement scenario throughout the document.

Source:&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.law.cornell.edu\&sz=32)

LII / Legal Information Institute+1

## 3. Section-by-section review

Here is how I'd classify the rest of the material.

| Section                    | Assessment            | Required action                                                     |
| -------------------------- | --------------------- | ------------------------------------------------------------------- |
| 1.1 Roth container         | Mostly correct        | Qualify state-law claims and taxable brokerage comparisons          |
| 1.2 Contribution liquidity | Correct               | Distinguish regular contribution basis from earnings and exceptions |
| 1.3 Tagged layers          | Good abstraction      | Introduce year-specific conversion sub-ledgers                      |
| 1.4 Income limits          | Correct               | Add compensation eligibility and qualifying plan caveats            |
| 2.1 Four myths             | Mostly correct        | Fix FIFO explanation and qualify the MBD rollover statement         |
| 2.2 Narrative prose        | Conceptually strong   | No substantive correction                                           |
| 2.3 Systems formulation    | Strong                | Refine three-clock and queue definitions                            |
| 3.1 Direct contribution    | Mostly correct        | Refine excess-contribution scenario                                 |
| 3.2 Backdoor Roth          | Good                  | Fix step-transaction language and pro-rata implementation           |
| 3.3 Mega Backdoor          | Important corrections | Fix catch-up limits, Q&A citation, and plan-specific assumptions    |
| 3.4 Pre-tax conversions    | Mostly correct        | Distinguish taxable conversions from ordinary rollovers             |
| 3.5 Ingestion matrix       | Needs revision        | Propagate corrected classifications and liquidity conditions        |

### Section 1.2 — Contribution basis

Your $30,000 contribution / $42,000 account example is correct.

The important nuance is that Roth IRA distributions are aggregated across all of an individual's Roth IRAs.

You should explicitly state that the $30,000 is the taxpayer's cumulative remaining regular contribution basis, not necessarily the amount contributed to one particular brokerage account.

Also, the statement that earnings remain restricted until age 59½ is too absolute. Nonqualified earnings distributions can be made earlier, but may incur ordinary income tax and the 10% additional tax, subject to exceptions.

### Section 1.4 — High-earner paradox

Your 2026 numbers are correct:

| Filing status                                | 2026 MAGI phaseout |
| -------------------------------------------- | ------------------ |
| Single / Head of Household                   | $153k–$168k       |
| Married Filing Jointly                       | $242k–$252k       |
| Married Filing Separately, lived with spouse | $0–$10k           |

The IRA contribution limit is also correct at $7,500, or $8,600 for people aged 50 or older.

One wording issue: you say the backdoor and mega backdoor pipelines have zero income limits.

That is broadly right, but the Mega Backdoor also depends on employer plan provisions, annual additions limits, and nondiscrimination restrictions.

Sources:&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.irs.gov\&sz=32)

Internal Revenue Service+2

### Section 2.1 — The four myths

I particularly like this section.

Myth 4 is a useful way to introduce taxpayer-level aggregation.

I'd strengthen the explanation with one distinction:

The IRS aggregates Roth IRAs for ordering purposes, but that doesn't mean custodians maintain one literal shared account or that all Roth IRA assets are held together.

Your software abstraction is a logical ledger, not a claim about the custodian's physical accounting architecture.

### Section 3.1 — Excess contributions

There is a small overstatement:

> A mid-year promotion, signing bonus, or stock spike pushes their MAGI above the ceiling, that contribution becomes an excess contribution.

Not necessarily the entire contribution.

The Roth IRA contribution limit is reduced progressively across the phaseout band. An excess exists to the extent the actual contribution exceeds the recalculated allowable contribution.

Also, MAGI is determined for the entire tax year. A promotion or RSU vesting event is simply one factor affecting the final annual MAGI.

### Section 3.2 — Reverse rollover

The reverse rollover explanation is good.

One improvement: say that the rollover must remove all relevant pre-tax IRA balances before the applicable December 31 snapshot.

The remaining nondeductible basis is not eligible for rollover into an ordinary pre-tax employer plan.

The receiving employer plan must also accept the eligible incoming rollover.

### Section 3.3 — The strategic ordering recommendation

This is an interesting insight:

> Mega Backdoor should often be funded before the standard Backdoor Roth.

I agree that your accounting model establishes a legitimate reason for this ordering preference.

A Mega Backdoor rollover's investment-in-contract portion can become Tier 1, while a clean Backdoor Roth generally enters Tier 2b.

That means the former is not subject to Tier 2 head-of-line blocking.

However, I'd avoid saying it is strictly superior in general.

The comparison assumes:

- The employer plan supports in-plan Roth conversion.
- The plan allows the relevant rollover, potentially while employed.
- The individual can tolerate the plan's restrictions until rollover.
- The plan's investment choices and costs are acceptable.
- The individual values early access to Roth IRA contribution basis.

For an employee with a large existing taxable conversion queue, the advantage is particularly interesting.

I'd preserve this as a strategic insight, but qualify the recommendation.

## 4. One important conceptual improvement: your ledger needs more than three tiers

I think the biggest opportunity for improving the architecture is here.

Your three-tier model is good as a presentation abstraction:

- Tier 1: Regular contribution basis.
- Tier 2: Conversion contributions.
- Tier 3: Earnings.

But I would not implement the actual accounting engine with only three undifferentiated balance buckets.

I'd introduce a more detailed internal representation.

Proposed taxpayer-level ledger

Tier 1 — Regular contribution equivalent

Priority 1

- Direct Roth IRA contributions.
- Eligible designated Roth account rollover basis.
- Qualified designated Roth account rollover amounts.

Tier 2 — Conversion contributions

Priority 2

Year-specific tranche: 2024

- Taxable conversion principal (2a)
- Nontaxable conversion basis (2b)

Year-specific tranche: 2025

- Taxable conversion principal (2a)
- Nontaxable conversion basis (2b)

Year-specific tranche: 2026

- Taxable conversion principal (2a)
- Nontaxable conversion basis (2b)

FIFO across years; taxable portion first within each year.

Tier 3 — Earnings

Priority 3

- Investment appreciation.
- Dividends and interest.
- Earnings included in designated Roth rollovers under the applicable ordering rules.

Orthogonal metadata

- Source transaction and originating account.
- Contribution tax year.
- Conversion tax year.
- Taxable amount at conversion.
- Nontaxable basis.
- Applicable five-year clock.
- Remaining principal.

This separates two things that should not be conflated:

1. The statutory classification of capital.
2. The metadata necessary to calculate its distribution treatment.

For example, a $50,000 conversion need not be a single indivisible object. It can contain $45,000 taxable principal and $5,000 nontaxable basis.

Those amounts have different penalty consequences, even though they belong to the same conversion-year tranche.

This is where your engineering analogy becomes genuinely powerful.

## 5. A few claims I'd deliberately tone down

There are three phrases I'd reconsider because they create unnecessary legal exposure.

| Current wording                                      | My recommendation                                                               |
| ---------------------------------------------------- | ------------------------------------------------------------------------------- |
| "The IRS cannot apply judicial anti-abuse doctrines" | "No statutory or regulatory 30-day waiting requirement has been identified."    |
| "Permanent tax immunity across every US state"       | "Generally tax-free under federal law, subject to applicable state rules."      |
| "Mega Backdoor is strictly superior"                 | "Can offer a superior withdrawal-ordering position under specified conditions." |

I'd also reconsider:

> Retail personal finance blogs almost universally advise...

This isn't necessary to establish your technical point. Your argument is stronger when it stands on the statutory mechanics rather than a broad characterization of other writers.

## 6. What I'd add before proceeding to the domain model

I wouldn't expand Sections 1–3 much further. They're already substantial.

Instead, I'd add four explicit invariants to the end of Section 3.

Invariant 1 — Taxpayer aggregation

All Roth IRAs belonging to an individual are aggregated for Roth IRA distribution ordering. Custodian boundaries do not create independent ordering queues.

Invariant 2 — Conversion-year ordering

Conversion contributions are dequeued FIFO by conversion tax year. Within a given year, taxable amounts precede nontaxable amounts.

Invariant 3 — Basis provenance

Taxable and nontaxable portions of a conversion must retain separate balances and penalty metadata. A conversion's gross amount alone is insufficient to determine withdrawal treatment.

Invariant 4 — Account-type boundaries

A designated Roth 401(k) and a Roth IRA have different distribution rules. A rollover between them is a state transition that can change the ordering classification of the transferred capital.

These four invariants will give Section 4 a much stronger foundation.

## 7. My assessment of the document itself

# Assessment of v0.1

Conceptual architecture

Strong

Taxpayer ledger, provenance tagging, queues and clocks are a useful unifying abstraction.

Statutory correctness

Needs revision

Several important details need correction, especially FIFO semantics, rollover classification and five-year periods.

Numerical correctness

Needs revision

2026 catch-up limits and the §415(c) calculation need correction.

Engineering communication

Strong

The progression from motivation to ingestion adapters to accounting primitives is effective.

Ready for publication

Not yet

### My broader observation

I think the most valuable contribution here isn't the explanation of Backdoor Roth mechanics.

There are already plenty of articles explaining those mechanics.

The more interesting contribution is the attempt to unify four apparently different funding strategies into a single accounting model, and then use that model to reason about future withdrawals.

That is a much more reusable framework.

For example, an engineer should eventually be able to input:

- Their entire Roth IRA contribution history.
- All taxable and nontaxable conversion tranches.
- Their designated Roth 401(k) rollover history.
- Their current age and relevant account maturity dates.

And ask:

"If I withdraw $40,000 today, what exactly happens to each dollar, and what are the federal tax and penalty consequences?"

Your system should be able to answer that deterministically, with an explanation of the statutory rule behind each result.

That's a worthwhile engineering specification.

My recommendation: Fix the five major architectural/statutory issues first, then complete the domain model and state transitions. Don't spend time polishing prose yet. The ledger's correctness matters much more than the document's presentation at this stage.

One final point: I'd make a distinction throughout the document between verified statutory rules, administrative interpretations, and engineering abstractions. That will make this considerably more credible when CPAs and EAs start reviewing it.

The primary references I'd keep close while developing the next sections are:

- [Treasury Regulation §1.408A-6 — Roth IRA distributions](https://www.law.cornell.edu/cfr/text/26/1.408A-6?utm_source=chatgpt.com).
- [Treasury Regulation §1.408A-10 — Designated Roth account rollovers](https://www.law.cornell.edu/cfr/text/26/1.408A-10?utm_source=chatgpt.com).
- [Treasury Regulation §1.402A-1 — Designated Roth accounts](https://www.law.cornell.edu/cfr/text/26/1.402A-1?utm_source=chatgpt.com).
- [IRS Form 8606 instructions](https://www.irs.gov/instructions/i8606?utm_source=chatgpt.com).
- [IRS 401(k) contribution limits](https://www.irs.gov/retirement-plans/plan-participant-employee/retirement-topics-401k-and-profit-sharing-plan-contribution-limits?utm_source=chatgpt.com).
- [IRS guidance on after-tax 401(k) rollovers](https://www.irs.gov/retirement-plans/rollovers-of-after-tax-contributions-in-retirement-plans?utm_source=chatgpt.com).

This is a review of the material supplied through Section 3.5, not a complete tax opinion or an audit of the eventual implementation.
