# ----------------- Boilerplate
library(dplyr)
library(ggplot2)
library(patchwork)
library(slider)
library(data.table)
library(zoo)
library(tidyverse)
library(scales)
library(extrafont)
font_import(pattern="arial.ttf", prompt=FALSE)

# -------------- Trim Dataframe

trim_df <- function(df, grow_time, output_time){
  # Grab growth
  growth_rates <- df[df$time == grow_time,]
  growth_rates <- growth_rates[c("groupID", "strain", "rbs", "experiment", "growthrate")]
  growth_rates$experiment <- as.factor(growth_rates$experiment)
  # Grab Output
  expression <- df[df$time == output_time,]
  expression <- expression[c("groupID", "expression")]
  # Merge on ID
  merge <- merge(x = growth_rates, y = expression, by = "groupID", all.x = TRUE)
  return (merge)
}

# ---- plot logic

day_violin <- function(df, title){
  
  plot <- ggplot(df, aes(x=experiment, y=expression)) + 
    geom_violin() + theme_bw() + ggtitle(title) + geom_jitter(height = 0, width = 0.1)
  
  return (plot)
}



# ------------------- Generate
df_mch_per = read.csv("../processed_data/experimental_per_mcherry.csv")
df_gfp_per = read.csv("../processed_data/experimental_per_gfp.csv")
df_gfp_sat = read.csv("../processed_data/experimental_sat_gfp.csv")


cutoff_percent <- 0.1
global_growth_time = 11700+900*-2

mch_cutoff <- max(df_mch_per$expression, na.rm = TRUE)*cutoff_percent
gfp_cutoff <- max(max(df_gfp_per $expression, na.rm = TRUE), max(df_gfp_sat$expression, na.rm = TRUE))*cutoff_percent

# -- mCherry

mcherry_growth_time <- global_growth_time
mcherry_fluor_time <- global_growth_time+900*2

trimmed_df <- trim_df(df_mch_per, mcherry_growth_time, mcherry_fluor_time)

mch_plot <- day_violin(trimmed_df, "mCherry FOPtimized")
mch_plot

#ggsave('expr_v_grow/per_mch_growth.svg', mch_plot, width = 3.5, height = 3)


# -- sfGFP percent based
gfp_growth_time <- global_growth_time
gfp_fluor_time <- global_growth_time+900*0

trimmed_df <- trim_df(df_gfp_per, gfp_growth_time, gfp_fluor_time)

gfp_plot_per <- day_violin(trimmed_df, "sfGFP FOPtimized")
gfp_plot_per

#ggsave('expr_v_grow/per_gfp_growth.svg', gfp_plot, width = 3.5, height = 3)


# -- sfGFP sat based
gfp_growth_time <- global_growth_time
gfp_fluor_time <- global_growth_time+900*0


trimmed_df <- trim_df(df_gfp_sat, gfp_growth_time, gfp_fluor_time)

gfp_plot_sat <- day_violin(trimmed_df, "sfGFP Percent Otimized")
gfp_plot_sat

#ggsave('expr_v_grow/sat_gfp_growth.svg', gfp_plot, width = 3.5, height = 3)

mch_plot + gfp_plot_per + gfp_plot_sat