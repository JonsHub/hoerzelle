import datetime
import os
import time
import sqlalchemy as db
import pyautogui
import pyperclip
from countdown_slideshow import start_countdown_slideshow

WAITING_TIME = 30


picture = {
    '''                                 
    GUI-Object to       Filename of the actual image 
    look for            in the Folder
    '''  
    
    "lastname":         "Nachname.png",
    "firstname":        "Vorname.png",
    "date_of_birth":    "Gebdatum.png",
    "gender_male":      "geschlecht_mannlich.png",
    "gender_female":    "geschlecht_weiblich.png",
    "email":            "email.png",
    "autotest_Button":  "autotest_button.png",
    "start_Button":     "start_Button2.png",  # minSearchTime=5
    "end_window1":      "end_window_2.png",  # minSearchTime=5
    "end_window2":      "Fenster.png",  # minSearchTime=5
    "end_window3":      "end_window_1.png",  # minSearchTime=5
    "save":             "MainTest3_speichern.png",
    "print":            "MainTest3_drucken.png",  # minSearchTime=5
    "print_ok":         "Druck1_fenster_ok_2.png",  # minSearchTime=2
    "close":            "MainTest3_beenden.png",  # minSearchTime=3
    "remove_Patient":   "patient_entfernen_2.png"  # minSearchTime=5
}


def get_data(usr_id):
    # TODO hide uri string to DB
    engine = db.create_engine('mysql+pymysql://hoerzell:Abcd123$@fbi-mysqllehre.th-brandenburg.de/hoerzell_db')
    connection = engine.connect()
    metadata = db.MetaData()

    user = db.Table('user', metadata, autoload=True, autoload_with=engine)  # specifying user as a Table
    query = db.select([user.columns.id, user.columns.firstname, user.columns.lastname, user.columns.email,
                       user.columns.date_of_birth, user.columns.gender]).where(user.columns.id == usr_id)
    # creating query to get id, firstname, lastname, email-address, date of birth and gender; where id=given_id
    ResultProxy = connection.execute(query)  # executing query
    ResultSet = ResultProxy.fetchall()  # getting all the returned Data
    #print(ResultSet)

    global firstname
    firstname = ResultSet[0][1]
    print(ResultSet[0][1])

    global lastname
    lastname = ResultSet[0][2]
    print(ResultSet[0][2])

    global email
    email = ResultSet[0][3]
    print(ResultSet[0][3])
    
    global dob
    dob = ResultSet[0][4]
    print(ResultSet[0][4])

    global gender
    gender = ResultSet[0][5]
    print(ResultSet[0][5])


def get_data2(usr_id): #TODO: new version of get_data: new sqlalchemy syntax
    # TODO hide uri string to DB
    from sqlalchemy import create_engine, MetaData, select, Table

    # Create engine and connection
    engine = create_engine('mysql+pymysql://hoerzell:Abcd123$@fbi-mysqllehre.th-brandenburg.de/hoerzell_db')
    connection = engine.connect()
    metadata = MetaData()

    # Load table metadata
    metadata.reflect(bind=engine)

    # Get the user table
    user_table = metadata.tables['user']

    # Create query using new SQLAlchemy 2.x syntax
    query = select(
        user_table.c.id,
        user_table.c.firstname,
        user_table.c.lastname,
        user_table.c.email,
        user_table.c.date_of_birth,
        user_table.c.gender
    ).where(user_table.c.id == usr_id)

    try:
        result_proxy = connection.execute(query)
        result_set = result_proxy.fetchall()

        if not result_set:
            raise ValueError(f"No user found with id {usr_id}")

        global firstname, lastname, email, dob, gender
        firstname = result_set[0][1]
        lastname = result_set[0][2]
        email = result_set[0][3]
        dob = result_set[0][4]
        gender = result_set[0][5]

        print(f"Retrieved data for user: {firstname} {lastname}")

    except Exception as e:
        print(f"Error retrieving user data: {str(e)}")
        raise
    finally:
        connection.close()
        engine.dispose()


def check_for(name, mst):
    '''Take image name and min amount of time (int) to search. Will Mouse-Leftclick center of wanted area.'''
    path = f"C:\\Users\\LattePanda\\Desktop\\automation_1_3\\Bilder\\{name}"

    print(path)

    try:
        if isinstance(mst, int) and mst != 0:
            x, y = pyautogui.locateCenterOnScreen(path, minSearchTime=mst)
            pyautogui.moveTo(x, y)
            pyautogui.leftClick()
            return True
        else:
            x, y = pyautogui.locateCenterOnScreen(path)
            pyautogui.moveTo(x, y)
            pyautogui.leftClick()
            return True
    except(TypeError, pyautogui.ImageNotFoundException):
        return False


def check_for_2(name, mst):
    '''Take image name and min amount of time (int) to search. Will Mouse-Leftclick center of wanted area.'''
    path = f"C:\\Users\\LattePanda\\Desktop\\automation_1_3\\Bilder\\{name}"
    
    time.sleep(1)  # Allow some time for the UI to update

    print(path)
    print("does path exist: ",os.path.exists(path))  # Should return True

    try:
        if isinstance(mst, int) and mst != 0:
            x, y = pyautogui.locateCenterOnScreen(path, confidence=0.8)
            pyautogui.moveTo(x, y)
            pyautogui.leftClick()
            return True
        else:
            x, y = pyautogui.locateCenterOnScreen(path, confidence=0.8)
            
            pyautogui.moveTo(x, y)
            pyautogui.leftClick()
            return True
    except(TypeError, pyautogui.ImageNotFoundException):
        return False


def find(name, mst):
    '''Take image name and min amount of time (int) to search. Will just look for wanted area.'''
    path = f"C:\\Users\\LattePanda\\Desktop\\automation_1_3\\Bilder\\{name}"

    try:
        if isinstance(mst, int) and mst != 0:
            x, y, w, h = pyautogui.locateOnScreen(path, minSearchTime=mst)
            return True
        else:
            x, y, w, h = pyautogui.locateOnScreen(path)
            return True
    except (TypeError, pyautogui.ImageNotFoundException):
        return False



def find_2(name, mst):
    '''Take image name and min amount of time (int) to search. Will just look for wanted area.'''
    path = f"C:\\Users\\LattePanda\\Desktop\\automation_1_3\\Bilder\\{name}"

    try:
        if isinstance(mst, int) and mst != 0:
            x, y, w, h = pyautogui.locateOnScreen(path, minSearchTime=mst, confidence=0.8)
            return True
        else:
            x, y, w, h = pyautogui.locateOnScreen(path, confidence=0.8)
            return True
    except (TypeError, pyautogui.ImageNotFoundException):
        return False

def automate_registration():
    # prepare date of birth
    #dob2 = str(dob.day)
    if int(dob.day) < 10:
        dob2 = '0' + str(dob.day)
    else:
        dob2 = str(dob.day)
    if int(dob.month) < 10:
        dob2 = dob2 + '0' + str(dob.month)
    else:
        dob2 = dob2 + str(dob.month)
    dob2 = dob2 + str(dob.year)

    if check_for("Nachname.png", 0):
        pyautogui.write(lastname)
    else:
        pyautogui.write(lastname)

    if check_for(picture["firstname"], 0):
        pyautogui.write(firstname)
    else:
        pyautogui.press('tab')
        pyautogui.write(firstname)

    if check_for(picture["date_of_birth"], 0):
        pyautogui.write(dob2)
    else:
        pyautogui.press('tab')
        pyautogui.write(dob2)

    if gender == 'm':
        if not check_for(picture["gender_male"], 0):
            pyautogui.press('tab')
            pyautogui.hotkey('shift', 'enter')
            pyautogui.press('tab')  # setting the cursor to the female position
    else:
        if not check_for(picture["gender_female"], 0):
            pyautogui.press('tab', presses=2)  # cursor is sitting in female position
            pyautogui.hotkey('shift', 'enter')

    if check_for(picture["email"], 0):
        pyperclip.copy(email)
        pyautogui.hotkey('ctrl', 'v')
    else:
        pyautogui.press('tab', presses=6)
        pyperclip.copy(email)
        pyautogui.hotkey('ctrl', 'v')

    pyautogui.press('f2')
    time.sleep(3)
    pyautogui.press('enter')


def automate_test():
    i = 1
    
    # time.sleep(10)  # check every 20s

    check_for_2(picture["autotest_Button"], 0)
    print("hello")
    #check_for_2(picture["autotest_Button"], 0)
    check_for(picture["start_Button"], 5)
    # check if Test is over
    while i != 0:
        time.sleep(20)  # check every 20s

        if find_2(picture["end_window1"], 5):
            i = 0
        elif find_2(picture["end_window2"], 5):
            i = 0
        elif find_2(picture["end_window3"], 5):
            i = 0
        else:
            i = i + 1
            print(i)
    pyautogui.press('enter')

    check_for_2(picture["save"], 0)

    if not check_for_2(picture["print"], 5):
        try:
            print('Could not print result for' + firstname + ", " + lastname + "at: " + datetime.datetime.now())
        except Exception as e:
            print(f"Error: {e}")

    if not check_for_2(picture["print_ok"], 2):
        pyautogui.press('tab', presses=2)
        pyautogui.press('enter')

    time.sleep(2)
    pyautogui.write(lastname + "," + firstname + "_" + str(datetime.datetime.now()).replace(" ", "").replace(":", ""))
    pyautogui.press('enter')

    check_for_2(picture["close"], 3)

    if not check_for_2(picture["remove_Patient"], 5):
        pyautogui.press('tab', presses=26)
        pyautogui.press('enter')

    pyautogui.press('enter')


def main(usr_id):
    get_data(usr_id)
    automate_registration()
    # Start the countdown slideshow
    start_countdown_slideshow(WAITING_TIME)
    # time.sleep(10)
    automate_test()  # test starten
