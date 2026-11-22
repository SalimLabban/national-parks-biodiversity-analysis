import glob
from math import ceil

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy.stats import chi2_contingency


# Load and inspect the CSV files.
observations = pd.read_csv(glob.glob("observations*.csv")[0])
species = pd.read_csv(glob.glob("species_info*.csv")[0])

print("\nFirst five observation records:")
print(observations.head())
print("\nFirst five species records:")
print(species.head())
print("\nUnique scientific names:", species["scientific_name"].nunique())
print("Species categories:", species["category"].unique().tolist())
print("Conservation statuses:", species["conservation_status"].unique().tolist())


# Clean and merge records for the seven category DataFrames.
category_columns = species["category"].dropna().unique().tolist()
species_clean = (
    species.dropna(subset=["conservation_status"])
    .drop_duplicates(
        subset=["scientific_name", "common_names", "category"],
        keep="first"
    )
)

species_wide = (
    species_clean.pivot(
        index=["scientific_name", "common_names"],
        columns="category",
        values="conservation_status"
    )
    .reindex(columns=category_columns)
    .reset_index()
)

biodiversity = (
    observations.merge(species_wide, on="scientific_name", how="left")
    .dropna(subset=category_columns, how="all")
    .reset_index(drop=True)
)

print("\nFirst five merged records:")
print(biodiversity.head())
print("\nDataset size:", biodiversity.shape)
print("\nData types:")
print(biodiversity.dtypes)
print("\nRemaining missing values:")
print(biodiversity.isna().sum())
print("\nNumber of filled category cells per row:")
print(biodiversity[category_columns].notna().sum(axis=1).value_counts())
print("\nRows with no conservation status:")
print(biodiversity[category_columns].isna().all(axis=1).sum())
print(
    "\nRepeated scientific names in species_wide:",
    species_wide["scientific_name"].duplicated().sum()
)


# Create and preview one DataFrame for each species category.
def make_species_table(category):
    columns = [
        "scientific_name", "common_names", "park_name", "observations", category
    ]
    return (
        biodiversity.loc[biodiversity[category].notna(), columns]
        .rename(columns={category: "conservation_status"})
        .reset_index(drop=True)
    )


amphibians = make_species_table("Amphibian")
birds = make_species_table("Bird")
fish = make_species_table("Fish")
mammals = make_species_table("Mammal")
nonvascular_plants = make_species_table("Nonvascular Plant")
vascular_plants = make_species_table("Vascular Plant")
reptiles = make_species_table("Reptile")

for name, table in [
    ("Amphibians", amphibians),
    ("Birds", birds),
    ("Fish", fish),
    ("Mammals", mammals),
    ("Nonvascular plants", nonvascular_plants),
    ("Vascular plants", vascular_plants),
    ("Reptiles", reptiles)
]:
    print(f"\n{name}")
    print(table.head())


# Prepare one record per scientific name and category for Q1–Q3.
# If records conflict, keep the first status in this priority order.
status_order = [
    "Endangered", "Threatened", "Species of Concern",
    "In Recovery", "No status listed"
]
status_priority = {status: rank for rank, status in enumerate(status_order)}

species_summary = species[
    ["scientific_name", "category", "conservation_status"]
].copy()

species_summary["conservation_status"] = (
    species_summary["conservation_status"].fillna("No status listed")
)
species_summary["status_priority"] = (
    species_summary["conservation_status"].map(status_priority)
)
species_summary = (
    species_summary.sort_values("status_priority")
    .drop_duplicates(subset=["scientific_name", "category"])
    .copy()
)

sns.set_theme(style="whitegrid")


# Figure 1 / Q1: Conservation status of animal species.
animal_categories = ["Amphibian", "Bird", "Fish", "Mammal", "Reptile"]
animals = species_summary.loc[species_summary["category"].isin(animal_categories)]
animal_status_counts = (
    animals["conservation_status"].value_counts()
    .reindex(status_order, fill_value=0)
)

print("\nQ1. Conservation status of animal species")
print(pd.DataFrame({
    "species_count": animal_status_counts,
    "percent": (100 * animal_status_counts / len(animals)).round(2)
}))

fig1, ax1 = plt.subplots(figsize=(8, 4))
animal_status_counts.sort_values().plot.barh(ax=ax1, color="steelblue")
ax1.set_title("Q1. Conservation status of animal species")
ax1.set_xlabel("Number of species")
ax1.set_ylabel("Conservation status")
fig1.tight_layout()


# Figure 2: Conservation status across animals and plants.
# A scientific name can appear in multiple status groups in this summary.
solution_species = species.copy()
solution_species["conservation_status"] = (
    solution_species["conservation_status"].fillna("No Intervention")
)
all_status_counts = (
    solution_species.groupby("conservation_status")["scientific_name"]
    .nunique()
    .sort_values()
)

print("\nSolution addition. Conservation status across all species")
print(all_status_counts)

fig2, ax2 = plt.subplots(figsize=(8, 4))
all_status_counts.plot.barh(ax=ax2, color="steelblue")
ax2.set_title("Conservation status across all species")
ax2.set_xlabel("Number of unique scientific names")
ax2.set_ylabel("Conservation status")
fig2.tight_layout()


# Figure 3 / Q2: Percentage of species listed as endangered by category.
species_summary["is_endangered"] = (
    species_summary["conservation_status"].eq("Endangered")
)
endangered_summary = species_summary.groupby("category").agg(
    total_species=("scientific_name", "size"),
    endangered_species=("is_endangered", "sum")
)
endangered_summary["endangered_percent"] = (
    100 * endangered_summary["endangered_species"]
    / endangered_summary["total_species"]
)
endangered_summary = endangered_summary.sort_values(
    "endangered_percent", ascending=False
)

print("\nQ2. Endangered species by category")
print(endangered_summary.round(2))

fig3, ax3 = plt.subplots(figsize=(8, 5))
percentages = endangered_summary["endangered_percent"].sort_values()
bars = ax3.barh(percentages.index, percentages, color="seagreen")
ax3.bar_label(bars, labels=[f"{value:.2f}%" for value in percentages], padding=4)
ax3.set_xlim(0, percentages.max() + 0.6)
ax3.set_title("Q2. Percentage of species listed as endangered")
ax3.set_xlabel("Endangered species (%)")
ax3.set_ylabel("Species category")
fig3.tight_layout()


# Reproduce the notebook's percentages for any listed conservation status.
solution_species["is_protected"] = (
    solution_species["conservation_status"].ne("No Intervention")
)
category_counts = (
    solution_species.groupby(["category", "is_protected"])["scientific_name"]
    .nunique()
    .reset_index(name="species_count")
)
category_pivot = (
    category_counts.pivot(
        index="category", columns="is_protected", values="species_count"
    )
    .reindex(columns=[False, True])
    .fillna(0)
    .astype(int)
    .rename(columns={False: "not_protected", True: "protected"})
)
category_pivot["percent_protected"] = (
    100 * category_pivot["protected"]
    / (category_pivot["protected"] + category_pivot["not_protected"])
)

print("\nSolution addition. Species with any listed status by category")
print(category_pivot.round(2))


# Figure 4 / Q3: Test the association between category and listed status.
species_summary["has_listed_status"] = (
    species_summary["conservation_status"].ne("No status listed")
)
status_by_category = pd.crosstab(
    species_summary["category"], species_summary["has_listed_status"]
).rename(columns={False: "No status listed", True: "Status listed"})

chi2, p_value, degrees_of_freedom, expected = chi2_contingency(status_by_category)

print("\nQ3. Overall chi-square test of category and listed status")
print(status_by_category)
print(f"Chi-square statistic: {chi2:.2f}")
print(f"Degrees of freedom: {degrees_of_freedom}")
print(f"p-value: {p_value:.4g}")
print(f"Smallest expected count: {expected.min():.2f}")

if expected.min() < 5:
    print("Some expected counts are below 5. Interpret the p-value cautiously.")
elif p_value < 0.05:
    print("There is evidence of an association between category and listed status.")
else:
    print("There is insufficient evidence of an association at the 5% level.")

status_percent = (
    status_by_category.div(status_by_category.sum(axis=1), axis=0)
    .mul(100)
    .sort_values("Status listed")
)

fig4, ax4 = plt.subplots(figsize=(9, 5))
status_percent[["Status listed", "No status listed"]].plot.barh(
    ax=ax4, stacked=True, color=["seagreen", "lightgray"]
)
ax4.set_title("Q3. Listed conservation status by species category")
ax4.set_xlabel("Percentage of species")
ax4.set_ylabel("Species category")
ax4.set_xlim(0, 100)
ax4.legend(loc="lower right")
fig4.tight_layout()


# Reproduce the notebook's two pairwise chi-square tests.
for comparison in ["Bird", "Reptile"]:
    contingency = category_pivot.loc[
        ["Mammal", comparison], ["protected", "not_protected"]
    ]
    pair_chi2, pair_p, _, pair_expected = chi2_contingency(contingency)

    print(f"\nSolution addition. Mammal vs. {comparison}")
    print(contingency)
    print(f"Chi-square statistic: {pair_chi2:.3f}")
    print(f"p-value: {pair_p:.4f}")

    if pair_expected.min() < 5:
        print("Some expected counts are below 5. Interpret the p-value cautiously.")
    elif pair_p < 0.05:
        print("The difference is statistically significant at the 5% level.")
    else:
        print("There is insufficient evidence of a difference at the 5% level.")


# Figure 5 / Q4: Most recorded species at each park, including ties.
# Group the original observations to avoid duplicate metadata matches.
park_totals = observations.groupby(
    ["park_name", "scientific_name"], as_index=False
)["observations"].sum()

park_maximums = park_totals.groupby("park_name")["observations"].transform("max")
park_leaders = park_totals.loc[
    park_totals["observations"].eq(park_maximums)
].sort_values(["park_name", "scientific_name"])

print("\nQ4. Most recorded species at each park")
print(park_leaders.to_string(index=False))

park_labels = (
    park_leaders["park_name"].str.replace(" National Park", "", regex=False)
    + " | " + park_leaders["scientific_name"]
)

fig5, ax5 = plt.subplots(figsize=(10, 4))
ax5.barh(park_labels, park_leaders["observations"], color="steelblue")
ax5.set_title("Q4. Species with the most recorded observations at each park")
ax5.set_xlabel("Total recorded observations")
ax5.invert_yaxis()
fig5.tight_layout()


# Figure 6: Weekly sheep observations by park.
# Restrict the name search to mammals to exclude plants such as Sheep Sorrel.
solution_species["is_sheep"] = solution_species["common_names"].str.contains(
    "Sheep", regex=False, na=False
)
sheep_species = solution_species.loc[
    solution_species["is_sheep"] & solution_species["category"].eq("Mammal")
].drop_duplicates(subset=["scientific_name"])

print("\nSolution addition. Sheep species")
print(sheep_species[["scientific_name", "common_names"]].to_string(index=False))

sheep_observations = observations.merge(
    sheep_species, on="scientific_name", how="inner", validate="many_to_one"
)
obs_by_park = sheep_observations.groupby("park_name")["observations"].sum()

print("\nWeekly sheep observations by park")
print(obs_by_park)

sheep_plot = obs_by_park.sort_values().copy()
sheep_plot.index = sheep_plot.index.str.replace(" National Park", "", regex=False)

fig6, ax6 = plt.subplots(figsize=(9, 4))
sheep_plot.plot.barh(ax=ax6, color="seagreen")
ax6.set_title("Weekly sheep observations by park")
ax6.set_xlabel("Number of recorded observations")
ax6.set_ylabel("Park")
fig6.tight_layout()


# Estimate the time needed to reach the notebook's sample target.
baseline_rate = 0.15
target_rate = 0.10
minimum_detectable_effect = 100 * (baseline_rate - target_rate) / baseline_rate
sample_size_per_park = 870

print("\nSolution addition. Sheep study sample size")
print(f"Minimum detectable effect: {minimum_detectable_effect:.2f}% of baseline")
print(f"Target sample size per park: {sample_size_per_park}")

for park in ["Bryce National Park", "Yellowstone National Park"]:
    weekly_observations = obs_by_park.get(park, 0)
    if weekly_observations == 0:
        print(f"{park}: no sheep observations available for the estimate.")
        continue

    weeks = sample_size_per_park / weekly_observations
    print(f"{park}: {weeks:.2f} weeks, or {ceil(weeks)} full weeks.")


# Prepare one row per species and one column per park for Figures 7 and 8.
park_counts = park_totals.pivot(
    index="scientific_name", columns="park_name", values="observations"
)
yellowstone = "Yellowstone National Park"
yosemite = "Yosemite National Park"


# Figure 7: Yellowstone's 10 most recorded species across all four parks.
top_species = park_counts[yellowstone].nlargest(10).index
park_order = [yellowstone, *park_counts.columns.drop(yellowstone)]
heatmap_data = park_counts.loc[top_species, park_order].copy()
heatmap_data.columns = heatmap_data.columns.str.replace(
    " National Park", "", regex=False
)

fig7, ax7 = plt.subplots(figsize=(10, 6))
sns.heatmap(
    heatmap_data,
    annot=True,
    fmt=".0f",
    cmap="YlGn",
    cbar_kws={"label": "Recorded observations"},
    ax=ax7
)
ax7.set_title("Yellowstone's 10 most recorded species across parks")
ax7.set_xlabel("Park")
ax7.set_ylabel("Species")
fig7.tight_layout()


# Figure 8: Compare species observation counts in Yellowstone and Yosemite.
# A smaller grid makes each hexagon larger. Log shading makes lower counts
# easier to see. Empty hexagons are left blank.
park_comparison = park_counts[[yellowstone, yosemite]].dropna()

hex_plot = sns.jointplot(
    data=park_comparison,
    x=yellowstone,
    y=yosemite,
    kind="hex",
    color="seagreen",
    height=8,
    joint_kws={
        "gridsize": 24,
        "bins": "log",
        "mincnt": 1,
        "cmap": "YlGn"
    }
)
hex_plot.set_axis_labels(
    "Recorded observations in Yellowstone",
    "Recorded observations in Yosemite"
)
fig8 = hex_plot.figure
fig8.suptitle("Species observations in Yellowstone and Yosemite")
fig8.subplots_adjust(top=0.92)


# Save all eight figures with consistent filenames.
figures = [fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8]

print("\nSaved charts:")
for number, figure in enumerate(figures, start=1):
    filename = f"chart_{number}.png"
    figure.savefig(filename, dpi=300, bbox_inches="tight")
    print(filename)

plt.show()