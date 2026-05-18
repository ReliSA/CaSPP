# Markdown Analyzer — User Manual

How to use **Markdown Analyzer**: edit Markdown text files (`.md`), preview them, check them against your project’s rules, and sync with Git when your team uses it.

---

## Start the app

Run the program **from your project folder** (the folder your team gave you—the one that contains the project and its Git data). If you start it from the wrong place, it may not open. For install and build steps, see [INSTALLATION_OVERVIEW.md](INSTALLATION_OVERVIEW.md).

---

## Main screen

**Left sidebar — two modes**

- **Markdown** (folder icon): work on documents.
- **Git** (brand icon): check status and sync with the shared repository.

**Markdown mode**

1. **Open a document** — **File → Open File** (`Ctrl+O` / Mac `⌘+O`), or **File → Open Folder** (`Ctrl+F` / `⌘+F`) to fill the **Explorer** tree with Markdown files, then **double-click** a file.
2. **Edit** in the large text area. Several files can be open as **tabs**; use **Save Changes** or **File → Save File** (`Ctrl+S` / `⌘+S`) for the active tab.
3. Turn on **Live Preview** to see formatted output as you type (checkbox or **File → Show Live Preview**, `Ctrl+P` / `⌘+P`).
4. Turn on **Analyzer** to see whether the document follows the project structure (checkbox or **File → Show Analyzer Output**, `Ctrl+A` / `⌘+A`).

Use **Open Explorer** if the file tree is hidden. The **File** and **Git** menus repeat the same actions as the buttons on screen.

**Preview links:** Normal web links open in the browser; links to other Markdown files next to your document open in the app when that file exists.

---

## Analyzer (structure check)

The Analyzer updates when you **open** or **save** a file. It compares your document to a project template. **Warnings** include a **line number**—go to that line in the editor and fix the issue, then save again to refresh.

Your file’s **parent folder** must match what the project expects (for example: `categories`, `forms`, `methodologies`, `modes`, `perspectives`, `publications`, `stages`, `patterns`, or files under `catalogue`). If the Analyzer fails or says the template does not match, move the file into the right folder or ask your team.

---

## Git mode

Open the **Git** sidebar. The list below shows messages from each action.

| Button | What it does |
|--------|----------------|
| **Status** | Shows what changed (Markdown-focused). |
| **Fetch** | Gets the latest information from the server without changing your files yet. |
| **Pull** | Brings others’ changes into your copy of the project. |
| **Push** | Can save your Markdown changes to the shared repo; you may enter an optional **commit message** in the dialog. If Push is blocked, **Pull** first. |
| **Export Staged** | Puts **staged** files into a ZIP. See the warning below. |

Saving a Markdown file can **auto-stage** it for Git; you may see a note in the list. You still use **Push** when you want to send commits to the server.

> **WARNING — Export Staged**  
> After a successful export, the app **cleans your working folder** so a pull can run—including removing **untracked** files. Save your work, know what “staged” means, keep the ZIP somewhere safe, and ask a colleague before using this if you are unsure.

---

## Keyboard shortcuts

Same actions as the **File** and **Git** menus.

**Windows and Linux:** use **Ctrl**.  
**Mac:** use **⌘ (Command)** instead of **Ctrl**—for example **⌘+O** for Open File and **⌘+Shift+S** for Status. That matches how the shortcuts usually appear in the menu bar on macOS.

### File menu

| Menu action | Windows / Linux | Mac |
|-------------|-----------------|-----|
| Open File | `Ctrl+O` | `⌘+O` |
| Save File | `Ctrl+S` | `⌘+S` |
| Open Folder | `Ctrl+F` | `⌘+F` |
| Open Explorer | `Ctrl+E` | `⌘+E` |
| Show Live Preview | `Ctrl+P` | `⌘+P` |
| Show Analyzer Output | `Ctrl+A` | `⌘+A` |

### Git menu

| Menu action | Windows / Linux | Mac |
|-------------|-----------------|-----|
| Status | `Ctrl+Shift+S` | `⌘+Shift+S` |
| Fetch | `Ctrl+Shift+F` | `⌘+Shift+F` |
| Pull | `Ctrl+Shift+L` | `⌘+Shift+L` |
| Push | `Ctrl+Shift+P` | `⌘+Shift+P` |
| Export Staged | `Ctrl+Shift+E` | `⌘+Shift+E` |

---

## If something goes wrong

- **App won’t start:** Run it from inside the **project** folder.
- **Analyzer won’t run:** Put the file under the correct **folder type** (see above).
- **Push blocked:** **Pull** first; only use **Export Staged** after reading the warning above.

For repeated errors, tell support **what you clicked** and the **exact message** on screen.
