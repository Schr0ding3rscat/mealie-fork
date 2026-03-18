from pydantic import BaseModel, ConfigDict, Field

from mealie.schema._mealie import MealieModel
from mealie.schema.recipe.recipe_nutrition import Nutrition

# TODO: Should these exist?!?!?!?!?


class RecipeSlug(MealieModel):
    slug: str


class SlugResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": "adult-mac-and-cheese"})


class UpdateImageResponse(BaseModel):
    image: str


class RecipeDuplicate(BaseModel):
    name: str | None = None


class RecipeNutritionEstimateResponse(MealieModel):
    nutrition: Nutrition
    assumptions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    servings_used: float
