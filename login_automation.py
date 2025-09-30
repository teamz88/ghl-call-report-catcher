import asyncio
import time
from playwright.async_api import async_playwright
from app import get_latest_otp
from report_sender import CallReportSender

class TidyYourSalesLogin:
    def __init__(self):
        self.email = "info@omadligroup.com"
        self.password = "********"
        self.login_url = "https://app.tidyyoursales.com/"
        self.target_url = "https://app.tidyyoursales.com/v2/location/<location_id>/reporting/call"
        
    async def login_with_otp(self):
        """Automated login with OTP verification"""
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=False)  # Set to True for headless mode
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                print("🌐 Opening login page...")
                await page.goto(self.login_url)
                await page.wait_for_load_state('networkidle')
                
                # Fill login credentials
                print("📝 Filling login credentials...")
                await page.fill('#email', self.email)
                await page.fill('#password', self.password)
                
                # Submit login form
                print("🔐 Submitting login form...")
                await page.click('button[type="submit"]')
                
                # Wait for OTP verification page
                print("⏳ Waiting for OTP verification page...")
                await page.wait_for_selector('text=Verify Security Code', timeout=10000)
                print("✅ OTP verification page loaded")
                
                # Click "Send Security Code" button
                print("📤 Clicking 'Send Security Code' button...")
                await page.click('text=Send Security Code')
                print("✅ Security code sent")
                
                # Wait 30 seconds for email to arrive
                print("⏰ Waiting 30 seconds for email to arrive...")
                await asyncio.sleep(30)
                
                # Get latest OTP from email
                print("📧 Getting latest OTP from email...")
                otp_code = get_latest_otp()
                
                if not otp_code:
                    print("❌ Failed to get OTP code")
                    return False
                
                print(f"🔢 Using OTP: {otp_code}")
                
                # Find OTP input container and enter OTP
                print("⌨️ Entering OTP code...")
                
                # Wait for OTP input container
                otp_container = await page.wait_for_selector('.flex.flex-row.justify-center.px-2.text-center', timeout=10000)
                
                # Find all input fields in the OTP container
                otp_inputs = await otp_container.query_selector_all('input')
                
                # Enter each digit of OTP into separate inputs
                for i, digit in enumerate(otp_code):
                    if i < len(otp_inputs):
                        await otp_inputs[i].fill(digit)
                        await asyncio.sleep(0.1)  # Small delay between inputs
                
                print("✅ OTP entered successfully")
                
                # Wait 30 seconds for automatic processing or page to load
                print("⏰ Waiting 30 seconds for login processing...")
                await asyncio.sleep(30)
                
                # Navigate to target page
                print("🎯 Navigating to call reporting page...")
                await page.goto(self.target_url)
                print("⏰ Waiting 30 seconds for login processing...")
                await asyncio.sleep(15)
                
                print("🎉 Successfully logged in and navigated to call reporting page!")
                print(f"📍 Current URL: {page.url}")
                
                # Wait 30 seconds before interacting with the page
                print("⏰ Waiting 30 seconds before setting date range...")
                await asyncio.sleep(30)
                
                # Set date range to last 1 day
                print("📅 Setting date range to last 1 day...")
                
                # Try different selectors for the date picker
                date_picker_selectors = [
                    '#location-dashboard_date-picker',
                    '[data-testid="date-picker"]',
                    '.date-picker',
                    'input[type="text"][placeholder*="date"]',
                    '.n-date-picker'
                ]
                
                date_picker = None
                for selector in date_picker_selectors:
                    try:
                        date_picker = await page.wait_for_selector(selector, timeout=5000)
                        print(f"✅ Found date picker with selector: {selector}")
                        break
                    except:
                        continue
                
                if not date_picker:
                    print("❌ Could not find date picker element")
                    return
                
                await date_picker.click()
                print("📅 Clicked on date picker")
                
                # Wait for date picker to open
                await asyncio.sleep(3)
                
                # Get today's date and yesterday's date
                from datetime import datetime, timedelta
                today = datetime.now()
                yesterday = today - timedelta(days=1)
                
                # Format dates as MM/DD/YYYY
                start_date = yesterday.strftime("%m/%d/%Y")
                end_date = today.strftime("%m/%d/%Y")
                
                print(f"📅 Setting date range: {start_date} - {end_date}")
                
                # Try different approaches to fill date inputs
                date_input_selectors = [
                    'input[placeholder="Start Date"]',
                    'input[placeholder*="Start"]',
                    'input[placeholder*="start"]',
                    '.n-input input[type="text"]',
                    '.date-input input'
                ]
                
                # Fill start date
                start_input = None
                for selector in date_input_selectors:
                    try:
                        inputs = await page.query_selector_all(selector)
                        if inputs:
                            start_input = inputs[0]  # First input is usually start date
                            print(f"✅ Found start date input with selector: {selector}")
                            break
                    except:
                        continue
                
                if start_input:
                    # Clear and fill start date
                    await start_input.click(click_count=3)
                    await page.keyboard.press('Delete')
                    await asyncio.sleep(0.5)
                    await start_input.fill(start_date)
                    print(f"✅ Filled start date: {start_date}")
                else:
                    print("❌ Could not find start date input")
                
                # Fill end date
                end_input = None
                for selector in date_input_selectors:
                    try:
                        inputs = await page.query_selector_all(selector)
                        if len(inputs) > 1:
                            end_input = inputs[1]  # Second input is usually end date
                            print(f"✅ Found end date input with selector: {selector}")
                            break
                        elif len(inputs) == 1 and selector.find('End') != -1:
                            end_input = inputs[0]
                            break
                    except:
                        continue
                
                if end_input:
                    # Clear and fill end date
                    await end_input.click(click_count=3)
                    await page.keyboard.press('Delete')
                    await asyncio.sleep(0.5)
                    await end_input.fill(end_date)
                    print(f"✅ Filled end date: {end_date}")
                else:
                    print("❌ Could not find end date input")
                
                # Wait a bit before clicking confirm
                await asyncio.sleep(2)
                
                # Try different selectors for confirm button
                confirm_selectors = [
                    '.n-button.n-button--primary-type.n-button--tiny-type',
                    '.n-button--primary-type',
                    'button[type="submit"]',
                    'button:has-text("Confirm")',
                    'button:has-text("Apply")',
                    'button:has-text("OK")',
                    '.confirm-btn',
                    '.apply-btn'
                ]
                
                # Click confirm button
                print("✅ Clicking confirm button...")
                confirm_btn = None
                for selector in confirm_selectors:
                    try:
                        confirm_btn = await page.wait_for_selector(selector, timeout=3000)
                        print(f"✅ Found confirm button with selector: {selector}")
                        break
                    except:
                        continue
                
                if confirm_btn:
                    await confirm_btn.click()
                    print("✅ Clicked confirm button successfully")
                else:
                    print("❌ Could not find confirm button, trying to press Enter")
                    await page.keyboard.press('Enter')
                
                # Wait for data to load
                print("⏳ Waiting for data to load...")
                await asyncio.sleep(5)
                
                # Click export button
                print("📤 Clicking export button...")
                export_btn = await page.wait_for_selector('#call-reporting-dashboard_btn--export', timeout=10000)
                
                # Set up download handling
                async with page.expect_download() as download_info:
                    await export_btn.click()
                
                download = await download_info.value
                
                # Create reports folder if it doesn't exist
                import os
                reports_dir = "reports"
                if not os.path.exists(reports_dir):
                    os.makedirs(reports_dir)
                
                # Save the downloaded file to reports folder
                filename = download.suggested_filename
                file_path = os.path.join(reports_dir, filename)
                await download.save_as(file_path)
                
                print(f"✅ File downloaded and saved to: {file_path}")
                
                # Process and send reports to webhook
                print("📊 Processing and sending reports to webhook...")
                report_sender = CallReportSender()
                webhook_success = report_sender.process_and_send_reports()
                
                if webhook_success:
                    print("🎉 Reports successfully sent to n8n webhook!")
                else:
                    print("❌ Failed to send reports to webhook")
                
                # Keep browser open for a few seconds to verify
                await asyncio.sleep(5)
                
                return True
                
            except Exception as e:
                print(f"❌ Login failed: {e}")
                return False
                
            finally:
                await browser.close()

async def main():
    """Main function to run the login automation"""
    login_bot = TidyYourSalesLogin()
    success = await login_bot.login_with_otp()
    
    if success:
        print("✅ Login automation completed successfully!")
    else:
        print("❌ Login automation failed!")

if __name__ == "__main__":
    asyncio.run(main())