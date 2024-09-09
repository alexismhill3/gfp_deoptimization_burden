library(dplyr)
library(ggplot2)
library(patchwork)
library(slider)
library(data.table)
library(zoo)
library(tidyverse)
library(scales)

# # Load all the data into R
#
files= c('../../wet_scripting/percent_day_1/per1clean.csv',
         '../../wet_scripting/percent_day_2/per2clean.csv',
         '../../wet_scripting/percent_day_3/per3clean.csv')


window_size <- 4

filenames <- c(files)
experiment_ID <- 0

# Combine data into a complete dataframe with normalized values   ----------------------
well_placements <- data.frame(cds = c(0),
                              rbs = c(0),
                              well = c('l'),
                              experiment =c(1))


master_df = data.frame()
for (filename in files){
  csv_data <- read.csv(filename) # Load in the data
  experiment_ID <- experiment_ID + 1
  
  used_wells <- unique(csv_data$well)
  for (welltgt in used_wells){
    well_data <- csv_data %>% filter(well == welltgt)
    cds <- well_data$strain[1]
    print(well_data$strain[1])
    rbs <- well_data$rbs[1]
    well_placements[nrow(well_placements)+1, ] <- c(cds, rbs, welltgt, experiment_ID)
  }
  
  # Merge technical replicates
  csv_data <- csv_data %>% group_by(strain, rbs, time)
  #csv_data <- csv_data %>% dplyr::summarize(GFP = mean(GFP), mCherry = mean(mCherry), OD660 = mean(OD660))
  
  
  
  csv_data$gfp_norm <- csv_data$GFP/csv_data$OD660
  csv_data$mch_norm <- csv_data$mCherry/csv_data$OD660
  csv_data$lnOD660 <- log(csv_data$OD660)
  csv_data$experiment <- experiment_ID
  csv_data$groupID <- paste(csv_data$experiment,
                            csv_data$strain,
                            csv_data$rbs)
  
  # Fix time
  csv_data$time <- round(csv_data$time/900)*900
  
  # Create sliding windows
  processed_data <- data.frame()
  for (sample in unique(csv_data$groupID)){
    subset <- csv_data %>% filter(groupID == sample)
    subset$gfp_expression <- c(rep(NaN, window_size), 3600*diff(subset$GFP, lag=window_size))/slide_dbl(subset$OD660, ~mean(.x), .before=window_size)
    subset$mch_expression <- c(rep(NaN, window_size), 3600*diff(subset$mCherry, lag=window_size))/slide_dbl(subset$OD660, ~mean(.x), .before=window_size)
    
    subset$growthrate <- c(rep(NaN, window_size), 3600*diff(subset$lnOD660, lag=window_size)/(900*window_size))
    processed_data <- rbind(processed_data, subset)
  }
  
  # Add it to the master dataframe
  master_df = rbind(master_df, processed_data)
}

# Set target fluorescence depending on strain #tgt_fluor #tgt_expression

master_df<- master_df %>%
  mutate(tgt_fluor = case_when(groupID %like% "GFP" ~ gfp_norm,
                               groupID %like% "MCH" ~ mch_norm))
master_df <- master_df %>%
  mutate(tgt_expression = case_when(groupID %like% "GFP" ~ gfp_expression,
                                    groupID %like% "MCH" ~ mch_expression))

master_df <- master_df[c("time", "well", "strain", "rbs", "experiment", "groupID", "OD660", "growthrate", "tgt_fluor", "tgt_expression")]
names(master_df )[names(master_df ) == 'tgt_fluor'] <- 'fluor'
names(master_df )[names(master_df ) == 'tgt_expression'] <- 'expression'

per_gfp_df <-  master_df %>% filter(groupID %like% "GFP")
per_mch_df <-  master_df %>% filter(groupID %like% "MCH")

write.csv(per_gfp_df, file = "../experimental_per_gfp.csv")
write.csv(per_mch_df, file = "../experimental_per_mcherry.csv")