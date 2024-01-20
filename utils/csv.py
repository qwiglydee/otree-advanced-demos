""" Generic utils to load trials from csv files

It is loaded into a list of dicts representing all loaded rows and columns as dicts' fields.
"""
# This file is originally a part of https://github.com/qwiglydee/otree-advanced-demos
# SPDX-FileCopyrightText: © 2024 Maxim Vasilyev <qwiglydee@gmail.com>
# SPDX-License-Identifier: MIT

import csv
from pathlib import Path
from random import sample


def read_csv(filepath: Path, columns):
    """reads data from csv file

    Optionally, converts data to specified column types

    Example:
        POOL = read_csv("stimuli.csv", {'stimulus', 'response'})
        DATA = read_csv("data.csv", { 'response': str, 'response_time': float })

    Args:
        filepath: full path to the file to load
        columns: set of fields to load, or dict of { fld: type }

    Returns:
        list of dicts
    """
    if isinstance(columns, set):
        fields = {f: str for f in columns}
    else:
        fields = dict(columns)

    for k, f in list(fields.items()):
        if f is bool:
            fields[k] = parse_bool # type: ignore

    def parse(row):
        return {f: t(row[f.strip()]) if row[f] != "" else None for f, t in fields.items()}

    with open(filepath, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, dialect="excel")

        headers = reader.fieldnames or []
        if not set(fields.keys()) <= set(headers):
            missing = set(fields.keys()) - set(headers)
            raise RuntimeError(f"missing fields in {filepath}: {missing}")

        return [parse(row) for row in reader]


def parse_bool(val):
    if val.lower() == 'true':
        return True
    elif val.lower() == 'false':
        return False
    else:
        return bool(int(val))


def _matching(filters):
    def match(rec):
        return all(rec[key] == val for key, val in filters.items())
    return match


def filter_data(data, **filters):
    return list(filter(_matching(filters), data))


def get_item(data, **filters):
    [data] = filter(_matching(filters), data)
    return data


def count_data(data, **filters):
    return sum(map(_matching(filters), data))


def sample_data(data, cnt=None, **filters):
    if cnt is None:
        cnt = count_data(data, **filters)
    return list(sample(filter_data(data, **filters), k=cnt))
