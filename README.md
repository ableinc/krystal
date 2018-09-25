# Krystal
<b>Please Use Krystal In Demo Mode ONLY - New registrations are currently offline (Existing members are OK)</b>
- Author: Able (Jaylen Douglas)
- Platform: MacOS (Windows and Linux Support in the future)<br>
- Version: 0.90.4<br>
- Required: brew install swig, sox, portaudio [Do this before running depends.py]<br>
- Required: <i>tensorflow>=1.5, pyaudio, opencv-python, face_recognition, speechrecognition, tflearn, beautifulsoup</i> - You don't need to install these manually<br>
- Python >= 3.4 Required<br><br>
Krystal is intended to act as an intelligent friend you can always go to for a good conversation. 
She will learn you as a person and will accompany you when there may not be anyone else. <br><br>
Krystal is in <b>Alpha</b> testing 
now and you should not expect full functionality from her. Some features have been deprecated but may still show in the code. She will will be updated with algorithms that will achieve the goal of an artificially intelligent friend. Right now she is very basic but that is the point. 
# Use
To use Krystal please register for an account on <a href="http://www.able.digital#access">Able Access</a>, there you will receive
your own Able Access ID. This ID grants you access to all of Able's latest software.
<b>Note: You can use Krystal in Demo mode.</b>
<br>
# Change Log:
Change log updates per commit. Version: <b>0.90.4</b><br>
<b>MAJOR:</b> *Krystal's Responses Shortened Temporarily - Preparing for updates*
1) All API services have been restored.
2) Language engine was cleaned up. All information passed to Krystal will be categorized and stored for training later
3) Next: <br />
    - <b>Language Engine</b>
        * Create algorithm that detects the context of the given user statement and appropriately use Krystal's trained
        or on-demand resources to return an intelligent response.
        * Stronger training algorithm, possibly using the assistance of the cloud
    - <b>Command Handler</b>
        * Optimized processes that call upon different function to handle and manipulate the same information
    - <b>Training</b>
        * In the next few iterations of Krystal you may notice (while doing a benchmark test) that this application
        is consuming more power from your system. This is because as Krystal moves forward there will be 10% of dedicated
         resources spent on creating training and evaluation data. This means all of what you say to Krystal will be 
         stored and treated as data used to develop more sophisticated conversations with Krystal. 
        * No third parties will EVER gather, store, or share your conversations with Krystal. Your conversations are 
        completely created, stored, evaluated and trained locally and the binary files are sent back to Able's servers.
        * When you login to <a href="http://www.able.digital/access">Able Access</a> you'll notice a 'Records' tab, 
        as explained there all of what you say to Krystal and her replies are stored for your viewing. This introduces
        transparency between us and you. If it's not in the records it has NEVER been stored by Able.
# Heads up
Planned updates and improvements | Completion dates:
1) Krystal web application (any smartphone compatibility) | N/A
2) Less dependency on 'on-the-spot' information gathering (upon model completion) | N/A
3) Mobile application (not of importance at the moment, major changes to Krystal still needed) | N/A

# Starting Krystal: 
Interacting with Krystal starts with: <i>"Hey Krystal" or "Krystal"</i><br>
Accepted commands:
<br>
1) "Open [application]" (i.e. "Open Safari")<br>
2) "Search for [your hearts desire]" (i.e. "Search Google for how to make the world's best sandwich")<br>
1) "What is your name?"<br>
2) "Who is Barack Obama?"<br>
3) "Who is that?" (This uses face recognition to detect who's in front of the camera - Training required)<br>
4) "What is that?" (This uses object detection to detect what object is in front of the camera - No training required)<br>
# Training
Tensorflow is required for Krystal. To train Krystal on faces close to your heart refer to the 'Face Detection' section below. Also, please use clear images, no filters or facial effect...yes, no duck lips.
<br>
# First start:
1) Clone or download the zip file for Krystal<br>
2) Run 'depends.py'<br>
3) Then run 'python3 Krystal.py' (Remember that an Able Access ID is required to use Krystal.)<br>

# Features (In-Detail)
<h2>Face Detection (Vision)</h2>
Krystal comes with a unique feature that allows her to detect whomever you desire with a blink of an eye (well, a capture of a frame, but you get my point). She uses the well-designed source code of Ageitgey's <a href="https://github.com/ageitgey/face_recognition">Face Recognition</a> software. In Ageitgrey's example code, which Krystal uses, you must train a model that will contain the information for each individual person's name (described as the folder name/label). The training script is contained within the "model" directory, the file is called facerectrain.py. Special thanks to Ageitgrey. 
<b>NOTE:</b> Krystal comes with a pre-compiled model called "faces.ai" in the "model" directory, alongside the faces she is trained on are located in the "train" folder. When you add or remove images in the "train" folder the model will be updated upon training. If you would like to remove the known faces in the "train" directory please do so, but as later version of Krystal are released this option will be deprecated and you will only be using a model that is maintained by Able (with contributions from you of course). Login <a href="http://www.able.digital/access/login.php">here</a> to add your selfie to our universal model for training and release in the future.
<br>
<h2>Object Detection</h2>
Krystal comes with an pre-trained caffee model that contains a few commonly known or easy-to-train images. The images are general and there is a good chance of misidentification of abstract or unqiue objects. You can see the exact images the model can detect by checking the resources > Detection.py file. 
<br>
<h2>Personality & Thoughts</h2>
Krystal contains a very simple personality model that contains general information about her such as her name, age or creator. She is only invoked when a specific or relatively specific question is asked with a high probability of matching her knowledge. As stable updates are released in the coming time Krystal's personality model with expand with complexity and will begin to adapt to conversation in real-time as an artificially intellegent "human", or android for this purpose. Feel free to add information about Krystal, though in the future this will be removed. Krystal is intended to always be running and will only gather information when activated.<br>

# Demo Mode
1) Data is not personalized in this mode. Meaning, Krystal will not have any information on your name or habits about you.
2) Automatic updates are disabled
3) Some features may be limited in the future

# Known issues
1) Q: Random info when asked about who/what someone/something.<br>
   A: This is due to a less than stable algorithm that parses the web for information on what you're searching for.<br>
2) Q: No file found named _snowboydetect.so<br>
   A: You may need to grab a precombiled build for Snowboy (follow their instructions <a href="https://github.com/Kitt-AI/snowboy">here</a>) then add the correct files to the "SBpy3" folder. Also you could be running Krystal on an unsupprted platform
