import json
from typing import Any

from mealie.schema.openai.recipe_nutrition import OpenAIRecipeNutritionEstimate
from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_nutrition import Nutrition
from mealie.schema.recipe.request_helpers import RecipeNutritionEstimateResponse

from .openai import OpenAIService


class OpenAIRecipeNutritionService:
    @staticmethod
    def _ingredient_payload(recipe: Recipe) -> list[dict[str, Any]]:
        ingredients: list[dict[str, Any]] = []
        for ingredient in recipe.recipe_ingredient:
            unit_name = ingredient.unit.name if ingredient.unit else None
            food_name = ingredient.food.name if ingredient.food else None
            ingredients.append(
                {
                    "originalText": ingredient.original_text or None,
                    "display": ingredient.display or None,
                    "quantity": ingredient.quantity,
                    "unit": unit_name,
                    "food": food_name,
                    "note": ingredient.note or None,
                }
            )
        return ingredients

    @classmethod
    def _build_message(cls, recipe: Recipe) -> str:
        return json.dumps(
            {
                "name": recipe.name,
                "recipeServings": recipe.recipe_servings,
                "recipeYield": recipe.recipe_yield,
                "recipeYieldQuantity": recipe.recipe_yield_quantity,
                "ingredients": cls._ingredient_payload(recipe),
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )

    async def estimate(self, recipe: Recipe) -> RecipeNutritionEstimateResponse:
        if recipe.recipe_servings <= 0:
            raise ValueError("Recipe servings must be greater than 0")

        if not recipe.recipe_ingredient:
            raise ValueError("Recipe must include at least one ingredient")

        service = OpenAIService()
        prompt = service.get_prompt("recipes.calculate-recipe-nutrition")
        response = await service.get_response(
            prompt,
            self._build_message(recipe),
            response_schema=OpenAIRecipeNutritionEstimate,
        )

        if response is None:
            raise ValueError("No response from OpenAI")

        return RecipeNutritionEstimateResponse(
            nutrition=Nutrition.model_validate(response.nutrition.model_dump()),
            assumptions=response.assumptions,
            warnings=response.warnings,
            servings_used=recipe.recipe_servings,
        )
