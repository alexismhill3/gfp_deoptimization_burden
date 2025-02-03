# ----------------- Boilerplate
library(dplyr)
library(ggplot2)
library(patchwork)
library(slider)
library(data.table)
library(zoo)
library(tidyverse)
library(scales)

# ----------------- Plot logic
timeHM_formatter <- function(x) { # https://r-graphics.org/recipe-axes-time-rel
  x = x/60
  h <- floor(x/60)
  m <- floor(x %% 60)
  lab <- sprintf("%d", h) # Format the strings as HH:MM
  return(lab)
}


plot_growth <- function(df, strain_name){
  filtered_master <- df %>% filter(groupID %like% strain_name)
  return(ggplot() + 
           geom_line(data=filtered_master, aes(x = time, y = OD660, group=groupID), alpha = 0.3) +
           scale_x_continuous(breaks=c(0,900*8, 900*16,900*24, 900*32, 900*40), labels=NULL, limits=c(0, 900*4*6)) +
           geom_vline(xintercept=t1, linetype='dashed') +
           geom_vline(xintercept=t3, linetype='dashed')  + theme_bw() +
           xlab("") + ylab("") + scale_y_continuous(limits = c(0, 1), labels=NULL) +
           theme(legend.position="none") + theme(text = element_text(size = 16, family="Arial MS"), legend.position="none",
                                                 axis.title.x = element_text(size = 16, family="Arial MS"),
                                                 axis.title.y = element_text(size = 16, family="Arial MS"),
                                                 plot.title = element_text(size = 16, family="Arial MS")))}



plot_grid <- function(df){
  unique_cds <- sort(unlist(unique(df['strain'])))
  unique_rbs <- sort(unlist(unique(df['rbs'])))
  
  subplots <- list()
  row_no <- 0
  for (cds in unique_cds){
    row_no <- row_no +1
    column_no <- 0
    for (rbs in unique_rbs){
      column_no <- column_no +1
      subplot <- plot_growth(df, paste(cds, rbs))
      if (row_no == 1){
        subplot <- subplot + ggtitle(rbs) +theme()
      }
      if (column_no == 1){
        subplot <- subplot + ylab(cds)+ scale_y_continuous(limits = c(0, 1))
      }
      if (row_no == length(unique_cds)){  # If == last row
        subplot <- subplot +scale_x_continuous(breaks=c(0, 900*8, 900*16,900*24, 900*32, 900*40), limits=c(0, 900*4*8), labels=timeHM_formatter) 
      }
      
      subplots <- append(subplots, list(subplot))
    }
  }
  return (wrap_plots(subplots) + plot_layout(axis_title=))
  
}

# ------------------- Generate
window_size = 4

# -- mCherry
mch_time_start <- 8100
t1 = mch_time_start-900*window_size
t3 = mch_time_start


df = read.csv("../processed_data/experimental_per_mcherry.csv")
df <- df %>% filter(groupID %in% okay_measurements)


grid <- plot_grid(df)
grid
ggsave('fluor_grid/figure_s5.svg', grid, width = 9, height = 9)

# -- sfGFP
gfp_time_start <- 8100
t1 = gfp_time_start-900*window_size
t3 = gfp_time_start

df = read.csv("../processed_data/experimental_per_gfp.csv")
df <- df %>% filter(groupID %in% okay_measurements)


grid <- plot_grid(df)
grid
ggsave('fluor_grid/figure_s3.svg', grid, width = 9, height = 9)

df = read.csv("../processed_data/experimental_sat_gfp.csv")
df <- df %>% filter(groupID %in% okay_measurements)


grid <- plot_grid(df)
grid
ggsave('fluor_grid/figure_s7.svg', grid, width = 9, height = 9)