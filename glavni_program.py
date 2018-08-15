#!/usr/bin/env python3

import sqlite3
import bottle
import hashlib # računanje MD5 kriptografski hash za gesla

# uvozimo ustrezne podatke za povezavo
import auth_public as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import datetime

######################################################################
# Konfiguracija

# Vklopi debug, da se bodo predloge same osvežile in da bomo dobivali
# lepa sporočila o napakah.
bottle.debug(True)


# Mapa s statičnimi datotekami
static_dir = "./static"

# Skrivnost za kodiranje cookijev
secret = "to skrivnost je zelo tezko uganiti 1094107c907cw982982c42"


######################################################################
# Pomožne funkcije

def password_md5(s):
    """Vrni MD5 hash danega UTF-8 niza. Gesla vedno spravimo v bazo
       kodirana s to funkcijo."""
    h = hashlib.md5()
    h.update(s.encode('utf-8'))
    return h.hexdigest()

"""Dobimo uporabnika iz piskotka, ce ga ni, ga vrzemo na login stran"""
def get_user(auto_login = True, auto_redir=False):
    # Dobimo username iz piskotka
    username = bottle.request.get_cookie('username', secret=secret)
    # Preverimo, ali ta uporabnik obstaja
    if username is not None:
        if auto_redir:
            # Ce uporabnik ze prijavljen, ga damo na domačo stran
            bottle.redirect('/index/')
        else:
            c = conn.cursor()
            c.execute("SELECT * FROM uporabnik WHERE username=%s", [username])
            r = c.fetchone()
            if r is not None:
                # uporabnik obstaja, vrnemo njegove podatke
                return r
    # uporabnik ni prijavljen, vrnemo ga na login page
    if auto_login:
        bottle.redirect('/prijava/')
    else:
        return None


@bottle.route('/static/<filename:path>')
def static(filename):
    """Splošna funkcija, ki servira vse statične datoteke iz naslova
       /static/..."""
    return bottle.static_file(filename, root=static_dir)

@bottle.get('/')
def index():

    now = datetime.datetime.now()
    cur.execute("""SELECT * FROM akcija ORDER BY datum DESC""")
    tmp2 = cur.fetchall()
    za_prikaz = [x for x in tmp2 if now.date() < x[2]]
    return bottle.template('uvodna_stran.html', akcije=tmp2, akcije_prikaz = za_prikaz)

@bottle.get('/prijava/')
def prijava_get():
    """Serviraj formo za provo."""
    return bottle.template('prijava.html',
                           napaka=None,
                           username=None)

@bottle.post('/prijava/')
def prijava_post():
    """Obdelaj izpolnjeno formo za prijavo"""
    # Uporabniško ime, ki ga je uporabnik vpisal v formo
    username = bottle.request.forms.username
    # Izračunamo MD5 has gesla, ki ga bomo spravili
    password = password_md5(bottle.request.forms.password)

    # Preverimo, ali se je uporabnik pravilno prijavil
    c = conn.cursor()
    c.execute("SELECT * FROM uporabnik WHERE username=%s AND password=%s",
              [username, password])

    tmp = c.fetchone()

    if tmp is None:
        # Username in geslo se ne ujemata
        return bottle.template('prijava.html',
                               napaka="Nepravilna prijava",
                               username=username)
    else:
        # Vse je v redu, nastavimo cookie in preusmerimo na glavno stran
        bottle.response.set_cookie('username', username, path='/', secret=secret)
        if tmp[3] == 'stars':
            bottle.redirect('/indexstars/')
        elif tmp[3] == 'admin':
            bottle.redirect("/indexadmin/")
        else:
            bottle.redirect("/")


@bottle.get("/registracija/")
def regist_get():
    """Serviraj formo za login."""
    # curuser = get_user(auto_login = False)
    return bottle.template("registracija.html", name=None, surname=None, username=None, email=None,napaka=None)

@bottle.post("/registracija/")
def regist_post():
    username = bottle.request.forms.username
    name = bottle.request.forms.name
    surname = bottle.request.forms.surname
    email = bottle.request.forms.email
    password = password_md5(bottle.request.forms.password)
    password2 = password_md5(bottle.request.forms.confirmpassword)

    #preverimo, ce je izbrani username ze zaseden
    c1 = conn.cursor()
    c1.execute("SELECT * FROM uporabnik WHERE username=%s",
              [username])
    tmp = c1.fetchone()
    if tmp is not None:
        return bottle.template("registracija.html", name=name, surname=surname, username=username,
                               email=email, napaka="Uporabniško ime je že zasedeno!.")

    # preverimo, ali se gesli ujemata
    if password != password2:
        return bottle.template("registracija.html", name=name, surname=surname, username=username,
                               email=email, napaka="Gesli se ne ujemata!")

    # preverimo, ali obstaja uporabnik v tabeli oseba
    c2 = conn.cursor()
    c2.execute("SELECT * FROM oseba WHERE ime=%s AND priimek=%s AND mail=%s",
              [name, surname, email])
    tmp2 = c2.fetchone()
    if tmp2 is None:
        return bottle.template("registracija.html", name=name, surname=surname, username=username,
                              email=email, napaka="Niste še vpisani! Obrnite se na admina!")

    if tmp2[-2] != 'starš':
        return bottle.template("registracija.html", name=name, surname=surname, username=username,
                               email=email, napaka="Niste starš! Obrnite se na admina!")

    #ce pridemo, do sem, je vse uredu in lahko vnesemo zahtevek v bazo
    c = conn.cursor()
    c.execute("""INSERT INTO uporabnik (username, password, funkcija, idoseba)
                VALUES (%s, %s, %s, %s)""",
              [username, password, "stars", tmp2[0]])


    return bottle.template("registracija.html", name=None, surname=None, username=None, date=None,
                           address=None, email=None,napaka="Registrirani ste!")

@bottle.get("/odjava/")
def logout():
    """Pobrisi cookie in preusmeri na login."""
    bottle.response.delete_cookie('username', path='/', secret=secret)
    bottle.redirect('/prijava/')

@bottle.get("/pozabljeno_geslo/")
def password_get():
    return bottle.template("pozabljeno_geslo.html")


@bottle.get("/indexstars/")
def index_stars():
    now = datetime.datetime.now()

    c = conn.cursor()
    prijavljen = get_user()
    stars_id = prijavljen[4]
    c.execute("""SELECT otrok FROM otroci
                    WHERE stars= %s""",
              [stars_id])
    tmp = c.fetchall()
    otroci_id = tuple([otrok[0] for otrok in tmp])
    if otroci_id != ():
        c.execute("""SELECT * FROM oseba
                        WHERE id in %s""",
                    [otroci_id])
        tmp1 = c.fetchall()
    else:
        tmp1 = []

    c.execute("""SELECT * FROM akcija ORDER BY datum DESC""")
    tmp2 = c.fetchall()
    za_prikaz = [x for x in tmp2 if now.date() < x[2]]
    idji_za_prikaz = [x[0] for x in za_prikaz]
    prijavljeni_na_akcije = []
    for i in otroci_id:
        c.execute("""SELECT akcija FROM udelezenec
                    WHERE oseba=%s""", [i])
        akp = c.fetchall()
        otrokove_akcije = []
        for j in akp:
            if j[0] in idji_za_prikaz:
                otrokove_akcije.append(j)
        prijavljeni_na_akcije.append(otrokove_akcije)

    return bottle.template('indexstars.html', rows=tmp1, akcije=tmp2, prijavljeni_na_akcije=prijavljeni_na_akcije,
                           prijavljen=prijavljen, akcije_prikaz=za_prikaz, dodajnapis=None)

@bottle.post("/indexstars/")
def index_stars_post():
    now = datetime.datetime.now()
    c = conn.cursor()
    c.execute("""SELECT id FROM akcija""")
    akcije = c.fetchall() #idji akcij
    prijavljen = get_user()
    c.execute("""SELECT * FROM oseba WHERE id=%s""", [prijavljen[4]])
    podatki_prijavljen = c.fetchall()


    if bottle.request.POST.get('prijavi'): #argument je ime gumba!!!

        c.execute("""INSERT INTO oseba (ime, priimek, rojstvo, naslov,  clanarina, funkcija)
                        VALUES (%s, %s, %s, %s, %s, %s)""",
                  [bottle.request.forms.name, bottle.request.forms.surname, bottle.request.forms.date,  podatki_prijavljen[0][4], 0, "otrok"])
        c.execute("""SELECT MAX(id) FROM  oseba""")
        max_id = c.fetchall()
        c.execute("""INSERT INTO otroci VALUES (%s, %s)""",
                  [prijavljen[4], max_id[0][0]])

    c.execute("""SELECT * FROM akcija ORDER BY datum DESC""")
    tmp2 = c.fetchall()
    za_prikaz = [x for x in tmp2 if now.date() < x[2]]

    for akcija in za_prikaz:
        ime = 'prijaviAkcija'+str(akcija[0])
        if bottle.request.POST.get(ime):
            imeotrok = 'otrok'+str(akcija[0])
            prijavljen = bottle.request.POST.get(imeotrok)
            c.execute("""SELECT * FROM udelezenec
                            WHERE oseba = %s AND akcija = %s""",
                      [prijavljen, akcija[0]])
            tmp = c.fetchall()
            if tmp == []:
                c.execute("""
                         INSERT INTO udelezenec (oseba, akcija)
                         VALUES (%s,%s) """,
                          [prijavljen, akcija[0]])


    bottle.redirect('/indexstars/')


@bottle.get("/indexadmin/")
def index_admin():
    c = conn.cursor()
    c.execute("""SELECT id, ime, starost, termin FROM vod""")
    tmp = c.fetchall()
    tmpime = [x[1] for x in tmp]

    c.execute("""SELECT id, ime, datum, trajanje FROM akcija""")
    tmp0 = c.fetchall()
    tmp0ime = [x[1] for x in tmp0]

    c.execute("""SELECT id, ime, priimek, naslov, rojstvo, funkcija FROM oseba ORDER BY ime ASC""")
    tmp1 = c.fetchall()
    imena = [x[1] for x in tmp1]
    priimki = [x[2] for x in tmp1]
    otroci = [(x[1], x[2], x[3], x[4], x[0]) for x in tmp1 if x[5]=='otrok']
    starsi = [(x[1], x[2], x[3], x[4], x[0]) for x in tmp1 if x[5]=='starš']

    c.execute("""SELECT ime,priimek, telefon, mail, funkcija FROM oseba WHERE clanarina=0 AND funkcija='otrok' ORDER BY ime ASC""")
    tmp2 = c.fetchall()

    c.execute("""SELECT oseba.ime, oseba.priimek, oseba.naslov, oseba.rojstvo, oseba.id FROM oseba LEFT JOIN vod
            ON oseba.id = vod.vodnik LEFT JOIN akcija ON oseba.id = akcija.organizator WHERE vod.id IS NULL AND akcija.id IS NULL ORDER BY oseba.ime ASC""")
    izbrisi = c.fetchall()

    return bottle.template('indexadmin.html', rows_vod=tmpime, rows_akcija=tmp0ime, users1=imena,
                           users2=priimki, rows_tabela=None, vod_tabela=None, akcija_tabela=None,
                           napaka=None, skupna_tabela=None, akcije_vse=tmp0, napaka2=None, napaka3=None,
                           vodi_vse=tmp, clanarina=tmp2, napaka4=None, napaka5=None, izbrisani=izbrisi, parents=starsi,
                           children=otroci, funkcije=tmp1, napaka6=None)

# pomožna funkcija, ki vrne tabele za admina
def za_tabele_admin_post():
    c = conn.cursor()
    c.execute("""SELECT id, ime, starost, termin FROM vod""")
    tmp = c.fetchall()
    tmpime = [x[1] for x in tmp]


    c.execute("""SELECT id, ime, datum, trajanje FROM akcija""")
    tmp0 = c.fetchall()
    tmp0ime = [x[1] for x in tmp0]

    c.execute("""SELECT id, ime, priimek, naslov, rojstvo, funkcija FROM oseba ORDER BY ime ASC""")
    tmp1 = c.fetchall()
    imena = [x[1] for x in tmp1]
    priimki = [x[2] for x in tmp1]
    otroci = [(x[1], x[2], x[3], x[4], x[0]) for x in tmp1 if x[5]=='otrok']
    starsi = [(x[1], x[2], x[3], x[4], x[0]) for x in tmp1 if x[5]=='starš']

    c.execute("""SELECT ime,priimek, telefon, mail, funkcija FROM oseba WHERE clanarina=0 AND funkcija='otrok' ORDER BY ime ASC""")
    tmp2 = c.fetchall()

    c.execute("""SELECT oseba.ime, oseba.priimek, oseba.naslov, oseba.rojstvo, oseba.id FROM oseba LEFT JOIN vod
            ON oseba.id = vod.vodnik LEFT JOIN akcija ON oseba.id = akcija.organizator WHERE vod.id IS NULL AND akcija.id IS NULL ORDER BY oseba.ime ASC""")
    izbrisi = c.fetchall()
    return (tmpime, tmp0ime, imena, priimki, tmp0, tmp, tmp2, izbrisi, starsi, otroci, tmp1)

@bottle.post("/indexadmin/")
def index_admin_post():
    c = conn.cursor()
    [tmpime, tmp0ime, imena, priimki, tmp0, tmp, tmp2, izbrisi, starsi, otroci, tmp1] = za_tabele_admin_post()
    idji = [x[0] for x in tmp1]

    if bottle.request.POST.get('dodajclan'): #argument je ime gumba!!!

        id_vod = bottle.request.forms.vod

        vrednosti = [bottle.request.forms.name, bottle.request.forms.surname, bottle.request.forms.date,
                   bottle.request.forms.address, bottle.request.forms.telefon, bottle.request.forms.email, 0,
                     bottle.request.forms.zaposlitev, bottle.request.forms.funkcija]

        vrednosti = [x if x != '' else None for x in vrednosti]

        if id_vod != '':
            vrednosti.append(int(id_vod))
        else:
            vrednosti.append(None)

        if bottle.request.forms.funkcija != 'otrok' and id_vod != '':
            return bottle.template('indexadmin.html', rows_vod=tmpime, rows_akcija=tmp0ime, users1=imena,
                                   users2=priimki, rows_tabela=None, vod_tabela=None, akcija_tabela=None,
                                   napaka=None, skupna_tabela=None, akcije_vse=tmp0,
                                   napaka2=None, napaka3=None, vodi_vse=tmp, clanarina=tmp2,
                                   napaka4='Napaka: samo otrokom lahko določimo vod!', napaka5=None, izbrisani=izbrisi,
                                   parents=starsi, children=otroci, funkcije=tmp1, napaka6=None)
        if bottle.request.forms.funkcija == 'starš' and bottle.request.forms.email == '':
            return bottle.template('indexadmin.html', rows_vod=tmpime, rows_akcija=tmp0ime, users1=imena,
                                   users2=priimki, rows_tabela=None, vod_tabela=None, akcija_tabela=None,
                                   napaka=None, skupna_tabela=None, akcije_vse=tmp0,
                                   napaka2=None, napaka3=None, vodi_vse=tmp, clanarina=tmp2,
                                   napaka4='Napaka: starši morajo imeti email!', napaka5=None, izbrisani=izbrisi,
                                   parents=starsi, children=otroci, funkcije=tmp1, napaka6=None)

        c.execute("""INSERT INTO oseba (ime, priimek, rojstvo, naslov, telefon, mail, clanarina,
                                    zaposlitev, funkcija, vod) VALUES (%s, %s, %s, %s, %s, %s, %s, 
                                    %s, %s, %s)""", (vrednosti))

        [tmpime, tmp0ime, imena, priimki, tmp0, tmp, tmp2, izbrisi, starsi, otroci, tmp1] = za_tabele_admin_post()

        return bottle.template('indexadmin.html', rows_vod=tmpime, rows_akcija=tmp0ime, users1=imena,
                               users2=priimki, rows_tabela=None, vod_tabela=None, akcija_tabela=None,
                               napaka=None, skupna_tabela=None, akcije_vse=tmp0,
                               napaka2=None, napaka3=None, vodi_vse=tmp, clanarina=tmp2,
                               napaka4='Oseba je bila uspešno dodana!', napaka5=None, izbrisani=izbrisi,
                               parents=starsi, children=otroci, funkcije=tmp1, napaka6=None)


    if bottle.request.POST.get('izbrisimember'):  # argument je ime gumba!!!
        c.execute("""DELETE FROM oseba WHERE id=%s""",
                  [bottle.request.forms.izbrisimemberid])

        [tmpime,tmp0ime, imena,priimki,tmp0,tmp,tmp2, izbrisi,starsi,otroci, tmp1] = za_tabele_admin_post()

        return bottle.template('indexadmin.html', rows_vod=tmpime, rows_akcija=tmp0ime, users1=imena,
                               users2=priimki, rows_tabela=None, vod_tabela=None, akcija_tabela=None,
                               napaka=None, skupna_tabela=None, akcije_vse=tmp0,
                               napaka2=None, napaka3=None, vodi_vse=tmp, clanarina=tmp2,
                               napaka4=None, napaka5='Oseba je bila uspešno izbrisana!', izbrisani=izbrisi,
                               parents=starsi, children=otroci, funkcije=tmp1, napaka6=None)

    if bottle.request.POST.get('relacija'):
        # preverimo, ali relacija že obstaja. Če ja, vrnemo napako
        c.execute("""SELECT * FROM  otroci WHERE stars=%s AND otrok=%s""",
                  [bottle.request.forms.relacijastarsid, bottle.request.forms.relacijaotrokid])
        obstaja = c.fetchall()
        if obstaja:
            return bottle.template('indexadmin.html', rows_vod=tmpime, rows_akcija=tmp0ime, users1=imena,
                                   users2=priimki, rows_tabela=None, vod_tabela=None, akcija_tabela=None,
                                   napaka='Napaka: ta relacija že obstaja!', skupna_tabela=None, akcije_vse=tmp0,
                                   napaka2=None, napaka3=None, vodi_vse=tmp, clanarina=tmp2,
                                   napaka4=None, napaka5=None, izbrisani=izbrisi,
                                   parents=starsi, children=otroci, funkcije=tmp1, napaka6=None)

        c.execute("""INSERT INTO otroci VALUES (%s, %s)""", [bottle.request.forms.relacijastarsid, bottle.request.forms.relacijaotrokid])
        [tmpime,tmp0ime, imena,priimki,tmp0,tmp,tmp2, izbrisi,starsi,otroci, tmp1] = za_tabele_admin_post()

        return bottle.template('indexadmin.html', rows_vod=tmpime, rows_akcija=tmp0ime, users1=imena,
                               users2=priimki, rows_tabela=None, vod_tabela=None, akcija_tabela=None,
                               napaka='Relacija je bila uspešno dodana!', skupna_tabela=None, akcije_vse=tmp0,
                               napaka2=None, napaka3=None, vodi_vse=tmp, clanarina=tmp2,
                               napaka4=None, napaka5=None, izbrisani=izbrisi,
                               parents=starsi, children=otroci, funkcije=tmp1, napaka6=None)

    if bottle.request.POST.get('function'):  # argument je ime gumba!!!
        c.execute("""UPDATE oseba SET funkcija = %s WHERE id = %s""",
                      [bottle.request.forms.funkcija2, bottle.request.forms.funkcijaosebaid])
        [tmpime,tmp0ime, imena,priimki,tmp0,tmp,tmp2, izbrisi,starsi,otroci, tmp1] = za_tabele_admin_post()

        return bottle.template('indexadmin.html', rows_vod=tmpime, rows_akcija=tmp0ime, users1=imena,
                               users2=priimki, rows_tabela=None, vod_tabela=None, akcija_tabela=None,
                               napaka=None, skupna_tabela=None, akcije_vse=tmp0,
                               napaka2=None, napaka3=None, vodi_vse=tmp, clanarina=tmp2,
                               napaka4=None, napaka5=None, izbrisani=izbrisi,
                               parents=starsi, children=otroci, funkcije=tmp1, napaka6='Funckija je bila uspešno spremenjena!')

    if bottle.request.POST.get('dodajakcijo'):
        if int(bottle.request.forms.organizator) not in idji:
            return bottle.template('indexadmin.html', rows_vod=tmpime, rows_akcija=tmp0ime, users1=imena,
                                   users2=priimki, rows_tabela=None, vod_tabela=None, akcija_tabela=None,
                                   napaka=None, skupna_tabela=None, akcije_vse=tmp0, napaka2='Napaka: organizator ni pravi!',
                                   napaka3=None, vodi_vse=tmp, clanarina=tmp2, napaka4=None, napaka5=None, izbrisani=izbrisi,
                                   parents=starsi, children=otroci, funkcije=tmp1, napaka6=None)
        else:
            c.execute("""INSERT INTO akcija (ime, datum, trajanje, organizator, opis) VALUES (%s, %s, %s, %s, %s)""",
                  [bottle.request.forms.nameakc1, bottle.request.forms.dateakc1,
                   bottle.request.forms.time, bottle.request.forms.organizator, bottle.request.forms.comment])


    if bottle.request.POST.get('izbrisiakcijo'):
        c.execute("""DELETE FROM akcija WHERE id=%s""",
                  [bottle.request.forms.izbrisiakcijaid])

    if bottle.request.POST.get('dodajvod'):
        if int(bottle.request.forms.vodnik) not in idji:
            return bottle.template('indexadmin.html', rows_vod=tmpime, rows_akcija=tmp0ime, users1=imena,
                                   users2=priimki, rows_tabela=None, vod_tabela=None, akcija_tabela=None,
                                   napaka=None, skupna_tabela=None, akcije_vse=tmp0, napaka2=None,
                                        napaka3 = 'Napaka: vodnik ni pravi!', vodi_vse=tmp, clanarina=tmp2,
                                   napaka4=None, napaka5=None, izbrisani=izbrisi, parents=starsi, children=otroci, funkcije=tmp1, napaka6=None)
        else:
            c.execute("""INSERT INTO vod (ime, starost, termin, vodnik) VALUES (%s, %s, %s, %s)""",
                  [bottle.request.forms.namevod1, bottle.request.forms.starost,
                   bottle.request.forms.termin, bottle.request.forms.vodnik])


    if bottle.request.POST.get('izbrisivod'):
        c.execute("""DELETE FROM vod WHERE id=%s""",
                  [bottle.request.forms.izbrisivodid])

    if bottle.request.POST.get('isci'):  # argument je ime gumba!!!
        if bottle.request.forms.priimek == '':
            c.execute("""SELECT oseba.ime, priimek, rojstvo, naslov, telefon, mail, clanarina, 
            zaposlitev, funkcija, vod.ime FROM oseba LEFT OUTER JOIN vod ON oseba.vod = vod.id
                        WHERE oseba.ime=%s ORDER BY oseba.ime ASC""", [bottle.request.forms.ime])
            rows_tab = c.fetchall()
            return bottle.template('indexadmin.html', rows_vod=tmpime, rows_akcija=tmp0ime, users1=imena,
                                   users2=priimki, rows_tabela=rows_tab, vod_tabela=None, akcija_tabela=None,
                                   napaka=None, skupna_tabela=None, akcije_vse=tmp0, napaka2=None, napaka3=None,
                                   vodi_vse=tmp, clanarina=tmp2, napaka4=None, napaka5=None, izbrisani=izbrisi,
                                   parents=starsi, children=otroci, funkcije=tmp1, napaka6=None)
        if bottle.request.forms.ime == '':
            c.execute("""SELECT oseba.ime, priimek, rojstvo, naslov, telefon, mail, clanarina, 
            zaposlitev, funkcija, vod.ime FROM oseba LEFT OUTER JOIN vod ON oseba.vod = vod.id
                        WHERE priimek=%s""", [bottle.request.forms.priimek])
            rows_tab = c.fetchall()
            return bottle.template('indexadmin.html', rows_vod=tmpime, rows_akcija=tmp0ime, users1=imena,
                                   users2=priimki, rows_tabela=rows_tab, vod_tabela=None, akcija_tabela=None,
                                   napaka=None, skupna_tabela=None, akcije_vse=tmp0, napaka2=None, napaka3=None,
                                   vodi_vse=tmp, clanarina=tmp2, napaka4=None, napaka5=None, izbrisani=izbrisi,
                                   parents=starsi, children=otroci, funkcije=tmp1, napaka6=None)
        if bottle.request.forms.ime != '' and bottle.request.forms.priimek != '':
            c.execute("""SELECT oseba.ime, priimek, rojstvo, naslov, telefon, mail, clanarina, 
            zaposlitev, funkcija, vod.ime FROM oseba LEFT OUTER JOIN vod ON oseba.vod = vod.id
                        WHERE oseba.ime=%s AND priimek=%s""", [bottle.request.forms.ime, bottle.request.forms.priimek])
            rows_tab = c.fetchall()
            return bottle.template('indexadmin.html', rows_vod=tmpime, rows_akcija=tmp0ime, users1=imena,
                                   users2=priimki,  rows_tabela=rows_tab, vod_tabela=None, akcija_tabela=None,
                                   napaka=None, skupna_tabela=None, akcije_vse=tmp0, napaka2=None, napaka3=None,
                                   vodi_vse=tmp, clanarina=tmp2, napaka4=None, napaka5=None, izbrisani=izbrisi,
                                   parents=starsi, children=otroci, funkcije=tmp1, napaka6=None)
    if bottle.request.POST.get('izpis'):  # argument je ime gumba!!!
        if bottle.request.forms.vod2 == '':
            c.execute("""SELECT oseba.ime, oseba.priimek, oseba.funkcija, akcija.ime FROM oseba JOIN udelezenec 
            ON oseba.id = udelezenec.oseba JOIN akcija ON akcija.id = udelezenec.akcija
                        WHERE akcija.ime=%s ORDER BY oseba.ime ASC""", [bottle.request.forms.akcija2])
            rows_akc = c.fetchall()
            return bottle.template('indexadmin.html', rows_vod=tmpime, rows_akcija=tmp0ime, users1=imena,
                                   users2=priimki, rows_tabela=None, vod_tabela=None, akcija_tabela=rows_akc,
                                   napaka=None, skupna_tabela=None, akcije_vse=tmp0, napaka2=None, napaka3=None,
                                   vodi_vse=tmp, clanarina=tmp2, napaka4=None, napaka5=None, izbrisani=izbrisi,
                                   parents=starsi, children=otroci, funkcije=tmp1, napaka6=None)
        if bottle.request.forms.akcija2 == '':
            c.execute("""SELECT oseba.ime, oseba.priimek, oseba.funkcija, vod.ime FROM oseba JOIN vod ON oseba.vod = vod.id
                        WHERE vod.ime=%s ORDER BY oseba.ime ASC""", [bottle.request.forms.vod2])
            rows_vd = c.fetchall()
            return bottle.template('indexadmin.html', rows_vod=tmpime, rows_akcija=tmp0ime, users1=imena,
                                   users2=priimki, rows_tabela=None, vod_tabela=rows_vd, akcija_tabela=None,
                                   napaka=None, skupna_tabela=None, akcije_vse=tmp0, napaka2=None, napaka3=None,
                                   vodi_vse=tmp, clanarina=tmp2, napaka4=None, napaka5=None, izbrisani=izbrisi,
                                   parents=starsi, children=otroci, funkcije=tmp1, napaka6=None)
        if bottle.request.forms.akcija2 != '' and bottle.request.forms.vod2 != '':
            c.execute("""SELECT oseba.ime, oseba.priimek, oseba.funkcija, akcija.ime, vod.ime FROM oseba LEFT OUTER JOIN udelezenec ON oseba.id = udelezenec.oseba
LEFT OUTER JOIN akcija ON akcija.id = udelezenec.akcija LEFT OUTER JOIN vod ON oseba.vod = vod.id
                        WHERE akcija.ime=%s AND vod.ime=%s""", [bottle.request.forms.akcija2, bottle.request.forms.vod2])

            skp_tabela = c.fetchall()
            return bottle.template('indexadmin.html', rows_vod=tmpime, rows_akcija=tmp0ime, users1=imena,
                                   users2=priimki, rows_tabela=None, vod_tabela=None, akcija_tabela=None, napaka=None,
                                   skupna_tabela=skp_tabela, akcije_vse=tmp0, napaka2=None, napaka3=None, vodi_vse=tmp,
                                   clanarina=tmp2, napaka4=None, napaka5=None, izbrisani=izbrisi, parents=starsi,
                                   children=otroci, funkcije=tmp1, napaka6=None)

    bottle.redirect('/indexadmin/')

######################################################################
# Glavni program

# priklopimo se na bazo
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


# poženemo strežnik na portu 8080, glej http://localhost:8080/
bottle.run(host='localhost', port=8080, reloader=True)

