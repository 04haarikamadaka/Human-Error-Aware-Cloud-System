import hcl2

def parse_terraform_file(file_path):

    with open(file_path, "r") as file:
        parsed_data = hcl2.load(file)

    return parsed_data