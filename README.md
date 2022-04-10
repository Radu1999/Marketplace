Nume: Chivereanu Radu-Gabriel
Grupă: 335CA

# Tema 1

## Organizare

1. Solutia aleasa foloseste dictionare unde key-urile sunt id uri si values sunt liste.

**_Obligatoriu:_**

- Am implementat enuntul temei folosindu-ma de dictionare care retin pentru un id de producator toate produsele generate de acesta.

- Tema este utila intrucat impinge catre analizarea situatiilor ce pot genera racing conditions si deadlock.
- Implementarea putea fi mai eficienta prin modul de structurare al datelor. (Bottleneck ul este oferit de listele de produse unde operatiile de remove sunt O(n)).
- Zonele care sunt protejate cu lock-uri sunt generarea de id-uri, print-urile, si in metoda add_cart, intrucat acolo se interogheaza daca produsul e available mai intai si abia dupa se pune in cart (intre aceste 2 operatii poate exista racing condition). Modulul de logging este thread safe.

## Implementare

- Intregul enunt al temei este implementat.
- Print este o functie care nu este thread-safe, asa ca am protejat-o cu un lock din obiectul de marketplace al consumatorului. Initial lock-ul era static, in clasa consumator, dar din precizarile temei
  acest lucru nu este permis.
- Lucruri interesante descoperite pe parcurs

## Resurse utilizate

- Pentru modulul de logging: https://stackoverflow.com/questions/40088496/how-to-use-pythons-rotatingfilehandler

## Git

1. https://github.com/Radu1999/Marketplace
