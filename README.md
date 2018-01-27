# SecretSanta
Really rather simple to set-up and to use system for secret santa but with some important additions like secretly shared
shopping lists and gifting constraints (avoid gifts between family members for ex.).

## Setup
0. Install Python (3.6)
1. Install requirements (`pip3 install -r requirements.txt`)
2. Set up PostgresSQL with the script in `init_db.sql`
3. Set up uwsgi/gunicorn and nginx as you wish (to provide TLS)
4. You're done. Use `/profile` or `/settings` to configure your account.

## Wishlists

* All .css and other content should have a SRI hash included, make sure to update it after changing a file
* Make sure you load the production config to properly validate the captchas and to enable additional security measures that are extremely important