import asyncio

import pytest

import mealie.services.openai.openai as openai_module
from mealie.schema.openai.recipe_nutrition import OpenAINutrition, OpenAIRecipeNutritionEstimate
from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_ingredient import RecipeIngredient
from mealie.services.openai import OpenAIRecipeNutritionService, OpenAIService


class _SettingsStub:
    OPENAI_ENABLED = True
    OPENAI_MODEL = "gpt-4o"
    OPENAI_AUDIO_MODEL = "whisper-1"
    OPENAI_WORKERS = 1
    OPENAI_SEND_DATABASE_DATA = False
    OPENAI_ENABLE_IMAGE_SERVICES = True
    OPENAI_ENABLE_TRANSCRIPTION_SERVICES = True
    OPENAI_CUSTOM_PROMPT_DIR = None
    OPENAI_BASE_URL = None
    OPENAI_API_KEY = "dummy"
    OPENAI_REQUEST_TIMEOUT = 30
    OPENAI_CUSTOM_HEADERS: dict = {}
    OPENAI_CUSTOM_PARAMS: dict = {}


@pytest.fixture()
def openai_settings(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(openai_module, "get_app_settings", lambda: _SettingsStub())


def test_openai_recipe_nutrition_service(openai_settings: None, monkeypatch: pytest.MonkeyPatch):
    async def mock_get_response(self, prompt: str, message: str, *args, **kwargs):
        assert prompt == "nutrition prompt"
        assert '"recipeServings":4' in message
        assert '"food":"flour"' in message
        return OpenAIRecipeNutritionEstimate(
            nutrition=OpenAINutrition(calories="250", protein_content="8"),
            assumptions=["Assumed all-purpose flour."],
            warnings=["Salt was ignored."],
        )

    monkeypatch.setattr(OpenAIService, "get_prompt", lambda self, name: "nutrition prompt")
    monkeypatch.setattr(OpenAIService, "get_response", mock_get_response)

    recipe = Recipe(
        name="Pancakes",
        recipe_servings=4,
        recipe_ingredient=[
            RecipeIngredient(quantity=2, unit="cups", food="flour"),
            RecipeIngredient(note="salt to taste"),
        ],
    )

    result = asyncio.run(OpenAIRecipeNutritionService().estimate(recipe))

    assert result.nutrition.calories == "250"
    assert result.nutrition.protein_content == "8"
    assert result.servings_used == 4
    assert result.assumptions == ["Assumed all-purpose flour."]
    assert result.warnings == ["Salt was ignored."]


def test_openai_recipe_nutrition_service_requires_servings(openai_settings: None):
    recipe = Recipe(
        name="Soup",
        recipe_servings=0,
        recipe_ingredient=[RecipeIngredient(note="1 onion")],
    )

    with pytest.raises(ValueError, match="greater than 0"):
        asyncio.run(OpenAIRecipeNutritionService().estimate(recipe))
