from flask_script import Manager

from jolod import app
from jolod import db

app.config.from_object("config.DevelopmentConfig")

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command("db", MigrateCommand)

if __name__ == "__main__":
    manager.run()
