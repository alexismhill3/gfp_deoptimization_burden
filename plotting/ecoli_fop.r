library(dplyr)
library(ggplot2)
library(patchwork)
library(slider)
library(data.table)
library(zoo)
library(tidyverse)
library(scales)

library(spatstat)


#' Compute empirical cumulative distribution
#'
#' The empirical cumulative distribution function (ECDF) provides an alternative
#' visualisation of distribution. Compared to other visualisations that rely on
#' density (like [geom_histogram()]), the ECDF doesn't require any
#' tuning parameters and handles both continuous and categorical variables.
#' The downside is that it requires more training to accurately interpret,
#' and the underlying visual tasks are somewhat more challenging.
#'
#' @inheritParams layer
#' @inheritParams geom_point
#' @param na.rm If `FALSE` (the default), removes missing values with
#'    a warning.  If `TRUE` silently removes missing values.
#' @param n if NULL, do not interpolate. If not NULL, this is the number
#'   of points to interpolate with.
#' @param pad If `TRUE`, pad the ecdf with additional points (-Inf, 0)
#'   and (Inf, 1)
#' @section Computed variables:
#' \describe{
#'   \item{x}{x in data}
#'   \item{y}{cumulative density corresponding x}
#' }
#' @export
#' @examples
#' df <- data.frame(
#'   x = c(rnorm(100, 0, 3), rnorm(100, 0, 10)),
#'   g = gl(2, 100)
#' )
#' ggplot(df, aes(x)) + stat_ecdf(geom = "step")
#'
#' # Don't go to positive/negative infinity
#' ggplot(df, aes(x)) + stat_ecdf(geom = "step", pad = FALSE)
#'
#' # Multiple ECDFs
#' ggplot(df, aes(x, colour = g)) + stat_ecdf()
stat_ecdf <- function(mapping = NULL, data = NULL,
                      geom = "step", position = "identity",
                      weight =  NULL, 
                      ...,
                      n = NULL,
                      pad = TRUE,
                      na.rm = FALSE,
                      show.legend = NA,
                      inherit.aes = TRUE) {
  layer(
    data = data,
    mapping = mapping,
    stat = StatEcdf,
    geom = geom,
    position = position,
    show.legend = show.legend,
    inherit.aes = inherit.aes,
    params = list(
      n = n,
      pad = pad,
      na.rm = na.rm,
      weight = weight,
      ...
    )
  )
}


#' @rdname ggplot2-ggproto
#' @format NULL
#' @usage NULL
#' @export
#' 

StatEcdf <- ggproto("StatEcdf", Stat,
                    compute_group = function(data, scales, weight, n = NULL, pad = TRUE) {
                      # If n is NULL, use raw values; otherwise interpolate
                      if (is.null(n)) {
                        x <- unique(data$x)
                      } else {
                        x <- seq(min(data$x), max(data$x), length.out = n)
                      }
                      
                      if (pad) {
                        x <- c(-Inf, x, Inf)
                      }
                      y <- ewcdf(data$x, weights=data$weight/sum(data$weight))(x)
                      
                      data.frame(x = x, y = y)
                    },
                    
                    default_aes = aes(y = stat(y)),
                    
                    required_aes = c("x")
)

data = read.csv("with_fop.csv")

data

of_interest = data %>% select(c("fop", "avg", "Accession")) %>% arrange("fop") %>% filter(avg >= 0)


df <- of_interest %>%
  arrange(fop) %>% 
  mutate(prob_seq = seq_along(fop) / n()) %>%
  mutate(prob_mrna = avg / sum(avg), 
         prob_mrna = cumsum(prob_mrna)) 

dna = ggplot(df, aes(x = fop, y = prob_seq)) +
  geom_line(size = 1) +
  theme_bw() + ylab("Probability") +
  theme(text = element_text(size = 16, family="Arial MS"), legend.position="none",
        axis.title.x = element_text(size = 16, family="Arial MS"),
        axis.title.y = element_text(size = 16, family="Arial MS"),
        plot.title = element_text(size = 16, family="Arial MS"))

mrna = ggplot(df, aes(x = fop, y = prob_mrna)) +
  geom_line(size = 1) +
  theme_bw() + ylab("Probability") +
  theme(text = element_text(size = 16, family="Arial MS"), legend.position="none",
        axis.title.x = element_text(size = 16, family="Arial MS"),
        axis.title.y = element_text(size = 16, family="Arial MS"),
        plot.title = element_text(size = 16, family="Arial MS"))

grid = dna + mrna
grid
ggsave("cdf.svg", grid, width = 9, height = 3)

top_5_expressed <- head(df[order(df$avg,decreasing=T),],.05*nrow(df))
mean(top_5_expressed$fop)
weighted.mean(top_5_expressed$fop, top_5_expressed$avg)


fop_less_than_25 <- df %>% filter(fop <= 0.25)
fop_less_than_50 <- df %>% filter(fop <= 0.50)
fop_less_than_75 <- df %>% filter(fop <= 0.75)
fop_less_than_90 <- df %>% filter(fop <= 0.90)

max(fop_less_than_25$prob_seq)
max(fop_less_than_25$prob_mrna)
max(fop_less_than_50$prob_seq)
max(fop_less_than_50$prob_mrna)
max(fop_less_than_75$prob_seq)
max(fop_less_than_75$prob_mrna)
max(fop_less_than_90$prob_seq)
max(fop_less_than_90$prob_mrna)

top_mrna <- df %>% filter(prob_mrna >0.95)
mean(df$fop)
weighted.mean(df$fop, df$avg)
