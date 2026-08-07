# Py_Li_Engage 

A robust, modular, and humanized browser automation framework built in Python for LinkedIn session management, intelligent content engagement, and multi-profile interaction workflows.

---

## Project Structure

```text
C:.
├───.github
│       dependabot.yml
├───.venv
├───data
│       config.json
│       linkedin-profiles.json
│       linkedin-cookies.json
├───py_li_engage
│       __init__.py
│       config.py
│       engage.py
│       save_cookie.py
│       services.py
│       workflow_elements.py
├───scripts
│       misc.ps1
│       upgrade.ps1
    .gitignore
    pyproject.toml
    README.md

```

---

## Installation Guidelines

1. Ensure you have **Python 3.14+** and **`uv`** installed.
2. Clone the repository and navigate into the project root.
3. Create and activate your virtual environment:
```powershell
uv venv .venv --python 3.14
.venv\Scripts\Activate.ps1

```


4. Install package dependencies and download Playwright browser binaries:
```powershell
uv pip install -e .
playwright install

```



---

## Configuration Files Setup

Create your configuration files inside the `data/` directory:

1. **`data/config.json`**:
```json
{
  "GROQ_API_KEY": "your-groq-api-key-here"
}

```


2. **`data/linkedin-profiles.json`**:
```json
[
  "https://www.linkedin.com/in/target-profile-one/"
]

```



---

## Execution Workflow

### Step 1: Save Authentication Cookies

First, run the session cookie saver script to log in manually and cache your authenticated session state:

```powershell
python py_li_engage/save_cookie.py

```

### Step 2: Run the Automation Engine

Once your cookies are saved, execute the master orchestrator pipeline:

```powershell
python -m py_li_engage.engage

``` 