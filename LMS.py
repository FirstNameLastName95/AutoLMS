import requests
from bs4 import BeautifulSoup
import time
import json
import sys

# pip install requests
# pip install beautifulsoup4
# pip install html5lib

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

logInData = {
    "__LASTFOCUS": "",
    "__EVENTTARGET": "ctl00$BodyPH$btnLogin",
    "__EVENTARGUMENT": "",
    "__VIEWSTATE": "",
    "__VIEWSTATEGENERATOR": "",
    "__EVENTVALIDATION": "",
    "ctl00$BodyPH$tbEnrollment": "",
    "ctl00$BodyPH$tbPassword": "",
    "ctl00$BodyPH$ddlInstituteID": "3",
    "ctl00$BodyPH$ddlSubUserType": "None",
    "ctl00$hfJsEnabled": "0",
}


def enrollment(enroll):
    logInData["ctl00$BodyPH$tbEnrollment"] = enroll
    return enroll


def password(passw):
    logInData["ctl00$BodyPH$tbPassword"] = passw
    return passw


def oldDataFile(enroll):
    return enroll.replace("-", "") + ".json"


urlLogInCMS = "https://cms.bahria.edu.pk/Logins/Student/Login.aspx"

urlLogoutCMS = "https://cms.bahria.edu.pk/Sys/Student/Logoff.aspx"

urlGoToLMS = "https://cms.bahria.edu.pk/Sys/Common/GoToLMS.aspx"

urlLogOutLMS = "https://lms.bahria.edu.pk/Student/includes/studentprocess.php?s=signout"

urlAssignments = "https://lms.bahria.edu.pk/Student/Assignments.php"


def inputValues():
    try:
        with open("user.json", "r") as f:
            data = json.load(f)

    except FileNotFoundError:
        data = []

    if len(data) == 0:
        print("No users found! Please enter the details of the user...\n")
        enroll = input("Enter Enrollment Number: ")
        passw = input("Enter Password: ")
        data.append({"enroll": enroll, "passw": passw})
        with open("user.json", "w") as f:
            json.dump(data, f)
        return enrollment(enroll), password(passw)
    else:
        print("Select a user...\n")
        for i in range(len(data)):
            print(i + 1, ". ", data[i]["enroll"], sep="")
        while True:
            choice = input("Enter your choice: ")
            if choice.isnumeric() and int(choice) <= len(data):
                break
            else:
                print("Invalid choice")
                continue
        return enrollment(data[int(choice) - 1]["enroll"]), password(
            data[int(choice) - 1]["passw"]
        )


def test():
    try:
        print("Checking for internet connection...")
        requests.get("https://www.google.com/")

    except requests.exceptions.ConnectionError:
        print("No Internet... Waiting for internet...")
        time.sleep(5)
        test()
        return


def logInCMS():
    global s

    s = requests.Session()

    print("Heading over to CMS...")
    r = s.get(urlLogInCMS, headers=headers)

    print("Gathering data...")
    soup = BeautifulSoup(r.content, "html5lib")

    logInData["__VIEWSTATE"] = soup.find("input", attrs={"name": "__VIEWSTATE"})[
        "value"
    ]

    logInData["__VIEWSTATEGENERATOR"] = soup.find(
        "input", attrs={"name": "__VIEWSTATEGENERATOR"}
    )["value"]

    logInData["__EVENTVALIDATION"] = soup.find(
        "input", attrs={"name": "__EVENTVALIDATION"}
    )["value"]

    print("Logging into CMS...")
    r = s.post(urlLogInCMS, data=logInData)
    return r


def logOutCMS():
    print("Logging out of CMS...")
    r = s.get(urlLogoutCMS)
    return r


def LMS():
    print("Heading over to LMS...")
    r = s.get(urlGoToLMS)

    return r


def getLMSDashboard(request):
    print("Gathering data from LMS...")
    soup = BeautifulSoup(request.content, "html5lib")
    table = soup.find("table", attrs={"class": "table"})
    th = table.find_all("th")
    tr = table.find_all("tr")
    td = table.find_all("td")

    print("Parsing the data...")
    list = []
    for i in range(len(tr) - 1):
        list.append({})
        for j in range(len(th)):
            list[i][th[j].text.strip()] = td[j + ((i) * (len(th)))].text.strip()
    return list


def compareData(data, enroll):
    # compare data with the previous data
    print("Checking for previous records...")
    try:
        f = open(oldDataFile(enroll), "r")
        oldData = f.read()
        f.close()
    except FileNotFoundError:
        print("")
        print("")
        print("No previous data found! Creating a new file for future runs...")
        print("")
        print("")
        writeData(data, enroll)
        return

    print("Loading previous data...")
    oldData = json.loads(oldData)

    print("Comparing the data...")
    changeCheck = False
    # traverse list
    for course in data:
        # traverse dictionary named course
        for key, value in course.items():
            if value != oldData[data.index(course)][key]:
                changeCheck = True
                print("")
                print("")
                print(
                    "Change detected in",
                    oldData[data.index(course)]["Course Title"],
                    "!",
                )
                print("Change detected in", key)
                print("Old value:", oldData[data.index(course)][key])
                print("New value:", value)
                print("")
                print("")
    if not changeCheck:
        print("")
        print("")
        print("No changes detected")
        print("")
        print("")
    if changeCheck:
        print("")
        print("")
        print("Do you want to mark this as read?")
        print("1. Yes")
        print("2. No")
        while True:
            choice = input("Enter your choice: ")
            if choice == "1":
                print("Changes marked as read")
                print("")
                print("")
                writeData(data, enroll)
                break
            elif choice == "2":
                print("Changes not marked as read")
                print("")
                print("")
                break
            else:
                print("Invalid choice")
                continue
    return changeCheck


def writeData(data, enroll):
    # helper function for compareData() for writing data to a file
    print("Writing data to a file...")
    f = open(oldDataFile(enroll), "w")
    data = json.dumps(data)
    f.write(data)
    f.close()


def logOutLMS():
    print("Logging out of LMS...")
    r = s.get(urlLogOutLMS)
    return r


def toHTMLFile(request, fileName):
    # save html to file
    print("Converting the response to HTML file...")
    soup = BeautifulSoup(request.content, "html5lib")
    with open(fileName, "w", encoding="utf-8") as f:
        f.write(str(soup))


def main():
    fileName = "soup.html"
    enroll = inputValues()[0]

    while True:
        try:
            test()
            toHTMLFile(logInCMS(), fileName)
            lms = LMS()
            toHTMLFile(lms, fileName)

            data = getLMSDashboard(lms)
            oldDataFile(enroll)
            compareData(data, enroll)

            toHTMLFile(logOutLMS(), fileName)
            toHTMLFile(logOutCMS(), fileName)
        except:
            # print the error and line number
            print("Error: ", sys.exc_info()[0])
            print("Line: ", sys.exc_info()[2].tb_lineno)

            print("Something went wrong...")
            print("Trying again in 5 seconds...")
            time.sleep(5)
            continue
        print("Next check in 1 hour...")
        time.sleep(3600)


main()


# adding more features: pending assignments for now
def pendingAssignments():
    r = s.get(urlAssignments)
    # get all the "values" attribute of the "option" elements which are the children of the element "select" with id = courseID
    soup = BeautifulSoup(r.content, "html5lib")
