# CodeSync

<div align="center">

![App Icon](assets/icon.png)

**A lightweight, cross-platform code context synchronization tool designed to assist AI/LLM programming.**

[**简体中文**](README_CN.md) | [**Download Latest Release**](../../releases)

</div>

-----

## 📖 Introduction

**CodeSync** is designed to solve the "context window" management problem when working with Large Language Models (LLMs). It allows you to selectively package your local project's directory structure and file contents and sync them to your private server, generating a text format that is easy for AI to read.

With **CodeSync**, you no longer need to manually copy and paste dozens of files. Simply select your project folder, check the files you need, and sync with one click.

## ✨ Features

  * **🖥️ Cross-Platform:** Native support for Windows, macOS, and Linux.
  * **☁️ Private Deployment:** Easily deploy a private sync service using Docker; keep data in your own hands.
  * **🧠 Smart Filtering:** Automatically reads and respects `.gitignore` rules to exclude irrelevant files.
  * **⚡ Smart Sync:** Uses hash comparison to only upload changed file contents, saving bandwidth.
  * **🎨 Modern UI:** Supports Dark/Light theme switching and follows system settings.
  * **🌍 Multi-language:** Built-in English and Chinese interfaces, switchable at any time.
  * **📂 Visualization:** Automatically generates an ASCII tree view of the project to help AI understand reference relationships.

-----

## 🚀 Server Deployment (Docker)

To use the synchronization feature, you need to deploy the backend service on a server. Using Docker Compose is recommended.

### Prerequisites

  * A server with Docker installed.
  * Ensure the specified port is not currently in use.

### Step 1: Create Configuration File

Download [docker-compose.yml](server/docker-compose.yml) to your target folder.

**OR**

Create a file named `docker-compose.yml` in your target folder and fill in the following content:

```yaml
version: '3.8'

services:
  codesync-server:
    # Official Image
    image: ghcr.io/ryanzhou416/codesync/codesync-server:latest
    container_name: codesync_server
    # Restart policy
    restart: always
    ports:
      # Port Mapping: "HostPort:ContainerPort"
      # You can change the 8000 on the left to any port you want
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
```

### Step 2: Start the Service

Run the following command in the directory where your `docker-compose.yml` is located:

```bash
docker compose up -d
```

Once started successfully, the server will be listening at `http://your-server-ip:8000`.

-----

## 💻 Client Usage Guide

### 1\. Installation

Download the installer for your system from the [Release](../../releases):

  * **Windows:** Download and run `CodeSync_Setup_x*.exe`.
  * **macOS:** Download `CodeSync.dmg` and drag the app into the Applications folder.
  * **Linux:** Download the binary file or install the `.deb` package.

### 2\. Configuration

1.  Open the **CodeSync** software.
2.  In the top **Project Management** area:
      * **Project Name (Name):** Enter a unique identifier (e.g., `MyWeb`).
      * **Server (URL):** Enter your server address (e.g., `http://192.168.1.100:8000` or a domain name).
      * **Local Path (Path):** Click **Browse** to select your code's root directory.
3.  Click the **Save** button.

### 3\. Sync Code

1.  The file tree will load automatically.
2.  **Check** the files you want the AI to read.
      * *Tip:* Click filenames on the left to multi-select, and use the "Check Highlighted" button at the top for batch operations.
3.  Click **Start Sync** in the bottom right corner.
4.  The client will package the file structure and content and send it to the server.

### 4\. Get Context

After synchronization is complete, you (or your AI Agent) can access the full code context via a browser at the following address:
`http://your-server-ip:8000/MyWeb`

-----

## 🛠️ Local Development & Build

If you want to contribute to development or build from source:

### Requirements

  * Python 3.9+
  * `pip`

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/ryanzhou416/codesync.git
cd codesync

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run Client
python src/main.py

# 4. Run Server (Local test)
cd server
python server.py
```

-----

## 📄 License

This project is open-sourced under the MIT License.