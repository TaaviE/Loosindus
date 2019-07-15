# SecretSanta
[![Liberapay Status](https://img.shields.io/liberapay/patrons/Taavi.svg?logo=liberapay)](https://liberapay.com/Taavi)
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2FTaaviE%2FLoosindus.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2FTaaviE%2FLoosindus?ref=badge_shield)

A really simple to configure and to use system for secret santa but with some important additions like secretly shared
shopping lists and gifting constraints (avoid matches between family members for ex.).

Features and requirements:
  * Mobile- and Kindle-friendly - no massive dependencies, minimal or no Javascript on pages. All critical pages also work without JS and there's a nice script for precompressing everything for fast loading everything even when clients have a slow connection or your server is just a Raspberry Pi
  * It's relatively fast (for Python) - the code hasn't been heavily optimized but common pages load sub-second served by mediocre hardware
  * The UI is as simple as possible to make it usable for everyone
  * No Python 2
  * Works fairly well with Content Security Policy - no need for 'inline'-anything
  * Minimum of 4 users are required for any functionality - there's simply nothing secret when you have less than four people
  * The [version hosted by me](https://jolod.aegrel.ee) (TaaviE) is being actively used, but is the place where I field-test my changes so it might sometimes break
  * The app is intended to be used with multiple families, but it is okay if there's only one family in the group or one-person families in the group
  * The amount of groups an user can be in is technically not limited (multiple secret santa events at the same time) but the UI can't handle displaying it for that user, this limitation will be fixed in future versions
  * Implements Estonian ID card authentication that integrates with Flask-Security

## Eesti keeles

Lihtne veebiliides loosipakkide tegemiseks - lubab igal kasutajal koostada enda soovinimekirja ning seda enda salajase "jõuluvanaga" jagada (nimekirja saavad vaadata ka ülejäänud grupi liikmed). Loosipakid üksteise vahel jagab süsteem soovi korral automaatselt, vältides perekonnaliikmete vahelisi kinke ja eelmisel aastal loodud kombinatsioone. Eesmärk on suurendada üllatusmomenti, samal ajal vältides halbu kingitusi ning duplikaate (iga soovi saab kingi saaja suhtes varjatult broneerituks märkida). Süsteem lubab pärast seadistamist sisse logida ka ID-kaardiga, Google konto jt. Minimaalne soovituslik kasutajate hulk tarkvara kasutamiseks on neli inimest. Minu hallatud [instants](https://jolod.aegrel.ee) on aktiivses kasutuses, kuid ma kasutan seda muudatuste aktiivseks testimiseks seega see võib vahepeal mõne veaga olla.

## Setup (if you wish to self-host)

My aim is to keep this project as simple as possible in every aspect, including deploying.

 1. Install Python 3 (This application is developed on 3.7)
 2. Make a virtual environment (`python3 -m venv .venv && source .venv/bin/activate`)
 3. Install wheel with pip (`python3 -m pip install wheel`)
 4. Install requirements (`python3 -m pip install -r requirements.txt`)
 5. Set up PostgreSQL with the script in `init_db.sql`, I can't promise flask-sqlalchemy's schema creation will be perfect
 6. Set up uwsgi/gunicorn and nginx as you wish (to provide TLS), this app won't work without TLS, it's hardcoded
 7. **UPDATE THE CONFIGURATION** - this is so critical that everything will break if you don't, not kidding
 8. Estonian ID card support requires a subdomain and additional nginx configuration, if you don't configure it the option will just not work
 9. You're done. Use `/profile` or `/settings` to configure your account. `/recreategraph` to regenerate the gifting graph. Configuring groups and families currently has to be done manually in the database (trivial many-to-many relationship) but UI is actively being developed. 

In case this above was too complex you can just use the version hosted by me and ask if you need any help.

## Planned development

  * Check the GitHub Projects tab

## License
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2FTaaviE%2FLoosindus.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2FTaaviE%2FLoosindus?ref=badge_large)
