# Photo Backup - Server + Client
A self-hosted, custom photo-backup system that automatically syncs new photos from Android device to PC over local network

## Architecture
![alt text](<Screenshot From 2026-06-24 21-03-27.png>)
---
## Prerequisites
- Server ( Arch Linux )
    - Python
    - flask
    - writable directory for storing backup
- Client ( Android )
    - Termux
    - Python
    - Storage access to termux
---
## Installation
### Setup Server
Clone repo and create project directory
```bash
    git clone https://github.com/imramen07/photo-backup.git
    cd photo-backup
```
Install dependencies
```bash
    python -m venv venv
    source venv/bin/activate
    pip install flask
```
- Create local_config.py
    Rename demo_local_config.py to local_config.py
    add your localhost and preferred backup location in demo_local.py
Start the server
```bash
    python router.py
```
It listens 0.0.0.0 so will be accessible from any device on local network
---
### Setup Client
Open and_client.py in Termux
Make sure storage permissions are granted to Termux
In Termux, run
```bash
    pkg update && pkg upgrade -y
    pkg install python -y
    pip install requests
    chmod +x and_client.py
    python and_client.py
```
For automated run at specific intervals
In Termux run
```bash
    pkg install cronie -y
    crond
    crontab -e
```
---
### Author
Ramen
#### Github
https://github.com/imramen07