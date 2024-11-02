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
  growth_rates <- growth_rates[c("groupID", "strain", "rbs", "growthrate", "experiment", "well")]
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
plot_exp_gr <- function(df, coefficients, xtitle, colors){
  result <- ggplot() +
    geom_point(data= df,
               aes(x = expression,
                   y = growthrate,
                   color=strain,
                   shape=rbs,
                   size=2,
                   group=groupID)) +
    theme_bw() + theme(text = element_text(size = 16, family="Arial MS"), legend.position="none",
                       axis.title.x = element_text(size = 16, family="Arial MS"),
                       axis.title.y = element_text(size = 16, family="Arial MS")) +
    ylab("Growth Rate\n(Δln(OD660)/h)") + 
    xlab(xtitle) + 
    scale_color_manual(values=colors) + 
    scale_shape_manual(values = c("\u25FC", "\u2B24", "\u25B2","\u2666", "\u2605")) +
    ylim(0, 1.3) +
    geom_abline(data=coefficients, 
                aes(intercept=b,
                    slope=m,
                    colour=strain))+
    theme(axis.text=element_text(size=16),
          axis.title=element_text(size=20))  + expand_limits(x = 0, y = 0)
  return (result)
}

plot_exp_gr_threshold <- function(df_good, df_bad, threshhold, title, xtitle, xrange, ytitle, color){
  result <- ggplot() +
    geom_point(data= df_good,
               aes(x = expression,
                   y = growthrate,
                   shape=rbs), size=1.5, color=color) +
    geom_point(data= df_bad,
               aes(x = expression,
                   y = growthrate,
                   shape=rbs), size=1.5, color="#999999") +
    theme_bw() + theme(text = element_text(size = 16, family="Arial MS"), legend.position="none",
                       axis.title.x = element_text(size = 16, family="Arial MS"),
                       axis.title.y = element_text(size = 16, family="Arial MS"),
                       plot.title = element_text(size=16, family="Arial MS")) +
    geom_vline(xintercept=threshhold, linetype='dashed') + 
    scale_shape_manual(values = c("\u25FC", "\u2B24", "\u25B2","\u2666", "\u2605")) + 
    ylab(ytitle) + 
    xlab(xtitle) + 
    ylim(0, 1.3) + ggtitle(title) +
    theme(axis.text=element_text(size=16),
          axis.title=element_text(size=20))  + expand_limits(x = 0, y = 0) + expand_limits(x = xrange)
  return (result)
}


plot_slopes <- function(x_column, y_column, categories, colors){
  coefficients <- linreg_decent_fixed_b_coef(x_column, y_column, categories)
  model <- linreg_decent_fixed_b(x_column, y_column, categories)
  model_coef <- model$coef
  stderr_vector <- summary(model)$coefficients[, "Std. Error"]
  
  intercept_value <- model_coef["(Intercept)"]
  
  model_coef <- model_coef[names(model_coef) != "(Intercept)"]
  stderr_vector <- stderr_vector[names(stderr_vector) != "(Intercept)"]
  
  
  df <- data.frame(name = names(model_coef), m = model_coef, stderr = stderr_vector, row.names = NULL)
  
  df_final <- df %>%
    separate(name, into = c("dummy", "species"), sep = ":", fill = "left") %>%
    mutate(species = gsub("^species", "", species),
           b = intercept_value,) %>%
    select(b, species, m, stderr) %>% arrange(m)
  
  #df_final$species <- factor(df_final$species, levels = df_final$species)
  print(df_final)
  plot <- ggplot(df_final, aes(x=species, y=abs(m), fill=species)) +
    geom_bar(stat = "identity") + theme_bw() +    
    geom_errorbar(aes(x=species, ymin=abs(m)-stderr, ymax=abs(m)+stderr)) +
    scale_fill_manual(values=colors) +
    theme_bw() + theme(text = element_text(size = 16, family="Arial MS"), legend.position="none",
                       axis.title.x = element_text(size = 16, family="Arial MS"),
                       axis.title.y = element_text(size = 16, family="Arial MS"),
                       axis.text.y = element_text(size = 16, family="Arial MS"),
                       axis.text.x = element_text(angle = 90, size = 16, family="Arial MS")
                       ) +
    xlab("CDS") + ylab("Overexpression\nBurden")    
  
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


cutoff_percent <- 0.10
#regression_function <- linreg_decent_variable_b_coef
regression_function <- linreg_decent_fixed_b_coef
#regression_function <- linreg_decent_set_b_coef

mch_cutoff <- max(df_mch_per$expression, na.rm = TRUE)*cutoff_percent
gfp_cutoff <- max(max(df_gfp_per $expression, na.rm = TRUE), max(df_gfp_sat$expression, na.rm = TRUE))*cutoff_percent

# -- mCherry
global_growth_time = 11700+900*-4
colors = c("#fde725", "#5ec962", "#21918c", '#3b528b', '#440154')

mcherry_growth_time <- global_growth_time
mcherry_fluor_time <- global_growth_time+900*4

trimmed_df <- trim_df(df_mch_per, mcherry_growth_time, mcherry_fluor_time)
below_cuttoff_mch_sat <- trimmed_df  %>% filter(expression < mch_cutoff) %>% filter(!((experiment > 12) & (well %in% uninduced_wells)) )
trimmed_filtered_df_induced <- trimmed_df %>% filter(expression > mch_cutoff) %>% filter(!((experiment > 12) & (well %in% uninduced_wells)) )
okay_induced_mch <- unique(trimmed_filtered_df_induced$groupID) 
trimmed_filtered_df_uninduced <- trimmed_df %>% filter(experiment > 12) %>% filter(well %in% uninduced_wells) 
trimmed_filtered_df <- rbind(trimmed_filtered_df_induced, trimmed_filtered_df_uninduced)


mch_coefficients <- regression_function(trimmed_filtered_df$expression,
                                   trimmed_filtered_df$growthrate,
                                   trimmed_filtered_df$strain)
mch_plot <- plot_exp_gr(trimmed_filtered_df, mch_coefficients, "Relative Expression\n(ΔRFS/mean(OD660)/h)", colors)
mch_plot

mch_per_slopes <- plot_slopes(trimmed_filtered_df$expression,
                              trimmed_filtered_df$growthrate,
                              trimmed_filtered_df$strain, colors)

mch_per_top <- as.data.frame(trimmed_filtered_df %>% 
                               group_by(strain) %>% 
                               slice_max(expression, prop = 0.10) %>%
                               summarize(expression = mean(expression), growthrate = mean(growthrate)))
mch_per_top  <- merge(mch_per_top , mch_coefficients, by='strain', all.x=TRUE)
mch_per_top$calc_growthrate <- mch_per_top$expression*mch_per_top$m+mch_per_top$b
mch_per_top$percent <- 1-mch_per_top$calc_growthrate/mch_per_top$b
mch_per_top

ggsave('expr_v_grow/per_mch_growth.svg', mch_plot, width = 3.5, height = 3)

okay_mch_measurements <- unique(trimmed_filtered_df$groupID)

subplots <- list()
for (tgtstrain in c("MCH10", "MCH25", "MCH50", "MCH75", "MCH90")){
  good_induced <- trimmed_filtered_df_induced %>% filter(groupID %like% tgtstrain)
  count(good_induced)
  good_uninduced <- trimmed_filtered_df_uninduced %>% filter(groupID %like% tgtstrain)
  count(good_uninduced)
  df_good <- rbind(good_induced, good_uninduced)
  df_bad <- below_cuttoff_mch_sat %>% filter(groupID %like% tgtstrain)
  count(df_bad)
  threshhold <- mch_cutoff
  title <- tgtstrain
  xtitle <- ""
  ytitle <- ""
  #if (tgtstrain == "MCH50"){ytitle <- "Growth Rate\n(Δln(OD660)/h)"}
  xtitle <- ""
  #if (tgtstrain == "MCH90"){xtitle <- "mCherry2 Relative Expression\n(ΔRFS/mean(OD660)/h)"}
  color <- "#6a8ad5"
  xrange <- 33
  
  subplot <- plot_exp_gr_threshold(df_good, df_bad, threshhold, title, xtitle, xrange, ytitle, color)
  subplots <- append(subplots, list(subplot))}
mch_individuals <- wrap_plots(subplots) + plot_layout(ncol=1)
mch_individuals 


# -- sfGFP percent based
gfp_growth_time <- global_growth_time
gfp_fluor_time <- global_growth_time+900*1
colors = c("#fde725", "#5ec962", "#21918c", '#3b528b', '#440154')


trimmed_df <- trim_df(df_gfp_per, gfp_growth_time, gfp_fluor_time)
below_cuttoff_mch_sat <- trimmed_df  %>% filter(expression < gfp_cutoff) %>% filter(!((experiment > 12) & (well %in% uninduced_wells)) )
trimmed_filtered_df_induced <- trimmed_df %>% filter(expression > gfp_cutoff) %>% filter(!((experiment > 12) & (well %in% uninduced_wells)) )
okay_induced_pergfp <- unique(trimmed_filtered_df_induced$groupID) 
trimmed_filtered_df_uninduced <- trimmed_df %>% filter(experiment > 12) %>% filter(well %in% uninduced_wells) 
trimmed_filtered_df <- rbind(trimmed_filtered_df_induced, trimmed_filtered_df_uninduced)


gfp_coefficients <- regression_function(trimmed_filtered_df$expression,
                                               trimmed_filtered_df$growthrate,
                                             trimmed_filtered_df$strain)
gfp_plot_per <- plot_exp_gr(trimmed_filtered_df, gfp_coefficients, "Relative Expression\n(ΔGFS/mean(OD660)/h)", colors)
gfp_plot_per

gfp_per_slopes <- plot_slopes(trimmed_filtered_df$expression,
                              trimmed_filtered_df$growthrate,
                              trimmed_filtered_df$strain, colors)

gfp_per_top <- as.data.frame(trimmed_filtered_df %>% 
                               group_by(strain) %>% 
                               slice_max(expression, prop = 0.10) %>%
                               summarize(expression = mean(expression), growthrate = mean(growthrate)))
gfp_per_top  <- merge(gfp_per_top , gfp_coefficients, by='strain', all.x=TRUE)
gfp_per_top$calc_growthrate <- gfp_per_top$expression*gfp_per_top$m+gfp_per_top$b
gfp_per_top$percent <- 1-gfp_per_top$calc_growthrate/gfp_per_top$b
gfp_per_top 


ggsave('expr_v_grow/per_gfp_growth.svg', gfp_plot_per, width = 3.5, height = 3)
okay_pergfp_measurements <- unique(trimmed_filtered_df$groupID)

subplots <- list()
for (tgtstrain in c("GFP10", "GFP25", "GFP50", "GFP75", "GFP90")){
  good_induced <- trimmed_filtered_df_induced %>% filter(groupID %like% tgtstrain)
  count(good_induced)
  good_uninduced <- trimmed_filtered_df_uninduced %>% filter(groupID %like% tgtstrain)
  count(good_uninduced)
  df_good <- rbind(good_induced, good_uninduced)
  df_bad <- below_cuttoff_mch_sat %>% filter(groupID %like% tgtstrain)
  count(df_bad)
  threshhold <- gfp_cutoff
  title <- tgtstrain
  xtitle <- ""
  ytitle <- ""
  xtitle <- ""
  #if (tgtstrain == "GFP90"){xtitle <- "sfGFP Relative Expression\n(ΔRFS/mean(OD660)/h)"}
  color <- "#6a8ad5"
  xrange <- 14
  
  subplot <- plot_exp_gr_threshold(df_good, df_bad, threshhold, title, xtitle, xrange, ytitle, color)
  subplots <- append(subplots, list(subplot))}
gfp_per_individuals <- wrap_plots(subplots) + plot_layout(ncol=1)
gfp_per_individuals 


# -- sfGFP sat based
colors = c("#E69F00","#009E73", "#56B4E9", '#F0E442', '#0072B2'  )
gfp_growth_time <- global_growth_time
gfp_fluor_time <- global_growth_time+900*1


trimmed_df <- trim_df(df_gfp_sat, gfp_growth_time, gfp_fluor_time)
below_cuttoff_mch_sat <- trimmed_df  %>% filter(expression < gfp_cutoff) %>% filter(!((experiment > 12) & (well %in% uninduced_wells)) )
trimmed_filtered_df_induced <- trimmed_df %>% filter(expression > gfp_cutoff) %>% filter(!((experiment > 12) & (well %in% uninduced_wells)) )
okay_induced_satgfp <- unique(trimmed_filtered_df_induced$groupID) 
okay_induced_all <- unique(c(okay_induced_pergfp, okay_induced_satgfp, okay_induced_mch))
trimmed_filtered_df_uninduced <- trimmed_df %>% filter(experiment > 12) %>% filter(well %in% uninduced_wells) 
trimmed_filtered_df <- rbind(trimmed_filtered_df_induced, trimmed_filtered_df_uninduced)


gfp_coefficients <- regression_function(trimmed_filtered_df$expression,
                                               trimmed_filtered_df$growthrate,
                                               trimmed_filtered_df$strain)
gfp_coefficients <- gfp_coefficients[order(gfp_coefficients$m), ]
gfp_plot_sat <- plot_exp_gr(trimmed_filtered_df, gfp_coefficients, "Relative Expression\n(ΔGFS/mean(OD660)/h)", colors)
gfp_plot_sat

gfp_sat_slopes <- plot_slopes(trimmed_filtered_df$expression,
                              trimmed_filtered_df$growthrate,
                              trimmed_filtered_df$strain, colors)

ggsave('expr_v_grow/sat_gfp_growth.svg', gfp_plot_sat, width = 3.5, height = 3)

model <- linreg_decent_fixed_b(trimmed_filtered_df$expression,
                               trimmed_filtered_df$growthrate,
                               trimmed_filtered_df$strain)

gfp_sat_top <- as.data.frame(trimmed_filtered_df %>% 
                group_by(strain) %>% 
                slice_max(expression, prop = 0.10) %>%
                summarize(expression = mean(expression), growthrate = mean(growthrate)))
gfp_sat_top <- merge(gfp_sat_top , gfp_coefficients, by='strain', all.x=TRUE)
gfp_sat_top$calc_growthrate <- gfp_sat_top$expression*gfp_sat_top$m+gfp_sat_top$b
gfp_sat_top$percent <- 1-gfp_sat_top$calc_growthrate/gfp_sat_top$b
gfp_sat_top


subplots <- list()
for (tgtstrain in c("CTA", "GGA", "GGG", "GAG")){
  good_induced <- trimmed_filtered_df_induced %>% filter(groupID %like% tgtstrain)
  count(good_induced)
  good_uninduced <- trimmed_filtered_df_uninduced %>% filter(groupID %like% tgtstrain)
  count(good_uninduced)
  df_good <- rbind(good_induced, good_uninduced)
  df_bad <- below_cuttoff_mch_sat %>% filter(groupID %like% tgtstrain)
  count(df_bad)
  threshhold <- gfp_cutoff
  title <- tgtstrain
  xtitle <- ""
  ytitle <- ""
  xtitle <- ""
  #if (tgtstrain == "GAG"){xtitle <- "sfGFP Relative Expression\n(ΔRFS/mean(OD660)/h)"}
  color <- "#6a8ad5"
  xrange <- 14
  
  subplot <- plot_exp_gr_threshold(df_good, df_bad, threshhold, title, xtitle, xrange, ytitle, color)
  subplots <- append(subplots, list(subplot))}
gfp_sat_individuals <- wrap_plots(subplots) + plot_spacer() + plot_layout(ncol=1)
gfp_sat_individuals 

mch_plot + gfp_plot_per + gfp_plot_sat
mch_per_slopes + gfp_per_slopes + gfp_sat_slopes

ggsave('expr_v_grow/sat_gfp_slopes.svg', gfp_sat_slopes, width = 3, height = 3+0.214)
ggsave('expr_v_grow/per_mch_slopes.svg', mch_per_slopes, width = 3.5, height = 3)
ggsave('expr_v_grow/per_gfp_slopes.svg', gfp_per_slopes, width = 3.5, height = 3)

ggsave('expr_v_grow/gfp_sat_individuals.svg', gfp_sat_individuals, width = 3, height = 8.2)
ggsave('expr_v_grow/gfp_per_individuals.svg', gfp_per_individuals, width = 3, height = 9)
ggsave('expr_v_grow/mch_individuals.svg', mch_individuals, width = 3, height = 9)

okay_satgfp_measurements <- unique(trimmed_filtered_df$groupID)

okay_measurements <- c(okay_mch_measurements, okay_pergfp_measurements, okay_satgfp_measurements)
