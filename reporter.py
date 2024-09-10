#!/usr/bin/env python3

import pickle, json, datetime
from datetime import date, timedelta


f = open('today.pickle', 'rb')
courses = pickle.load(f)

today = date.today()
start = today - timedelta(days=today.weekday())
end = start + timedelta(days=6)
future = start + timedelta(days=5000)

for course in courses:
    print(courses[course]['name'])
    for i in courses[course]['assignments']:
        # print ("    " + i['name'])
        if i['due_at']:
            # print(i['due_at'])
            due = datetime.datetime.strptime(i['due_at'], '%Y-%m-%dT%H:%M:%SZ').date()
        else:
            due = future

        if not i['has_submitted_submissions']:
            if due < today:
                print ("  Overdue: " + i['name'])

            if due < end:
                if due > today:
                    print ("  This Week: " + i['name'])
                    # print(json.dumps(i))
