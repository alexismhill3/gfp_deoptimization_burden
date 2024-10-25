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
files= c('../../wet_scripting/percent_day_1/per1clean.csv',          #1
         '../../wet_scripting/percent_day_2/per2clean.csv',          #2
         '../../wet_scripting/percent_day_3/per3clean.csv',          #3
         '../../wet_scripting/saturation_day_1/sat1clean.csv',       #4
         '../../wet_scripting/saturation_day_2/sat2clean.csv',       #5
         '../../wet_scripting/saturation_day_3/sat3clean.csv',       #6
         '../../wet_scripting/percent_day_4/per4clean.csv',          #7
         '../../wet_scripting/percent_day_5/per5clean.csv',          #8
         '../../wet_scripting/percent_day_6/per6clean.csv',          #9
         '../../wet_scripting/low_temp_day_1/LT1clean.csv',          #10
         '../../wet_scripting/low_temp_day_2/LT2clean.csv',          #11
         '../../wet_scripting/low_temp_day_3/LT3clean.csv',          #12
         '../../wet_scripting/uninduced_day_1/uninduced1clean.csv',  #13
         '../../wet_scripting/uninduced_day_2/uninduced2clean.csv',  #14
         '../../wet_scripting/uninduced_day_3/uninduced3clean.csv',  #15
         '../../wet_scripting/uninduced_day_4/uninduced4clean.csv',  #16
         '../../wet_scripting/uninduced_day_5/uninduced5clean.csv',  #17
         '../../wet_scripting/uninduced_day_6/uninduced6clean.csv',  #18
         '../../wet_scripting/uninduced_day_7/uninduced7clean.csv',  #19
         '../../wet_scripting/uninduced_day_8/uninduced8clean.csv',  #20
         '../../wet_scripting/uninduced_day_9/uninduced9clean.csv')  #21


window_size <- 4

filenames <- c(files)
experiment_ID <- 0

# Combine data into a complete dataframe with normalized values   ----------------------
well_placements <- data.frame(cds = c(0),
                              rbs = c(0),
                              well = c('l'),
                              experiment =c(1))

rbs_names <- c('T7' = 'R1',
               'A' = 'R0.25',
               'B' = 'R0.5',
               'C' = 'R2',
               'D' = 'R4')


master_df = data.frame()
for (filename in files){
  csv_data <- read.csv(filename) # Load in the data
  
  experiment_ID <- experiment_ID + 1
  
  used_wells <- unique(csv_data$well)
  for (welltgt in used_wells){
    well_data <- csv_data %>% filter(well == welltgt)
    cds <- well_data$strain[1]
    rbs <- well_data$rbs[1]
    well_placements[nrow(well_placements)+1, ] <- c(cds, rbs, welltgt, experiment_ID)
  }
  
  # Merge technical replicates
  #csv_data <- csv_data %>% group_by(strain, rbs, time)
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
    
    # Expression formula
    subset$gfp_expression <- c(rep(NaN, window_size), diff(subset$GFP, lag=window_size))/slide_dbl(subset$OD660, ~mean(.x), .before=window_size)
    subset$mch_expression <- c(rep(NaN, window_size), window_size*diff(subset$mCherry, lag=window_size))/slide_dbl(subset$OD660, ~mean(.x), .before=window_size)
    
    # Alternative expression formula
    #subset$gfp_expression <- c(rep(NaN, window_size), 900*window_size*diff(subset$gfp_norm, lag=window_size))
    #subset$mch_expression <- c(rep(NaN, window_size), 900*window_size*diff(subset$mch_expression, lag=window_size))
    
    
    subset$growthrate <- c(rep(NaN, window_size), diff(subset$lnOD660, lag=window_size))
    processed_data <- rbind(processed_data, subset)
  }
  
  # Add it to the master dataframe
  master_df = rbind(master_df, processed_data)
}
master_df <- master_df  %>% filter_all(all_vars(!is.infinite(.)))

# Normalize fluorescence to maximum appearant fluorescence for each fluorophore
max_gfp <- max(master_df$GFP)
master_df$GFP <- master_df$GFP/max_gfp*10
master_df$gfp_norm <- master_df$gfp_norm/max_gfp*10
master_df$gfp_expression <- master_df$gfp_expression/max_gfp*10

max_mch <- max(master_df$mCherry)
master_df$mCherry <- master_df$mCherry/max_mch*10
master_df$mch_norm <- master_df$mch_norm/max_mch*10
master_df$mch_expression <- master_df$mch_expression/max_mch*10


# Set target fluorescence depending on strain #tgt_fluor #tgt_expression

master_df<- master_df %>%
  mutate(tgt_fluor = case_when(groupID %like% "GFP" ~ gfp_norm,
                               groupID %like% "GGA" ~ gfp_norm,
                               groupID %like% "GAG" ~ gfp_norm,
                               groupID %like% "GGG" ~ gfp_norm,
                               groupID %like% "CTA" ~ gfp_norm,
                               groupID %like% "MCH" ~ mch_norm))

master_df <- master_df %>%
  mutate(tgt_expression = case_when(groupID %like% "GFP" ~ gfp_expression,
                                    groupID %like% "GGA" ~ gfp_expression,
                                    groupID %like% "GAG" ~ gfp_expression,
                                    groupID %like% "GGG" ~ gfp_expression,
                                    groupID %like% "CTA" ~ gfp_expression,
                                    groupID %like% "MCH" ~ mch_expression))

master_df <- master_df[c("time", "well", "strain", "rbs", "experiment", "groupID", "OD660", "growthrate", "tgt_fluor", "tgt_expression")]
names(master_df )[names(master_df ) == 'tgt_fluor'] <- 'fluor'
names(master_df )[names(master_df ) == 'tgt_expression'] <- 'expression'



rbs_names <- c('E' = 'R1',
               'A' = 'R0.25',
               'B' = 'R0.5',
               'C' = 'R2',
               'D' = 'R4')

# Make RBS names abstract
master_df$rbs = names(rbs_names)[match(master_df$rbs, rbs_names)]
master_df$groupID <- paste(master_df$experiment,
                           master_df$strain,
                           master_df$rbs)


# Save
per_mch_df <-  master_df %>% filter(groupID %like% "MCH")
write.csv(per_mch_df, file = "../experimental_per_mcherry.csv")

per_gfp_df <- master_df %>% filter(groupID %like% "GFP")
write.csv(per_gfp_df, file = "../experimental_per_gfp.csv")

sat_gfp_df <- master_df %>% filter(strain %in% c("GFP50", "GGG", "GGA", "GAG", "CTA"))
write.csv(sat_gfp_df, file = "../experimental_sat_gfp.csv")