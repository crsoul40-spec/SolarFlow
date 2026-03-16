"""
SolarFlow App — Professional Quote Generator
=============================================
Tkinter GUI for generating residential solar proposals.
Uses the same accounting logic as quote_builder.py.
No external dependencies — standard library only.
"""

import re
import tkinter as tk
from tkinter import messagebox
from datetime import datetime


# ---------------------------------------------------------------------------
# Configuration — edit these defaults to match your company
# ---------------------------------------------------------------------------
COMPANY_NAME = "Your Solar Company"
COMPANY_PHONE = "(555) 000-0000"
COMPANY_EMAIL = "info@yourcompany.com"
COMPANY_WEBSITE = "www.yourcompany.com"

ITC_RATE = 0.30
PANEL_WATTAGE = 400
SYSTEM_WARRANTY_YEARS = 25

# Theme colors
PRIMARY_BLUE = "#1565C0"
DARK_BLUE = "#0D47A1"
LIGHT_BLUE = "#E3F2FD"
ACCENT_BLUE = "#42A5F5"
WHITE = "#FFFFFF"
DARK_TEXT = "#212121"
SUBTLE_TEXT = "#757575"


# ---------------------------------------------------------------------------
# Accounting logic (matches quote_builder.py)
# ---------------------------------------------------------------------------

def calculate_monthly_payment(principal, annual_rate_pct, term_months):
    """PMT formula: P = r(PV) / (1 - (1 + r)^-n)"""
    if annual_rate_pct == 0:
        return principal / term_months
    r = annual_rate_pct / 100 / 12
    return (r * principal) / (1 - (1 + r) ** -term_months)


def currency(value):
    return f"${value:,.2f}"


def make_filename(customer_name):
    cleaned = re.sub(r"[^a-zA-Z0-9]", "", customer_name)
    return f"{cleaned}_SolarQuote.txt"


def run_calculations(data):
    gross_cost = data["system_kw"] * data["cost_per_watt"] * 1000
    itc_amount = gross_cost * ITC_RATE
    net_cost = gross_cost - itc_amount

    monthly_payment = calculate_monthly_payment(
        net_cost, data["apr"], data["term_months"]
    )
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


def render_quote(q):
    divider = "=" * 60
    thin = "-" * 60
    lines = [
        divider,
        f"  {COMPANY_NAME}".center(60),
        "  Solar Energy Proposal".center(60),
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
# GUI Application
# ---------------------------------------------------------------------------

class SolarFlowApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SolarFlow - Professional Quote Generator")
        self.root.configure(bg=WHITE)
        self.root.resizable(False, False)

        # Center window on screen
        window_width, window_height = 520, 720
        x = (self.root.winfo_screenwidth() // 2) - (window_width // 2)
        y = (self.root.winfo_screenheight() // 2) - (window_height // 2)
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.entries = {}
        self._build_ui()

    def _build_ui(self):
        # -- Header banner --
        header = tk.Frame(self.root, bg=PRIMARY_BLUE, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header, text="SolarFlow", font=("Segoe UI", 22, "bold"),
            bg=PRIMARY_BLUE, fg=WHITE,
        ).pack(pady=(14, 0))

        tk.Label(
            header, text="Professional Quote Generator",
            font=("Segoe UI", 10), bg=PRIMARY_BLUE, fg=LIGHT_BLUE,
        ).pack()

        # -- Scrollable form area --
        form_outer = tk.Frame(self.root, bg=WHITE)
        form_outer.pack(fill="both", expand=True, padx=30, pady=(15, 0))

        # Section: Customer Information
        self._section_label(form_outer, "Customer Information")
        self._add_field(form_outer, "Customer Name", "customer_name")
        self._add_field(form_outer, "Street Address", "address")

        # Section: System Design
        self._section_label(form_outer, "System Design")
        row = tk.Frame(form_outer, bg=WHITE)
        row.pack(fill="x", pady=(0, 2))
        self._add_field(row, "System Size (kW)", "system_kw", side="left")
        self._add_field(row, "Number of Panels", "num_panels", side="right")

        # Section: Pricing
        self._section_label(form_outer, "Pricing")
        self._add_field(form_outer, "Cost per Watt ($)", "cost_per_watt", default="3.00")

        # Section: Energy Production
        self._section_label(form_outer, "Energy Production")
        row2 = tk.Frame(form_outer, bg=WHITE)
        row2.pack(fill="x", pady=(0, 2))
        self._add_field(row2, "Annual Production (kWh)", "annual_kwh", side="left")
        self._add_field(row2, "Utility Rate ($/kWh)", "utility_rate", default="0.13", side="right")

        # Section: Financing Terms
        self._section_label(form_outer, "Financing Terms")
        row3 = tk.Frame(form_outer, bg=WHITE)
        row3.pack(fill="x", pady=(0, 2))
        self._add_field(row3, "Loan Term (months)", "term_months", default="240", side="left")
        self._add_field(row3, "Loan APR (%)", "apr", default="5.99", side="right")

        # -- Generate button --
        btn_frame = tk.Frame(self.root, bg=WHITE)
        btn_frame.pack(fill="x", padx=30, pady=(10, 5))

        self.generate_btn = tk.Button(
            btn_frame,
            text="Generate Professional Quote",
            font=("Segoe UI", 13, "bold"),
            bg=PRIMARY_BLUE, fg=WHITE,
            activebackground=DARK_BLUE, activeforeground=WHITE,
            relief="flat", cursor="hand2",
            height=2,
            command=self._generate_quote,
        )
        self.generate_btn.pack(fill="x", ipady=2)
        self.generate_btn.bind("<Enter>", lambda e: self.generate_btn.config(bg=DARK_BLUE))
        self.generate_btn.bind("<Leave>", lambda e: self.generate_btn.config(bg=PRIMARY_BLUE))

        # -- Footer --
        footer = tk.Frame(self.root, bg=LIGHT_BLUE, height=35)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        tk.Label(
            footer,
            text="SolarFlow: The 15-Minute Business Engine",
            font=("Segoe UI", 8), bg=LIGHT_BLUE, fg=SUBTLE_TEXT,
        ).pack(pady=8)

    def _section_label(self, parent, text):
        frame = tk.Frame(parent, bg=WHITE)
        frame.pack(fill="x", pady=(12, 4))
        tk.Label(
            frame, text=text, font=("Segoe UI", 10, "bold"),
            bg=WHITE, fg=PRIMARY_BLUE, anchor="w",
        ).pack(fill="x")
        tk.Frame(frame, bg=ACCENT_BLUE, height=2).pack(fill="x", pady=(2, 0))

    def _add_field(self, parent, label, key, default="", side=None):
        if side:
            container = tk.Frame(parent, bg=WHITE)
            container.pack(side="left", fill="x", expand=True, padx=(0, 5 if side == "left" else 0))
        else:
            container = tk.Frame(parent, bg=WHITE)
            container.pack(fill="x", pady=(0, 2))

        tk.Label(
            container, text=label, font=("Segoe UI", 9),
            bg=WHITE, fg=DARK_TEXT, anchor="w",
        ).pack(fill="x")

        entry = tk.Entry(
            container, font=("Segoe UI", 10),
            relief="solid", bd=1,
            highlightcolor=ACCENT_BLUE, highlightthickness=1,
        )
        entry.pack(fill="x", ipady=4)
        if default:
            entry.insert(0, default)

        self.entries[key] = entry

    def _generate_quote(self):
        # Validate and collect inputs
        try:
            customer_name = self.entries["customer_name"].get().strip()
            address = self.entries["address"].get().strip()

            if not customer_name:
                messagebox.showwarning("Missing Field", "Please enter the customer name.")
                return
            if not address:
                messagebox.showwarning("Missing Field", "Please enter the street address.")
                return

            system_kw = float(self.entries["system_kw"].get())
            num_panels = int(self.entries["num_panels"].get())
            cost_per_watt = float(self.entries["cost_per_watt"].get())
            annual_kwh = float(self.entries["annual_kwh"].get())
            utility_rate = float(self.entries["utility_rate"].get())
            term_months = int(self.entries["term_months"].get())
            apr = float(self.entries["apr"].get())
        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Please check that all numeric fields contain valid numbers."
            )
            return

        if system_kw <= 0 or num_panels <= 0 or cost_per_watt <= 0:
            messagebox.showerror(
                "Invalid Input",
                "System size, panel count, and cost per watt must be greater than zero."
            )
            return

        # Run calculations
        data = {
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

        results = run_calculations(data)
        quote_text = render_quote(results)

        # Save file
        filename = make_filename(customer_name)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(quote_text)

        # Show success message
        messagebox.showinfo(
            "Quote Generated",
            f"Quote saved successfully!\n\n"
            f"File: {filename}\n\n"
            f"Gross Cost: {currency(results['gross_cost'])}\n"
            f"ITC (30%): -{currency(results['itc_amount'])}\n"
            f"Net Cost: {currency(results['net_cost'])}\n"
            f"Monthly Payment: {currency(results['monthly_payment'])}/mo\n"
            f"Annual Savings: {currency(results['annual_savings'])}\n"
            f"Payback: {results['payback_years']:.1f} years"
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = SolarFlowApp(root)
    root.mainloop()
