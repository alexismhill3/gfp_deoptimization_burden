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
plot_exp_gr <- function(df, xtitle, colors){
  result <- ggplot() +
    geom_point(data= df,
               aes(x = expression,
                   y = growthrate,
                   color=strain,
                   shape=rbs,
                   size=3, alpha=0.9,
                   group=groupID)) +
    theme_bw() + theme(text = element_text(size = 16, family="Arial MS"),
                       axis.title.x = element_text(size = 16, family="Arial MS"),
                       axis.title.y = element_text(size = 16, family="Arial MS")) +
    ylab("Growth Rate\n(Δln(OD660)/h)") + 
    xlab(xtitle) + 
    scale_color_manual(values=colors) + 
    scale_shape_manual(values = c("\u25FC", "\u2B24", "\u25B2","\u2666", "\u2605")) +
    ylim(0, 1) +
    theme(axis.text=element_text(size=16),
          axis.title=element_text(size=20))  + expand_limits(x = 0, y = 0)
  return (result)
}

plot_slopes <- function(x_column, y_column, categories, colors){
  coefficients <- linreg_decent_set_b_coef(x_column, y_column, categories)
  model <- linreg_decent_set_b(x_column, y_column, categories)
  model$coef <- lapply(model$model, coef)
  model <- unnest_wider(model, coef)
  model$b <- set_intersept
  model$stderr <- lapply(model$model, function(mo) {summary(mo)$coefficients[, "Std. Error"]})
  model <- unnest(model, stderr)
  colnames(model)[colnames(model) == 'x'] <- 'm'
  plot <- ggplot(model, aes(x=species, y=abs(m), fill=species)) +
    geom_bar(stat = "identity") + theme_bw() +    
    geom_errorbar(aes(x=species, ymin=abs(m)-stderr, ymax=abs(m)+stderr)) +
    scale_fill_manual(values=colors) +
    theme_bw() + theme(text = element_text(size = 16, family="Arial MS"), 
                       axis.title.x = element_text(size = 16, family="Arial MS"),
                       axis.title.y = element_text(size = 16, family="Arial MS"),
                       axis.text.x = element_text(angle = 90,, size = 16, family="Arial MS")
                       ) +
    xlab("CDS") + ylab("abs(slope)")    
  
  return (plot)}

# ------------------- Generate
df_mch_per = read.csv("../processed_data/experimental_per_mcherry.csv")
df_gfp_per = read.csv("../processed_data/experimental_per_gfp.csv")
df_gfp_sat = read.csv("../processed_data/experimental_sat_gfp.csv")

uninduced_wells <- c("B7", "B8", "B9", "B10", "B11",
                   "C7", "C8", "C9", "C10", "C11",
                   "D7", "D8", "D9", "D10", "D11",
                   "E7", "E8", "E9", "E10", "E11",
                   "F7", "F8", "F9", "F10", "F11",
                   "G7", "G8", "G9", "G10", "G11")
df_gfp_per = df_gfp_per %>% filter(experiment > 12) %>% filter(well %in% uninduced_wells)
df_gfp_sat = df_gfp_sat %>% filter(experiment > 12) %>% filter(well %in% uninduced_wells)


cutoff_percent <- -0.10
#regression_function <- linreg_decent_variable_b_coef
regression_function <- linreg_decent_fixed_b_coef
#regression_function <- linreg_decent_set_b_coef

mch_cutoff <- max(df_mch_per$expression, na.rm = TRUE)*cutoff_percent
gfp_cutoff <- max(max(df_gfp_per $expression, na.rm = TRUE), max(df_gfp_sat$expression, na.rm = TRUE))*cutoff_percent

# -- mCherry
global_growth_time = 11700+900*-2
colors = c("#fde725", "#5ec962", "#21918c", '#3b528b', '#440154')

mcherry_growth_time <- global_growth_time
mcherry_fluor_time <- global_growth_time+900*2

trimmed_df <- trim_df(df_mch_per, mcherry_growth_time, mcherry_fluor_time)
trimmed_filtered_df <- trimmed_df %>% filter(expression > mch_cutoff)
#trimmed_filtered_df <- trimmed_filtered_df %>% filter(!(strain == "MCH90"))


mch_coefficients <- regression_function(trimmed_filtered_df$expression,
                                   trimmed_filtered_df$growthrate,
                                   trimmed_filtered_df$strain)
mch_plot <- plot_exp_gr(trimmed_filtered_df, "Relative Expression\n(ΔRFS/mean(OD660)/h)", colors)
mch_plot

mch_per_slopes <- plot_slopes(trimmed_filtered_df$expression,
                              trimmed_filtered_df$growthrate,
                              trimmed_filtered_df$strain, colors)

ggsave('expr_v_grow/per_mch_growth_unind.svg', mch_plot, width = 3.5, height = 3)


# -- sfGFP percent based
gfp_growth_time <- global_growth_time
gfp_fluor_time <- global_growth_time+900*0
colors = c("#fde725", "#5ec962", "#21918c", '#3b528b', '#440154')

trimmed_df <- trim_df(df_gfp_per, gfp_growth_time, gfp_fluor_time)
trimmed_filtered_df <- trimmed_df %>% filter(expression > gfp_cutoff)


gfp_plot_per <- plot_exp_gr(trimmed_filtered_df, "Relative Expression\n(ΔGFS/mean(OD660)/h)", colors)
gfp_plot_per

ggsave('expr_v_grow/per_gfp_growth_unind.svg', gfp_plot_per, width = 3.5, height = 3)


# -- sfGFP sat based
colors = c("#E69F00", "#56B4E9", "#009E73", '#F0E442', '#0072B2')
gfp_growth_time <- global_growth_time
gfp_fluor_time <- global_growth_time+900*0


trimmed_df <- trim_df(df_gfp_sat, gfp_growth_time, gfp_fluor_time)
trimmed_filtered_df <- trimmed_df %>% filter(expression > gfp_cutoff)

gfp_plot_sat <- plot_exp_gr(trimmed_filtered_df,  "Relative Expression\n(ΔGFS/mean(OD660)/h)", colors)
gfp_plot_sat

ggsave('expr_v_grow/sat_gfp_growth_unind.svg', gfp_plot_sat, width = 3.5, height = 3)


gfp_plot_per + gfp_plot_sat
