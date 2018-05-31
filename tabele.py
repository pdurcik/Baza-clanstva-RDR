import clani as pf



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
vse_tabele = [oseba, akcija, vod, otroci, udelezenec, prostovoljec]
#
# for tabela in vse_tabele:
#     pf.pobrisi_tabelo(tabela)
#     pf.ustvari_tabelo(tabela)
#stolpec vod v tabelo oseba

#pf.dodaj_stolpec('oseba', 'vod', 'INTEGER REFERENCES vod(id)')


print('haha')