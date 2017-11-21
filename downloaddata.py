#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import http.cookiejar
from datetime import datetime
from getpass import getpass
from urllib.parse import urlencode
from urllib.request import build_opener
from urllib.error import HTTPError
from urllib.request import HTTPCookieProcessor
from json import loads


class WrongPasswordError(Exception):
    pass


class SessionExpiredError(Exception):
    pass


class Librus:
    """Klasa odpowiadająca za odbieranie danych z librusa"""
    BASE_URL = "https://api.librus.pl/"
    URL_ME = BASE_URL + "2.0/Me"
    URL_HOMEWORK = BASE_URL + "2.0/HomeWorks"
    URL_GRADE = BASE_URL + "2.0/Grades"
    URL_CALENDAR = BASE_URL + "2.0/Calendars"
    URL_TOKEN = BASE_URL + "OAuth/Token"
    URL_TIMTABLE = BASE_URL + "2.0/Timetables"
    URL_USERS = BASE_URL + "2.0/Users"
    URL_SUBJECTS = BASE_URL + "2.0/Subjects"
    URL_GRADES_CATEGORIES = BASE_URL + "2.0/Grades/Categories"
    URL_HOMEWORK_CATEGORIES = BASE_URL + "2.0/HomeWorks/Categories"
    URL_LUCKY_NUMBER = BASE_URL + "2.0/LuckyNumbers"
    URL_COLORS = BASE_URL + "2.0/Colors"
    URL_UNITS = BASE_URL + "2.0/Units"
    URL_PARENTS_MEATING = BASE_URL + "2.0/ParentTeacherConferences"
    URL_CALENDAR_SUBSTITIUSIONS = BASE_URL + "2.0/Calendars/Substitutions"
    URL_UNATTENDANCE = BASE_URL + "2.0/Attendances?showPresences=true"
    URL_ANNOUNCEMENT = BASE_URL + "2.0/SchoolNotices"
    URL_ATTENDACE_TYPE = BASE_URL + "2.0/Attendances/Types"
    URL_LESSONS = BASE_URL + '2.0/Lessons'

    def __init__(self, login, password):
        self.__username = login
        self.__cached_objects = dict()
        self.__password = password
        # Stworzenie słoika na ciasteczka ;)
        self.__cj = cj = http.cookiejar.CookieJar()
        self.__opener = build_opener(HTTPCookieProcessor(cj))
        self.__login()

    def login(self):
        self.__login()

    def __login(self):
        """Funkcja wykonująca logowanie do librusa"""
        # Odebranie ciasteczek
        self.__opener.addheaders = [('Authorization', 'Basic MzU6NjM2YWI0MThjY2JlODgyYjE5YTMzZjU3N2U5NGNiNGY=')]

        try:
            self.__opener.open('https://synergia.librus.pl')
            list(self.__cj)[0].domain = 'api.librus.pl'
            tokens = self.get_api_response(self.URL_TOKEN,
                                           data={
                                               'grant_type':
                                                   'password',
                                               'username':
                                                   self.__username,
                                               'password':
                                                   self.__password,

                                               'librus_long_term_token': '1',
                                           })

        except HTTPError as e:
            e.getcode() == 400
            raise WrongPasswordError('Nieprawidłowe hasło')
        self.__opener.addheaders = [('Authorization', 'Bearer %s' %
                                     tokens['access_token'])]

    def get_api_response(self, url, data=None):
        return loads(
            self.__opener.open(url, data=urlencode(data).encode('utf-8') if data else None).read().decode('utf-8'))

    def get_api_object(self, url):
        if url in self.__cached_objects:
            return self.__cached_objects[url]
        try:
            res = self.get_api_response(url)
            self.__cached_objects[url] = res
            return res
        except HTTPError:
            self.__cached_objects[url] = None
            return None

    def get_announcements(self):
        """
        Funkcja pobierająca dane ze strony
https://librus.synergia.pl/ogloszenia
        :returns: :return: lista [{"author": autor,
                         "title": tytuł,
                         "time": czas,
                         "content": zawartość}]
        """
        # Załadowanie ogłoszeń
        try:
            data = loads(self.__opener.open('https://api.librus.pl/2.0/SchoolNotices').read())
        except HTTPError:
            raise SessionExpiredError
        return [{'author': notice[u'AddedBy'][u'Id'],
                 'title': notice[u'Subject'].encode('utf-8'),
                 'content': notice[u'Content'].encode('utf-8'),
                 'time': notice[u'StartDate']
                 } for notice in data[u'SchoolNotices']]


class User(object):
    def __init__(self, librus, json=None, url=None):
        if not (json or url):
            raise AttributeError
        self.id = None  # type: int
        self.url = None  # type: int
        self.first_name = None  # type: str
        self.last_name = None  # type: str
        if not json:
            json = librus.get_api_object(url)
        if not json:
            return
        self.first_name = json['User']['FirstName']
        self.last_name = json['User']['LastName']
        self.id = json['User']['Id']


class Lesson(object):
    def __init__(self, librus, json=None, url=None):
        if not (json or url):
            raise AttributeError
        self.id = None  # type: int
        self.url = None  # type: str
        self.teacher = None  # type: User
        self.cls = None
        self.subject = None  # type: Subject
        if not json:
            json = librus.get_api_object(url)
        self.teacher = User(librus,
                            url=json['Lesson']['Teacher']['Url'])
        self.subject = Subject(librus,
                               url=json['Lesson']['Subject']['Url'])
        self.id = json['Lesson']['Id']
        self.url = json['Url']


class Subject(object):
    def __init__(self, librus, json=None, url=None):
        if not (json or url):
            raise AttributeError
        self.id = None  # type: int
        self.url = None  # type: str
        self.name = None  # type: str
        self.number = None  # type: int
        self.short = None  # type: str
        self.is_extracurricular = None  # type: bool
        self.is_block_lesson = None  # type: bool
        if not json:
            json = librus.get_api_object(url)
        self.name = json['Subject']['Name']
        self.number = json['Subject']['No']
        self.short = json['Subject']['Short']
        self.is_block_lesson = json['Subject']['IsBlockLesson']
        self.is_extracurricular = json['Subject']['IsExtracurricular']
        self.id = json['Subject']['Id']
        self.url = json['Url']


class AttendanceType(object):
    def __init__(self, librus, json=None, url=None):
        if not (json or url):
            raise AttributeError
        self.id = None  # type: int
        self.url = None  # type: str
        self.short = None  # type: str
        self.name = None  # type: str
        self.order = None  # type: int
        self.color_rgb = None  # type: str
        self.is_presence_kind = None  # type: bool
        if not json:
            json = librus.get_api_object(url)
        self.is_presence_kind = json['Type']['IsPresenceKind']
        self.id = json['Type']['Id']
        self.short = json['Type']['Short']
        self.name = json['Type']['Name']
        self.order = json['Type']['Order']
        self.color_rgb = json['Type']['ColorRGB'] if 'ColorRGB' in json['Type'] else None


class Attendance(object):
    def __init__(self, librus, json=None, url=None):
        if not (json or url):
            raise AttributeError
        self.id = None  # type: int
        self.url = None  # type: str
        self.semester_id = None  # type: int
        self.lesson_num = None  # type: int
        self.lesson = None  # type: Lesson
        self.added_by = None  # type: User
        self.date = None  # type: datetime
        self.add_date = None  # type: datetime
        self.student = None  # type: User
        self.type = None  # type: AttendanceType
        if not json:
            json = librus.get_api_object(url)
        self.id = json['Id']
        self.student = User(librus, url=json['Student']['Url'])
        self.added_by = User(librus, url=json['AddedBy']['Url'])
        self.lesson = Lesson(librus, url=json['Lesson']['Url'])
        self.lesson_num = json['LessonNo']
        self.date = datetime.strptime(json['Date'], '%Y-%m-%d')
        self.add_date = datetime.strptime(json['AddDate'], '%Y-%m-%d %H:%M:%S')
        self.type = AttendanceType(librus, url=json['Type']['Url'])
        self.semester_id = json['Semester']