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
plot_fluor <- function(df, strain_name, maxy){
  filtered_master <- df %>% filter(groupID %like% strain_name)
  subplot <- ggplot() + 
    geom_line(data=filtered_master, aes(x = time, y = fluor, group=groupID, alpha = 0.05)) +
    scale_x_time(breaks = scales::breaks_width("2 hours"), labels=NULL, limits=c(0, 900*4*8)) +
    geom_vline(xintercept=t1-900*shift_amnt, linetype='dashed') +
    geom_vline(xintercept=t3-900*shift_amnt, linetype='dashed') + theme_bw() +
    theme(axis.text=element_text(size=16), axis.title=element_text(size=20), legend.position="none")+ 
    scale_y_continuous(limit=c(0, maxy), labels=NULL) + xlab("") + ylab("")
  return(subplot)} 

plot_grid <- function(df, maxy){
  unique_cds <- sort(unlist(unique(df['strain'])))
  unique_rbs <- sort(unlist(unique(df['rbs'])))
  
  subplots <- list()
  row_no <- 0
  for (cds in unique_cds){
    row_no <- row_no +1
    column_no <- 0
    for (rbs in unique_rbs){
      column_no <- column_no +1
      subplot <- plot_fluor(df, paste(cds, rbs), maxy)
      if (row_no == 1){
        subplot <- subplot + ggtitle(rbs)
      }
      if (column_no == 1){
        subplot <- subplot + ylab(cds)+ scale_y_continuous(limit=c(0, maxy))
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
mch_time_start <- 11700-1*900
t1 = mch_time_start-900*window_size
t3 = mch_time_start
shift_amnt = -3

maxy = 15


df = read.csv("../processed_data/experimental_per_mcherry.csv")

grid <- plot_grid(df, maxy)
grid
ggsave('fluor_grid/per_mch_fluor.png', grid, width = 9, height = 9)

# -- sfGFP percent
gfp_time_start <- 11700-2*900
t1 = gfp_time_start-900*window_size
t3 = gfp_time_start
shift_amnt = 0

maxy = 10

df = read.csv("../processed_data/experimental_per_gfp.csv")

grid <- plot_grid(df, maxy)
grid
ggsave('fluor_grid/per_gfp_fluor.png', grid, width = 9, height = 9)


# -- sfGFP sat
gfp_time_start <- 11700-2*900
t1 = gfp_time_start-900*window_size
t3 = gfp_time_start
shift_amnt = 0

maxy = 80000

df = read.csv("../processed_data/experimental_sat_gfp.csv")

grid <- plot_grid(df, maxy)
grid
ggsave('fluor_grid/per_gfp_fluor.png', grid, width = 9, height = 9)