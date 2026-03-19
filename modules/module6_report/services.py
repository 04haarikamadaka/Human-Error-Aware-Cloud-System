from fpdf import FPDF
import os, datetime, re

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Security Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def clean(self, text):
        return str(text or "N/A").encode('latin-1', 'ignore').decode('latin-1')


def generate_pdf_report(filename, violations, risk_score, risk_level, recommendations):
    os.makedirs("data/reports", exist_ok=True)

    # safe filename
    filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"data/reports/report_{filename}_{timestamp}.pdf"

    pdf = PDF()
    pdf.add_page()
    clean = pdf.clean

    # --- Basic Info ---
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 8, clean(f"File: {filename}"), 0, 1)
    pdf.cell(0, 8, clean(f"Risk: {risk_score}/100 ({risk_level})"), 0, 1)
    pdf.cell(0, 8, clean(f"Violations: {len(violations or [])}"), 0, 1)
    pdf.ln(5)

    # --- Violations ---
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, "Violations", 0, 1)

    pdf.set_font('Arial', '', 11)
    if violations:
        for i, v in enumerate(violations, 1):
            pdf.multi_cell(0, 6, clean(
                f"{i}. {v.get('description','No desc')}\n"
                f"Resource: {v.get('resource','Unknown')}\n"
                f"Severity: {v.get('severity','N/A')}"
            ))
            pdf.ln(2)
    else:
        pdf.cell(0, 8, "No violations found", 0, 1)

    # --- Recommendations ---
    if recommendations:
        pdf.add_page()
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, "Recommendations", 0, 1)

        pdf.set_font('Arial', '', 11)
        for i, r in enumerate(recommendations, 1):
            pdf.multi_cell(0, 6, clean(
                f"{i}. {r.get('issue','No issue')}\n"
                f"Fix: {r.get('fix','No fix')}"
            ))
            pdf.ln(2)

    pdf.output(path)
    return path