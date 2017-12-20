# SecretSanta
Really rather simple to set-up and to use system for secret santa but with some important additions like secretly shared
shopping lists and gifting constraints (avoid gifts between family members for ex.).

## Setup
0. Install Python (3.6)
1. Install requirements (`pip3 install requirements.txt`)
2. Set up PostgresSQL with the table `jolod`, with `INTEGER` column `user_id` and JSON column `notes` and update your usernames and passwords in the config file
2. Start it with python then either modify the built-in variables to enter information abour your families or use `/setup`
3. Generate graph with `/recreategraph`
4. Stop using the built-in developement server and disable debug mode
5. Set up uwsgi and nginx as you wish.
6. Use nginx to manage the mandatory basic HTTP auth properly.
7. You're done.