from pydantic import Field

from ._base import OpenAIBase


class OpenAINutrition(OpenAIBase):
    calories: str | None = Field(
        None, description="Calories per serving as a plain number string without units when possible."
    )
    carbohydrate_content: str | None = Field(
        None, description="Carbohydrates per serving in grams as a plain number string."
    )
    cholesterol_content: str | None = Field(
        None, description="Cholesterol per serving in milligrams as a plain number string."
    )
    fat_content: str | None = Field(None, description="Fat per serving in grams as a plain number string.")
    fiber_content: str | None = Field(None, description="Fiber per serving in grams as a plain number string.")
    protein_content: str | None = Field(None, description="Protein per serving in grams as a plain number string.")
    saturated_fat_content: str | None = Field(
        None, description="Saturated fat per serving in grams as a plain number string."
    )
    sodium_content: str | None = Field(
        None, description="Sodium per serving in milligrams as a plain number string."
    )
    sugar_content: str | None = Field(None, description="Sugar per serving in grams as a plain number string.")
    trans_fat_content: str | None = Field(
        None, description="Trans fat per serving in grams as a plain number string."
    )
    unsaturated_fat_content: str | None = Field(
        None, description="Unsaturated fat per serving in grams as a plain number string."
    )


class OpenAIRecipeNutritionEstimate(OpenAIBase):
    nutrition: OpenAINutrition = Field(..., description="Estimated nutrition facts per serving.")
    assumptions: list[str] = Field(default_factory=list, description="Reasonable assumptions made during estimation.")
    warnings: list[str] = Field(default_factory=list, description="Warnings about ambiguity or missing data.")
