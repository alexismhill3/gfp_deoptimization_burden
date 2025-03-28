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
    geom_line(data=strain_dataframe_master, aes(x = time, y = OD660, group=interaction(groupID, well)), alpha = 0.05) +
    ggtitle(paste("Growth of", strain_name, "under IPTG Induction")) + 
    plot_theme + ylab("OD660") +scale_x_time() +
    geom_vline(xintercept=t1, linetype='dashed') +
    geom_vline(xintercept=t3, linetype='dashed') +theme(axis.text=element_text(size=16),
                                                        axis.title=element_text(size=20))
  p2 <- ggplot() + 
    geom_line(data=strain_dataframe_master, aes(x = time, y = fluor, group=interaction(groupID, well)), alpha = 0.05) +
    ggtitle(paste("Fluorescence of ", strain_name, "under IPTG Induction")) + 
    plot_theme + ylab("AU") +scale_x_time() +
    geom_vline(xintercept=t1-900*shift_amnt, linetype='dashed') +
    geom_vline(xintercept=t3-900*shift_amnt, linetype='dashed') +theme(axis.text=element_text(size=16),
                                                                       axis.title=element_text(size=20))
  p3 <- ggplot()+
    geom_line(data=strain_dataframe_master, aes(x = time, y = growthrate, group=interaction(groupID, well)), alpha = 0.05) +
    ggtitle(paste("Growth Rate of ", strain_name, "under IPTG Induction")) + 
    plot_theme + ylab("Growth Rate") +scale_x_time() +
    geom_vline(xintercept=t3, linetype='dashed') +theme(axis.text=element_text(size=16),
                                                        axis.title=element_text(size=20))
  p4 <- ggplot()+
    geom_line(data=strain_dataframe_master, aes(x = time, y = expression, group=interaction(groupID, well)), alpha = 0.05) +
    ggtitle(paste("Expression of ", strain_name, "under IPTG Induction")) + 
    plot_theme + ylab("AU/second") +scale_x_time() +
    geom_vline(xintercept=t3-900*shift_amnt, linetype='dashed')  +theme(axis.text=element_text(size=16),
                                                                        axis.title=element_text(size=20))
  
  
  show(p1 + p2 + p3 + p4)
  
}

# ------------------- Generate
window_size = 3

# -- mCherry
mch_time_start <- 8100
t1 = mch_time_start-900*window_size
t3 = mch_time_start
shift_amnt = -4
mch_fluor_peak = t3-900*shift_amnt

df = read.csv("../processed_data/experimental_per_mcherry.csv")
df <- df %>% filter(groupID %in% okay_induced_all)

peaks <- df %>% filter(groupID %like% "nonsence")
for (sample in unique(df$groupID)){
  graph_master <- df  %>% filter(groupID == sample)
  expression_peak <- graph_master[which.max(graph_master$expression),]
  peaks <- rbind(peaks, expression_peak)
}
mch_peak <- median(peaks$time)
rm(peaks)

grid <- graph_strain_grey(df, "mch", t1, t2, shift_amnt)
grid
ggsave('aggrigate/per_mch_agg.png', grid, width = 9, height = 9)

# -- sfGFP
gfp_time_start <- 8100
t1 = gfp_time_start-900*window_size
t3 = gfp_time_start
shift_amnt = 0
gfp_fluor_peak = t3-900*shift_amnt

df = read.csv("../processed_data/experimental_per_gfp.csv")
df <- df %>% filter(groupID %in% okay_induced_all)

peaks <- df %>% filter(groupID %like% "nonsence")
for (sample in unique(df$groupID)){
  graph_master <- df  %>% filter(groupID == sample)
  expression_peak <- graph_master[which.max(graph_master$expression),]
  peaks <- rbind(peaks, expression_peak)
}
gfp_peak <- median(peaks$time)


grid <- graph_strain_grey(df, 'gfp', t1, t2, shift_amnt)
grid
ggsave('aggrigate/per_gfp_agg.png', grid, width = 9, height = 9)