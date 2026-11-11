"""Generate a fictional, structured sample PDF for trying out and evaluating tinyrag.

The content is invented on purpose: an LLM cannot know these facts from its
training data, so a correct answer proves that retrieval worked.

Usage:
    uv run python scripts/make_sample_pdf.py [output_path]
"""

import io
import sys
from pathlib import Path

import pymupdf

DEFAULT_OUTPUT = Path("data/pdfs/nordlicht_handbuch.pdf")
PAGE_HEADER = "Nordlicht Robotik GmbH - Mitarbeiterhandbuch (Stand: März 2026)"
MARGIN = 72  # 1 inch in PDF points

CSS = """
body { font-family: sans-serif; font-size: 10.5pt; }
h1 { font-size: 18pt; font-weight: bold; margin-top: 18pt; }
h2 { font-size: 13pt; font-weight: bold; margin-top: 10pt; }
p, li { margin-bottom: 6pt; }
"""

HTML = """
<h1>1 Über Nordlicht Robotik</h1>

<h2>1.1 Unternehmensprofil</h2>
<p>Die Nordlicht Robotik GmbH wurde 2014 in Kiel von Dr. Hanna Petersen und Jonas Brandt
gegründet. Das Unternehmen entwickelt autonome Unterwasser-Inspektionsroboter für
Offshore-Windparks. Das bekannteste Produkt ist die Roboterserie „Seehund", deren aktuelle
Generation Seehund S4 Fundamente und Kabeltrassen bis in 120 Meter Tiefe prüfen kann.</p>
<p>Derzeit beschäftigt Nordlicht Robotik 142 Mitarbeitende. Geschäftsführerin ist
Dr. Hanna Petersen, Jonas Brandt verantwortet als technischer Leiter (CTO) die Entwicklung.</p>

<h2>1.2 Standorte</h2>
<p>Der Hauptsitz befindet sich am Hörnkai 7 in Kiel. Dort sind Verwaltung, Entwicklung und
Fertigung untergebracht. Seit 2021 betreibt das Unternehmen eine Außenstelle im dänischen
Esbjerg mit 18 Mitarbeitenden, die vor allem Wartung und Einsatzplanung für Kunden in der
Nordsee übernimmt. Ersatzteile und Einsatzausrüstung lagern in einem Logistikzentrum in
Rendsburg.</p>

<h1>2 Arbeitszeit und Urlaub</h1>

<h2>2.1 Arbeitszeit</h2>
<p>Bei Nordlicht Robotik gilt Vertrauensarbeitszeit bei einer regulären Wochenarbeitszeit
von 38 Stunden. Von Montag bis Donnerstag gilt eine Kernzeit von 10:00 bis 15:00 Uhr,
am Freitag von 10:00 bis 13:00 Uhr. Innerhalb der Kernzeit sollen alle Mitarbeitenden
erreichbar sein. Überstunden werden im Zeiterfassungsportal „Kompass" erfasst und können
in Freizeit ausgeglichen werden.</p>

<h2>2.2 Urlaub</h2>
<p>Alle Mitarbeitenden haben Anspruch auf 30 Urlaubstage pro Kalenderjahr. Zusätzlich sind
der 24. und der 31. Dezember arbeitsfrei. Urlaubsanträge werden mindestens drei Wochen
im Voraus über das Portal „Kompass" gestellt und von der direkten Führungskraft genehmigt.</p>
<p>Nicht genommener Urlaub kann bis zu einer Höhe von 15 Tagen in das Folgejahr übertragen
werden. Übertragener Urlaub muss bis zum 31. März des Folgejahres genommen werden, sonst
verfällt er.</p>

<h2>2.3 Mobiles Arbeiten</h2>
<p>Mobiles Arbeiten ist an bis zu drei Tagen pro Woche möglich, sofern die Tätigkeit es
zulässt. Für die Einrichtung eines Arbeitsplatzes zu Hause zahlt das Unternehmen einmalig
eine Ausstattungspauschale von 600 Euro. Mitarbeitende in der Fertigung sind von dieser
Regelung ausgenommen.</p>

<h1>3 Reisen und Spesen</h1>

<h2>3.1 Reisekosten</h2>
<p>Dienstreisen mit der Bahn werden in der 2. Klasse gebucht; ab einer einfachen Fahrzeit von
vier Stunden ist die 1. Klasse erlaubt. Flüge werden ausschließlich in der Economy-Klasse
gebucht und müssen vorab von der Bereichsleitung genehmigt werden.</p>
<p>Die Hotelkosten dürfen 140 Euro pro Nacht nicht übersteigen. Für Übernachtungen in
Esbjerg gilt abweichend eine Obergrenze von 1.100 Dänischen Kronen pro Nacht.</p>

<h2>3.2 Offshore-Einsätze</h2>
<p>Für jeden Tag auf See erhalten Mitarbeitende eine Offshore-Zulage von 85 Euro zusätzlich
zum regulären Gehalt. Ein Offshore-Einsatz dauert höchstens 14 Tage am Stück; danach ist
eine Ruhephase an Land von mindestens 7 Tagen vorgeschrieben.</p>
<p>Voraussetzung für jeden Einsatz ist ein gültiges Sicherheitstraining für Offshore-Arbeiten
sowie eine aktuelle arbeitsmedizinische Untersuchung, die nicht älter als zwei Jahre ist.
Die Einsatzplanung erfolgt über die Außenstelle Esbjerg.</p>

<h2>3.3 Abrechnung</h2>
<p>Reisekosten werden innerhalb von 30 Tagen nach Ende der Reise über das Portal „Kompass"
abgerechnet. Alle Belege werden digital hochgeladen; Originalbelege müssen nicht
aufbewahrt werden. Die Erstattung erfolgt mit der nächsten Gehaltsabrechnung.</p>

<h1>4 IT und Sicherheit</h1>

<h2>4.1 Passwörter und Zugänge</h2>
<p>Passwörter müssen mindestens 14 Zeichen lang sein. Für alle Firmenkonten ist die
Zwei-Faktor-Authentifizierung verpflichtend. Zugangsdaten werden ausschließlich im
firmeneigenen Passwortmanager gespeichert und niemals per E-Mail oder Chat weitergegeben.</p>

<h2>4.2 Wartungsfenster</h2>
<p>Am ersten Dienstag jedes Monats findet zwischen 18:00 und 22:00 Uhr das planmäßige
Wartungsfenster statt. In dieser Zeit sind das Portal „Kompass" und der interne Git-Server
nicht erreichbar. Kurzfristige Notfallwartungen kündigt das IT-Team mindestens zwei Stunden
vorher per E-Mail an.</p>

<h2>4.3 Sicherheitsvorfälle</h2>
<p>Bei einem Verdacht auf einen Sicherheitsvorfall, etwa einer Phishing-Mail oder einem
verlorenen Laptop, ist wie folgt vorzugehen:</p>
<ol>
<li>Das betroffene Gerät sofort vom Netzwerk trennen, aber nicht ausschalten.</li>
<li>Den Vorfall innerhalb von einer Stunde an security@nordlicht-robotik.example melden.</li>
<li>Außerhalb der Geschäftszeiten zusätzlich die Sicherheits-Hotline unter der
Durchwahl 999 anrufen.</li>
</ol>

<h1>5 Ansprechpartner</h1>
<p>Für Fragen zu Urlaub, Gehalt und Verträgen ist die Personalabteilung zuständig;
Ansprechpartnerin ist Miriam Okafor (Durchwahl 210). Technische Probleme meldet man dem
IT-Support-Team „Leuchtturm" (Durchwahl 300). Vorsitzender des Betriebsrats ist
Ole Christiansen (Durchwahl 250).</p>
"""


def render_story(html: str) -> bytes:
    """Lay out HTML across as many A4 pages as needed and return the PDF bytes."""
    buffer = io.BytesIO()
    writer = pymupdf.DocumentWriter(buffer)
    story = pymupdf.Story(html=html, user_css=CSS)
    page_rect = pymupdf.paper_rect("a4")
    content_rect = page_rect + (MARGIN, MARGIN, -MARGIN, -MARGIN)

    more_content = True
    while more_content:
        device = writer.begin_page(page_rect)
        more_content, _ = story.place(content_rect)
        story.draw(device)
        writer.end_page()
    writer.close()
    return buffer.getvalue()


def add_header_and_footer(pdf_bytes: bytes) -> pymupdf.Document:
    """Stamp a running header and page numbers - the kind of noise real PDFs have."""
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    for number, page in enumerate(doc, start=1):
        page.insert_text((MARGIN, 40), PAGE_HEADER, fontsize=8)
        footer = f"Seite {number} von {doc.page_count}"
        page.insert_text((MARGIN, page.rect.height - 30), footer, fontsize=8)
    return doc


def main() -> None:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUTPUT
    output.parent.mkdir(parents=True, exist_ok=True)
    doc = add_header_and_footer(render_story(HTML))
    doc.save(output)
    print(f"Wrote {output} ({doc.page_count} pages)")


if __name__ == "__main__":
    main()
