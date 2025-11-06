"""
GUI components for the Batch Code Scanner
"""
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from typing import Optional
from database import DatabaseManager
from csv_exporter import CSVExporter
from config import WINDOW_TITLE, WINDOW_SIZE, WINDOW_BG, PRIMARY_COLOR, TEXT_COLOR, INFO_COLOR, STATUS_COLOR, TEXT_COLOR1

class BatchCodeScannerGUI:
    """Main GUI class for the Batch Code Scanner application"""
    
    def __init__(self, root):
        self.root = root
        self.db_manager = DatabaseManager()
        self.csv_exporter = CSVExporter()
        
        self._setup_window()
        self._create_widgets()
    
    def _setup_window(self):
        """Configure the main window"""
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.configure(bg=WINDOW_BG)
    
    def _create_widgets(self):
        """Create all GUI widgets"""
        # Main frame
        main_frame = tk.Frame(self.root, bg=WINDOW_BG, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self._create_title(main_frame)
        self._create_input_section(main_frame)
        self._create_info_section(main_frame)
        self._create_table_section(main_frame)
        self._create_status_bar(main_frame)
    
    def _create_title(self, parent):
        """Create title label with logo and border"""
        # Create a frame with border for the header
        header_frame = tk.Frame(
            parent, 
            bg="white",
            relief=tk.RIDGE,
            borderwidth=2,
            padx=20,
            pady=15
        )
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Inner frame to hold logo and title
        title_frame = tk.Frame(header_frame, bg="white")
        title_frame.pack()
        
        # Add logo on the left
        self._add_logo(title_frame)
        
        # Add title text
        title_label = tk.Label(
            title_frame,
            text=WINDOW_TITLE,
            font=("Arial", 20, "bold"),
            bg="white",
            fg=TEXT_COLOR
        )
        title_label.pack(side=tk.LEFT, padx=(15, 0))
    
    def _create_input_section(self, parent):
        """Create input section with dropdown, dynamic label, entry, and scan button"""
        input_frame = tk.Frame(parent, bg=WINDOW_BG)
        input_frame.pack(fill=tk.X, pady=(0, 20))
        
        # === SCAN MODE DROPDOWN ===
        tk.Label(
            input_frame,
            text="Scan Mode:",
            font=("Arial", 12),
            bg=WINDOW_BG,
            fg=TEXT_COLOR1
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.scan_mode = tk.StringVar(value="Serial Number")
        mode_dropdown = ttk.Combobox(
            input_frame,
            textvariable=self.scan_mode,
            values=["Serial Number", "Batch Code"],
            state="readonly",
            width=15,
            font=("Arial", 11)
        )
        mode_dropdown.pack(side=tk.LEFT, padx=(0, 15))
        mode_dropdown.bind("<<ComboboxSelected>>", self._on_mode_change)

        # === DYNAMIC LABEL ===
        self.input_label = tk.Label(
            input_frame,
            text="Serial Number:",
            font=("Arial", 12),
            bg=WINDOW_BG,
            fg=TEXT_COLOR1
        )
        self.input_label.pack(side=tk.LEFT, padx=(0, 10))

        # === INPUT ENTRY ===
        self.scan_entry = tk.Entry(input_frame, font=("Arial", 12), width=30)
        self.scan_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.scan_entry.bind('<Return>', lambda e: self.scan_input())
        self.scan_entry.focus()

        # === SCAN BUTTON ===
        scan_btn = tk.Button(
            input_frame,
            text="Scan",
            font=("Arial", 11, "bold"),
            bg=PRIMARY_COLOR,
            fg="white",
            padx=20,
            pady=5,
            command=self.scan_input,
            cursor="hand2"
        )
        scan_btn.pack(side=tk.LEFT)


    def _on_mode_change(self, event=None):
        """Update input label when scan mode changes"""
        mode = self.scan_mode.get()
        label_text = "Serial Number:" if mode == "Serial Number" else "Batch Code:"
        self.input_label.config(text=label_text)
        self.scan_entry.delete(0, tk.END)
        self.scan_entry.focus()


    def scan_input(self):
        """Handle scanning based on selected mode (Serial or Batch Code)"""
        input_value = self.scan_entry.get().strip()
        mode = self.scan_mode.get()

        if not input_value:
            messagebox.showwarning("Input Required", f"Please enter a {mode.lower()}.")
            return

        try:
            if mode == "Serial Number":
                # === SCAN BY SERIAL NUMBER ===
                assembly_data = self.db_manager.get_batch_info(input_value)
                if not assembly_data:
                    messagebox.showwarning(
                        "Not Found",
                        f"Serial '{input_value}' not found in assembly1 table."
                    )
                    self.status_label.config(text=f"Serial '{input_value}' not found")
                    return
                batch_code = assembly_data["batch_code"]
                po_num = assembly_data["po_num"]

            else:  # mode == "Batch Code"
                # === SCAN BY BATCH CODE ===
                assembly_data = self.db_manager.get_batch_info_by_batch(input_value)
                if not assembly_data:
                    messagebox.showwarning(
                        "Not Found",
                        f"Batch code '{input_value}' not found."
                    )
                    self.status_label.config(text=f"Batch '{input_value}' not found")
                    return
                batch_code = assembly_data["batch_code"]
                po_num = assembly_data["po_num"]

            # === COMMON: Fetch all serials in batch ===
            all_serials = self.db_manager.get_all_serials_in_batch(batch_code)

            # Update UI
            self.batch_label.config(text=batch_code)
            self.po_label.config(text=po_num)
            self.count_label.config(text=str(len(all_serials)))
            self._update_table(all_serials)

            # Export CSV
            filepath = self.csv_exporter.export_to_csv(all_serials, batch_code)

            # Update status
            self.status_label.config(
                text=f"Found {len(all_serials)} serials in batch '{batch_code}' - CSV downloaded"
            )

            # Clear and refocus
            self.scan_entry.delete(0, tk.END)
            self.scan_entry.focus()

        except ConnectionError as err:
            messagebox.showerror("Database Error", str(err))
            self.status_label.config(text="Database connection failed")
        except Exception as err:
            messagebox.showerror("Error", f"An error occurred: {err}")
            self.status_label.config(text="Error occurred during scan")
    
    def _add_logo(self, parent):
        """Add company logo"""
        try:
            # Load and resize the logo
            logo_path = r"C:\Users\cadetautomation\Desktop\batch_code\kaertech_logo512.png"
            
            if os.path.exists(logo_path):
                image = Image.open(logo_path)
                # Resize to fit nicely next to title
                image = image.resize((60, 60), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                
                # Create label to display the logo
                logo_label = tk.Label(
                    parent,
                    image=photo,
                    bg="white"
                )
                logo_label.image = photo  # Keep a reference!
                logo_label.pack(side=tk.LEFT)
            else:
                print(f"Logo file not found at: {logo_path}")
        except Exception as e:
            # If logo fails to load, just skip it silently
            print(f"Logo not loaded: {e}")
    
    def _create_info_section(self, parent):
        """Create information display section"""
        info_frame = tk.LabelFrame(
            parent,
            text="Batch Information",
            font=("Arial", 12, "bold"),
            bg=WINDOW_BG,
            fg=TEXT_COLOR1,
            padx=15,
            pady=15
        )
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Batch Code
        self._create_info_row(info_frame, "Batch Code:", "batch_label")
        
        # PO Number
        self._create_info_row(info_frame, "PO Number:", "po_label")
        
        # Count
        self._create_info_row(info_frame, "Total Serial Numbers:", "count_label", default="0")
    
    def _create_info_row(self, parent, label_text: str, attr_name: str, default: str = "N/A"):
        """Helper method to create info row"""
        frame = tk.Frame(parent, bg=WINDOW_BG)
        frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            frame,
            text=label_text,
            font=("Arial", 11, "bold"),
            bg=WINDOW_BG,
            fg=TEXT_COLOR1
        ).pack(side=tk.LEFT)
        
        label = tk.Label(
            frame,
            text=default,
            font=("Arial", 11),
            bg=WINDOW_BG,
            fg=INFO_COLOR
        )
        label.pack(side=tk.LEFT, padx=(10, 0))
        
        setattr(self, attr_name, label)
    
    def _create_table_section(self, parent):
        """Create table section with treeview"""
        table_frame = tk.LabelFrame(
            parent,
            text="Serial Numbers in Batch",
            font=("Arial", 12, "bold"),
            bg=WINDOW_BG,
            fg=TEXT_COLOR1,
            padx=10,
            pady=10
        )
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create Treeview
        columns = ("Serial Number", "Batch Code", "PO Number")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=15
        )
        
        # Define headings
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER, width=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_status_bar(self, parent):
        """Create status bar"""
        self.status_label = tk.Label(
            parent,
            text="Ready to scan...",
            font=("Arial", 10),
            bg=WINDOW_BG,
            fg=STATUS_COLOR,
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X, pady=(10, 0))
    
    def scan_serial(self):
        """Main function to scan serial number and retrieve batch data"""
        serial_num = self.serial_entry.get().strip()
        
        if not serial_num:
            messagebox.showwarning("Input Required", "Please enter a serial number.")
            return
        
        try:
            # Get batch info
            assembly_data = self.db_manager.get_batch_info(serial_num)
            
            if not assembly_data:
                messagebox.showwarning(
                    "Not Found",
                    f"⚠️ Serial '{serial_num}' not found in assembly1 table."
                )
                self.status_label.config(text=f"Serial number '{serial_num}' not found")
                return
            
            batch_code = assembly_data["batch_code"]
            po_num = assembly_data["po_num"]
            
            # Update info labels
            self.batch_label.config(text=batch_code)
            self.po_label.config(text=po_num)
            
            # Get all serial numbers in batch
            all_serials = self.db_manager.get_all_serials_in_batch(batch_code)
            
            # Update table
            self._update_table(all_serials)
            
            # Update count
            self.count_label.config(text=str(len(all_serials)))
            
            # Export to CSV
            filepath = self.csv_exporter.export_to_csv(all_serials, batch_code)
            
            # Update status
            self.status_label.config(
                text=f"✓ Found {len(all_serials)} serial numbers in batch '{batch_code}' - CSV downloaded"
            )
            
            # Clear entry and refocus
            self.serial_entry.delete(0, tk.END)
            self.serial_entry.focus()
            
        except ConnectionError as err:
            messagebox.showerror("Database Error", str(err))
            self.status_label.config(text="Database connection failed")
        except Exception as err:
            messagebox.showerror("Error", f"An error occurred: {err}")
            self.status_label.config(text="Error occurred during scan")
    
    def _update_table(self, data):
        """Update the treeview table with data"""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Insert new data
        for row in data:
            self.tree.insert("", tk.END, values=(
                row["serial_num"],
                row["batch_code"],
                row["po_num"]
            ))