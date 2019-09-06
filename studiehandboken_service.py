import requests
import datetime
import pprint
import locale

baseUrl = "http://stserv.abo.fi/api/accomplishment-plan/"
courseUrl = "http://stserv.abo.fi/api/realizations/course/"
languageCode = ["En", "Fi", "Sv"]
keys = {"M.Sc.": 4349, "B.Sc.": 5071, "Other": 0}
courses = {}
courses_timetable = {}
default_lang = "value" + languageCode[0]


# Default swedish
def website_parser(website_code, lang=default_lang, output=True):
    # TODO: make test for websited code
    r = requests.get(url=baseUrl + website_code)
    response = r.json()
    title = response[0]["name"][lang]

    if output: print("This is the students handbook of {}".format(title))

    recursive_print(response[0]["children"], indent=4, lang=lang, p=output)


def recursive_print(dictionary, indent=4, lang=default_lang, p=True):
    for child in dictionary:
        if child["type"] == "STUDY_MODULE" or child["type"] == "CATEGORY":
            if p: print((' ' * indent), child["name"][lang])
            recursive_print(child["children"], indent + 4, lang, p)
        elif child["type"] == "COURSE_UNIT":
            if p: print((' ' * indent), child["name"][lang], child["maxCredits"], "sp", "[" + child["code"] + "]")
            courses[child["name"][lang]] = child["id"]


def course_parser(course_code, lang=default_lang):
    # TODO: make test for websited code
    r = requests.get(url=courseUrl + course_code)
    response = r.json()
    if len(response) > 0:
        title = response[0]["name"][lang]
        get_reservations(response[0], lang)
    # else:
    #     print("No information about", course_code)


def get_reservations(course, lang=default_lang):
    res = []
    today = datetime.datetime.now()
    for index, reservation in enumerate(course["reservations"]):
        startStamp = reservation["startTime"] / 1000
        endStamp = reservation["endTime"] / 1000
        start = datetime.datetime.fromtimestamp(startStamp)
        end = datetime.datetime.fromtimestamp(endStamp)
        # print(course["name"][language], start, "-", end)

        # Filter out old reservations
        if start > today:
            res.append({"startTime": start, "endTime": end})

    courses_timetable[course["name"][lang]] = res

def get_thisweek_sunday(plus_weeks=1):
    today = datetime.datetime.now()
    weekday = datetime.datetime.weekday(today)
    return today.now() + datetime.timedelta(days=((7 * plus_weeks) + 6 - weekday))


def main_parser(program="M.Sc.", lang=default_lang, weeks=0):
    if lang is "English":
        lang = "valueEn"
        lang_code = "en"
    elif lang is "Finnish":
        lang = "valueFi"
        lang_code = "fi_FI"
    else:
        lang = "valueSv"
        lang_code = "sv_SE"

    output = False
    website_parser(str(keys[program]), lang, output=output)
    get_thisweek_sunday()
    if output: print("Searching for courses...")
    for k, v in courses.items():
        course_parser(v, lang)

    weeks_from_now = weeks
    if output: ("Looking for next {} weeks courses.. Hold on!".format(weeks_from_now + 1))
    sunday = get_thisweek_sunday(weeks_from_now)
    text = ""
    # locale.setlocale(locale.LC_TIME, 'sv_SE')

    for name, timetable in courses_timetable.items():
        if timetable:
            first = True
            for time in sorted(timetable, key=lambda item: item["startTime"]):
                if time["startTime"] < sunday:
                    if output:
                        if first:
                            print("-------------------------------------------")
                            print(name)
                            first = False
                        print(time["startTime"].strftime("%A %d.%m"), time["startTime"].strftime("%H:%M"), "-",
                              time["endTime"].strftime("%H:%M"))
                        break
                    else:
                        if first:
                            text = text + name + "\n"
                            first = False
                        # chatbot
                        text = text + " " * 15 + time["startTime"].strftime("%A %d.%m") + " " + time[
                            "startTime"].strftime(
                            "%H:%M") + "-" + time["endTime"].strftime("%H:%M") + "\n"
                        # break
    if len(text) > 0:
        return text
    else:
        return


if __name__ == "__main__":
    text = main_parser("M.Sc.", default_lang, weeks=1)
    print(text)
