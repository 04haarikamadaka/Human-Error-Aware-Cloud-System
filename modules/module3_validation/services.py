import yaml

def load_security_rules():

    with open("config/security_rules.yaml", "r") as file:
        rules = yaml.safe_load(file)

    return rules


def validate_resources(parsed_data):

    rules = load_security_rules()
    violations = []

    if "resource" in parsed_data:

        for resource in parsed_data["resource"]:

            for resource_type, instances in resource.items():

                for name, properties in instances.items():

                    for rule_name, rule in rules.items():

                        if resource_type == rule["resource_type"]:
                            
                            # Check for exact value disallowed
                            if "disallowed_value" in rule:
                                check_field = rule["check"]
                                if check_field in properties:
                                    if properties[check_field] == rule["disallowed_value"]:
                                        violations.append(create_violation(rule_name, rule, name))
                            
                            # Check for missing required configuration
                            elif "missing_value" in rule:
                                check_field = rule["check"]
                                if check_field not in properties:
                                    violations.append(create_violation(rule_name, rule, name))
                            
                            # Check if value contains something (like IP ranges)
                            elif "contains" in rule:
                                check_field = rule["check"]
                                if check_field in properties:
                                    if rule["contains"] in str(properties[check_field]):
                                        # Check port if specified
                                        if "port" in rule:
                                            if "to_port" in properties and properties["to_port"] == rule["port"]:
                                                violations.append(create_violation(rule_name, rule, name))
                                        else:
                                            violations.append(create_violation(rule_name, rule, name))
                            
                            # Check if value is less than threshold
                            elif "less_than" in rule:
                                check_field = rule["check"]
                                if check_field in properties:
                                    if int(properties[check_field]) < rule["less_than"]:
                                        violations.append(create_violation(rule_name, rule, name))

    return violations


def create_violation(rule_name, rule, resource_name):
    return {
        "rule": rule_name,
        "description": rule["description"],
        "severity": rule["severity"],
        "resource": resource_name,
        "recommendation": rule.get("recommendation", "Review and fix this security issue")
    }