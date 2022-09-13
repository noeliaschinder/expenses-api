from datetime import date
import datetime
from dateutil.relativedelta import relativedelta

class DateUtils():

    @classmethod
    def get_next_month_period(cls, months_to_sum_up = 1):
        today = date.today()
        future_date = today + relativedelta(months=months_to_sum_up)
        next_period_year = future_date.year
        next_period_month = f"0{future_date.month}" if future_date.month < 10 else future_date.month
        return f"{next_period_year}{next_period_month}"

    @classmethod
    def get_current_month_period(cls):
        today = date.today()
        return today.strftime("%Y%m")

    @classmethod
    def get_today_str(cls):
        today = date.today()
        return today.strftime("%Y%m%d")

    # @classmethod
    # def extract_period_from_date(cls, fecha):
    #     periodo_actual = datetime.datetime.strptime(fecha, "%d-%m-%Y").date()
    #     month = periodo_actual.month
    #     if int(month) < 10:
    #         month = f"0{month}"
    #     return f"{month}-{periodo_actual.year}"

    @classmethod
    def periodo_to_db_date_format(cls, periodo):
        datetime_object = datetime.datetime.strptime(periodo, "%m-%Y").date()
        month = datetime_object.month
        if int(month) < 10:
            month = f"0{month}"
        return f"{datetime_object.year}{month}"

    @classmethod
    def fecha_to_db_date_format(cls, fecha):
        datetime_object = datetime.datetime.strptime(fecha, "%d-%m-%Y").date()
        month = datetime_object.month
        if int(month) < 10:
            month = f"0{month}"
        day = datetime_object.day
        if int(day) < 10:
            day = f"0{day}"
        return f"{datetime_object.year}{month}{day}"

    @classmethod
    def periodo_to_date_object(cls, periodo):
        return datetime.datetime.strptime(periodo, "%Y%m").date()


