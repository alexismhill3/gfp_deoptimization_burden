library(dplyr)
library(ggplot2)
library(patchwork)


# ---------- Some last mile processing
pre_data <- read.csv("../processed_data/experimental_pre_induction.csv")
post_data_per_mch <- read.csv("../processed_data/experimental_per_mcherry.csv")
post_data_per_gfp <- read.csv("../processed_data/experimental_per_gfp.csv")
post_data_sat_gfp <- read.csv("../processed_data/experimental_sat_gfp.csv")

pre_data$gfp_norm <- pre_data$GFP/pre_data$OD660
pre_data$mch_norm <- pre_data$mCherry/pre_data$OD660

pre_data$pre_fluor <-   case_when(
  pre_data$cds %in% c("GFP10",
                               "GFP25",
                               "GFP50",
                               "GFP75",
                               "GFP90",
                               "GGG",
                               "GGA",
                               "GAG",
                               "CTA") ~ pre_data$gfp_norm,
                    
  pre_data$cds %in% c("MCH10",
                               "MCH25",
                               "MCH50",
                               "MCH75",
                               "MCH90") ~ pre_data$mch_norm)
pre_data <- pre_data %>% filter(time == 0)

pre_data <- pre_data %>% select(pre_fluor, rbs, cds, experiment)
colnames(pre_data)[colnames(pre_data) == 'cds'] <- 'strain'

# --------- Boilerplate for selecting expression window
trim_df <- function(df, grow_time, output_time){
  # Grab growth
  growth_rates <- df[df$time == grow_time,]
  growth_rates <- growth_rates[c("groupID", "strain", "rbs", "growthrate", "experiment")]
  # Grab Output
  expression <- df[df$time == output_time,]
  expression <- expression[c("groupID", "expression")]
  # Merge on ID
  merge <- merge(x = growth_rates, y = expression, by = "groupID", all.x = TRUE)
  return (merge)
}

# ---------Plot logic

plot <- function(df){
  result <- ggplot() + geom_point(data = df, aes(x=pre_fluor, y=expression, color=strain, shape=rbs)) + theme_bw() + expand_limits(x=0)
  
  return (result)
}

# -------- Merge on experiment number, RBS, and CDS and plot
global_growth_time = 11700+900*-2
# -- mCherry

mcherry_growth_time <- global_growth_time
mcherry_fluor_time <- global_growth_time+900*2

trimmed_df <- trim_df(post_data_per_mch, mcherry_growth_time, mcherry_fluor_time)
merged = merge(trimmed_df, pre_data, by=c('strain', 'rbs', "experiment"))
mch_plot <- plot(merged)
mch_plot

# -- GFP Percent

gfp_growth_time <- global_growth_time
gfp_fluor_time <- global_growth_time+900*0

trimmed_df <- trim_df(post_data_per_gfp, gfp_growth_time, gfp_fluor_time)
merged = merge(trimmed_df, pre_data, by=c('strain', 'rbs', "experiment"))
gfp_per_plot <- plot(merged)
gfp_per_plot

# -- GFP Sat

gfp_growth_time <- global_growth_time
gfp_fluor_time <- global_growth_time+900*0

trimmed_df <- trim_df(post_data_sat_gfp, gfp_growth_time, gfp_fluor_time)
merged = merge(trimmed_df, pre_data, by=c('strain', 'rbs', "experiment"))
gfp_sat_plot <- plot(merged)
gfp_sat_plot

mch_plot + gfp_per_plot + gfp_sat_plot