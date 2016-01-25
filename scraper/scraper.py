""" Original python command-line scraper for UNSW lecture times. Unused in the webapp. """

import re
import sys
from collections import Counter

import requests

SEMESTER = "15s2"
BASE_URL = "http://www.cse.unsw.edu.au/~teachadmin/lecture_times/" + SEMESTER
DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday")


def html_extract_absolute_urls(base_url, html):
    pass


def get_courses(course_category):
    index = requests.get('{}/{}'.format(BASE_URL, course_category))
    subpages = re.findall(r'A HREF="(.*?\.html)"', index.text)
    return ['{}/{}'.format(course_category, subpage) for subpage in subpages]


def get_lectures(user_courses):
    courses = []
    for arg in user_courses:
        if len(arg) == 4:
            courses += get_courses(arg)
        elif len(arg) == 8:
            courses.append('{}/{}.html'.format(arg[:4], arg[4:]))
        else:
            print("Invalid argument: {}".format(arg))

    table_texts = {}
    for course in courses:
        print(course)
        response = requests.get('{}/{}'.format(BASE_URL, course))
        if response.status_code == 200:
            table_match = re.search(r'<table border=1.*?>(.*?)</table>', response.text, re.DOTALL)
            table_texts[course] = table_match.group(1)
        else:
            print("Could not find course {}".format(course))

    tables = {}
    for course, tableText in table_texts.items():
        tables[course] = {}
        row_texts = re.findall(r'<tr>(.*?)(?=(?:$|<tr>))', tableText, re.DOTALL)
        for rowText in row_texts:
            time = re.search(r'<th>(.*?)<', rowText).group(1)
            cells = re.findall(r'<td.*?small>(.*?)(?=(?:$|<td))', rowText)
            for day, cell in zip(DAYS, cells):
                cell_count = re.findall(r'([A-Z0-9]*?)\((.*?)\)', cell)
                cell_count = [(name, int(count)) for name, count in cell_count]
                tables[course][(day, time)] = cell_count
    return tables


def total_count(lectures):
    count = Counter()
    for subject in lectures.values():
        subject_count = {dayTime: sum([count[1] for count in subjectList]) for dayTime, subjectList in subject.items()}
        count.update(subject_count)
    return dict(count)


def main():
    if len(sys.argv) <= 1:
        exit("Usage: python scraper.py COMP1917 COMP1921 COMP1927 ...")
    lectures = get_lectures(sys.argv[1:])
    total = total_count(lectures)
    ordered_count = sorted(total.items(), key=lambda item: (DAYS.index(item[0][0]), int(item[0][1].split(':')[0])))
    print("\n".join(["{} {}: {}".format(count[0][0], count[0][1], count[1]) for count in ordered_count]))

if __name__ == '__main__':
    main()
