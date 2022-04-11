export FLASK_APP=/home/ec2-user/web_tier/server/__init__.py
(trap 'kill 0' SIGINT; python3 result_poller/main.py & python3 controller/main.py & flask run --host 0.0.0.0 --port 5001) 