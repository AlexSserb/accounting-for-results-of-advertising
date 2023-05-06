from datetime import datetime
from PyQt5 import QtGui
from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import QApplication, QTableView
from PyQt5 import uic
import sys
import pyqtgraph as pg

sys.path.insert(0, '..')

from src.models.forecaster import Forecaster
from src.models.promotion_analyzer import PromotionAnalyser
from src.views.message_box import *
from src.models.banner_editor import *


class FormMode(Enum):
    default = 0
    adding = 1
    editing = 2
    block_all = 3


class MainWnd:
    def __init__(self):
        form, window = uic.loadUiType(join(dirname(__file__), 'ui_main_window.ui'))
        self._app = QApplication(sys.argv)
        self._window = window()
        self._form = form()
        self._banner_editor = BannerEditor()
        self._pr_analyser = PromotionAnalyser()
        self._forecaster = Forecaster()
        self._banner_form_mode = FormMode.default
        self._impression_form_mode = FormMode.block_all
        self._window.setWindowIcon(QtGui.QIcon(join(dirname(__file__), '../images/icon_ad.png')))

    # region Setting up tables
    def _set_tableviews(self):
        self._set_tableview_banners()
        self._set_tableview_showings()
        self._set_tableview_pr_analyse()
        self._set_tableview_forecast()

    def _set_tableview_banners(self):
        self._form.tableview_banners.setModel(self._banner_editor)
        self._form.tableview_banners.setSelectionBehavior(QTableView.SelectRows)
        self._form.tableview_banners.setColumnWidth(0, 190)
        self._form.tableview_banners.setColumnWidth(1, 290)
        self._form.tableview_banners.setColumnWidth(2, 290)

    def _set_tableview_showings(self):
        self._form.tableview_showings.setModel(self._banner_editor.showing_editor)
        self._form.tableview_showings.setSelectionBehavior(QTableView.SelectRows)
        self._form.tableview_showings.setColumnWidth(0, 220)
        self._form.tableview_showings.setColumnWidth(1, 210)

    def _set_tableview_pr_analyse(self):
        self._form.tableview_pr_banners.setModel(self._pr_analyser)
        self._form.tableview_pr_banners.setSelectionBehavior(QTableView.SelectRows)
        self._form.tableview_pr_banners.setColumnWidth(0, 155)
        self._form.tableview_pr_banners.setColumnWidth(1, 155)
        self._form.tableview_pr_banners.setColumnWidth(2, 155)

    def _set_tableview_forecast(self):
        self._form.tableview_forecast.setModel(self._forecaster)
        self._form.tableview_forecast.setSelectionBehavior(QTableView.SelectRows)
        self._form.tableview_forecast.setColumnWidth(0, 170)
        self._form.tableview_forecast.setColumnWidth(1, 220)
        self._form.tableview_forecast.setColumnWidth(2, 270)

    # endregion

    # region Setting up the events of the main window
    def _set_events(self):
        self._set_events_menu_buttons()
        self._set_events_tables()
        self._set_events_banner_buttons()
        self._set_events_impression_buttons()
        self._form.combobox_sort_by.currentIndexChanged.connect(self._sort_by_changed)
        self._set_events_pr_analyser()

    def _set_events_tables(self):
        self._last_selected_banner = -1
        self._form.tableview_banners.clicked.connect(self._table_banners_clicked)
        self._last_selected_showing = -1
        self._form.tableview_showings.clicked.connect(self._table_showings_clicked)
        self._last_selected_pr_ban = -1
        self._form.tableview_pr_banners.clicked.connect(self._pr_table_clicked)
        self._last_selected_fc_ban = -1
        self._form.tableview_forecast.clicked.connect(self._fc_table_clicked)

    def _set_events_banner_buttons(self):
        self._form.button_save_changes_banner.clicked.connect(self._save_banner_changes)
        self._form.button_delete_banner.clicked.connect(self._delete_banner)
        self._form.button_new_banner.clicked.connect(self._change_form_for_new_banner)
        self._form.button_randdata.clicked.connect(self._generate_random_data)

    def _set_events_menu_buttons(self):
        self._form.button_banners_view.clicked.connect(self._switching_to_banners_overview)
        self._form.button_showings_view.clicked.connect(self._switching_to_shows_overview)
        self._form.button_banner_analysis.clicked.connect(self._switching_to_promotion_results)
        self._form.button_forecast_view.clicked.connect(self._switching_to_forecasting)

    def _set_events_pr_analyser(self):
        self._form.calendar_widget.clicked.connect(self._calendar_clicked)

    # Switching to the banner overview tab
    def _switching_to_banners_overview(self):
        self._form.stackedWidget.setCurrentWidget(self._form.banners_overview)
        self._form.stackedWidget_2.setCurrentWidget(self._form.banners_editor)

    # Switching to the tab of viewing the records of banner shows
    def _switching_to_shows_overview(self):
        self._form.stackedWidget.setCurrentWidget(self._form.banners_overview)
        self._form.stackedWidget_2.setCurrentWidget(self._form.showings_editor)

    # Switching to the tab for analyzing the results of advertising services promotion
    def _switching_to_promotion_results(self):
        self._form.stackedWidget.setCurrentWidget(self._form.banners_analisys)
        self._pr_analyser.set_banners(self._banner_editor.get_banners())
        min = QDate(self._pr_analyser.get_min_date())
        max = QDate().currentDate().addDays(-1)
        self._form.calendar_widget.setDateRange(min, max)
        while min.daysTo(max) >= 0:
            self._form.calendar_widget.setDateTextFormat(min, self._blocked_format)
            min = min.addDays(1)
        self._fill_alltime_data()

    # Initializing the format for active calendar dates
    def _set_enabled_dates_format(self):
        font = self._form.calendar_widget.font()
        self._blocked_format = self._form.calendar_widget.dateTextFormat(QDate())
        font.setBold(True)
        self._blocked_format.setFont(font)

    # Switching to the tab for forecasting
    def _switching_to_forecasting(self):
        self._form.stackedWidget.setCurrentWidget(self._form.banners_forecasting)
        self._forecaster.set_banners(self._banner_editor.get_banners())

    # Setting events for the form for banner show records
    def _set_events_impression_buttons(self):
        self._form.button_save_changes_showing.clicked.connect(self._save_show_changes)
        self._form.button_delete_showing.clicked.connect(self._delete_show)
        self._form.button_new_showing.clicked.connect(self._change_form_for_new_show)

    # endregion

    # region Events for banner editing
    # Selecting a row in the banner table
    def _table_banners_clicked(self, clicked_index: QModelIndex):
        self._banner_form_mode = FormMode.editing
        self._set_banner_form_widgets()

        self._last_selected_banner = clicked_index.row()
        self._impression_form_mode = FormMode.default
        self._set_showing_form_widgets()

        banner = self._banner_editor.get_banner_short_data(self._last_selected_banner)
        self._fill_banner_form(banner)
        self._fill_showing_form()

    def _save_banner_changes(self):
        try:
            if self._banner_form_mode == FormMode.editing:
                self._banner_editor.save_changes_for_banner(self._banner_from_form(), self._last_selected_banner)
            elif self._banner_form_mode == FormMode.adding:
                self._banner_editor.add_banner(self._banner_from_form())

            self._banner_form_mode = FormMode.default
            self._set_banner_form_widgets()
            self._impression_form_mode = FormMode.block_all
            self._set_showing_form_widgets()

            self._fill_banner_form()
            self._fill_showing_form()
            self._banner_editor.clear_showing_editor_data()

            self._banner_editor.sort_banners()
        except Exception as ex:
            show_error_messagebox("Error of banner saving.", ex.args[0])

    def _delete_banner(self):
        self._banner_form_mode = FormMode.default
        self._banner_editor.delete_banner(self._last_selected_banner)
        self._fill_banner_form()
        self._set_banner_form_widgets()
        self._banner_editor.clear_showing_editor_data()

    # Changing the form for getting data about new banner
    def _change_form_for_new_banner(self):
        self._fill_banner_form()
        self._banner_form_mode = FormMode.adding
        self._set_banner_form_widgets()
        self._impression_form_mode = FormMode.block_all
        self._set_showing_form_widgets()
        self._banner_editor.clear_showing_editor_data()

    # Selecting the method of ordering elements
    def _sort_by_changed(self, index):
        self._banner_editor.sort_banners(SortedMode(index))
        self._banner_editor.clear_showing_editor_data()
        self._banner_form_mode = FormMode.default
        self._set_banner_form_widgets()
        self._fill_banner_form()
        self._impression_form_mode = FormMode.block_all
        self._set_showing_form_widgets()
        self._fill_showing_form()

    # endregion

    # region Events for editing banner show records
    # Selecting the row of the show records table
    def _table_showings_clicked(self, clicked_index: QModelIndex):
        self._impression_form_mode = FormMode.editing
        self._set_showing_form_widgets()
        self._last_selected_showing = clicked_index.row()

        showing = self._banner_editor.get_showing_short_data(self._last_selected_showing)
        self._fill_showing_form(showing)

    # Saving changes of the show
    def _save_show_changes(self):
        try:
            if self._impression_form_mode == FormMode.editing:
                self._banner_editor.save_changes_for_showing(self._showing_from_form(),
                                                             self._last_selected_banner,
                                                             self._last_selected_showing)
            elif self._impression_form_mode == FormMode.adding:
                self._banner_editor.add_showing(self._showing_from_form(),
                                                self._last_selected_banner)

            self._impression_form_mode = FormMode.default
            self._set_showing_form_widgets()
            self._fill_showing_form()
            self._banner_editor.showing_editor.layoutChanged.emit()
        except Exception as ex:
            show_error_messagebox("Error of saving banner show record.", ex.args[0])

    def _delete_show(self):
        self._impression_form_mode = FormMode.default
        self._banner_editor.delete_showing(self._last_selected_banner, self._last_selected_showing)
        self._fill_showing_form()
        self._set_showing_form_widgets()
        self._banner_editor.showing_editor.layoutChanged.emit()

    # Changing the form for getting data about new show
    def _change_form_for_new_show(self):
        self._fill_showing_form()
        self._impression_form_mode = FormMode.adding
        self._set_showing_form_widgets()
        self._banner_editor.showing_editor.layoutChanged.emit()

    # Random data generation
    def _generate_random_data(self):
        try:
            self._impression_form_mode = FormMode.block_all
            self._set_showing_form_widgets()
            self._banner_form_mode = FormMode.default
            self._set_banner_form_default()
            self._banner_editor.gen_rand_data()
            show_success_messagebox("Data generated successfully.")
        except Exception as ex:
            show_error_messagebox("Data generation error.", ex.args[0])

    # endregion

    # region Tab events to analyze the results of advertising promotion
    def _calendar_clicked(self):
        self._pr_analyser.set_banners_to_display(self._form.calendar_widget.selectedDate())

    def _pr_table_clicked(self, clicked_index: QModelIndex):
        if self._last_selected_pr_ban != clicked_index.row:
            self._fill_ban_form_for_date(clicked_index.row())
            self._last_selected_pr_ban = clicked_index.row

    # endregion

    # region Events for the banner show forecast tab
    def _fc_table_clicked(self, clicked_index: QModelIndex):
        if self._last_selected_fc_ban != clicked_index.row:
            self._form.graphicview.clear()
            dates, showings, min_sh, max_sh = self._forecaster.get_forecast_for_banner(clicked_index.row())
            timestamps = []
            for date in dates:
                timestamps.append(datetime(date.year(), date.month(), date.day()).timestamp())
            self._form.graphicview.plot(timestamps, min_sh, symbol='o', pen=pg.mkPen('r', width=4),
                                        name='Minimal number of shows per day')
            self._form.graphicview.plot(timestamps, max_sh, symbol='o', pen=pg.mkPen('g', width=4),
                                        name='Maximum number of shows per day')
            self._form.graphicview.plot(timestamps, showings, symbol='o', pen=pg.mkPen('b', width=4),
                                        name='Forecasted number of shows')

    # endregion

    # region Interaction with banner form
    # Getting banner short data from form
    def _banner_from_form(self) -> BannerShortData:
        banner = BannerShortData(
            self._form.bname_input.text(),
            self._form.bcomp_name_input.text(),
            self._form.date_start_edit.date(),
            self._form.date_end_edit.date(),
            self._form.spin_box_min_showings.value(),
            self._form.spin_box_max_showings.value())
        return banner

    # Settings of banner form
    def _set_banner_form_widgets(self):
        if self._banner_form_mode == FormMode.adding:
            self._set_banner_form_adding()
        elif self._banner_form_mode == FormMode.editing:
            self._set_banner_form_editing()
        else:
            self._set_banner_form_default()

    def _set_banner_form_adding(self):
        self._form.label_baner_form_title.setText('New banner information')
        self._form.button_save_changes_banner.setEnabled(True)
        self._form.button_delete_banner.setEnabled(False)
        self._form.button_new_banner.setEnabled(False)
        self._set_enabled_banner_form(True)

    def _set_banner_form_editing(self):
        self._form.label_baner_form_title.setText('Banner information')
        self._form.button_save_changes_banner.setEnabled(True)
        self._form.button_delete_banner.setEnabled(True)
        self._form.button_new_banner.setEnabled(True)
        self._set_enabled_banner_form(True)

    def _set_banner_form_default(self):
        self._form.label_baner_form_title.setText('Banner information')
        self._form.button_save_changes_banner.setEnabled(False)
        self._form.button_delete_banner.setEnabled(False)
        self._form.button_new_banner.setEnabled(True)
        self._set_enabled_banner_form(False)

    # Loading banner data into the form
    def _fill_banner_form(self, banner=BannerShortData('', '', QDate(), QDate(), 0, 0)):
        self._form.bname_input.setText(banner.name)
        self._form.bcomp_name_input.setText(banner.company_name)
        self._form.date_start_edit.setDate(banner.date_start)
        self._form.date_end_edit.setDate(banner.date_end)
        self._form.spin_box_min_showings.setValue(banner.min_showings)
        self._form.spin_box_max_showings.setValue(banner.max_showings)

    # Blocking and unblocking the form elements for banners
    def _set_enabled_banner_form(self, is_enabled: bool):
        self._form.bname_input.setEnabled(is_enabled)
        self._form.bcomp_name_input.setEnabled(is_enabled)
        self._form.date_start_edit.setEnabled(is_enabled)
        self._form.date_end_edit.setEnabled(is_enabled)
        self._form.spin_box_min_showings.setEnabled(is_enabled)
        self._form.spin_box_max_showings.setEnabled(is_enabled)

    # endregion

    # region Interaction with the form to record a banner show
    # Getting the record of banner's show from form
    def _showing_from_form(self) -> ShowingShortData:
        showing = ShowingShortData(
            self._form.site_name_input.text(),
            self._form.datetime_edit.dateTime())
        return showing

    # Setting form for record show of a banner
    def _set_showing_form_widgets(self):
        if self._impression_form_mode == FormMode.adding:
            self._set_sh_form_adding()
        elif self._impression_form_mode == FormMode.editing:
            self._set_sh_form_editing()
        elif self._impression_form_mode == FormMode.block_all:
            self._set_sh_form_block_all()
        else:
            self._set_sh_form_default()

    def _set_sh_form_adding(self):
        self._form.label_showing_form_title.setText('Information about the new banner show')
        self._form.button_save_changes_showing.setEnabled(True)
        self._form.button_delete_showing.setEnabled(False)
        self._form.button_new_showing.setEnabled(False)
        self._set_enabled_showing_form(True)

    def _set_sh_form_editing(self):
        self._form.label_showing_form_title.setText('Information about the banner show')
        self._form.button_save_changes_showing.setEnabled(True)
        self._form.button_delete_showing.setEnabled(True)
        self._form.button_new_showing.setEnabled(True)
        self._set_enabled_showing_form(True)

    def _set_sh_form_block_all(self):
        self._form.label_showing_form_title.setText('Information about the banner show')
        self._form.button_save_changes_showing.setEnabled(False)
        self._form.button_delete_showing.setEnabled(False)
        self._form.button_new_showing.setEnabled(False)
        self._set_enabled_showing_form(False)

    def _set_sh_form_default(self):
        self._form.label_showing_form_title.setText('Information about the banner show')
        self._form.button_save_changes_showing.setEnabled(False)
        self._form.button_delete_showing.setEnabled(False)
        self._form.button_new_showing.setEnabled(True)
        self._set_enabled_showing_form(False)

    # Loading show data into the form
    def _fill_showing_form(self, showing=ShowingShortData()):
        self._form.site_name_input.setText(showing.site_name)
        self._form.datetime_edit.setDateTime(showing.datetime)

    # Blocking and unblocking the form elements for showings
    def _set_enabled_showing_form(self, is_enabled: bool):
        self._form.site_name_input.setEnabled(is_enabled)
        self._form.datetime_edit.setEnabled(is_enabled)

    # endregion

    # region Interaction with forms to analyze the results of advertising promotion
    def _fill_ban_form_for_date(self, banner_index: int):
        banner_pr_data = self._pr_analyser.get_banner_info(banner_index, self._form.calendar_widget.selectedDate())
        self._form.line_bname.setText(banner_pr_data.name)
        self._form.line_bcomp_name.setText(banner_pr_data.company_name)
        self._form.label_min_sh_now.setText(f'Min number of shows: {banner_pr_data.min_sh_today}')
        self._form.label_max_sh_now.setText(f'Max number of shows: {banner_pr_data.max_sh_today}')
        self._form.label_fact_sh_now.setText(f'Actual number of shows: {banner_pr_data.fact_sh_today}')
        self._form.label_pct_now.setText(f'The minimum is completed by: {banner_pr_data.min_comp_percent_today() :.3f}%')

        self._form.label_min_sh.setText(f'Min number of shows: {banner_pr_data.min_sh_all}')
        self._form.label_max_sh.setText(f'Max number of shows: {banner_pr_data.max_sh_all}')
        self._form.label_fact_sh.setText(f'Actual number of shows: {banner_pr_data.fact_sh_all}')
        self._form.label_pct.setText(f'The minimum is completed by: {banner_pr_data.min_comp_percent_all() :.3f}%')
        self._form.label_date_start.setText(f'Start of banner validity: {banner_pr_data.date_start_str()}')
        self._form.label_date_end.setText(f'End of banner validity: {banner_pr_data.date_end_str()}')

    def _fill_alltime_data(self):
        alltime_data = self._pr_analyser.get_alltime_data()
        if alltime_data is None or len(alltime_data) != 3:
            return
        self._form.label_all_fact_sh.setText(f'Total actual shows: {alltime_data[0]}')
        self._form.label_all_min_sh.setText(f'Total min number of shows: {alltime_data[1]}')
        self._form.label_all_max_sh.setText(f'Total max number of shows: {alltime_data[2]}')
        percent = alltime_data[0] / alltime_data[1] * 100
        if percent > 100:
            percent = 100
        self._form.label_pct_all.setText(f'The minimum is completed by:  {percent :.3f}%')

    # endregion

    # Setting graph for the forecast output
    def _set_graphic(self):
        self._form.graphicview.addLegend()
        self._form.graphicview.setAxisItems(axisItems={'bottom': pg.DateAxisItem()})
        self._form.graphicview.setLabel(axis='bottom', text='Date')
        self._form.graphicview.setLabel(axis='left', text='Number of shows')
        self._form.graphicview.setBackground('w')

    def run(self):
        self._form.setupUi(self._window)

        self._set_banner_form_widgets()
        self._set_showing_form_widgets()
        self._set_graphic()
        self._set_events()
        self._set_tableviews()
        self._set_enabled_dates_format()

        self._window.show()
        self._app.exec_()
