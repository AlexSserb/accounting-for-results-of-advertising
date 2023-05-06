from src.models.banner_editor import *


# Class for analyzing the results of banner advertising promotion
class PromotionAnalyser(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._all_banners = []
        self._banners_to_show = []
        # _date_banners_dict format - { QDate : [id1, id2, id3, ...] }
        self._date_banners_dict = {}
        self._min_date = QDate()
        self._max_date = QDate()
        self._selected_date = QDate()
        self._headers = ['Name', 'Min shows', 'Actual shows']

    def get_min_date(self) -> QDate:
        return self._min_date

    def get_max_date(self) -> QDate:
        return self._max_date

    def get_banner_info(self, index: int, date: QDate) -> BannerPromotionData:
        banner_pr = BannerPromotionData()
        banner_pr.set_from_banner(self._banners_to_show[index], date)
        return banner_pr

    def get_alltime_data(self) -> (int, int, int):
        all_fact_showings = 0
        all_min_showings = 0
        all_max_showings = 0
        for banner in self._all_banners:
            all_fact_showings += len(banner.showings)
            days = banner.date_start.daysTo(banner.date_end) + 1
            all_min_showings += banner.min_showings * days
            all_max_showings += banner.max_showings * days
        return all_fact_showings, all_min_showings, all_max_showings

    def find_min_max_banner_dates(self):
        min_date = QDate.currentDate().addYears(100)
        max_date = QDate.currentDate().addYears(-100)
        for banner in self._all_banners:
            if min_date.daysTo(banner.date_start) < 0:
                min_date = banner.date_start
            if max_date.daysTo(banner.date_end) > 0:
                max_date = banner.date_end
        if QDate.currentDate().daysTo(max_date) > 0:
            max_date = QDate.currentDate()
        return min_date, max_date

    def set_banners(self, banners: list[Banner]):
        self._all_banners = banners
        self._min_date, self._max_date = self.find_min_max_banner_dates()
        self._set_date_banners_dict()

    # Filling the dictionary, where the key is a date
    # and the value is a list of banners shown on this date
    def _set_date_banners_dict(self):
        date = QDate(self._min_date)
        while date.daysTo(self._max_date) >= 0:
            self._date_banners_dict[date] = []
            date = date.addDays(1)
        for banner in self._all_banners:
            for showing in banner.showings:
                date = QDate(showing.datetime.date())
                if date.daysTo(QDate.currentDate()) >= 0:
                    self._date_banners_dict.get(date).append(banner.id)

    # Filling the list to display the banner table (for a specific date)
    def set_banners_to_display(self, date: QDate):
        self.beginResetModel()
        self._selected_date = date
        ids = self._date_banners_dict.get(date)
        self._banners_to_show.clear()
        if ids is not None:
            for banner in self._all_banners:
                for id in ids:
                    if id == banner.id:
                        self._banners_to_show.append(banner)
                        break
        self.endResetModel()

    # region Overriding methods for filling the table
    def headerData(self, section, orientation, role=...):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headers[section]
        return None

    def rowCount(self, parent=None):
        return len(self._banners_to_show)

    def columnCount(self, parent=None):
        return len(self._headers)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            row = index.row()
            column = index.column()
            if column == 0:
                return self._banners_to_show[row].name
            if column == 1:
                return self._banners_to_show[row].min_showings
            if column == 2:
                return self._banners_to_show[row].count_showings_for_date(self._selected_date)
        return None
    # endregion
