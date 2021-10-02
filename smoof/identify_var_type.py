import re

from pandas import Series


class VarTypeIdentifier:

    def __init__(self, var_series: Series) -> None:

        self.__var_series = var_series

    def identify_type(self) -> None:

        if self.__is_date():
            self.__type = 'date'
        elif self.__is_category():
            self.__type = self.__get_category_type()
        elif self.__is_numeric():
            self.__type = 'numeric'
        else:
            return ValueError('unidentifiable type')

    def __is_date(self) -> None:
        
        if self.__var_series.dtype != 'object':
            return False

        pattern = re.compile('[0-9]{2,4}[/-][0-9]{2,4}[/-][0-9]{2,4}')

        return pattern.match(self.__var_series.iloc[0])

    def __is_numeric(self) -> None:

        var_dtype_str = str(self.__var_series.dtype)

        pattern_int = re.compile('int[0-9]{1,2}')
        pattern_float = re.compile('float[0-9]{1,2}')

        return pattern_float.match(var_dtype_str) or pattern_int.match(var_dtype_str)

    def __is_category(self) -> None:

        return (self.__var_series.dtype == 'object') or (self.__var_series.nunique() <= 15)

    def __get_category_type(self) -> str:

        nunique_label = self.__var_series.nunique()

        return 'category_long' if nunique_label > 15 else 'category_short'

    def get_type(self) -> None:
        
        return self.__type



