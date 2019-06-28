import csv
from tempfile import NamedTemporaryFile
from useful_utilities import *
import shutil
import ast


def enable_testing():
    # TODO
    append_data = debug_func()
    identify = debug_func(append_data)
    store = debug_func(store)


def append_data(nid, did, filename, data, append=False):
    if append:
        with open(filename, "a") as readFile:
            writer = csv.writer(readFile)
            writer.writerows([[nid, did, data]])
            readFile.flush()
            return
    else:
        with open(filename, "r+") as readFile:
            reader = csv.reader(readFile)
            writer = csv.writer(readFile)
            lines = list(reader)
            i = 0
            for row in lines:
                if row[0] == [nid] or row[1] == [did]:
                    print("failure")
                    raise AssertionError
            writer.writerows([[nid, did, data]])


def identify(name, value, filename):
    value = str(value)
    name = str(name)
    with open(filename, "r") as readFile:
        reader = csv.reader(readFile)
        name_found = False
        for row in reader:
            if row[0] == name and row[1] == value:
                row[-1] = ast.literal_eval(row[-1])
                return row[-1]
            if row[0] == name:
                name_found = True
    if name_found:
        return None
    else:
        return None


def identify_name(name, filename):
    with open(filename, "r") as readFile:
        reader = csv.reader(readFile)
        for row in reader:
            if row[0] == name:
                row[-1] = ast.literal_eval(row[-1])
                return row[-1]
        return None


def store(name, value, data, filename):
    temp_file = NamedTemporaryFile(mode="w", delete=False)
    with open(filename, "r+") as csv_file:
        reader = csv.reader(csv_file)
        writer = csv.writer(temp_file)
        changed = False
        for row in reader:
            if row[0] == name and row[1] == value:
                row[2] = ast.literal_eval(row[2])
                row[2] = row[2] + data
                changed = True
            writer.writerow(row)
        if not changed:
            writer.writerow([name, value, data])
        temp_file.flush()
        csv_file.flush()
        shutil.move(temp_file.name, filename)
