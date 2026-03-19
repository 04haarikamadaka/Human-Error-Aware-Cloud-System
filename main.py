import streamlit as st
import os
import json
from modules.module2_parser.services import parse_terraform_file
from modules.module3_validation.services import validate_resources
from modules.module4_risk.services import calculate_risk_score, determine_risk_level
from modules.module5_recommendation.services import generate_recommendations
from modules.module6_report.services import generate_pdf_report
from shared.history_manager import HistoryManager

# Page settings
st.set_page_config(page_title="Human Error Aware Cloud System", page_icon="🛡️")

history_mgr = HistoryManager()

st.title("🛡️ Human Error Aware Cloud System")
st.write("Detect misconfigurations in Terraform Infrastructure")

# Sidebar
st.sidebar.title("Options")
dev_mode = st.sidebar.checkbox("Developer Mode")

st.sidebar.subheader("Scan History")

# Clear history
if st.sidebar.button("Clear History"):
    with open(history_mgr.history_file, "w") as f:
        json.dump([], f)
    st.sidebar.success("History cleared")
    st.rerun()

# Show history
history = history_mgr.get_history(limit=5)

if history:
    for scan in history:
        st.sidebar.write(
            f"{scan['filename']} | {scan['risk_level']} | Score {scan['risk_score']}"
        )
else:
    st.sidebar.info("No scans yet")

# File upload
uploaded_file = st.file_uploader("Upload Terraform file (.tf)", type=["tf"])

if uploaded_file:
    with st.spinner("Analyzing..."):
        upload_folder = "data/uploads"
        os.makedirs(upload_folder, exist_ok=True)

        file_path = os.path.join(upload_folder, uploaded_file.name)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Run pipeline
        parsed_data = parse_terraform_file(file_path)
        violations = validate_resources(parsed_data)
        risk_score = calculate_risk_score(violations)
        risk_level = determine_risk_level(risk_score)
        recommendations = generate_recommendations(violations)

        history_mgr.save_scan(uploaded_file.name, violations, risk_score, risk_level)

    st.success("Analysis Complete")

    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Risk Score", f"{risk_score}/100")
    col2.metric("Risk Level", risk_level)
    col3.metric("Violations", len(violations))

    # Developer mode
    if dev_mode:
        st.subheader("Parsed Terraform Data")
        st.json(parsed_data)

    # Violations
    if violations:
        st.subheader("Security Violations")
        for v in violations:
            st.warning(
                f"{v['severity']} - {v['description']} | Resource: {v['resource']}"
            )
    else:
        st.success("No violations found")

    # Recommendations
    if recommendations:
        st.subheader("Recommendations")
        for r in recommendations:
            st.info(
                f"**Issue:** {r['issue']}\n\n"
                f"**Fix:** {r['fix']}\n\n"
                f"**Resource:** {r['resource']}"
            )

    # PDF report
    if violations:
        report_path = generate_pdf_report(
            uploaded_file.name, violations, risk_score, risk_level, recommendations
        )

        with open(report_path, "rb") as pdf:
            st.download_button(
                "Download PDF Report",
                pdf,
                file_name=f"report_{uploaded_file.name}.pdf",
                mime="application/pdf",
            )