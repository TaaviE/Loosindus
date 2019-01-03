# SecretSanta
[![Liberapay Status](https://img.shields.io/liberapay/patrons/Taavi.svg?logo=liberapay)](https://liberapay.com/Taavi)
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2FTaaviE%2FSecretSanta.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2FTaaviE%2FSecretSanta?ref=badge_shield)

Really rather simple to set-up and to use system for secret santa but with some important additions like secretly shared
shopping lists and gifting constraints (avoid gifts between family members for ex.). Minimum 4 users for minimal functionality. The [version hosted by](https://jolod.aegrel.ee) me (TaaviE) is being actively used, but is the place where I field-test my changes so it might sometimes break.

## Eesti keeles

Lihtne veebiliides loosipakkide tegemiseks - lubab igal kasutajal koostada enda soovinimekirja ning seda enda salajase "jõuluvanaga" jagada (tegelikult saavad nimekirja vaadata ka ülejäänud grupi liikmed). Loosipakid üksteise vahel jagab süsteem soovi korral automaatselt, vältides perekonnaliikmetevahelisi kinke ja eelmisel aastal loodud kombinatsioone. Süsteem lubab pärast seadistamist sisse logida ka ID-kaardiga. Minimaalne soovituslik kasutajate hulk tarkvara kasutamiseks on neli inimest. Minu hallatud [versioon](https://jolod.aegrel.ee) on aktiivses kasutuses, kuid ma kasutan seda muudatuste aktiivseks testimises seega see võib vahepeal mõne veaga olla.

## Setup (if you wish to self-host)
 1. Install Python 3 (Developed on 3.7)
 2. Make a virtual environment (`python3 -m venv .venv && source .venv/bin/activate`)
 3. Install wheel with pip (`python3 -m pip install wheel`)
 4. Install requirements (`python3 -m pip install -r requirements.txt`)
 5. Set up PostgreSQL with the script in `init_db.sql`
 6. Set up uwsgi/gunicorn and nginx as you wish (to provide TLS)
 7. **UPDATE THE CONFIGURATION** and sitemap to your own URL 
 8. Estonian ID card support requires a subdomain and additional nginx configuration, if you don't configure it the option will just not work
 9. You're done. Use `/profile` or `/settings` to configure your account. Configuring groups and families currently has to be done manually in the database

## My wishlist for future changes

  * All .css and other content should have a SRI hash included, generate that based on files themselves
  * Make sure you load the production config to properly validate the captchas and to enable additional security measures that are extremely important
  * Allow multiple groups - currently they're technically possible to create but the UI doesn't display buttons for the groups
  * Allow multiple families for user - same as previous, technically possible but no UI support
  * Allow reshuffling with a button from the UI with confirmation - the button doesn't exist because it's really disruptive and could be accidentally clicked D:
  * Add more configuration options for users - add name changes, profile pictures
  * Add comments for wishes
  * Reimplement email sending

## License
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2FTaaviE%2FSecretSanta.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2FTaaviE%2FSecretSanta?ref=badge_large)
