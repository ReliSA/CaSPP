# User Installation and Running the Application

This document describes how to run the application as a regular user.

This section is intended for users who only want to run the application and do not need to modify the source code.

The application can be used in two ways:

1. Run an already prepared executable.
2. Generate the executable using the provided build script and then run it.

---

## 1. Requirements

If a pre-built executable is provided, the user does not need to manually install Python packages or create a virtual environment.

However, the application may still require **Git** to be installed on the system if Git-related functionality is used.

Git installation documentation: https://git-scm.com/downloads

To verify that Git is installed, run:

```bash
git --version
```

Expected output:

```bash
git version x.x.x
```

---

# 2. Running an Existing Executable

Use this option if the executable has already been created and is available on your system.

---

## 2.1 Windows

Navigate to the folder containing the built application and run:

```powershell
.\markdown_analyzer.exe
```

If the executable is located in the `dist` folder, run:

```powershell
.\dist\markdown_analyzer.exe
```

---

## 2.2 Linux / macOS

Navigate to the folder containing the built application and run:

```bash
./markdown_analyzer
```

If the executable is located in the `dist` folder, run:

```bash
./dist/markdown_analyzer
```

If the file cannot be executed, make it executable first:

```bash
chmod +x ./dist/markdown_analyzer
```

Then run it again:

```bash
./dist/markdown_analyzer
```

---

# 3. Creating and Running the Executable Using Build Scripts

Use this option if the executable is not available yet, but the project contains the provided build scripts.

The build scripts create the executable and place it in the `dist` directory.

---

## 3.1 Windows

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

After the script finishes, run the generated executable:

```powershell
.\dist\markdown_analyzer.exe
```

---

## 3.2 Linux / macOS

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

After the script finishes, run the generated executable:

```bash
./dist/markdown_analyzer
```

---

# 4. Notes

* Regular users do not need to manually create a virtual environment.
* Regular users do not need to manually install Python dependencies if they use the provided build scripts or a pre-built executable.
* Git must be installed if Git-related features of the application are used.
* If the application does not start, check whether the executable has the correct permissions and whether Git is installed.
* On Windows, PowerShell execution policies may block script execution.
