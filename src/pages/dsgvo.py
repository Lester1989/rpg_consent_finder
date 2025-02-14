import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")
dsgvo_css = """
body {
  font-family: Arial, sans-serif;
  line-height: 1.6;
  margin: 0;
  padding: 10px;
  background-color: #f4f4f4;
}

h1, h2, h3 {
  color: #333;
}

h1 {
  font-size: 2em;
  margin-bottom: 0.5em;
}

h2 {
  font-size: 1.5em;
  margin-top: 1em;
  margin-bottom: 0.5em;
}

h3 {
  font-size: 1.2em;
  margin-top: 1em;
  margin-bottom: 0.5em;
}

p {
  margin: 0.5em 0;
}

ul {
  list-style-type: none;
  padding: 0;
}

ul.index {
  margin: 1em 0;
}

ul.index li {
  margin: 0.5em 0;
}

ul.index li a {
  text-decoration: none;
  color: #007BFF;
}

ul.index li a:hover {
  text-decoration: underline;
}

ul.m-elements {
  margin: 1em 0;
  padding-left: 1em;
}

ul.m-elements li {
  margin: 0.5em 0;
}

ul.glossary {
  margin: 1em 0;
  padding-left: 1em;
}

ul.glossary li {
  margin: 0.5em 0;
}

strong {
  font-weight: bold;
}

a {
  color: #007BFF;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

.seal {
  margin-top: 2em;
  text-align: center;
}

.seal a {
  color: #007BFF;
  text-decoration: none;
}

.seal a:hover {
  text-decoration: underline;
}
"""

dsgvo_html = f"""
<html>
<head>
  <title>Datenschutzerklärung</title>
  <style>
    {dsgvo_css}
  </style>
</head>

<body>
<a href="{BASE_URL}/faq">Zurück zur FAQ</a>
<h1>Datenschutzerklärung</h1>
<h2 id="m4158">Präambel</h2>
<p>
  Mit der folgenden Datenschutzerklärung möchten wir Sie darüber aufklären,
  welche Arten Ihrer personenbezogenen Daten (nachfolgend auch kurz als "Daten"
  bezeichnet) wir zu welchen Zwecken und in welchem Umfang im Rahmen der
  Bereitstellung unserer Applikation verarbeiten.
</p>
<p>Die verwendeten Begriffe sind nicht geschlechtsspezifisch.</p>

<p>Stand: 14. Februar 2025</p>
<h2>Inhaltsübersicht</h2>
<ul class="index">
  <li><a class="index-link" href="#m4158">Präambel</a></li>
  <li><a class="index-link" href="#m3">Verantwortlicher</a></li>
  <li>
    <a class="index-link" href="#mOverview">Übersicht der Verarbeitungen</a>
  </li>
  <li><a class="index-link" href="#m2427">Maßgebliche Rechtsgrundlagen</a></li>
  <li>
    <a class="index-link" href="#m12"
      >Allgemeine Informationen zur Datenspeicherung und Löschung</a
    >
  </li>
  <li><a class="index-link" href="#m10">Rechte der betroffenen Personen</a></li>
  <li>
    <a class="index-link" href="#m225"
      >Bereitstellung des Onlineangebots und Webhosting</a
    >
  </li>
  <li>
    <a class="index-link" href="#m367"
      >Registrierung, Anmeldung und Nutzerkonto</a
    >
  </li>
  <li><a class="index-link" href="#m432">Community Funktionen</a></li>
  <li><a class="index-link" href="#m451">Single-Sign-On-Anmeldung</a></li>
  <li>
    <a class="index-link" href="#m328"
      >Plug-ins und eingebettete Funktionen sowie Inhalte</a
    >
  </li>
  <li><a class="index-link" href="#m15">Änderung und Aktualisierung</a></li>
  <li><a class="index-link" href="#m42">Begriffsdefinitionen</a></li>
</ul>
<h2 id="m3">Verantwortlicher</h2>
<p>Lukas Jaspaert<br />Jürgingsmühle 9<br />33739 Bielefeld</p>
<p>E-Mail-Adresse: <a href="mailto:l.ester@gmx.de">l.ester@gmx.de</a></p>
<p>
  Impressum:
  <a
    href="https://content-consent-finder.lesterserver.de/impressum"
    target="_blank"
    >https://content-consent-finder.lesterserver.de/impressum</a
  >
</p>

<h2 id="mOverview">Übersicht der Verarbeitungen</h2>
<p>
  Die nachfolgende Übersicht fasst die Arten der verarbeiteten Daten und die
  Zwecke ihrer Verarbeitung zusammen und verweist auf die betroffenen Personen.
</p>
<h3>Arten der verarbeiteten Daten</h3>
<ul>
  <li>Bestandsdaten.</li>
  <li>Kontaktdaten.</li>
  <li>Inhaltsdaten.</li>
  <li>Nutzungsdaten.</li>
  <li>Meta-, Kommunikations- und Verfahrensdaten.</li>
  <li>Protokolldaten.</li>
</ul>
<h3>Kategorien betroffener Personen</h3>
<ul>
  <li>Nutzer.</li>
</ul>
<h3>Zwecke der Verarbeitung</h3>
<ul>
  <li>
    Erbringung vertraglicher Leistungen und Erfüllung vertraglicher Pflichten.
  </li>
  <li>Sicherheitsmaßnahmen.</li>
  <li>Organisations- und Verwaltungsverfahren.</li>
  <li>Anmeldeverfahren.</li>
  <li>Bereitstellung unseres Onlineangebotes und Nutzerfreundlichkeit.</li>
  <li>Informationstechnische Infrastruktur.</li>
</ul>
<h2 id="m2427">Maßgebliche Rechtsgrundlagen</h2>
<p>
  <strong>Maßgebliche Rechtsgrundlagen nach der DSGVO: </strong>Im Folgenden
  erhalten Sie eine Übersicht der Rechtsgrundlagen der DSGVO, auf deren Basis
  wir personenbezogene Daten verarbeiten. Bitte nehmen Sie zur Kenntnis, dass
  neben den Regelungen der DSGVO nationale Datenschutzvorgaben in Ihrem bzw.
  unserem Wohn- oder Sitzland gelten können. Sollten ferner im Einzelfall
  speziellere Rechtsgrundlagen maßgeblich sein, teilen wir Ihnen diese in der
  Datenschutzerklärung mit.
</p>
<ul>
  <li>
    <strong>Einwilligung (Art. 6 Abs. 1 S. 1 lit. a) DSGVO)</strong> - Die
    betroffene Person hat ihre Einwilligung in die Verarbeitung der sie
    betreffenden personenbezogenen Daten für einen spezifischen Zweck oder
    mehrere bestimmte Zwecke gegeben.
  </li>
  <li>
    <strong
      >Vertragserfüllung und vorvertragliche Anfragen (Art. 6 Abs. 1 S. 1 lit.
      b) DSGVO)</strong
    >
    - Die Verarbeitung ist für die Erfüllung eines Vertrags, dessen
    Vertragspartei die betroffene Person ist, oder zur Durchführung
    vorvertraglicher Maßnahmen erforderlich, die auf Anfrage der betroffenen
    Person erfolgen.
  </li>
  <li>
    <strong>Berechtigte Interessen (Art. 6 Abs. 1 S. 1 lit. f) DSGVO)</strong> -
    die Verarbeitung ist zur Wahrung der berechtigten Interessen des
    Verantwortlichen oder eines Dritten notwendig, vorausgesetzt, dass die
    Interessen, Grundrechte und Grundfreiheiten der betroffenen Person, die den
    Schutz personenbezogener Daten verlangen, nicht überwiegen.
  </li>
</ul>
<p>
  <strong>Nationale Datenschutzregelungen in Deutschland: </strong>Zusätzlich zu
  den Datenschutzregelungen der DSGVO gelten nationale Regelungen zum
  Datenschutz in Deutschland. Hierzu gehört insbesondere das Gesetz zum Schutz
  vor Missbrauch personenbezogener Daten bei der Datenverarbeitung
  (Bundesdatenschutzgesetz – BDSG). Das BDSG enthält insbesondere
  Spezialregelungen zum Recht auf Auskunft, zum Recht auf Löschung, zum
  Widerspruchsrecht, zur Verarbeitung besonderer Kategorien personenbezogener
  Daten, zur Verarbeitung für andere Zwecke und zur Übermittlung sowie
  automatisierten Entscheidungsfindung im Einzelfall einschließlich Profiling.
  Ferner können Landesdatenschutzgesetze der einzelnen Bundesländer zur
  Anwendung gelangen.
</p>
<p>
  <strong>Hinweis auf Geltung DSGVO und Schweizer DSG: </strong>Diese
  Datenschutzhinweise dienen sowohl der Informationserteilung nach dem Schweizer
  DSG als auch nach der Datenschutzgrundverordnung (DSGVO). Aus diesem Grund
  bitten wir Sie zu beachten, dass aufgrund der breiteren räumlichen Anwendung
  und Verständlichkeit die Begriffe der DSGVO verwendet werden. Insbesondere
  statt der im Schweizer DSG verwendeten Begriffe „Bearbeitung" von
  „Personendaten", "überwiegendes Interesse" und "besonders schützenswerte
  Personendaten" werden die in der DSGVO verwendeten Begriffe „Verarbeitung" von
  „personenbezogenen Daten" sowie "berechtigtes Interesse" und "besondere
  Kategorien von Daten" verwendet. Die gesetzliche Bedeutung der Begriffe wird
  jedoch im Rahmen der Geltung des Schweizer DSG weiterhin nach dem Schweizer
  DSG bestimmt.
</p>

<h2 id="m12">Allgemeine Informationen zur Datenspeicherung und Löschung</h2>
<p>
  Wir löschen personenbezogene Daten, die wir verarbeiten, gemäß den
  gesetzlichen Bestimmungen, sobald die zugrundeliegenden Einwilligungen
  widerrufen werden oder keine weiteren rechtlichen Grundlagen für die
  Verarbeitung bestehen. Dies betrifft Fälle, in denen der ursprüngliche
  Verarbeitungszweck entfällt oder die Daten nicht mehr benötigt werden.
  Ausnahmen von dieser Regelung bestehen, wenn gesetzliche Pflichten oder
  besondere Interessen eine längere Aufbewahrung oder Archivierung der Daten
  erfordern.
</p>
<p>
  Insbesondere müssen Daten, die aus handels- oder steuerrechtlichen Gründen
  aufbewahrt werden müssen oder deren Speicherung notwendig ist zur
  Rechtsverfolgung oder zum Schutz der Rechte anderer natürlicher oder
  juristischer Personen, entsprechend archiviert werden.
</p>
<p>
  Unsere Datenschutzhinweise enthalten zusätzliche Informationen zur
  Aufbewahrung und Löschung von Daten, die speziell für bestimmte
  Verarbeitungsprozesse gelten.
</p>
<p>
  Bei mehreren Angaben zur Aufbewahrungsdauer oder Löschungsfristen eines
  Datums, ist stets die längste Frist maßgeblich.
</p>
<p>
  Beginnt eine Frist nicht ausdrücklich zu einem bestimmten Datum und beträgt
  sie mindestens ein Jahr, so startet sie automatisch am Ende des
  Kalenderjahres, in dem das fristauslösende Ereignis eingetreten ist. Im Fall
  laufender Vertragsverhältnisse, in deren Rahmen Daten gespeichert werden, ist
  das fristauslösende Ereignis der Zeitpunkt des Wirksamwerdens der Kündigung
  oder sonstige Beendigung des Rechtsverhältnisses.
</p>
<p>
  Daten, die nicht mehr für den ursprünglich vorgesehenen Zweck, sondern
  aufgrund gesetzlicher Vorgaben oder anderer Gründe aufbewahrt werden,
  verarbeiten wir ausschließlich zu den Gründen, die ihre Aufbewahrung
  rechtfertigen.
</p>
<p>
  <strong
    >Weitere Hinweise zu Verarbeitungsprozessen, Verfahren und Diensten:</strong
  >
</p>
<ul class="m-elements">
  <li>
    <strong>Aufbewahrung und Löschung von Daten: </strong>Die folgenden
    allgemeinen Fristen gelten für die Aufbewahrung und Archivierung nach
    deutschem Recht:
    <ul>
      <li>
        10 Jahre - Aufbewahrungsfrist für Bücher und Aufzeichnungen,
        Jahresabschlüsse, Inventare, Lageberichte, Eröffnungsbilanz sowie die zu
        ihrem Verständnis erforderlichen Arbeitsanweisungen und sonstigen
        Organisationsunterlagen (§ 147 Abs. 1 Nr. 1 i.V.m. Abs. 3 AO, § 14b Abs.
        1 UStG, § 257 Abs. 1 Nr. 1 i.V.m. Abs. 4 HGB).
      </li>
      <li>
        8 Jahre - Buchungsbelege, wie z. B. Rechnungen und Kostenbelege (§ 147
        Abs. 1 Nr. 4 und 4a i.V.m. Abs. 3 Satz 1 AO sowie § 257 Abs. 1 Nr. 4
        i.V.m. Abs. 4 HGB).
      </li>
      <li>
        6 Jahre - Übrige Geschäftsunterlagen: empfangene Handels- oder
        Geschäftsbriefe, Wiedergaben der abgesandten Handels- oder
        Geschäftsbriefe, sonstige Unterlagen, soweit sie für die Besteuerung von
        Bedeutung sind, z. B. Stundenlohnzettel, Betriebsabrechnungsbögen,
        Kalkulationsunterlagen, Preisauszeichnungen, aber auch
        Lohnabrechnungsunterlagen, soweit sie nicht bereits Buchungsbelege sind
        und Kassenstreifen (§ 147 Abs. 1 Nr. 2, 3, 5 i.V.m. Abs. 3 AO, § 257
        Abs. 1 Nr. 2 u. 3 i.V.m. Abs. 4 HGB).
      </li>
      <li>
        3 Jahre - Daten, die erforderlich sind, um potenzielle Gewährleistungs-
        und Schadensersatzansprüche oder ähnliche vertragliche Ansprüche und
        Rechte zu berücksichtigen sowie damit verbundene Anfragen zu bearbeiten,
        basierend auf früheren Geschäftserfahrungen und üblichen
        Branchenpraktiken, werden für die Dauer der regulären gesetzlichen
        Verjährungsfrist von drei Jahren gespeichert (§§ 195, 199 BGB).
      </li>
    </ul>
  </li>
</ul>
<h2 id="m10">Rechte der betroffenen Personen</h2>
<p>
  Rechte der betroffenen Personen aus der DSGVO: Ihnen stehen als Betroffene
  nach der DSGVO verschiedene Rechte zu, die sich insbesondere aus Art. 15 bis
  21 DSGVO ergeben:
</p>
<ul>
  <li>
    <strong
      >Widerspruchsrecht: Sie haben das Recht, aus Gründen, die sich aus Ihrer
      besonderen Situation ergeben, jederzeit gegen die Verarbeitung der Sie
      betreffenden personenbezogenen Daten, die aufgrund von Art. 6 Abs. 1 lit.
      e oder f DSGVO erfolgt, Widerspruch einzulegen; dies gilt auch für ein auf
      diese Bestimmungen gestütztes Profiling. Werden die Sie betreffenden
      personenbezogenen Daten verarbeitet, um Direktwerbung zu betreiben, haben
      Sie das Recht, jederzeit Widerspruch gegen die Verarbeitung der Sie
      betreffenden personenbezogenen Daten zum Zwecke derartiger Werbung
      einzulegen; dies gilt auch für das Profiling, soweit es mit solcher
      Direktwerbung in Verbindung steht.</strong
    >
  </li>
  <li>
    <strong>Widerrufsrecht bei Einwilligungen:</strong> Sie haben das Recht,
    erteilte Einwilligungen jederzeit zu widerrufen.
  </li>
  <li>
    <strong>Auskunftsrecht:</strong> Sie haben das Recht, eine Bestätigung
    darüber zu verlangen, ob betreffende Daten verarbeitet werden und auf
    Auskunft über diese Daten sowie auf weitere Informationen und Kopie der
    Daten entsprechend den gesetzlichen Vorgaben.
  </li>
  <li>
    <strong>Recht auf Berichtigung:</strong> Sie haben entsprechend den
    gesetzlichen Vorgaben das Recht, die Vervollständigung der Sie betreffenden
    Daten oder die Berichtigung der Sie betreffenden unrichtigen Daten zu
    verlangen.
  </li>
  <li>
    <strong>Recht auf Löschung und Einschränkung der Verarbeitung:</strong> Sie
    haben nach Maßgabe der gesetzlichen Vorgaben das Recht, zu verlangen, dass
    Sie betreffende Daten unverzüglich gelöscht werden, bzw. alternativ nach
    Maßgabe der gesetzlichen Vorgaben eine Einschränkung der Verarbeitung der
    Daten zu verlangen.
  </li>
  <li>
    <strong>Recht auf Datenübertragbarkeit:</strong> Sie haben das Recht, Sie
    betreffende Daten, die Sie uns bereitgestellt haben, nach Maßgabe der
    gesetzlichen Vorgaben in einem strukturierten, gängigen und
    maschinenlesbaren Format zu erhalten oder deren Übermittlung an einen
    anderen Verantwortlichen zu fordern.
  </li>
  <li>
    <strong>Beschwerde bei Aufsichtsbehörde:</strong> Sie haben unbeschadet
    eines anderweitigen verwaltungsrechtlichen oder gerichtlichen Rechtsbehelfs
    das Recht auf Beschwerde bei einer Aufsichtsbehörde, insbesondere in dem
    Mitgliedstaat ihres gewöhnlichen Aufenthaltsorts, ihres Arbeitsplatzes oder
    des Orts des mutmaßlichen Verstoßes, wenn Sie der Ansicht sind, dass die
    Verarbeitung der Sie betreffenden personenbezogenen Daten gegen die Vorgaben
    der DSGVO verstößt.
  </li>
</ul>

<h2 id="m225">Bereitstellung des Onlineangebots und Webhosting</h2>
<p>
  Wir verarbeiten die Daten der Nutzer, um ihnen unsere Online-Dienste zur
  Verfügung stellen zu können. Zu diesem Zweck verarbeiten wir die IP-Adresse
  des Nutzers, die notwendig ist, um die Inhalte und Funktionen unserer
  Online-Dienste an den Browser oder das Endgerät der Nutzer zu übermitteln.
</p>
<ul class="m-elements">
  <li>
    <strong>Verarbeitete Datenarten:</strong> Nutzungsdaten (z. B. Seitenaufrufe
    und Verweildauer, Klickpfade, Nutzungsintensität und -frequenz, verwendete
    Gerätetypen und Betriebssysteme, Interaktionen mit Inhalten und Funktionen);
    Meta-, Kommunikations- und Verfahrensdaten (z. B. IP-Adressen, Zeitangaben,
    Identifikationsnummern, beteiligte Personen). Protokolldaten (z. B. Logfiles
    betreffend Logins oder den Abruf von Daten oder Zugriffszeiten.).
  </li>
  <li>
    <strong>Betroffene Personen:</strong> Nutzer (z. B. Webseitenbesucher,
    Nutzer von Onlinediensten).
  </li>
  <li>
    <strong>Zwecke der Verarbeitung:</strong> Bereitstellung unseres
    Onlineangebotes und Nutzerfreundlichkeit; Informationstechnische
    Infrastruktur (Betrieb und Bereitstellung von Informationssystemen und
    technischen Geräten (Computer, Server etc.)). Sicherheitsmaßnahmen.
  </li>
  <li>
    <strong>Aufbewahrung und Löschung:</strong> Löschung entsprechend Angaben im
    Abschnitt "Allgemeine Informationen zur Datenspeicherung und Löschung".
  </li>
  <li class="">
    <strong>Rechtsgrundlagen:</strong> Berechtigte Interessen (Art. 6 Abs. 1 S.
    1 lit. f) DSGVO).
  </li>
</ul>
<p>
  <strong
    >Weitere Hinweise zu Verarbeitungsprozessen, Verfahren und Diensten:</strong
  >
</p>
<ul class="m-elements">
  <li>
    <strong>Bereitstellung Onlineangebot auf gemietetem Speicherplatz: </strong
    >Für die Bereitstellung unseres Onlineangebotes nutzen wir Speicherplatz,
    Rechenkapazität und Software, die wir von einem entsprechenden
    Serveranbieter (auch "Webhoster" genannt) mieten oder anderweitig beziehen;
    <span class=""
      ><strong>Rechtsgrundlagen:</strong> Berechtigte Interessen (Art. 6 Abs. 1
      S. 1 lit. f) DSGVO).</span
    >
  </li>
  <li>
    <strong>Erhebung von Zugriffsdaten und Logfiles: </strong>Der Zugriff auf
    unser Onlineangebot wird in Form von sogenannten "Server-Logfiles"
    protokolliert. Zu den Serverlogfiles können die Adresse und der Name der
    abgerufenen Webseiten und Dateien, Datum und Uhrzeit des Abrufs, übertragene
    Datenmengen, Meldung über erfolgreichen Abruf, Browsertyp nebst Version, das
    Betriebssystem des Nutzers, Referrer URL (die zuvor besuchte Seite) und im
    Regelfall IP-Adressen und der anfragende Provider gehören. Die
    Serverlogfiles können zum einen zu Sicherheitszwecken eingesetzt werden,
    z. B. um eine Überlastung der Server zu vermeiden (insbesondere im Fall von
    missbräuchlichen Angriffen, sogenannten DDoS-Attacken), und zum anderen, um
    die Auslastung der Server und ihre Stabilität sicherzustellen;
    <span class=""
      ><strong>Rechtsgrundlagen:</strong> Berechtigte Interessen (Art. 6 Abs. 1
      S. 1 lit. f) DSGVO). </span
    ><strong>Löschung von Daten:</strong> Logfile-Informationen werden für die
    Dauer von maximal 30 Tagen gespeichert und danach gelöscht oder
    anonymisiert. Daten, deren weitere Aufbewahrung zu Beweiszwecken
    erforderlich ist, sind bis zur endgültigen Klärung des jeweiligen Vorfalls
    von der Löschung ausgenommen.
  </li>
  <li>
    <strong>netcup: </strong>Leistungen auf dem Gebiet der Bereitstellung von
    informationstechnischer Infrastruktur und verbundenen Dienstleistungen
    (z. B. Speicherplatz und/oder Rechenkapazitäten);
    <strong>Dienstanbieter:</strong> netcup GmbH, Daimlerstraße 25, D-76185
    Karlsruhe, Deutschland;
    <span class=""
      ><strong>Rechtsgrundlagen:</strong> Berechtigte Interessen (Art. 6 Abs. 1
      S. 1 lit. f) DSGVO); </span
    ><strong>Website:</strong>
    <a href="https://www.netcup.de/" target="_blank">https://www.netcup.de/</a>;
    <strong>Datenschutzerklärung:</strong>
    <a
      href="https://www.netcup.de/kontakt/datenschutzerklaerung.php"
      target="_blank"
      >https://www.netcup.de/kontakt/datenschutzerklaerung.php</a
    >. <strong>Auftragsverarbeitungsvertrag:</strong>
    <a href="https://helpcenter.netcup.com/de/wiki/general/avv/" target="_blank"
      >https://helpcenter.netcup.com/de/wiki/general/avv/</a
    >.
  </li>
</ul>
<h2 id="m367">Registrierung, Anmeldung und Nutzerkonto</h2>
<p>
  Nutzer können ein Nutzerkonto anlegen. Im Rahmen der Registrierung werden den
  Nutzern die erforderlichen Pflichtangaben mitgeteilt und zu Zwecken der
  Bereitstellung des Nutzerkontos auf Grundlage vertraglicher Pflichterfüllung
  verarbeitet. Zu den verarbeiteten Daten gehören insbesondere die
  Login-Informationen (Nutzername, Passwort sowie eine E-Mail-Adresse).
</p>
<p>
  Im Rahmen der Inanspruchnahme unserer Registrierungs- und Anmeldefunktionen
  sowie der Nutzung des Nutzerkontos speichern wir die IP-Adresse und den
  Zeitpunkt der jeweiligen Nutzerhandlung. Die Speicherung erfolgt auf Grundlage
  unserer berechtigten Interessen als auch jener der Nutzer an einem Schutz vor
  Missbrauch und sonstiger unbefugter Nutzung. Eine Weitergabe dieser Daten an
  Dritte erfolgt grundsätzlich nicht, es sei denn, sie ist zur Verfolgung
  unserer Ansprüche erforderlich oder es besteht eine gesetzliche Verpflichtung
  hierzu.
</p>
<p>
  Die Nutzer können über Vorgänge, die für deren Nutzerkonto relevant sind, wie
  z. B. technische Änderungen, per E-Mail informiert werden.
</p>
<ul class="m-elements">
  <li>
    <strong>Verarbeitete Datenarten:</strong> Bestandsdaten (z. B. der
    vollständige Name, Wohnadresse, Kontaktinformationen, Kundennummer, etc.);
    Kontaktdaten (z. B. Post- und E-Mail-Adressen oder Telefonnummern);
    Inhaltsdaten (z. B. textliche oder bildliche Nachrichten und Beiträge sowie
    die sie betreffenden Informationen, wie z. B. Angaben zur Autorenschaft oder
    Zeitpunkt der Erstellung); Nutzungsdaten (z. B. Seitenaufrufe und
    Verweildauer, Klickpfade, Nutzungsintensität und -frequenz, verwendete
    Gerätetypen und Betriebssysteme, Interaktionen mit Inhalten und Funktionen).
    Protokolldaten (z. B. Logfiles betreffend Logins oder den Abruf von Daten
    oder Zugriffszeiten.).
  </li>
  <li>
    <strong>Betroffene Personen:</strong> Nutzer (z. B. Webseitenbesucher,
    Nutzer von Onlinediensten).
  </li>
  <li>
    <strong>Zwecke der Verarbeitung:</strong> Erbringung vertraglicher
    Leistungen und Erfüllung vertraglicher Pflichten; Sicherheitsmaßnahmen;
    Organisations- und Verwaltungsverfahren. Bereitstellung unseres
    Onlineangebotes und Nutzerfreundlichkeit.
  </li>
  <li>
    <strong>Aufbewahrung und Löschung:</strong> Löschung entsprechend Angaben im
    Abschnitt "Allgemeine Informationen zur Datenspeicherung und Löschung".
    Löschung nach Kündigung.
  </li>
  <li class="">
    <strong>Rechtsgrundlagen:</strong> Vertragserfüllung und vorvertragliche
    Anfragen (Art. 6 Abs. 1 S. 1 lit. b) DSGVO). Berechtigte Interessen (Art. 6
    Abs. 1 S. 1 lit. f) DSGVO).
  </li>
</ul>
<p>
  <strong
    >Weitere Hinweise zu Verarbeitungsprozessen, Verfahren und Diensten:</strong
  >
</p>
<ul class="m-elements">
  <li>
    <strong>Registrierung mit Pseudonymen: </strong>Nutzer dürfen statt
    Klarnamen Pseudonyme als Nutzernamen verwenden;
    <span class=""
      ><strong>Rechtsgrundlagen:</strong> Vertragserfüllung und vorvertragliche
      Anfragen (Art. 6 Abs. 1 S. 1 lit. b) DSGVO).</span
    >
  </li>
</ul>
<h2 id="m432">Community Funktionen</h2>
<p>
  Die von uns bereitgestellten Community Funktionen erlauben es Nutzern
  miteinander in Konversationen oder sonst miteinander in einen Austausch zu
  treten. Hierbei bitten wir zu beachten, dass die Nutzung der
  Communityfunktionen nur unter Beachtung der geltenden Rechtslage, unserer
  Bedingungen und Richtlinien sowie der Rechte anderer Nutzer und Dritter
  gestattet ist.
</p>
<ul class="m-elements">
  <li>
    <strong>Verarbeitete Datenarten:</strong> Bestandsdaten (z. B. der
    vollständige Name, Wohnadresse, Kontaktinformationen, Kundennummer, etc.).
    Nutzungsdaten (z. B. Seitenaufrufe und Verweildauer, Klickpfade,
    Nutzungsintensität und -frequenz, verwendete Gerätetypen und
    Betriebssysteme, Interaktionen mit Inhalten und Funktionen).
  </li>
  <li>
    <strong>Betroffene Personen:</strong> Nutzer (z. B. Webseitenbesucher,
    Nutzer von Onlinediensten).
  </li>
  <li>
    <strong>Zwecke der Verarbeitung:</strong> Erbringung vertraglicher
    Leistungen und Erfüllung vertraglicher Pflichten; Sicherheitsmaßnahmen.
    Bereitstellung unseres Onlineangebotes und Nutzerfreundlichkeit.
  </li>
  <li>
    <strong>Aufbewahrung und Löschung:</strong> Löschung entsprechend Angaben im
    Abschnitt "Allgemeine Informationen zur Datenspeicherung und Löschung".
  </li>
  <li class="">
    <strong>Rechtsgrundlagen:</strong> Vertragserfüllung und vorvertragliche
    Anfragen (Art. 6 Abs. 1 S. 1 lit. b) DSGVO). Berechtigte Interessen (Art. 6
    Abs. 1 S. 1 lit. f) DSGVO).
  </li>
</ul>
<p>
  <strong
    >Weitere Hinweise zu Verarbeitungsprozessen, Verfahren und Diensten:</strong
  >
</p>
<ul class="m-elements">
  <li>
    <strong>Einstellung der Sichtbarkeit von Beiträgen: </strong>Die Nutzer
    können mittels Einstellungen bestimmen, in welchem Umfang die von ihnen
    erstellten Beiträge und Inhalte für die Öffentlichkeit oder nur für
    bestimmte Personen oder Gruppen sichtbar, bzw. zugänglich sind;
    <span class=""
      ><strong>Rechtsgrundlagen:</strong> Vertragserfüllung und vorvertragliche
      Anfragen (Art. 6 Abs. 1 S. 1 lit. b) DSGVO).</span
    >
  </li>
  <li>
    <strong>Recht zur Löschung von Inhalten und Informationen: </strong>Die
    Löschung von Beiträgen, Inhalten oder Angaben der Nutzer ist nach einer
    sachgerechten Abwägung im erforderlichen Umfang zulässig soweit konkrete
    Anhaltspunkte dafür bestehen, dass sie einen Verstoß gegen gesetzliche
    Regeln, unsere Vorgaben oder Rechte Dritter darstellen;
    <span class=""
      ><strong>Rechtsgrundlagen:</strong> Vertragserfüllung und vorvertragliche
      Anfragen (Art. 6 Abs. 1 S. 1 lit. b) DSGVO).</span
    >
  </li>
</ul>
<h2 id="m451">Single-Sign-On-Anmeldung</h2>
<p>
  Als "Single-Sign-On" oder "Single-Sign-On-Anmeldung bzw. "-Authentifizierung"
  werden Verfahren bezeichnet, die es Nutzern erlauben, sich mit Hilfe eines
  Nutzerkontos bei einem Anbieter von Single-Sign-On-Verfahren (z. B. einem
  sozialen Netzwerk), auch bei unserem Onlineangebot, anzumelden. Voraussetzung
  der Single-Sign-On-Authentifizierung ist, dass die Nutzer bei dem jeweiligen
  Single-Sign-On-Anbieter registriert sind und die erforderlichen Zugangsdaten
  in dem dafür vorgesehenen Onlineformular eingeben, bzw. schon bei dem
  Single-Sign-On-Anbieter angemeldet sind und die Single-Sign-On-Anmeldung via
  Schaltfläche bestätigen.
</p>
<p>
  Die Authentifizierung erfolgt direkt bei dem jeweiligen
  Single-Sign-On-Anbieter. Im Rahmen einer solchen Authentifizierung erhalten
  wir eine Nutzer-ID mit der Information, dass der Nutzer unter dieser Nutzer-ID
  beim jeweiligen Single-Sign-On-Anbieter eingeloggt ist und eine für uns für
  andere Zwecke nicht weiter nutzbare ID (sog "User Handle"). Ob uns zusätzliche
  Daten übermittelt werden, hängt allein von dem genutzten
  Single-Sign-On-Verfahren ab, von den gewählten Datenfreigaben im Rahmen der
  Authentifizierung und zudem davon, welche Daten Nutzer in den Privatsphäre-
  oder sonstigen Einstellungen des Nutzerkontos beim Single-Sign-On-Anbieter
  freigegeben haben. Es können je nach Single-Sign-On-Anbieter und der Wahl der
  Nutzer verschiedene Daten sein, in der Regel sind es die E-Mail-Adresse und
  der Benutzername. Das im Rahmen des Single-Sign-On-Verfahrens eingegebene
  Passwort bei dem Single-Sign-On-Anbieter ist für uns weder einsehbar, noch
  wird es von uns gespeichert.
</p>
<p>
  Die Nutzer werden gebeten, zu beachten, dass deren bei uns gespeicherte
  Angaben automatisch mit ihrem Nutzerkonto beim Single-Sign-On-Anbieter
  abgeglichen werden können, dies jedoch nicht immer möglich ist oder
  tatsächlich erfolgt. Ändern sich z. B. die E-Mail-Adressen der Nutzer, müssen
  sie diese manuell in ihrem Nutzerkonto bei uns ändern.
</p>
<p>
  Die Single-Sign-On-Anmeldung können wir, sofern mit den Nutzern vereinbart, im
  Rahmen der oder vor der Vertragserfüllung einsetzen, soweit die Nutzer darum
  gebeten wurden, im Rahmen einer Einwilligung verarbeiten und setzen sie
  ansonsten auf Grundlage der berechtigten Interessen unsererseits und der
  Interessen der Nutzer an einem effektiven und sicheren Anmeldesystem ein.
</p>
<p>
  Sollten Nutzer sich einmal entscheiden, die Verknüpfung ihres Nutzerkontos
  beim Single-Sign-On-Anbieter nicht mehr für das Single-Sign-On-Verfahren
  nutzen zu wollen, müssen sie diese Verbindung innerhalb ihres Nutzerkontos
  beim Single-Sign-On-Anbieter aufheben. Möchten Nutzer deren Daten bei uns
  löschen, müssen sie ihre Registrierung bei uns kündigen.
</p>
<ul class="m-elements">
  <li>
    <strong>Verarbeitete Datenarten:</strong> Bestandsdaten (z. B. der
    vollständige Name, Wohnadresse, Kontaktinformationen, Kundennummer, etc.);
    Kontaktdaten (z. B. Post- und E-Mail-Adressen oder Telefonnummern);
    Nutzungsdaten (z. B. Seitenaufrufe und Verweildauer, Klickpfade,
    Nutzungsintensität und -frequenz, verwendete Gerätetypen und
    Betriebssysteme, Interaktionen mit Inhalten und Funktionen). Meta-,
    Kommunikations- und Verfahrensdaten (z. B. IP-Adressen, Zeitangaben,
    Identifikationsnummern, beteiligte Personen).
  </li>
  <li>
    <strong>Betroffene Personen:</strong> Nutzer (z. B. Webseitenbesucher,
    Nutzer von Onlinediensten).
  </li>
  <li>
    <strong>Zwecke der Verarbeitung:</strong> Erbringung vertraglicher
    Leistungen und Erfüllung vertraglicher Pflichten; Sicherheitsmaßnahmen;
    Anmeldeverfahren. Bereitstellung unseres Onlineangebotes und
    Nutzerfreundlichkeit.
  </li>
  <li>
    <strong>Aufbewahrung und Löschung:</strong> Löschung entsprechend Angaben im
    Abschnitt "Allgemeine Informationen zur Datenspeicherung und Löschung".
    Löschung nach Kündigung.
  </li>
  <li class="">
    <strong>Rechtsgrundlagen:</strong> Vertragserfüllung und vorvertragliche
    Anfragen (Art. 6 Abs. 1 S. 1 lit. b) DSGVO). Berechtigte Interessen (Art. 6
    Abs. 1 S. 1 lit. f) DSGVO).
  </li>
</ul>
<p>
  <strong
    >Weitere Hinweise zu Verarbeitungsprozessen, Verfahren und Diensten:</strong
  >
</p>
<ul class="m-elements">
  <li>
    <strong>Google Single-Sign-On: </strong>Authentifizierungsdienste für
    Nutzeranmeldungen, Bereitstellung von Single Sign-On-Funktionen, Verwaltung
    von Identitätsinformationen und Anwendungsintegrationen;
    <strong>Dienstanbieter:</strong> Google Ireland Limited, Gordon House,
    Barrow Street, Dublin 4, Irland;
    <span class=""
      ><strong>Rechtsgrundlagen:</strong> Berechtigte Interessen (Art. 6 Abs. 1
      S. 1 lit. f) DSGVO); </span
    ><strong>Website:</strong>
    <a href="https://www.google.de" target="_blank">https://www.google.de</a>;
    <strong>Datenschutzerklärung:</strong>
    <a href="https://policies.google.com/privacy" target="_blank"
      >https://policies.google.com/privacy</a
    >; <strong>Grundlage Drittlandtransfers:</strong> Data Privacy Framework
    (DPF). <strong>Widerspruchsmöglichkeit (Opt-Out):</strong> Einstellungen für
    die Darstellung von Werbeeinblendungen:
    <a href="https://myadcenter.google.com/" target="_blank"
      >https://myadcenter.google.com/</a
    >.
  </li>
  <li>
    <strong>OpenID Single-Sign-On: </strong>Authentifizierungsdienste für
    Nutzeranmeldungen, Bereitstellung von Single Sign-On-Funktionen, Verwaltung
    von Identitätsinformationen und Anwendungsintegrationen;
    <strong>Dienstanbieter:</strong> OpenID Foundation, 2400 Camino Ramon, Suite
    375, San Ramon, CA 94583, USA;
    <span class=""
      ><strong>Rechtsgrundlagen:</strong> Berechtigte Interessen (Art. 6 Abs. 1
      S. 1 lit. f) DSGVO); </span
    ><strong>Website:</strong>
    <a href="https://openid.net" target="_blank">https://openid.net</a>;
    <strong>Datenschutzerklärung:</strong>
    <a href="https://openid.net/policies/" target="_blank"
      >https://openid.net/policies/</a
    >. <strong>Grundlage Drittlandtransfers:</strong> Data Privacy Framework
    (DPF).
  </li>
</ul>
<h2 id="m328">Plug-ins und eingebettete Funktionen sowie Inhalte</h2>
<p>
  Wir binden Funktions- und Inhaltselemente in unser Onlineangebot ein, die von
  den Servern ihrer jeweiligen Anbieter (nachfolgend als „Drittanbieter"
  bezeichnet) bezogen werden. Dabei kann es sich zum Beispiel um Grafiken,
  Videos oder Stadtpläne handeln (nachfolgend einheitlich als „Inhalte"
  bezeichnet).
</p>
<p>
  Die Einbindung setzt immer voraus, dass die Drittanbieter dieser Inhalte die
  IP-Adresse der Nutzer verarbeiten, da sie ohne IP-Adresse die Inhalte nicht an
  deren Browser senden könnten. Die IP-Adresse ist damit für die Darstellung
  dieser Inhalte oder Funktionen erforderlich. Wir bemühen uns, nur solche
  Inhalte zu verwenden, deren jeweilige Anbieter die IP-Adresse lediglich zur
  Auslieferung der Inhalte anzuwenden. Drittanbieter können ferner sogenannte
  Pixel-Tags (unsichtbare Grafiken, auch als „Web Beacons" bezeichnet) für
  statistische oder Marketingzwecke einsetzen. Durch die „Pixel-Tags" können
  Informationen, wie etwa der Besucherverkehr auf den Seiten dieser Website,
  ausgewertet werden. Die pseudonymen Informationen können darüber hinaus in
  Cookies auf dem Gerät der Nutzer gespeichert werden und unter anderem
  technische Auskünfte zum Browser und zum Betriebssystem, zu verweisenden
  Websites, zur Besuchszeit sowie weitere Angaben zur Nutzung unseres
  Onlineangebots enthalten, aber auch mit solchen Informationen aus anderen
  Quellen verbunden werden.
</p>
<p>
  <strong>Hinweise zu Rechtsgrundlagen:</strong> Sofern wir die Nutzer um ihre
  Einwilligung in den Einsatz der Drittanbieter bitten, stellt die
  Rechtsgrundlage der Datenverarbeitung die Erlaubnis dar. Ansonsten werden die
  Nutzerdaten auf Grundlage unserer berechtigten Interessen (d. h. Interesse an
  effizienten, wirtschaftlichen und empfängerfreundlichen Leistungen)
  verarbeitet. In diesem Zusammenhang möchten wir Sie auch auf die Informationen
  zur Verwendung von Cookies in dieser Datenschutzerklärung hinweisen.
</p>
<ul class="m-elements">
  <li>
    <strong>Verarbeitete Datenarten:</strong> Nutzungsdaten (z. B. Seitenaufrufe
    und Verweildauer, Klickpfade, Nutzungsintensität und -frequenz, verwendete
    Gerätetypen und Betriebssysteme, Interaktionen mit Inhalten und Funktionen).
    Meta-, Kommunikations- und Verfahrensdaten (z. B. IP-Adressen, Zeitangaben,
    Identifikationsnummern, beteiligte Personen).
  </li>
  <li>
    <strong>Betroffene Personen:</strong> Nutzer (z. B. Webseitenbesucher,
    Nutzer von Onlinediensten).
  </li>
  <li>
    <strong>Zwecke der Verarbeitung:</strong> Bereitstellung unseres
    Onlineangebotes und Nutzerfreundlichkeit.
  </li>
  <li>
    <strong>Aufbewahrung und Löschung:</strong> Löschung entsprechend Angaben im
    Abschnitt "Allgemeine Informationen zur Datenspeicherung und Löschung".
    Speicherung von Cookies von bis zu 2 Jahren (Sofern nicht anders angegeben,
    können Cookies und ähnliche Speichermethoden für einen Zeitraum von zwei
    Jahren auf den Geräten der Nutzer gespeichert werden.).
  </li>
  <li class="">
    <strong>Rechtsgrundlagen:</strong> Einwilligung (Art. 6 Abs. 1 S. 1 lit. a)
    DSGVO). Berechtigte Interessen (Art. 6 Abs. 1 S. 1 lit. f) DSGVO).
  </li>
</ul>
<p>
  <strong
    >Weitere Hinweise zu Verarbeitungsprozessen, Verfahren und Diensten:</strong
  >
</p>
<ul class="m-elements">
  <li>
    <strong
      >Einbindung von Drittsoftware, Skripten oder Frameworks (z. B. jQuery): </strong
    >Wir binden in unser Onlineangebot Software ein, die wir von Servern anderer
    Anbieter abrufen (z. B. Funktions-Bibliotheken, die wir zwecks Darstellung
    oder Nutzerfreundlichkeit unseres Onlineangebotes verwenden). Hierbei
    erheben die jeweiligen Anbieter die IP-Adresse der Nutzer und können diese
    zu Zwecken der Übermittlung der Software an den Browser der Nutzer sowie zu
    Zwecken der Sicherheit, als auch zur Auswertung und Optimierung ihres
    Angebotes verarbeiten. - Wir binden in unser Onlineangebot Software ein, die
    wir von Servern anderer Anbieter abrufen (z. B. Funktions-Bibliotheken, die
    wir zwecks Darstellung oder Nutzerfreundlichkeit unseres Onlineangebotes
    verwenden). Hierbei erheben die jeweiligen Anbieter die IP-Adresse der
    Nutzer und können diese zu Zwecken der Übermittlung der Software an den
    Browser der Nutzer sowie zu Zwecken der Sicherheit, als auch zur Auswertung
    und Optimierung ihres Angebotes verarbeiten;
    <span class=""
      ><strong>Rechtsgrundlagen:</strong> Berechtigte Interessen (Art. 6 Abs. 1
      S. 1 lit. f) DSGVO).</span
    >
  </li>
  <li>
    <strong>Google Fonts (Bezug vom Google Server): </strong>Bezug von Schriften
    (und Symbolen) zum Zwecke einer technisch sicheren, wartungsfreien und
    effizienten Nutzung von Schriften und Symbolen im Hinblick auf Aktualität
    und Ladezeiten, deren einheitliche Darstellung und Berücksichtigung
    möglicher lizenzrechtlicher Beschränkungen. Dem Anbieter der Schriftarten
    wird die IP-Adresse des Nutzers mitgeteilt, damit die Schriftarten im
    Browser des Nutzers zur Verfügung gestellt werden können. Darüber hinaus
    werden technische Daten (Spracheinstellungen, Bildschirmauflösung,
    Betriebssystem, verwendete Hardware) übermittelt, die für die Bereitstellung
    der Schriften in Abhängigkeit von den verwendeten Geräten und der
    technischen Umgebung notwendig sind. Diese Daten können auf einem Server des
    Anbieters der Schriftarten in den USA verarbeitet werden - Beim Besuch
    unseres Onlineangebotes senden die Browser der Nutzer ihre Browser
    HTTP-Anfragen an die Google Fonts Web API (d. h. eine Softwareschnittstelle
    für den Abruf der Schriftarten). Die Google Fonts Web API stellt den Nutzern
    die Cascading Style Sheets (CSS) von Google Fonts und danach die in der CCS
    angegebenen Schriftarten zur Verfügung. Zu diesen HTTP-Anfragen gehören (1)
    die vom jeweiligen Nutzer für den Zugriff auf das Internet verwendete
    IP-Adresse, (2) die angeforderte URL auf dem Google-Server und (3) die
    HTTP-Header, einschließlich des User-Agents, der die Browser- und
    Betriebssystemversionen der Websitebesucher beschreibt, sowie die
    Verweis-URL (d. h. die Webseite, auf der die Google-Schriftart angezeigt
    werden soll). IP-Adressen werden weder auf Google-Servern protokolliert noch
    gespeichert und sie werden nicht analysiert. Die Google Fonts Web API
    protokolliert Details der HTTP-Anfragen (angeforderte URL, User-Agent und
    Verweis-URL). Der Zugriff auf diese Daten ist eingeschränkt und streng
    kontrolliert. Die angeforderte URL identifiziert die Schriftfamilien, für
    die der Nutzer Schriftarten laden möchte. Diese Daten werden protokolliert,
    damit Google bestimmen kann, wie oft eine bestimmte Schriftfamilie
    angefordert wird. Bei der Google Fonts Web API muss der User-Agent die
    Schriftart anpassen, die für den jeweiligen Browsertyp generiert wird. Der
    User-Agent wird in erster Linie zum Debugging protokolliert und verwendet,
    um aggregierte Nutzungsstatistiken zu generieren, mit denen die Beliebtheit
    von Schriftfamilien gemessen wird. Diese zusammengefassten
    Nutzungsstatistiken werden auf der Seite „Analysen" von Google Fonts
    veröffentlicht. Schließlich wird die Verweis-URL protokolliert, sodass die
    Daten für die Wartung der Produktion verwendet und ein aggregierter Bericht
    zu den Top-Integrationen basierend auf der Anzahl der Schriftartenanfragen
    generiert werden kann. Google verwendet laut eigener Auskunft keine der von
    Google Fonts erfassten Informationen, um Profile von Endnutzern zu erstellen
    oder zielgerichtete Anzeigen zu schalten;
    <strong>Dienstanbieter:</strong> Google Ireland Limited, Gordon House,
    Barrow Street, Dublin 4, Irland;
    <span class=""
      ><strong>Rechtsgrundlagen:</strong> Berechtigte Interessen (Art. 6 Abs. 1
      S. 1 lit. f) DSGVO); </span
    ><strong>Website:</strong>
    <a href="https://fonts.google.com/" target="_blank"
      >https://fonts.google.com/</a
    >; <strong>Datenschutzerklärung:</strong>
    <a href="https://policies.google.com/privacy" target="_blank"
      >https://policies.google.com/privacy</a
    >; <strong>Grundlage Drittlandtransfers:</strong> Data Privacy Framework
    (DPF). <strong>Weitere Informationen:</strong>
    <a
      href="https://developers.google.com/fonts/faq/privacy?hl=de"
      target="_blank"
      >https://developers.google.com/fonts/faq/privacy?hl=de</a
    >.
  </li>
</ul>
<h2 id="m15">Änderung und Aktualisierung</h2>
<p>
  Wir bitten Sie, sich regelmäßig über den Inhalt unserer Datenschutzerklärung
  zu informieren. Wir passen die Datenschutzerklärung an, sobald die Änderungen
  der von uns durchgeführten Datenverarbeitungen dies erforderlich machen. Wir
  informieren Sie, sobald durch die Änderungen eine Mitwirkungshandlung
  Ihrerseits (z. B. Einwilligung) oder eine sonstige individuelle
  Benachrichtigung erforderlich wird.
</p>
<p>
  Sofern wir in dieser Datenschutzerklärung Adressen und Kontaktinformationen
  von Unternehmen und Organisationen angeben, bitten wir zu beachten, dass die
  Adressen sich über die Zeit ändern können und bitten die Angaben vor
  Kontaktaufnahme zu prüfen.
</p>

<h2 id="m42">Begriffsdefinitionen</h2>
<p>
  In diesem Abschnitt erhalten Sie eine Übersicht über die in dieser
  Datenschutzerklärung verwendeten Begrifflichkeiten. Soweit die
  Begrifflichkeiten gesetzlich definiert sind, gelten deren gesetzliche
  Definitionen. Die nachfolgenden Erläuterungen sollen dagegen vor allem dem
  Verständnis dienen.
</p>
<ul class="glossary">
  <li>
    <strong>Bestandsdaten:</strong> Bestandsdaten umfassen wesentliche
    Informationen, die für die Identifikation und Verwaltung von
    Vertragspartnern, Benutzerkonten, Profilen und ähnlichen Zuordnungen
    notwendig sind. Diese Daten können u.a. persönliche und demografische
    Angaben wie Namen, Kontaktinformationen (Adressen, Telefonnummern,
    E-Mail-Adressen), Geburtsdaten und spezifische Identifikatoren
    (Benutzer-IDs) beinhalten. Bestandsdaten bilden die Grundlage für jegliche
    formelle Interaktion zwischen Personen und Diensten, Einrichtungen oder
    Systemen, indem sie eine eindeutige Zuordnung und Kommunikation ermöglichen.
  </li>
  <li>
    <strong>Inhaltsdaten:</strong> Inhaltsdaten umfassen Informationen, die im
    Zuge der Erstellung, Bearbeitung und Veröffentlichung von Inhalten aller Art
    generiert werden. Diese Kategorie von Daten kann Texte, Bilder, Videos,
    Audiodateien und andere multimediale Inhalte einschließen, die auf
    verschiedenen Plattformen und Medien veröffentlicht werden. Inhaltsdaten
    sind nicht nur auf den eigentlichen Inhalt beschränkt, sondern beinhalten
    auch Metadaten, die Informationen über den Inhalt selbst liefern, wie Tags,
    Beschreibungen, Autoreninformationen und Veröffentlichungsdaten
  </li>
  <li>
    <strong>Kontaktdaten:</strong> Kontaktdaten sind essentielle Informationen,
    die die Kommunikation mit Personen oder Organisationen ermöglichen. Sie
    umfassen u.a. Telefonnummern, postalische Adressen und E-Mail-Adressen,
    sowie Kommunikationsmittel wie soziale Medien-Handles und
    Instant-Messaging-Identifikatoren.
  </li>
  <li>
    <strong>Meta-, Kommunikations- und Verfahrensdaten:</strong> Meta-,
    Kommunikations- und Verfahrensdaten sind Kategorien, die Informationen über
    die Art und Weise enthalten, wie Daten verarbeitet, übermittelt und
    verwaltet werden. Meta-Daten, auch bekannt als Daten über Daten, umfassen
    Informationen, die den Kontext, die Herkunft und die Struktur anderer Daten
    beschreiben. Sie können Angaben zur Dateigröße, dem Erstellungsdatum, dem
    Autor eines Dokuments und den Änderungshistorien beinhalten.
    Kommunikationsdaten erfassen den Austausch von Informationen zwischen
    Nutzern über verschiedene Kanäle, wie E-Mail-Verkehr, Anrufprotokolle,
    Nachrichten in sozialen Netzwerken und Chat-Verläufe, inklusive der
    beteiligten Personen, Zeitstempel und Übertragungswege. Verfahrensdaten
    beschreiben die Prozesse und Abläufe innerhalb von Systemen oder
    Organisationen, einschließlich Workflow-Dokumentationen, Protokolle von
    Transaktionen und Aktivitäten, sowie Audit-Logs, die zur Nachverfolgung und
    Überprüfung von Vorgängen verwendet werden.
  </li>
  <li>
    <strong>Nutzungsdaten:</strong> Nutzungsdaten beziehen sich auf
    Informationen, die erfassen, wie Nutzer mit digitalen Produkten,
    Dienstleistungen oder Plattformen interagieren. Diese Daten umfassen eine
    breite Palette von Informationen, die aufzeigen, wie Nutzer Anwendungen
    nutzen, welche Funktionen sie bevorzugen, wie lange sie auf bestimmten
    Seiten verweilen und über welche Pfade sie durch eine Anwendung navigieren.
    Nutzungsdaten können auch die Häufigkeit der Nutzung, Zeitstempel von
    Aktivitäten, IP-Adressen, Geräteinformationen und Standortdaten
    einschließen. Sie sind besonders wertvoll für die Analyse des
    Nutzerverhaltens, die Optimierung von Benutzererfahrungen, das
    Personalisieren von Inhalten und das Verbessern von Produkten oder
    Dienstleistungen. Darüber hinaus spielen Nutzungsdaten eine entscheidende
    Rolle beim Erkennen von Trends, Vorlieben und möglichen Problembereichen
    innerhalb digitaler Angebote
  </li>
  <li>
    <strong>Personenbezogene Daten:</strong> "Personenbezogene Daten" sind alle
    Informationen, die sich auf eine identifizierte oder identifizierbare
    natürliche Person (im Folgenden "betroffene Person") beziehen; als
    identifizierbar wird eine natürliche Person angesehen, die direkt oder
    indirekt, insbesondere mittels Zuordnung zu einer Kennung wie einem Namen,
    zu einer Kennnummer, zu Standortdaten, zu einer Online-Kennung (z. B.
    Cookie) oder zu einem oder mehreren besonderen Merkmalen identifiziert
    werden kann, die Ausdruck der physischen, physiologischen, genetischen,
    psychischen, wirtschaftlichen, kulturellen oder sozialen Identität dieser
    natürlichen Person sind.
  </li>
  <li>
    <strong>Protokolldaten:</strong> Protokolldaten sind Informationen über
    Ereignisse oder Aktivitäten, die in einem System oder Netzwerk protokolliert
    wurden. Diese Daten enthalten typischerweise Informationen wie Zeitstempel,
    IP-Adressen, Benutzeraktionen, Fehlermeldungen und andere Details über die
    Nutzung oder den Betrieb eines Systems. Protokolldaten werden oft zur
    Analyse von Systemproblemen, zur Sicherheitsüberwachung oder zur Erstellung
    von Leistungsberichten verwendet.
  </li>
  <li>
    <strong>Verantwortlicher:</strong> Als "Verantwortlicher" wird die
    natürliche oder juristische Person, Behörde, Einrichtung oder andere Stelle,
    die allein oder gemeinsam mit anderen über die Zwecke und Mittel der
    Verarbeitung von personenbezogenen Daten entscheidet, bezeichnet.
  </li>
  <li>
    <strong>Verarbeitung:</strong> "Verarbeitung" ist jeder mit oder ohne Hilfe
    automatisierter Verfahren ausgeführte Vorgang oder jede solche Vorgangsreihe
    im Zusammenhang mit personenbezogenen Daten. Der Begriff reicht weit und
    umfasst praktisch jeden Umgang mit Daten, sei es das Erheben, das Auswerten,
    das Speichern, das Übermitteln oder das Löschen.
  </li>
</ul>
<p class="seal">
  <a
    href="https://datenschutz-generator.de/"
    title="Rechtstext von Dr. Schwenke - für weitere Informationen bitte anklicken."
    target="_blank"
    rel="noopener noreferrer nofollow"
    >Erstellt mit kostenlosem Datenschutz-Generator.de von Dr. Thomas
    Schwenke</a
  >
</p>
<a href="{BASE_URL}/faq">Zurück zur FAQ</a>
</body>
</html>
"""
