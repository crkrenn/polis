import sys
import re

def replace_inner_variables(value, variables):
    # Define a pattern for ${VAR_NAME} placeholders
    pattern = re.compile(r'\$\{([^}]+)\}')

    # Substitute each matched placeholder with its value from the 'variables' dictionary
    return pattern.sub(lambda m: variables.get(m.group(1), m.group(0)), value)

def load_env_to_gcloud(env_file_path):
    gcloud_env_vars = {}

    with open(env_file_path, 'r') as f:
        for line in f.readlines():
            # Skipping commented lines
            if not line.startswith('#') and '=' in line:
                key, value = line.strip().split('=', 1)
                gcloud_env_vars[key] = value

    # Second pass for replacing inner variables
    for key, value in gcloud_env_vars.items():
        gcloud_env_vars[key] = replace_inner_variables(value, gcloud_env_vars)

    gcloud_env_str = ','.join([f"{k}={v}" for k, v in gcloud_env_vars.items()])
    print(f"{gcloud_env_str}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python <script_name> <path_to_env_file>")
        sys.exit(1)

    env_file_path = sys.argv[1]
    load_env_to_gcloud(env_file_path)
