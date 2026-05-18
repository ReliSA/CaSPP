# Development Environment Setup and Running the Application

This document describes how to prepare the development environment for this project and how to run the application using build scripts.

---

## 1. Check Python Version

Before starting, make sure you have **Python 3.10** installed.
Official Python installation documentation: https://www.python.org/downloads/

```bash
python3 --version
```

or

```bash
python --version
```

Expected output:

```bash
Python 3.10.x
```

---

## 2. Clone the Repository

Clone the repository to your local machine:

```bash
git clone <HTTPS/SSH/GitHub CLI>
```

---

## 3. Set Up Development Environment

To isolate project dependencies, it is recommended to use a virtual environment.

### 3.1 Navigate to Project Root

**Linux / macOS:**

```bash
cd /path/to/project
```

**Windows:**

```powershell
cd C:\path\to\project_root
```

---

### 3.2 Create Virtual Environment

```bash
python3.10 -m venv venv
```

---

### 3.3 Activate Virtual Environment

**Linux / macOS:**

```bash
source venv/bin/activate
```

**Windows:**

```powershell
venv\Scripts\activate
```

---

### 3.4 Verify Activation

After activation, your terminal should show something like:

```bash
(venv) user@machine:~/project$
```

Verify Python version:

```bash
python --version
```

---

### 3.5 Install Dependencies

Install required packages:

```bash
pip install -r requirements.txt
```

If `pip` does not work:

```bash
python -m pip install -r requirements.txt
```

---

## 4. Run Application Using Build Scripts

The application can be run on both Windows and Unix-based systems.

---

### 4.1 Windows

```powershell
cd C:\path\to\project_root

# If script execution is blocked
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

.\build_script.ps1
.\dist\markdown_analyzer.exe
```

---

### 4.2 Linux / macOS

```bash
cd /path/to/project_root

# Make script executable if needed
chmod +x build_script.sh

./build_script.sh
./dist/markdown_analyzer
```

---

## Notes

* Ensure Python 3.10 is used (not older versions like 3.8).
* Always activate the virtual environment before installing dependencies or running scripts.
* On Windows, PowerShell execution policies may block script execution.
