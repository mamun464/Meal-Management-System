# Step by Step guideline to setup the repo locally

Please follow the steps sequentially to setup the repo in your local environment without errors. Approximate setup time is 1 hour. Skip the steps you have already done.

### Step 1: For Ubuntu/Linux
```sh
sudo apt update
sudo apt install python3-venv
```
### Step 2: Create Vertual-Environment
```sh
python3 -m venv .venv

```

### Step 3: Active your Vertual-Environment
```sh
source .venv/bin/activate
```
### Step 4: Install Required Packages
```sh
pip install -r requirements.txt
```

### Step 5: Run the project
```sh
python manage.py runserver
```




