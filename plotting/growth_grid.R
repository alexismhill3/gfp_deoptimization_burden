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
plot_growth <- function(df, strain_name){
  filtered_master <- df %>% filter(groupID %like% strain_name)
  return(ggplot() + 
           geom_line(data=filtered_master, aes(x = time, y = OD660, group=interaction(groupID, well), alpha = 0.05)) +
           scale_x_time(breaks = scales::breaks_width("2 hours"), labels=NULL, limits=c(0, 900*4*8)) +
           geom_vline(xintercept=t1, linetype='dashed') +
           geom_vline(xintercept=t3, linetype='dashed')  + theme_bw() +
           xlab("") + ylab("") + scale_y_continuous(limits = c(0, 1), labels=NULL) +
           theme(legend.position="none") + theme(axis.text=element_text(size=16), axis.title=element_text(size=20)))}


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
        subplot <- subplot + ggtitle(rbs)
      }
      if (column_no == 1){
        subplot <- subplot + ylab(cds)+ scale_y_continuous(limits = c(0, 1))
      }
      if (row_no == length(unique_cds)){  # If == last row
        subplot <- subplot +scale_x_time(breaks = scales::breaks_width("2 hours"), limits=c(0, 900*4*8), labels=label_time(format = "%H")) 
      }
      
      subplots <- append(subplots, list(subplot))
    }
  }
  return (wrap_plots(subplots))
  
}

# ------------------- Generate
window_size = 4

# -- mCherry
mch_time_start <- 11700
t1 = mch_time_start-900*window_size
t3 = mch_time_start
shift_amnt = -3


df = read.csv("../processed_data/experimental_per_mcherry.csv")

grid <- plot_grid(df)
grid
ggsave('fluor_grid/per_mch_growth.png', grid, width = 9, height = 9)

# -- sfGFP
gfp_time_start <- 11700 
t1 = gfp_time_start-900*window_size
t3 = gfp_time_start
shift_amnt = 0

df = read.csv("../processed_data/experimental_per_gfp.csv")

grid <- plot_grid(df)
grid
ggsave('fluor_grid/per_gfp_growth.png', grid, width = 9, height = 9)