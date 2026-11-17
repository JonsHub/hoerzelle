# Hörzelle – TODO

Diese Liste bündelt die offenen Punkte aus der Architekturübersicht, den bisherigen
Notizen und dem aktuellen MA33-Ablauf. Der produktive Ablauf soll für Patienten
vollautomatisch wirken; die interne Steuerung von MAICO/MA33 ist dabei der kritische
technische Teil.

## 1. MA33-Steuerung – höchste Priorität

### Aktuell gewünschter Ablauf

1. Patientendaten sind in der MA33-Maske eingetragen.
2. Der Patient sieht nur die Startoberfläche und klickt auf **Start**.
3. Das Programm aktiviert **Autotest**.
4. Nach dem Öffnen des Autotest-Bereichs aktiviert das Programm **Play**.
5. Der Test läuft. Die Python-Oberfläche legt optional einen schwarzen Hinweisbildschirm
   mit „Test läuft …“ darüber; dieser muss zum Testen ausblendbar sein.
6. Nach Testende aktiviert das Programm **Speichern & beenden**.
7. Im Bestätigungsdialog „Messwerte vom Auto-Test übernehmen?“ aktiviert es **Ja**.
8. Die Messwerte werden als XML verarbeitet, bewertet und anschließend in der
   Ergebnisübersicht/Ampel für den Patienten angezeigt.

### Bekannte Fehler

- [ ] Klick auf **Autotest** kommt nicht zuverlässig an.
- [ ] Nach der Patienten-ID bricht der Ablauf bei einem weiteren Klick ab.
- [ ] **Speichern & beenden** wird nicht zuverlässig ausgelöst.
- [ ] Der Bestätigungsdialog zur Übernahme der Messtöne muss sicher erkannt und mit
  **Ja** bestätigt werden.
- [ ] Der Testbildschirm muss sich zum Testen ausblenden lassen, ohne den eigentlichen
  Ablauf oder die MA33-Fenstersteuerung zu stören.

### Ersatz für relative Klickkoordinaten

- [ ] Relative Koordinaten nicht mehr als alleinige Erkennung verwenden. Sie sind wegen
  unterschiedlicher Monitorgrößen, Skalierung, Fensterpositionen und Auflösungen
  unzuverlässig.
- [ ] OCR-/Bildanalyse-Prototyp für die sichtbaren Beschriftungen prüfen:
  **Autotest**, **Play**, **Speichern & beenden**, **Ja**.
- [ ] Vor jedem Klick den aktuellen MA33-Zustand feststellen:
  - Hauptansicht ohne Autotest-Details (Bild 1)
  - geöffneter Autotest-Bereich mit Play/Stop und Einstellungen (Bild 2)
  - Test beendet mit Dialog zur Messwertübernahme (Bild 3)
- [ ] OCR-Erkennung auf einen zugeschnittenen Bereich des aktiven MA33-Fensters
  begrenzen; nicht den gesamten Bildschirm analysieren.
- [ ] Erkannte Textposition in eine Klickposition umwandeln und vor dem Klicken
  prüfen, dass das erwartete Label gefunden wurde.
- [ ] Nach dem Klick den Zustandswechsel verifizieren, statt nur `sleep()` zu verwenden.
- [ ] Fallback und sichtbare Fehlermeldung vorsehen, wenn OCR/Bilderkennung keinen
  eindeutigen Button findet.
- [ ] Erst einen isolierten OCR-Prototyp mit den drei vorhandenen Screenshots bauen;
  noch keine vollständige Umstellung der Produktionsautomation.

## 2. Patientenablauf und Warteschlange

- [ ] Den gescannten Patienten gezielt bis zur MAICO-Automation durchreichen. Aktuell
  darf nicht automatisch die gesamte JSON-Liste verarbeitet werden, wenn nur ein
  Patient den QR-Code gescannt hat.
- [ ] Mehrere Patienten für das Deployment sauber unterstützen, beispielsweise eine
  Liste von zehn Patienten, ohne falsche Reihenfolge oder falsche Zuordnung.
- [ ] Festlegen, ob die Patientenmaske vor dem sichtbaren Start bereits vollständig
  eingetragen wird. Ziel: Der Patient sieht die interne Python-/MAICO-Vorbereitung
  möglichst nicht.
- [ ] Patienten nach erfolgreichem Abschluss zuverlässig aus der lokalen Warteschlange
  entfernen.
- [ ] Fehlerfälle wiederholbar machen: kein Patient darf bei einem Teilfehler
  versehentlich als abgeschlossen gelten oder doppelt verarbeitet werden.

## 3. Dateien, XML und Datenzuordnung

- [ ] Sicherstellen, dass beim Start die benötigten Verzeichnisse tatsächlich erzeugt
  werden.
- [ ] Vor der Auswahl der neuesten XML-Datei prüfen, dass sie zu genau diesem
  Patienten und Testlauf gehört.
- [ ] XML-Eingang, XML-Ausgang, Umbenennung und Archivierung eindeutig definieren.
- [ ] Alte XML-/PDF-Dateien vor einem neuen Lauf erkennen oder kontrolliert archivieren.
- [ ] Temporäre PDF-Bilder auch bei Fehlern zuverlässig löschen.
- [ ] Dateinamen mit Sonderzeichen, langen Namen und ungültigen Pfadzeichen testen.
- [ ] Pfad zur MAICO-/EDV-Integration konfigurierbar machen statt fest zu verdrahten.

## 4. OCR-/GUI-Automation

- [ ] Abhängigkeit und geeignetes Verfahren festlegen: OCR für Textlabels,
  Bildvorlagen/Feature-Matching für rein grafische Elemente und Win32-Fensterinfos,
  soweit verfügbar.
- [ ] Prüfen, ob MA33-Steuerelemente über Windows-Accessibility/UI-Automation
  erreichbar sind; diese Lösung wäre robuster als Bildschirmkoordinaten.
- [ ] Windows-DPI-Skalierung und mehrere Monitorgrößen testen.
- [ ] Fenster gezielt finden, fokussieren und auf Vordergrund prüfen.
- [ ] Timeouts für Prozess-, Fokus-, Fenster- und OCR-Wartevorgänge ergänzen.
- [ ] Testmodus mit sichtbaren Markierungen der erkannten Buttons bereitstellen.
- [ ] Hardware-freien Simulationsmodus für Kamera, MAICO und MA33 ermöglichen.

## 5. Sicherheit und Fehlerbehandlung

- [ ] Datenbankzugang nicht im Quellcode hinterlegen, sondern sicher konfigurieren.
- [ ] QR-SALT und Validierungslogik aus der fest verdrahteten Implementierung herauslösen.
- [ ] JSON-, XML- und Datenbankdaten vor GUI-, Datei- und PyAutoGUI-Verwendung
  validieren.
- [ ] Breite `except`-Blöcke und leere Fehlerpfade durch konkrete Fehlerbehandlung
  und Logging ersetzen.
- [ ] Nach drei ungültigen QR-Versuchen einen definierten Bereitschafts-/Fehlerzustand
  anzeigen statt den Kiosk unkontrolliert neu zu starten.

## 6. Produktqualität und Wartbarkeit

- [ ] Zustandsmaschine für Vorbereitung, Bereitschaft, Test, Speichern, Auswertung,
  Ergebnis und Fehler einführen.
- [ ] Audiogramm-Erzeugung zwischen PDF und Ergebnis-GUI gemeinsam nutzen.
- [ ] Tests für QR-Hash, Evaluator-Grenzfälle, XML-Parsing, Dateinamen und
  Warteschlangenoperationen ergänzen.
- [ ] MAICO-/MA33-Pfade, Fenstertitel und UI-Konfiguration zentral konfigurierbar
  machen.
- [ ] `playground.py` und `db_update.py` als experimentell kennzeichnen, integrieren
  oder aus dem produktiven Verzeichnis entfernen.
- [ ] Datenbanktreiber und `requirements.txt` prüfen; SQLAlchemy und der tatsächlich
  benötigte MySQL-Treiber müssen zusammenpassen.
- [ ] Confluence-/Projektdokumentation aufräumen und den produktiven Ablauf eindeutig
  beschreiben.
