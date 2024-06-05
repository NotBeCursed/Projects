# CPM - CLI Password Manager
---

## Setup
**Install requirements**
```
pip install -r requirements.txt
```

**Compile code**
To protect the code and, above all, access to your data, we recommend you **compile** the following code
```
python3 -m py_compile cpm.py
mv ./__pycache__/cpm* cpm
rm -rf ./__pycache__
rm -f cpm.py
```

**Run code**
```
$ python3 ./cpm -h

usage: cpm [-h] [--file FILE] [--login LOGIN] [--password PASSWORD] [--title TITLE] [--description DESCRIPTION] [--all] {add,delete,show}

CLI Password Manager

positional arguments:
  {add,delete,show}

optional arguments:
  -h, --help            show this help message and exit
  --file FILE, -f FILE  JSON database file
  --login LOGIN, -l LOGIN
                        Specify login
  --password PASSWORD, -p PASSWORD
                        Specify password
  --title TITLE, -t TITLE
                        Specify title
  --description DESCRIPTION, -d DESCRIPTION
                        Add a description
  --all, -a             Delete/Show all entries
```
