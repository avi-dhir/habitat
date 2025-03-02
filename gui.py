import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
import yaml
import subprocess

###################################
# Data Extraction and Command Logic
###################################
def extract_tuples(config_path):
    """
    Reads the YAML configuration file and extracts:
      - name, version, install_command(s)
    for each item in package_managers, environment, or developer_tools.

    If 'install_command' is a multi-line string or list, it is converted into a single shell-executable string.
    
    Returns a list of (name:str, version:str, command:str) tuples.
    """
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    results = []
    for section in ["package_managers", "environment", "developer_tools"]:
        if section in config:
            for name, details in config[section].items():
                version = details.get("version", "latest")
                command = details.get("install_command", "")

                # Normalize install_command into a single string
                if isinstance(command, str):
                    command_str = " && ".join(cmd.strip() for cmd in command.splitlines() if cmd.strip())  # Join multiline
                elif isinstance(command, list):
                    command_str = " && ".join(command)  # Join list into a string
                else:
                    command_str = ""

                results.append((name, version, command_str))  # Store as a single string

    return results

def tuples_to_yaml(tuples_list, output_path):
    """
    Converts a list of (name, version, command) tuples back to a YAML configuration file.
    Places all items in the "environment" section.
    
    Args:
        tuples_list: List of (name, version, command) tuples
        output_path: Path where the YAML file will be saved
    """
    config = {
        "environment": {}
    }
    
    for name, version, command in tuples_list:
        if command and " | " in command:
            command_list = command.split("\n")
        else:
            command_list = command
            
        config["environment"][name] = {
            "version": version,
            "install_command": command_list
        }
    with open(output_path, "w") as file:
        yaml.dump(config, file, default_flow_style=False, sort_keys=False)
    return config

def run_commands(cart_items):
    """
    Executes the command from each tuple in cart_items.
    cart_items is a list of (Name, Version, Command) tuples.
    """
    for (name, version, command) in cart_items:
        if command:
            print(f"Running command for {name} v{version}: {command}")
            try:
                result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                print(result.stdout.decode())
            except subprocess.CalledProcessError as e:
                print(f"Error running command for {name} v{version}: {e.stderr.decode()}")
        else:
            print(f"No command to run for {name} v{version}")
    print("All commands run.")

###################################
# Main HabitatApp and Pages
###################################
ctk.set_appearance_mode("System")  # "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

class HabitatApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Habitat")
        # Force 450x450 window size, then center it
        self.geometry("400x400")
        self.update_idletasks()
        self.center_window(390, 290)
        self.resizable(False, False)

        # The cart holds (Name, version, command) items
        self.software_cart = []

        # Main container
        container = ctk.CTkFrame(self, corner_radius=0, border_width=0, fg_color="transparent")
        container.pack(fill="both", expand=True)

        self.frames = {}
        for Page in (WelcomePage, CreatePage, CartPage):
            page_name = Page.__name__
            frame = Page(parent=container, controller=self)
            self.frames[page_name] = frame
            # Let each page fill container
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("WelcomePage")

    def center_window(self, width=450, height=450):
        """Centers the window on the screen."""
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w // 2) - (width // 2)
        y = (screen_h // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def show_frame(self, page_name: str):
        frame = self.frames[page_name]
        frame.tkraise()
        if page_name == "CartPage":
            self.frames["CartPage"].refresh_cart()
        elif page_name == "CreatePage":
            self.frames["CreatePage"].update_cart_button()

    def add_to_cart(self, name: str, version: str, command: str):
        new_item = (name, version, command)
        if new_item not in self.software_cart:
            self.software_cart.append(new_item)
            self.frames["CreatePage"].update_cart_button()
            self.frames["CartPage"].refresh_cart()
        else:
            messagebox.showinfo(
                "Duplicate Entry", f"'{name} v{version}' is already in the cart."
            )

    def clear_cart(self):
        self.software_cart.clear()
        self.frames["CartPage"].refresh_cart()
        self.frames["CreatePage"].update_cart_button()


class WelcomePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=0, border_width=0, fg_color="transparent")
        self.controller = controller

        title_label = ctk.CTkLabel(
            self,
            text="Welcome to Habitat",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        title_label.pack(pady=(20, 10), anchor="center")

        create_button = ctk.CTkButton(
            self,
            text="Create",
            width=120,
            command=lambda: controller.show_frame("CreatePage")
        )
        create_button.pack(pady=6, anchor="center")

        import_button = ctk.CTkButton(
            self,
            text="Import",
            width=120,
            command=self.import_file
        )
        import_button.pack(pady=6, anchor="center")

    def import_file(self):
        file_path = filedialog.askopenfilename(
            title="Import Dependencies (.yaml only)",
            filetypes=[("YAML Files", "*.yaml"), ("All Files", "*.*")],
        )
        if not file_path:
            return
        if not file_path.lower().endswith(".yaml"):
            messagebox.showerror("Error", "Please select a .yaml file.")
            return
        self.controller.clear_cart()

        try:
            all_items = extract_tuples(file_path)
            if all_items:
                for (name, version, cmd) in all_items:
                    self.controller.add_to_cart(name, version, cmd)
            else:
                messagebox.showinfo("No Commands Found", "No valid commands found in YAML.")
            self.controller.show_frame("CartPage")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse YAML: {e}")


class CreatePage(ctk.CTkFrame):
    """
    Allows user to add (Name, Version) via text entries,
    plus a "Search" button. On the same row, there's a "Cart" button.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Input area with grid layout
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(pady=10)

        # We'll use 4 columns now: name, version, search, cart
        input_frame.grid_rowconfigure(0, weight=1)
        for col in range(4):
            input_frame.grid_columnconfigure(col, weight=1)

        self.name_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Name",
            width=160,  # Increased from 80 to 160
            justify="center"
        )
        # If you want it to span more columns, adjust columnspan accordingly.
        self.name_entry.grid(row=0, column=0, padx=8, pady=5, columnspan=2)

        search_button = ctk.CTkButton(
            input_frame,
            text="Search",
            command=self.search_item,
            width=60,
        )
        search_button.grid(row=0, column=2, padx=8, pady=5)

        self.cart_button = ctk.CTkButton(
            input_frame,
            text="Cart (0)",
            width=70,
            command=lambda: self.controller.show_frame("CartPage")
        )
        self.cart_button.grid(row=0, column=3, padx=8, pady=5)

        # Popular items
        popular_label = ctk.CTkLabel(
            self,
            text="Popular Items:",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        popular_label.pack(pady=(8, 4), anchor="center")

        popular_frame = ctk.CTkFrame(self, corner_radius=0, border_width=0, fg_color="transparent")
        popular_frame.pack(pady=4)

        self.popular_libraries = [
            ("Node.js", "latest", "npm install -g node"),
            ("Python", "3.10", "pip install python"),
            ("VSCode", "1.81.1", "code --install-extension"),
        ]

        # Create a dictionary to store version entry widgets for popular items
        self.popular_version_entries = {}

        for item in self.popular_libraries:
            name, version, cmd = item
            
            # Create a frame for each popular item
            item_frame = ctk.CTkFrame(
                popular_frame,
                corner_radius=0,
                border_width=0,
                fg_color="transparent"
            )
            item_frame.pack(pady=4, anchor="center")
            
            # Name button
            name_button = ctk.CTkButton(
                item_frame,
                text=name,
                width=100,
                command=lambda i=item: self.add_popular_item(i)
            )
            name_button.pack(side="left", padx=(0, 5))
            
            # Version entry
            version_entry = ctk.CTkEntry(
                item_frame,
                width=80,
                justify="center"
            )
            version_entry.insert(0, version)
            version_entry.pack(side="left")
            
            # Store reference to the entry widget
            self.popular_version_entries[name] = version_entry

        back_button = ctk.CTkButton(
            self,
            text="Back",
            width=60,
            command=lambda: controller.show_frame("WelcomePage")
        )
        back_button.pack(padx=(20, 0), pady=6, side="left", anchor="center")

        self.update_cart_button()

    def search_item(self):
        """When user clicks 'Search', treat it like adding items with no command."""
        name = self.name_entry.get().strip()
        version = self.version_entry.get().strip() or "latest"  # Default to "latest" if empty
        command = ""
        if name:
            self.controller.add_to_cart(name, version, command)
            # Clear entries
            self.name_entry.delete(0, tk.END)
            self.version_entry.delete(0, tk.END)
            self.update_cart_button()
        else:
            messagebox.showwarning("Input Error", "Please enter at least a Name.")

    def add_popular_item(self, item):
        name, _, cmd = item
        # Get the current version from the entry
        version = self.popular_version_entries[name].get().strip() or "latest"
        self.controller.add_to_cart(name, version, cmd)
        self.update_cart_button()

    def update_cart_button(self):
        """Sets the cart button text to 'Cart (#)'."""
        count = len(self.controller.software_cart)
        self.cart_button.configure(text=f"Cart ({count})")


# class CartPage(ctk.CTkFrame):
#     """
#     Displays (Name, version) from the cart with editable version field.
#     """
#     def __init__(self, parent, controller):
#         super().__init__(parent, corner_radius=0, border_width=0, fg_color="transparent")
#         self.controller = controller
#         self.version_entries = {}  # To store version entry widgets

#         title_label = ctk.CTkLabel(
#             self,
#             text="Shopping Cart",
#             font=ctk.CTkFont(size=15, weight="bold"),
#         )
#         title_label.pack(pady=(10, 6), anchor="center")

#         self.scroll_frame = ctk.CTkScrollableFrame(
#             self,
#             width=350,
#             corner_radius=0,
#             border_width=0,
#             fg_color="transparent",
#         )
#         self.scroll_frame.pack(padx=10, pady=(0, 6), fill="both", expand=True)

#         bottom_frame = ctk.CTkFrame(
#             self, corner_radius=0, border_width=0, fg_color="transparent"
#         )
#         bottom_frame.pack(fill="x", pady=6)

#         run_button = ctk.CTkButton(
#             bottom_frame, text="Run", width=60, command=self.on_run_commands
#         )
#         run_button.pack(side="right", padx=(0, 20))

#         back_button = ctk.CTkButton(
#             bottom_frame, text="Back", width=60, command=self.on_back
#         )
#         back_button.pack(side="left", padx=(20, 0))
        
#         # Add an update all button
#         update_button = ctk.CTkButton(
#             bottom_frame, text="Update All", width=80, command=self.update_all_versions
#         )
#         update_button.pack(side="bottom", pady=5)

#     def refresh_cart(self):
#         """Refreshes the cart display with Name + Editable Version."""
#         for widget in self.scroll_frame.winfo_children():
#             widget.destroy()
            
#         self.version_entries.clear()

#         for idx, item in enumerate(self.controller.software_cart, start=1):
#             name, version, cmd = item
            
#             item_frame = ctk.CTkFrame(
#                 self.scroll_frame,
#                 corner_radius=0,
#                 border_width=0,
#                 fg_color="transparent"
#             )
#             item_frame.pack(fill="x", pady=4, padx=15)

#             # Name label
#             name_label = ctk.CTkLabel(item_frame, text=f"{idx}. {name}")
#             name_label.pack(side="left", padx=5)
            
#             # Version entry field
#             version_entry = ctk.CTkEntry(
#                 item_frame, 
#                 width=80,
#                 justify="center"
#             )
#             version_entry.insert(0, version)
#             version_entry.pack(side="left", padx=5)
            
#             # Store the entry widget with reference to the item for updating later
#             self.version_entries[item] = (version_entry, idx-1)

#             # Remove button
#             remove_button = ctk.CTkButton(
#                 item_frame, text="X", width=25, command=lambda t=item: self.remove_from_cart(t)
#             )
#             remove_button.pack(side="right", padx=5)

#     def update_all_versions(self):
#         """Updates all item versions based on entry fields."""
#         new_cart = []
        
#         # Iterate through current cart and get updated versions
#         for item, (entry_widget, idx) in self.version_entries.items():
#             name, _, cmd = item
#             new_version = entry_widget.get().strip() or "latest"
#             new_item = (name, new_version, cmd)
#             new_cart.append(new_item)
        
#         # Replace the entire cart
#         self.controller.software_cart = new_cart
#         self.refresh_cart()
#         messagebox.showinfo("Updated", "All versions have been updated.")

#     def remove_from_cart(self, tuple_item):
#         if tuple_item in self.controller.software_cart:
#             self.controller.software_cart.remove(tuple_item)
#             self.refresh_cart()
#             self.controller.frames["CreatePage"].update_cart_button()
#             messagebox.showinfo("Removed", f"'{tuple_item[0]}' was removed.")
#         else:
#             messagebox.showwarning("Not Found", "Item is not in the cart.")

#     def on_run_commands(self):
#         # First update all versions
#         self.update_all_versions()
        
#         if self.controller.software_cart:
#             run_commands(self.controller.software_cart)
#             messagebox.showinfo("Done", "Commands executed (see console output).")
#         else:
#             messagebox.showinfo("Empty Cart", "No items to install.")

#     def on_back(self):
#         # Update versions before going back
#         self.update_all_versions()
#         self.controller.show_frame("CreatePage")
#         self.controller.frames["CreatePage"].update_cart_button()

#     def tkraise(self, aboveThis=None):
#         self.refresh_cart()
#         super().tkraise(aboveThis)

class CartPage(ctk.CTkFrame):
    """
    Displays (Name, Version) from the cart with editable version fields.
    Updates automatically when a version is changed.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=0, border_width=0, fg_color="transparent")
        self.controller = controller
        self.version_entries = {}  # Store version entry widgets

        title_label = ctk.CTkLabel(
            self,
            text="Shopping Cart",
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        title_label.pack(pady=(10, 6), anchor="center")

        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            width=350,
            corner_radius=0,
            border_width=0,
            fg_color="transparent",
        )
        self.scroll_frame.pack(padx=10, pady=(0, 6), fill="both", expand=True)

        bottom_frame = ctk.CTkFrame(self, corner_radius=0, border_width=0, fg_color="transparent")
        bottom_frame.pack(fill="x", pady=6)

        export_button = ctk.CTkButton(bottom_frame, text="Export", width=60, command=self.export_to_yaml)
        export_button.pack(side="right", padx=(0, 10))
        
        run_button = ctk.CTkButton(
            bottom_frame, text="Run", width=60, command=self.on_run_commands
        )
        run_button.pack(side="right", padx=(0, 20))

        back_button = ctk.CTkButton(
            bottom_frame, text="Back", width=60, command=self.on_back
        )
        back_button.pack(side="left", padx=(20, 0))

    def refresh_cart(self):
        """Refreshes the cart display with Name + Editable Version."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        self.version_entries.clear()

        for idx, item in enumerate(self.controller.software_cart, start=1):
            name, version, cmd = item
            
            item_frame = ctk.CTkFrame(
                self.scroll_frame,
                corner_radius=0,
                border_width=0,
                fg_color="transparent"
            )
            item_frame.pack(fill="x", pady=4, padx=15)

            # Name label
            name_label = ctk.CTkLabel(item_frame, text=f"{idx}. {name}")
            name_label.pack(side="left", padx=5)
            
            # Version entry field
            version_entry = ctk.CTkEntry(
                item_frame, 
                width=80,
                justify="center"
            )
            version_entry.insert(0, version)
            version_entry.pack(side="left", padx=5)
            
            # Bind focus-out event to auto-update version
            version_entry.bind("<FocusOut>", lambda e, i=item, v=version_entry: self.update_version(i, v))

            # Store the entry widget with reference to the item for updating later
            self.version_entries[item] = version_entry

            # Remove button
            remove_button = ctk.CTkButton(
                item_frame, text="X", width=25, command=lambda t=item: self.remove_from_cart(t)
            )
            remove_button.pack(side="right", padx=5)

    def update_version(self, item, entry_widget):
        """Updates version in cart when an entry loses focus."""
        new_version = entry_widget.get().strip() or "latest"
        if item in self.controller.software_cart:
            name, _, cmd = item
            updated_item = (name, new_version, cmd)
            index = self.controller.software_cart.index(item)
            self.controller.software_cart[index] = updated_item
            print(f"Updated '{name}' to version {new_version}")

    def remove_from_cart(self, tuple_item):
        if tuple_item in self.controller.software_cart:
            self.controller.software_cart.remove(tuple_item)
            self.refresh_cart()
            self.controller.frames["CreatePage"].update_cart_button()
            messagebox.showinfo("Removed", f"'{tuple_item[0]}' was removed.")
        else:
            messagebox.showwarning("Not Found", "Item is not in the cart.")

    def on_run_commands(self):
        """Run commands with the latest versions."""
        if self.controller.software_cart:
            run_commands(self.controller.software_cart)
            messagebox.showinfo("Done", "Commands executed (see console output).")
        else:
            messagebox.showinfo("Empty Cart", "No items to install.")

    def on_back(self):
        """Return to CreatePage with updated versions."""
        self.controller.show_frame("CreatePage")
        self.controller.frames["CreatePage"].update_cart_button()

    def tkraise(self, aboveThis=None):
        self.refresh_cart()
        super().tkraise(aboveThis)
        
    def export_to_yaml(self):
        if self.controller.software_cart:
            tuples_to_yaml(self.controller.software_cart, "habitat.yaml")
            messagebox.showinfo("Exported", "Cart items exported to habitat.yaml.")
        else:
            messagebox.showwarning("Empty Cart", "No items to export.")
if __name__ == "__main__":
    app = HabitatApp()
    app.mainloop()
