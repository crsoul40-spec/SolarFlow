"""
SolarFlow Professional Desktop App
===================================
Tabbed Tkinter GUI with Quote Generator and Email Templates viewer.
No external dependencies beyond the standard library.
"""

import os
import re
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
COMPANY_NAME = "Your Solar Company"
COMPANY_PHONE = "(555) 000-0000"
COMPANY_EMAIL = "info@yourcompany.com"
COMPANY_WEBSITE = "www.yourcompany.com"

ITC_RATE = 0.30
PANEL_WATTAGE = 400
SYSTEM_WARRANTY_YEARS = 25

# Theme
PRIMARY_BLUE = "#1565C0"
DARK_BLUE = "#0D47A1"
LIGHT_BLUE = "#E3F2FD"
ACCENT_BLUE = "#42A5F5"
WHITE = "#FFFFFF"
DARK_TEXT = "#212121"
SUBTLE_TEXT = "#757575"
BORDER_GRAY = "#E0E0E0"


# ---------------------------------------------------------------------------
# Accounting logic
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
# Email Templates loader
# ---------------------------------------------------------------------------

def load_email_templates():
    """Load EMAIL_TEMPLATES.md from the same directory as this script."""
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    path = os.path.join(base_dir, "EMAIL_TEMPLATES.md")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return (
            "EMAIL_TEMPLATES.md not found.\n\n"
            "Place the file in the same folder as this application."
        )


def parse_templates(raw_text):
    """Split the raw markdown into individual template sections."""
    templates = []
    chunks = re.split(r"^## (Template \d+:.+)$", raw_text, flags=re.MULTILINE)

    # chunks[0] is the header text before the first template
    for i in range(1, len(chunks), 2):
        title = chunks[i].strip()
        body = chunks[i + 1].strip() if i + 1 < len(chunks) else ""
        templates.append((title, body))

    if not templates:
        templates.append(("All Templates", raw_text))

    return templates


# ---------------------------------------------------------------------------
# GUI Application
# ---------------------------------------------------------------------------

class SolarFlowGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SolarFlow v1 - Professional Quote Generator")
        self.root.configure(bg=WHITE)
        self.root.resizable(False, False)

        window_width, window_height = 600, 780
        x = (self.root.winfo_screenwidth() // 2) - (window_width // 2)
        y = (self.root.winfo_screenheight() // 2) - (window_height // 2)
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.entries = {}
        self._configure_styles()
        self._build_header()
        self._build_tabs()
        self._build_footer()

    # -- Styles --

    def _configure_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.style.configure("TNotebook", background=WHITE, borderwidth=0)
        self.style.configure(
            "TNotebook.Tab",
            background=LIGHT_BLUE, foreground=DARK_TEXT,
            font=("Segoe UI", 10, "bold"), padding=[20, 8],
        )
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", PRIMARY_BLUE)],
            foreground=[("selected", WHITE)],
        )
        self.style.configure("TFrame", background=WHITE)

    # -- Header --

    def _build_header(self):
        header = tk.Frame(self.root, bg=PRIMARY_BLUE, height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header, text="SolarFlow", font=("Segoe UI", 22, "bold"),
            bg=PRIMARY_BLUE, fg=WHITE,
        ).pack(pady=(10, 0))

        tk.Label(
            header, text="The 15-Minute Business Engine",
            font=("Segoe UI", 9), bg=PRIMARY_BLUE, fg=LIGHT_BLUE,
        ).pack()

    # -- Tabs --

    def _build_tabs(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=0, pady=0)

        # Tab 1: Quote Generator
        self.tab_quote = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_quote, text="  Quote Generator  ")
        self._build_quote_tab()

        # Tab 2: Email Templates
        self.tab_email = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_email, text="  Email Templates  ")
        self._build_email_tab()

    # -- Tab 1: Quote Generator --

    def _build_quote_tab(self):
        canvas = tk.Canvas(self.tab_quote, bg=WHITE, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab_quote, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=WHITE)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        form = tk.Frame(scroll_frame, bg=WHITE)
        form.pack(fill="x", padx=30, pady=(10, 5))

        # Customer Information
        self._section(form, "Customer Information")
        self._field(form, "Customer Name", "customer_name")
        self._field(form, "Street Address", "address")

        # System Design
        self._section(form, "System Design")
        row1 = tk.Frame(form, bg=WHITE)
        row1.pack(fill="x", pady=(0, 2))
        self._field(row1, "System Size (kW)", "system_kw", side="left")
        self._field(row1, "Number of Panels", "num_panels", side="right")

        # Pricing
        self._section(form, "Pricing")
        self._field(form, "Cost per Watt ($)", "cost_per_watt", default="3.00")

        # Energy Production
        self._section(form, "Energy Production")
        row2 = tk.Frame(form, bg=WHITE)
        row2.pack(fill="x", pady=(0, 2))
        self._field(row2, "Annual Production (kWh)", "annual_kwh", side="left")
        self._field(row2, "Utility Rate ($/kWh)", "utility_rate", default="0.13", side="right")

        # Financing
        self._section(form, "Financing Terms")
        row3 = tk.Frame(form, bg=WHITE)
        row3.pack(fill="x", pady=(0, 2))
        self._field(row3, "Loan Term (months)", "term_months", default="240", side="left")
        self._field(row3, "Loan APR (%)", "apr", default="5.99", side="right")

        # Generate button
        btn_frame = tk.Frame(scroll_frame, bg=WHITE)
        btn_frame.pack(fill="x", padx=30, pady=(15, 15))

        self.gen_btn = tk.Button(
            btn_frame, text="Generate Professional Quote",
            font=("Segoe UI", 13, "bold"),
            bg=PRIMARY_BLUE, fg=WHITE,
            activebackground=DARK_BLUE, activeforeground=WHITE,
            relief="flat", cursor="hand2", height=2,
            command=self._generate_quote,
        )
        self.gen_btn.pack(fill="x", ipady=2)
        self.gen_btn.bind("<Enter>", lambda e: self.gen_btn.config(bg=DARK_BLUE))
        self.gen_btn.bind("<Leave>", lambda e: self.gen_btn.config(bg=PRIMARY_BLUE))

    # -- Tab 2: Email Templates --

    def _build_email_tab(self):
        container = tk.Frame(self.tab_email, bg=WHITE)
        container.pack(fill="both", expand=True, padx=15, pady=10)

        # Template selector
        selector_frame = tk.Frame(container, bg=WHITE)
        selector_frame.pack(fill="x", pady=(0, 8))

        tk.Label(
            selector_frame, text="Select Template:",
            font=("Segoe UI", 10, "bold"), bg=WHITE, fg=PRIMARY_BLUE,
        ).pack(side="left", padx=(0, 10))

        self.template_var = tk.StringVar()
        raw_text = load_email_templates()
        self.templates = parse_templates(raw_text)
        template_names = [t[0] for t in self.templates]

        self.template_dropdown = ttk.Combobox(
            selector_frame, textvariable=self.template_var,
            values=template_names, state="readonly",
            font=("Segoe UI", 10), width=45,
        )
        self.template_dropdown.pack(side="left", fill="x", expand=True)
        self.template_dropdown.bind("<<ComboboxSelected>>", self._on_template_select)

        if template_names:
            self.template_dropdown.current(0)

        # Text display area
        text_frame = tk.Frame(container, bg=BORDER_GRAY, bd=1, relief="solid")
        text_frame.pack(fill="both", expand=True, pady=(0, 8))

        self.template_text = tk.Text(
            text_frame, font=("Consolas", 10), wrap="word",
            bg=WHITE, fg=DARK_TEXT, relief="flat",
            padx=12, pady=10, spacing3=2,
        )
        text_scroll = ttk.Scrollbar(text_frame, orient="vertical", command=self.template_text.yview)
        self.template_text.configure(yscrollcommand=text_scroll.set)

        text_scroll.pack(side="right", fill="y")
        self.template_text.pack(side="left", fill="both", expand=True)

        # Load first template
        if self.templates:
            self.template_text.insert("1.0", self.templates[0][1])
            self.template_text.config(state="disabled")

        # Buttons row
        btn_row = tk.Frame(container, bg=WHITE)
        btn_row.pack(fill="x")

        self.copy_btn = tk.Button(
            btn_row, text="Copy to Clipboard",
            font=("Segoe UI", 11, "bold"),
            bg=PRIMARY_BLUE, fg=WHITE,
            activebackground=DARK_BLUE, activeforeground=WHITE,
            relief="flat", cursor="hand2",
            command=self._copy_template,
        )
        self.copy_btn.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 5))
        self.copy_btn.bind("<Enter>", lambda e: self.copy_btn.config(bg=DARK_BLUE))
        self.copy_btn.bind("<Leave>", lambda e: self.copy_btn.config(bg=PRIMARY_BLUE))

        self.copy_all_btn = tk.Button(
            btn_row, text="Copy All Templates",
            font=("Segoe UI", 11),
            bg=ACCENT_BLUE, fg=WHITE,
            activebackground=PRIMARY_BLUE, activeforeground=WHITE,
            relief="flat", cursor="hand2",
            command=self._copy_all_templates,
        )
        self.copy_all_btn.pack(side="left", fill="x", expand=True, ipady=6, padx=(5, 0))
        self.copy_all_btn.bind("<Enter>", lambda e: self.copy_all_btn.config(bg=PRIMARY_BLUE))
        self.copy_all_btn.bind("<Leave>", lambda e: self.copy_all_btn.config(bg=ACCENT_BLUE))

    # -- Footer --

    def _build_footer(self):
        footer = tk.Frame(self.root, bg=LIGHT_BLUE, height=32)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        tk.Label(
            footer, text="SolarFlow v1  |  The 15-Minute Business Engine",
            font=("Segoe UI", 8), bg=LIGHT_BLUE, fg=SUBTLE_TEXT,
        ).pack(pady=7)

    # -- Form helpers --

    def _section(self, parent, text):
        frame = tk.Frame(parent, bg=WHITE)
        frame.pack(fill="x", pady=(14, 4))
        tk.Label(
            frame, text=text, font=("Segoe UI", 10, "bold"),
            bg=WHITE, fg=PRIMARY_BLUE, anchor="w",
        ).pack(fill="x")
        tk.Frame(frame, bg=ACCENT_BLUE, height=2).pack(fill="x", pady=(2, 0))

    def _field(self, parent, label, key, default="", side=None):
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

    # -- Actions --

    def _generate_quote(self):
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
                "Please check that all numeric fields contain valid numbers.",
            )
            return

        if system_kw <= 0 or num_panels <= 0 or cost_per_watt <= 0:
            messagebox.showerror(
                "Invalid Input",
                "System size, panel count, and cost per watt must be greater than zero.",
            )
            return

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

        # Save file next to the executable / script
        if getattr(sys, "frozen", False):
            save_dir = os.path.dirname(sys.executable)
        else:
            save_dir = os.path.dirname(os.path.abspath(__file__))

        filename = make_filename(customer_name)
        filepath = os.path.join(save_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(quote_text)

        messagebox.showinfo(
            "Quote Generated",
            f"Quote saved successfully!\n\n"
            f"File: {filename}\n\n"
            f"Gross Cost: {currency(results['gross_cost'])}\n"
            f"ITC (30%): -{currency(results['itc_amount'])}\n"
            f"Net Cost: {currency(results['net_cost'])}\n"
            f"Monthly Payment: {currency(results['monthly_payment'])}/mo\n"
            f"Annual Savings: {currency(results['annual_savings'])}\n"
            f"Payback: {results['payback_years']:.1f} years",
        )

    def _on_template_select(self, event):
        idx = self.template_dropdown.current()
        if 0 <= idx < len(self.templates):
            self.template_text.config(state="normal")
            self.template_text.delete("1.0", "end")
            self.template_text.insert("1.0", self.templates[idx][1])
            self.template_text.config(state="disabled")

    def _copy_template(self):
        self.root.clipboard_clear()
        content = self.template_text.get("1.0", "end-1c")
        self.root.clipboard_append(content)
        messagebox.showinfo("Copied", "Template copied to clipboard!")

    def _copy_all_templates(self):
        self.root.clipboard_clear()
        raw = load_email_templates()
        self.root.clipboard_append(raw)
        messagebox.showinfo("Copied", "All templates copied to clipboard!")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = SolarFlowGUI(root)
    root.mainloop()
