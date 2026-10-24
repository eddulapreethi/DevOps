import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from flask import Flask, abort, redirect, render_template, request, url_for


SEED_RECIPES = [
    (
        "Creamy Tomato Pasta",
        "Dinner",
        25,
        "Pasta, crushed tomatoes, cream, garlic, olive oil, parmesan",
        "Cook the pasta until al dente.\nSaute garlic in olive oil and stir in tomatoes and cream.\nToss the sauce with pasta and finish with parmesan.",
    ),
    (
        "Avocado Breakfast Toast",
        "Breakfast",
        10,
        "Sourdough bread, ripe avocado, lemon, chilli flakes, salt",
        "Toast the sourdough until golden.\nMash avocado with lemon and salt.\nSpread over toast and finish with chilli flakes.",
    ),
    (
        "Mango Yogurt Bowl",
        "Dessert",
        5,
        "Mango, plain yogurt, granola, honey",
        "Dice the mango.\nSpoon yogurt into a bowl and top with mango and granola.\nDrizzle with honey to serve.",
    ),
]


def create_app(database_path=None):
    app = Flask(__name__)
    app.config["DATABASE_PATH"] = str(
        database_path
        or os.environ.get(
            "DATABASE_PATH", Path(app.instance_path) / "recipes.db"
        )
    )
    Path(app.config["DATABASE_PATH"]).parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connect_db():
        connection = sqlite3.connect(app.config["DATABASE_PATH"])
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    with connect_db() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                prep_time INTEGER NOT NULL,
                ingredients TEXT NOT NULL,
                instructions TEXT NOT NULL
            )
            """
        )
        recipe_count = connection.execute(
            "SELECT COUNT(*) FROM recipes"
        ).fetchone()[0]
        if recipe_count == 0:
            connection.executemany(
                """
                INSERT INTO recipes
                    (title, category, prep_time, ingredients, instructions)
                VALUES (?, ?, ?, ?, ?)
                """,
                SEED_RECIPES,
            )

    @app.route("/")
    def index():
        with connect_db() as connection:
            recipes = connection.execute(
                "SELECT * FROM recipes ORDER BY id DESC LIMIT 3"
            ).fetchall()
            total_recipes = connection.execute(
                "SELECT COUNT(*) FROM recipes"
            ).fetchone()[0]
        return render_template(
            "index.html", recipes=recipes, total_recipes=total_recipes
        )

    @app.route("/recipes")
    def recipes():
        search = request.args.get("q", "").strip()
        with connect_db() as connection:
            if search:
                matching_recipes = connection.execute(
                    """
                    SELECT * FROM recipes
                    WHERE title LIKE ? OR category LIKE ?
                    ORDER BY title
                    """,
                    (f"%{search}%", f"%{search}%"),
                ).fetchall()
            else:
                matching_recipes = connection.execute(
                    "SELECT * FROM recipes ORDER BY title"
                ).fetchall()
        return render_template(
            "recipes.html", recipes=matching_recipes, search=search
        )

    @app.route("/recipes/new", methods=["GET", "POST"])
    def add_recipe():
        error = None
        form = request.form if request.method == "POST" else {}
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            category = request.form.get("category", "").strip()
            prep_time = request.form.get("prep_time", "").strip()
            ingredients = request.form.get("ingredients", "").strip()
            instructions = request.form.get("instructions", "").strip()

            if not all((title, category, prep_time, ingredients, instructions)):
                error = "Please complete every field before saving your recipe."
            elif len(title) > 100 or len(category) > 50:
                error = "Keep the recipe name under 100 characters and category under 50."
            else:
                try:
                    prep_time_minutes = int(prep_time)
                except ValueError:
                    prep_time_minutes = 0

                if not 1 <= prep_time_minutes <= 1440:
                    error = "Preparation time must be between 1 and 1440 minutes."
                else:
                    with connect_db() as connection:
                        cursor = connection.execute(
                            """
                            INSERT INTO recipes
                                (title, category, prep_time, ingredients, instructions)
                            VALUES (?, ?, ?, ?, ?)
                            """,
                            (
                                title,
                                category,
                                prep_time_minutes,
                                ingredients,
                                instructions,
                            ),
                        )
                        recipe_id = cursor.lastrowid
                    return redirect(url_for("recipe_detail", recipe_id=recipe_id))

        return render_template("add_recipe.html", error=error, form=form)

    @app.route("/recipes/<int:recipe_id>")
    def recipe_detail(recipe_id):
        with connect_db() as connection:
            recipe = connection.execute(
                "SELECT * FROM recipes WHERE id = ?", (recipe_id,)
            ).fetchone()
        if recipe is None:
            abort(404)
        return render_template(
            "recipe_detail.html",
            recipe=recipe,
            ingredients=recipe["ingredients"].splitlines(),
            instructions=recipe["instructions"].splitlines(),
        )

    @app.route("/healthz")
    def health_check():
        return {"status": "ok"}, 200

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
