echo "This script will set up a python virtual env in the dir that it is provoked, pleasd make sure your python3 command is available"
sudo apt-get -y install libmysqlclient-dev
echo "Installing Virtual Environment module"
python3 -m pip install virtualenv
echo "Setting up venv"
python3 -m venv env
source env/bin/activate
echo "Installing required packages"
python3 -m pip install -r requirements.txt
echo "Running Front End server now"
nohup python3 frontend/run.py > frontend_log.txt &
echo "Running MemCache server now"
nohup python3 memcache/run.py > memcache_log.txt &

