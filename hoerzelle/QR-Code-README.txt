Um einen QR-Code zu erstellen, müssen lediglich 3 Schritte erfolgen.

1. Verbindung zu FortiClient muss vorhanden sein.
2. in playground.py in TEST_CONFIG:
    "test_patient_download" und "test_qr_code_creation" auf 1 geändert werden.
3. Ausführen mit linter oder nach Änderung der Variablen 
    in hoerzelle/hoerzelle in die Addresszeile klicken
    "cmd" eingeben
    "Eingeben: python playground.py
Und der QR-Code wird mit Patienten-ID aus der Datenbank als Namen in /data/qr_codes abgespeichert.