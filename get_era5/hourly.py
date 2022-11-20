"""Get ERA5 by CDS API calls."""
import os
from typing import List, Union
from datetime import datetime, date, timedelta
import numpy as np
import xarray as xr
import cdsapi
from sithom.xr import mon_increase, plot_units

DATEFORMAT: str = "%Y-%m-%d"
DATA_PATH: str = ""


def str_to_date(strdate: Union[str, any], dateformat: str = DATEFORMAT) -> any:
    """
    String to date.

    Args:
        strdate (Union[str, any]): The string date encoded by the dateformat.
        dateformat (str, optional): The format of the date. Defaults to DATEFORMAT.

    Returns:
        any: Datetime object.

    Example:
        >>> from src.data_loading.ecmwf import str_to_date
        >>> date = str_to_date("2005-08-25")
        >>> date.year
        2005
        >>> date.month
        8
        >>> date.day
        25
    """
    if isinstance(strdate, str):
        strdate = datetime.strptime(strdate, dateformat)
    return strdate


def two_char_int(int_input: int) -> str:
    """
    Two char int.

    Args:
        int_input (int): input integer.

    Returns:
        str: Two char int.
    """
    ret_str = str(int_input)
    if len(ret_str) == 1:
        ret_str = "0" + ret_str
    return ret_str


HOURS = [two_char_int(x) + ":00" for x in range(0, 24)]
MONTHS = [two_char_int(x) for x in range(1, 13)]


def date_to_str(date: any) -> str:
    month_str = two_char_int(date.month)
    day_str = two_char_int(date.day)
    return str(date.year) + "-" + month_str + "-" + day_str


def end_of_year(year: int) -> str:
    return str(year) + "-" + str(12) + "-" + str(31)


def start_of_year(year: int) -> str:
    return str(year) + "-" + "01" + "-" + "01"


def end_of_month(date_inp: any) -> str:
    if date_inp.month != 12:
        return date_to_str(
            date(int(date_inp.year), int(date_inp.month + 1), 1) - timedelta(days=1)
        )
    else:
        return end_of_year(date_inp.year)


def start_of_month(date_inp: any) -> str:
    month_str = two_char_int(date_inp.month)
    return str(date_inp.year) + "-" + month_str + "-" + "01"


def year_month_day_lists(
    startdate: Union[np.datetime64, str], enddate: Union[np.datetime64, str]
) -> List[Union[str, List[str]]]:
    """
    Month Day lists for running cds api.

    !Inclusive counting!

    If str formatted as '%Y-%m-%d'

    Args:
        startdate (np.datetime64): Start date.
        enddate (np.datetime64): End date.

    Returns:
        List[List[str]]: [[Year, Month, [Day1, Day2, ...]], [[Month2], ...]]

    Examples of use::
        >>> from src.data_loading.ecmwf import year_month_day_lists
        >>> year_month_day_lists("2005-08-20", "2005-08-31")
            [['2005', '08', ['20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']]]
        >>> year_month_day_lists("2021-08-29", "2021-09-05")
            [['2021', '08', ['29', '30', '31']], ['2021', '09', ['01', '02', '03', '04', '05']]]
        >>> year_month_day_lists("2021-12-29", "2022-01-03")
            [['2021', '12', ['29', '30', '31']], ['2022', '01', ['01', '02', '03']]]
        >>> year_month_day_lists("2004-02-28", "2004-03-03")
            [['2004', '02', ['28', '29']], ['2004', '03', ['01', '02', '03']]]
        >>> year_month_day_lists("2005-02-28", "2005-03-02")
            [['2005', '02', ['28']], ['2005', '03', ['01', '02']]]
        >>> year_month_day_lists("2000-02-27", "2000-03-02")
            [['2000', '02', ['27', '28', '29']], ['2000', '03', ['01', '02']]]
        >>> year_month_day_lists("1700-02-27", "1700-03-02")
            [['1700', '02', ['27', '28']], ['1700', '03', ['01', '02']]]
    """
    startdate = str_to_date(startdate)
    enddate = str_to_date(enddate)

    assert startdate <= enddate  # end either the same day, or a later day.

    if startdate.year < enddate.year:
        start_part = year_month_day_lists(startdate, end_of_year(startdate.year))
        end_part = year_month_day_lists(start_of_year(enddate.year), enddate)
        if startdate.year < enddate.year - 1:
            intermediate_piece = []
            for year in range(startdate.year + 1, enddate.year):
                intermediate_piece += year_month_day_lists(
                    start_of_year(year), end_of_year(year)
                )
            final_list = start_part + intermediate_piece + end_part
        else:
            final_list = start_part + end_part
    elif startdate.month < enddate.month:
        start_part = year_month_day_lists(startdate, end_of_month(startdate))
        end_part = year_month_day_lists(start_of_month(enddate), enddate)
        if startdate.month < enddate.month - 1:
            intermediate_piece = []
            for month in range(startdate.month + 1, enddate.month):
                temp_date = date(startdate.year, month, 1)
                intermediate_piece += year_month_day_lists(
                    start_of_month(temp_date), end_of_month(temp_date)
                )
            final_list = start_part + intermediate_piece + end_part
        else:
            final_list = start_part + end_part
    else:
        final_list = [
            [
                str(startdate.year),
                two_char_int(startdate.month),
                [two_char_int(x) for x in range(startdate.day, enddate.day + 1)],
            ]
        ]

    return final_list


def katrina_netcdf(vars, file_name,bbox) -> None:
    """
    ERA5 longer entry.
    """
    date_list = year_month_day_lists("2005-08-20", "2005-09-05")
    client = cdsapi.Client()
    file_name_list = [
        os.path.join(DATA_PATH, "katrina-" + str(i) + ".nc")
        for i in range(len(date_list))
    ]
    for i in range(len(date_list)):
        client.retrieve(
            "reanalysis-era5-single-levels",
            {
                "product_type": "reanalysis",
                "format": "netcdf",
                "variable": vars,
                "year": date_list[i][0],
                "month": date_list[i][1],
                "day": date_list[i][2],
                "time": HOURS,
                "area": bbox.ecmwf(),
            },
            file_name_list[i],
        )
    xr.open_mfdataset(file_name_list).to_netcdf(file_name)



if __name__ == "__main__":
    # python src/data_loading/ecmwf.py
    # print(year_month_day_lists("2003-08-11", "2006-01-02"))
    # katrina_netcdf(vars=ECMWF_AIR_VAR, file_name=KATRINA_ERA5_NC)
    # katrina_netcdf(vars=ECMWF_WATER_VAR, file_name=KATRINA_WATER_ERA5_NC)
    # monthly_avgs()
    print("ok")
