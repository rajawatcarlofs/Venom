# Telegram Message Manager

Complete production-ready web application for managing multiple Telegram accounts and sending bulk messages to groups and channels.

## Features

- **Multi-Account Management**: Add and manage multiple Telegram accounts
- **Group Management**: Load, search, and manage Telegram groups and channels
- **Message Composer**: Create messages with emoji support and save templates
- **Campaign System**: Create and execute message campaigns
- **Scheduling**: Configure delays between messages
- **Real-time Logs**: Monitor system activity and logs
- **Dashboard**: View statistics and quick actions
- **Dark Mode**: Dark theme support
- **Security**: Password-protected admin panel

## Requirements

- Python 3.12+
- Windows / Linux / macOS

## Installation

### Windows
```bash
install.bat
```

### Linux/macOS
```bash
chmod +x install.sh
./install.sh
```

## Setup

1. Get your Telegram API credentials:
   - Visit https://my.telegram.org
   - Create an application
   - Get your API ID and API Hash

2. Edit `.env` file with your credentials:
```
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
ADMIN_PASSWORD=your_admin_password
```

## Running the Application

### Windows
```bash
start.bat
```

### Linux/macOS
```bash
./start.sh
```

The application will be available at `http://127.0.0.1:5000`

## Default Credentials

- **Username**: Not required
- **Password**: `admin123` (change in .env file)

## Project Structure

```
telegram-message-manager/
├── app.py                          # Main Flask application
├── database.py                     # Database models
├── telegram_handler.py             # Telegram integration
├── config.py                       # Configuration
├── auth.py                         # Authentication
├── utils.py                        # Utilities
├── requirements.txt                # Dependencies
├── .env.example                    # Environment template
├── install.bat / install.sh        # Installation scripts
├── start.bat / start.sh            # Launcher scripts
├── templates/                      # HTML templates
├── static/                         # CSS and JavaScript
│   ├── css/
│   │   ├── style.css
│   │   └── dark-mode.css
│   └── js/
│       ├── main.js
│       ├── accounts.js
│       ├── groups.js
│       ├── campaigns.js
│       ├── composer.js
│       └── dashboard.js
└── sessions/                       # Telegram sessions
```

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite
- **Telegram**: Telethon
- **Frontend**: Bootstrap 5, JavaScript
- **Security**: CSRF protection, password hashing

## API Endpoints

### Authentication
- `POST /login` - Login to admin panel
- `GET /logout` - Logout

### Accounts
- `GET /api/accounts` - Get all accounts
- `POST /api/account/add` - Add new account
- `POST /api/account/verify` - Verify OTP
- `POST /api/account/<id>/disconnect` - Disconnect account

### Groups
- `GET /api/groups` - Get all groups
- `POST /api/groups/load` - Load groups from accounts
- `POST /api/groups/save-selection` - Save selected groups
- `GET /api/groups/export` - Export groups
- `POST /api/groups/import` - Import groups

### Templates
- `GET /api/templates` - Get all templates
- `POST /api/template/save` - Save template
- `DELETE /api/template/<id>/delete` - Delete template

### Campaigns
- `GET /api/campaigns` - Get all campaigns
- `POST /api/campaign/create` - Create campaign
- `POST /api/campaign/<id>/start` - Start campaign
- `POST /api/campaign/<id>/pause` - Pause campaign
- `POST /api/campaign/<id>/resume` - Resume campaign
- `POST /api/campaign/<id>/stop` - Stop campaign
- `DELETE /api/campaign/<id>/delete` - Delete campaign

### Logs
- `GET /api/logs` - Get system logs
- `GET /api/logs/export` - Export logs

### Settings
- `GET /api/settings` - Get settings
- `POST /api/settings/update` - Update settings

## Troubleshooting

### API Credentials Error
Make sure you have configured your Telegram API credentials in the `.env` file.

### Database Error
Delete `telegram_manager.db` and run installation again.

### Port Already in Use
Change the port in `app.py` or stop the application using port 5000.

## Security Notes

- Change the default admin password immediately
- Use a strong SECRET_KEY in production
- Secure your API credentials in `.env`
- Never commit `.env` file to version control

## License

This project is open source and available under the MIT License.

## Support

For issues and questions, please create an issue in the repository.

---

**Created**: 2024
**Version**: 1.0.0
**Status**: Production Ready
