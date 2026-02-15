"""Regenerate all analysis figures from benchmark_results.csv."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

FIGURES_DIR = Path("results/figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
df = pd.read_csv("results/benchmark_results.csv")
print(f"Loaded {len(df)} results")

quality_cols = ["completeness", "accuracy", "structure", "insight", "readability", "overall"]

# 01 - Quality Scores
quality_avg = df.groupby("framework")[quality_cols].mean().reset_index()
quality_melted = quality_avg.melt(id_vars="framework", var_name="metric", value_name="score")
fig = px.bar(
    quality_melted, x="framework", y="score", color="metric", barmode="group",
    title="Average Quality Scores by Framework", labels={"score": "Score", "framework": "Framework"},
)
fig.update_layout(yaxis_range=[8, 10.2])
fig.write_image(FIGURES_DIR / "01_quality_scores.png", width=1200, height=600, scale=2)
print("01 done")

# 02 - Latency
latency_avg = df.groupby("framework")["latency_seconds"].mean().reset_index().sort_values("latency_seconds")
fig = px.bar(
    latency_avg, x="framework", y="latency_seconds", title="Average Latency by Framework",
    labels={"latency_seconds": "Latency (seconds)", "framework": "Framework"}, color="framework",
)
fig.write_image(FIGURES_DIR / "02_latency.png", width=1200, height=600, scale=2)
print("02 done")

# 03 - Token Usage
token_avg = df.groupby("framework")[["input_tokens", "output_tokens"]].mean().reset_index()
token_melted = token_avg.melt(id_vars="framework", var_name="type", value_name="tokens")
fig = px.bar(
    token_melted, x="framework", y="tokens", color="type", barmode="stack",
    title="Average Token Usage by Framework", labels={"tokens": "Tokens", "framework": "Framework"},
)
fig.write_image(FIGURES_DIR / "03_token_usage.png", width=1200, height=600, scale=2)
print("03 done")

# 04 - Score Distribution
fig = px.box(
    df, x="framework", y="overall", color="framework",
    title="Overall Quality Score Distribution by Framework",
    labels={"overall": "Overall Score", "framework": "Framework"}, points="all",
)
fig.update_layout(yaxis_range=[8, 10.2])
fig.write_image(FIGURES_DIR / "04_score_distribution.png", width=1200, height=600, scale=2)
print("04 done")

# 05 - Quality Metric Distributions
quality_df = df.melt(id_vars=["framework"], value_vars=quality_cols, var_name="metric", value_name="score")
fig = px.box(
    quality_df, x="metric", y="score", color="framework",
    title="Quality Metric Distributions by Framework", labels={"score": "Score", "metric": "Metric"},
)
fig.update_layout(yaxis_range=[7, 10.3])
fig.write_image(FIGURES_DIR / "05_quality_metric_distributions.png", width=1200, height=600, scale=2)
print("05 done")

# 06 - Per-Company Quality
company_quality = df.groupby(["framework", "company"])["overall"].agg(["mean", "std"]).reset_index()
company_quality.columns = ["framework", "company", "mean_quality", "std_quality"]
fig = px.bar(
    company_quality, x="company", y="mean_quality", color="framework", barmode="group",
    error_y="std_quality", title="Average Quality Score by Company and Framework",
    labels={"mean_quality": "Overall Score", "company": "Company"},
)
fig.update_layout(yaxis_range=[8, 10.5])
fig.write_image(FIGURES_DIR / "06_per_company_quality.png", width=1200, height=600, scale=2)
print("06 done")

# 07 - Quality vs Latency
fig = px.scatter(
    df, x="latency_seconds", y="overall", color="framework", symbol="company",
    title="Quality vs Latency Trade-off",
    labels={"latency_seconds": "Latency (seconds)", "overall": "Overall Quality Score"},
    hover_data=["company", "iteration", "total_tokens"],
)
fig.update_traces(marker=dict(size=10))
fig.update_layout(yaxis_range=[8, 10.2])
fig.write_image(FIGURES_DIR / "07_quality_vs_latency.png", width=1200, height=600, scale=2)
print("07 done")

# 08 - Radar Chart
radar_cols = ["completeness", "accuracy", "structure", "insight", "readability"]
radar_avg = df.groupby("framework")[radar_cols].mean()
fig = go.Figure()
for fw in radar_avg.index:
    values = radar_avg.loc[fw].tolist()
    values.append(values[0])
    fig.add_trace(go.Scatterpolar(
        r=values, theta=radar_cols + [radar_cols[0]], fill="toself", name=fw, opacity=0.6,
    ))
fig.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[8.5, 10.2])),
    title="Quality Dimension Profiles by Framework", showlegend=True,
)
fig.write_image(FIGURES_DIR / "08_radar_quality_profiles.png", width=1200, height=700, scale=2)
print("08 done")

# 09 - Report Length
df["report_words"] = df["report_text"].str.split().str.len()
fig = px.box(
    df, x="framework", y="report_words", color="framework",
    title="Report Length (Word Count) by Framework",
    labels={"report_words": "Word Count", "framework": "Framework"}, points="all",
)
fig.write_image(FIGURES_DIR / "09_report_length.png", width=1200, height=600, scale=2)
print("09 done")

# 10 - Report Length vs Quality
fig2 = px.scatter(
    df, x="report_words", y="overall", color="framework",
    title="Report Length vs Quality Score",
    labels={"report_words": "Word Count", "overall": "Overall Quality"},
    hover_data=["company", "iteration"],
)
fig2.update_layout(yaxis_range=[8, 10.2])
fig2.write_image(FIGURES_DIR / "10_report_length_vs_quality.png", width=1200, height=600, scale=2)
print("10 done")

# 11 - Token Efficiency
df_with_tokens = df[df["total_tokens"] > 0].copy()
if len(df_with_tokens) > 0:
    df_with_tokens["quality_per_1k_tokens"] = (
        df_with_tokens["overall"] / df_with_tokens["total_tokens"] * 1000
    )
    efficiency = df_with_tokens.groupby("framework").agg({
        "quality_per_1k_tokens": "mean",
        "total_tokens": "mean",
        "overall": "mean",
    }).round(4)
    efficiency.columns = ["Quality / 1K Tokens", "Avg Tokens", "Avg Quality"]
    efficiency = efficiency.sort_values("Quality / 1K Tokens", ascending=False)
    fig = px.bar(
        efficiency.reset_index(), x="framework", y="Quality / 1K Tokens", color="framework",
        title="Token Efficiency: Quality Score per 1K Tokens (higher = better)",
    )
    fig.write_image(FIGURES_DIR / "11_token_efficiency.png", width=1200, height=600, scale=2)
    print("11 done")

# 12 - Latency Heatmap
latency_pivot = df.pivot_table(
    values="latency_seconds", index="framework", columns="company", aggfunc="mean",
).round(1)
fig = px.imshow(
    latency_pivot, text_auto=True, color_continuous_scale="YlOrRd",
    title="Average Latency (seconds) — Framework x Company",
    labels=dict(x="Company", y="Framework", color="Latency (s)"), aspect="auto",
)
fig.write_image(FIGURES_DIR / "12_latency_heatmap.png", width=1200, height=600, scale=2)
print("12 done")

# 13 - Quality Heatmap
quality_pivot = df.pivot_table(
    values="overall", index="framework", columns="company", aggfunc="mean",
).round(2)
fig2 = px.imshow(
    quality_pivot, text_auto=True, color_continuous_scale="RdYlGn",
    title="Average Quality Score — Framework x Company",
    labels=dict(x="Company", y="Framework", color="Quality"),
    aspect="auto", zmin=7, zmax=10,
)
fig2.write_image(FIGURES_DIR / "13_quality_heatmap.png", width=1200, height=600, scale=2)
print("13 done")

print("\nAll 13 figures regenerated successfully!")
