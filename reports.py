"""
Reports module for Gold Jewelry Business Management System
Handles all report generation functionality
"""

import tkinter as tk
from tkinter import ttk
from database import DatabaseManager

class ReportsManager:
    def __init__(self, db_manager):
        """Initialize reports manager with database connection"""
        self.db = db_manager
        self.reports_text = None
    
    def set_reports_text(self, text_widget):
        """Set the reports text widget"""
        self.reports_text = text_widget
    
    def generate_inventory_report(self):
        """Generate inventory report"""
        if not self.reports_text:
            return
            
        self.reports_text.delete(1.0, tk.END)
        self.reports_text.insert(tk.END, "=== GOLD INVENTORY REPORT ===\n\n")
        
        try:
            # Get inventory summary
            query = '''
                SELECT gt.name, SUM(i.weight_grams) as total_weight, 
                       COUNT(*) as total_items, SUM(CASE WHEN i.is_available = 1 THEN i.weight_grams ELSE 0 END) as available_weight
                FROM gold_inventory i
                JOIN gold_types gt ON i.gold_type_id = gt.gold_type_id
                GROUP BY gt.gold_type_id, gt.name
            '''
            rows = self.db.execute_query(query)
            
            for row in rows:
                self.reports_text.insert(tk.END, f"Gold Type: {row[0]}\n")
                self.reports_text.insert(tk.END, f"Total Weight: {row[1]:.2f} grams\n")
                self.reports_text.insert(tk.END, f"Total Items: {row[2]}\n")
                self.reports_text.insert(tk.END, f"Available Weight: {row[3]:.2f} grams\n")
                self.reports_text.insert(tk.END, f"Allocated Weight: {row[1] - row[3]:.2f} grams\n")
                self.reports_text.insert(tk.END, "-" * 50 + "\n")
        except Exception as e:
            self.reports_text.insert(tk.END, f"Error generating inventory report: {str(e)}\n")
    
    def generate_work_orders_report(self):
        """Generate work orders report"""
        if not self.reports_text:
            return
            
        self.reports_text.delete(1.0, tk.END)
        self.reports_text.insert(tk.END, "=== WORK ORDERS REPORT ===\n\n")
        
        try:
            # Get work orders summary
            query = '''
                SELECT wo.status, COUNT(*) as count, SUM(wo.gold_weight_issued) as total_gold_issued
                FROM work_orders wo
                GROUP BY wo.status
            '''
            rows = self.db.execute_query(query)
            
            for row in rows:
                self.reports_text.insert(tk.END, f"Status: {row[0]}\n")
                self.reports_text.insert(tk.END, f"Count: {row[1]}\n")
                self.reports_text.insert(tk.END, f"Total Gold Issued: {row[2]:.2f} grams\n")
                self.reports_text.insert(tk.END, "-" * 50 + "\n")
        except Exception as e:
            self.reports_text.insert(tk.END, f"Error generating work orders report: {str(e)}\n")
    
    def generate_freelancer_report(self):
        """Generate freelancer performance report"""
        if not self.reports_text:
            return
            
        self.reports_text.delete(1.0, tk.END)
        self.reports_text.insert(tk.END, "=== FREELANCER PERFORMANCE REPORT ===\n\n")
        
        try:
            # Get freelancer performance
            query = '''
                SELECT f.full_name, COUNT(wo.work_order_id) as total_orders,
                       SUM(wo.gold_weight_issued) as total_gold_issued,
                       SUM(wo.final_jewelry_weight) as total_completed,
                       SUM(wo.wastage_weight) as total_wastage
                FROM freelancers f
                LEFT JOIN work_orders wo ON f.freelancer_id = wo.freelancer_id
                WHERE f.is_active = 1
                GROUP BY f.freelancer_id, f.full_name
            '''
            rows = self.db.execute_query(query)
            
            for row in rows:
                self.reports_text.insert(tk.END, f"Freelancer: {row[0]}\n")
                self.reports_text.insert(tk.END, f"Total Orders: {row[1]}\n")
                self.reports_text.insert(tk.END, f"Total Gold Issued: {row[2]:.2f} grams\n")
                self.reports_text.insert(tk.END, f"Total Completed: {row[3]:.2f} grams\n")
                self.reports_text.insert(tk.END, f"Total Wastage: {row[4]:.2f} grams\n")
                if row[2] and row[2] > 0:
                    efficiency = ((row[3] / row[2]) * 100) if row[2] > 0 else 0
                    self.reports_text.insert(tk.END, f"Efficiency: {efficiency:.1f}%\n")
                self.reports_text.insert(tk.END, "-" * 50 + "\n")
        except Exception as e:
            self.reports_text.insert(tk.END, f"Error generating freelancer report: {str(e)}\n")
    
    def generate_wastage_report(self):
        """Generate wastage analysis report"""
        if not self.reports_text:
            return
            
        self.reports_text.delete(1.0, tk.END)
        self.reports_text.insert(tk.END, "=== WASTAGE ANALYSIS REPORT ===\n\n")
        
        try:
            # Get wastage summary
            query = '''
                SELECT SUM(wo.gold_weight_issued) as total_issued,
                       SUM(wo.final_jewelry_weight) as total_completed,
                       SUM(wo.wastage_weight) as total_wastage
                FROM work_orders wo
                WHERE wo.status = 'completed'
            '''
            row = self.db.execute_query(query)[0]
            
            if row[0]:
                total_issued = row[0]
                total_completed = row[1] or 0
                total_wastage = row[2] or 0
                
                self.reports_text.insert(tk.END, f"Total Gold Issued: {total_issued:.2f} grams\n")
                self.reports_text.insert(tk.END, f"Total Jewelry Completed: {total_completed:.2f} grams\n")
                self.reports_text.insert(tk.END, f"Total Wastage: {total_wastage:.2f} grams\n")
                self.reports_text.insert(tk.END, f"Wastage Percentage: {(total_wastage/total_issued)*100:.2f}%\n")
                self.reports_text.insert(tk.END, f"Efficiency: {(total_completed/total_issued)*100:.2f}%\n")
            else:
                self.reports_text.insert(tk.END, "No completed work orders found.\n")
        except Exception as e:
            self.reports_text.insert(tk.END, f"Error generating wastage report: {str(e)}\n")
    
    def generate_monthly_report(self):
        """Generate monthly summary report"""
        if not self.reports_text:
            return
            
        self.reports_text.delete(1.0, tk.END)
        self.reports_text.insert(tk.END, "=== MONTHLY SUMMARY REPORT ===\n\n")
        
        try:
            # Get current month data
            from datetime import datetime
            current_month = datetime.now().strftime("%Y-%m")
            
            # Work orders this month
            work_orders_query = '''
                SELECT COUNT(*) as total_orders, 
                       SUM(gold_weight_issued) as total_gold_issued,
                       SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_orders
                FROM work_orders 
                WHERE strftime('%Y-%m', issue_date) = ?
            '''
            work_orders_data = self.db.execute_query(work_orders_query, (current_month,))[0]
            
            # Inventory changes this month
            inventory_query = '''
                SELECT COUNT(*) as new_items, SUM(weight_grams) as total_added
                FROM gold_inventory 
                WHERE strftime('%Y-%m', received_date) = ?
            '''
            inventory_data = self.db.execute_query(inventory_query, (current_month,))[0]
            
            # Freelancer activity
            freelancer_query = '''
                SELECT COUNT(DISTINCT f.freelancer_id) as active_freelancers
                FROM freelancers f
                JOIN work_orders wo ON f.freelancer_id = wo.freelancer_id
                WHERE strftime('%Y-%m', wo.issue_date) = ? AND f.is_active = 1
            '''
            freelancer_data = self.db.execute_query(freelancer_query, (current_month,))[0]
            
            self.reports_text.insert(tk.END, f"Report Period: {current_month}\n")
            self.reports_text.insert(tk.END, "=" * 30 + "\n\n")
            
            self.reports_text.insert(tk.END, "WORK ORDERS:\n")
            self.reports_text.insert(tk.END, f"Total Orders: {work_orders_data[0]}\n")
            self.reports_text.insert(tk.END, f"Completed Orders: {work_orders_data[2]}\n")
            self.reports_text.insert(tk.END, f"Total Gold Issued: {work_orders_data[1]:.2f} grams\n")
            self.reports_text.insert(tk.END, f"Completion Rate: {(work_orders_data[2]/work_orders_data[0]*100) if work_orders_data[0] > 0 else 0:.1f}%\n\n")
            
            self.reports_text.insert(tk.END, "INVENTORY:\n")
            self.reports_text.insert(tk.END, f"New Items Added: {inventory_data[0]}\n")
            self.reports_text.insert(tk.END, f"Total Gold Added: {inventory_data[1]:.2f} grams\n\n")
            
            self.reports_text.insert(tk.END, "FREELANCERS:\n")
            self.reports_text.insert(tk.END, f"Active Freelancers: {freelancer_data[0]}\n")
            
        except Exception as e:
            self.reports_text.insert(tk.END, f"Error generating monthly report: {str(e)}\n")
    
    def generate_detailed_work_orders_report(self):
        """Generate detailed work orders report with all information"""
        if not self.reports_text:
            return
            
        self.reports_text.delete(1.0, tk.END)
        self.reports_text.insert(tk.END, "=== DETAILED WORK ORDERS REPORT ===\n\n")
        
        try:
            # Get detailed work orders
            query = '''
                SELECT wo.work_order_id, f.full_name, wo.jewelry_design, 
                       wo.gold_weight_issued, wo.expected_final_weight, wo.final_jewelry_weight,
                       wo.wastage_weight, wo.status, wo.issue_date, wo.completion_date
                FROM work_orders wo
                JOIN freelancers f ON wo.freelancer_id = f.freelancer_id
                ORDER BY wo.issue_date DESC
            '''
            rows = self.db.execute_query(query)
            
            for row in rows:
                self.reports_text.insert(tk.END, f"Order ID: {row[0]}\n")
                self.reports_text.insert(tk.END, f"Freelancer: {row[1]}\n")
                self.reports_text.insert(tk.END, f"Design: {row[2]}\n")
                self.reports_text.insert(tk.END, f"Gold Issued: {row[3]:.2f} grams\n")
                self.reports_text.insert(tk.END, f"Expected Weight: {row[4]:.2f} grams\n")
                self.reports_text.insert(tk.END, f"Final Weight: {row[5]:.2f} grams\n" if row[5] else "Final Weight: Not completed\n")
                self.reports_text.insert(tk.END, f"Wastage: {row[6]:.2f} grams\n" if row[6] else "Wastage: Not recorded\n")
                self.reports_text.insert(tk.END, f"Status: {row[7]}\n")
                self.reports_text.insert(tk.END, f"Issue Date: {row[8]}\n")
                self.reports_text.insert(tk.END, f"Completion Date: {row[9]}\n" if row[9] else "Completion Date: Pending\n")
                
                # Calculate efficiency if completed
                if row[5] and row[3]:
                    efficiency = (row[5] / row[3]) * 100
                    self.reports_text.insert(tk.END, f"Efficiency: {efficiency:.1f}%\n")
                
                self.reports_text.insert(tk.END, "-" * 60 + "\n")
        except Exception as e:
            self.reports_text.insert(tk.END, f"Error generating detailed work orders report: {str(e)}\n")
    
    def export_report_to_file(self, filename=None):
        """Export current report to a text file"""
        if not self.reports_text:
            return
            
        if not filename:
            from datetime import datetime
            filename = f"gold_jewelry_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            content = self.reports_text.get(1.0, tk.END)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            return filename
        except Exception as e:
            print(f"Error exporting report: {e}")
            return None
