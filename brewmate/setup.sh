sudo nano /boot/config.txt
dtoverlay=w1-gpio,gpiopin=4
sudo modprobe w1-gpio
sudo modprobe w1-therm
sudo pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
