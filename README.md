# 🤖 Discord Management Bot

A modern and powerful Discord server management bot built with **discord.py**.

This bot provides a complete server management solution with moderation tools, verification systems, ticket support, role management, channel management, and many more features.

---

# ✨ Features

## 🌍 Multi-Language Support

The bot supports both **English and Turkish**.

Features:

* Server language settings
* Language selection panel
* Commands responding according to selected language

Command:

```bash
!dil
```

---

# 🛠️ Channel Management

Advanced channel management tools for server administrators.

### Create Text Channel

```bash
!kanal text channel-name
```

### Create Voice Channel

```bash
!kanal voice channel-name
```

### Delete Channel

```bash
!sil channel-name
```

---

# 🛡️ Moderation System

A complete moderation system to keep your server safe.

## Mute Users

```bash
!mute @user duration reason
```

Supported durations:

* Seconds
* Minutes
* Hours
* Days

## Unmute Users

```bash
!unmute @user
```

## Kick Users

```bash
!kick @user reason
```

## Ban Users

```bash
!ban @user reason
```

## Unban Users

```bash
!unban user_id
```

## Warning System

Give warnings to users:

```bash
!warn @user reason
```

View warning history:

```bash
!warnings @user
```

## Clear Messages

Delete messages quickly:

```bash
!clear amount
```

---

# ✅ Verification System

A button-based verification system.

Features:

* Verification panels
* Automatic role assignment
* User verification checks
* Persistent buttons that continue working after bot restart

Setup:

```bash
!verify-setup @role
```

---

# 🎫 Ticket System

A professional support ticket system.

Features:

* Private ticket channels
* User and staff-only access
* Automatic channel creation
* Ticket closing system

Setup:

```bash
!ticket-setup
```

---

# 🎭 Role System

Advanced role management features.

## Create Custom Roles

```bash
!rol-olustur role-name #color-code
```

## Self Role Menu

```bash
!rolmenu @role1 @role2
```

Features:

* Dropdown role selection
* Supports up to 25 roles
* Users can easily add or remove roles

---

# 📌 General Commands

## Bot Latency

```bash
!ping
```

Shows bot API and message latency.

---

## Server Information

```bash
!server
```

Displays:

* Server owner
* Member count
* Channel count
* Role count
* Server creation date

---

## User Information

```bash
!kullanici
```

Displays:

* Username
* Discord ID
* Account creation date
* Server join date
* Highest role

---

## Help Menu

```bash
!help
```

Modern embed-based command help system.

---

## Bot Owner

```bash
!owner
```

Displays bot owner information.

---

# ⚙️ Technical Features

Built with:

* Python
* discord.py
* JSON data storage
* Embed-based UI
* Buttons and Dropdown menus
* Persistent Views
* Permission management
* Error handling system
* Cooldown system

---

# 🎨 Design

The bot uses a modern Discord-style interface.

Features:

* Purple theme (`0x8B5CF6`)
* Clean embed messages
* Interactive buttons
* Dropdown menus
* User-friendly command system

---

# 📦 Installation

Clone the repository:

```bash
git clone https://github.com/username/repository.git
```

Enter the project folder:

```bash
cd repository
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Add your Discord bot token:

```python
TOKEN = "YOUR_BOT_TOKEN"
```

Start the bot:

```bash
python botdiscord.py
```

---

# 🔐 Required Discord Permissions

For the bot to work correctly, enable:

* Administrator
* Manage Channels
* Manage Roles
* Kick Members
* Ban Members
* Manage Messages
* Send Messages
* Embed Links

---

# 📋 Command Overview

| Command         | Description               |
| --------------- | ------------------------- |
| `!help`         | Opens help menu           |
| `!owner`        | Shows bot owner           |
| `!ping`         | Shows latency             |
| `!server`       | Server information        |
| `!kullanici`    | User information          |
| `!mute`         | Mute users                |
| `!ban`          | Ban users                 |
| `!kick`         | Kick users                |
| `!warn`         | Warn users                |
| `!ticket-setup` | Setup ticket system       |
| `!verify-setup` | Setup verification system |

---

# 📜 License

This project was developed for personal and educational purposes.

---

⭐ If you like this project, consider giving it a star!
