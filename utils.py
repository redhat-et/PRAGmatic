import re


def create_elastic_auth_string(settings):
    elasticsearch_user = settings["elasticsearch_user"]
    elasticsearch_password_file = settings["elasticsearch_password_file"]

    elasticsearch_password = None
    try:
        with open(elasticsearch_password_file, 'r') as file:
            for line in file:
                match = re.match(r'^New value: (.+)$', line.strip())
                if match:
                    elasticsearch_password = match.group(1)
                    break
    except FileNotFoundError:
        print("File not found.")
        return None
    if elasticsearch_password is None:
        print("Unexpected password file format.")
        return None

    return f"{elasticsearch_user}:{elasticsearch_password}"
