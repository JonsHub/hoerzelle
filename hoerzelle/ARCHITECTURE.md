# Hörzelle – Gesamtübersicht

## 1. Kurzfassung

Die Hörzelle ist eine Windows-Kiosk-Anwendung für einen automatisierten Hörtest:

1. Patientenliste aus einer MySQL-Datenbank laden oder aus `patients.json` verwenden.
2. Einen QR-Code über die Kamera einlesen und gegen die lokale Patientenliste prüfen.
3. Den Patienten in Patientenmaske über Tastatur- und Mausklick-Automation anlegen.
4. Den Hörtest in der MA-Software starten und auf die Testfenster warten.
5. Das erzeugte XML einlesen und beide Ohren anhand einer JSON-Konfiguration bewerten.
6. Ergebnis als Ampel-GUI und PDF anzeigen.
7. Testdateien archivieren, den Patienten aus der lokalen Warteschlange entfernen und MAICO neu starten.
8. Für den nächsten Patienten wieder bei der QR-Abfrage beginnen.


## 2. Einstiegspunkt und Gesamtprogrammablauf

### Start

```text
python main.py
  -> run_kiosk()
     -> main() in einer Endlosschleife
```

`run_kiosk()` startet keinen separaten Prozess. Nach einem erfolgreichen Patientenlauf
beginnt es direkt mit dem nächsten QR-Code. Bei einem fehlgeschlagenen Lauf wartet es
fünf Sekunden und versucht es erneut.

### Patientenlauf

1. `main()` setzt drei QR-Versuche voraus.
2. `qr_code_validate.check_qr_code()` öffnet die Kamera und prüft den gelesenen Hash.
3. Bei Erfolg wird `current_patient_id` gesetzt.
4. `test_start_gui.PatientStartScreen` zeigt die Startinformationen.
5. `fill_in_patient.run_automation()` sucht MAICO und trägt aktuell die Patienten aus
   der gesamten lokalen Liste ein.
6. `hearing_test_automation.runner()` startet den Hörtest, wartet auf Beginn und Ende
   und speichert das Ergebnis.
7. Die neueste XML-Datei aus `data/saved_tests/` wird eingelesen.
8. `test_evaluator` berechnet Ampelfarben und Hochtonwarnungen.
9. `pdf_generator` erstellt einen PDF-Bericht.
10. `test_result_gui.EvaluationGUI` zeigt Ergebnis, Details und Audiogramme.
11. Das XML wird umbenannt, XML/PDF werden ins Archiv verschoben und der Patient aus
    `patients.json` entfernt.
12. `maico_handler.restart_maico()` beendet und startet `maico32.exe` neu.

## 3. Modulübersicht

| Datei | Rolle | Abhängigkeiten / Zugriffe |
|---|---|---|
| [`main.py`](./main.py) | Orchestriert den vollständigen Kioskablauf | Fast alle Kernmodule; lokale Dateien; MAICO/MA33 indirekt |
| [`paths_dir.py`](./paths_dir.py) | Zentrale Pfade; Verzeichnisse anlegen; XML-Dateien finden | Nur `pathlib`; Dateisystem |
| [`qr_code_validate.py`](./qr_code_validate.py) | QR-Code über Kamera lesen und validieren | OpenCV, `patient_manager`, `paths_dir`; Kamera |
| [`qr_code_create.py`](./qr_code_create.py) | QR-Bilder für alle Patienten erzeugen | `qrcode`, `patient_manager`, `paths_dir`; Dateisystem |
| [`patient_manager.py`](./patient_manager.py) | Patienten laden, Warteschlange verwalten, Tests archivieren | `patient_json_save`, Datenbankmodul, `paths_dir`, JSON, `shutil` |
| [`patient_database_download.py`](./patient_database_download.py) | Patientendaten aus MySQL lesen | SQLAlchemy; Datenbankserver |
| [`patient_json_save.py`](./patient_json_save.py) | Datenbankresultate in JSON serialisieren | Datenbankmodul, `paths_dir`; Dateisystem |
| [`fill_in_patient.py`](./fill_in_patient.py) | Patientendaten in MAICO-Maske eintragen und XML vorbereiten | Windows-Prozesse, PyAutoGUI, Clipboard, `gui_utils` |
| [`hearing_test_automation.py`](./hearing_test_automation.py) | Hörtest starten, überwachen und speichern | PyAutoGUI, `gui_utils`, `window_config`; MA33 |
| [`gui_utils.py`](./gui_utils.py) | Windows-Fokus, Fenstersuche, Koordinatenklicks und Wartezustände | Win32, psutil, PyAutoGUI, Tkinter |
| [`window_config.py`](./window_config.py) | Fenstertitel und relative Button-Koordinaten | Keine |
| [`test_evaluator.py`](./test_evaluator.py) | XML lesen und Messwerte bewerten | Python-XML; Konfigurationsdict |
| [`pdf_generator.py`](./pdf_generator.py) | Audiogramme und PDF-Bericht erzeugen | Matplotlib, ReportLab; `paths_dir`, `test_evaluator` |
| [`test_start_gui.py`](./test_start_gui.py) | Vollbild-Startanweisung für Patienten | Tkinter |
| [`test_result_gui.py`](./test_result_gui.py) | Vollbild-Ergebnis, Details und Audiogramme | Tkinter, Matplotlib, Pillow, `paths_dir` |
| [`generate_file_name.py`](./generate_file_name.py) | Dateinamen aus Patient und Zeitstempel bilden | JSON, `paths_dir` |
| [`maico_handler.py`](./maico_handler.py) | `maico32.exe` beenden und neu starten | `os`, `subprocess`; fest verdrahteter Windows-Pfad |
| [`db_update.py`](./db_update.py) | Separater periodischer Datenbank-/Warteschlangenlauf | `patient_manager`; nicht aus `main.py` aufgerufen |
| [`playground.py`](./playground.py) | Experimenteller bzw. älterer alternativer Ablauf | Viele Kernmodule; nicht der dokumentierte Einstiegspunkt |

## 4. Daten und Verzeichnisse

Die Pfade werden relativ zum Verzeichnis von `paths_dir.py` gebildet.

| Pfad | Inhalt | Lesen durch | Schreiben/Verschieben durch |
|---|---|---|---|
| `data/saved_patients/patients.json` | Lokale Patientenliste/Warteschlange | QR, Automation, Dateinamengenerierung, Manager | Datenbank-Download, Manager |
| `data/evaluation_config.json` | Bewertungsgrenzen | `main`, Evaluator, PDF | Manuell/Administration |
| `data/saved_tests/*.xml` | Aktuell gespeicherte MAICO-Testergebnisse | `main`, Evaluator, PDF | MAICO bzw. XML-Export |
| `data/saved_tests/*.pdf` | Aktuelle Berichte | Anzeige/Archivierung | PDF-Generator |
| `data/archive/` | Abgeschlossene XML- und PDF-Dateien | Administration | `patient_manager.move_to_test_archive` |
| `data/xml_port/in.xml` | Von der Automation erzeugte Patientendaten für MAICO | MAICO/Exportprozess | `fill_in_patient` |
| `data/xml_port/out.xml` | Konfigurierter Ausgangs-/Übergabeort | Externe Software/Administration | Nicht direkt im Hauptablauf |
| `data/qr_codes/*.png` | QR-Codes pro Patienten-ID | Ausgabe/Verteilung | `qr_code_create` |
| `images/ampel_*.png` | Ampelbilder der Ergebnis-GUI | `test_result_gui` | Manuell |
| `Test XMLS/` | Beispiel- und Test-XMLs | Manuelle Tests/Entwicklung | Manuell |

## 5. Abhängigkeits- und Zugriffsbild

```text
MySQL
  -> patient_database_download
  -> patient_json_save
  -> data/saved_patients/patients.json
       -> qr_code_create -> data/qr_codes/*.png
       -> qr_code_validate <- Kamera
       -> fill_in_patient -> MAICO32
                              -> data/xml_port/in.xml
MAICO32/MA33
  -> data/saved_tests/out.xml
  -> hearing_test_automation
  -> generate_file_name
  -> XML umbenennen
       -> test_evaluator + data/evaluation_config.json
       -> test_result_gui
       -> pdf_generator -> data/saved_tests/*.pdf
       -> patient_manager -> data/archive/
```

### Wer greift worauf zu?

- **Datenbank:** Nur `patient_database_download.py`. Die Zugangsdaten/URL werden beim
  Import des Moduls für SQLAlchemy verwendet.
- **Patienten-JSON:** `patient_manager`, `qr_code_validate`, `qr_code_create`,
  `fill_in_patient` und `generate_file_name`.
- **Kamera:** Nur `qr_code_validate`.
- **Windows-Fenster und Eingaben:** `gui_utils`, `fill_in_patient` und
  `hearing_test_automation`.
- **MAICO-Prozesse:** `fill_in_patient` wartet auf `maico32.exe`; `maico_handler`
  beendet/startet diesen Prozess. `gui_utils` und die Testautomation arbeiten mit
  `ma33.exe`.
- **Ergebnisdateien:** `main`, `hearing_test_automation`, `test_evaluator`,
  `pdf_generator` und `patient_manager`.
- **Patientenanzeige:** Die GUIs zeigen Namen bzw. Testergebnisse aus lokalen XML- und
  JSON-Daten an.

## 6. Bewertungslogik

`test_evaluator.evaluate_ears()` bewertet jedes Ohr getrennt:

- Ab `40 dB` zählt ein Messwert als rot-relevant.
- Ab `25 dB` zählt ein Messwert als gelb-relevant.
- Ab drei roten Messwerten wird das Ohr rot.
- Ein einzelner Wert ab `60 dB` löst ebenfalls gelb aus.
- Zusätzlich wird ein PTA4-Mittelwert aus 500, 1000, 2000 und 4000 Hz gebildet.
- PTA4 `< 25 dB`: grün; PTA4 `< 40 dB`: gelb; sonst rot.
- Ab zwei auffälligen Hochtonwerten aus 3000, 4000, 6000 und 8000 Hz wird die
  Hochtonwarnung angezeigt.

Die Grenzwerte stehen in [`data/evaluation_config.json`](./data/evaluation_config.json)
und werden zur Laufzeit geladen. Eine leere Ohrmessung wird derzeit als grün bewertet.

## 7. Offene Punkte und TODOs

### Priorität 1 – Korrektheit und Sicherheit

- [ ] In [`main.py`](./main.py) `paths_dir.ensure_directories_exist()` tatsächlich
  aufrufen. Aktuell wird nur das Funktionsobjekt referenziert.
- [ ] Nach drei ungültigen QR-Versuchen einen definierten Zustand herstellen:
  verständliche Benutzeranzeige, Kamera sauber schließen und entweder kontrolliert
  zum Bereitschaftsbildschirm zurückkehren oder den Lauf mit einem sichtbaren Fehler
  beenden. Aktuell gibt `main()` `False` zurück; `run_kiosk()` startet danach
  dauerhaft alle fünf Sekunden neu.
- [ ] Den gescannten `current_patient_id` bis zur Automation durchreichen. Aktuell
  verarbeitet `fill_in_patient.run_automation()` die komplette JSON-Liste und nicht
  garantiert den gescannten Patienten.
- [ ] Datenbankzugang, QR-SALT und externe Pfade aus dem Quellcode entfernen und über
  sichere Konfiguration/Umgebungsvariablen bereitstellen. Der feste SALT ist kein
  Geheimnis, wenn der Quellcode verfügbar ist.
- [ ] JSON-, XML- und Datenbankdaten validieren, bevor sie in GUIs, Dateinamen oder
  PyAutoGUI-Eingaben gelangen.

### Priorität 2 – Robustheit im Betrieb

- [ ] Keine unbestimmten Endlosschleifen ohne Timeout in Prozess-, Fokus- und
  Fenstervorgängen (`gui_utils`, `fill_in_patient`, `hearing_test_automation`).
- [ ] Vor der Auswahl der neuesten XML-Datei prüfen, dass sie zu genau diesem
  Patienten/Test gehört; alte Dateien können derzeit als Ergebnis verwendet werden.
- [ ] Dateiumbenennung, Archivierung und Patientenentfernung transaktional bzw.
  wiederholbar machen. Ein Fehler nach dem Test darf nicht zu doppelten oder
  verlorenen Läufen führen.
- [ ] Temporäre PDF-Bilder mit `try/finally` aufräumen; bei einem Fehler bleiben sie
  aktuell möglicherweise in `data/saved_tests/temp_images/`.
- [ ] `except:` und breit gefasste Exceptions durch konkrete Fehlerbehandlung und
  Logging ersetzen.
- [ ] MAICO-/MA33-Pfade, Fenstertitel und Koordinaten konfigurierbar machen und eine
  Kalibrierung bzw. Startprüfung ergänzen.

### Priorität 3 – Wartbarkeit und Tests

- [ ] Gemeinsame Audiogramm-Erzeugung von `pdf_generator` und `test_result_gui`
  extrahieren, damit Darstellung und Grenzzonen nicht auseinanderlaufen.
- [ ] Unit-Tests für QR-Hash, Evaluator-Grenzfälle, XML-Parsing,
  Dateinamengenerierung und Warteschlangenoperationen ergänzen.
- [ ] Einen Hardware-freien Simulationsmodus für Kamera, MAICO und MA33 bereitstellen.
- [ ] `playground.py` und `db_update.py` als experimentell kennzeichnen, integrieren
  oder aus dem produktiven Verzeichnis entfernen.
- [ ] Abhängigkeit `mypysql` prüfen: Der Code verwendet SQLAlchemy; der passende
  SQLAlchemy-MySQL-Treiber sollte explizit und korrekt dokumentiert sein.
- [ ] Start-, Fehler- und Abschlusszustände in einer Zustandsmaschine modellieren,
  statt den Ablauf ausschließlich über `sleep()` und implizite Fokuszustände zu steuern.

## 8. Betriebshinweise

Die Anwendung setzt aktuell mindestens voraus:

- Windows mit funktionierendem `maico32.exe` und `ma33.exe`
- Kamera auf Index `0`
- stabile Bildschirmauflösung und unveränderte MAICO-/MA33-Fenster
- Schreibrechte im Projektverzeichnis
- erreichbare MySQL-Datenbank beim erstmaligen Laden der Patienten
- installierte Python-Abhängigkeiten aus [`requirements.txt`](./requirements.txt)

Vor einem echten Patiententest sollte mindestens geprüft werden:

1. Sind MAICO und MA33 gestartet und im erwarteten Zustand?
2. Ist `patients.json` aktuell und enthält sie die erwarteten IDs?
3. Ist die Kamera verfügbar?
4. Existieren `data/evaluation_config.json` und die Ampelbilder?
5. Ist `data/saved_tests/` leer oder sind alte Testdateien eindeutig archiviert?
6. Funktionieren die in [`window_config.py`](./window_config.py) hinterlegten
   Koordinaten auf dem Zielgerät?

`paths_dir.ensure_directories_exist()` kennt alle Datenverzeichnisse außer einer
optionalen Log-Struktur. Die JSON- und Konfigurationsdateien selbst werden nicht mit
Default-Inhalten angelegt. Fehlende oder beschädigte Dateien können daher erst beim
jeweiligen Zugriff auffallen.