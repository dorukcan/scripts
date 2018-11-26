import copy
import os
from pprint import pprint

import xlrd
from slugify import slugify


def merge_all_dicts(dict_arr, with_none=False):
    result = {}

    for item in dict_arr:
        if not with_none:
            _item = copy.deepcopy(item)

            for key, value in _item.items():
                if value is None:
                    del item[key]

        result = merge_dicts(result, item)

    return result


def merge_dicts(dict1, dict2):
    return {**dict1, **dict2}


def get_first_line(target_str):
    target_str = " ".join(target_str.split())

    # re_result = re.search("(.*?) [A-Z]", target_str)
    # target_str = re_result.group(1) if re_result else target_str

    return target_str


def read_merged_cell(rowx, colx, thesheet):
    for crange in thesheet.merged_cells:
        rlo, rhi, clo, chi = crange
        if rowx in range(rlo, rhi):
            if colx in range(clo, chi):
                return thesheet.cell_value(rlo, clo)

    return thesheet.cell_value(rowx, colx)


class YokSpider:
    def __init__(self):
        self.source_folder = "C:\\Users\\dorukcan\\Downloads"

    def extract_file(self, file_obj):
        output = {}

        # get file path
        file_path = os.path.join(self.source_folder, file_obj["file_name"])

        # initialize excel
        book = xlrd.open_workbook(file_path, formatting_info=True)

        for item in book.xf_list:
            pprint(item.__dict__)
            pprint(item.alignment.__dict__)
            pprint(item.background.__dict__)
            pprint(item.border.__dict__)
            pprint(item.protection.__dict__)
            print("-------------")

        sh = book.sheet_by_index(0)
        pprint(sh._first_full_rowx)

        # initialize variables
        output["title"] = slugify(get_first_line(sh.cell(0, 0).value), separator="_")
        output["data"] = []

        # extract keys
        keys = []
        for col in range(file_obj["column_start"] - 1, file_obj["column_end"]):
            key = ""

            for row in range(file_obj["header_row_start"] - 1, file_obj["header_row_end"]):
                if sh.cell(row, col).value == "" and row == file_obj["header_row_end"] - 1:
                    key += file_obj["missing_key"] + " "
                else:
                    raw_key = read_merged_cell(row, col, sh)
                    raw_key = int(raw_key) if type(raw_key) is float else raw_key
                    key += str(raw_key) + " "

            key = key[-60:]
            key = key + "1" if key in keys else key

            keys.append(key)

        # extract values
        values = []
        for row in range(file_obj["values_row_start"] - 1, file_obj["values_row_end"]):
            value = []

            for col in range(file_obj["column_start"] - 1, file_obj["column_end"]):
                print(sh.cell(row, col).__repr__())

                val = sh.cell(row, col).value

                if type(val) is int or type(val) is float:
                    val = val * file_obj["multiply"]

                val = None if val == "" else val

                value.append(val)

            values.append(value)

        # merge keys and values
        for row in values:
            dict_obj = {}

            for key, value in zip(keys, row):
                key = slugify(key, separator="_")
                key = "_" + key if len(key) != 0 and key[0].isdigit() else key
                dict_obj[key] = value

            output["data"].append(dict_obj)

        return output

    def run(self):
        files = [{
            "file_name": "2017_T105_V1.xls",
            "missing_key": "universite",
            "multiply": 1,
            "header_row_start": 2,
            "header_row_end": 4,
            "values_row_start": 5,
            "values_row_end": 10,
            "column_start": 1,
            "column_end": 46,
        }]

        data = self.extract_file(files[0])
        # pprint(data)


if __name__ == "__main__":
    YokSpider().run()
