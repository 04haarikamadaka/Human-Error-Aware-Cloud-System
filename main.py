import streamlit as st
import os
import json
from datetime import datetime
from modules.module2_parser.services import parse_terraform_file
from modules.module3_validation.services import validate_resources
from modules.module4_risk.services import calculate_risk_score, determine_risk_level
from modules.module5_recommendation.services import generate_recommendations
from modules.module6_report.services import generate_report, generate_pdf_report
from shared.history_manager import HistoryManager

# Page config
st.set_page_config(
    page_title="Human Error Aware Cloud System",
    page_icon="🛡️",
    layout="centered"
)

# Simple custom CSS
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-box {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        border-left: 4px solid #667eea;
    }
    .violation-critical {
        background: #ffebee;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
        margin: 0.5rem 0;
    }
    .violation-high {
        background: #fff3e0;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #fd7e14;
        margin: 0.5rem 0;
    }
    .violation-medium {
        background: #fff8e1;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #ffc107;
        margin: 0.5rem 0;
    }
    .violation-low {
        background: #e8f5e9;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #28a745;
        margin: 0.5rem 0;
    }
    .recommendation-box {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #2196f3;
        margin: 0.5rem 0;
    }
    .footer {
        text-align: center;
        color: #666;
        font-size: 0.8rem;
        margin-top: 3rem;
        padding: 1rem;
        border-top: 1px solid #ddd;
    }
    .history-item {
        background: #f8f9fa;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.3rem 0;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize history manager
history_mgr = HistoryManager()

# Header
st.markdown("""
    <div class="main-header">
        <h1>  Human Error Aware Cloud System   </h1>
        <p>Detect misconfigurations in your Infrastructure as Code</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/security-checked--v1.png", width=80)
    
    # Developer Mode Toggle
    dev_mode = st.checkbox("🔧 Developer Mode", value=False, 
                        help="Show technical details and parsed data")
    
    st.divider()
    
    # Scan History Section
    st.markdown("### 📊 Scan History")
    
    # Clear History button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🗑️ ", help="Clear all scan history"):
            with open(history_mgr.history_file, 'w') as f:
                json.dump([], f)
            st.success("History cleared!")
            st.rerun()
    
    # Show recent scans
    recent_scans = history_mgr.get_history(limit=10)
    if recent_scans:
        for scan in recent_scans:
            risk_color = {
                "CRITICAL": "red",
                "HIGH": "orange",
                "MEDIUM": "gold",
                "LOW": "green"
            }.get(scan['risk_level'], "gray")
            
            st.markdown(f"""
            <div class="history-item">
                <strong>{scan['filename'][:20]}...</strong><br>
                <span style="color: {risk_color};">⬤</span> {scan['risk_level']} | Score: {scan['risk_score']}/100<br>
                <small>{scan['timestamp'][:10]}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No scans yet")

# Main content
st.markdown("### 📤 Upload Terraform File")
uploaded_file = st.file_uploader("Choose a .tf file", type=["tf"], label_visibility="collapsed")

if uploaded_file is not None:
    
    # Show loading message
    with st.spinner("Analyzing your infrastructure..."):
        
        # Save file
        upload_folder = "data/uploads"
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, uploaded_file.name)
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Run analysis
        parsed_data = parse_terraform_file(file_path)
        violations = validate_resources(parsed_data)
        risk_score = calculate_risk_score(violations)
        risk_level = determine_risk_level(risk_score)
        recommendations = generate_recommendations(violations)
        
        # Save to history
        history_mgr.save_scan(uploaded_file.name, violations, risk_score, risk_level)
    
    # Success message
    st.success(f"✅ Analysis complete for: {uploaded_file.name}")
    
    # Key metrics in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-box">
            <h3>🎯 Risk Score</h3>
            <h2>{risk_score}/100</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        level_color = {
            "CRITICAL": "red",
            "HIGH": "orange",
            "MEDIUM": "gold",
            "LOW": "green"
        }.get(risk_level, "gray")
        
        st.markdown(f"""
        <div class="metric-box">
            <h3>⚠️ Risk Level</h3>
            <h2 style="color: {level_color};">{risk_level}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-box">
            <h3>🔍 Violations</h3>
            <h2>{len(violations)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Developer Mode
    if dev_mode:
        with st.expander("🔧 Developer Mode - Parsed Terraform Data", expanded=True):
            st.json(parsed_data)
            
            # Show score calculation
            st.markdown("**Score Calculation:**")
            if violations:
                for v in violations:
                    points = {
                        "CRITICAL": 25,
                        "HIGH": 15,
                        "MEDIUM": 8,
                        "LOW": 3
                    }.get(v["severity"], 0)
                    st.markdown(f"- {v['severity']}: {v['description'][:50]}... (+{points} points)")
                st.markdown(f"**Total Score:** {risk_score}/100")
    
    # Violations section
    if violations:
        st.markdown("### 🚨 Security Violations Found")
        
        for v in violations:
            if v["severity"] == "CRITICAL":
                style = "violation-critical"
                icon = "🔥"
            elif v["severity"] == "HIGH":
                style = "violation-high"
                icon = "⚠️"
            elif v["severity"] == "MEDIUM":
                style = "violation-medium"
                icon = "⚡"
            else:
                style = "violation-low"
                icon = "ℹ️"
            
            points = {
                "CRITICAL": 25,
                "HIGH": 15,
                "MEDIUM": 8,
                "LOW": 3
            }.get(v["severity"], 0)
            
            st.markdown(f"""
            <div class="{style}">
                <strong>{icon} {v['severity']}:</strong> {v['description']}<br>
                <small>Resource: {v['resource']} | Impact: +{points} points</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ No security violations found! Your infrastructure is secure.")
    
    # Recommendations section
    if recommendations:
        st.markdown("### 💡 Recommendations")
        
        for r in recommendations:
            st.markdown(f"""
            <div class="recommendation-box">
                <strong>📋 Issue:</strong> {r['issue']}<br>
                <strong>🔧 Fix:</strong> {r['fix']}<br>
                <small>Resource: {r['resource']} | Severity: {r['severity']}</small>
            </div>
            """, unsafe_allow_html=True)
    
    # Simple PDF Report download
    if violations:
        st.markdown("### 📥 Download Report")
        
        # Generate PDF report
        report_path = generate_pdf_report(
            uploaded_file.name, violations, risk_score, risk_level, recommendations
        )
        
        # Read and offer download
        with open(report_path, "rb") as pdf_file:
            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_file.read(),
                file_name=f"security_report_{uploaded_file.name.replace('.tf', '')}.pdf",
                mime="application/pdf"
            )

# Footer
st.markdown("""
    <div class="footer">
        🛡️ Human Error Aware Cloud System  | Mini Project | Risk Score: 0-100 Scale
    </div>
""", unsafe_allow_html=True)