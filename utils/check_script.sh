cd /home/da1/Desktop/omar_projects/Survista/utils
export PATH=/home/da1/anaconda3/envs/omar_env/bin:/usr/bin:/bin
echo $PATH >> ~/Desktop/output.txt
export GOOGLE_APPLICATION_CREDENTIALS=/home/da1/Desktop/omar_projects/SentimentAPIAuth.json
python fileChecker.py
