from PyQt5.QtCore import QAbstractTableModel, Qt

from src.models.showing import *


class ShowingEditor(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._showings = []
        self._headers = ["Site name", "Show time"]

    def init_showings(self, showings):
        self.beginResetModel()
        self._showings = showings
        self.endResetModel()

    def clear_showings(self):
        self.beginResetModel()
        self._showings = []
        self.endResetModel()

    def headerData(self, section, orientation, role=...):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headers[section]

    def rowCount(self, parent=None):
        return len(self._showings)

    def columnCount(self, parent=None):
        return len(self._headers)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            row = index.row()
            column = index.column()
            if column == 0:
                return self._showings[row].site_name
            if column == 1:
                return self._showings[row].datetime

    def get_short_showing(self, index: int) -> ShowingShortData:
        return self._showings[index].to_showing_short_data()
