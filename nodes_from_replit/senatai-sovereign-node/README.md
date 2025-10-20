# Senatai Sovereign Node

## Purpose
The **Sovereign Node** is a self-contained, offline version of Senatai designed for portable deployment on USB thumb drives or local machines. It enables users to engage with Canadian legislation, earn Policap, and participate in civic discourse **without requiring internet connectivity**.

## Key Features
- 🔒 **Fully Offline**: No network connectivity required
- 💾 **SQLite Database**: All data stored locally in portable `data/senatai.db` file
- 🚀 **Portable**: Run from any USB drive on Windows/Linux/Mac
- 👤 **Single-User**: Optimized for personal use
- 📊 **Pre-loaded Bills**: Comes with sample Canadian legislation
- 🎯 **Full Feature Set**: All core Senatai features work offline

## Deployment Strategy

### For End Users (Thumb Drive Distribution)

1. **Copy to USB Drive**: 
   ```bash
   cp -r senatai-sovereign-node /media/usb-drive/
   ```

2. **Run on any machine**:
   ```bash
   cd /media/usb-drive/senatai-sovereign-node
   python app.py
   ```

3. **Access in browser**: Navigate to `http://localhost:5000`

### Technical Architecture

**Database**: SQLite with relative path (`data/senatai.db`)
- Automatically created on first run
- Portable across operating systems
- All user data, votes, and Policap stored locally

**No Network Dependencies**:
- No PostgreSQL connection attempts
- No external API calls
- No data synchronization (future: optional P2P sync to Persistent Nodes)

**Security**:
- User authentication works locally
- Passwords hashed with Werkzeug
- Session management via Flask-Login

## File Structure
```
senatai-sovereign-node/
├── app.py                  # Main application (SQLite-only)
├── question_generator.py   # Sophisticated question system
├── topic_matcher.py        # Bill matching engine
├── icebreakers.py         # Rotating welcome messages
├── demographics.py        # Optional demographic collection
├── policap_rewards.py     # Reward calculation with diminishing returns
├── badges.py              # Two-tier badge system
├── data/
│   └── senatai.db        # Local SQLite database
├── templates/             # Jinja2 HTML templates
└── static/               # CSS and assets
```

## Requirements
- Python 3.8+
- Flask
- Flask-Login
- Werkzeug

Install dependencies:
```bash
pip install flask flask-login werkzeug
```

## Configuration
All configuration uses relative paths for portability. The database file is created in the `data/` subdirectory automatically.

**Default Admin Account**:
- Username: `admin`
- Password: `changetheadminpassword` (change immediately!)

## Development vs Production

This fork is designed for **offline, local use**. For a multi-user web deployment, use the **Persistent Node** fork instead.

## Future Features
- Optional sync with Persistent Node for anonymized data sharing
- Mobile companion app support
- Encrypted export/import for user data portability

---

**Privacy First**: Your data stays on your device. No tracking, no cloud storage, full user ownership.
