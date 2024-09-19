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
  growth_rates <- growth_rates[c("groupID", "strain", "rbs", "growthrate")]
  # Grab Output
  expression <- df[df$time == output_time,]
  expression <- expression[c("groupID", "expression")]
  # Merge on ID
  merge <- merge(x = growth_rates, y = expression, by = "groupID", all.x = TRUE)
  return (merge)
}



# -------------- Regression models
set_intersept <- 0.9
linreg_decent_set_b <- function(x_column, y_column, categories) {
  reg_df <- data.frame(x=x_column, y=y_column, species = categories)
  models <- reg_df %>% group_by(species) %>% do(model = lm(y ~ x +0 + 
                                                             offset(rep(set_intersept, nrow(.))), data = .))
  
  return(models)
}
linreg_decent_set_b_coef <- function(x_column, y_column, categories) {
  regression <- linreg_decent_set_b(x_column, y_column, categories)
  regression$coef <- lapply(regression$model, coef)
  regression <- unnest_wider(regression, coef)
  print(regression)
  
  coefficients <- data.frame(b=set_intersept,
                             m=regression$x,
                             strain=regression$species)
  
  return(coefficients)
}


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

linreg_decent_variable_b <- function(x_column, y_column, categories) {
  reg_df <- data.frame(x=x_column, y=y_column, species = categories)
  models <- reg_df %>% group_by(species) %>% do(model = lm(y ~ x, data = .))
  
  return(models)
}
linreg_decent_variable_b_coef <- function(x_column, y_column, categories) {
  regression <- linreg_decent_variable_b(x_column, y_column, categories)
  regression$coef <- lapply(regression$model, coef)
  regression <- unnest_wider(regression, coef)
  
  coefficients <- data.frame(b=regression$`(Intercept)`,
                             m=regression$x,
                             strain=regression$species)
  
  return(coefficients)
}



# ----------------- Plot logic
plot_exp_gr <- function(df, coefficients, xtitle){
  result <- ggplot() +
    geom_point(data= df,
               aes(x = expression,
                   y = growthrate,
                   color=strain,
                   shape=rbs,
                   size=3,
                   group=groupID)) +
    theme_bw() + theme(text = element_text(size = 16, family="Arial MS"), legend.position="none",
                       axis.title.x = element_text(size = 16, family="Arial MS"),
                       axis.title.y = element_text(size = 16, family="Arial MS")) +
    ylab("Growth Rate\n(Δln(OD660)/h)") + 
    xlab(xtitle) + 
    scale_color_manual(values=c("#fde725", "#5ec962", "#21918c", '#3b528b', '#440154')) + 
    scale_shape_manual(values = c("\u25FC", "\u2B24", "\u25B2","\u2666", "\u2605")) +
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
df_mch_per = read.csv("../processed_data/experimental_per_mcherry.csv")
df_gfp_per = read.csv("../processed_data/experimental_per_gfp.csv")
df_gfp_sat = read.csv("../processed_data/experimental_sat_gfp.csv")


cutoff_percent <- 0.1
#regression_function <- linreg_decent_variable_b_coef
#regression_function <- linreg_decent_fixed_b_coef
regression_function <- linreg_decent_set_b_coef

mch_cutoff <- max(df_mch_per$expression, na.rm = TRUE)*cutoff_percent
gfp_cutoff <- max(max(df_gfp_per $expression, na.rm = TRUE), max(df_gfp_sat$expression, na.rm = TRUE))*cutoff_percent

# -- mCherry
global_growth_time = 11700+900*-2


mcherry_growth_time <- global_growth_time
mcherry_fluor_time <- global_growth_time+900*2

trimmed_df <- trim_df(df_mch_per, mcherry_growth_time, mcherry_fluor_time)
trimmed_filtered_df <- trimmed_df %>% filter(expression > mch_cutoff)


mch_coefficients <- regression_function(trimmed_filtered_df$expression,
                                   trimmed_filtered_df$growthrate,
                                   trimmed_filtered_df$strain)
mch_plot <- plot_exp_gr(trimmed_df, mch_coefficients, "Relative Expression\n(ΔRFS/mean(OD660)/h)")
mch_plot

ggsave('expr_v_grow/per_mch_growth.svg', mch_plot, width = 3.5, height = 3)


# -- sfGFP percent based
gfp_growth_time <- global_growth_time
gfp_fluor_time <- global_growth_time+900*0

trimmed_df <- trim_df(df_gfp_per, gfp_growth_time, gfp_fluor_time)
trimmed_filtered_df <- trimmed_df %>% filter(expression > gfp_cutoff)


gfp_coefficients <- regression_function(trimmed_filtered_df$expression,
                                               trimmed_filtered_df$growthrate,
                                               trimmed_filtered_df$strain)
gfp_plot_per <- plot_exp_gr(trimmed_df, gfp_coefficients, "Relative Expression\n(ΔGFS/mean(OD660)/h)")
gfp_plot_per

ggsave('expr_v_grow/per_gfp_growth.svg', gfp_plot_per, width = 3.5, height = 3)


# -- sfGFP sat based
gfp_growth_time <- global_growth_time
gfp_fluor_time <- global_growth_time+900*0


trimmed_df <- trim_df(df_gfp_sat, gfp_growth_time, gfp_fluor_time)
trimmed_filtered_df <- trimmed_df %>% filter(expression > gfp_cutoff)

gfp_coefficients <- regression_function(trimmed_filtered_df$expression,
                                               trimmed_filtered_df$growthrate,
                                               trimmed_filtered_df$strain)
gfp_plot_sat <- plot_exp_gr(trimmed_df, gfp_coefficients, "Relative Expression\n(ΔGFS/mean(OD660)/h)")
gfp_plot_sat

ggsave('expr_v_grow/sat_gfp_growth.svg', gfp_plot_sat, width = 3.5, height = 3)


mch_plot + gfp_plot_per + gfp_plot_sat