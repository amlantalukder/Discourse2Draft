ps aux | grep "/Discourse2Draft/.venv/bin/gunicorn" | grep -v grep
pkill -f /Discourse2Draft/.venv/bin/gunicorn
uv run gunicorn -k workers.MyUvicornWorker -b 127.0.0.1:8229 main:app --daemon