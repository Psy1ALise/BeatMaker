import os
import json
import pyaudio
import wave
import threading
from PyQt5.QtWidgets import QMenu, QInputDialog, QFileDialog
from PyQt5.QtCore import QUrl, QTimer
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent 

class BeatMakerController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.current_selected_row = None
        self.bpm = 100
        self.interval = 150
        self.isPlaying = False
        self.timer = QTimer()
        self.sample_players = {row: QMediaPlayer() for row in range(8)}
        self.current_column = 0

        # Connect Top Panels
        self.view.play_stop_button.clicked.connect(self.toggle_play_stop)
        self.view.bpm_spinbox.valueChanged.connect(self.updateBPM)
        self.view.clear_sample_button.clicked.connect(self.clear_samples)
        self.view.clear_beat_button.clicked.connect(self.clear_beat)
        self.view.load_button.clicked.connect(self.load_beat)
        self.view.save_button.clicked.connect(self.save_beat)
        self.view.record_button.clicked.connect(self.record_sample)

        # Connect Beat Maker
        for row, button in view.sample_buttons.items():
            button.clicked.connect(lambda _, row=row: self.on_sample_button_clicked(row))
        for row, button in self.view.sample_buttons.items():
            button.rightClicked.connect(self.on_sample_button_right_clicked)
        for key, button in view.beat_buttons.items():
            button.clicked.connect(lambda _, row=key[0], col=key[1]: self.on_beat_button_clicked(row, col))

        # Connect Bottom Panels
        self.view.refresh_sample.clicked.connect(self.refreshSampleList)
        self.view.play_stop_preview_button.clicked.connect(self.togglePlayStopPreview)
        self.view.player.stateChanged.connect(self.handlePlaybackStateChanged)
        self.view.seek_slider.sliderMoved.connect(self.seekPosition)
        self.view.player.positionChanged.connect(self.updateSlider)
        self.view.player.durationChanged.connect(self.updateDuration)
        self.view.sample_list.itemClicked.connect(self.sampleSelected)
        self.populateSampleListInView() # Populate the sample list in the view


    def toggle_play_stop(self):
        if self.view.play_stop_button.isChecked():
            self.view.play_stop_button.setText("Stop")
            self.play_stop_protection(True)
            self.updateBPM()
            self.startPlay()
            print("Play started")
        else:
            self.view.play_stop_button.setText("Play")
            self.play_stop_protection(False)
            self.stopPlay()
            print("Play stopped")

    def play_stop_protection(self, disable):
        # List of items to be disabled
        individual_buttons = [
            self.view.record_button,
            self.view.clear_sample_button,
            self.view.clear_beat_button,
            self.view.load_button,
            self.view.save_button,  
            self.view.play_stop_preview_button,  
            self.view.bpm_spinbox,  
        ]

        # Combine individual buttons and beat/sample buttons into one list
        all_buttons = individual_buttons + list(self.view.beat_buttons.values()) + list(self.view.sample_buttons.values())

        # Disable/enable all buttons in the combined list
        for button in all_buttons:
            button.setEnabled(not disable)

    def startPlay(self):
        self.sample_players = {}
        for row in range(8):
            sample_name = self.model.samples[row]
            if sample_name != "None":
                sample_path = self.model.getSampleFilePath("samples", sample_name)
                player = QMediaPlayer()
                player.setMedia(QMediaContent(QUrl.fromLocalFile(sample_path)))
                self.sample_players[row] = player

        self.audio_index = self.model.get_audio_index()
        self.current_column = 0
        self.timer.timeout.connect(self.highlightCurrentColumn)
        self.timer.timeout.connect(self.playBeats)
        self.timer.start(self.interval)

    def playBeats(self):
        for row, beats in self.audio_index:
            if self.current_column in beats:
                player = self.sample_players.get(row)
                if player:
                    if player.state() == QMediaPlayer.PlayingState:
                        player.stop()
                    player.play()

        self.current_column = 0 if (self.current_column + 1) >= 32 else self.current_column + 1

    def stopPlay(self):
        if self.timer.isActive():
            self.timer.stop()
            self.timer.timeout.disconnect(self.playBeats)
            self.timer.timeout.disconnect(self.highlightCurrentColumn)
            
        for row in range(8):
            button = self.view.beat_buttons[(row, (self.current_column - 1) if self.current_column > 0 else 31)]
            original_style = button.styleSheet()
            original_bg_color = original_style.split('background-color: ')[1].split(';')[0] if 'background-color:' in original_style else '#FFFFFF'
            button.setStyleSheet(f"QPushButton {{ border: 1px solid #000000; background-color: {original_bg_color}; border-radius: 5px; }}")

        for player in self.sample_players.values():
            if player:
                player.stop()

        self.current_column = 0

    def highlightCurrentColumn(self):
        # Iterate through all rows and update only the buttons in the current column
        for row in range(8):
            button = self.view.beat_buttons[(row, self.current_column)]
            original_style = button.styleSheet()
            original_bg_color = original_style.split('background-color: ')[1].split(';')[0] if 'background-color:' in original_style else '#FFFFFF'
            button.setStyleSheet(f"QPushButton {{ border: 2px solid #FFFFFF; background-color: {original_bg_color}; border-radius: 5px; }}")

        # Reset the style of buttons in the previous column
        for row in range(8):
            button = self.view.beat_buttons[(row, (self.current_column - 1) if self.current_column > 0 else 31)]
            original_style = button.styleSheet()
            original_bg_color = original_style.split('background-color: ')[1].split(';')[0] if 'background-color:' in original_style else '#FFFFFF'
            button.setStyleSheet(f"QPushButton {{ border: 1px solid #000000; background-color: {original_bg_color}; border-radius: 5px; }}")

    def updateBPM(self):
        # Update BPM based on the current value of the QSpinBox
        self.bpm = self.view.bpm_spinbox.value()
        self.updateBeatInterval()

    def updateBeatInterval(self):
        # Calculate the new interval based on BPM
        interval = int((15.0 / self.bpm) * 1000.0)  # Convert BPM to interval in ms
        self.interval = interval

    def clear_samples(self):
        self.model.clear_all_samples()

    def clear_beat(self):
        self.current_selected_row = None
        for row in range(8):
            for col in range(32):
                beat_button = self.view.beat_buttons[(row, col)]
                original_color = "#2A2A2A" if (col + 1) % 4 != 1 else "#414141"  # Set to original color
                beat_button.setStyleSheet(f"background-color: {original_color}; border-radius: 5px;")
        self.model.clear_button_state()

    def load_beat(self):
        self.clear_samples()
        self.clear_beat()
        # Ensure 'saves' directory exists and get the list of saved files
        saves_dir = os.path.join(os.path.dirname(__file__), 'saves')
        if not os.path.exists(saves_dir):
            print("No saved beats available.")
            return
        # Get list of saved beats
        saved_beats = [f for f in os.listdir(saves_dir) if f.endswith('.json')]
        # Check if there are saved beats
        if not saved_beats:
            print("No saved beats found.")
            return
        # Open file selection dialog
        selected_file, _ = QFileDialog.getOpenFileName(self.view, "Load Beat", saves_dir, "JSON Files (*.json)")
        # If a file is selected, load it
        if selected_file:
            with open(selected_file, 'r') as file:
                data = json.load(file)
                self.model.samples = data.get('samples', ["None"] * 8)
                button_states = data.get('button_states', {})
                self.model.button_states = {tuple(map(int, k.split(','))): v for k, v in button_states.items()}
                bpm = data.get('bpm', 100)  # Get the BPM value or default to 100
                self.view.bpm_spinbox.setValue(bpm)  # Update the BPM spinbox in the view
                self.update_view_from_model()
            print(f"Beat '{os.path.basename(selected_file)}' loaded successfully.")
        else:
            print("Load cancelled.")

    def update_view_from_model(self):
        # Update beat buttons based on the button_states
        for row in range(8):
            for col in range(32):
                beat_button = self.view.beat_buttons[(row, col)]
                is_on = self.model.get_button_state(row, col)
                if is_on:
                    beat_button.setStyleSheet(f"background-color: {self.view.row_colors[row]}; border-radius: 5px;")

    def save_beat(self):
        # Ensure 'saves' directory exists
        saves_dir = os.path.join(os.path.dirname(__file__), 'saves')
        if not os.path.exists(saves_dir):
            os.makedirs(saves_dir)

        # Prompt for the name of the beat
        beat_name, ok = QInputDialog.getText(self.view, "Save Beat", "Enter a name for the beat:")
        if ok and beat_name:
            # Construct the file path
            file_path = os.path.join(saves_dir, beat_name + '.json')

            # Prepare the data to be saved
            data_to_save = {
                'samples': self.model.samples,
                'button_states': {','.join(map(str, k)): v for k, v in self.model.button_states.items()},
                'bpm': self.view.bpm_spinbox.value()  # Save the BPM value
            }

            # Save the data to a JSON file
            with open(file_path, 'w') as file:
                json.dump(data_to_save, file, indent=4)
            print(f"Beat '{beat_name}' saved successfully.")
        else:
            print("Save cancelled.")
    
    def record_sample(self):
        if self.view.record_button.isChecked():
            # Start recording
            self.view.record_button.setText("Stop Recording")
            # Disable other buttons
            self.record_protection(True)
            self.is_recording = True
            self.audio_frames = []
            self.recording_thread = threading.Thread(target=self.record_audio)
            self.recording_thread.start()
        else:
            # Stop recording
            self.view.record_button.setText("Start Recording")
            self.record_protection(False)
            self.is_recording = False
            self.recording_thread.join()  # Wait for recording thread to finish

            # Prompt for file name
            file_name, ok = QInputDialog.getText(None, "Save Recording", "Enter file name:")
            if ok and file_name:
                self.save_recorded_audio(file_name)

    def record_protection(self, disable):
        # List of items to be disabled
        individual_buttons = [
            self.view.play_stop_button,
            self.view.clear_sample_button,
            self.view.clear_beat_button,
            self.view.load_button,
            self.view.save_button,  
            self.view.play_stop_preview_button,  
            self.view.bpm_spinbox,  
        ]

        # Combine individual buttons and beat/sample buttons into one list
        all_buttons = individual_buttons + list(self.view.beat_buttons.values()) + list(self.view.sample_buttons.values())

        # Disable/enable all buttons in the combined list
        for button in all_buttons:
            button.setEnabled(not disable)
    
    def record_audio(self):
        # Set up the recording parameters
        format = pyaudio.paInt16  # 16-bit resolution
        channels = 2              # Stereo recording
        rate = 44100              # Sample rate in Hz
        chunk = 1024              # Buffer size

        # Initialize PyAudio
        audio = pyaudio.PyAudio()

        # Open the stream for recording
        stream = audio.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)

        # Recording loop
        while self.is_recording:
            data = stream.read(chunk)
            self.audio_frames.append(data)

        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        # Terminate PyAudio
        audio.terminate()

    def save_recorded_audio(self, file_name):
        # Define the path to the 'samples' folder
        samples_folder = os.path.join(os.path.dirname(__file__), 'samples')

        # Check if the 'samples' directory exists, create it if not
        if not os.path.exists(samples_folder):
            os.makedirs(samples_folder)

        # Complete file path
        complete_file_path = os.path.join(samples_folder, file_name + '.wav')

        # Save the recorded audio to a WAV file in the 'samples' folder
        wav_file = wave.open(complete_file_path, 'wb')
        wav_file.setnchannels(2)  # Stereo
        wav_file.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
        wav_file.setframerate(44100)
        wav_file.writeframes(b''.join(self.audio_frames))
        wav_file.close()

        self.model.refreshSampleFiles()
        self.view.populateSampleList(self.model.getSamples())

    def on_beat_button_clicked(self, row, col):
        # Toggle the button state and update the model
        is_on = self.model.toggle_button_state(row, col)
        beat_button = self.view.beat_buttons[(row, col)]
        if is_on:
            # Set the beat button to the row color
            beat_button.setStyleSheet(f"background-color: {self.view.row_colors[row]}; border-radius: 5px;")
            if not self.isPlaying:
                self.play_preview(row)
        else:
            beat_button.setStyleSheet("background-color: #909090; border-radius: 5px;")
        # If the selected row is different from the current row, update the row selection
        if self.current_selected_row != row:
            self.select_row(row)

    def on_sample_button_clicked(self, row):
        self.play_preview(row)

        if self.current_selected_row != row:
            self.select_row(row)

    def select_row(self, row):
    # Deselect the current row if a different row's sample button is clicked
        if self.current_selected_row is not None and self.current_selected_row != row:
            self.deselect_row(self.current_selected_row)

        # Update the current selected row
        self.current_selected_row = row

        # Update the sample button color for the new row
        new_color = self.view.row_colors[row]
        self.view.sample_buttons[row].setStyleSheet(f"background-color: {new_color}; border-radius: 5px;")

        # Update the beat buttons in the new row
        for col in range(32):
            button = self.view.beat_buttons[(row, col)]
            if self.model.get_button_state(row, col):
                button.setStyleSheet(f"background-color: {new_color}; border-radius: 5px;")
            else:
                button.setStyleSheet("background-color: #909090; border-radius: 5px;")

    def deselect_row(self, row):
        # Reset the sample button to its original color
        original_sample_color = "#2A2A2A"
        self.view.sample_buttons[row].setStyleSheet(f"background-color: {original_sample_color}; border-radius: 5px;")

        # Reset the 'off' beat buttons to their original colors
        for col in range(32):
            if not self.model.get_button_state(row, col):
                original_button_color = "#2A2A2A" if (col + 1) % 4 != 1 else "#414141"
                beat_button = self.view.beat_buttons[(row, col)]
                beat_button.setStyleSheet(f"background-color: {original_button_color}; border-radius: 5px;")

    def play_preview(self, row):
        sample_name = self.model.samples[row]
        if sample_name != "None":
                # Get the full path of the sample file
                sample_path = self.model.getSampleFilePath("samples", sample_name)
                # Set the media to the player and play
                self.view.player.setMedia(QMediaContent(QUrl.fromLocalFile(sample_path)))
                self.view.play_stop_preview_button.setChecked(True)
                self.view.play_stop_preview_button.setText("Stop")
                self.view.player.play()

    def on_sample_button_right_clicked(self, row, globalPos):
        # Create the context menu
        self.select_row(row)
        context_menu = QMenu()
        choose_sample = self.createSampleSubMenu(row)
        context_menu.addMenu(choose_sample)
        clear_sample = context_menu.addAction("Clear Sample")
        clear_sample.triggered.connect(lambda: self.clearSample(row))
        context_menu.exec_(globalPos)

    def createSampleSubMenu(self, row):
        submenu = QMenu(f"Choose Sample for Row {row}")
        samples = self.model.getSamples()
        for sample in samples:
            action = submenu.addAction(sample)
            action.triggered.connect(lambda _, s=sample: self.onSampleSelected(row, s))
        return submenu

    def onSampleSelected(self, row, sample):
        print(f"Set sample {sample} for row {row}")
        self.model.set_sample(row, sample)

    def clearSample(self, row):
        print(f"Clear row {row} sample")
        self.model.clear_sample(row)
    
    def populateSampleListInView(self):
        sample_files = self.model.getSamples()
        self.view.populateSampleList(sample_files)

    def refreshSampleList(self):
        self.model.refreshSampleFiles()
        self.view.populateSampleList(self.model.getSamples())

    def togglePlayStopPreview(self):
        if self.view.play_stop_preview_button.isChecked():
            self.startPreview()
            self.view.play_stop_preview_button.setText("Stop")
        else:
            self.stopPreview()
            self.view.play_stop_preview_button.setText("Play")

    def startPreview(self):
        if self.view.sample_list.currentItem():
            sample_file = self.view.sample_list.currentItem().text()
            sample_path = os.path.join(os.path.dirname(__file__), "samples", sample_file)
            self.view.player.setMedia(QMediaContent(QUrl.fromLocalFile(sample_path)))
            self.view.player.play()

    def handlePlaybackStateChanged(self, state):
        if state == QMediaPlayer.StoppedState:
            self.view.play_stop_preview_button.setChecked(False)
            self.view.play_stop_preview_button.setText("Play")

    def stopPreview(self):
        self.view.player.stop()

    def seekPosition(self, position):
        self.view.player.setPosition(position)

    def updateDuration(self, duration):
        self.view.seek_slider.setRange(0, duration)  # Set the range in milliseconds
        duration_in_seconds = max(duration // 1000, 1)  # Round up to at least 1 second
        minutes = duration_in_seconds // 60
        seconds = duration_in_seconds % 60
        formatted_duration = f"{minutes:02d}:{seconds:02d}"  # Format to xx:xx
        self.view.sample_duration_label.setText(formatted_duration)

    def updateSlider(self, position):
        self.view.seek_slider.setValue(position)  # Update position in milliseconds

    def sampleSelected(self, item):
        sample_file = item.text()
        sample_path = os.path.join(os.path.dirname(__file__), "samples", sample_file)
        self.view.player.setMedia(QMediaContent(QUrl.fromLocalFile(sample_path)))
        self.view.player.durationChanged.connect(self.updateDuration)
        # Temporarily load the media to fetch its duration
        self.view.player.stop()  # Stop immediately to avoid playing
