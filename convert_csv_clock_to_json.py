import pandas as pd
import json

df = pd.read_csv("clock.csv")
df['start'] = pd.to_datetime(df['start'], format="%Y-%m-%d %H:%M")
df['end'] = pd.to_datetime(df['end'], format="%Y-%m-%d %H:%M")
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
    main_dict['children'].append(
        {
            "name": i.split('|')[0],
            "value": cleaned_dict[i]
        })
json.dump(out_dict, open('clock.json', 'w'))
