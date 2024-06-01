This repo is the code for a youtube video collaboration between Mellow labs and Make it for less
# Video links
[![Mellow video](images/mellow%20thumbnail.jpg)](https://youtu.be/H-ASTThyACs?si=M-ha3bR2ZG4uutzs) [![Make it for less](images/makeIt%20thumbnail.png)](https://youtu.be/XPEIRgjqhrA)

# Required Libraries (Available from Arduino library manager)
- AnimatedGif
- PNGDec
- TFT_espi

# Instruction for web server
- Go to [render website](https://render.com/)
- create account
- On your dashboard create a new Web Service
- Choose "Build and deploy from a Git repository"
- In the public git repository section enter "https://gitlab.com/makeitforless/love-box-server" and click continue
- Enter whatever name you want
- change start command to "gunicorn -t 0 -w 4 app:app"
- Select free as intance type
- click create web service
- From the dashboard click on your new service
- Save the URL at the top left of the page, you will need to enter it into the Arduino code later
- Go to the URL and make sure you see the page from the video

# Instructions for CYD
- Soldering
    - The only only soldering needed for this project is to connect the servo power, and ground to the pins micro usb pins on the CYD and the data pin to GPIO 21
- Programming
    - Download the git repo and open heart-box.ino
    - If using the Arduino IDE make sure that all files are added to project by going to Sketch > Add File and adding GIFDraw.ino and PNG_FS_Support,ino
    - Find User_Setup.h file (should be wherever your Arduino install is located) and replace with the User_Setup.h file from this repo 
    - Follow [this](https://randomnerdtutorials.com/installing-the-esp32-board-in-arduino-ide-windows-instructions/) guide to set up the arduino ide to program the esp32
    - Select the ESP32 Dev Module as your board
    - Change the "ssid" variable to the name of your wifi network
    - Change the "password" variable to the password for your wifi
    - Change the "render_site" variable to the URL from your render site + "/longPoll"
    - Upload
    - If everything is working you should see Connecting to \<your wifi name\> then the current time.
    - You should now be able to send a photo or gif from your website to the device

    # 3D print file
    The files for 3D printing the case are available [here](https://www.printables.com/@Mellow)


