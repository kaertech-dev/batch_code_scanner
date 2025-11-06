"""
Batch Code Scanner Application
Main entry point for the application
"""
import tkinter as tk
from gui import BatchCodeScannerGUI


def main():
    """Initialize and run the application"""
    root = tk.Tk()
    app = BatchCodeScannerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()