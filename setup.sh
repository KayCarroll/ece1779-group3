echo "This script will set up a python virtual env in the dir that it is provoked, pleasd make sure your python3 command is available"
sudo apt-get -y install libmysqlclient-dev
echo "Installing Virtual Environment module"
python3 -m pip install virtualenv
echo "Setting up venv"
python3 -m venv env
source env/bin/activate
echo "Installing required packages"
pip install wheel==0.38.4
python3 -m pip install -r requirements.txt