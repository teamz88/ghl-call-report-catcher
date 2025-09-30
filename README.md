# Microsoft Graph API Email Retrieval Script

A Python script to authenticate with Microsoft Graph API and retrieve email messages from your Microsoft 365/Outlook account.

## Features

- **Multiple Authentication Methods**: Supports both confidential client (app-only) and public client (delegated) authentication
- **Email Retrieval**: Get messages from inbox, sent items, drafts, or any mail folder
- **Search Functionality**: Search through your emails using Microsoft Graph's search capabilities
- **Time-based Filtering**: Retrieve messages from specific time periods
- **Message Details**: Get full details of specific messages
- **Interactive Menu**: User-friendly command-line interface
- **Comprehensive Logging**: Detailed logging for debugging and monitoring

## Prerequisites

1. **Microsoft Azure App Registration**: You need to register an application in Azure Active Directory
2. **Python 3.7+**: Make sure you have Python 3.7 or higher installed
3. **Required Permissions**: Your app needs appropriate Microsoft Graph permissions

## Setup Instructions

### 1. Azure App Registration

1. Go to the [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** > **App registrations**
3. Click **New registration**
4. Fill in the details:
   - **Name**: Your app name (e.g., "Email Retrieval Script")
   - **Supported account types**: Choose based on your needs
   - **Redirect URI**: For public client, you can use `http://localhost`
5. Click **Register**

### 2. Configure API Permissions

1. In your app registration, go to **API permissions**
2. Click **Add a permission**
3. Select **Microsoft Graph**
4. Choose **Delegated permissions** (for user access) or **Application permissions** (for app-only access)
5. Add the following permissions:
   - `Mail.Read` - Read user mail
   - `Mail.ReadWrite` - Read and write user mail (if needed)
   - `User.Read` - Read user profile
6. Click **Grant admin consent** (if you have admin rights)

### 3. Get Client Credentials

1. In your app registration, go to **Overview** and copy:
   - **Application (client) ID**
   - **Directory (tenant) ID**
2. If using confidential client, go to **Certificates & secrets**:
   - Click **New client secret**
   - Add a description and expiration
   - Copy the **Value** (not the Secret ID)

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure the Application

1. Open `config.json` and update the following values:

```json
{
    "client_id": "your-application-client-id",
    "client_secret": "your-client-secret-if-using-confidential-client",
    "authority": "https://login.microsoftonline.com/your-tenant-id",
    "scope": ["https://graph.microsoft.com/Mail.Read"],
    "username": "your-email@domain.com",
    "password": "your-password-if-using-username-password-flow"
}
```

**Configuration Options:**

- **client_id**: Your Azure app's Application (client) ID
- **client_secret**: Client secret (only needed for confidential client apps)
- **authority**: Your tenant's authority URL
- **scope**: List of Microsoft Graph scopes your app needs
- **username/password**: Only needed for username/password authentication flow

## Usage

### Running the Script

```bash
python app.py
```

### Interactive Menu Options

1. **Get recent messages (inbox)**: Retrieve the most recent messages from your inbox
2. **Get messages from last 24 hours**: Get all messages received in the last 24 hours
3. **Search messages**: Search for messages using keywords
4. **Get message details**: Get full details of a specific message by ID
5. **Get messages from specific folder**: Retrieve messages from any mail folder
6. **Exit**: Close the application

### Programmatic Usage

You can also use the `GraphEmailClient` class directly in your own code:

```python
from app import GraphEmailClient

# Initialize the client
client = GraphEmailClient("config.json")

# Authenticate
if client.authenticate():
    # Get recent messages
    messages = client.get_messages(count=20)
    
    # Search for messages
    search_results = client.search_messages("important meeting")
    
    # Get messages from last week
    recent_messages = client.get_recent_messages(hours=168)  # 7 days
    
    # Get message details
    if messages:
        message_details = client.get_message_details(messages[0]['id'])
```

## Authentication Flows

### 1. Interactive Authentication (Recommended for Personal Use)

- Opens a browser window for user login
- Most secure for personal accounts
- No need to store passwords in config

### 2. Username/Password Authentication

- Provide username and password in config.json
- Less secure but convenient for automation
- May not work with accounts that have MFA enabled

### 3. Client Credentials Flow (For App-Only Access)

- Uses client secret for authentication
- Good for server-to-server scenarios
- Requires application permissions in Azure

## Logging

The script creates detailed logs in `email_retrieval.log` and also displays logs in the console. Log levels include:

- **INFO**: General information about operations
- **ERROR**: Error messages and failures
- **DEBUG**: Detailed debugging information (if enabled)

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Check your client_id and tenant_id in config.json
   - Ensure your app has the required permissions
   - Verify admin consent has been granted

2. **Permission Denied**
   - Make sure your app has the necessary Microsoft Graph permissions
   - Check if admin consent is required and granted

3. **Token Expired**
   - The script handles token refresh automatically
   - If issues persist, try re-authenticating

4. **MFA Issues**
   - Username/password flow may not work with MFA
   - Use interactive authentication instead

### Getting Help

- Check the logs in `email_retrieval.log` for detailed error messages
- Verify your Azure app registration settings
- Ensure all required permissions are granted

## Security Notes

- Never commit your `config.json` file with real credentials to version control
- Use environment variables for sensitive information in production
- Regularly rotate client secrets
- Follow the principle of least privilege when assigning permissions

## License

This project is provided as-is for educational and development purposes.