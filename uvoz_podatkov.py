import pomozne_funkcije as pf

pari_stars_otrok = [[13, 25],[17,26],[77,82],[11,5],[13,33],[13,14],[16,19],[17,88],[1,6],[1,7],[27,66],[54,72],[8,15]]



ooo = []
sss = []
for [i,j] in pari_stars_otrok:
    sss.append(i)
    ooo.append(j)

ooo = list(set(ooo))
sss = list(set(sss))
pari = list(set(sss + ooo))


funkcije_oseb_id = [44, 46, 52, 67, 70, 85]
funkcije_oseb = ['GG načelnik', 'PP načelnik', 'RR načelnik', 'gospodar', 'tajnik', 'blagajnik']
vodniki = [73, 74, 99]

neaktivni_id = list(set(list(range(100)))-set(funkcije_oseb_id)-set(pari)-set(vodniki))

####VODI

vod_prasec = [25, 26, 82, 5]
vod_vombat = [33, 14, 19, 88]
vod_veverice = [66, 6, 7, 72, 15]

vodi = [[0, 'krškopoljski prašiči', 8, 3, 73], [1, 'vombati', 11, 2, 74], [2, 'leteče veverice', 16, 4, 99]]

prostovoljci_0 = [7,5,16,12,8,34,99,55]
prostovoljci_1 = [44,88,64,53,27,54]
prostovoljci_2 = [85,86,87,88,89,90,97,92,93,94,95,96,97,98,99]

prostovoljci_0 = list(set(prostovoljci_0)-set(pari))
prostovoljci_1 = list(set(prostovoljci_1)-set(pari))
prostovoljci_2 = list(set(prostovoljci_2)-set(pari))

udelezenci_0 = []
udelezenci_1 = []
udelezenci_2 = []
for i in range(25,36):
    udelezenci_0.append(i)

for i in range(35,46):
    udelezenci_1.append(i)
for i in range(45,56):
    udelezenci_2.append(i)

udelezenci_0 = list(set(udelezenci_0)-set(prostovoljci_0)-set(pari))
udelezenci_1 = list(set(udelezenci_1)-set(prostovoljci_1)-set(pari))
udelezenci_2 = list(set(udelezenci_2)-set(prostovoljci_2)-set(pari))


akcije = [[0, 'Izlet v neznano', '01-01-2018', '8h', 2], [1, 'Izlet v znano', '05-06-2017', '24h', 7], [2, 'Izlet v NY', '11-09-2001', '3dni', 98]]

####################################################################################################
####################################################################################################





###TABELA OSEBA
pf.uvozi_podatke(oseba)

#stolpec vod
#(tole sva zgleda povozila)

#stolpec funkcija

for i in range(100):
    if i in ooo:
        cur.execute(
        """UPDATE oseba
        SET
        (funkcija) = (%s)
        WHERE
        id = %s;""" , ['otrok', i])
        conn.commit()
    if i in sss:
        cur.execute(
        """UPDATE oseba
        SET
        (funkcija) = (%s)
        WHERE
        id = %s;""" , ['starš', i])
        conn.commit()


cur.execute(
    """UPDATE oseba
    SET
    (funkcija) = (%s)
    WHERE
    id = %s;""", ['načelnik', 73])
conn.commit()

cur.execute(
    """UPDATE oseba
    SET
    (funkcija) = (%s)
    WHERE
    id = %s;""", ['starešina', 74])
conn.commit()

cur.execute(
    """UPDATE oseba
    SET
    (funkcija) = (%s)
    WHERE
    id = %s;""", ['MČ načelnik', 99])
conn.commit()


for l in range(len(funkcije_oseb_id)):
    cur.execute(
    """UPDATE oseba
    SET
    (funkcija) = (%s)
    WHERE
    id = %s;""" , [funkcije_oseb[l], funkcije_oseb_id[l]])
    conn.commit()

for l in range(len(neaktivni_id)):
    cur.execute(
    """UPDATE oseba
    SET
    (funkcija) = (%s)
    WHERE
    id = %s;""" , ['neaktiven', neaktivni_id[l]])
    conn.commit()



#####akcije, prostovoljci, udelezenci


pf.uvozi_podatke_seznam(akcija, akcije)

for i in prostovoljci_0:
    cur.execute(
     """
    INSERT
    INTO
    prostovoljec(oseba, akcija)
    VALUES(%s, %s);""" % (i, 0))
    conn.commit()

for i in prostovoljci_1:
    cur.execute(
     """
    INSERT
    INTO
    prostovoljec(oseba, akcija)
    VALUES(%s, %s);""" % (i, 1))
    conn.commit()

for i in prostovoljci_2:
    cur.execute(
     """
    INSERT
    INTO
    prostovoljec(oseba, akcija)
    VALUES(%s, %s);""" % (i, 2))
    conn.commit()

#####otroci starsi
pf.uvozi_podatke_seznam(otroci, pari_stars_otrok)