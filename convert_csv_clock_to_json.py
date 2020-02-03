import sys
import argparse
import enum
import datetime as dt
import pandas as pd
import json


class ExportKind(enum.Enum):
    L_7DAYS = 1
    CURR_WEEK = 2
    LAST_WEEK = 3


MAP_EXPORT = {
    "last_7_days": ExportKind.L_7DAYS,
    "current_week": ExportKind.CURR_WEEK,
    "last_week": ExportKind.LAST_WEEK
}


def merge_item(out_dict):
    if 'children' not in out_dict:
        return out_dict

    new_dict = {
        "name": out_dict['name'],
        "children": []
    }
    if 'value' in out_dict:
        new_dict['value'] = out_dict['value']

    done = []
    for i in out_dict['children']:
        if i['name'] in done:
            continue

        m = {
            "name": i['name']
        }

        if 'children' in i:
            m['children'] = i['children'][:]

        if 'value' in i:
            m['value'] = i['value']

        for j in out_dict['children']:
            if i['name'] == j['name'] and i != j:
                if 'value' in i or 'value' in j:
                    m['value'] = i.get('value', 0) + j.get('value', 0)
                if 'children' in i or 'children' in j:
                    m['children'] = (i.get('children', []) +
                                     j.get('children', []))

        done.append(i['name'])
        new_dict['children'].append(m)

    new_dict['children'] = [merge_item(i) for i in new_dict['children']]
    return new_dict


def csv_to_json_hierarchy(input_file, output_file, kind=None):
    df = pd.read_csv(input_file)
    df['start'] = pd.to_datetime(df['start'], format="%Y-%m-%d %H:%M")
    df['end'] = pd.to_datetime(df['end'], format="%Y-%m-%d %H:%M")

    if kind == ExportKind.L_7DAYS:
        range_max = df['end'].max()
        range_min = range_max - dt.timedelta(days=7)
        df = df.loc[df['start'] >= range_min]
    elif kind == ExportKind.CURR_WEEK:
        today = dt.date.today()
        if today.weekday() != 0:
            t = today - dt.timedelta(days=-today.weekday(), weeks=1)
        else:
            t = today - dt.timedelta(seconds=0)
        t = dt.datetime.combine(t, dt.datetime.min.time())
        df = df.loc[df['start'] >= t]
    elif kind is not None:
        raise ValueError("Enter correct date options")

    df['time'] = (pd.to_numeric(df['end'] - df['start'])/10**9)/60
    df['parents'] = df['parents'].fillna('Top')
    df['task|parents'] = df['task'] + '|' + df['parents']
    cleaned = df[['task|parents', 'time']].groupby('task|parents').sum()

    cleaned_dict = cleaned.to_dict()['time']
    out_dict = {
        "name": "clock",
        "children": []
    }
    for i in cleaned_dict:
        all_parents = i.split('|')[1].split('/')

        main_dict = out_dict
        for p in all_parents:
            if p == "Top":
                continue
            if p not in [u['name'] for u in main_dict['children']]:
                main_dict['children'].append({"name": p, "children": []})

            main_dict = [a for a in main_dict['children']
                         if a['name'] == p][0]

    for i in cleaned_dict:
        all_parents = i.split('|')[1].split('/')
        main_dict = out_dict
        for p in all_parents:
            if p == "Top":
                continue

            main_dict = [u for u in main_dict['children']
                         if u['name'] == p][0]

        main_dict['children'].append({
            "name": i.split('|')[0],
            "value": cleaned_dict[i]
        })

    out_dict = merge_item(out_dict)
    json.dump(out_dict, output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_filename", "-f", nargs='?',
                        type=argparse.FileType('r'),
                        default=sys.stdin)
    parser.add_argument("--output_filename", "-o", nargs='?',
                        type=argparse.FileType('w'),
                        default=sys.stdout)
    parser.add_argument("--dates", "-d",
                        choices=["last_7_days", "current_week", "last_week"],
                        default="current_week")

    args = parser.parse_args()

    csv_to_json_hierarchy(args.input_filename, args.output_filename,
                          kind=MAP_EXPORT.get(args.dates))
