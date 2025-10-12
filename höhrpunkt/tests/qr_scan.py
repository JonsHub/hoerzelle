import cv2
import sqlalchemy as db
import sys

engine = db.create_engine('mysql+pymysql://hoerzell:Abcd123$@fbi-mysqllehre.th-brandenburg.de/hoerzell_db')
metadata = db.MetaData()

def get_valid_id_set():
    user_table = db.Table(
        "user",
        metadata,
        db.Column("id", db.Integer, primary_key=True),
        autoload_with=engine
    )
    valid_id_set = set()
    try:
        with engine.connect() as connection:
            query = db.select(user_table.c.id)
            result = connection.execute(query)
            for row in result:
                valid_id_set.add(str(row[0])) 
        return valid_id_set
    except Exception as e:
        print(f"Fehler beim Abrufen der Datenbank-IDs: {e}")
        sys.exit(1)


def qr_code_scanner_with_validation():
    print("--- Scanner gestartet ---")
    
    valid_id_set = get_valid_id_set() 
    
    if not valid_id_set:
        print("Keine gültigen User-IDs gefunden. Scanner beendet sich.")
        return

    qr_detector = cv2.QRCodeDetector()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Fehler: Kamera konnte nicht geöffnet werden.")
        return

    print("Richte die Kamera auf einen QR-Code. Drücke 'q' zum Beenden.")

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        retval, decoded_info, points, straight_qrcode = qr_detector.detectAndDecodeMulti(frame)

        if retval:
            for info, point_set in zip(decoded_info, points):
                if info and point_set.any():
                    decoded_id = info
                    points_int = point_set.astype(int)

                    if decoded_id in valid_id_set:
                        cv2.polylines(frame, [points_int], True, (0, 255, 0), 5)
                        cv2.putText(frame, "SUCCESS", tuple(points_int[0]), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
                    else:
                        cv2.polylines(frame, [points_int], True, (0, 0, 255), 3)
                        cv2.putText(frame, "UNKNOWN", tuple(points_int[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

                    if decoded_id in valid_id_set:
                        print("-" * 40)
                        print(f"🎉 VALIDIERUNG ERFOLGREICH! ID '{decoded_id}' gefunden.")
                        print("-" * 40)
                        cap.release()
                        cv2.destroyAllWindows()
                        return decoded_id


        cv2.imshow('QR Code Scanner', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()