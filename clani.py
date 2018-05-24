# uvozimo ustrezne podatke za povezavo
import auth
auth.db = "sem2018_%s" % auth.user

from random import randint
import itertools

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import csv

pari_stars_otrok = [[13, 25],[17,26],[77,82],[11,5],[13,33],[13,14],[16,19],[17,88],[1,6],[1,7],[27,66],[54,72],[8,15]]

pari = []
ooo = []
sss = []
for [i,j] in pari_stars_otrok:
    sss.append(i)
    ooo.append(j)

ooo = list(set(ooo))


pari = list(set(pari))

vod_prasec = [25, 26, 82, 5]
vod_vombat = [33, 14, 19, 88]
vod_veverice = [66, 6, 7, 72, 15]

vodi = [[0, 'krškopoljski prašiči', 8, 3, 73], [1, 'vombati', 11, 2, 74], [2, 'leteče veverice', 16, 4, 99]]

akcije = [[0, 'Izlet v neznano', '01-01-2018', '8h', 2], [1, 'Izlet v znano', '05-06-2017', '24h', 7], [2, 'Izlet v NY', '11-09-2001', '3dni', 98]]

def ustvari_tabelo(seznam):
    cur.execute(seznam[1])
    print("Narejena tabela %s" % seznam[0])
    conn.commit()

def pobrisi_tabelo(tabela):
    cur.execute("""
        DROP TABLE %s;
    """ % tabela[0])
    print("Izbrisana tabela %s" %tabela[0])
    conn.commit()

def uvozi_podatke(seznam):
    with open("podatki_novi.csv") as f:
        rd = csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        idd = 0
        for r in rd:
            rr = [None if x in ('', ',') else x for x in r]
            r = [idd] + rr
            #print(r)

            cur.execute(seznam[2], r)
            rid, = cur.fetchone()
            print("Uvožena oseba %s z ID-jem %d" % (r[0], rid))
            idd += 1
    conn.commit()

def uvozi_podatke_seznam(tabela, seznam):
    for r in seznam:
        cur.execute(tabela[2], r)
        rid, = cur.fetchone()
        print("Uvožen vod %s z ID-jem %d" % (r[0], rid))
    conn.commit()

def clani_clanarina1():
    cur.execute("""
        SELECT * FROM clani
        WHERE clanarina = 1
    """)
    return cur.fetchall()

conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

def dodaj_stolpec(table, stolpec, datatype):
    cur.execute("""
            ALTER TABLE %s
            ADD %s %s;
        """ % (table, stolpec, datatype))
    conn.commit()


# oseba mora imeti stolpec vod, ki ima vrednosti null
# prostovoljec in udeleženec so tabele z referencami na id akcij in oseb
# janos: če ima puščico, je nov stolpec. če je nima, je nova tabela
# je starš ista finta kot na vajah
# vod INTEGER NOT NULL REFERENCES vod(id)
oseba = ["oseba",
         """
         CREATE TABLE oseba(
            id SERIAL PRIMARY KEY,
            ime TEXT NOT NULL,
            priimek TEXT NOT NULL,
            rojstvo DATE NOT NULL,
            naslov TEXT NOT NULL,
            telefon TEXT,
            mail TEXT,
            clanarina INTEGER NOT NULL,
            zaposlitev TEXT,
            funkcija TEXT
            
            );
         """,
         """
         INSERT INTO oseba
         (id, ime, priimek, rojstvo, naslov, telefon, mail, clanarina, zaposlitev, funkcija)
         VALUES (%s, %s,%s,%s,%s,%s,%s,%s, %s, null)
         RETURNING id
         """]

# naredi 5 akcij
# trajanje: 4ur, 5 dni itd..
akcija = ["akcija",
         """
         CREATE TABLE akcija(
            id SERIAL PRIMARY KEY,
            ime TEXT NOT NULL,
            datum DATE NOT NULL,
            trajanje TEXT NOT NULL,
            organizator INTEGER NOT NULL REFERENCES oseba(id)
            )

        ;
         """,
         """
         INSERT INTO akcija
         (id, ime, datum, trajanje, organizator)
         VALUES (%s,%s,%s,%s,%s)
         RETURNING id
         """]

prostovoljec = ["prostovoljec",
         """
         CREATE TABLE prostovoljec(
            oseba INTEGER NOT NULL REFERENCES oseba(id),
            akcija INTEGER NOT NULL REFERENCES akcija(id)
            )

        ;
         """,
         """
         INSERT INTO prostovoljec
         (oseba, akcija)
         VALUES (%s,%s)
         """]

udelezenec = ["udelezenec",
         """
         CREATE TABLE udelezenec(
            oseba INTEGER NOT NULL REFERENCES oseba(id),
            akcija INTEGER NOT NULL REFERENCES akcija(id)
            )

        ;
         """,
         """
         INSERT INTO udelezenec
         (oseba, akcija)
         VALUES (%s,%s)
         """]

# 3 vode
# ime živali!
# št od 6 do 16 - starost ljudi
vod = ["vod",
         """
         CREATE TABLE vod(
            id SERIAL PRIMARY KEY,
            ime TEXT NOT NULL,
            starost INTEGER NOT NULL,
            termin INTEGER NOT NULL,
            vodnik INTEGER NOT NULL REFERENCES oseba(id)
            )

        ;
         """,
         """
         INSERT INTO vod
         (id, ime, starost, termin, vodnik)
         VALUES (%s, %s,%s,%s,%s)
         RETURNING id
         """]

otroci = ["otroci",
         """
         CREATE TABLE otroci (
         stars INTEGER NOT NULL REFERENCES oseba(id),
         otrok INTEGER NOT NULL REFERENCES oseba(id),
         PRIMARY KEY (stars, otrok),
         CHECK (stars <> otrok)
         );

         """,
         """
         INSERT INTO otroci
         (stars, otrok)
         VALUES (%s,%s)
         RETURNING stars
         """]

seznamVseh = [oseba]

def ustvari_vse_tabele():
    for seznam in seznamVseh:
        ustvari_tabelo(seznam)

def izbrisi_vse_tabele():
    for seznam in seznamVseh:
        pobrisi_tabelo(seznam)


#pobrisi_tabelo(oseba)
#ustvari_tabelo(oseba)
#uvozi_podatke(oseba)

#pobrisi_tabelo(vod)
#ustvari_tabelo(akcija)
#uvozi_podatke_seznam(akcija, akcije)

#pobrisi_tabelo(otroci)
#ustvari_tabelo(otroci)
#uvozi_podatke_seznam(otroci, pari_stars_otrok)

#dodaj_stolpec('oseba', 'vod', 'INTEGER REFERENCES vod(id)')

# for i in range(100):
#     if i in ooo:
#         cur.execute(
#         """UPDATE oseba
#         SET
#         (funkcija) = (%s)
#         WHERE
#         id = %s;""" , ['otrok', i])
#         conn.commit()
#     if i in sss:
#         cur.execute(
#         """UPDATE oseba
#         SET
#         (funkcija) = (%s)
#         WHERE
#         id = %s;""" , ['starš', i])
#         conn.commit()

#ustvari_tabelo(prostovoljec)
#ustvari_tabelo(udelezenec)

# prostovoljci_0 = [7,5,16,12,8,34,99,55]
# prostovoljci_1 = [44,88,64,53,27,54]
# prostovoljci_2 = [85,86,87,88,89,90,97,92,93,94,95,96,97,98,99]
#
# prostovoljci_0 = list(set(prostovoljci_0)-set(pari))
# prostovoljci_1 = list(set(prostovoljci_1)-set(pari))
# prostovoljci_2 = list(set(prostovoljci_2)-set(pari))
#
# udelezenci_0 = []
# udelezenci_1 = []
# udelezenci_2 = []
# for i in range(25,36):
#     udelezenci_0.append(i)
#
# for i in range(35,46):
#     udelezenci_1.append(i)
# for i in range(45,56):
#     udelezenci_2.append(i)
#
# udelezenci_0 = list(set(udelezenci_0)-set(prostovoljci_0)-set(pari))
# udelezenci_1 = list(set(udelezenci_1)-set(prostovoljci_1)-set(pari))
# udelezenci_2 = list(set(udelezenci_2)-set(prostovoljci_2)-set(pari))

# for i in prostovoljci_2:
#     cur.execute(
#      """
#     INSERT
#     INTO
#     prostovoljec(oseba, akcija)
#     VALUES(%s, %s);""" % (i, 2))
#     conn.commit()
#
# cur.execute(
#     """UPDATE oseba
#     SET
#     (funkcija) = (%s)
#     WHERE
#     id = %s;""", ['načelnik', 73])
# conn.commit()
#
# cur.execute(
#     """UPDATE oseba
#     SET
#     (funkcija) = (%s)
#     WHERE
#     id = %s;""", ['starešina', 74])
# conn.commit()
#
# cur.execute(
#     """UPDATE oseba
#     SET
#     (funkcija) = (%s)
#     WHERE
#     id = %s;""", ['MČ načelnik', 99])
# conn.commit()

funkcije_oseb_id = [44, 46, 52, 67, 70, 85]
funkcije_oseb = ['GG načelnik', 'PP načelnik', 'RR načelnik', 'gospodar', 'tajnik', 'blagajnik']
vodniki = [73, 74, 99]

pari = list(set(ooo+sss))


neaktivni_id = list(set(list(range(100)))-set(funkcije_oseb_id)-set(pari)-set(vodniki))

print(len(pari)+len(neaktivni_id)+len(funkcije_oseb_id)+len(vodniki))

# for l in range(len(funkcije_oseb_id)):
#     cur.execute(
#     """UPDATE oseba
#     SET
#     (funkcija) = (%s)
#     WHERE
#     id = %s;""" , [funkcije_oseb[l], funkcije_oseb_id[l]])
#     conn.commit()

# for l in range(len(neaktivni_id)):
#     cur.execute(
#     """UPDATE oseba
#     SET
#     (funkcija) = (%s)
#     WHERE
#     id = %s;""" , ['neaktiven', neaktivni_id[l]])
#     conn.commit()