import datetime
import mechanize
import re
import requests

now = datetime.datetime.now()
if now.hour >= 1 and not now.hour <= 5:
    br = mechanize.Browser()
    br.set_handle_equiv(True)
    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)
    br.set_handle_refresh(True)
    mechanize.Browser().handlers
    br.set_handle_redirect(mechanize.HTTPRedirectHandler)

    br.clear_history();
    br.open("https://qis.hochschule-trier.de/qisserver/rds?state=user&type=0&category=menu.browse&startpage=portal.vm")

    br.select_form(nr=0)
    br.form['j_username'] = 'your_username'
    br.form['j_password'] = 'your_password'
    br.submit()

    br.open("https://qis.hochschule-trier.de/qisserver/rds?state=user&amp;type=1&amp;category=auth.login&amp;startpage=portal.vm&amp;breadCrumbSource=portal")
    br.open("https://qis.hochschule-trier.de/qisserver/rds?state=user&type=0")

    br.select_form(nr=0)
    br.submit()
    br.open("https://qis.hochschule-trier.de/qisserver/rds?state=user&type=0&category=menu.browse&startpage=portal.vm")

    br.select_form('loginform')
    br.form['asdf'] = 'your_username'
    br.form['fdsa'] = 'your_password'
    br.submit()
    br.open("https://qis.hochschule-trier.de/qisserver/rds?state=user&type=0&category=menu.browse&startpage=portal.vm")

    for l in br.links():
        if l.text == 'Prüfungsverwaltung':
            br.follow_link(l)

    for l in br.links():
        if l.text == 'Notenspiegel':
            br.follow_link(l)

    for l in br.links():
        if l.text == 'Abschluss Bachelor of Science':
            br.follow_link(l)

    for l in br.links():
        if l.text == 'Informatik - Digitale Medien und Spiele (PO-Version 2019)':
            r6 = br.follow_link(l)

    modulnumbers = ["modulnumbers", "modulnumbers", "modulnumbers", "modulnumbers"]  #Modulnummern aus QIS
    all_tr_tags_list = re.findall('<tr>([\S\s]*?)<\/tr>', str(r6.read())) #Schneide alle <tr> Tags in Liste
    all_list = []

    for tr_tag in all_tr_tags_list: #durchläuft Liste
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

    all_list = all_list[:len(all_list)-9]   #Entferne letzten 9 Einträge mit Abkürzungsübersicht

    i = 0
    for x in all_list:
        if x.find("(Studienleistung)") != -1:   #Entferne alle Prüfungsvorleistungen
            all_list.remove(x)
        if x.find("PV") != -1:      #Entferne alle PVs, wenn mit 1. nicht richtig funktioniert hat
            all_list.remove(x)
        i += 1

    for x in all_list:
        if x.find("PV") != -1 or x.find("AN") != -1:    #Sollte PV übrig bleiben, hier ignorieren
            pass
        elif x.find("BE") != -1 or x.find("NB") != -1:  #Schaue ob BEstandener oder NichtBestander Eintrag
            if now.month >= 10 or now.month <= 4:   #Haben wir Oktober-April?
                if now.month >= 10 and now.month <= 12:
                    semester = "WiSe " + str(now.year)[len(str(now.year))//2:]+"/"+(int(str(now.year)[len(str(now.year))//2:])+1)   #Dann "WiSe Altes Jahr/Neues Jahr"
                else:
                    semester = "WiSe " + str(now.year)[len(str(now.year)) // 2:] + "/" + (int(str(now.year)[len(str(now.year)) // 2:]) - 1)  # Dann "WiSe Neues Jahr/Altes Jahr"
            else:
                semester = "SoSe " + str(now.year)[len(str(now.year))//2:]  #Dann nicht, "SoSe Aktuelles Jahr"
            if any(y in x for y in modulnumbers) and x.find(semester) != -1:    #Finde aktuelles Semesterjahr in Modulübersicht
                with open("Klausur_log.txt") as f:
                    if (semester + ": "+ x.split(semester)[0]) in f.read():
                        pass
                    else:
                        f = open("Klausur_log.txt", "a")
                        f.write(semester + ": "+ x.split(semester)[0])
                        f.close()

                        url = "iftttwebrequesturl"
                        param = {'value1': x.split(semester)[0]}
                        requests.post(url, param)   #Wenn ja, sende IFTTT Webrequest

                        dicord_url = "discordwebhookurl"    #Öffentlicher Discord-Server
                        dis_param = {'content': '@everyone **' + semester + ": "+ x.split(semester)[0] + 'Noten sind online!**'}
                        requests.post(dicord_url, dis_param)    #Sende Discord Webhook
    br.close()
