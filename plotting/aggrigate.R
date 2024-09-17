# ----------------- Boilerplate
library(dplyr)
library(ggplot2)
library(patchwork)
library(slider)
library(data.table)
library(zoo)
library(tidyverse)
library(scales)

plot_theme = theme_bw()
# ----------------- Plot logic
graph_strain_grey<- function(strain_dataframe_master, strain_name, t1, t2, shift_amnt){
  
  p1 <- ggplot() + 
    geom_line(data=strain_dataframe_master, aes(x = time, y = OD660, group=groupID, alpha = 0.05)) +
    ggtitle(paste("Growth of", strain_name, "under IPTG Induction")) + 
    plot_theme + ylab("OD660") +scale_x_time() +
    geom_vline(xintercept=t1, linetype='dashed') +
    geom_vline(xintercept=t3, linetype='dashed') +theme(axis.text=element_text(size=16),
                                                        axis.title=element_text(size=20))
  p2 <- ggplot() + 
    geom_line(data=strain_dataframe_master, aes(x = time, y = fluor, group=groupID, alpha = 0.05)) +
    ggtitle(paste("Fluorescence of ", strain_name, "under IPTG Induction")) + 
    plot_theme + ylab("AU") +scale_x_time() +
    geom_vline(xintercept=t1-900*shift_amnt, linetype='dashed') +
    geom_vline(xintercept=t3-900*shift_amnt, linetype='dashed') +theme(axis.text=element_text(size=16),
                                                                       axis.title=element_text(size=20))
  p3 <- ggplot()+
    geom_line(data=strain_dataframe_master, aes(x = time, y = growthrate, group=groupID, alpha = 0.05)) +
    ggtitle(paste("Growth Rate of ", strain_name, "under IPTG Induction")) + 
    plot_theme + ylab("Growth Rate") +scale_x_time() +
    geom_vline(xintercept=t3, linetype='dashed') +theme(axis.text=element_text(size=16),
                                                        axis.title=element_text(size=20))
  p4 <- ggplot()+
    geom_line(data=strain_dataframe_master, aes(x = time, y = expression, group=groupID, alpha = 0.05)) +
    ggtitle(paste("Expression of ", strain_name, "under IPTG Induction")) + 
    plot_theme + ylab("AU/second") +scale_x_time() +
    geom_vline(xintercept=t3-900*shift_amnt, linetype='dashed')  +theme(axis.text=element_text(size=16),
                                                                        axis.title=element_text(size=20))
  
  
  show(p1 + p2 + p3 + p4)
  
}

# ------------------- Generate
window_size = 3

# -- mCherry
mch_time_start <- 11700
t1 = mch_time_start-900*window_size
t3 = mch_time_start
shift_amnt = -3

df = read.csv("../processed_data/experimental_per_mcherry.csv")

grid <- graph_strain_grey(df, "mch", t1, t2, shift_amnt)
grid
ggsave('aggrigate/per_mch_agg.png', grid, width = 9, height = 9)

# -- sfGFP
gfp_time_start <- 11700-900
t1 = gfp_time_start-900*window_size
t3 = gfp_time_start
shift_amnt = 0

df = read.csv("../processed_data/experimental_per_gfp.csv")

grid <- graph_strain_grey(df, 'gfp', t1, t2, shift_amnt)
grid
ggsave('aggrigate/per_gfp_agg.png', grid, width = 9, height = 9)