from flask_script import Manager
from flask_script import Manager
from yetanotherpaste import app
from yetanotherpaste import db

app.config.from_object("config.DevelopmentConfig")

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command("db", MigrateCommand)

if __name__ == "__main__":
    manager.run()
