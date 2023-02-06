echo "Running Front End server now"
nohup python3 frontend/run.py > frontend_log.txt &
echo "Running MemCache server now"
nohup python3 memcache/run.py > memcache_log.txt &

