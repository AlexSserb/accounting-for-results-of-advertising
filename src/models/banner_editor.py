from enum import Enum

from src.drivers.advertis_driver import *
from src.models.showing_editor import *


class SortedMode(Enum):
    by_date_start = 0
    by_date_end = 1


class BannerEditor(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._advertising_driver = AdvertisDriver()
        self._banners = []
        self._headers = ["Name", "Start date of banner action", "End date of banner action"]
        self.showing_editor = ShowingEditor()
        self._sorted_mode = SortedMode.by_date_end
        self._init_all_banners_from_db()

    def get_banners(self):
        return self._banners

    def _init_all_banners_from_db(self):
        self._banners = self._advertising_driver.get_all_banners()
        self.sort_banners()

    def sort_banners(self, sort_mode: SortedMode = SortedMode.by_date_start):
        self.beginResetModel()
        if self._sorted_mode == sort_mode:
            return
        self._sorted_mode = sort_mode
        if self._sorted_mode == SortedMode.by_date_start:
            self._banners = sorted(self._banners, key=lambda x: x.date_start)
        elif self._sorted_mode == SortedMode.by_date_end:
            self._banners = sorted(self._banners, key=lambda x: x.date_end)
        self.endResetModel()

    def _resort_banners(self):
        self.beginResetModel()
        if self._sorted_mode == SortedMode.by_date_start:
            self._banners = sorted(self._banners, key=lambda x: x.date_start)
        elif self._sorted_mode == SortedMode.by_date_end:
            self._banners = sorted(self._banners, key=lambda x: x.date_end)
        self.endResetModel()

    def find_min_max_banner_dates(self):
        min_date = QDate.currentDate().addYears(100)
        max_date = QDate.currentDate().addYears(-100)
        for banner in self._banners:
            if min_date.daysTo(banner.date_start) < 0:
                min_date = banner.date_start
            if max_date.daysTo(banner.date_end) > 0:
                max_date = banner.date_end
        if QDate.currentDate().daysTo(max_date) > 0:
            max_date = QDate.currentDate()
        return min_date, max_date

    def find_min_banner_date(self):
        min_date = QDate.currentDate().addYears(100)
        for banner in self._banners:
            if min_date.daysTo(banner.date_start) < 0:
                min_date = banner.date_start
        return min_date

    # region Overriding methods for filling the table
    def headerData(self, section, orientation, role=...):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headers[section]

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
                return self._banners[row].date_start
            if column == 2:
                return self._banners[row].date_end

    # endregion

    def save_changes_for_banner(self, banner_short_data: BannerShortData, index: int):
        self.beginResetModel()
        banner = Banner(self._banners[index].id, banner_short_data.name,
                        banner_short_data.company_name, banner_short_data.date_start,
                        banner_short_data.date_end, banner_short_data.min_showings,
                        banner_short_data.max_showings, self._banners[index].showings)
        self._advertising_driver.update_banner(banner)
        self._banners[index] = banner
        self.endResetModel()

    def delete_banner(self, index: int):
        self.beginResetModel()
        banner = self._banners.pop(index)
        self._advertising_driver.delete_banner(banner.id)
        self.endResetModel()

    def add_banner(self, banner_short_data: BannerShortData):
        self.beginResetModel()
        banner_id = self._advertising_driver.insert_banner(banner_short_data)
        banner = Banner(banner_id, banner_short_data.name,
                        banner_short_data.company_name, banner_short_data.date_start,
                        banner_short_data.date_end, banner_short_data.min_showings,
                        banner_short_data.max_showings, [])
        self._banners.append(banner)
        self.endResetModel()

    # Getting brief information for the banner (for output to the form)
    def get_banner_short_data(self, index: int) -> BannerShortData:
        self.showing_editor.init_showings(self._banners[index].showings)
        return self._banners[index].to_banner_short_data()

    def save_changes_for_showing(self, short_showing: ShowingShortData, ind_banner: int, ind_showing: int):
        self.beginResetModel()
        selected_banner = self._banners[ind_banner]
        self._check_showing_correct(short_showing, selected_banner)
        showing = Showing(selected_banner.showings[ind_showing].id,
                          short_showing.site_name, short_showing.datetime,
                          selected_banner.id)
        self._advertising_driver.update_showing(showing)
        selected_banner.showings[ind_showing] = showing
        self.endResetModel()

    def add_showing(self, short_showing: ShowingShortData, ind_banner: int):
        selected_banner = self._banners[ind_banner]
        self._check_showing_correct(short_showing, selected_banner)
        self.beginResetModel()
        showing_id = self._advertising_driver.insert_showing(short_showing, selected_banner.id)
        showing = Showing(showing_id, short_showing.site_name,
                          short_showing.datetime, selected_banner.id)
        selected_banner.add_showing(showing)
        self.endResetModel()

    def delete_showing(self, ind_banner: int, ind_showing: int):
        self.beginResetModel()
        showing = self._banners[ind_banner].pop_showing(ind_showing)
        self._advertising_driver.delete_showing(showing.id)
        self.endResetModel()

    # Cleaning the table of records about banner impressions
    def clear_showing_editor_data(self):
        self.showing_editor.clear_showings()

    # Getting brief information for the banner show record (for output to the form)
    def get_showing_short_data(self, index: int) -> ShowingShortData:
        return self.showing_editor.get_short_showing(index)

    # The method checks the showing short data correctness
    def _check_showing_correct(self, showing: ShowingShortData, banner: Banner):
        date = showing.datetime.date()
        if banner.count_showings_for_date(date) >= banner.max_showings:
            raise Exception('The max. number of impressions has been reached for the given date.')
        if date.daysTo(banner.date_end) < 0 or banner.date_start.daysTo(date) < 0:
            raise Exception('The show date is not included in the banner validity period.')

    # Generation of random data
    def gen_rand_data(self):
        self._advertising_driver.generate_random_data()
        self._banners = self._advertising_driver.get_all_banners()
        self._resort_banners()
