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
    Reads the YAML configuration file and attempts to extract:
      name, version, install_command
    for each defined item in package_managers, environment, or developer_tools.

    Returns a list of (name:str, version:str, command:str) tuples.
    """
    with open(config_path, "r") as file:
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

        try:
            self.controller.clear_cart()
            from extract_tuples import extract_tuples
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
            width=160,  # Doubled from 80 to 160
            justify="center"
        )
        self.name_entry.grid(row=0, column=0, padx=8, pady=5, columnspan=3)  # Increased column span

        search_button = ctk.CTkButton(
            input_frame,
            text="Search",
            command=self.search_item,
            width=60,
        )
        search_button.grid(row=0, column=3, padx=8, pady=5)  # Moved to the last column

        # Cart button on the same row
        self.cart_button = ctk.CTkButton(
            input_frame,
            text="Cart (0)",
            width=70,
            command=lambda: self.controller.show_frame("CartPage")
        )
        self.cart_button.grid(row=0, column=4, padx=8, pady=5)  # Shifted one column to the right if needed


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

        for item in self.popular_libraries:
            name, version, cmd = item
            display_text = f"{name} (v{version})"
            btn = ctk.CTkButton(
                popular_frame,
                text=display_text,
                width=180,
                command=lambda i=item: self.add_popular_tuple(i),
            )
            btn.pack(pady=4, anchor="center")

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
        version = self.version_entry.get().strip()
        command = ""
        if name and version:
            self.controller.add_to_cart(name, version, command)
            # Clear entries
            self.name_entry.delete(0, tk.END)
            self.version_entry.delete(0, tk.END)
            self.update_cart_button()
        else:
            messagebox.showwarning("Input Error", "Please fill out both Name and Version.")

    def add_popular_tuple(self, item):
        name, version, cmd = item
        self.controller.add_to_cart(name, version, cmd)
        self.update_cart_button()

    def update_cart_button(self):
        """Sets the cart button text to 'Cart (#)'."""
        count = len(self.controller.software_cart)
        self.cart_button.configure(text=f"Cart ({count})")


class CartPage(ctk.CTkFrame):
    """
    Displays (Name, version) from the cart but not the command in the UI.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=0, border_width=0, fg_color="transparent")
        self.controller = controller

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

        bottom_frame = ctk.CTkFrame(
            self, corner_radius=0, border_width=0, fg_color="transparent"
        )
        bottom_frame.pack(fill="x", pady=6)

        run_button = ctk.CTkButton(
            bottom_frame, text="Run", width=60, command=self.on_run_commands
        )
        run_button.pack(side="right", padx=(0, 20))

        back_button = ctk.CTkButton(
            bottom_frame, text="Back", width=60, command=self.on_back
        )
        back_button.pack(side="left", padx=(20, 0))

    def refresh_cart(self):
        """Refreshes the cart display with Name + Version only."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        for idx, item in enumerate(self.controller.software_cart, start=1):
            name, version, _cmd = item
            item_frame = ctk.CTkFrame(
                self.scroll_frame,
                corner_radius=0,
                border_width=0,
                fg_color="transparent"
            )
            item_frame.pack(fill="x", pady=4, padx=15)

            label_text = f"{idx}. {name} (v{version})"
            label = ctk.CTkLabel(item_frame, text=label_text)
            label.pack(side="left", padx=5)

            remove_button = ctk.CTkButton(
                item_frame, text="X", width=25, command=lambda t=item: self.remove_from_cart(t)
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
        self.controller.frames["CreatePage"].update_cart_button()

    def tkraise(self, aboveThis=None):
        self.refresh_cart()
        super().tkraise(aboveThis)


if __name__ == "__main__":
    app = HabitatApp()
    app.mainloop()
