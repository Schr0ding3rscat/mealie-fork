<template>
  <div v-if="valueNotNull || edit || showEstimateAction">
    <BaseDialog
      v-model="estimateDialog"
      :title="$t('recipe.nutrition-estimate-preview')"
      :icon="$globals.icons.robot"
      :submit-text="$t('recipe.overwrite-nutrition')"
      can-submit
      @submit="applyEstimate"
    >
      <v-card-text class="pb-2">
        <p class="mb-4">
          {{ $t("recipe.nutrition-estimate-preview-description", { servings: estimateResult?.servingsUsed ?? recipe.recipeServings }) }}
        </p>

        <v-row>
          <v-col cols="12" md="6">
            <div class="text-subtitle-2 mb-2">
              {{ $t("recipe.current-nutrition-values") }}
            </div>
            <v-list density="compact" class="border rounded">
              <v-list-item
                v-for="(item, key, index) in currentRenderedList"
                :key="`current-${index}`"
                style="min-height: 25px"
              >
                <v-list-item-title class="pl-2 d-flex">
                  <div>{{ item.label }}</div>
                  <div class="ml-auto mr-1">
                    {{ item.value }}
                  </div>
                  <div>{{ item.suffix }}</div>
                </v-list-item-title>
              </v-list-item>
              <v-list-item v-if="Object.keys(currentRenderedList).length === 0">
                <v-list-item-title class="pl-2">
                  {{ $t("recipe.no-nutrition-values") }}
                </v-list-item-title>
              </v-list-item>
            </v-list>
          </v-col>
          <v-col cols="12" md="6">
            <div class="text-subtitle-2 mb-2">
              {{ $t("recipe.proposed-nutrition-values") }}
            </div>
            <v-list density="compact" class="border rounded">
              <v-list-item
                v-for="(item, key, index) in estimatedRenderedList"
                :key="`estimated-${index}`"
                style="min-height: 25px"
              >
                <v-list-item-title class="pl-2 d-flex">
                  <div>{{ item.label }}</div>
                  <div class="ml-auto mr-1">
                    {{ item.value }}
                  </div>
                  <div>{{ item.suffix }}</div>
                </v-list-item-title>
              </v-list-item>
              <v-list-item v-if="Object.keys(estimatedRenderedList).length === 0">
                <v-list-item-title class="pl-2">
                  {{ $t("recipe.no-nutrition-values") }}
                </v-list-item-title>
              </v-list-item>
            </v-list>
          </v-col>
        </v-row>

        <v-alert
          v-if="estimateResult?.warnings.length"
          type="warning"
          variant="tonal"
          class="mt-4"
        >
          <div class="font-weight-medium mb-1">
            {{ $t("recipe.nutrition-estimate-warnings") }}
          </div>
          <ul class="pl-4 mb-0">
            <li v-for="(warning, index) in estimateResult?.warnings" :key="`warning-${index}`">
              {{ warning }}
            </li>
          </ul>
        </v-alert>

        <v-alert
          v-if="estimateResult?.assumptions.length"
          type="info"
          variant="tonal"
          class="mt-4"
        >
          <div class="font-weight-medium mb-1">
            {{ $t("recipe.nutrition-estimate-assumptions") }}
          </div>
          <ul class="pl-4 mb-0">
            <li v-for="(assumption, index) in estimateResult?.assumptions" :key="`assumption-${index}`">
              {{ assumption }}
            </li>
          </ul>
        </v-alert>
      </v-card-text>
    </BaseDialog>

    <v-card class="mt-2">
      <v-card-title class="pt-2 pb-0 d-flex align-center">
        <span>{{ $t("recipe.nutrition") }}</span>
        <v-spacer />
        <BaseButton
          v-if="showEstimateAction"
          size="small"
          color="info"
          :loading="isEstimating"
          :disabled="isEstimating"
          @click="calculateNutrition"
        >
          <template #icon>
            {{ $globals.icons.robot }}
          </template>
          {{ $t("recipe.calculate-nutrition-with-ai") }}
        </BaseButton>
      </v-card-title>
      <v-divider class="mx-2 my-1" />
      <v-card-text v-if="edit">
        <div
          v-for="(item, key, index) in modelValue"
          :key="index"
        >
          <v-number-input
            :model-value="modelValue[key] ? Number(modelValue[key]) : null"
            :label="labels[key].label"
            :suffix="labels[key].suffix"
            density="compact"
            autocomplete="off"
            variant="underlined"
            control-variant="stacked"
            inset
            :precision="null"
            :min="0"
            @update:model-value="updateValue(key, $event)"
          />
        </div>
      </v-card-text>
      <v-list
        v-if="showViewer"
        density="compact"
        class="mt-0 pt-0"
      >
        <v-list-item
          v-for="(item, key, index) in renderedList"
          :key="index"
          style="min-height: 25px"
        >
          <v-list-item-title class="pl-2 d-flex">
            <div>{{ item.label }}</div>
            <div class="ml-auto mr-1">
              {{ item.value }}
            </div>
            <div>{{ item.suffix }}</div>
          </v-list-item-title>
        </v-list-item>
      </v-list>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { useNutritionLabels } from "~/composables/recipes";
import type { NoUndefinedField } from "~/lib/api/types/non-generated";
import type { NutritionLabelType } from "~/composables/recipes/use-recipe-nutrition";
import type { Nutrition, Recipe } from "~/lib/api/types/recipe";
import type { RecipeNutritionEstimateResponse } from "~/lib/api/user/recipes/recipe";
import { useUserApi } from "~/composables/api";
import { PageMode, usePageState } from "~/composables/recipe-page/shared-state";
import { alert } from "~/composables/use-toast";
import { useGlobalI18n } from "~/composables/use-global-i18n";

interface Props {
  edit?: boolean;
  recipe: NoUndefinedField<Recipe>;
}
const props = withDefaults(defineProps<Props>(), {
  edit: true,
});

const modelValue = defineModel<Nutrition>({ required: true });

const { $appInfo } = useNuxtApp();
const api = useUserApi();
const i18n = useGlobalI18n();
const { setMode } = usePageState(props.recipe.slug);
const { labels } = useNutritionLabels();
const estimateDialog = ref(false);
const isEstimating = ref(false);
const estimateResult = ref<RecipeNutritionEstimateResponse | null>(null);

const valueNotNull = computed(() => {
  let key: keyof Nutrition;
  for (key in modelValue.value) {
    if (modelValue.value[key] !== null) {
      return true;
    }
  }
  return false;
});

const showViewer = computed(() => !props.edit && valueNotNull.value);
const showEstimateAction = computed(() => $appInfo.enableOpenai && !!props.recipe.slug);

function updateValue(key: number | string, event: number | null) {
  modelValue.value = { ...modelValue.value, [key]: event === null ? null : String(event) };
}

function renderNutritionList(nutrition: Nutrition | null | undefined) {
  return Object.entries(labels).reduce((item: NutritionLabelType, [key, label]) => {
    if (nutrition?.[key]?.trim()) {
      item[key] = {
        ...label,
        value: nutrition[key],
      };
    }
    return item;
  }, {});
}

// Build a new list that only contains nutritional information that has a value
const renderedList = computed(() => {
  return renderNutritionList(modelValue.value);
});

const currentRenderedList = computed(() => renderNutritionList(modelValue.value));
const estimatedRenderedList = computed(() => renderNutritionList(estimateResult.value?.nutrition));

async function calculateNutrition() {
  if (!props.recipe.recipeIngredient.length) {
    alert.warning(i18n.t("recipe.nutrition-estimate-no-ingredients"));
    return;
  }

  if ((props.recipe.recipeServings ?? 0) <= 0) {
    alert.warning(i18n.t("recipe.nutrition-estimate-servings-required"));
    return;
  }

  isEstimating.value = true;
  const { data, error } = await api.recipes.calculateNutrition(props.recipe.slug);
  isEstimating.value = false;

  if (error || !data) {
    alert.error(i18n.t("recipe.nutrition-estimate-failed"));
    return;
  }

  estimateResult.value = data;
  estimateDialog.value = true;
}

function applyEstimate() {
  if (!estimateResult.value) {
    return;
  }

  modelValue.value = { ...estimateResult.value.nutrition };
  estimateDialog.value = false;

  if (!props.edit) {
    setMode(PageMode.EDIT);
  }

  alert.success(i18n.t("recipe.nutrition-estimate-save-to-apply"));
}
</script>

<style lang="scss" scoped></style>
