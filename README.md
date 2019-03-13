# Krystal
- Author: Able (Jaylen Douglas)
- Platform: MacOS
- Version: 0.91.0
- Required: [Skip to 'Getting Started']
- Python >= 3.6 Required<br><br>

Krystal is in <b>Alpha</b> testing.

# Use
To use Krystal please register for an account on <a href="https://www.able.digital#access">Able Access</a>, there you will receive
your own AiKey. This key grants you access to all of Able's software.
<b>Note: You can use Krystal in Demo mode.</b>

# Getting Started:
There are a few dependencies required to use Krystal. I've created a python script that will install everything for you.
Feel free to open the file to check each individual package.
1) Clone or download the zip file for Krystal<br>
2) Run 'install.py'
3) Run 'python3 krystal.py'

# Change Log:
Date: March 12, 2019 - Version: <b>0.91.0</b>

1) Threading operations simplified
2) All knowledge given is processed, organized and stored locally (Memory)
3) You can run requests via terminal entry by uncommenting line 45 and commenting line 44 on krystal.py (run as normal)

# Heads up
Planned updates and improvements | Completion dates:
1) Krystal web application (any smartphone compatibility) | N/A
2) Less dependency on 'on-the-spot' information gathering (upon model completion) | N/A
3) Mobile application (not of importance at the moment, major changes to Krystal still needed) | N/A

# Starting Krystal:
Interacting with Krystal starts with: <i>"Hey Krystal" or "Krystal"</i><br>
Accepted commands:

1) "Open [application]" (i.e. "Open Safari")
2) "Search for [your hearts desire]" (i.e. "Search Google for how to make the world's best sandwich")
1) "What is your name?"
2) "Who is Barack Obama?"
3) "Who is that?" (This uses face recognition to detect who's in front of the camera - Training required)
4) "What is that?" (This uses object detection to detect what object is in front of the camera - No training required)
# Training
Tensorflow is required for Krystal. To train Krystal on faces close to your heart refer to the 'Face Detection' section below.


# Features (Detailed)
<b>Face Detection (Vision)</b><br />
Krystal comes with a unique feature that allows her to detect whomever you desire with a blink of an eye (well, a
capture of a frame, but you get my point). She uses the well-designed source code of Ageitgey's
<a href="https://github.com/ageitgey/face_recognition">Face Recognition</a> software. In Ageitgrey's example code,
which Krystal uses, you must train a model that will contain the information for each individual person's name
(described as the folder name/label). The training script is contained within the "model" directory, the file is called
facerectrain.py. Special thanks to Ageitgrey. <br />
<b>NOTE:</b> Krystal comes with a pre-compiled model called "faces.ai" in the "model" directory, alongside the faces
she is trained on are located in the "train" folder. When you add or remove images in the "train" folder the model will
be updated upon training. If you would like to remove the known faces in the "train" directory please do so, but as
later version of Krystal are released this option will be deprecated and you will only be using a model that is
maintained by Able (with contributions from you of course). Login <a href="http://www.able.digital/access/login.php">here</a>
to add your selfie to our universal model for training and release in the future.
<br />
<b>Object Detection</b><br />
Krystal comes with an pre-trained Caffe model that contains a few commonly known or easy-to-train images. The images are
general and there is a good chance of misidentification of abstract or unique objects. You can see the exact images the
model can detect by checking the resources > Detection.py file.
<br />
<b>Personality & Thoughts</b><br />
Krystal contains a very simple personality model that contains general information about her such as her name, age or
creator. This is only invoked when a specific question or type of question is asked. As stable updates are released Krystal's 
personality model will expand in complexity and will begin to respond in conversation like dialogue.
Krystal is intended to always be running and will only gather information when activated.<br>

# Demo Mode
1) Data is not personalized in this mode. Meaning, Krystal will not have any information about you (i.e. your name or habits).
2) Automatic updates are disabled
3) Some features may be limited in the future

# Known issues
1) <b>Q/S</b>: Random info when asked about who/what someone/something.<br />
   A: This is due to a less than stable algorithm that parses the web for information on what you're searching for.<br>
2) <b>Q/S</b>: No file found named _snowboydetect.so<br />
   A: You may need to grab a precompiled build for Snowboy (follow their instructions <a href="https://github.com/Kitt-AI/snowboy">here</a>) then add the correct files to the "SBpy3" folder.
3) <b>Q/S</b>: I get a warning message from Tensorflow every time I start Krystal (i.e. keep_dims)<br />
   A: This is all dependant on Tensorflow, please ignore. Krystal will use a modified version of Tensorflow in the future.
4) <b>Q/S</b> I cannot connect to Able servers with AiKey
   A: Please run in demo mode. Features are being updated daily and Krystal's API is going through changes as well. 
