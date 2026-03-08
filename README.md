# Human-Error-Aware-Cloud-System
It is a system in which it takes input as configuration files and analyses the files in order to detect any dangerous settings or errors by humans in the configuration file before deployment and sending it to the cloud server. 
# What the project will actually do

A system that:

1. **Takes cloud infrastructure code (Terraform / CloudFormation / YAML)**
2. **Analyzes it**
3. **Detects human mistakes before deployment**
4. **Shows a risk score**
5. **Explains why**
6. **Suggests better alternatives**
7. **Supports multiple cloud providers (AWS + Azure)**
8. **Has a clean UI**
9. **Has an explanation + proof of work (report + demo)**

## **Hardware Requirements**

- **Laptop or PC** (your current laptop is fine)
- **RAM:** 4 GB minimum (8 GB recommended for smooth operation)
- **Storage:** 10–15 GB free space (for Python, libraries, and sample files)
- **Internet:** Required for installing libraries and optionally testing cloud examples


## **Software Requirements**

- **Operating System:** Windows 10/11, macOS, or Linux
- **Python 3.10+** (main programming language)
- **Libraries:**
    - `streamlit` → for UI
    - `python-hcl2` → parse Terraform files
    - `PyYAML` → parse YAML/CloudFormation files
    - `reportlab` → optional, for PDF report export
- **Code Editor:** VS Code (recommended)
- **Web Browser:** Chrome/Edge/Firefox (to run Streamlit UI)
