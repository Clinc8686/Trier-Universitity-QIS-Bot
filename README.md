# Trier-Universitity-QIS-Bot
A Web-Crawler that reads the grade system of University-Trier QIS and inform by IFTTT Webhook and Discord Webhook.<br/>
<br/>
Required Packages:<br/>
datetime<br/>
sys<br/>
mechanize<br/>
requests<br/>
re<br/>
os.path<br/>
<br/>

Run the start.py script in crontab on linux. Or you can run the start_looped.py script, which only have to started once.
For Windows is start_looped_windows.pyw recommended. It will change the registry to run every startup automatically.
But you need for the Windwos version further the Package winreg.
