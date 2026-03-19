def generate_recommendations(violations):
    recommendations = []

    for v in violations:
        rule_name = v.get("rule", "").lower()
        resource = v.get("resource", "Unknown resource")

        # -------- S3 PUBLIC READ --------
        if "s3_public_access" in rule_name or "public" in rule_name:
            recommendations.append({
                "issue": "S3 bucket allows public read access",
                "fix": "Set ACL to private or enable 'Block Public Access' in AWS S3 settings",
                "resource": resource,
                "explanation": """
Basic:
This S3 bucket is publicly accessible, meaning anyone on the internet can view its contents.

Why this is a problem:
If the bucket contains sensitive data like user information, backups, or private files, it can be accessed by unauthorized people.

Real-world impact:
Many real-world data breaches have happened due to publicly exposed cloud storage. Attackers can download confidential data easily.

Advanced:
Public access is controlled using ACLs (Access Control Lists) and bucket policies. If misconfigured, it allows unrestricted access.
Cloud providers like AWS provide 'Block Public Access' settings to prevent this mistake.

Best Practice:
Always keep S3 buckets private by default. Use IAM roles and policies to give controlled access only to authorized users.
"""
            })

        # -------- S3 PUBLIC WRITE --------
        elif "s3_public_write" in rule_name or "write" in rule_name:
            recommendations.append({
                "issue": "S3 bucket allows public write access",
                "fix": "Remove public write permissions and restrict access using IAM policies",
                "resource": resource,
                "explanation": """
Basic:
This bucket allows anyone to upload, modify, or delete files.

Why this is dangerous:
Anyone on the internet can change your data or upload malicious content.

Real-world impact:
Attackers can upload harmful files, delete important data, or use your storage for illegal purposes.

Advanced:
Public write access is a severe misconfiguration. It violates the principle of least privilege in cloud security.
Proper IAM roles and strict bucket policies should be used instead.

Best Practice:
Never allow public write access. Only authenticated users with proper permissions should be allowed to modify data.
"""
            })

        # -------- DEFAULT FALLBACK --------
        else:
            recommendations.append({
                "issue": v.get("description", "Unknown issue"),
                "fix": "Review configuration and follow cloud security best practices",
                "resource": resource,
                "explanation": """
Basic:
There is a configuration issue in your cloud setup.

Why this is important:
Incorrect configurations can lead to security risks, downtime, or performance issues.

Advanced:
Cloud systems require proper configuration of networking, permissions, and resources.
Even small mistakes can lead to serious problems.

Best Practice:
Always follow cloud provider guidelines and enable security best practices like encryption, access control, and monitoring.
"""
            })

    return recommendations