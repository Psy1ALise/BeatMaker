from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QSpacerItem, QSizePolicy, QPushButton, QHBoxLayout, QLabel, QSpinBox, QListWidget, QSlider
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from PyQt5.QtMultimedia import QMediaPlayer

class BeatMakerView(QWidget): 
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('BeatMaker')
        self.setGeometry(100, 100, 1700, 800)
        self.setStyleSheet("background-color: #3C3C3C;") 
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        self.top_panel = self.createTopPanel(80, '#3C3C3C')  # Adjust the color as needed
        main_layout.addWidget(self.top_panel)

        self.app_panel = self.createAppPanel()
        main_layout.addWidget(self.app_panel)

        self.bottom_panel = self.createBottomPanel(160, '#3C3C3C')  # Adjust the color as needed
        main_layout.addWidget(self.bottom_panel)


    def createTopPanel(self, height, color):
        panel = QWidget()
        panel_layout = QHBoxLayout()  # Use QHBoxLayout to align items horizontally
        panel.setLayout(panel_layout)
        panel.setFixedHeight(height)
        panel.setStyleSheet(f"background-color: {color};")

        # Play/Stop Switch Button
        self.play_stop_button = QPushButton("Play")
        self.play_stop_button.setCheckable(True)
        self.play_stop_button.setStyleSheet("background-color: #606060; color: #FFFFFF;font-weight: bold;")
        panel_layout.addWidget(self.play_stop_button)

        # BPM Spin Box with Title
        bpm_label = QLabel("BPM:")
        bpm_label.setStyleSheet("color: #FFFFFF;")
        self.bpm_spinbox = QSpinBox()
        self.bpm_spinbox.setRange(1, 500)  # Set the range from 20 to 300
        self.bpm_spinbox.setValue(100)  # Default BPM of 100
        self.bpm_spinbox.setFixedWidth(100)  # Set width to 100 pixels
        self.bpm_spinbox.setStyleSheet("background-color: #606060; color: #FFFFFF;font-weight: bold;")
        panel_layout.addWidget(bpm_label)
        panel_layout.addWidget(self.bpm_spinbox)

        # Clear Sample Button
        self.clear_sample_button = QPushButton("Clear Samples")
        self.clear_sample_button.setStyleSheet("background-color: #606060; color: #FFFFFF;font-weight: bold;")
        panel_layout.addWidget(self.clear_sample_button)

        # Clear Beat Button
        self.clear_beat_button = QPushButton("Clear Beat")
        self.clear_beat_button.setStyleSheet("background-color: #606060; color: #FFFFFF;font-weight: bold;")
        panel_layout.addWidget(self.clear_beat_button)

        # Load Beat Button
        self.load_button = QPushButton("Load")
        self.load_button.setStyleSheet("background-color: #606060; color: #FFFFFF;font-weight: bold;")
        panel_layout.addWidget(self.load_button)

        # Save Button
        self.save_button = QPushButton("Save")
        self.save_button.setStyleSheet("background-color: #606060; color: #FFFFFF;font-weight: bold;")
        panel_layout.addWidget(self.save_button)
        
        # Record own voice Sample
        self.record_button = QPushButton("Start Recording")
        self.record_button.setCheckable(True)
        self.record_button.setStyleSheet("background-color: #606060; color: #FFFFFF;font-weight: bold;")
        panel_layout.addWidget(self.record_button)
        
        # Add a spacer to push everything to the left
        panel_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        return panel

    def createBottomPanel(self, height, color):
        panel = QWidget()
        panel_layout = QHBoxLayout()
        panel.setLayout(panel_layout)
        panel.setFixedHeight(height)
        panel.setAutoFillBackground(True)
        panel.setStyleSheet(f"background-color: {color};")

        sample_list_panel = self.createSampleListPanel()
        preview_panel = self.createMediaPlayerPanel()

        panel_layout.addWidget(sample_list_panel)
        panel_layout.addWidget(preview_panel)

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        panel_layout.addSpacerItem(spacer)
        
        return panel

    def createSampleListPanel(self):
        sample_list_panel = QWidget()
        sample_list_panel_layout = QVBoxLayout()
        sample_list_panel.setLayout(sample_list_panel_layout)
        sample_list_panel.setMaximumWidth(400)

        sample_list_title = QLabel("Available Samples")
        sample_list_title.setStyleSheet("color: white; font-weight: bold;")
        sample_list_panel_layout.addWidget(sample_list_title)
        
        self.refresh_sample = QPushButton("Refresh")
        self.refresh_sample.setFixedWidth(100)
        self.refresh_sample.setStyleSheet("color: white;")
        sample_list_panel_layout.addWidget(self.refresh_sample)

        self.sample_list = QListWidget()
        self.populateSampleList("samples")
        self.sample_list.setStyleSheet("QListWidget { color: white; }")
        sample_list_panel_layout.addWidget(self.sample_list)

        return sample_list_panel

    def populateSampleList(self, sample_files):
        self.sample_list.clear()
        for file in sample_files:
            self.sample_list.addItem(file)

    def createMediaPlayerPanel(self):
        preview_panel = QWidget()
        preview_panel_layout = QVBoxLayout()
        preview_panel.setLayout(preview_panel_layout)
        preview_panel.setMaximumWidth(400)

        player_title = QLabel("Preview Sample")
        player_title.setStyleSheet("color: white; font-weight: bold;")
        preview_panel_layout.addWidget(player_title)

        self.createMediaPlayerControls(preview_panel_layout)

        return preview_panel

    def createMediaPlayerControls(self, layout):
        self.player = QMediaPlayer()
        control_layout = QHBoxLayout()  # Horizontal layout for the controls

        # Play/Stop Preview Button
        self.play_stop_preview_button = QPushButton("Play")
        self.play_stop_preview_button.setCheckable(True)
        self.play_stop_preview_button.setStyleSheet("color: white;")
        control_layout.addWidget(self.play_stop_preview_button)

        # Seek Slider
        self.seek_slider = QSlider(Qt.Horizontal)
        self.seek_slider.setStyleSheet("QSlider::handle:horizontal { background-color: #909090; }")
        self.seek_slider.setDisabled(True)  # Disable the slider for user interaction
        control_layout.addWidget(self.seek_slider)

        # Sample Duration Label
        self.sample_duration_label = QLabel("00:00")
        self.sample_duration_label.setStyleSheet("color: white;")
        control_layout.addWidget(self.sample_duration_label)

        layout.addLayout(control_layout)


    def createAppPanel(self):
        panel = QWidget()
        panel_layout = QVBoxLayout()
        panel.setLayout(panel_layout)
        panel.setStyleSheet("background-color: #141414;")

        # Add spacer at the top (expanding)
        top_spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        panel_layout.addItem(top_spacer)

        # Create a layout for the beat matrix
        matrix_layout = QHBoxLayout()
        matrix_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        grid_layout = QGridLayout()
        grid_layout.setSpacing(8)

        self.beat_buttons = {}  # Dictionary to store buttons

        # Create beat matrix with sample selectors and beat buttons
        self.row_colors = ["#FF0000", "#FFA500", "#FFFF00", "#008000", "#00FFFF", "#0000FF", "#FFC0CB", "#800080"]
        self.beat_buttons = {}  # Store beat buttons
        self.sample_buttons = {}  # Store sample selector buttons

        for row in range(8):
            # Sample selector for the row
            sample_selector = self.createSampleSelector(row)
            self.sample_buttons[row] = sample_selector
            grid_layout.addWidget(sample_selector, row, 0)

            # Beat buttons
            for col in range(1, 33):  # 32 columns for beats
                beat_button = self.createBeatButton(row, col)
                grid_layout.addWidget(beat_button, row, col)
                self.beat_buttons[(row, col-1)] = beat_button

        matrix_layout.addLayout(grid_layout)
        matrix_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Add matrix layout to panel layout
        panel_layout.addLayout(matrix_layout)

        # Add spacer at the bottom (expanding)
        bottom_spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        panel_layout.addItem(bottom_spacer)

        return panel

    def createSampleSelector(self, row):
        sample_selector = SampleSelectorButton(row) 
        sample_selector.setFixedSize(70, 40) 
        sample_selector.setStyleSheet("""
            QPushButton {
                background-color: #2A2A2A; 
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #4D4D4D;
            }
        """)
        return sample_selector

    def createBeatButton(self, row, col):
        color = "#2A2A2A" if col % 4 != 1 else "#414141"  # Alternate color for specific columns
        beat_button = QPushButton()
        beat_button.setFixedSize(40, 40)
        beat_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color}; 
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: #4D4D4D;
            }}
        """)
        return beat_button

# create a customized right click class
class SampleSelectorButton(QPushButton):
    rightClicked = pyqtSignal(int, QPoint)

    def __init__(self, row, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.row = row

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            globalPos = self.mapToGlobal(event.pos())
            self.rightClicked.emit(self.row, globalPos)
        super().mousePressEvent(event)
