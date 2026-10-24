import pytest

from app import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app(tmp_path / "test-recipes.db")
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


def test_home_page_shows_recipe_organizer(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Recipe Organizer" in response.data
    assert b"Creamy Tomato Pasta" in response.data


def test_recipe_list_and_search(client):
    response = client.get("/recipes?q=tomato")

    assert response.status_code == 200
    assert b"Creamy Tomato Pasta" in response.data
    assert b"Mango Yogurt Bowl" not in response.data


def test_add_recipe_and_view_details(client):
    response = client.post(
        "/recipes/new",
        data={
            "title": "Garden Salad",
            "category": "Lunch",
            "prep_time": "15",
            "ingredients": "Lettuce\nTomato\nCucumber",
            "instructions": "Wash the vegetables.\nChop and toss together.",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Garden Salad" in response.data
    assert b"Chop and toss together." in response.data


def test_add_recipe_requires_all_fields(client):
    response = client.post(
        "/recipes/new",
        data={"title": "Incomplete recipe"},
    )

    assert response.status_code == 200
    assert b"Please complete every field" in response.data


def test_unknown_recipe_returns_not_found(client):
    response = client.get("/recipes/999")

    assert response.status_code == 404


def test_health_check(client):
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json == {"status": "ok"}
