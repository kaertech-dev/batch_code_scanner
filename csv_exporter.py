"""
CSV export functionality for batch data
"""
import csv
import os
from datetime import datetime
from typing import List, Dict, Any


class CSVExporter:
    """Handles CSV file generation and export"""
    
    @staticmethod
    def get_downloads_path() -> str:
        """Get the user's Downloads folder path"""
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        if not os.path.exists(downloads_path):
            downloads_path = os.getcwd()
        return downloads_path
    
    @staticmethod
    def generate_filename(batch_code: str) -> str:
        """Generate filename with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"batch_{batch_code}_{timestamp}.csv"
    
    def export_to_csv(self, data: List[Dict[str, Any]], batch_code: str) -> str:
        """
        Export batch data to CSV file
        
        Args:
            data: List of dictionaries containing serial numbers and batch info
            batch_code: The batch code for filename generation
            
        Returns:
            Full path to the saved CSV file
            
        Raises:
            Exception: If file writing fails
        """
        filename = self.generate_filename(batch_code)
        downloads_path = self.get_downloads_path()
        filepath = os.path.join(downloads_path, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write headers
            writer.writerow(["Serial Number", "Batch Code", "PO Number"])
            
            # Write data
            for row in data:
                writer.writerow([
                    row["serial_num"],
                    row["batch_code"],
                    row["po_num"]
                ])
        
        return filepath