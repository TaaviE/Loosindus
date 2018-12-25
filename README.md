# SecretSanta
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2FTaaviE%2FSecretSanta.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2FTaaviE%2FSecretSanta?ref=badge_shield)

Really rather simple to set-up and to use system for secret santa but with some important additions like secretly shared
shopping lists and gifting constraints (avoid gifts between family members for ex.). Minimum 

## Setup
 1. Install Python 3 (Developed on 3.7)
 2. Make a virtual environment (`python3 -m venv .venv && source .venv/bin/activate`)
 3. Install wheel with pip (`python3 -m pip install wheel`)
 4. Install requirements (`python3 -m pip install -r requirements.txt`)
 5. Set up PostgreSQL with the script in `init_db.sql`
 6. Set up uwsgi/gunicorn and nginx as you wish (to provide TLS)
 7. **UPDATE THE CONFIGURATION** and sitemap to your own URL 
 8. Estonian ID card support requires a subdomain and additional nginx configuration, if you don't configure it the option will just not work
 9. You're done. Use `/profile` or `/settings` to configure your account. Configuring groups and families currently has to be done manually in the database

## Wishlists

  * All .css and other content should have a SRI hash included, make sure to update it after changing a file
  * Make sure you load the production config to properly validate the captchas and to enable additional security measures that are extremely important

## License
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2FTaaviE%2FSecretSanta.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2FTaaviE%2FSecretSanta?ref=badge_large)

## Eesti keeles

Lihtne veebiliides loosipakkide tegemiseks - lubab igal kasutajal koostada enda soovinimekirja ning seda enda salajase "jõuluvanaga" jagada. Loosipakid üksteise vahel jagab süsteem soovi korral automaatselt, vältides perekonnasiseseid kinke ja eelmisel aastal olnud kombinatsioone. Süsteem lubab pärast seadistamist sisse logida ka ID-kaardiga. Minimaalne soovituslik kasutajate hulk tarkvara kasutamiseks on neli inimest.
