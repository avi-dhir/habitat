import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog

# Global style settings for CustomTkinter
ctk.set_appearance_mode("System")   # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue") # Themes: "blue" (default), "green", "dark-blue"

class HabitatApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Habitat")
        self.geometry("600x400")
        
        container = ctk.CTkFrame(self, corner_radius=0)
        container.pack(fill="both", expand=True)

        self.frames = {}

        # Initialize each page and store in frames dict
        for Page in (WelcomePage, NodePage, SoftwarePage):
            page_name = Page.__name__
            frame = Page(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Show the Welcome page by default
        self.show_frame("WelcomePage")

    def show_frame(self, page_name: str):
        """Bring the specified page to the front."""
        frame = self.frames[page_name]
        frame.tkraise()


class WelcomePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # "Welcome to Habitat" label
        self.title_label = ctk.CTkLabel(
            self,
            text="Welcome to Habitat",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=30)

        # "Create" button
        self.create_button = ctk.CTkButton(
            self,
            text="Create",
            command=self.go_to_node_page
        )
        self.create_button.pack(pady=10)

        # "Import" button
        self.import_button = ctk.CTkButton(
            self,
            text="Import",
            command=self.import_file
        )
        self.import_button.pack(pady=10)

    def go_to_node_page(self):
        """Navigate to the NodePage."""
        self.controller.show_frame("NodePage")

    def import_file(self):
        """Open a file dialog to import a file with software/dependencies."""
        file_path = filedialog.askopenfilename(
            title="Import Dependencies",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            # You can read the file, parse dependencies, etc.
            print(f"Imported file: {file_path}")
            # After importing, maybe go to NodePage or some other logic:
            self.controller.show_frame("NodePage")


class NodePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Search bar
        self.search_entry = ctk.CTkEntry(
            self,
            placeholder_text="Search for a node..."
        )
        self.search_entry.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        # "Cart" icon placeholder (can be replaced with an actual image)
        self.cart_button = ctk.CTkButton(
            self,
            text="Cart",
            command=self.go_to_software_page
        )
        self.cart_button.grid(row=0, column=1, padx=10, pady=20)

        # Node list frame
        self.node_list_frame = ctk.CTkFrame(self)
        self.node_list_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")

        # Populate with a few placeholder nodes
        for i in range(5):
            node_label = ctk.CTkLabel(self.node_list_frame, text=f"Node {i+1}")
            node_label.pack(anchor="w", pady=2)

        # Button to go back to welcome
        self.back_button = ctk.CTkButton(
            self,
            text="Back to Welcome",
            command=lambda: controller.show_frame("WelcomePage")
        )
        self.back_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Make rows/columns responsive
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(1, weight=1)

    def go_to_software_page(self):
        """Navigate to the SoftwarePage."""
        self.controller.show_frame("SoftwarePage")


class SoftwarePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # A label to indicate we are adding software packages
        self.title_label = ctk.CTkLabel(
            self,
            text="Add/Install Software Packages",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.title_label.pack(pady=10)

        # Frame to hold software checkboxes
        self.software_frame = ctk.CTkFrame(self)
        self.software_frame.pack(pady=10, fill="both", expand=True)

        # Example software packages
        self.software_vars = {}
        software_list = ["Node.js", "Python", "Docker", "Git", "Nginx"]
        for software in software_list:
            var = tk.BooleanVar(value=False)
            chk = ctk.CTkCheckBox(
                self.software_frame,
                text=software,
                variable=var
            )
            chk.pack(anchor="w", pady=2)
            self.software_vars[software] = var

        # Bottom frame with Run and Export
        self.bottom_frame = ctk.CTkFrame(self)
        self.bottom_frame.pack(fill="x", pady=10)

        self.run_button = ctk.CTkButton(
            self.bottom_frame,
            text="Run",
            command=self.run_software_install
        )
        self.run_button.pack(side="left", padx=20)

        self.export_button = ctk.CTkButton(
            self.bottom_frame,
            text="Export",
            command=self.export_software_list
        )
        self.export_button.pack(side="left", padx=20)

        # Button to go back to NodePage
        self.back_button = ctk.CTkButton(
            self.bottom_frame,
            text="Back",
            command=lambda: controller.show_frame("NodePage")
        )
        self.back_button.pack(side="right", padx=20)

    def run_software_install(self):
        """Run the installation commands for the selected software."""
        selected = [s for s, var in self.software_vars.items() if var.get()]
        print(f"Installing: {selected}")
        # Here you would actually run the install commands (subprocess, etc.)

    def export_software_list(self):
        """Export the list of selected software to a file."""
        selected = [s for s, var in self.software_vars.items() if var.get()]
        if selected:
            export_path = filedialog.asksaveasfilename(
                title="Export Software List",
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
            )
            if export_path:
                with open(export_path, "w") as f:
                    for software in selected:
                        f.write(software + "\n")
                print(f"Exported to: {export_path}")
        else:
            print("No software selected for export.")


if __name__ == "__main__":
    app = HabitatApp()
    app.mainloop()
