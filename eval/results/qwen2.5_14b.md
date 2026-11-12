# Evaluation results

LLM `qwen2.5:14b` · Embeddings `bge-m3` · top_k 5 · 12 questions

| Metric | Result |
|---|---|
| Retrieval Hit@1 | 9/10 (90%) |
| Retrieval Hit@5 | 10/10 (100%) |
| Correct answers | 8/12 (67%) |
| Avg. answer time | 20.8 s |

## Details

| # | Category | Question | Expected | Answer | Rank | OK |
|---|---|---|---|---|---|---|
| 1 | Direkter Fakt | Wie viele Urlaubstage habe ich im Jahr? | 30 Tage, zusätzlich 24. und 31. Dezember frei | Alle Mitarbeitenden haben Anspruch auf 30 Urlaubstage pro Kalenderjahr. [1] | 1 | ✅ |
| 2 | Direkter Fakt | Wie lang muss ein Passwort mindestens sein? | 14 Zeichen | Ein Passwort muss mindestens 14 Zeichen lang sein. [1] | 1 | ✅ |
| 3 | Umformuliert | Kann ich von zu Hause arbeiten, und kriege ich dafür Geld? | Ja, bis zu 3 Tage pro Woche; einmalig 600 Euro Ausstattungspauschale | Ja, mobiles Arbeiten ist an bis zu drei Tagen pro Woche möglich und das Unternehmen zahlt einmalig eine Ausstattungspauschale von 600 Euro für die Einrichtung eines Arbeitsplatzes zu Hause. [1] | 1 | ✅ |
| 4 | Umformuliert | Wen rufe ich an, wenn mein Rechner nicht geht? | IT-Support-Team „Leuchtturm“, Durchwahl 300 | Dazu finde ich in den Dokumenten keine Information. | 2 | ❌ |
| 5 | Umgangssprache | Kann ich Resturlaub ins nächste Jahr schieben? | Ja, bis zu 15 Tage; muss bis 31. März genommen werden | Ja, nicht genommener Urlaub kann bis zu einer Höhe von 15 Tagen in das Folgejahr übertragen werden. [1] | 1 | ❌ |
| 6 | Detail/Ausnahme | Darf ich als Mitarbeiter in der Fertigung mobil arbeiten? | Nein, die Fertigung ist von der Regelung ausgenommen | Mitarbeitende in der Fertigung sind von der Regelung für mobiles Arbeiten ausgenommen. [1] | 1 | ✅ |
| 7 | Zeitbezug | Wie schnell muss ich eine Phishing-Mail melden? | Innerhalb von einer Stunde an security@nordlicht-robotik.example | Den Vorfall innerhalb von einer Stunde an security@nordlicht-robotik.example melden.[1] | 1 | ✅ |
| 8 | Rechnen | Wie viel Offshore-Zulage bekomme ich maximal für einen einzelnen Einsatz am Stück? | 14 Tage × 85 Euro = 1.190 Euro | Für jeden Tag auf See erhalten Mitarbeitende eine Offshore-Zulage von 85 Euro zusätzlich zum regulären Gehalt. Ein Offshore-Einsatz dauert höchstens 14 Tage am Stück; danach ist eine Ruhephase an Land von mindestens 7 Tagen vorgeschrieben.<br><br>Maximal für einen einzelnen Einsatz am Stück bekommst du also eine Offshore-Zulage von 85 Euro pro Tag, wenn der Einsatz 14 Tage dauert. [1] | 1 | ❌ |
| 9 | Zwei Abschnitte | Über welches Portal rechne ich Reisekosten ab, und wann ist es wegen Wartung nicht erreichbar? | Kompass; am ersten Dienstag im Monat von 18 bis 22 Uhr | Reisekosten werden über das Portal „Kompass" abgerechnet. Dieses Portal ist am ersten Dienstag jedes Monats zwischen 18:00 und 22:00 Uhr aufgrund von Wartungsarbeiten nicht erreichbar.<br><br>Quellen:<br>[1]<br>[2] | 1, 2 | ✅ |
| 10 | Falsche Annahme | Warum wurde die Außenstelle in Esbjerg 2019 eröffnet? | Korrektur: eröffnet 2021; ein Grund wird nicht genannt (Aufgabe: Wartung und Einsatzplanung) | Dazu finde ich in den Dokumenten keine Information. | 1 | ❌ |
| 11 | Keine Antwort | Gibt es einen Zuschuss zum Mittagessen? | Steht nicht im Dokument | Dazu finde ich in den Dokumenten keine Information. | n/a | ✅ |
| 12 | Keine Antwort (verlockend) | Wie viele Tage Sonderurlaub bekomme ich zu meiner Hochzeit? | Steht nicht im Dokument (nur regulärer Urlaub ist geregelt) | Dazu finde ich in den Dokumenten keine Information. | n/a | ✅ |
