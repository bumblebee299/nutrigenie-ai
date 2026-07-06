"use client";

import { useForm, useFieldArray } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Plus, X, Loader2 } from "lucide-react";
import type { MealPlanRequest } from "@/services/types/meal_plan";

const schema = z.object({
  age: z.coerce.number().int().min(1).max(120),
  height_cm: z.coerce.number().min(50).max(300),
  weight_kg: z.coerce.number().min(10).max(500),
  gender: z.enum(["male", "female", "other"]),
  goal: z.enum(["weight_loss", "weight_gain", "maintenance", "muscle_gain"]),
  lifestyle: z.enum([
    "sedentary",
    "lightly_active",
    "moderately_active",
    "very_active",
    "extra_active",
  ]),
  budget_usd_per_day: z.coerce.number().min(1).optional().or(z.literal("")),
  diseases: z.array(z.object({ value: z.string() })),
  allergies: z.array(z.object({ value: z.string() })),
  cuisine_preference: z.array(z.object({ value: z.string() })),
});

type FormValues = z.infer<typeof schema>;

interface MealPlanFormProps {
  userId: string;
  onSubmit: (payload: MealPlanRequest) => void;
  isLoading: boolean;
}

function TagInput({
  label,
  placeholder,
  items,
  onAdd,
  onRemove,
}: {
  label: string;
  placeholder: string;
  items: { value: string }[];
  onAdd: () => void;
  onRemove: (i: number) => void;
}) {
  return (
    <div>
      <span className="label">{label}</span>
      <div className="flex flex-wrap gap-2 mb-2">
        {items.map((item, i) => (
          <span
            key={i}
            className="flex items-center gap-1 text-xs bg-gray-800 border border-gray-700 rounded-full px-3 py-1 text-gray-300"
          >
            {item.value}
            <button
              type="button"
              onClick={() => onRemove(i)}
              className="text-gray-500 hover:text-red-400 transition-colors"
            >
              <X size={11} />
            </button>
          </span>
        ))}
      </div>
      <button
        type="button"
        onClick={onAdd}
        className="flex items-center gap-1 text-xs text-brand-400 hover:text-brand-300 transition-colors"
      >
        <Plus size={13} />
        Add {placeholder}
      </button>
    </div>
  );
}

export function MealPlanForm({ userId, onSubmit, isLoading }: MealPlanFormProps) {
  const {
    register,
    handleSubmit,
    control,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      gender: "male",
      goal: "maintenance",
      lifestyle: "moderately_active",
      diseases: [],
      allergies: [],
      cuisine_preference: [],
    },
  });

  const diseases = useFieldArray({ control, name: "diseases" });
  const allergies = useFieldArray({ control, name: "allergies" });
  const cuisines = useFieldArray({ control, name: "cuisine_preference" });

  function handleFormSubmit(values: FormValues) {
    onSubmit({
      user_id: userId,
      age: values.age,
      height_cm: values.height_cm,
      weight_kg: values.weight_kg,
      gender: values.gender,
      goal: values.goal,
      lifestyle: values.lifestyle,
      diseases: values.diseases.map((d) => d.value).filter(Boolean),
      allergies: values.allergies.map((a) => a.value).filter(Boolean),
      cuisine_preference: values.cuisine_preference.map((c) => c.value).filter(Boolean),
      budget_usd_per_day: values.budget_usd_per_day
        ? Number(values.budget_usd_per_day)
        : undefined,
    });
  }

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="card space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-white">Your Profile</h2>
        <p className="text-sm text-gray-400 mt-0.5">
          Fill in your details to generate a personalised meal plan.
        </p>
      </div>

      {/* Biometrics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div>
          <label htmlFor="age" className="label">Age</label>
          <input id="age" type="number" className="input-field" placeholder="28" {...register("age")} />
          {errors.age && <p className="mt-1 text-xs text-red-400">{errors.age.message}</p>}
        </div>
        <div>
          <label htmlFor="height_cm" className="label">Height (cm)</label>
          <input id="height_cm" type="number" step="0.1" className="input-field" placeholder="170" {...register("height_cm")} />
          {errors.height_cm && <p className="mt-1 text-xs text-red-400">{errors.height_cm.message}</p>}
        </div>
        <div>
          <label htmlFor="weight_kg" className="label">Weight (kg)</label>
          <input id="weight_kg" type="number" step="0.1" className="input-field" placeholder="70" {...register("weight_kg")} />
          {errors.weight_kg && <p className="mt-1 text-xs text-red-400">{errors.weight_kg.message}</p>}
        </div>
        <div>
          <label htmlFor="budget" className="label">Budget ($/day)</label>
          <input id="budget" type="number" step="0.5" className="input-field" placeholder="Optional" {...register("budget_usd_per_day")} />
        </div>
      </div>

      {/* Dropdowns */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div>
          <label htmlFor="gender" className="label">Gender</label>
          <select id="gender" className="input-field" {...register("gender")}>
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
          </select>
        </div>
        <div>
          <label htmlFor="goal" className="label">Goal</label>
          <select id="goal" className="input-field" {...register("goal")}>
            <option value="weight_loss">Weight Loss</option>
            <option value="weight_gain">Weight Gain</option>
            <option value="maintenance">Maintenance</option>
            <option value="muscle_gain">Muscle Gain</option>
          </select>
        </div>
        <div>
          <label htmlFor="lifestyle" className="label">Lifestyle</label>
          <select id="lifestyle" className="input-field" {...register("lifestyle")}>
            <option value="sedentary">Sedentary</option>
            <option value="lightly_active">Lightly Active</option>
            <option value="moderately_active">Moderately Active</option>
            <option value="very_active">Very Active</option>
            <option value="extra_active">Extra Active</option>
          </select>
        </div>
      </div>

      {/* Tag inputs */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <TagInput
          label="Medical Conditions"
          placeholder="condition"
          items={diseases.fields}
          onAdd={() => {
            const val = prompt("Enter condition (e.g. diabetes)");
            if (val?.trim()) diseases.append({ value: val.trim() });
          }}
          onRemove={(i) => diseases.remove(i)}
        />
        <TagInput
          label="Allergies"
          placeholder="allergen"
          items={allergies.fields}
          onAdd={() => {
            const val = prompt("Enter allergen (e.g. nuts)");
            if (val?.trim()) allergies.append({ value: val.trim() });
          }}
          onRemove={(i) => allergies.remove(i)}
        />
        <TagInput
          label="Cuisine Preferences"
          placeholder="cuisine"
          items={cuisines.fields}
          onAdd={() => {
            const val = prompt("Enter cuisine (e.g. Mediterranean)");
            if (val?.trim()) cuisines.append({ value: val.trim() });
          }}
          onRemove={(i) => cuisines.remove(i)}
        />
      </div>

      <button type="submit" disabled={isLoading} className="btn-primary w-full sm:w-auto flex items-center gap-2">
        {isLoading ? (
          <>
            <Loader2 size={16} className="animate-spin" />
            Generating your plan…
          </>
        ) : (
          "Generate Meal Plan"
        )}
      </button>
    </form>
  );
}
