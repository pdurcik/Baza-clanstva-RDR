# uvozimo ustrezne podatke za povezavo
import auth
auth.db = "sem2018_%s" % auth.user

from random import randint
import itertools

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import csv


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


def izbrisi_vse_tabele():
    for seznam in seznamVseh:
        pobrisi_tabelo(seznam)


