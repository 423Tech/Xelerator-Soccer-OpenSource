python3 -m venv ./venv --system-site-packages
source ./venv/bin/activate
pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
pip install -r ./src/requirements.txt
echo "Virtual environment setup complete.✅"