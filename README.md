# PhaseWaitingRoomApp
Repo for the Aegis Phase Waiting Room Application


Phase Waiting Room Screen Application
==================================================
The waiting room screen application is an application that shall display in a Firefox browser the patients that are ready to enter the facility. The app shall display the next patient that can enter. The app will also show the current queue of patients per window (depending on the number of windows in the clinic). The browser shall cycle through displaying the news, weather in the clinic's location, random factoids, and patients being called up.

Development Instructions
==================================================
Install pip to install & use required python libraries.
```bash
    sudo apt-get install python-pip
```

Next, install the virtual environment - virtualenv.
```bash
    pip install virtualenv
```

Setup the virtual environment for the app
```bash
    virtualenv WaitingRoomApp
    cd WaitingRoomApp
```

Active the virtual env
```bash
    . bin/activate
```

Now, clone this repo
```bash
    git clone https://github.com/LuisFuentes/PhaseWaitingRoomApp.git
    cd PhaseWaitingRoomApp
```
Install the python dependencies using pip
```bash
    pip install -r requirements.txt
```
