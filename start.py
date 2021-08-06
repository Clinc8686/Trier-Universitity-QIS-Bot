import datetime
import sys
import mechanize
import re
import requests
import os.path

global username, password, modulnumbers, filepath, discord_webhook_url, ifttt_url
filepath = os.getcwd()

username = ''   #REQUIRED! set your QIS-Username to login
password = ''    #REQUIRED! set your QIS-Password to login

#REQUIRED! add below your modulnumbers for which you want to get notified
modulnumbers = ["9971", "9973", "5551", "5484", "9977", "5485", "5455", "24562", "38593", "38595", "38597", "38599", "38601", "38603", "38605", "9999", "10021", "10025", "8230", "13886", "13888"]  #Modulnummern aus QIS

#REQUIRED! add below your discord webhook link like 'https://discord.com/api/webhooks/number/alphanumeric'
#How to create a Discord-Webhook? -> https://youtu.be/6t3UyMJYeso
discord_webhook_url = ''

#OPTIONAL! add below your ifttt-webrequest to get notified like 'https://maker.ifttt.com/trigger/your_values/with/key/number'
ifttt_url = ''

def main():
    now = datetime.datetime.now()
    if now.hour >= 0 and not now.hour <= 5: #Ist aktuelle Uhrzeit zwischen 0 und 5 Uhr? Dazwischen ist QIS abgeschaltet
        br = mechanize.Browser()
        br.set_handle_equiv(True)
        br.set_handle_gzip(True)
        br.set_handle_redirect(True)
        br.set_handle_referer(True)
        br.set_handle_robots(False)
        br.set_handle_refresh(True)
        mechanize.Browser().handlers
        br.set_handle_redirect(mechanize.HTTPRedirectHandler)
        br.clear_history()

        br.open("https://qis.hochschule-trier.de/qisserver/rds?state=user&type=0&category=menu.browse&startpage=portal.vm")     #1. Anmeldeseite öffnen: Hochschul-Seite
        br.select_form(nr=0)
        br.form['j_username'] = username
        br.form['j_password'] = password
        br.submit()

        br.open("https://qis.hochschule-trier.de/qisserver/rds?state=user&amp;type=1&amp;category=auth.login&amp;startpage=portal.vm&amp;breadCrumbSource=portal")  #Irgendeine Hochschul-Seite zum setzen der Session & Cookies
        br.open("https://qis.hochschule-trier.de/qisserver/rds?state=user&type=0")  #Weiterleitung folgen
        br.select_form(nr=0)
        br.submit()

        br.open("https://qis.hochschule-trier.de/qisserver/rds?state=user&type=0&category=menu.browse&startpage=portal.vm") #2. Anmeldeseite öffnen: QIS'
        br.select_form('loginform')
        br.form['asdf'] = username
        br.form['fdsa'] = password
        br.submit()
        br.open("https://qis.hochschule-trier.de/qisserver/rds?state=user&type=0&category=menu.browse&startpage=portal.vm")     #Öffne QIS Startseite

        for l in br.links():
            if l.text == 'Prüfungsverwaltung':
                br.follow_link(l)   #Folge Reiter Prüfungsverwaltung

        for l in br.links():
            if l.text == 'Notenspiegel':
                br.follow_link(l)   #Folge Reiter Notenspiegel

        for l in br.links():
            if l.text == 'Abschluss Bachelor of Science':
                br.follow_link(l)   #Folge Reiter Abschluss Bachelor of Science

        for l in br.links():
            if l.text == 'Informatik - Digitale Medien und Spiele (PO-Version 2019)':
                r6 = br.follow_link(l)  #Folge Reiter Informatik - Digitale Medien und Spiele (PO-Version 2019)

        all_tr_tags_list = re.findall('<tr>([\S\s]*?)<\/tr>', str(r6.read())) #Schneide alle <tr> Tags aus & pack in Liste -> Einzelnen Module
        all_list = []

        for tr_tag in all_tr_tags_list: #durchläuft Tag-Liste
            tmp = tr_tag
            tmp = tmp.encode().decode("utf-8")  #decodet noch mal wegen Zeichen
            cleaner = re.compile('<.*?>')       #Compiliere nachfolgenden Command
            tmp = re.sub(cleaner, '', tmp)      #Alle html Tags entfernen
            tmp = tmp.replace('\\t', '').replace('\\n', '') #Ersetze alle \t & \n durch Leerzeichen
            tmp = ' '.join(tmp.split())     #Ersetze mehrfache Leerzeichen, durch ein einzelnes
            all_list.append(tmp)    #Füge zu neuer Liste hinzu, da auf alte kein Zugriff bei der Schleife

        i = 0
        while i < 10:   #Entferne ersten 9 Einträge mit Name, Studiengang etc.
            all_list.pop(0)
            i += 1

        all_list = all_list[:len(all_list)-9]   #Entferne letzten 9 Einträge mit Legendenübersicht, & Hinweisen

        for modul in all_list:
            if modul.find("Studienleistung") != -1:  # Entferne alle Prüfungsvorleistungen
                all_list.remove(modul)

        for modul in all_list:
            if modul.find("PV") != -1:  # Entferne alle Prüfungsvorleistungen
                all_list.remove(modul)

        for modul in all_list:
            if modul.find("PV") != -1 or modul.find("AN") != -1:    #Sollte PV übrig bleiben, hier ignorieren
                pass
            elif modul.find("BE") != -1 or modul.find("NB") != -1:  #Schaue ob BEstandener oder NichtBestander Eintrag
                if now.month >= 10 or now.month <= 4:   #Haben wir Oktober-April?
                    if now.month >= 10 and now.month <= 12:
                        semester = "WiSe " + str(now.year)[len(str(now.year))//2:]+"/"+(int(str(now.year)[len(str(now.year))//2:]) + 1)   #Dann "WiSe Altes Jahr/Neues Jahr"
                    else:
                        semester = "WiSe " + str(now.year)[len(str(now.year)) // 2:] + "/" + (int(str(now.year)[len(str(now.year)) // 2:]) - 1)  # Dann "WiSe Neues Jahr/Altes Jahr"
                else:
                    semester = "SoSe " + str(now.year)[len(str(now.year))//2:]  #Dann nicht, "SoSe Aktuelles Jahr"
                if any(y in modul for y in modulnumbers) and modul.find(semester) != -1:    #Finde aktuelles Semesterjahr in Modulübersicht
                    if os.path.isfile(filepath+"\Klausur_log.txt") == False:    #Prüfe ob Datei zur speicherung der Prüfungen existiert
                        f = open(filepath+"\Klausur_log.txt", "w")         #Wenn nicht, erstelle Datei
                        f.write("")
                        f.close()
                    with open(filepath+"\Klausur_log.txt") as f:      #Öffne Datei & lese Zeilenweise ein
                        if (semester + ": " + modul.split(semester)[0]) in f.read():    #Prüfe ob in Datei schon das Semester + Klausurname existiert
                            pass    #Wenn existiert, überspringe Klausur, da keine neue Benachrichtigung nötig
                        else:
                            f2 = open(filepath+"\Klausur_log.txt", "a+")   #Klausur existiert noch nicht, schreibe Klausur in Datei
                            f2.write(semester + ": " + modul.split(semester)[0])
                            f2.close()

                            ifttt_request(modul, semester)
                            discord_webhook(modul, semester)
                    f.close()
        br.close()

def ifttt_request(modul, semester):
    if not ifttt_url:   #Ist ifttt_request gesetzt?
        pass
    else:
        param = {'value1': modul.split(semester)[0]}
        requests.post(ifttt_url, param)  # Wenn ja, sende IFTTT Webrequest

def discord_webhook(modul, semester):
        dis_param = {'content': '@everyone **' + semester + ": " + modul.split(semester)[0] + 'Noten sind online!**'}
        requests.post(discord_webhook_url, dis_param)  # Sende Discord Webhook

if __name__ == "__main__":
    if not password:    #Prüfe ob passwort gesetzt
        sys.exit('Password is not set!')
    if not username:    #Prüfe ob username gesetzt
        sys.exit('Username is not set!')
    if not modulnumbers:    #Prüfe ob modulnummern gesetzt
        sys.exit('No Modulnumbers set!')
    if not discord_webhook_url: #Prüfe ob discord-webhook gesetzt
        sys.exit('No Discord-Webhook set!')

    main()