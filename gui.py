import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import yaml

from extract_commands import extract_name

# Suppose you place extract_commands.py in the same folder and import its functions
# If you prefer, you can inline or replicate the logic below
# from extract_commands import extract_commands, run_commands, extract_name

####################
# Dummy placeholders 
####################

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
            for _, details in config[section].items():
                command = details.get("install_command")
                if command:
                    commands.append(command)
    return commands

def run_commands(commands):
    """
    Executes a list of commands (just printing here for demo).
    """
    for cmd in commands:
        print(f"Running command: {cmd}")
    print("All commands run (demo).")


###################################
# Main HabitatApp and Pages
###################################
ctk.set_appearance_mode("System")   # "System", "Dark", "Light"
ctk.set_default_color_theme("blue") # "blue", "green", "dark-blue"

class HabitatApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Habitat")
        
        # Fixed window size
        self.geometry("600x400")
        self.resizable(False, False)

        # This list will hold the software we want to install:
        self.software_cart = []
        self.names = []

        # Container for pages
        container = ctk.CTkFrame(self, corner_radius=0)
        container.pack(fill="both", expand=True)

        self.frames = {}

        for Page in (WelcomePage, CreatePage, CartPage):
            page_name = Page.__name__
            frame = Page(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("WelcomePage")

    def show_frame(self, page_name: str):
        """Bring the specified page to the front."""
        frame = self.frames[page_name]
        frame.tkraise()

    def add_to_cart(self, item):
        """Add a given item (string or dict) to the software cart."""
        if item not in self.software_cart:
            self.software_cart.append(item)
    
        # Force update the cart icon (count) if we're on CreatePage
            create_page = self.frames["CreatePage"]
            create_page.update_cart_icon()
        else:
            messagebox.showinfo("Duplicate Entry", f"'{item}' is already in the cart.")
    def add_to_names(self, name):
        """Add a given name to the names list."""
        if name not in self.names:
            self.names.append(name)
        else:
            messagebox.showinfo("Duplicate Entry", f"'{name}' is already in the list.")
    
    def clear_cart(self):
        """Utility to clear the cart if needed."""
        self.software_cart.clear()
        self.names.clear() 

class WelcomePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        title_label = ctk.CTkLabel(
            self,
            text="Welcome to Habitat",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=30)

        # Create button
        create_button = ctk.CTkButton(
            self,
            text="Create",
            command=lambda: controller.show_frame("CreatePage")
        )
        create_button.pack(pady=10)

        # Import button
        import_button = ctk.CTkButton(
            self,
            text="Import",
            command=self.import_file
        )
        import_button.pack(pady=10)

    def import_file(self):
        """
        Open a file dialog to import only a YAML file.
        If user selects a valid YAML, parse it and store in the cart,
        then go to the CartPage to show the user what is about to be installed.
        """
        file_path = filedialog.askopenfilename(
            title="Import Dependencies (.yaml only)",
            filetypes=[("YAML Files", "*.yaml"), ("All Files", "*.*")]
        )

        if not file_path:
            # User cancelled
            return

        # Check file extension
        if not file_path.lower().endswith(".yaml"):
            messagebox.showerror("Error", "Please select a .yaml file.")
            return

        try:
            # Clear any existing cart items
            self.controller.clear_cart()

            # Extract commands from the YAML
            names = extract_name(file_path)
            commands = extract_commands(file_path)
            # For demonstration, let's store them as strings in the cart
            if commands:
                for cmd in commands:
                    self.controller.add_to_cart(cmd)
            else:
                messagebox.showinfo("No Commands Found", "No install commands found in YAML.")

            if names:
                for name in names:
                    self.controller.add_to_names(name)
            else: 
                messagebox.showinfo("No Names Found", "No names found in YAML.")

            # Go to CartPage to see what we have
            self.controller.show_frame("CartPage")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse YAML: {e}")


class CreatePage(ctk.CTkFrame):
    """
    A page that shows some popular libraries as clickable items and
    a text entry for custom libraries. 
    A 'cart' button in the top-right corner shows how many items are in the cart.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Top frame for search and cart
        top_frame = ctk.CTkFrame(self)
        top_frame.pack(fill="x", pady=10)

        # Search entry for custom libraries
        self.search_entry = ctk.CTkEntry(top_frame, placeholder_text="Type a library/framework...")
        self.search_entry.pack(side="left", padx=10)

        # "Add" button 
        add_button = ctk.CTkButton(top_frame, text="Add", command=self.add_custom_library)
        add_button.pack(side="left", padx=5)

        # Cart button on the right
        self.cart_button = ctk.CTkButton(top_frame, text="Cart (0)", command=self.go_to_cart)
        self.cart_button.pack(side="right", padx=10)

        # A frame to display popular libraries
        popular_frame = ctk.CTkFrame(self)
        popular_frame.pack(fill="both", expand=True, pady=10)

        ctk.CTkLabel(popular_frame, text="Popular Libraries:", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)

        # Example popular libraries
        self.popular_libraries = ["Node.js", "Python", "VSCode"]
        for lib in self.popular_libraries:
            btn = ctk.CTkButton(popular_frame, text=lib, command=lambda x=lib: self.add_popular_library(x))
            btn.pack(pady=5)

        # Back button
        back_button = ctk.CTkButton(self, text="Back", command=lambda: controller.show_frame("WelcomePage"))
        back_button.pack(pady=5)

        # Update cart icon initially
        self.update_cart_icon()

    def add_popular_library(self, lib_name):
        self.controller.add_to_names(lib_name)
        self.controller.add_to_cart(lib_name)
        self.update_cart_icon()

    def add_custom_library(self):
        custom_lib = self.search_entry.get().strip()
        if custom_lib:
            self.controller.add_to_cart(custom_lib)
            self.search_entry.delete(0, tk.END)
            self.update_cart_icon()

    def update_cart_icon(self):
        count = len(self.controller.software_cart)
        self.cart_button.configure(text=f"Cart ({count})")

    def go_to_cart(self):
        # Navigate to cart page
        self.controller.show_frame("CartPage")


class CartPage(ctk.CTkFrame):
    """
    Shows all items in the cart and has a "Run commands" button
    to perform the installation (via run_commands).
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        title_label = ctk.CTkLabel(self, text="Shopping Cart", font=ctk.CTkFont(size=18, weight="bold"))
        title_label.pack(pady=10)

        # Scrollable frame to list items
        self.scroll_frame = ctk.CTkScrollableFrame(self, width=500, height=200)
        self.scroll_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Buttons at bottom
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.pack(fill="x", pady=10)

        run_button = ctk.CTkButton(bottom_frame, text="Run commands", command=self.on_run_commands)
        run_button.pack(side="left", padx=20)

        back_button = ctk.CTkButton(bottom_frame, text="Back", command=self.on_back)
        back_button.pack(side="right", padx=20)

    def refresh_cart(self):
        """ Refreshes the cart display dynamically """
        # Clear previous items
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Display items with remove buttons
        for idx, item in enumerate(self.controller.software_cart, start=1):
            item_frame = ctk.CTkFrame(self.scroll_frame)
            item_frame.pack(fill="x", pady=2, padx=5)

            label = ctk.CTkLabel(item_frame, text=f"{idx}. {item}")
            label.pack(side="left", padx=5)

            remove_button = ctk.CTkButton(item_frame, text="Remove", width=80, command=lambda i=item: self.remove_from_cart(i))
            remove_button.pack(side="right", padx=5)

    def remove_from_cart(self, item):
        """ Removes an item from the cart and updates the UI """
        if item in self.controller.software_cart:
            self.controller.software_cart.remove(item)
            self.refresh_cart()  # Refresh UI
            messagebox.showinfo("Removed", f"'{item}' was removed from the cart.")
        else:
            messagebox.showwarning("Not Found", f"'{item}' is not in the cart.")

    def on_run_commands(self):
        """ Runs the installation commands for all selected software """
        if self.controller.software_cart:
            run_commands(self.controller.software_cart)
            messagebox.showinfo("Done", "Commands executed (see console output).")
        else:
            messagebox.showinfo("Empty Cart", "No items to install.")

    def on_back(self):
        """ Navigates back to the previous page """
        self.controller.show_frame("CreatePage")
        create_page = self.controller.frames["CreatePage"]
        create_page.update_cart_icon()
        
        
    def tkraise(self, aboveThis=None):
        """ Overrides tkraise to update cart items dynamically """
        self.refresh_cart()
        super().tkraise(aboveThis)


if __name__ == "__main__":
    app = HabitatApp()
    app.mainloop()
