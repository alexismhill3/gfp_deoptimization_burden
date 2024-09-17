# ----------------- Boilerplate
library(dplyr)
library(ggplot2)
library(patchwork)
library(slider)
library(data.table)
library(zoo)
library(tidyverse)
library(scales)

# -------------- Trim Dataframe

trim_df <- function(df, grow_time, output_time){
  # Grab growth
  growth_rates <- df[df$time == grow_time,]
  growth_rates <- growth_rates[c("groupID", "strain", "rbs", "growthrate")]
  # Grab Output
  expression <- df[df$time == output_time,]
  expression <- expression[c("groupID", "expression")]
  # Merge on ID
  merge <- merge(x = growth_rates, y = expression, by = "groupID", all.x = TRUE)
  return (merge)
}



# -------------- Regression model

linreg_decent_fixed_b <- function(x_column, y_column, categories) {
  reg_df <- data.frame(x=x_column, y=y_column, species = categories)
  model <- lm(y~x:species, data=reg_df )
  
  return(model)
}
linreg_decent_fixed_b_coef <- function(x_column, y_column, categories) {
  regression <- linreg_decent_fixed_b(x_column, y_column, categories)
  coefficients <- data.frame(b=rep(regression$coefficients[1], length(unique(categories))),
                             m=regression$coefficients[-1],
                             strain=sort(unique(categories)))
  
  return(coefficients)
}



# ----------------- Plot logic
plot_exp_gr <- function(df, coefficients){
  result <- ggplot() +
    geom_point(data= df,
               aes(x = expression,
                   y = growthrate,
                   color=strain,
                   shape=rbs,
                   size=3,
                   group=groupID)) +
    theme_bw() + 
    ylab("Growth Rate") + 
    xlab("Expression") + 
    scale_color_manual(values=c("#fde725", "#5ec962", "#21918c", '#3b528b', '#440154')) + 
    scale_shape_manual(values = c(15, 16, 17,18, 19)) +
    ylim(0, 1) +
    geom_abline(data=coefficients, 
                aes(intercept=b,
                    slope=m,
                    colour=strain))+
    theme(axis.text=element_text(size=16),
          axis.title=element_text(size=20))
  return (result)
}


# ------------------- Generate
# -- mCherry
mcherry_growth_time <- 11700+900*-2
mcherry_fluor_time <- 11700+900*1

df = read.csv("../processed_data/experimental_per_mcherry.csv")

trimmed_df <- trim_df(df, mcherry_growth_time, mcherry_fluor_time)
trimmed_df <- trimmed_df %>% group_by(strain, rbs) %>% filter(expression == max(expression))

mch_coefficients <- linreg_decent_fixed_b_coef(trimmed_df$expression,
                                   trimmed_df$growthrate,
                                   trimmed_df$strain)
mch_plot <- plot_exp_gr(trimmed_df, mch_coefficients)
mch_plot

ggsave('expr_v_grow/per_mch_growth.png', mch_plot, width = 9, height = 9)

# -- sfGFP
gfp_growth_time <- 11700+900*-2
gfp_fluor_time <- 11700+900*-1

df = read.csv("../processed_data/experimental_per_gfp.csv")

trimmed_df <- trim_df(df, gfp_growth_time, gfp_fluor_time)
trimmed_df <- trimmed_df %>% group_by(strain, rbs) %>% filter(expression == max(expression))


gfp_coefficients <- linreg_decent_fixed_b_coef(trimmed_df$expression,
                                               trimmed_df$growthrate,
                                               trimmed_df$strain)
gfp_plot <- plot_exp_gr(trimmed_df, gfp_coefficients)
gfp_plot

ggsave('expr_v_grow/per_gfp_growth.png', gfp_plot, width = 9, height = 9)

# -- sfGFP
gfp_growth_time <- 11700+900*-2
gfp_fluor_time <- 11700+900*-1

df = read.csv("../processed_data/experimental_sat_gfp.csv")

trimmed_df <- trim_df(df, gfp_growth_time, gfp_fluor_time)
trimmed_df <- trimmed_df %>% group_by(strain, rbs) %>% filter(expression == max(expression))

gfp_coefficients <- linreg_decent_fixed_b_coef(trimmed_df$expression,
                                               trimmed_df$growthrate,
                                               trimmed_df$strain)
gfp_plot <- plot_exp_gr(trimmed_df, gfp_coefficients)
gfp_plot

ggsave('expr_v_grow/per_sat_growth.png', gfp_plot, width = 9, height = 9)