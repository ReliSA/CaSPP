# Development Environment Setup and Building the Application

This document describes how to prepare the development environment, install dependencies, and build the application from source.

This section is intended for developers who want to modify the source code, install dependencies, or build the application manually.

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

Then navigate to the project root directory.

**Linux / macOS:**

```bash
cd /path/to/project_root
```

**Windows:**

```powershell
cd C:\path\to\project_root
```

---

## 3. Create a Virtual Environment

To isolate project dependencies, create a virtual environment:

```bash
python3.10 -m venv venv
```

On Windows, if `python3.10` is not available, use:

```powershell
py -3.10 -m venv venv
```

---

## 4. Activate the Virtual Environment

**Linux / macOS:**

```bash
source venv/bin/activate
```

**Windows:**

```powershell
venv\Scripts\activate
```

---

## 5. Verify Activation

After activation, your terminal should show something like:

```bash
(venv) user@machine:~/project$
```

Verify that the correct Python version is used:

```bash
python --version
```

Expected output:

```bash
Python 3.10.x
```

---

## 6. Install Dependencies

Install the required packages:

```bash
pip install -r requirements.txt
```

If `pip` does not work, use:

```bash
python -m pip install -r requirements.txt
```

---

# Building and Running from Source

The application can be built on both Windows and Unix-based systems.

---

## 7. Windows

Navigate to the project root:

```powershell
cd C:\path\to\project_root
```

If PowerShell blocks script execution, allow script execution only for the current terminal session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Run the build script:

```powershell
.\build_script.ps1
```

Run the built application:

```powershell
.\dist\markdown_analyzer.exe
```

---

## 8. Linux / macOS

Navigate to the project root:

```bash
cd /path/to/project_root
```

Make the build script executable if needed:

```bash
chmod +x build_script.sh
```

Run the build script:

```bash
./build_script.sh
```

Run the built application:

```bash
./dist/markdown_analyzer
```

---

## 9. Notes

* Use **Python 3.10** for development.
* Older Python versions, such as Python 3.8, may cause dependency or compatibility issues.
* Always activate the virtual environment before installing dependencies or building the application manually.
* On Windows, PowerShell execution policies may block script execution.
* If Git-related functionality is used, Git must also be installed on the system.
