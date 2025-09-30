import os
import csv
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class CallReportSender:
    def __init__(self):
        self.reports_folder = "reports"
        self.webhook_url = "https://n8n.omadligrouphq.com/webhook/call-reports-sender"
    
    def get_latest_csv_file(self) -> Optional[str]:
        """Find the latest CSV file in the reports folder"""
        try:
            if not os.path.exists(self.reports_folder):
                print(f"❌ Reports folder '{self.reports_folder}' does not exist")
                return None
            
            csv_files = [f for f in os.listdir(self.reports_folder) if f.endswith('.csv')]
            
            if not csv_files:
                print("❌ No CSV files found in reports folder")
                return None
            
            # Sort files by modification time (newest first)
            csv_files.sort(key=lambda x: os.path.getmtime(os.path.join(self.reports_folder, x)), reverse=True)
            
            latest_file = csv_files[0]
            file_path = os.path.join(self.reports_folder, latest_file)
            
            print(f"✅ Found latest CSV file: {latest_file}")
            return file_path
            
        except Exception as e:
            print(f"❌ Error finding latest CSV file: {str(e)}")
            return None
    
    def parse_csv_data(self, file_path: str) -> List[Dict]:
        """Parse CSV file and extract data"""
        try:
            reports = []
            
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                
                for row in csv_reader:
                    # Clean up the row data
                    cleaned_row = {}
                    for key, value in row.items():
                        # Clean up field names and values
                        clean_key = key.strip()
                        clean_value = value.strip() if value else ""
                        cleaned_row[clean_key] = clean_value
                    
                    reports.append(cleaned_row)
            
            print(f"✅ Parsed {len(reports)} records from CSV")
            return reports
            
        except Exception as e:
            print(f"❌ Error parsing CSV file: {str(e)}")
            return []
    
    def filter_latest_day_reports(self, reports: List[Dict]) -> List[Dict]:
        """Filter reports to get only the latest day's data"""
        try:
            if not reports:
                return []
            
            # Get the latest date from the reports
            latest_date = None
            for report in reports:
                date_str = report.get('Date & Time', '')
                if date_str:
                    try:
                        # Parse the date (format: 2025-09-30 10:09:23)
                        report_date = datetime.strptime(date_str.split(' ')[0], '%Y-%m-%d').date()
                        if latest_date is None or report_date > latest_date:
                            latest_date = report_date
                    except ValueError:
                        continue
            
            if latest_date is None:
                print("❌ Could not determine latest date from reports")
                return []
            
            # Filter reports for the latest date
            latest_day_reports = []
            for report in reports:
                date_str = report.get('Date & Time', '')
                if date_str:
                    try:
                        report_date = datetime.strptime(date_str.split(' ')[0], '%Y-%m-%d').date()
                        if report_date == latest_date:
                            latest_day_reports.append(report)
                    except ValueError:
                        continue
            
            print(f"✅ Filtered {len(latest_day_reports)} reports for latest date: {latest_date}")
            return latest_day_reports
            
        except Exception as e:
            print(f"❌ Error filtering latest day reports: {str(e)}")
            return []
    
    def send_to_webhook(self, reports: List[Dict]) -> bool:
        """Send reports to n8n webhook"""
        try:
            if not reports:
                print("❌ No reports to send")
                return False
            
            # Prepare payload
            payload = {
                "timestamp": datetime.now().isoformat(),
                "total_reports": len(reports),
                "reports": reports
            }
            
            print(f"📤 Sending {len(reports)} reports to webhook...")
            
            # Send POST request
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'CallReportSender/1.0'
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ Successfully sent reports to webhook")
                print(f"📊 Response: {response.text}")
                return True
            else:
                print(f"❌ Webhook request failed with status {response.status_code}")
                print(f"📄 Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error sending to webhook: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Error sending to webhook: {str(e)}")
            return False
    
    def process_and_send_reports(self) -> bool:
        """Main function to process CSV and send to webhook"""
        try:
            print("🚀 Starting call report processing...")
            
            # Step 1: Find latest CSV file
            latest_file = self.get_latest_csv_file()
            if not latest_file:
                return False
            
            # Step 2: Parse CSV data
            all_reports = self.parse_csv_data(latest_file)
            if not all_reports:
                return False
            
            # Step 3: Filter for latest day
            latest_day_reports = self.filter_latest_day_reports(all_reports)
            if not latest_day_reports:
                print("❌ No reports found for the latest day")
                return False
            
            # Step 4: Send to webhook
            success = self.send_to_webhook(latest_day_reports)
            
            if success:
                print("🎉 Call report processing completed successfully!")
            else:
                print("❌ Call report processing failed!")
            
            return success
            
        except Exception as e:
            print(f"❌ Error in process_and_send_reports: {str(e)}")
            return False

def main():
    """Main function to run the report sender"""
    sender = CallReportSender()
    success = sender.process_and_send_reports()
    
    if not success:
        exit(1)

if __name__ == "__main__":
    main()