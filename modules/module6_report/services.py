from fpdf import FPDF
import os
from datetime import datetime

def generate_pdf_report(uploaded_filename, violations, risk_score, risk_level, recommendations):
    
    # Create reports folder
    report_folder = "data/reports"
    os.makedirs(report_folder, exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"security_report_{timestamp}.pdf"
    report_path = os.path.join(report_folder, report_filename)
    
    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "CLOUD SECURITY REPORT", 0, 1, "C")
    pdf.ln(5)
    
    # Date and file
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1)
    pdf.cell(0, 6, f"File: {uploaded_filename}", 0, 1)
    pdf.ln(5)
    
    # Risk Score
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, f"Risk Score: {risk_score}/100", 0, 1)
    pdf.cell(0, 8, f"Risk Level: {risk_level}", 0, 1)
    pdf.ln(5)
    
    # Violations
    if violations:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "SECURITY VIOLATIONS:", 0, 1)
        pdf.ln(2)
        
        pdf.set_font("Arial", "", 10)
        for i, v in enumerate(violations, 1):
            # Use dash instead of bullet
            pdf.multi_cell(0, 6, f"{i}. [{v['severity']}] {v['description']}")
            pdf.cell(0, 4, f"   Resource: {v['resource']}", 0, 1)
            pdf.ln(2)
    else:
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 8, "No security violations found.", 0, 1)
    
    pdf.ln(5)
    
    # Recommendations
    if recommendations:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "RECOMMENDATIONS:", 0, 1)
        pdf.ln(2)
        
        pdf.set_font("Arial", "", 10)
        for i, r in enumerate(recommendations, 1):
            # Use dash instead of bullet
            pdf.multi_cell(0, 6, f"{i}. ISSUE: {r['issue']}")
            pdf.multi_cell(0, 6, f"   FIX: {r['fix']}")
            pdf.cell(0, 4, f"   Resource: {r['resource']} | Severity: {r['severity']}", 0, 1)
            pdf.ln(3)
    
    # Save PDF - using latin-1 safe characters only
    pdf.output(report_path)
    return report_path

# Keep original function name for compatibility
def generate_report(uploaded_filename, parsed_data, violations, risk_score, risk_level, recommendations):
    report_path = generate_pdf_report(
        uploaded_filename, violations, risk_score, risk_level, recommendations
    )
    return {"status": "success"}, report_path