# Habitat - Dependency Manager

Habitat is a tool that simplifies the management of software dependencies through a graphical user interface. It allows users to create a list of software dependencies, add them to a cart, and run installation commands in a streamlined process. The software is built with Python's `tkinter` and `customtkinter` for the GUI and utilizes YAML for configuration management. This project also uses a locally running DeepSeek model from Ollama to generate terminal commands to install software libraries using specified package managers on different operating systems.

## Features

- **User-friendly GUI** for adding, viewing, and managing dependencies.
- **Import YAML**: Import a YAML configuration file containing dependencies and their respective install commands.
- **Search for Dependencies**: Add items to the cart by searching for their name and version.
- **Execute Commands**: Run the installation commands of the items in the cart with a single click.
- **Cart Management**: View, modify, and remove items from the cart.
- **Popular Items**: Predefined list of popular software items (e.g., Node.js, Python, VSCode) for quick addition to the cart.

## Requirements

- Python 3.x
- `customtkinter` library for advanced UI
- `yaml` library for handling YAML configuration files

You can install the necessary dependencies via pip:

```bash
pip install customtkinter pyyaml
## How to Use

### Running the Application
To run the application, execute the following command in the terminal:

```bash
python habitat.py
```

This will open the Habitat GUI where you can:

- **Create a New Dependency List**:  
  Click "Create" to manually add items with their names, versions, and installation commands.

- **Import an Existing Dependency List**:  
  Click "Import" to load a `.yaml` file containing predefined dependencies.

- **Search for a Dependency**:  
  Enter the name of a software in the search bar and add it to your cart.

- **Manage the Cart**:  
  Once you’ve added items to the cart, you can view them by clicking the "Cart" button.  
  From the cart, you can run the installation commands for each item.

### YAML Configuration File
The YAML file used to import dependencies should be structured as follows:

```yaml
package_managers:
  npm:
    version: "latest"
    install_command: |
      npm install -g npm
  pip:
    version: "latest"
    install_command: |
      pip install --upgrade pip

environment:
  python:
    version: "3.10"
    install_command: |
      sudo apt install python3.10
  nodejs:
    version: "14"
    install_command: |
      sudo apt install nodejs

developer_tools:
  vscode:
    version: "1.58.0"
    install_command: |
      code --install-extension ms-python.python
```

### Extracting and Running Commands
The commands listed in the YAML file will be processed and normalized into a single executable string. When you add dependencies to the cart, you can execute these commands in sequence with a click.

### Cart Management
- **Add to Cart**: When a dependency is added to the cart, it is stored as a tuple containing the name, version, and install command.
- **Remove from Cart**: You can remove items from the cart if needed.
- **Run Commands**: All commands in the cart can be executed at once using the "Run Commands" button. This will execute the install commands for all items in the cart sequentially.

### Code Overview

- **`extract_tuples(config_path)`**  
  Reads the YAML configuration file and extracts the relevant information, such as the name, version, and install command(s) for each item in the `package_managers`, `environment`, or `developer_tools` sections.

- **`tuples_to_yaml(tuples_list, output_path)`**  
  Converts the list of dependency tuples back into a YAML file. This is useful for saving a custom configuration after modifying or adding dependencies.

- **`run_commands(cart_items)`**  
  Executes the installation commands for each dependency in the cart.

### GUI Pages
- **WelcomePage**: The first screen the user sees, offering options to create a new list or import an existing one.
- **CreatePage**: Allows users to manually add dependencies and select from popular libraries.
- **CartPage**: Displays the current cart with the option to run installation commands.


