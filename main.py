import sys
from PyQt5.QtWidgets import QApplication
from model import BeatMakerModel
from view import BeatMakerView
from controller import BeatMakerController

def main():
    app = QApplication(sys.argv)
    model = BeatMakerModel()
    view = BeatMakerView()
    controller = BeatMakerController(model, view)
    view.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
