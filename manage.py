from flask_migrate import Migrate
from app import create_app
from app.extensions import db
from scripts.seed_db import seed_initial_data


app = create_app()
migrate = Migrate(app, db)


@app.cli.command()
def seed():
    """Seed the database with data."""
    seed_initial_data()
    print("Data inserted successfully.")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
