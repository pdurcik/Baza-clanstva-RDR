#!/usr/bin/env python3

import sqlite3
import bottle
import hashlib # računanje MD5 kriptografski hash za gesla
from datetime import datetime

# uvozimo ustrezne podatke za povezavo
import auth as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

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

@bottle.route('/')
def main():
    """Glavna stran."""
    # Iz cookieja dobimo uporabnika (ali ga preusmerimo na login, če
    # nima cookija)
    (username, ime) = get_user()
    # Morebitno sporočilo za uporabnika
    sporocilo = get_sporocilo()
    # Vrnemo predlogo za glavno stran
    return bottle.template('uvodna_stran.html',
                           ime=ime,
                           username=username,
                           sporocilo=sporocilo)

@bottle.get('/')
def index():
    cur.execute("""SELECT * FROM akcija""")
    tmp2 = cur.fetchall()
    return bottle.template('uvodna_stran.html', akcije=tmp2)


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
    # password = bottle.request.forms.password

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
        # bottle.redirect('/prva/')
        # bottle.response.set_cookie('username', username, path='/', secret=secret)
        if tmp[3] == 'stars':
            bottle.redirect('/indexstars/')
        elif tmp[3] == 'admin':
            bottle.redirect("/indexadmin/")
        else:
            bottle.redirect("/")

# @bottle.get("/logout/")
# def logout():
#     """Pobriši cookie in preusmeri na login."""
#     bottle.response.delete_cookie('username')
#     bottle.redirect('/login/')


@bottle.get("/registracija/")
def login_get():
    """Serviraj formo za login."""
    curuser = get_user(auto_login = False)
    return bottle.template("registracija.html", name=None, surname=None, username=None, email=None,napaka=None)

@bottle.post("/registracija/")
def nov_zahtevek():
    ''' Vstavi novo sporocilo v tabelo sporocila.'''
    username = bottle.request.forms.get('username')
    name = bottle.request.forms.get('name')
    surname = bottle.request.forms.get('surname')
    email = bottle.request.forms.get('email')

    #trenutno je tule mali bug, saj ce geslo vsebuje sumnik, se program zlomi
    password = password_md5(bottle.request.forms.get('password'))
    password2 = password_md5(bottle.request.forms.get('confirmpassword'))

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
#
# @bottle.get('/glavna_stran/')
# def index_get():
#     return bottle.template('uvodna_stran.html', name=None, surname=None, institution=None, mail=None,napaka=None)


@bottle.get("/indexstars/")
def index_stars():
    prijavljen = get_user()
    #print (prijavljen)
    stars_id = prijavljen[0]
    cur.execute("""SELECT otrok FROM otroci
                    WHERE stars= %s""",
              [stars_id])
    tmp = cur.fetchall()
    otroci_id = tuple([otrok[0] for otrok in tmp])
    cur.execute("""SELECT * FROM oseba
                    WHERE id in %s""",
                [otroci_id])
    tmp1 = cur.fetchall()

    cur.execute("""SELECT * FROM akcija""")
    tmp2 = cur.fetchall()
    prijavljeni_na_akcije = []
    for i in otroci_id:
        cur.execute("""SELECT akcija FROM udelezenec
                    WHERE oseba=%s""", [i])
        akp = cur.fetchall()
        prijavljeni_na_akcije.append(akp)


    return bottle.template('indexstars.html', rows=tmp1, akcije=tmp2, prijavljeni_na_akcije=prijavljeni_na_akcije, prijavljen=prijavljen)

@bottle.post("/indexstars/")
def nov_zahtevek():
    c = conn.cursor()
    c.execute("""SELECT id FROM akcija""")
    akcije = c.fetchall() #idji akcij
    if bottle.request.POST.get('prijavi'): #argument je ime gumba!!!
        prijavljen = get_user()
        c = conn.cursor()
        c.execute("""INSERT INTO oseba (ime, priimek, rojstvo, naslov, clanarina, funkcija)
                        VALUES (%s, %s, %s, %s, %s, %s)""",
                  [bottle.request.forms.name, bottle.request.forms.surname, bottle.request.forms.date, prijavljen[4], 0, "otrok"])
    if bottle.request.POST.get('prijaviAkcija1'):
        prijavljen = bottle.request.POST.get("Izberi_otroka1")

        c.execute("""
                 INSERT INTO udelezenec (oseba, akcija)
                 VALUES (%s,%s) """,
                  [prijavljen, akcije[-3]])
    if bottle.request.POST.get('prijaviAkcija2'):
        prijavljen = bottle.request.POST.get("Izberi_otroka2")
        c = conn.cursor()
        c.execute("""
                 INSERT INTO udelezenec (oseba, akcija)
                 VALUES (%s,%s) """,
                  [prijavljen, akcije[-2]])
    if bottle.request.POST.get('prijaviAkcija3'):
        prijavljen = bottle.request.POST.get("Izberi_otroka3")
        c = conn.cursor()
        c.execute("""
                     INSERT INTO udelezenec (oseba, akcija)
                     VALUES (%s,%s) """,
                      [prijavljen, akcije[-1]])



    bottle.redirect('/indexstars/')






@bottle.get("/indexadmin/")
def index_admin():
    cur.execute("""SELECT * FROM vod""")
    tmp = cur.fetchall()
    tmpime = [x[0] for x in tmp]

    cur.execute("""SELECT ime, datum, trajanje FROM akcija""")
    tmp0 = cur.fetchall()
    tmp0ime = [x[0] for x in tmp0]

    cur.execute("""SELECT ime,priimek FROM oseba""")
    tmp1 = cur.fetchall()
    imena = [x[0] for x in tmp1]
    priimki = [x[1] for x in tmp1]

    cur.execute("""SELECT ime,priimek, telefon, mail, funkcija FROM oseba WHERE clanarina=0 ORDER BY ime ASC""")
    tmp2 = cur.fetchall()


    return bottle.template('indexadmin.html', rows_vod=tmpime, rows_akcija=tmp0ime, users1=imena,
                           users2=priimki, rows_tabela=None, vod_tabela=None, akcija_tabela=None,
                           napaka=None, skupna_tabela=None, akcije_vse=tmp0, napaka2=None, napaka3=None,
                           vodi_vse=tmp, clanarina=tmp2)

@bottle.post("/indexadmin/")
def nov_zahtevek_admin():
    cur.execute("""SELECT ime, starost, termin FROM vod""")
    tmp = cur.fetchall()
    tmpime = [x[0] for x in tmp]


    cur.execute("""SELECT ime, datum, trajanje FROM akcija""")
    tmp0 = cur.fetchall()
    tmp0ime = [x[0] for x in tmp0]

    cur.execute("""SELECT ime, priimek, id FROM oseba""")
    tmp1 = cur.fetchall()
    imena = [x[0] for x in tmp1]
    priimki = [x[1] for x in tmp1]
    idji = [x[2] for x in tmp1]

    cur.execute("""SELECT ime,priimek, telefon, mail, funkcija FROM oseba WHERE clanarina=0""")
    tmp2 = cur.fetchall()

    if bottle.request.POST.get('dodajclan'): #argument je ime gumba!!!
        id_vod = bottle.request.forms.vod



        c = conn.cursor()

        vrednosti = [bottle.request.forms.name, bottle.request.forms.surname, bottle.request.forms.date,
                   bottle.request.forms.address, bottle.request.forms.telefon, bottle.request.forms.email, 0,
                     bottle.request.forms.zaposlitev, bottle.request.forms.funkcija, id_vod]
        vrednosti = [x for x in vrednosti if x!=None]
        print (vrednosti)
        if bottle.request.forms.funkcija != 'otrok':
            sql = """INSERT INTO oseba (ime, priimek, rojstvo, naslov, telefon, mail, clanarina,
                                        zaposlitev, funkcija) VALUES {}"""
            c.execute(sql.format(tuple(vrednosti)))
        else:
            sql = """INSERT INTO oseba (ime, priimek, rojstvo, naslov, telefon, mail, clanarina,
                                        zaposlitev, funkcija, vod) VALUES {}"""
            c.execute(sql.format(tuple(vrednosti)))

    if bottle.request.POST.get('izbrisiclan'):  # argument je ime gumba!!!
        c = conn.cursor()
        c.execute("""DELETE FROM oseba WHERE ime=%s AND priimek=%s AND rojstvo=%s AND naslov=%s""",
                  [bottle.request.forms.name, bottle.request.forms.surname, bottle.request.forms.date,
                   bottle.request.forms.address])

    if bottle.request.POST.get('starsotrok'):  # argument je ime gumba!!!
        c = conn.cursor()
        stars = [bottle.request.forms.namestars, bottle.request.forms.surnamestars, bottle.request.forms.datestars,
                   bottle.request.forms.addressstars]
        otrok = [bottle.request.forms.nameotrok, bottle.request.forms.surnameotrok, bottle.request.forms.dateotrok,
                 bottle.request.forms.addressotrok]

        cur.execute("""SELECT id,funkcija FROM oseba
                        WHERE ime=%s AND priimek=%s AND rojstvo=%s AND naslov=%s""",
                    stars)
        tmpstars = cur.fetchall()

        cur.execute("""SELECT id,funkcija FROM oseba
                        WHERE ime=%s AND priimek=%s AND rojstvo=%s AND naslov=%s""",
                    otrok)

        tmpotrok = cur.fetchall()

        if tmpstars == []:
            return bottle.template('indexadmin.html', rows_vod=tmpime, rows_akcija=tmp0ime, users1=imena,
                                   users2=priimki, rows_tabela=None, vod_tabela=None, akcija_tabela=None,
                                   napaka='Napaka: starša ni v bazi!', skupna_tabela=None, akcije_vse=tmp0,
                                   napaka2=None, napaka3=None, vodi_vse=tmp, clanarina=tmp2)

        if tmpotrok == []:
            return bottle.template('indexadmin.html', rows_vod=tmpime, rows_akcija=tmp0ime, users1=imena,
                                   users2=priimki, rows_tabela=None, vod_tabela=None, akcija_tabela=None,
                                   napaka='Napaka: otroka ni v bazi!', skupna_tabela=None, akcije_vse=tmp0,
                                   napaka2=None, napaka3=None, vodi_vse=tmp, clanarina=tmp2)

        id_stars = tmpstars[0][0]
        funkcija_stars = tmpstars[0][1]

        id_otrok = tmpotrok[0][0]
        funkcija_otrok = tmpotrok[0][1]

        if funkcija_stars != stars:
            return bottle.template('indexadmin.html', rows_vod=tmpime, rows_akcija=tmp0ime, users1=imena,
                                   users2=priimki, rows_tabela=None, vod_tabela=None, akcija_tabela=None,
                                   napaka='Napaka: vnesena oseba ni starš!', skupna_tabela=None, akcije_vse=tmp0,
                                   napaka2=None, napaka3=None, vodi_vse=tmp, clanarina=tmp2)

        if funkcija_otrok != otrok:
            return bottle.template('indexadmin.html', rows_vod=tmpime, rows_akcija=tmp0ime, users1=imena,
                                   users2=priimki, rows_tabela=None, vod_tabela=None, akcija_tabela=None,
                                   napaka='Napaka: vnesena oseba ni otrok!', skupna_tabela=None, akcije_vse=tmp0,
                                   napaka2=None, napaka3=None, vodi_vse=tmp, clanarina=tmp2)

        c.execute("""INSERT INTO otroci VALUES (%s, %s)""", [id_stars, id_otrok])

    if bottle.request.POST.get('funkcija'):  # argument je ime gumba!!!
        c = conn.cursor()
        c.execute("""UPDATE oseba SET funkcija = %s WHERE ime = %s AND  priimek = %s
                        AND rojstvo = %s  AND naslov = %s""",
                  [bottle.request.forms.function, bottle.request.forms.name, bottle.request.forms.surname, bottle.request.forms.date,
                   bottle.request.forms.address])

    if bottle.request.POST.get('dodajakcijo'):
        if int(bottle.request.forms.organizator) not in idji:
            return bottle.template('indexadmin.html', rows_vod=tmpime, rows_akcija=tmp0ime, users1=imena,
                                   users2=priimki, rows_tabela=None, vod_tabela=None, akcija_tabela=None,
                                   napaka=None, skupna_tabela=None, akcije_vse=tmp0, napaka2='Napaka: organizator ni pravi!',
                                   napaka3=None, vodi_vse=tmp, clanarina=tmp2)
        else:
            c = conn.cursor()
            c.execute("""INSERT INTO akcija (ime, datum, trajanje, organizator, opis) VALUES (%s, %s, %s, %s, %s)""",
                  [bottle.request.forms.nameakc1, bottle.request.forms.dateakc1,
                   bottle.request.forms.time, bottle.request.forms.organizator, bottle.request.forms.comment])


    if bottle.request.POST.get('izbrisiakcijo'):
        c = conn.cursor()
        c.execute("""DELETE FROM akcija WHERE ime=%s AND datum=%s""",
                  [bottle.request.forms.name, bottle.request.forms.date])



    if bottle.request.POST.get('dodajvod'):
        if int(bottle.request.forms.vodnik) not in idji:
            return bottle.template('indexadmin.html', rows_vod=tmpime, rows_akcija=tmp0ime, users1=imena,
                                   users2=priimki, rows_tabela=None, vod_tabela=None, akcija_tabela=None,
                                   napaka=None, skupna_tabela=None, akcije_vse=tmp0, napaka2=None,
                                        napaka3 = 'Napaka: vodnik ni pravi!', vodi_vse=tmp, clanarina=tmp2)
        else:
            c = conn.cursor()
            c.execute("""INSERT INTO vod (ime, starost, termin, vodnik) VALUES (%s, %s, %s, %s)""",
                  [bottle.request.forms.namevod1, bottle.request.forms.starost,
                   bottle.request.forms.termin, bottle.request.forms.vodnik])


    if bottle.request.POST.get('izbrisivod'):
        c = conn.cursor()
        c.execute("""DELETE FROM vod WHERE ime=%s""",
                  [bottle.request.forms.name])

    if bottle.request.POST.get('isci'):  # argument je ime gumba!!!
        if bottle.request.forms.priimek == '':
            cur.execute("""SELECT oseba.ime, priimek, rojstvo, naslov, telefon, mail, clanarina, 
            zaposlitev, funkcija, vod.ime FROM oseba LEFT OUTER JOIN vod ON oseba.vod = vod.id
                        WHERE oseba.ime=%s""", [bottle.request.forms.ime])
            rows_tab = cur.fetchall()
            return bottle.template('indexadmin.html', rows_vod=tmpime, rows_akcija=tmp0ime, users1=imena,
                                   users2=priimki, rows_tabela=rows_tab, vod_tabela=None, akcija_tabela=None,
                                   napaka=None, skupna_tabela=None, akcije_vse=tmp0, napaka2=None, napaka3=None,
                                   vodi_vse=tmp, clanarina=tmp2)
        if bottle.request.forms.ime == '':
            cur.execute("""SELECT oseba.ime, priimek, rojstvo, naslov, telefon, mail, clanarina, 
            zaposlitev, funkcija, vod.ime FROM oseba LEFT OUTER JOIN vod ON oseba.vod = vod.id
                        WHERE priimek=%s""", [bottle.request.forms.priimek])
            rows_tab = cur.fetchall()
            return bottle.template('indexadmin.html', rows_vod=tmpime, rows_akcija=tmp0ime, users1=imena,
                                   users2=priimki, rows_tabela=rows_tab, vod_tabela=None, akcija_tabela=None,
                                   napaka=None, skupna_tabela=None, akcije_vse=tmp0, napaka2=None, napaka3=None,
                                   vodi_vse=tmp, clanarina=tmp2)
        if bottle.request.forms.ime != '' and bottle.request.forms.priimek != '':
            cur.execute("""SELECT oseba.ime, priimek, rojstvo, naslov, telefon, mail, clanarina, 
            zaposlitev, funkcija, vod.ime FROM oseba LEFT OUTER JOIN vod ON oseba.vod = vod.id
                        WHERE oseba.ime=%s AND priimek=%s""", [bottle.request.forms.ime, bottle.request.forms.priimek])
            rows_tab = cur.fetchall()
            return bottle.template('indexadmin.html', rows_vod=tmpime, rows_akcija=tmp0ime, users1=imena,
                                   users2=priimki,  rows_tabela=rows_tab, vod_tabela=None, akcija_tabela=None,
                                   napaka=None, skupna_tabela=None, akcije_vse=tmp0, napaka2=None, napaka3=None,
                                   vodi_vse=tmp, clanarina=tmp2)
    if bottle.request.POST.get('izpis'):  # argument je ime gumba!!!
        if bottle.request.forms.vod2 == '':
            cur.execute("""SELECT oseba.ime, oseba.priimek, oseba.funkcija, akcija.ime FROM oseba JOIN udelezenec 
            ON oseba.id = udelezenec.oseba JOIN akcija ON akcija.id = udelezenec.akcija
                        WHERE akcija.ime=%s""", [bottle.request.forms.akcija2])
            rows_akc = cur.fetchall()
            return bottle.template('indexadmin.html', rows_vod=tmpime, rows_akcija=tmp0ime, users1=imena,
                                   users2=priimki, rows_tabela=None, vod_tabela=None, akcija_tabela=rows_akc,
                                   napaka=None, skupna_tabela=None, akcije_vse=tmp0, napaka2=None, napaka3=None,
                                   vodi_vse=tmp, clanarina=tmp2)
        if bottle.request.forms.akcija2 == '':
            cur.execute("""SELECT oseba.ime, oseba.priimek, oseba.funkcija, vod.ime FROM oseba JOIN vod ON oseba.vod = vod.id
                        WHERE vod.ime=%s""", [bottle.request.forms.vod2])
            rows_vd = cur.fetchall()
            return bottle.template('indexadmin.html', rows_vod=tmpime, rows_akcija=tmp0ime, users1=imena,
                                   users2=priimki, rows_tabela=None, vod_tabela=rows_vd, akcija_tabela=None,
                                   napaka=None, skupna_tabela=None, akcije_vse=tmp0, napaka2=None, napaka3=None,
                                   vodi_vse=tmp, clanarina=tmp2)
        if bottle.request.forms.akcija2 != '' and bottle.request.forms.vod2 != '':
            cur.execute("""SELECT oseba.ime, oseba.priimek, oseba.funkcija, akcija.ime, vod.ime FROM oseba LEFT OUTER JOIN udelezenec ON oseba.id = udelezenec.oseba
LEFT OUTER JOIN akcija ON akcija.id = udelezenec.akcija LEFT OUTER JOIN vod ON oseba.vod = vod.id
                        WHERE akcija.ime=%s AND vod.ime=%s""", [bottle.request.forms.akcija2, bottle.request.forms.vod2])
            skp_tabela = cur.fetchall()

            return bottle.template('indexadmin.html', rows_vod=tmpime, rows_akcija=tmp0ime, users1=imena,
                                   users2=priimki, rows_tabela=None, vod_tabela=None, akcija_tabela=None, napaka=None,
                                   skupna_tabela=skp_tabela, akcije_vse=tmp0, napaka2=None, napaka3=None, vodi_vse=tmp, clanarina=tmp2)

    bottle.redirect('/indexadmin/')
######################################################################
# Glavni program

# priklopimo se na bazo
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


# poženemo strežnik na portu 8080, glej http://localhost:8080/
bottle.run(host='localhost', port=8080, reloader=True)