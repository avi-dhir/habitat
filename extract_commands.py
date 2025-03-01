import yaml
import sys
import subprocess




def extract_commands(config_path):
    """
    Reads the YAML configuration file and extracts all install commands.
    Returns a list of commands.
    """
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    commands = []
    for section in ["package_managers", "environment", "developer_tools"]:
        if section in config:
            for tool, details in config[section].items():
                command = details.get("install_command")
                if command:
                    commands.append(command)
    return commands

def run_commands(commands):
    """
    Executes a list of commands in the terminal.

    :param commands: List of command strings.
    """
    # ls = ["ls"]
    for cmd in commands:
        print(f"Running command: {cmd}")
        try:
            # subprocess.run(cmd, shell=True, check=True)
            print("Command executed successfully.\n")
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {cmd}")
            print(f"Error details: {e}\n")


def extract_name(config_path):
    """
    Reads the YAML configuration file and extracts all install commands.
    Returns a list of names of applications.
    """
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    names = []
    for section in ["environment", "developer_tools"]:
        if section in config:
            for tool, name in config[section].items():
                if tool:
                    names.append(tool)
    return names

def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_commands.py <config_file>")
        sys.exit(1)
    
    config_path = sys.argv[1]
    commands = extract_commands(config_path)
    names = extract_name(config_path)

    run_commands(commands)

    for cmd in commands:
        print(cmd)

    for name in names:
        print(name)

if __name__ == '__main__':
    main()

