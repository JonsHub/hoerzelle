import cv2  # pip3 install opencv-python
import sqlalchemy as db 
import datetime
import hashlib

import program


def calculate_hashes(results):
    rlist = []

    for x in range(len(results)):
        erg = []
        key = ""
        columns = [results[x][0]]

        for i in results[x]:
            key = key + str(i)
        erg.append(hashlib.sha256(key.encode()).hexdigest())
        columns.append(erg)

        rlist.append(columns)
    print(rlist)  # --debug
    return rlist


def download_appointments():
    '''should run once daily. '''

    engine = db.create_engine('mysql+pymysql://hoerzell:Abcd123$@fbi-mysqllehre.th-brandenburg.de/hoerzell_db')
    connection = engine.connect()
    metadata = db.MetaData()

    # specifying user as a Table
    user = db.Table('user', metadata, autoload=True, autoload_with=engine)
    # specifying appointment as a Table
    appointment = db.Table('appointment', metadata, autoload=True, autoload_with=engine)

    '''
    SELECT firstname, lastname, password_hash, date 
    FROM user, appointment 
    WHERE user.id=appointment.user_id && appointments.date=today
    '''
    query = db.select([user.columns.id, appointment.columns.user_id, user.columns.firstname, user.columns.lastname,
                       user.columns.password_hash, appointment.columns.date])  # appointment.columns.time_slot
    query = query.select_from(user.join(appointment, user.columns.id == appointment.columns.user_id)).where(
       appointment.columns.date == datetime.date.today())  # WHERE...

    results = connection.execute(query).fetchall()
    returnlist = calculate_hashes(results)

    return returnlist


def scan_code():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # initialize the cam
    detector = cv2.QRCodeDetector()  # initialize the cv2 QR-Code detector

    while True:
        _, img = cap.read()  # starting capture from cam
        data, bbox, _ = detector.detectAndDecode(img)

        # check if there is a QRCode in the image
        if bbox is not None:
            if data:
                print("[+] QR Code detected, data:", data)  # printing the data of the QR-Code
                return data

        # display webcam image -debug
        cv2.imshow("Camera Image", img)  # other window showing webcam view

        if cv2.waitKey(1) == ord("q"):  # stop by pressing 'q'
            break
    cap.release()
    cv2.destroyAllWindows()


def validate_code(code, app_list): #check list for code
    for x in range(0, len(app_list)):
        temp2 = app_list[x][1]
        if temp2[0].__eq__(code):
            return app_list[x][0]


def main():
    d = datetime.date.min  # datetime.date.today() - datetime.timedelta(days = 1)

    while True:
        if not d.__eq__(datetime.date.today()):
            app_list = download_appointments()
            d = datetime.date.today()
        code = scan_code()
        user = validate_code(code, app_list)

        if user is None:
            print("unknown QR-Code")
            continue  # Eintritt verweigert, weil QRCode unbekannt -> Suche nach validem Code
        else:  # Eintritt gewährt
            print("unlock doors")
            # TODO Arduinocode für Türöffnen einbinden
            print("starting the Test")
            program.main(user)  # Start automatischer Hörtest
            # TODO nach austritt von Kunde verschließen einbinden


if __name__ == "__main__":
    main()
