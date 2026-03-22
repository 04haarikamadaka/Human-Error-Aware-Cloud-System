import streamlit as st
import os
import json
from modules.module2_parser.services import parse_terraform_file
from modules.module3_validation.services import validate_resources
from modules.module4_risk.services import calculate_risk_score, determine_risk_level
from modules.module5_recommendation.services import generate_recommendations
from modules.module6_report.services import generate_pdf_report
from shared.history_manager import HistoryManager

# Page config
st.set_page_config(page_title="Human Error Aware Cloud System ", page_icon="🛡️")

# Initialize
history_mgr = HistoryManager()

# Title
st.title("🛡️ Human Error Aware Cloud System ")
st.write("Check your Terraform files for security issues")

# Sidebar
with st.sidebar:
    st.header("Options")
    dev_mode = st.checkbox("Developer Mode")
    
    st.header("Recent Scans")
    history = history_mgr.get_history(limit=5)
    if history:
        for scan in history:
            st.write(f"{scan['filename']} - {scan['risk_level']} ({scan['risk_score']})")
    else:
        st.info("No scans yet")
    
    if st.button("Clear History"):
        with open(history_mgr.history_file, "w") as f:
            json.dump([], f)
        st.rerun()

# Main content - File upload
uploaded_file = st.file_uploader("Upload Terraform file (.tf)", type=["tf"])

if uploaded_file:
    with st.spinner("Analyzing your file..."):
        # Save uploaded file
        os.makedirs("data/uploads", exist_ok=True)
        file_path = os.path.join("data/uploads", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Run security checks
        parsed_data = parse_terraform_file(file_path)
        violations = validate_resources(parsed_data)
        risk_score = calculate_risk_score(violations)
        risk_level = determine_risk_level(risk_score)
        recommendations = generate_recommendations(violations)
        
        # Save to history
        history_mgr.save_scan(uploaded_file.name, violations, risk_score, risk_level)
    
    st.success("✅ Analysis Complete!")
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Risk Score", f"{risk_score}/100")
    col2.metric("Risk Level", risk_level)
    col3.metric("Violations", len(violations))
    
    # Developer mode - show raw data
    if dev_mode:
        st.subheader("Raw Data")
        st.json(parsed_data)
    
    # Simple explanations for violations
    simple_explanations = {
        "s3_public_read": "Your storage bucket is open to everyone on the internet - like leaving your front door unlocked.",
        "s3_public_write": "Anyone can add/delete files in your storage - like giving strangers keys to your house.",
        "s3_encryption_disabled": "Your files aren't encrypted - like writing secrets on a postcard.",
        "s3_versioning_disabled": "Deleted files are gone forever - like using a whiteboard without taking photos.",
        "ec2_public_ip": "Your server is directly exposed to the internet - like putting your computer on the sidewalk.",
        "ec2_open_ssh": "Your server's admin door is open to everyone - like leaving your house keys under the mat.",
        "ec2_open_rdp": "Your Windows remote desktop is open to all - like leaving your office door wide open.",
        "rds_publicly_accessible": "Your database is exposed online - like putting your safe in the middle of a street.",
        "rds_encryption_disabled": "Your database data isn't encrypted - like writing passwords on a whiteboard.",
        "rds_backup_retention_short": "You're only keeping 1-2 days of backups - like not backing up your phone for months.",
        "iam_root_access_keys": "You're using master admin keys for everything - like giving everyone the bank vault key.",
        "iam_password_no_policy": "Weak passwords are allowed - like letting people use 'password123'.",
        "ebs_unencrypted": "Your virtual hard drives aren't encrypted - like selling a laptop without wiping it.",
        "cloudfront_no_https": "Your website allows unencrypted traffic - like sending mail on a postcard.",
        "lambda_no_vpc": "Your functions run in an open network - like having a secret meeting in a public park.",
        "cloudtrail_disabled": "You're not logging who does what - like a store with no security cameras.",
        "elasticache_no_encryption": "Your cached data isn't encrypted - like leaving passwords on sticky notes."
    }
    
    # Show violations with explanations
    if violations:
        st.subheader("🔴 Security Violations")
        for v in violations:
            with st.expander(f"⚠️ {v['severity']} - {v['description']}"):
                desc = v['description'].lower()
                explanation = "The way your cloud service is set up has a security problem."
                
                # Match violation to simple explanation
                if "s3" in desc:
                    if "public read" in desc:
                        explanation = simple_explanations["s3_public_read"]
                    elif "public write" in desc:
                        explanation = simple_explanations["s3_public_write"]
                    elif "encrypt" in desc:
                        explanation = simple_explanations["s3_encryption_disabled"]
                    elif "version" in desc:
                        explanation = simple_explanations["s3_versioning_disabled"]
                elif "ec2" in desc or "instance" in desc:
                    if "public ip" in desc:
                        explanation = simple_explanations["ec2_public_ip"]
                    elif "ssh" in desc:
                        explanation = simple_explanations["ec2_open_ssh"]
                    elif "rdp" in desc:
                        explanation = simple_explanations["ec2_open_rdp"]
                elif "rds" in desc or "database" in desc:
                    if "public" in desc:
                        explanation = simple_explanations["rds_publicly_accessible"]
                    elif "encrypt" in desc:
                        explanation = simple_explanations["rds_encryption_disabled"]
                    elif "backup" in desc or "retention" in desc:
                        explanation = simple_explanations["rds_backup_retention_short"]
                elif "iam" in desc:
                    if "root" in desc or "access key" in desc:
                        explanation = simple_explanations["iam_root_access_keys"]
                    elif "password" in desc:
                        explanation = simple_explanations["iam_password_no_policy"]
                elif "ebs" in desc or "volume" in desc:
                    explanation = simple_explanations["ebs_unencrypted"]
                elif "cloudfront" in desc:
                    explanation = simple_explanations["cloudfront_no_https"]
                elif "lambda" in desc:
                    explanation = simple_explanations["lambda_no_vpc"]
                elif "cloudtrail" in desc:
                    explanation = simple_explanations["cloudtrail_disabled"]
                elif "elasticache" in desc or "cache" in desc:
                    explanation = simple_explanations["elasticache_no_encryption"]
                
                st.write(f"**What's wrong:** {explanation}")
                st.write(f"**Resource:** {v['resource']}")
    else:
        st.success("✅ No violations found - your configuration looks safe!")
    
    # IMPROVED: Recommendations with step-by-step instructions
    if recommendations:
        st.subheader("📋 Step-by-Step Fixes")
        
        # Define step-by-step fixes for common issues
        step_by_step_fixes = {
            "s3_public_read": [
                "1️⃣ **Go to AWS Console** → Open S3 service",
                "2️⃣ **Click on your bucket** from the list",
                "3️⃣ **Go to Permissions tab**",
                "4️⃣ **Find 'Block public access'** section → Click 'Edit'",
                "5️⃣ **Check ALL boxes** to block public access",
                "6️⃣ **Click 'Save changes'**",
                "7️⃣ **Verify**: Try opening a file URL in incognito mode - you should see 'Access Denied'"
            ],
            "s3_public_write": [
                "1️⃣ **Open AWS Console** → Go to S3",
                "2️⃣ **Select your bucket** → Click 'Permissions'",
                "3️⃣ **Check 'Bucket Policy'** - Delete any policy with 'Effect:Allow' and 'Principal:*'",
                "4️⃣ **Check 'Access Control List'** - Remove 'Everyone' write permissions",
                "5️⃣ **Save changes**",
                "6️⃣ **Test**: Try uploading a file without credentials - it should fail"
            ],
            "s3_encryption_disabled": [
                "1️⃣ **AWS Console** → S3 → Your bucket",
                "2️⃣ **Go to Properties tab**",
                "3️⃣ **Scroll to 'Default encryption'** → Click 'Edit'",
                "4️⃣ **Select 'Enable'** → Choose 'Amazon S3 key (SSE-S3)'",
                "5️⃣ **Click 'Save changes'**",
                "6️⃣ **For existing files**, run this command:",
                "   ```bash\n   aws s3 cp s3://your-bucket/ s3://your-bucket/ --recursive --sse AES256\n   ```"
            ],
            "s3_versioning_disabled": [
                "1️⃣ **AWS Console** → S3 → Your bucket",
                "2️⃣ **Go to Properties tab**",
                "3️⃣ **Scroll to 'Bucket Versioning'** → Click 'Edit'",
                "4️⃣ **Select 'Enable'**",
                "5️⃣ **Click 'Save changes'**",
                "6️⃣ **⚠️ Note**: Once enabled, versioning CANNOT be disabled (only suspended)"
            ],
            "ec2_public_ip": [
                "1️⃣ **AWS Console** → EC2 → Instances",
                "2️⃣ **Select your instance**",
                "3️⃣ **Click Actions** → Networking → Manage IP addresses",
                "4️⃣ **Set 'Auto-assign public IP' to 'Disable'**",
                "5️⃣ **Click 'Update'**",
                "6️⃣ **Alternative**: Move instance to a private subnet"
            ],
            "ec2_open_ssh": [
                "1️⃣ **AWS Console** → EC2 → Security Groups",
                "2️⃣ **Find the security group** attached to your instance",
                "3️⃣ **Click Inbound rules** → Edit inbound rules",
                "4️⃣ **Find SSH rule** (port 22)",
                "5️⃣ **Change '0.0.0.0/0'** to your office IP (e.g., '203.0.113.0/24')",
                "6️⃣ **Click 'Save rules'**",
                "7️⃣ **Test**: Try SSH from outside your office - connection should timeout"
            ],
            "ec2_open_rdp": [
                "1️⃣ **AWS Console** → EC2 → Security Groups",
                "2️⃣ **Select your security group**",
                "3️⃣ **Edit inbound rules**",
                "4️⃣ **Find RDP rule** (port 3389)",
                "5️⃣ **Replace '0.0.0.0/0'** with your office IP range",
                "6️⃣ **Save changes**"
            ],
            "rds_publicly_accessible": [
                "1️⃣ **AWS Console** → RDS → Databases",
                "2️⃣ **Select your database**",
                "3️⃣ **Click 'Modify'**",
                "4️⃣ **Under 'Connectivity'** → Set 'Public accessibility' to 'No'",
                "5️⃣ **Click 'Continue'** → Choose 'Apply immediately'",
                "6️⃣ **Wait for modification** to complete",
                "7️⃣ **Access securely**: Use a bastion host or VPN"
            ],
            "rds_encryption_disabled": [
                "⚠️ **Warning**: You can't encrypt an existing database directly",
                "1️⃣ **Create a snapshot**: RDS → Databases → Actions → Take snapshot",
                "2️⃣ **Copy snapshot with encryption**:",
                "   - Go to Snapshots → Select snapshot → Actions → Copy snapshot",
                "   - Check 'Enable encryption' → Choose a key → Copy",
                "3️⃣ **Restore encrypted database**:",
                "   - Select encrypted snapshot → Actions → Restore snapshot",
                "4️⃣ **Update your app** to use the new database endpoint"
            ],
            "rds_backup_retention_short": [
                "1️⃣ **AWS Console** → RDS → Databases",
                "2️⃣ **Select your database** → Click 'Modify'",
                "3️⃣ **Under 'Backup'** → Set 'Backup retention period' to 7-35 days",
                "4️⃣ **Set backup window** (e.g., 03:00-04:00)",
                "5️⃣ **Click 'Continue'** → Apply immediately",
                "6️⃣ **Verify**: Check that backups are being created"
            ],
            "iam_root_access_keys": [
                "1️⃣ **AWS Console** → IAM → Users",
                "2️⃣ **Click on 'root' user**",
                "3️⃣ **Go to 'Security credentials' tab**",
                "4️⃣ **Find Access keys section**",
                "5️⃣ **Click 'Make inactive'** (wait a few days to ensure nothing breaks)",
                "6️⃣ **Then click 'Delete'**",
                "7️⃣ **Create IAM users** for daily work with limited permissions",
                "8️⃣ **Enable MFA** on all IAM users"
            ],
            "iam_password_no_policy": [
                "1️⃣ **AWS Console** → IAM → Account settings",
                "2️⃣ **Click 'Edit'** on Password policy",
                "3️⃣ **Configure strong policy**:",
                "   - Minimum length: 14 characters",
                "   - Require: uppercase, lowercase, numbers, symbols",
                "4️⃣ **Click 'Apply password policy'**",
                "5️⃣ **Users will need to change passwords** on next login"
            ]
        }
        
        for r in recommendations:
            with st.expander(f"📋 {r['issue']}"):
                st.write(f"**Resource:** {r['resource']}")
                st.write("---")
                
                # Get issue text for matching
                issue = r['issue'].lower()
                
                # Show step-by-step instructions if available
                steps_shown = False
                
                if "s3" in issue:
                    if "public read" in issue:
                        for step in step_by_step_fixes["s3_public_read"]:
                            st.write(step)
                        steps_shown = True
                    elif "public write" in issue:
                        for step in step_by_step_fixes["s3_public_write"]:
                            st.write(step)
                        steps_shown = True
                    elif "encrypt" in issue:
                        for step in step_by_step_fixes["s3_encryption_disabled"]:
                            st.write(step)
                        steps_shown = True
                    elif "version" in issue:
                        for step in step_by_step_fixes["s3_versioning_disabled"]:
                            st.write(step)
                        steps_shown = True
                
                elif "ec2" in issue or "instance" in issue:
                    if "public ip" in issue:
                        for step in step_by_step_fixes["ec2_public_ip"]:
                            st.write(step)
                        steps_shown = True
                    elif "ssh" in issue:
                        for step in step_by_step_fixes["ec2_open_ssh"]:
                            st.write(step)
                        steps_shown = True
                    elif "rdp" in issue:
                        for step in step_by_step_fixes["ec2_open_rdp"]:
                            st.write(step)
                        steps_shown = True
                
                elif "rds" in issue or "database" in issue:
                    if "public" in issue:
                        for step in step_by_step_fixes["rds_publicly_accessible"]:
                            st.write(step)
                        steps_shown = True
                    elif "encrypt" in issue:
                        for step in step_by_step_fixes["rds_encryption_disabled"]:
                            st.write(step)
                        steps_shown = True
                    elif "backup" in issue or "retention" in issue:
                        for step in step_by_step_fixes["rds_backup_retention_short"]:
                            st.write(step)
                        steps_shown = True
                
                elif "iam" in issue:
                    if "root" in issue or "access key" in issue:
                        for step in step_by_step_fixes["iam_root_access_keys"]:
                            st.write(step)
                        steps_shown = True
                    elif "password" in issue:
                        for step in step_by_step_fixes["iam_password_no_policy"]:
                            st.write(step)
                        steps_shown = True
                
                # If no step-by-step guide, show the original recommendation
                if not steps_shown:
                    st.write(f"**Quick fix:** {r['fix']}")
                    st.write("\n**For detailed steps:**")
                    st.write("1️⃣ Check your cloud provider's documentation")
                    st.write("2️⃣ Review your current settings")
                    st.write("3️⃣ Make changes one at a time")
                    st.write("4️⃣ Test after each change")
    
    # Download PDF report
    if violations:
        report_path = generate_pdf_report(
            uploaded_file.name, violations, risk_score, risk_level, recommendations
        )
        with open(report_path, "rb") as pdf:
            st.download_button("📥 Download PDF Report", pdf, 
                            file_name=f"report_{uploaded_file.name}.pdf",
                            mime="application/pdf")
    
    