import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
import yaml

###################################
# Data Extraction and Command Logic
###################################
def extract_tuples(config_path):
    """
    Reads the YAML configuration file and attempts to extract:
      name, version, install_command
    for each defined item in package_managers, environment, or developer_tools.

    Returns a list of (name:str, version:str, command:str) tuples.
    """
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    results = []
    for section in ["package_managers", "environment", "developer_tools"]:
        if section in config:
            for _, details in config[section].items():
                name = details.get("name", "Unknown")
                version = details.get("version", "latest")
                command = details.get("install_command", "")
                results.append((name, version, command))

    return results


def run_commands(cart_items):
    """
    Executes the command from each tuple in cart_items.
    cart_items is a list of (Name, Version, Command) tuples.

    For demo purposes, we just print them.
    """
    for (name, version, command) in cart_items:
        print(f"Running command for {name} v{version}: {command}")
    print("All commands run (demo).")

###################################
# Main HabitatApp and Pages
###################################

ctk.set_appearance_mode("System")  # "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

class HabitatApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Habitat")
        # Make it more square to reduce bottom "chin"
        self.geometry("420x420")
        self.resizable(False, False)

        # The cart will hold tuples of (Name, version, command).
        self.software_cart = []

        # Container for pages
        container = ctk.CTkFrame(self, corner_radius=0)
        container.pack(fill="both", expand=True)
        self.frames = {}

        # We have three pages: Welcome, Create, Cart.
        for Page in (WelcomePage, CreatePage, CartPage):
            page_name = Page.__name__
            frame = Page(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("WelcomePage")

    def show_frame(self, page_name: str):
        """Bring the specified page to the front, with any needed refresh."""
        frame = self.frames[page_name]
        frame.tkraise()

        if page_name == "CartPage":
            self.frames["CartPage"].refresh_cart()
        elif page_name == "CreatePage":
            self.frames["CreatePage"].update_cart_icon()

    def add_to_cart(self, name: str, version: str, command: str):
        """Add a (Name, version, command) tuple to software_cart if not duplicate."""
        new_item = (name, version, command)
        if new_item not in self.software_cart:
            self.software_cart.append(new_item)
            self.frames["CreatePage"].update_cart_icon()
            self.frames["CartPage"].refresh_cart()
        else:
            messagebox.showinfo("Duplicate Entry", f"'{name} v{version}' is already in the cart.")

    def clear_cart(self):
        """Utility to clear the entire cart."""
        self.software_cart.clear()
        self.frames["CartPage"].refresh_cart()
        self.frames["CreatePage"].update_cart_icon()

###################################
# Welcome Page
###################################

class WelcomePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Title
        title_label = ctk.CTkLabel(
            self,
            text="Welcome to Habitat",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        # Reduced padding to minimize blank space
        title_label.pack(pady=(15, 8))

        create_button = ctk.CTkButton(
            self,
            text="Create",
            command=lambda: controller.show_frame("CreatePage"),
            width=120
        )
        create_button.pack(pady=4)

        import_button = ctk.CTkButton(
            self,
            text="Import",
            command=self.import_file,
            width=120
        )
        import_button.pack(pady=4)

    def import_file(self):
        """
        Opens a file dialog to import only a YAML file.
        Then extracts (Name, version, command) tuples.
        """
        file_path = filedialog.askopenfilename(
            title="Import Dependencies (.yaml only)",
            filetypes=[("YAML Files", "*.yaml"), ("All Files", "*.*")]
        )
        if not file_path:
            return  # User cancelled
        if not file_path.lower().endswith(".yaml"):
            messagebox.showerror("Error", "Please select a .yaml file.")
            return

        try:
            self.controller.clear_cart()
            from extract_tuples import extract_tuples  # If local, keep direct reference.
        except ImportError:
            messagebox.showerror("Import Error", "extract_tuples function not found.")
            return
        except Exception as e:
            messagebox.showerror("Error", f"Error setting up import: {e}")
            return

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

###################################
# Create Page
###################################

class CreatePage(ctk.CTkFrame):
    """
    Allows user to add (Name, version, command) via text entries,
    plus a selection of popular libraries stored as tuples.

    We only display Name + Version in the UI text.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Container for input fields
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(fill="x", pady=5)

        # Entries for name, version, command
        self.name_entry = ctk.CTkEntry(input_frame, placeholder_text="Name", width=75)
        self.name_entry.grid(row=0, column=0, padx=3)

        self.version_entry = ctk.CTkEntry(input_frame, placeholder_text="Version", width=75)
        self.version_entry.grid(row=0, column=1, padx=3)

        self.command_entry = ctk.CTkEntry(input_frame, placeholder_text="Command", width=75)
        self.command_entry.grid(row=0, column=2, padx=3)

        add_button = ctk.CTkButton(input_frame, text="Add", command=self.add_custom_tuple, width=45)
        add_button.grid(row=0, column=3, padx=(3,0))

        # Cart button top-right
        self.cart_button = ctk.CTkButton(self, text="Cart (0)", command=self.go_to_cart, width=90)
        self.cart_button.pack(anchor="ne", padx=10, pady=(0,2))

        # Popular library tuples
        popular_label = ctk.CTkLabel(self, text="Popular Items:", font=ctk.CTkFont(size=14, weight="bold"))
        popular_label.pack(pady=(4,2))

        popular_frame = ctk.CTkFrame(self)
        popular_frame.pack(fill="x", pady=(0,5), padx=20)

        # Each item is (Name, version, command)
        self.popular_libraries = [
            ("Node.js", "latest", "npm install -g node"),
            ("Python", "3.10", "pip install python"),
            ("VSCode", "1.81.1", "code --install-extension")
        ]

        # Stack them vertically, narrower width
        for item in self.popular_libraries:
            name, version, _cmd = item
            text_display = f"{name} (v{version})"
            btn = ctk.CTkButton(
                popular_frame,
                text=text_display,
                command=lambda i=item: self.add_popular_tuple(i),
                width=180
            )
            btn.pack(pady=2)

        # Back button
        back_button = ctk.CTkButton(self, text="Back", command=lambda: controller.show_frame("WelcomePage"), width=60)
        back_button.pack(pady=(0,2))

        self.update_cart_icon()

    def add_custom_tuple(self):
        name = self.name_entry.get().strip()
        version = self.version_entry.get().strip()
        command = self.command_entry.get().strip()
        if name and version and command:
            self.controller.add_to_cart(name, version, command)
            self.name_entry.delete(0, tk.END)
            self.version_entry.delete(0, tk.END)
            self.command_entry.delete(0, tk.END)
            self.update_cart_icon()
        else:
            messagebox.showwarning("Input Error", "Please fill out Name, Version, and Command.")

    def add_popular_tuple(self, item):
        name, version, cmd = item
        self.controller.add_to_cart(name, version, cmd)
        self.update_cart_icon()

    def update_cart_icon(self):
        count = len(self.controller.software_cart)
        self.cart_button.configure(text=f"Cart ({count})")

    def go_to_cart(self):
        self.controller.show_frame("CartPage")

###################################
# Cart Page
###################################

class CartPage(ctk.CTkFrame):
    """
    Displays the (Name, version, command) tuples in the cart.
    Only shows Name + Version in the UI.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        title_label = ctk.CTkLabel(self, text="Shopping Cart", font=ctk.CTkFont(size=15, weight="bold"))
        title_label.pack(pady=(8,2))

        # Adjust scroll frame for square layout
        # Removing explicit height so it shrinks if no items.
        self.scroll_frame = ctk.CTkScrollableFrame(self, width=350)
        self.scroll_frame.pack(padx=10, pady=(0,2), fill="both", expand=True)

        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.pack(fill="x", pady=(0,5))

        run_button = ctk.CTkButton(bottom_frame, text="Run", command=self.on_run_commands, width=60)
        run_button.pack(side="left", padx=(10,0))

        back_button = ctk.CTkButton(bottom_frame, text="Back", command=self.on_back, width=60)
        back_button.pack(side="right", padx=(0,10))

    def refresh_cart(self):
        """Refreshes the cart display with just Name and Version."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        for idx, item in enumerate(self.controller.software_cart, start=1):
            name, version, _cmd = item

            item_frame = ctk.CTkFrame(self.scroll_frame)
            item_frame.pack(fill="x", pady=2, padx=5)

            label_text = f"{idx}. {name} (v{version})"
            label = ctk.CTkLabel(item_frame, text=label_text)
            label.pack(side="left", padx=5)

            remove_button = ctk.CTkButton(
                item_frame,
                text="X",
                width=25,
                command=lambda t=item: self.remove_from_cart(t)
            )
            remove_button.pack(side="right", padx=5)

    def remove_from_cart(self, tuple_item):
        if tuple_item in self.controller.software_cart:
            self.controller.software_cart.remove(tuple_item)
            self.refresh_cart()
            messagebox.showinfo("Removed", f"'{tuple_item[0]}' was removed.")
        else:
            messagebox.showwarning("Not Found", "Item is not in the cart.")

    def on_run_commands(self):
        if self.controller.software_cart:
            run_commands(self.controller.software_cart)
            messagebox.showinfo("Done", "Commands executed (see console output).")
        else:
            messagebox.showinfo("Empty Cart", "No items to install.")

    def on_back(self):
        self.controller.show_frame("CreatePage")
        self.controller.frames["CreatePage"].update_cart_icon()

    def tkraise(self, aboveThis=None):
        self.refresh_cart()
        super().tkraise(aboveThis)

if __name__ == "__main__":
    app = HabitatApp()
    app.mainloop()
