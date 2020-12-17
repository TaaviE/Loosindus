# Loosindus

A really simple to configure and to use system for secret santa but with some important additions like secretly shared
shopping lists and gifting constraints (avoid matches between family members for ex.).

Features:
  * Keeps the secret in "Secret Santa", a lot of effort has gone into hiding both the santas and possible gifts
  * Very simple to use
  * Possibility to share gift wishlists with people to avoid duplicate gifts and other hassle coordinating gifts
  * Best possible gift target and receiver generation to avoid combinations that would ruin the surprise
  * Responsive design - desktops, tablets, phones and even Kindles are supported - no massive JS dependencies, minimal or no Javascript on pages. All critical pages should also work without JS.
  * Supports multiple events, multiple groups and multiple families at the same time, with optional advanced features
  * Supports Estonian ID card authentication


For self-hosters:
  * Works very well with Content Security Policy - no need for 'inline'-anything
  * The app is intended to be used with multiple families, but it is okay if there's only one family in the group or one-person families in the group
  * The amount of groups an user can be in is not limited (multiple secret santa events at the same time)
  * The [version hosted by me](https://jolod.aegrel.ee) (TaaviE) is being actively used, but is the place where I beta-test my changes so it might sometimes break
  * Estonian (and other client TLS cert) authentication with Flask-Security requires extra configuration

## Eesti keeles

Lihtne veebiliides loosipakkide tegemiseks - lubab igal kasutajal koostada enda soovinimekirja ning seda enda salajase "jõuluvanaga" jagada (nimekirja saavad vaadata ka ülejäänud grupi liikmed).
Loosipakid üksteise vahel jagab süsteem soovi korral automaatselt, vältides perekonnaliikmete vahelisi kinke ja eelmisel aastal loodud kombinatsioone.
Eesmärk on suurendada üllatusmomenti, samal ajal vältides halbu kingitusi ning duplikaate (iga soovi saab kingi saaja suhtes varjatult broneerituks märkida).
Süsteem lubab pärast seadistamist sisse logida ka ID-kaardiga, Google konto jt.
Minimaalne kasutajate hulk tarkvara kasutamiseks on loogiliselt neli inimest.
Minu hallatud [instants](https://jolod.aegrel.ee) on aktiivses kasutuses, kuid ma kasutan seda muudatuste aktiivseks testimiseks seega see võib vahepeal mõne veaga olla.

## Setup (if you wish to self-host)

My aim is to keep this project as simple as possible in every aspect, including deploying.

 1. Install Python 3.8 (No, older versions do not work)
 2. Make a virtual environment (`python3 -m venv .venv && source .venv/bin/activate`)
 3. Install wheel with pip (`python3 -m pip install wheel`)
 4. Install requirements (`python3 -m pip install -r requirements.txt`)
 5. Set up PostgreSQL with the script in `init_db.sql`
 6. Set up uwsgi/gunicorn and nginx
 7. **UPDATE THE CONFIGURATION** - this is so critical that everything will break if you don't, not kidding
 8. Estonian ID card support requires a subdomain and additional nginx configuration, if you don't configure it, it will just not work
 9. You're done. Use the setup wizard to begin.

In case this above was too complex you can just use the version hosted by me and ask if you need any help.

## Planned development

  * Check the GitHub Projects tab
  * If you have requests or issues, open an issue on GitHub

## Donations

  * [![Liberapay Status](https://img.shields.io/liberapay/patrons/Taavi.svg?logo=liberapay)](https://liberapay.com/Taavi)

### Keywords

  * Kingituste tegemise rakendus
  * Kingituste loosimine
  * Secret santa web application
  * Loosipakkide tegemise rakendus
  * Loosipakkide loosimine
  * Loosipakirakendus
