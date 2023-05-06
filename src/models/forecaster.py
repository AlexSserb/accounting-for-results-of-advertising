from PyQt5.QtCore import QAbstractTableModel, Qt

from src.models.banner import *


class Forecaster(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._average_sh_in_week = [0, 0, 0, 0, 0, 0, 0]
        self._banners = []
        self._forecast_showings = []
        self._min_date = QDate()
        self._max_date = QDate()
        self._headers = ["Name", "Company", "End date of banner action"]

    def set_banners(self, banners: list[Banner]):
        self.beginResetModel()
        self._forecast_showings.clear()
        self._banners = banners
        self._min_max_dates()
        self._analyse_results()
        self._sort_banners()
        self._forecast_showings = [dict() for _ in range(len(self._banners))]
        self._calc_forecast_for_banners()
        self.endResetModel()

    # Calculate the average number of shows for each day of the week
    def _analyse_results(self):
        for banner in self._banners:
            for sh in banner.showings:
                date = sh.datetime.date()
                if date.daysTo(QDate().currentDate()) > 0:
                    self._average_sh_in_week[date.dayOfWeek() - 1] += 1
        amount_days_of_week = self._amount_days_of_week()
        for i, _ in enumerate(self._average_sh_in_week):
            self._average_sh_in_week[i] /= amount_days_of_week[i]

    # Getting the start and end dates of all banners
    def _min_max_dates(self):
        self._min_date = QDate().currentDate().addYears(10)
        self._max_date = QDate().currentDate().addYears(-10)
        for banner in self._banners:
            if self._min_date.daysTo(banner.date_start) < 0:
                self._min_date = banner.date_start
            if self._max_date.daysTo(banner.date_end) > 0:
                self._max_date = banner.date_end

    # Number of days of the week in the banner validity period
    def _amount_days_of_week(self):
        date = QDate(self._min_date)
        amount = [0, 0, 0, 0, 0, 0, 0]
        while date.daysTo(QDate().currentDate()) > 0:
            amount[date.dayOfWeek() - 1] += 1
            date = date.addDays(1)
        return amount

    # Sort banners by min amount of shows
    def _sort_banners(self):
        sorted_banners = []
        for banner in self._banners:
            if QDate().currentDate().daysTo(banner.date_end) > 0:
                sorted_banners.append(banner)
        self._banners = sorted(sorted_banners, key=lambda x: x.min_showings)

    # For each date to calculate the forecast of banner shows
    def _calc_forecast_for_banners(self):
        date = QDate().currentDate()
        while date.daysTo(self._max_date) >= 0:
            target_sh = self._average_sh_in_week[date.dayOfWeek() - 1]
            self._calc_forecast_for_date(date, target_sh)
            date = date.addDays(1)

    # Calculate impressions forecast for a certain date
    def _calc_forecast_for_date(self, date: QDate, target: int):
        all_min_sh = self._sum_min_showings_for_date(date)
        for i, banner in enumerate(self._banners):
            if banner.is_active_on_date(date):
                sh_for_date = round(banner.min_showings * target / all_min_sh)
                if sh_for_date > banner.max_showings:
                    sh_for_date = banner.max_showings
                self._forecast_showings[i][date] = sh_for_date

    # Total minimum number of banners shows for the given date
    def _sum_min_showings_for_date(self, date: QDate):
        all_min_sh = 0
        for banner in self._banners:
            if banner.is_active_on_date(date):
                all_min_sh += banner.min_showings
        return all_min_sh

    # Get the impression forecast for the banner
    # return [dates of banner action, forecasted impressions, min impressions, max impressions]
    def get_forecast_for_banner(self, index: int) -> tuple[list, list, list, list]:
        dates = list(self._forecast_showings[index].keys())
        showings = []
        min_sh = []
        max_sh = []
        for date in dates:
            showings.append(self._forecast_showings[index].get(date))
            min_sh.append(self._banners[index].min_showings)
            max_sh.append(self._banners[index].max_showings)
        return dates, showings, min_sh, max_sh

    # region Redefining the methods for filling the table
    def headerData(self, section, orientation, role=...):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headers[section]
        return None

    def rowCount(self, parent=None):
        return len(self._banners)

    def columnCount(self, parent=None):
        return len(self._headers)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            row = index.row()
            column = index.column()
            if column == 0:
                return self._banners[row].name
            if column == 1:
                return self._banners[row].company_name
            if column == 2:
                return self._banners[row].date_end
        return None
    # endregion
