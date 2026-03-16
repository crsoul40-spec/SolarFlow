"""
SolarFlow Quote Builder
=======================
Generates professional residential solar proposals from the command line.
No external dependencies — runs on Python 3.8+ standard library only.
"""

import math
import os
import re
import sys
from datetime import datetime


# ---------------------------------------------------------------------------
# Configuration — edit these defaults to match your company
# ---------------------------------------------------------------------------
COMPANY_NAME = "Your Solar Company"
COMPANY_PHONE = "(555) 000-0000"
COMPANY_EMAIL = "info@yourcompany.com"
COMPANY_WEBSITE = "www.yourcompany.com"

ITC_RATE = 0.30            # Federal Investment Tax Credit (30% through 2032)
DEFAULT_COST_PER_WATT = 3.00
DEFAULT_FINANCING_TERM = 240   # months
DEFAULT_FINANCING_APR = 5.99   # percent
DEFAULT_UTILITY_RATE = 0.13    # $/kWh
PANEL_WATTAGE = 400            # watts per panel (used for estimate display)
SYSTEM_WARRANTY_YEARS = 25
OUTPUT_DIR = "quotes"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def prompt(label: str, default=None, cast=str, required=True) -> object:
    """Prompt the user for input with optional default and type casting."""
    suffix = f" [{default}]" if default is not None else ""
    while True:
        raw = input(f"  {label}{suffix}: ").strip()
        if not raw and default is not None:
            raw = str(default)
        if not raw:
            if required:
                print("    * This field is required.")
                continue
            return None
        try:
            return cast(raw)
        except (ValueError, TypeError):
            print(f"    * Invalid input. Expected {cast.__name__}.")


def currency(value: float) -> str:
    """Format a number as US currency."""
    return f"${value:,.2f}"


def sanitize_filename(name: str) -> str:
    """Turn a customer name into a safe filename fragment."""
    return re.sub(r"[^a-zA-Z0-9]+", "_", name).strip("_").lower()


def calculate_monthly_payment(principal: float, annual_rate: float, term_months: int) -> float:
    """Standard amortization formula for fixed monthly payment."""
    if annual_rate == 0:
        return principal / term_months
    monthly_rate = annual_rate / 100 / 12
    return principal * (monthly_rate * (1 + monthly_rate) ** term_months) / \
           ((1 + monthly_rate) ** term_months - 1)


# ---------------------------------------------------------------------------
# Input collection
# ---------------------------------------------------------------------------

def collect_inputs() -> dict:
    """Walk the user through every input field and return a dict."""
    print("\n" + "=" * 60)
    print("  SOLARFLOW QUOTE BUILDER")
    print("=" * 60)

    print("\n-- Customer Information --")
    customer_name = prompt("Customer name", cast=str)
    address = prompt("Property address", cast=str)

    print("\n-- System Design --")
    system_kw = prompt("System size (kW)", cast=float)
    num_panels = prompt("Number of panels", cast=int)

    print("\n-- Pricing --")
    cost_per_watt = prompt("Cost per watt ($)", default=DEFAULT_COST_PER_WATT, cast=float)

    print("\n-- Energy Production --")
    annual_kwh = prompt("Estimated annual production (kWh)", cast=float)
    utility_rate = prompt("Customer utility rate ($/kWh)", default=DEFAULT_UTILITY_RATE, cast=float)

    print("\n-- Financing --")
    term_months = prompt("Loan term (months)", default=DEFAULT_FINANCING_TERM, cast=int)
    apr = prompt("Loan APR (%)", default=DEFAULT_FINANCING_APR, cast=float)

    return {
        "customer_name": customer_name,
        "address": address,
        "system_kw": system_kw,
        "num_panels": num_panels,
        "cost_per_watt": cost_per_watt,
        "annual_kwh": annual_kwh,
        "utility_rate": utility_rate,
        "term_months": term_months,
        "apr": apr,
    }


# ---------------------------------------------------------------------------
# Calculations
# ---------------------------------------------------------------------------

def calculate(data: dict) -> dict:
    """Derive every output number from the raw inputs."""
    gross_cost = data["system_kw"] * data["cost_per_watt"] * 1000
    itc_amount = gross_cost * ITC_RATE
    net_cost = gross_cost - itc_amount

    monthly_payment = calculate_monthly_payment(net_cost, data["apr"], data["term_months"])
    total_financed = monthly_payment * data["term_months"]
    total_interest = total_financed - net_cost

    annual_savings = data["annual_kwh"] * data["utility_rate"]
    monthly_savings = annual_savings / 12
    payback_years = net_cost / annual_savings if annual_savings > 0 else 0

    lifetime_production = data["annual_kwh"] * SYSTEM_WARRANTY_YEARS
    lifetime_savings = annual_savings * SYSTEM_WARRANTY_YEARS

    return {
        **data,
        "gross_cost": gross_cost,
        "itc_rate_pct": int(ITC_RATE * 100),
        "itc_amount": itc_amount,
        "net_cost": net_cost,
        "monthly_payment": monthly_payment,
        "total_financed": total_financed,
        "total_interest": total_interest,
        "annual_savings": annual_savings,
        "monthly_savings": monthly_savings,
        "payback_years": payback_years,
        "lifetime_production": lifetime_production,
        "lifetime_savings": lifetime_savings,
        "date": datetime.now().strftime("%B %d, %Y"),
    }


# ---------------------------------------------------------------------------
# Quote rendering
# ---------------------------------------------------------------------------

def render_quote(q: dict) -> str:
    """Build the full text of the proposal."""
    divider = "=" * 60
    thin = "-" * 60

    lines = [
        divider,
        f"  {COMPANY_NAME}".center(60),
        f"  Solar Energy Proposal".center(60),
        divider,
        "",
        f"  Prepared for:   {q['customer_name']}",
        f"  Property:       {q['address']}",
        f"  Date:           {q['date']}",
        "",
        divider,
        "  SYSTEM OVERVIEW",
        divider,
        "",
        f"  System size:            {q['system_kw']:.2f} kW",
        f"  Number of panels:       {q['num_panels']}",
        f"  Panel wattage (est.):   {PANEL_WATTAGE} W",
        f"  Warranty coverage:      {SYSTEM_WARRANTY_YEARS} years",
        "",
        divider,
        "  PRICING & INCENTIVES",
        divider,
        "",
        f"  Gross system cost:                  {currency(q['gross_cost']):>14}",
        f"  Federal tax credit ({q['itc_rate_pct']}% ITC):      -{currency(q['itc_amount']):>13}",
        f"                                      {thin[:14]}",
        f"  Net cost after tax credit:          {currency(q['net_cost']):>14}",
        "",
        divider,
        "  FINANCING ESTIMATE",
        divider,
        "",
        f"  Loan amount:            {currency(q['net_cost'])}",
        f"  Term:                   {q['term_months']} months ({q['term_months'] // 12} years)",
        f"  APR:                    {q['apr']:.2f}%",
        f"  Monthly payment:        {currency(q['monthly_payment'])}",
        f"  Total financed:         {currency(q['total_financed'])}",
        f"  Total interest:         {currency(q['total_interest'])}",
        "",
        divider,
        "  ENERGY SAVINGS ESTIMATE",
        divider,
        "",
        f"  Annual production:      {q['annual_kwh']:,.0f} kWh",
        f"  Utility rate:           {currency(q['utility_rate'])}/kWh",
        f"  Monthly savings:        {currency(q['monthly_savings'])}",
        f"  Annual savings:         {currency(q['annual_savings'])}",
        f"  Payback period:         {q['payback_years']:.1f} years",
        "",
        f"  {SYSTEM_WARRANTY_YEARS}-Year Projections:",
        f"    Total production:     {q['lifetime_production']:,.0f} kWh",
        f"    Total savings:        {currency(q['lifetime_savings'])}",
        "",
        divider,
        "  NEXT STEPS",
        divider,
        "",
        "  1. Review this proposal and note any questions.",
        "  2. Schedule a follow-up call to discuss financing options.",
        "  3. Sign the installation agreement to lock in your pricing.",
        "  4. We handle permitting, installation, and utility interconnection.",
        "  5. Start generating clean energy from your roof.",
        "",
        divider,
        "  IMPORTANT DISCLOSURES",
        divider,
        "",
        "  * The federal Investment Tax Credit (ITC) is a tax credit, not a",
        "    refund. Consult a qualified tax professional to determine your",
        "    eligibility and how the credit applies to your tax situation.",
        "",
        "  * Energy production estimates are based on projected system output",
        "    and current utility rates. Actual results may vary due to weather,",
        "    shading, utility rate changes, and other factors.",
        "",
        "  * Financing terms shown are estimates. Final loan approval, rates,",
        "    and terms are subject to lender review and credit qualification.",
        "",
        "  * This proposal is valid for 30 days from the date above.",
        "",
        divider,
        f"  {COMPANY_NAME}",
        f"  {COMPANY_PHONE}  |  {COMPANY_EMAIL}",
        f"  {COMPANY_WEBSITE}",
        divider,
        "",
        "  Generated by SolarFlow: The 15-Minute Business Engine",
        "",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# File output
# ---------------------------------------------------------------------------

def save_quote(text: str, customer_name: str) -> str:
    """Write the proposal to a text file and return the path."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    date_stamp = datetime.now().strftime("%Y%m%d")
    filename = f"quote_{sanitize_filename(customer_name)}_{date_stamp}.txt"
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)
    return filepath


# ---------------------------------------------------------------------------
# Console summary
# ---------------------------------------------------------------------------

def print_summary(q: dict) -> None:
    """Print a compact summary to the terminal after generation."""
    print("\n" + "-" * 60)
    print("  QUOTE SUMMARY")
    print("-" * 60)
    print(f"  Customer:         {q['customer_name']}")
    print(f"  System:           {q['system_kw']:.2f} kW  ({q['num_panels']} panels)")
    print(f"  Gross cost:       {currency(q['gross_cost'])}")
    print(f"  ITC ({q['itc_rate_pct']}%):         -{currency(q['itc_amount'])}")
    print(f"  Net cost:         {currency(q['net_cost'])}")
    print(f"  Monthly payment:  {currency(q['monthly_payment'])}/mo")
    print(f"  Annual savings:   {currency(q['annual_savings'])}")
    print(f"  Payback:          {q['payback_years']:.1f} years")
    print("-" * 60)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    try:
        data = collect_inputs()
    except (KeyboardInterrupt, EOFError):
        print("\n\n  Quote cancelled.\n")
        sys.exit(0)

    results = calculate(data)
    quote_text = render_quote(results)
    filepath = save_quote(quote_text, data["customer_name"])

    print_summary(results)
    print(f"\n  Quote saved to: {filepath}")
    print("  Open the file and attach it to your proposal email.\n")


if __name__ == "__main__":
    main()
