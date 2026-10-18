Here's a refined prompt that will get Claude to think like a solution architect and build a scalable navigation framework for future planning modules.

# Integrate Intro Presentation With Trust Detail Homepage

We now have two primary presentation files:

## File 1 (Primary Entry Point)
- Ihab_Shahawi_Intro.html

This is the main presentation and landing page that will be used during the client meeting.

## File 2 (Trust Knowledge Center)
- Estate_Trust_Info_Live_HomePage.html

This contains the detailed trust explanations, examples, asset recommendations, trustee structures, beneficiary illustrations, trust diagrams, and implementation details for the Shahawi family.

---

# Overall Objective

The Intro presentation should function as the executive summary.

The Trust homepage should function as the detailed reference library.

The client journey should be:

Ihab_Shahawi_Intro.html
↓
Trust recommendation appears
↓
Client clicks trust
↓
Estate_Trust_Info_Live_HomePage.html opens
↓
The exact trust section opens automatically
↓
User sees the detailed family-specific example

The experience should feel seamless and integrated.

---

# Specific Tasks

## 1. Trust Recommendation Synchronization

Review Page 4 of:

Ihab_Shahawi_Intro.html

Identify every trust recommendation displayed, including:

- Revocable Living Trust
- ILIT
- SLAT
- Dynasty Trust
- GST Trust
- CRT
- CLAT
- Family Legacy Trust
- Any additional trust recommendations

For every trust shown on Page 4:

Verify that a corresponding detailed example exists inside:

Estate_Trust_Info_Live_HomePage.html

If not present:

Create the missing trust section.

---

## 2. Deep Linking

Each trust box on Page 4 should become clickable.

Example:

- Click SLAT
→ Open Estate_Trust_Info_Live_HomePage.html#slat-example

- Click ILIT
→ Open Estate_Trust_Info_Live_HomePage.html#ilit-example

- Click Dynasty Trust
→ Open Estate_Trust_Info_Live_HomePage.html#dynasty-example

Each trust section should have a permanent anchor ID.

---

## 3. Context Synchronization

When the trust page opens:

The user should immediately see:

### Trust Summary Banner

Include:

- Trust name
- Recommended assets
- Approximate value of assigned assets
- Primary beneficiaries
- Planning purpose

Example:

SLAT
Recommended Funding:
$4.2M Commercial Real Estate
$1.5M Brokerage Assets

Beneficiaries:
Vivian
Children

Purpose:
Estate reduction, asset protection, family flexibility

This should match the recommendation shown on Page 4.

---

## 4. Create a Trust Recommendation Matrix

Add a section near Page 2 of:

Estate_Trust_Info_Live_HomePage.html

called:

# Recommended Trust Structure for the Shahawi Family

Create a chart:

| Trust | Purpose | Assets Assigned | Beneficiaries | Priority |
|---------|---------|---------|---------|---------|

The chart should exactly match the recommendations shown on Page 4 of the Intro presentation.

This becomes the synchronization layer between the Intro presentation and the detailed trust pages.

---

## 5. Trust Navigation Dashboard

At the top of Estate_Trust_Info_Live_HomePage.html create a navigation dashboard.

Example:

Trust Overview
├── Revocable Trust
├── ILIT
├── SLAT
├── Dynasty Trust
├── GST Trust
├── CRT
├── CLAT
├── Family Legacy Trust
├── Life Insurance Examples
├── Rockefeller Waterfall
└── Asset Protection

Each menu item should jump directly to the section.

---

## 6. Future Expansion Architecture

Please implement the navigation structure so future planning modules can easily be added.

We anticipate future pages such as:

### Asset Protection
Asset_Protection_HomePage.html

### Retirement Planning
Retirement_Planning_HomePage.html

### Business Succession
Business_Succession_HomePage.html

### Tax Planning
Tax_Strategy_HomePage.html

Build a scalable framework where:

Intro Page
│
├── Trust Planning
├── Asset Protection
├── Retirement Planning
├── Tax Planning
├── Business Succession
└── Charitable Planning

The trust page should follow this architecture and be ready for future modules.

---

# User Experience Goal

The client should be able to:

1. Start at Ihab_Shahawi_Intro.html
2. See the recommended trust architecture
3. Click on any trust
4. Open the detailed family-specific explanation
5. Navigate back easily
6. Explore related planning concepts

The experience should resemble a modern interactive family-office portal rather than a static presentation.

---

# Design Requirements

Use:

- Consistent color scheme across both files
- Identical trust names
- Consistent terminology
- Shared icons
- Shared visual language
- Responsive design

Maintain continuity between the Intro page and the Estate_Trust_Info_Live_HomePage.

The client should feel they are moving deeper into the same planning system, not opening a separate document.


This version tells Claude not merely to link pages, but to create a modular family-office planning portal where the Intro page becomes the dashboard and Trust, Asset Protection, Retirement, Tax, and Succession become expandable knowledge centers. That architecture will serve you well as you continue adding planning modules for Ihab.