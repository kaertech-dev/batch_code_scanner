import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pymysql
import csv
from datetime import datetime
import os

class BatchCodeScanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Batch Code Scanner")
        self.root.geometry("900x650")
        self.root.configure(bg="#f0f0f0")
        
        # Database configuration
        self.config = {
            'host': '192.168.1.38',
            'user': 'testing',
            'password': 'testing',
            'database': 'ledtech'
        }
        
        # Create main frame
        main_frame = tk.Frame(root, bg="#f0f0f0", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="Batch Code Scanner", 
                              font=("Arial", 20, "bold"), bg="#f0f0f0", fg="#333")
        title_label.pack(pady=(0, 20))
        
        # === DROPDOWN + INPUT FRAME ===
        input_frame = tk.Frame(main_frame, bg="#f0f0f0")
        input_frame.pack(fill=tk.X, pady=(0, 20))

        # Dropdown for scan type
        tk.Label(input_frame, text="Scan Mode:", font=("Arial", 12), bg="#f0f0f0").pack(side=tk.LEFT, padx=(0, 10))
        
        self.scan_mode = tk.StringVar(value="Serial Number")
        mode_dropdown = ttk.Combobox(input_frame, textvariable=self.scan_mode, state="readonly",
                                    values=["Serial Number", "Batch Code"], width=15, font=("Arial", 11))
        mode_dropdown.pack(side=tk.LEFT, padx=(0, 15))
        mode_dropdown.bind("<<ComboboxSelected>>", self.on_mode_change)

        # Dynamic label
        self.input_label = tk.Label(input_frame, text="Serial Number:", font=("Arial", 12), bg="#f0f0f0")
        self.input_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.scan_entry = tk.Entry(input_frame, font=("Arial", 12), width=30)
        self.scan_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.scan_entry.bind('<Return>', lambda e: self.scan_input())
        self.scan_entry.focus()
        
        scan_btn = tk.Button(input_frame, text="Scan", font=("Arial", 11, "bold"),
                            bg="#4CAF50", fg="white", padx=20, pady=5,
                            command=self.scan_input, cursor="hand2")
        scan_btn.pack(side=tk.LEFT)

        # Info frame
        info_frame = tk.LabelFrame(main_frame, text="Batch Information", 
                                  font=("Arial", 12, "bold"), bg="#f0f0f0", 
                                  padx=15, pady=15)
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Batch Code info
        batch_info_frame = tk.Frame(info_frame, bg="#f0f0f0")
        batch_info_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(batch_info_frame, text="Batch Code:", font=("Arial", 11, "bold"),
                bg="#f0f0f0").pack(side=tk.LEFT)
        self.batch_label = tk.Label(batch_info_frame, text="N/A", 
                                    font=("Arial", 11), bg="#f0f0f0", fg="#0066cc")
        self.batch_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # PO Number info
        po_info_frame = tk.Frame(info_frame, bg="#f0f0f0")
        po_info_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(po_info_frame, text="PO Number:", font=("Arial", 11, "bold"),
                bg="#f0f0f0").pack(side=tk.LEFT)
        self.po_label = tk.Label(po_info_frame, text="N/A", 
                                font=("Arial", 11), bg="#f0f0f0", fg="#0066cc")
        self.po_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Count info
        count_info_frame = tk.Frame(info_frame, bg="#f0f0f0")
        count_info_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(count_info_frame, text="Total Serial Numbers:", 
                font=("Arial", 11, "bold"), bg="#f0f0f0").pack(side=tk.LEFT)
        self.count_label = tk.Label(count_info_frame, text="0", 
                                   font=("Arial", 11), bg="#f0f0f0", fg="#0066cc")
        self.count_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Table frame
        table_frame = tk.LabelFrame(main_frame, text="Serial Numbers in Batch", 
                                   font=("Arial", 12, "bold"), bg="#f0f0f0",
                                   padx=10, pady=10)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create Treeview
        columns = ("Serial Number", "Batch Code", "PO Number")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER, width=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Status bar
        self.status_label = tk.Label(main_frame, text="Ready to scan...", 
                                     font=("Arial", 10), bg="#f0f0f0", 
                                     fg="#666", anchor=tk.W)
        self.status_label.pack(fill=tk.X, pady=(10, 0))
        
    def on_mode_change(self, event=None):
        """Update label when scan mode changes"""
        mode = self.scan_mode.get()
        self.input_label.config(text=f"{mode}:" if mode == "Serial Number" else "Batch Code:")
        self.scan_entry.delete(0, tk.END)
        self.scan_entry.focus()

    def get_db_connection(self):
        """Create and return database connection"""
        try:
            db = pymysql.connect(**self.config, cursorclass=pymysql.cursors.DictCursor)
            return db
        except pymysql.Error as err:
            messagebox.showerror("Database Error", f"Failed to connect to database:\n{err}")
            return None
    
    def scan_input(self):
        """Handle scanning based on selected mode"""
        input_value = self.scan_entry.get().strip()
        mode = self.scan_mode.get()

        if not input_value:
            messagebox.showwarning("Input Required", f"Please enter a {mode.lower()}.")
            return
        
        db = self.get_db_connection()
        if not db:
            return
        
        cursor = db.cursor()
        
        try:
            if mode == "Serial Number":
                # === SCAN BY SERIAL NUMBER ===
                cursor.execute(
                    "SELECT batch_code, po_num FROM faceware_assembly1 WHERE serial_num = %s", 
                    (input_value,)
                )
                assembly_data = cursor.fetchone()
                
                if not assembly_data:
                    messagebox.showwarning("Not Found", 
                                         f"Serial '{input_value}' not found in assembly1 table.")
                    self.status_label.config(text=f"Serial number '{input_value}' not found")
                    return
                
                batch_code = assembly_data["batch_code"]
                po_num = assembly_data["po_num"]
                
            else:  # mode == "Batch Code"
                # === SCAN BY BATCH CODE ===
                cursor.execute(
                    "SELECT batch_code, po_num FROM faceware_assembly1 WHERE batch_code = %s LIMIT 1", 
                    (input_value,)
                )
                assembly_data = cursor.fetchone()
                
                if not assembly_data:
                    messagebox.showwarning("Not Found", 
                                         f"Batch code '{input_value}' not found.")
                    self.status_label.config(text=f"Batch code '{input_value}' not found")
                    return
                
                batch_code = assembly_data["batch_code"]
                po_num = assembly_data["po_num"]
            
            # === COMMON LOGIC: Fetch all serials in batch ===
            cursor.execute(
                """SELECT serial_num, batch_code, po_num 
                   FROM faceware_assembly1 
                   WHERE batch_code = %s 
                   ORDER BY serial_num""", 
                (batch_code,)
            )
            all_serials = cursor.fetchall()
            
            # Update UI
            self.batch_label.config(text=batch_code)
            self.po_label.config(text=po_num)
            self.count_label.config(text=str(len(all_serials)))
            
            # Clear and populate tree
            for item in self.tree.get_children():
                self.tree.delete(item)
            for row in all_serials:
                self.tree.insert("", tk.END, values=(
                    row["serial_num"], 
                    row["batch_code"], 
                    row["po_num"]
                ))
            
            # Auto-download CSV
            self.auto_download_csv(all_serials, batch_code)
            
            # Update status
            self.status_label.config(
                text=f"Found {len(all_serials)} serials in batch '{batch_code}' - CSV downloaded"
            )
            
            # Clear and refocus
            self.scan_entry.delete(0, tk.END)
            self.scan_entry.focus()
            
        except pymysql.Error as err:
            messagebox.showerror("Database Error", f"Error querying database:\n{err}")
            self.status_label.config(text="Error occurred during scan")
        finally:
            cursor.close()
            db.close()
    
    def auto_download_csv(self, data, batch_code):
        """Automatically download CSV file with batch data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"batch_{batch_code}_{timestamp}.csv"
        
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        if not os.path.exists(downloads_path):
            downloads_path = os.getcwd()
        
        filepath = os.path.join(downloads_path, filename)
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Serial Number", "Batch Code", "PO Number"])
                for row in data:
                    writer.writerow([row["serial_num"], row["batch_code"], row["po_num"]])
            
            self.status_label.config(text=f"CSV saved: {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to save CSV:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BatchCodeScanner(root)
    root.mainloop()