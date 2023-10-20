# glitchy
___
- you can connect to the Pi by ssh port 22
- user: pi
- password: android
- or using the VNC viewer on port 5900 (to use the GUI)
___

to download the `glitchy` repository to RPi execute:

```
git clone https://github.com/simonawist/glitchy.git
```
remember to check out to branch master:
```
git checkout master
```
now you have the latest code
___
to run the experiment execute:
```
python3 app.py
```

Inside `app.py` you can change the parameters of the experiment - pls take a look.

___
to collect data from experiment execute:
```
python3 android-runner android-runner/config.json
```

Inside `android-runner` you can change the parameters of the  `devices.json` and `config.json` files - pls take a look.

___
The Raspberry Pi is configured following this guide:
https://github.com/S2-group/android-runner/blob/master/docs/rpi_ar_setup.md

- android-sdk is installed
- adb is installed 
- monkeyrunner is installed 
- java was downgraded from 11 to 8
- tmux is installed
- python-slugify installed
- lxml installed
- psutil installed
- pluginbase installed
- pandas installed
- numpy installed

- the external drive is configured, and available at `/home/pi/external_memory`
- inside there is our code pulled down from github (`glitchy` folder)
- also `android-runner` with examples is downloaded there
- the configuration of the `wpa_supplicant.conf` file was modified so as to allow the RPi to connect to the laptop's hotspot:
```
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
```
- the RPi's WiFi chip was activated:
```
sudo ifconfig wlan0 down
sudo ifconfig wlan0 up
```
- the RPi was restarted:
```
sudo reboot
```
- after restart, the RPi automatically connected to the laptop's WiFi. The Android device was connected via the same laptop's WiFi (and connected via port 5555 to the RPi). This allowed the experiment to be run without the need to connect a USB cable to the RPi, and therefore avoiding the device to be charged during the run (instead, the device was charged between runs).

<p align="center">
<img src="https://github.com/simonawist/android-runner/blob/master/glitchy/Experiment%20setup.png" alt="Experiment setup" width="500"/>
</p>

___
Before running the experiment, the Android devices were prepared as follows:
- all devices wiped (factory reset)
- developer options and USB debugging enabled
- "Stay awake" option enabled in Developer options 
- WhatsApp, Messenger and Telegram installed on all devices
- `com.example.batterymanager_utility.apk` installed on all devices
- minimum screen brightness
- any services with push notifications (e.g., Google Play Store, Google Play Services, Google News, Samsung Push Service etc.) turned off
- location services, bluetooth, sound and vibrations turned off
