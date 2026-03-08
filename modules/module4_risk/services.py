def calculate_risk_score(violations):
    """
    Calculate risk score on a scale of 0-100
    0 = completely secure, 100 = critically insecure
    """
    if not violations:
        return 0
    
    # Base scores for each severity
    severity_scores = {
        "CRITICAL": 25,  # Each critical violation adds 25 points
        "HIGH": 15,       # Each high violation adds 15 points
        "MEDIUM": 8,      # Each medium violation adds 8 points
        "LOW": 3          # Each low violation adds 3 points
    }
    
    # Calculate raw score
    raw_score = 0
    for v in violations:
        severity = v["severity"]
        if severity in severity_scores:
            raw_score += severity_scores[severity]
    
    # Cap at 100
    final_score = min(raw_score, 100)
    
    return final_score


def determine_risk_level(score):
    """
    Determine risk level based on 0-100 score
    """
    if score >= 70:
        return "CRITICAL"
    elif score >= 50:
        return "HIGH"
    elif score >= 25:
        return "MEDIUM"
    else:
        return "LOW"