#!/usr/bin/env bash
# Extract translations to file
pybabel extract -F translations/babel.cfg -k lazy_gettext -o translations/messages.pot .

# Initialize a translation
#pybabel init -i translations/messages.pot -d translations -l ee

# Update translations
pybabel update -i translations/messages.pot -d translations

# Update individual translations
#pybabel update -i translations/messages.pot -d translations -l en

# Compile translations
pybabel compile -d translations