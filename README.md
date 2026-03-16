# SolarFlow: The 15-Minute Business Engine

**Your complete sales operations kit for residential solar contracting.**

---

## Quick Start

Get up and running in three steps:

### Step 1: Install Python (if needed)

The quote builder requires Python 3.8 or higher. Check if it's already installed:

```bash
python --version
```

If you don't have Python, download it free from [python.org](https://www.python.org/downloads/). During installation on Windows, check the box that says **"Add Python to PATH."**

### Step 2: Run Your First Quote

You have two options — a desktop GUI or a command-line tool. Both produce the same professional quote.

**Option A: Desktop App (recommended)**

Double-click or run:

```bash
python SolarFlow_App.py
```

A window will open with labeled input fields. Fill them in, click **"Generate Professional Quote"**, and your quote is saved.

**Option B: Command Line**

```bash
python quote_builder.py
```

The script will walk you through entering the customer's details in the terminal.

Both save your finished quote as `[CustomerName]_SolarQuote.txt` in the same folder.

### Step 3: Send Your First Follow-Up Email

1. Open `EMAIL_TEMPLATES.md`
2. Copy **Template 1: Post-Visit Thank You**
3. Replace the `[BRACKETED]` placeholders with the homeowner's details
4. Paste into your email client and send

That's it. You're running SolarFlow.

---

## Using the Desktop App (`SolarFlow_App.py`)

The desktop app is the easiest way to generate quotes. Launch it with:

```bash
python SolarFlow_App.py
```

A professional window opens with labeled fields for all inputs. Fill in the customer details, system specs, and financing terms, then click **"Generate Professional Quote."** The app validates your entries, runs the calculations, saves the quote file, and shows a success message with the key numbers.

The app uses the same accounting logic as the command-line tool — same ITC calculation, same PMT formula, same output file.

---

## Using the Command-Line Tool (`quote_builder.py`)

### What It Does

The quote builder generates a professional solar proposal from a few simple inputs. It calculates costs, tax credits, financing, and estimated savings automatically.

### Inputs You'll Provide

| Input | Example | Notes |
|-------|---------|-------|
| Customer name | Jane Smith | Used in the proposal header |
| Street address | 123 Oak Lane, Austin, TX | Installation address |
| System size (kW) | 8.5 | Based on your site assessment |
| Number of panels | 22 | Based on your design |
| Cost per watt ($) | 3.00 | Your company's pricing |
| Annual energy production (kWh) | 12,750 | From your PVWatts or shade analysis |
| Utility rate ($/kWh) | 0.13 | Customer's current electric rate |
| Financing term (months) | 240 | Loan term (e.g., 120, 180, 240) |
| Financing APR (%) | 5.99 | Interest rate from your lending partner |

### What the Quote Includes

- **Gross System Cost** — System size × cost per watt × 1,000
- **Federal ITC Estimate** — 30% of gross cost (current rate as of 2024–2032)
- **Net Cost After ITC** — What the homeowner actually pays after claiming the credit
- **Estimated Monthly Payment** — Based on the net cost, term, and APR you provide
- **Estimated Year-1 Savings** — Annual production × utility rate
- **Simple Payback Period** — Net cost ÷ annual savings

### Customization

The script is a single Python file with no external dependencies. You can open it in any text editor to:

- Add your company name and logo path to the header
- Adjust the default ITC percentage if legislation changes
- Modify the output format

---

## Email Templates

SolarFlow includes five follow-up email templates in `EMAIL_TEMPLATES.md`. Each is designed for a specific stage of the residential solar sales cycle.

| # | Template | When to Send |
|---|----------|-------------|
| 1 | Post-Visit Thank You | Within 2 hours of leaving the home |
| 2 | Quote Sent Nudge | 24 hours after sending the proposal |
| 3 | Financing & Tax Credit Breakdown | 72 hours after the proposal |
| 4 | Social Proof & Urgency | 7 days after the proposal |
| 5 | Final Outreach & Reassurance | 14 days after the proposal |

### How to Use Them

1. Open `EMAIL_TEMPLATES.md`
2. Find the template matching your follow-up stage
3. Copy the entire template
4. Replace every `[BRACKETED PLACEHOLDER]` with the real information
5. Paste into Gmail, Outlook, or your preferred email client
6. Review once, then send

All placeholders are clearly marked. Most templates take under 60 seconds to personalize.

---

## Daily Workflow

Run through this checklist every morning before you start driving to job sites:

- [ ] **New leads from yesterday** — Run `quote_builder.py` for each and send proposals
- [ ] **24-hour follow-ups** — Send Template 2 to anyone who received a quote yesterday
- [ ] **72-hour follow-ups** — Send Template 3 to anyone approaching the 3-day mark
- [ ] **7-day follow-ups** — Send Template 4 to anyone at the one-week mark
- [ ] **14-day follow-ups** — Send Template 5 as a final touchpoint
- [ ] **Cold leads** — Anyone past 14 days with no response moves to your monthly re-engagement list

**Time required: 15 minutes.**

---

## File Overview

```
solarflow/
├── SolarFlow_App.py       # Desktop GUI application
├── quote_builder.py       # Command-line quote tool
├── EMAIL_TEMPLATES.md     # 5 follow-up email templates
├── PRODUCT_PAGE.md        # Product sales page (for your reference)
└── README.md              # This file
```

---

## Requirements

- Python 3.8+ (for the quote builder and desktop app)
- Tkinter (included with Python on Windows and Mac — Linux users may need `sudo apt install python3-tk`)
- Any email client (Gmail, Outlook, Yahoo Mail, etc.)
- No third-party Python packages required
- Works on Windows, Mac, and Linux

---

## Legal Disclaimer

### Regarding the Federal Investment Tax Credit (ITC)

The solar Investment Tax Credit (ITC) information referenced in SolarFlow, including the 30% credit rate, is based on provisions of the **Inflation Reduction Act of 2022** as currently enacted under **26 U.S.C. § 48** and **26 U.S.C. § 25D**.

**This product does not provide tax, legal, or financial advice.**

- The ITC is a **federal tax credit**, not a refund. Homeowners must have sufficient federal tax liability to claim the credit.
- The 30% ITC rate is scheduled for residential solar projects placed in service through **December 31, 2032**. The rate steps down to 26% in 2033 and 22% in 2034 under current law.
- State and local incentives, rebates, SRECs, and net metering policies vary by jurisdiction and are **not calculated** by the SolarFlow quote builder.
- Tax credit eligibility depends on individual taxpayer circumstances. **Always advise homeowners to consult a qualified tax professional** before making financial decisions based on ITC estimates.
- Legislative changes at the federal or state level may alter incentive availability, credit percentages, or eligibility requirements at any time.

**You, the contractor, are responsible for ensuring all representations made to homeowners about tax credits, savings, and financing are accurate and compliant with applicable federal, state, and local regulations, including FTC guidelines on advertising and consumer protection.**

SolarFlow is a productivity tool. It is not a substitute for professional tax counsel, legal advice, or certified financial planning.

---

## Support

If you have questions about using SolarFlow, refer back to this README or reach out through the Gumroad product page where you purchased this kit.

---

*SolarFlow: The 15-Minute Business Engine — Stop quoting. Start closing.*
