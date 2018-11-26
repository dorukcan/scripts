# -*- coding: utf-8 -*-

import datetime
import re

import requests
from bs4 import BeautifulSoup
from sqlalchemy import *

"""
Güney Kampüs
İB : Washburn Hall (İktisadi ve İdari Bilimler Fakültesi)
JF : John Freely Binası
NB : Natuk Birkan Binası
SH : Sloane Hall (Sosyoloji ve Psikoloji Bölümleri)
M  : Perkins Hall (Mühendislik Fakültesi)
TB : Anderson Hall (Fen-Edebiyat Fakültesi)	
BIM : Bilgi İşlem Merkezi

Kuzey Kampüs
KYD : Kuzey YADYOK Binası
EF : Eğitim Fakültesi
BM : Bilgisayar Mühendisliği Binası	
ET : Kilyos Kampüsü	
KB : Fen ve Mühendislik Binası (Kare Blok)	
KP : Kuzey Park Binası	
NH : Yeni Bina	
YYD : Yeni YADYOK Binası	

Hisar Kampüs	
HA : Hisar Kampüs -A Blok	
HB : Hisar Kampüs -B Blok	
HC : Hisar Kampüs-C Blok	
HD : Hisar Kampüs-D Blok	
HE : Hisar Kampüs-E Blok	

Uçak Savar Kampüsü	
GKM : Garanti Kültür Merkezi	

Kandilli Kampüsü	
BME : Biyomedikal Mühendisliği Enstitüsü	

Kilyos Kampüsü	
SA : YADYOK	
"""

""" GET COURSE DATA SECTION """


def fetchCourseListData(semester):
    # get course list data
    cacheName = makeFileNameSafe(semester)
    rawData = cache(cacheName)

    if rawData == None:
        print(cacheName + " datasi yokmus")
        r = requests.post("http://registration.boun.edu.tr/scripts/schdepsel.asp", data={'semester': semester})
        cache(cacheName, r.text)
        rawData = r.text

    print(cacheName + " course list geldi")

    # extract course list
    result = []
    soup = BeautifulSoup(rawData, "lxml")
    for course in soup.findAll("td", class_="schtd"):
        name = course.find("font").get_text()
        url = "http://registration.boun.edu.tr/" + course.find("a").get("href")
        result.append({"name": name, "url": url})
    print("course list ayristi")

    return result


def fetchCourseData(courseName, courseUrl):
    # get course data
    cacheName = makeFileNameSafe(courseName)
    print(cacheName + " icindeyiz")

    rawData = cache(cacheName)
    if rawData == None:
        print(cacheName + " datasi yokmus")
        r = requests.get(courseUrl)
        cache(cacheName, r.text)
        rawData = r.text

        # extract course data
    soup = BeautifulSoup(rawData, "lxml")
    result = []
    for row in soup.findAll("tr", {'class': ['schtd', 'schtd2']}):
        cells = row.findAll("td")
        if len(cells) != 14:
            print(cells[0])
            continue

        code = cells[0].get_text().replace('\xa0', '').replace(" ", "")
        description = ""  # cells[1].find("a").attrs["onclick"]
        name = cells[2].get_text().replace('\xa0', '')
        name = makeRegistrationNameSafe(name)
        credits = cells[3].get_text().replace('\xa0', '')
        ects = cells[4].get_text().replace('\xa0', '')
        quota = ""  # "http://registration.boun.edu.tr/scripts/quotasearch.asp?abbr=ASIA&code=501&section=01"
        instructor = cells[6].get_text().replace('\xa0', '')
        instructor = makeRegistrationNameSafe(instructor)
        days = cells[7].get_text().replace('\xa0', '')
        hours = cells[8].get_text().replace('\xa0', '')
        rooms = cells[9].get_text().replace('\xa0', '').replace("Ý", "I").replace(" ", "")

        result.append({"code": code, "description": description, "name": name, "credits": credits, "ects": ects,
                       "quota": quota, "instructor": instructor, "days": days, "hours": hours, "rooms": rooms})
    print(cacheName + " course data ayristi")
    return result


def saveCourseData(data):
    print("saveCourseInformation icindeyiz")

    engine = create_engine('sqlite:///bcp.db', echo=False)
    metadata = MetaData()

    courses = Table("courses", metadata,
                    Column("id", Integer, primary_key=True, autoincrement=True, unique=True),
                    Column("code", Text),
                    Column("description", Text),
                    Column("name", Text),
                    Column("credits", Text),
                    Column("ects", Text),
                    Column("quota", Text),
                    Column("instructor", Text, default="TBA"),
                    Column("days", Text, default="TBA"),
                    Column("hours", Text, default="TBA"),
                    Column("rooms", Text, default="TBA"))
    metadata.create_all(engine)

    connection = engine.connect()
    insert = courses.insert()
    connection.execute(insert, data)

    print("saveCourseInformation bitti")


def cache(name, text=None):
    engine = create_engine('sqlite:///bcp.db', echo=False)
    metadata = MetaData()

    cache = Table("cache", metadata,
                  Column("id", Integer, primary_key=True, autoincrement=True, unique=True),
                  Column("name", Text),
                  Column("data", Text),
                  Column("date", Text))
    metadata.create_all(engine)

    if text is None:
        s = select([cache.c.data]).where(cache.c.name == name)
        result = engine.execute(s).fetchone()
        if result is None:
            return None
        else:
            return result["data"]
    else:
        ins = cache.insert().values(name=name, data=text, date=str(datetime.datetime.now()))
        ins.compile()
        engine.execute(ins)


def makeFileNameSafe(name):
    # https://stackoverflow.com/questions/2021624/string-sanitizer-for-filename
    return re.sub(r"[^\w\s\d\-_~,;:\[\]\(\).]", "", name)


def makeRegistrationNameSafe(name):
    forbidden = 'ÝÖÐÞÇÜ'
    allowed = 'IOGSCU'
    translate_table = dict((ord(char), allowed[i]) for i, char in enumerate(forbidden))

    return name.translate(translate_table)


""" USE COURSE DATA SECTION """


def getCourseInfo(code):
    engine = create_engine('sqlite:///bcp.db', echo=False)
    metadata = MetaData()
    metadata.bind = engine

    courses = Table("courses", metadata, autoload=True)
    s = select([courses]).where(courses.c.code == code)
    result = engine.execute(s).fetchone()

    if result is None:
        return None
    else:
        return {"name": result["name"],
                "instructor": result["instructor"],
                "rooms": result["rooms"],
                "days": result["days"],
                "hours": result["hours"]}


def scheduleDataOfRoom(roomCode):
    officialDays = {"M": 0, "T": 1, "W": 2, "Th": 3, "F": 4, "St": 5}
    schedule = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

    engine = create_engine('sqlite:///bcp.db', echo=False)
    metadata = MetaData()
    metadata.bind = engine

    courses = Table("courses", metadata, autoload=True)
    s = select([courses]).where(courses.c.rooms.like("%" + roomCode + "%"))
    for row in engine.execute(s):
        days = re.findall('[A-Z][a-z]*', row[courses.c.days])
        hours = list(row[courses.c.hours])
        rooms = row[courses.c.rooms].split("|")

        for day, hour, room in zip(days, hours, rooms):
            if room == roomCode:
                schedule[officialDays[day]][int(hour) - 1] = row[courses.c.code]

    return schedule


def makeNiceSchedule(schedule):
    days = ["Monday", "Thursay", "Wednesday", "Thursday", "Friday", "Saturday"]
    hours = ["09:00 - 10:00", "10:00 - 11:00", "11:00 - 12:00", "12:00 - 13:00", "13:00 - 14:00", "14:00 - 15:00",
             "15:00 - 16:00", "16:00 - 17:00", "17:00 - 18:00", "18:00 - 19:00", "19:00 - 20:00", "20:00 - 21:00"]

    for i, day in enumerate(schedule):
        print(days[i])
        for j, hour in enumerate(day):
            if hour != 0:
                print(hours[j] + " : " + hour)


def findEmptySpaces(schedule, dayCode):
    """what are we living for?"""

    result = []
    officialDays = {"M": 0, "T": 1, "W": 2, "Th": 3, "F": 4}

    day = schedule[officialDays[dayCode]]
    for i, hour in enumerate(day):
        try:
            if day[i - 1] == 0 and hour == 0 and day[i + 1] == 0:
                return day
        except IndexError:
            continue

        if i == 3:
            break


def getRoomsInBuilding(building):
    result = []

    engine = create_engine('sqlite:///bcp.db', echo=False)
    metadata = MetaData()
    metadata.bind = engine

    courses = Table("courses", metadata, autoload=True)
    s = select([courses]).where(courses.c.rooms.like("%" + building + "%"))
    for row in engine.execute(s):
        rooms = row[courses.c.rooms].split("|")
        for room in rooms:
            if building in room and room not in result:
                result.append(room)
    return sorted(result)


if __name__ == '__main__':
    """
    semester = "2017/2018-1"
    courseList = fetchCourseListData(semester)
    print("#############################################")

    for course in courseList:
        info = fetchCourseData(course["name"], course["url"])
        saveCourseData(info)
        print("#############################################")
    """

    print(getCourseInfo("CHEM105.01"))
    print("#############################################")

    # print findEmptySpaces(scheduleOfRoom("NH 101"))
    # print makeNiceSchedule(scheduleOfRoom("NH 101"))

    print(getRoomsInBuilding("NH"))
    print("#############################################")

    for room in getRoomsInBuilding("EF"):
        print(room, findEmptySpaces(scheduleDataOfRoom(room), "Th"))
