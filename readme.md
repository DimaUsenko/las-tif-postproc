# Usage 

Python 3.10 | [requirements.txt](./requirements.txt)
```bash
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

At first run [main.py](src/main.py) script for creating preferences file: 
```bash
cd src
python main.py
```

After creating preferences.json file in [src](./src) directory u can specify dataset (absolute) path:
```yaml
tif_dir: "/home/deusenko/PycharmProjects/las-tif-postproc/src/tif_dir"
```

Then u can run script:
```bash
python main.py
```

