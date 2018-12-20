library(tidyverse)
library(ggExtra)
library(magrittr) # <3
library(lubridate)
library(stringr) # essencial para trabalhar com textos
library(tidytext) # um dos melhores pacotes para text mining
library(lexiconPT)
library(dplyr)

vec = c('FAZENDO um teste','Atenção','12345')
vec2 = c(1,2,3)
data <- data.frame(vec2,vec)
names(data) <- c('ids','Messages')

tidy <- data %>%
  unnest_tokens(word, messages)# %>% #Break the lyrics into individual words
  # filter(!word %in% undesirable_words)

unnest_tokens(vec)

clean <- tibble(Messages = data$Messages) %>%
  unnest_tokens(word, Messages) %>%
  select(everything())
