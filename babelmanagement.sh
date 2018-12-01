#!/usr/bin/env bash
# Extract translations to file
pybabel extract -F translations/babel.cf -k lazy_gettext -o translations/messages.pot .

# Initialize a translation
pybabel init -i translations/messages.pot -d translations -l ee

# Compile translations
pybabel compile -d translations

# Update translations
pybabel update -i translations/messages.pot -d translations

# Update individual translations
pybabel update -i translations/messages.pot -d translations -l en
