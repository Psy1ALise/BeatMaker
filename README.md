The project is a beat maker that creates a UI interface that can let user to import beat, record their own voice sample and set beat pattern and play the loop of the beat.

Environment:

Python 3.9 on Windows 10

Installation:

pip install -r requirements.txt

To execute the program, an empty folder named "samples" need to be created along with the source code.

A Screenshot:

![image](https://github.com/Psy1ALise/BeatMaker/assets/54691057/1b410f1e-fd14-40f1-9486-0887a560da9f)

The project is made on Model-View-Controller (MVC) structure. Beside the driver main program, model.py hold the data structures in the back end, view.py handles the GUI interface, and controller.py provides the IO functionalities.

The UI is built with within pyqt5. This is a library provide a better UI design with more delicate built-in functions than Tkinker. This is why I choose pyqt5.

The UI divided into three parts, the top panel, app panel and bottom panel.

The top panel has a set of user control buttons.

The beat panel has a grid of 8 rows 33 buttons. The first column of buttons are used for sample management. And the rest of the columns are used for beat pattern.

The bottom panel shows a list of available samples and a preview section. The user can pick a sample to preview it.

The main part of the user interaction is on the top panel and the app panel.

Beat Editing:

On the App panel, when user turns on/off a button in the grid, it will change the beat pattern data structures in model.

The user can right click on the first row to open a context menu to set or clear sample from one track.

Playback:

When hit play the controller will scan through the beat pattern in the model and play the samples according to the beat pattern at the set BPM from left to right from the start.

Clear sample/beat:

There are clear samples, clear beat function. The controller will modify the according data structures in the model, and also update the GUI.

Load/save:

When user click save, the controller will give create record and save the data structures of the used samples and beat pattern into a json file into the "saves" folder (will be created if not exists).

When click load, the controller will open a the save folder and let the user pick the json file that has the pattern saved priorly.

Record:

When user hit record, the controller will open an audio stream that record from the user's audio input. The user will be asked to name the sample after it is recorded and then update the available sample list.
