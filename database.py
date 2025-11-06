"""
Database operations for the Batch Code Scanner
"""
import pymysql
from typing import Optional, List, Dict, Any
from config import DB_CONFIG

class DatabaseManager:
    """Handles all database operations"""
    
    def __init__(self):
        self.config = DB_CONFIG
    
    def get_connection(self) -> Optional[pymysql.connections.Connection]:
        """Create and return database connection"""
        try:
            db = pymysql.connect(
                **self.config, 
                cursorclass=pymysql.cursors.DictCursor
            )
            return db
        except pymysql.Error as err:
            raise ConnectionError(f"Failed to connect to database: {err}")
    
    def get_batch_info(self, serial_num: str) -> Optional[Dict[str, Any]]:
        """
        Get batch_code and po_num for a given serial number
        
        Args:
            serial_num: The serial number to look up
            
        Returns:
            Dictionary with batch_code and po_num, or None if not found
        """
        db = self.get_connection()
        cursor = db.cursor()
        
        try:
            cursor.execute(
                "SELECT batch_code, po_num FROM faceware_assembly1 WHERE serial_num = %s",
                (serial_num,)
            )
            result = cursor.fetchone()
            return result
        finally:
            cursor.close()
            db.close()
    
    def get_all_serials_in_batch(self, batch_code: str) -> List[Dict[str, Any]]:
        """
        Get all serial numbers with the same batch_code
        
        Args:
            batch_code: The batch code to search for
            
        Returns:
            List of dictionaries containing serial_num, batch_code, and po_num
        """
        db = self.get_connection()
        cursor = db.cursor()
        
        try:
            cursor.execute(
                """SELECT serial_num, batch_code, po_num 
                   FROM faceware_assembly1 
                   WHERE batch_code = %s 
                   ORDER BY serial_num""",
                (batch_code,)
            )
            results = cursor.fetchall()
            return results
        finally:
            cursor.close()
            db.close()
    def get_batch_info_by_batch(self, batch_code: str) -> Optional[Dict[str, Any]]:
        """Get batch_code and po_num for a given batch_code (any row in the batch)"""
        db = self.get_connection()
        cursor = db.cursor()
        
        try:
            cursor.execute(
                "SELECT batch_code, po_num FROM faceware_assembly1 WHERE batch_code = %s LIMIT 1",
                (batch_code,)
            )
            result = cursor.fetchone()
            return result
        finally:
            cursor.close()
            db.close()