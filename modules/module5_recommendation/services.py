def generate_recommendations(violations):
    
    recommendations = []
    
    for v in violations:
        recommendations.append({
            "rule": v["rule"],
            "issue": v["description"],
            "fix": v.get("recommendation", "Review and fix this security issue"),
            "severity": v["severity"],
            "resource": v["resource"]
        })
    
    return recommendations