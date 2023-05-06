from dataclasses import dataclass

from PyQt5.QtCore import QDateTime

DATETIME_FORMAT = 'dd.MM.yyyy hh:mm'


@dataclass(slots=True)
class Showing:
    id: int = 0
    site_name: str = ''
    datetime: QDateTime = QDateTime()
    banner_id: int = 0

    def to_showing_short_data(self):
        return ShowingShortData(self.site_name, self.datetime)

    def datetime_str(self) -> str:
        return self.datetime.toString(DATETIME_FORMAT)


@dataclass(slots=True)
class ShowingShortData:
    site_name: str = ''
    datetime: QDateTime = QDateTime()
