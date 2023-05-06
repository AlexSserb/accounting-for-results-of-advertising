import sqlite3
from os.path import dirname, join
from random import randint

from src.models.banner import *
from src.models.showing import *


class AdvertisDriver:
    def __init__(self):
        self.__db_file_name = join(dirname(__file__), '../resources/advertisement.db')
        self._con = sqlite3.connect(self.__db_file_name)
        self.create_banners_table()
        self.create_showings_table()

    def recreate_tables(self):
        self.drop_banners_table()
        self.drop_showings_table()
        self.create_banners_table()
        self.create_showings_table()

    # region Banner table
    def create_banners_table(self):
        cur = self._con.cursor()
        cur.execute(""" CREATE TABLE IF NOT EXISTS "banners"(
                    "id" INTEGER NOT NULL UNIQUE,
                    "name" TEXT NOT NULL,
                    "company_name" TEXT NOT NULL,
                    "date_start" TEXT NOT NULL,
                    "date_end" TEXT NOT NULL,
                    "min_showings" INTEGER NOT NULL,
                    "max_showings" INTEGER NOT NULL,
                    PRIMARY KEY("id" AUTOINCREMENT) );
                    """)
        self._con.commit()
        cur.close()

    def drop_banners_table(self):
        cur = self._con.cursor()
        cur.execute("DROP TABLE banners")
        self._con.commit()
        cur.close()

    def get_all_banners(self) -> list[Banner]:
        b_list = self._get_all_banners_as_list()
        banners = []
        for b_el in b_list:
            showings = self.get_showings_for_banner(b_el[0])
            banners.append(Banner(id=b_el[0], name=b_el[1], company_name=b_el[2],
                                  date_start=QDate.fromString(b_el[3], DATE_FORMAT),
                                  date_end=QDate.fromString(b_el[4], DATE_FORMAT),
                                  min_showings=b_el[5], max_showings=b_el[6], showings=showings))
        return banners

    def _get_all_banners_as_list(self) -> list:
        cur = self._con.cursor()
        cur.execute("SELECT * FROM banners")
        banners = cur.fetchall()
        cur.close()
        return banners

    def update_banner(self, banner: Banner):
        cur = self._con.cursor()
        cur.execute("""UPDATE banners SET name = ?, company_name = ?, date_start = ?, date_end = ?, 
                    min_showings = ?, max_showings = ? WHERE id = ?;""",
                    (banner.name,
                     banner.company_name,
                     banner.date_start_str(),
                     banner.date_end_str(),
                     banner.min_showings,
                     banner.max_showings,
                     banner.id))
        self._con.commit()
        cur.close()

    def delete_banner(self, uid: int):
        cur = self._con.cursor()
        cur.execute(f"DELETE FROM banners WHERE id = {uid}")
        cur.execute(f"DELETE FROM showings WHERE banner_id = {uid}")
        self._con.commit()
        cur.close()

    def insert_banner(self, banner: BannerShortData):
        cur = self._con.cursor()
        cur.execute("""INSERT INTO banners (name, company_name, date_start, date_end, min_showings, max_showings)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (banner.name, banner.company_name, banner.date_start_str(),
                     banner.date_end_str(), banner.min_showings, banner.max_showings))
        self._con.commit()
        last_row_id = cur.lastrowid
        cur.close()
        return last_row_id

    def insert_banners(self, banners: list[BannerShortData]):
        cur = self._con.cursor()
        for banner in banners:
            cur.execute("""INSERT INTO banners (name, company_name, date_start, date_end, min_showings, max_showings)
                        VALUES (?, ?, ?, ?, ?, ?)""",
                        (banner.name, banner.company_name, banner.date_start_str(),
                         banner.date_end_str(), banner.min_showings, banner.max_showings))
        self._con.commit()
        cur.close()

    # endregion

    # region Table of records about banner shows
    def create_showings_table(self):
        cur = self._con.cursor()
        cur.execute(""" CREATE TABLE IF NOT EXISTS "showings"(
                    "id" INTEGER NOT NULL UNIQUE,
                    "site_name" TEXT NOT NULL,
                    "datetime" TEXT NOT NULL,
                    "banner_id" INTEGER NOT NULL,
                    PRIMARY KEY("id" AUTOINCREMENT) );
                    """)
        self._con.commit()
        cur.close()

    def drop_showings_table(self):
        cur = self._con.cursor()
        cur.execute("DROP TABLE showings")
        self._con.commit()
        cur.close()

    def get_showings_for_banner(self, banner_id: int):
        cur = self._con.cursor()
        cur.execute(f"SELECT * FROM showings WHERE banner_id = {banner_id}")
        sh_list = cur.fetchall()
        cur.close()
        showings = []
        for sh_el in sh_list:
            showings.append(Showing(id=sh_el[0], site_name=sh_el[1],
                                    datetime=QDateTime().fromString(sh_el[2], DATETIME_FORMAT),
                                    banner_id=sh_el[3]))
        return showings

    def update_showing(self, showing: Showing):
        cur = self._con.cursor()
        cur.execute("""UPDATE showings SET site_name = ?, datetime = ? WHERE id = ?;""",
                    (showing.site_name, showing.datetime_str(), showing.id))
        self._con.commit()
        cur.close()

    def delete_showing(self, uid: int):
        cur = self._con.cursor()
        cur.execute(f"DELETE FROM showings WHERE id = {uid}")
        self._con.commit()
        cur.close()

    def insert_showing(self, showing: ShowingShortData, banner_id: int):
        cur = self._con.cursor()
        cur.execute("""INSERT INTO showings (site_name, datetime, banner_id) VALUES (?, ?, ?)""",
                    (showing.site_name, showing.datetime.toString(DATETIME_FORMAT), banner_id))
        self._con.commit()
        last_row_id = cur.lastrowid
        cur.close()
        return last_row_id

    def insert_showings(self, showings: list[ShowingShortData], banner_id: int):
        cur = self._con.cursor()
        for showing in showings:
            cur.execute("""INSERT INTO showings (site_name, datetime, banner_id) VALUES (?, ?, ?)""",
                        (showing.site_name, showing.datetime.toString(DATETIME_FORMAT), banner_id))
        self._con.commit()
        cur.close()

    # endregion

    # region Random data generation
    def generate_random_data(self):
        self.recreate_tables()
        banners = self._banners_for_rand_gen()
        self.insert_banners(banners)
        self._gen_rand_showings(banners)

    def _banners_for_rand_gen(self) -> list[BannerShortData]:
        currd = QDate().currentDate()
        return [BannerShortData('Banner 1', 'Company 1', currd.addDays(-15), currd.addDays(12), 5, 30),
                BannerShortData('Banner 2', 'Company 2', currd.addDays(-18), currd.addDays(14), 10, 25),
                BannerShortData('Banner 3', 'Company 3', currd.addDays(-8), currd.addDays(5), 10, 30),
                BannerShortData('Banner 4', 'Company 4', currd.addDays(-13), currd.addDays(3), 5, 25),
                BannerShortData('Banner 5', 'Company 5', currd.addDays(-7), currd.addDays(7), 15, 30),
                BannerShortData('Banner 6', 'Company 6', currd.addDays(1), currd.addDays(15), 10, 20)]

    # Generation random shows for list of banners
    def _gen_rand_showings(self, banners: list[BannerShortData]):
        for banner_id in range(1, 7):
            self._gen_rand_showings_for_banner(banners[banner_id - 1], banner_id)

    # Generation random shows for one banner
    def _gen_rand_showings_for_banner(self, banner: BannerShortData, banner_id):
        cur = self._con.cursor()
        sites = ['Cucumber.com', 'WeeeWeee.com', 'Ooooo.com', 'qwerty.com',
                 'Kva.com', 'la.com', 'Ggg.com', 'Jojo.com', 'Robot.com']
        date = banner.date_start
        last_date = QDate().currentDate()
        while date.daysTo(last_date) > 0:
            datetime = QDateTime(date)
            shows_amount = randint(1, banner.max_showings)
            for _ in range(shows_amount):
                cur.execute("""INSERT INTO showings (site_name, datetime, banner_id) VALUES (?, ?, ?)""",
                            (sites[randint(0, 8)], datetime.addSecs(randint(0, 15000)).toString(DATETIME_FORMAT),
                             banner_id))
            date = date.addDays(1)
        cur.close()

    # endregion
