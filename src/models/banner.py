from dataclasses import dataclass

from PyQt5.QtCore import QDate

from src.models.showing import Showing

DATE_FORMAT = 'dd.MM.yyyy'


@dataclass(slots=True)
class Banner:
    id: int = 0
    name: str = ''
    company_name: str = ''
    date_start: QDate = QDate()
    date_end: QDate = QDate()
    _min_showings: int = 0
    _max_showings: int = 0
    _showings: list[Showing] = ()

    def __init__(self, id: int, name: str, company_name: str, date_start: QDate,
                 date_end: QDate, min_showings: int, max_showings: int, showings: list):
        if date_start.daysTo(date_end) < 0:
            raise Exception('Incorrect dates were entered.')
        if min_showings < 0 | max_showings < 0:
            raise Exception('The number of shows cannot be negative.')
        if min_showings > max_showings:
            raise Exception('The minimum number of shows cannot be higher than the maximum number of shows.')
        self.id = id
        self.name = name
        self.company_name = company_name
        self.date_start = date_start
        self.date_end = date_end
        self.min_showings = min_showings
        self.max_showings = max_showings
        self._showings = showings

    @property
    def min_showings(self) -> int:
        return self._min_showings

    @min_showings.setter
    def min_showings(self, min_showings: int):
        if min_showings < 0:
            min_showings = 0
        self._min_showings = min_showings

    @property
    def max_showings(self) -> int:
        return self._max_showings

    @max_showings.setter
    def max_showings(self, max_showings: int):
        if max_showings < 0:
            max_showings = 0
        self._max_showings = max_showings

    @property
    def showings(self) -> list[Showing]:
        return self._showings

    @showings.setter
    def showings(self, sh: list[Showing]):
        self._showings = sh

    def add_showing(self, showing: Showing):
        self._showings.append(showing)

    def pop_showing(self, index):
        showing = self._showings.pop(index)
        return showing

    def date_start_str(self) -> str:
        return self.date_start.toString(DATE_FORMAT)

    def date_end_str(self) -> str:
        return self.date_end.toString(DATE_FORMAT)

    def to_banner_short_data(self):
        return BannerShortData(self.name, self.company_name, self.date_start,
                               self.date_end, self.min_showings, self.max_showings)

    # Getting the number of banner impressions for the selected date (default for current date)
    def count_showings_for_date(self, date: QDate = QDate.currentDate()) -> int:
        amount = 0
        for sh in self._showings:
            if sh.datetime.date() == date:
                amount += 1
        return amount

    def is_active_on_date(self, date: QDate):
        return self.date_start.daysTo(date) >= 0 & date.daysTo(self.date_end) >= 0


# Brief information about banner
@dataclass(slots=True)
class BannerShortData:
    name: str = ''
    company_name: str = ''
    date_start: QDate = QDate()
    date_end: QDate = QDate()
    _min_showings: int = 0
    _max_showings: int = 0

    def __init__(self, name: str, company_name: str, date_start: QDate,
                 date_end: QDate, min_showings: int, max_showings: int):
        if date_start.daysTo(date_end) < 0:
            raise Exception('Incorrect dates were entered.')
        if min_showings < 0 | max_showings < 0:
            raise Exception('The number of shows cannot be negative.')
        if min_showings > max_showings:
            raise Exception('The minimum number of shows cannot be higher than the maximum number of shows.')
        self.name = name
        self.company_name = company_name
        self.date_start = date_start
        self.date_end = date_end
        self.min_showings = min_showings
        self.max_showings = max_showings

    @property
    def min_showings(self) -> int:
        return self._min_showings

    @min_showings.setter
    def min_showings(self, min_showings: int):
        if min_showings < 0:
            min_showings = 0
        self._min_showings = min_showings

    @property
    def max_showings(self) -> int:
        return self._max_showings

    @max_showings.setter
    def max_showings(self, max_showings: int):
        if max_showings < 0:
            max_showings = 0
        self._max_showings = max_showings

    def date_start_str(self) -> str:
        return self.date_start.toString(DATE_FORMAT)

    def date_end_str(self) -> str:
        return self.date_end.toString(DATE_FORMAT)


# Information about banner promotion
@dataclass(slots=True)
class BannerPromotionData:
    name: str = ''
    company_name: str = ''
    min_sh_today: int = 0
    max_sh_today: int = 0
    fact_sh_today: int = 0
    min_sh_all: int = 0
    max_sh_all: int = 0
    fact_sh_all: int = 0
    date_start: QDate = QDate()
    date_end: QDate = QDate()

    def set_from_banner(self, banner: Banner, date: QDate):
        self.name = banner.name
        self.company_name = banner.company_name
        self.min_sh_today = banner.min_showings
        self.max_sh_today = banner.max_showings
        self.fact_sh_today = banner.count_showings_for_date(date)
        days = banner.date_start.daysTo(banner.date_end) + 1
        self.min_sh_all = days * banner.min_showings
        self.max_sh_all = days * banner.max_showings
        self.fact_sh_all = len(banner.showings)
        self.date_start = banner.date_start
        self.date_end = banner.date_end

    # Returns the percentage of completion of the minimum number of impressions for a fixed date
    def min_comp_percent_today(self) -> float:
        percent = self.fact_sh_today / self.min_sh_today * 100
        if percent > 100:
            percent = 100
        return percent

    # Returns the percentage of completion of the minimum number of impressions for all time
    def min_comp_percent_all(self) -> float:
        percent = self.fact_sh_all / self.min_sh_all * 100
        if percent > 100:
            percent = 100
        return percent

    def date_start_str(self) -> str:
        return self.date_start.toString(DATE_FORMAT)

    def date_end_str(self) -> str:
        return self.date_end.toString(DATE_FORMAT)
