### Install and load all relevant packages for all analyses ###

# List of packages to load
packages <- c("tidyverse", "haven", "AER", "lubridate", "interflex", "ggpubr", "stargazer", 
              "reshape2", "ggsignif", "estimatr", "fixest", "texreg", "networkD3"
)

# Function to check and install packages
install_and_load <- function(package_name) {
  if (!requireNamespace(package_name, quietly = TRUE)) {
    install.packages(package_name, dependencies = TRUE)
  }
  library(package_name, character.only = TRUE)
}

# Load and install packages
lapply(packages, install_and_load)





### Load data ###

load("edf1.RData")
load("edf2.RData")
edf <- bind_rows(edf1,edf2)



### Data wrangling ###

edf$ec <- "No Echo Chamber"
edf$ec[edf$community_all_periods == 0] <- "Moderate Echo Chamber"
edf$ec[edf$community_all_periods == 1] <- "Extreme Echo Chamber"
table(edf$ec)



### H1 ###


## for Tweets
contingency_table <- table(edf$ec)

# Perform Chi-square test

  test_results <- chisq.test(contingency_table)

# Create pairwise comparisons
pairwise_comparisons <- combn(names(contingency_table), 2, simplify = FALSE)

raw_p <- sapply(pairwise_comparisons, function(pair) {
  n1 <- contingency_table[[pair[1]]]
  n2 <- contingency_table[[pair[2]]]
  binom.test(n1, n1 + n2, p = 0.5)$p.value
})
p_values <- p.adjust(raw_p, method = "holm")


# Convert p-values to significance annotations
annotations <- sapply(p_values, function(p) {
  if (p < 0.001) "*** p < 0.001" else if (p < 0.01) "**" else if (p < 0.05) "*" else "NS"
})


proportions <- edf %>%
  group_by(ec) %>%
  summarise(
    count = n(),
    proportion = count / nrow(edf),
    total = nrow(edf)
  )

# Calculate 95% confidence intervals
proportions <- proportions %>%
  rowwise() %>%
  mutate(
    lower_ci = proportion - qt(0.975, total - 1) * sqrt((proportion * (1 - proportion)) / total),
    upper_ci = proportion + qt(0.975, total - 1) * sqrt((proportion * (1 - proportion)) / total)
  )
  
  

# Create the plot
h1_1 <- ggplot(proportions, aes(x = ec, y = proportion)) +
  geom_bar(stat = "identity", fill = "skyblue", color = "black", width = 0.7, size = 3) +
  geom_errorbar(aes(ymin = lower_ci, ymax = upper_ci), width = 0.2, size = 3) +
  geom_text(aes(label = count, y = proportion / 2), vjust = 0.5, size = 8) +
  labs(
    title = "B: Proportion of Tweets in Each Echo Chamber Category",
    x = "Echo Chamber Category",
    y = "Proportion of Tweets"
  ) +
  theme_minimal(base_size = 25)

# Add significance annotations
h1_1 <- h1_1 +
  geom_signif(
    comparisons = pairwise_comparisons,
    annotations = annotations,
    y_position = c(0.6, 0.7, 0.8),  
    textsize = 8
  )
h1_1

## for MEPs
username_categories <- edf %>%
  group_by(username) %>%
  summarise(category = names(sort(table(ec), decreasing = TRUE))[1])

contingency_table2 <- table(username_categories$category)

# Perform Chi-square test
sample_size <- sum(contingency_table2)
test_results <- chisq.test(contingency_table2)

# Create pairwise comparisons
pairwise_comparisons2 <- combn(names(contingency_table2), 2, simplify = FALSE)
raw_p <- sapply(pairwise_comparisons2, function(pair) {
  n1 <- contingency_table2[[pair[1]]]
  n2 <- contingency_table2[[pair[2]]]
  binom.test(n1, n1 + n2, p = 0.5)$p.value
})

p_values <- p.adjust(raw_p, method = "holm")

# Convert p-values to significance annotations
annotations <- sapply(p_values, function(p) {
  if (p < 0.001) "*** p < 0.001" else if (p < 0.01) "**" else if (p < 0.05) "*" else "NS"
})


proportions2 <- username_categories %>%
  group_by(category) %>%
  summarise(
    count = n(),
    proportion = count / nrow(username_categories),
    total = nrow(username_categories)
  )

# Calculate 95% confidence intervals
proportions2 <- proportions2 %>%
  rowwise() %>%
    mutate(
      lower_ci = proportion - qt(0.975, total - 1) * sqrt((proportion * (1 - proportion)) / total),
      upper_ci = proportion + qt(0.975, total - 1) * sqrt((proportion * (1 - proportion)) / total)
    )




# Create the plot
h1_2 <- ggplot(proportions2, aes(x = category, y = proportion)) +
  geom_bar(stat = "identity", fill = "deepskyblue2", color = "black", width = 0.7, size = 3) +
  geom_errorbar(aes(ymin = lower_ci, ymax = upper_ci), width = 0.2, size = 3) +
  geom_text(aes(label = count, y = proportion / 2), vjust = 0.5, size = 8) +
  labs(
    title = "A: Proportion of MEPs in Each Echo Chamber Category",
    x = "Echo Chamber Category",
    y = "Proportion of MEPs"
  ) +
  theme_minimal(base_size = 25)

# Add significance annotations
h1_2 <- h1_2 +
  geom_signif(
    comparisons = pairwise_comparisons2,
    annotations = annotations,
    y_position = c(0.6, 0.7, 0.8), 
    textsize = 8
  )


# Plot both plots together
ggarrange(h1_2, h1_1)








### H2 ###


### for left right ###

username_categories2 <- edf %>%
  group_by(username, lrgen) %>%
  summarise(category = names(sort(table(ec), decreasing = TRUE))[1]) 



# Calculate means and confidence intervals
summary_stats <- username_categories2 %>%
  group_by(category) %>%
  summarise(
    mean_lrgen = mean(lrgen, na.rm = TRUE),
    sd_lrgen = sd(lrgen, na.rm = TRUE),
    n = n()
  ) %>%
  mutate(
    se = sd_lrgen / sqrt(n),
    lower_ci = mean_lrgen - qt(0.975, n - 1) * se,
    upper_ci = mean_lrgen + qt(0.975, n - 1) * se
  )



# Perform pairwise t-tests
pairwise_comparisons3 <- combn(unique(username_categories2$category), 2, simplify = FALSE)
p_values3 <- sapply(pairwise_comparisons3, function(pair) {
  t_test3 <- t.test(lrgen ~ category, data = subset(username_categories2, category %in% pair))
  t_test3$p.value
})

# Convert p-values to significance annotations
annotations3 <- sapply(p_values3, function(p) {
  if (p < 0.001) "*** p < 0.001" else if (p < 0.01) "**" else if (p < 0.05) "*" else "NS"
})


# Calculate Median LR position
medianLR <- median(edf$lrgen, na.rm = TRUE)

# Create the plot
h2_1 <- ggplot(summary_stats, aes(x = category, y = mean_lrgen)) +
  geom_bar(stat = "identity", fill = "grey", color = "black", width = 0.7, size = 3) +
  geom_errorbar(aes(ymin = lower_ci, ymax = upper_ci), width = 0.2, size = 3) +
  geom_text(aes(label = round(mean_lrgen, 2), y = mean_lrgen / 2), vjust = 0.5, size = 8) +
  labs(
    title = "A: Left-Right Ideology in Each Echo Chamber Category",
    x = "Echo Chamber Category",
    y = "LR Mean"
  ) +
  theme_minimal(base_size = 18) +
  geom_hline(yintercept = medianLR, color = "red", linetype = "dashed", size = 2) +
  scale_y_continuous(limits = c(0, 10))

# Add significance annotations
h2_1 <- h2_1 +
  geom_signif(
    comparisons = pairwise_comparisons3,
    annotations = annotations3,
    y_position = max(summary_stats$mean_lrgen) + c(-2, -1, 0),  # Adjust y_position to avoid overlap
    textsize = 8
  )

# Print the plot
print(h2_1)





### for eu position ###

username_categories3 <- edf %>%
  group_by(username, eu_position) %>%
  summarise(category = names(sort(table(ec), decreasing = TRUE))[1]) 



# Calculate means and confidence intervals
summary_stats2 <- username_categories3 %>%
  group_by(category) %>%
  summarise(
    mean_eu_position = mean(eu_position, na.rm = TRUE),
    sd_eu_position = sd(eu_position, na.rm = TRUE),
    n = n()
  ) %>%
  mutate(
    se = sd_eu_position / sqrt(n),
    lower_ci = mean_eu_position - qt(0.975, n - 1) * se,
    upper_ci = mean_eu_position + qt(0.975, n - 1) * se
  )



# Perform pairwise t-tests
pairwise_comparisons4 <- combn(unique(username_categories3$category), 2, simplify = FALSE)
p_values4 <- sapply(pairwise_comparisons4, function(pair) {
  t_test4 <- t.test(eu_position ~ category, data = subset(username_categories3, category %in% pair))
  t_test4$p.value
})

# Convert p-values to significance annotations
annotations4 <- sapply(p_values4, function(p) {
  if (p < 0.001) "*** p < 0.001" else if (p < 0.01) "**" else if (p < 0.05) "*" else "NS"
})


# Calculate Median EU position
medianEU <- median(edf$eu_position, na.rm = TRUE)

# Create the plot
h2_2 <- ggplot(summary_stats2, aes(x = category, y = mean_eu_position)) +
  geom_bar(stat = "identity", fill = "deepskyblue2", color = "black", width = 0.7, size = 3) +
  geom_errorbar(aes(ymin = lower_ci, ymax = upper_ci), width = 0.2, size = 3) +
  geom_text(aes(label = round(mean_eu_position, 2), y = mean_eu_position / 2), vjust = 0.5, size = 8) +
  labs(
    title = "C: EU Position in Each Echo Chamber Category",
    x = "Echo Chamber Category",
    y = "Mean EU Position"
  ) +
  theme_minimal(base_size = 18) +
  geom_hline(yintercept = medianEU, color = "red", linetype = "dashed", size = 2) +
  scale_y_continuous(limits = c(0, 10))

# Add significance annotations
h2_2 <- h2_2 +
  geom_signif(
    comparisons = pairwise_comparisons4,
    annotations = annotations4,
    y_position = max(summary_stats2$mean_eu_position) + c(0, 0.5, 1),  # Adjust y_position to avoid overlap
    textsize = 8
  )

# Print the plot
print(h2_2)





### for galtan position ###

username_categories4 <- edf %>%
  group_by(username, galtan) %>%
  summarise(category = names(sort(table(ec), decreasing = TRUE))[1]) 



# Calculate means and confidence intervals
summary_stats3 <- username_categories4 %>%
  group_by(category) %>%
  summarise(
    mean_galtan = mean(galtan, na.rm = TRUE),
    sd_galtan = sd(galtan, na.rm = TRUE),
    n = n()
  ) %>%
  mutate(
    se = sd_galtan / sqrt(n),
    lower_ci = mean_galtan - qt(0.975, n - 1) * se,
    upper_ci = mean_galtan + qt(0.975, n - 1) * se
  )



# Perform pairwise t-tests
pairwise_comparisons5 <- combn(unique(username_categories4$category), 2, simplify = FALSE)
p_values5 <- sapply(pairwise_comparisons5, function(pair) {
  t_test5 <- t.test(galtan ~ category, data = subset(username_categories4, category %in% pair))
  t_test5$p.value
})

# Convert p-values to significance annotations
annotations5 <- sapply(p_values5, function(p) {
  if (p < 0.001) "*** p < 0.001" else if (p < 0.01) "**" else if (p < 0.05) "*" else "NS"
})


# Calculate Median GALTAN position
medianGT <- median(edf$galtan, na.rm = TRUE)



# Create the plot
h2_3 <- ggplot(summary_stats3, aes(x = category, y = mean_galtan)) +
  geom_bar(stat = "identity", fill = "darkturquoise", color = "black", width = 0.7, size = 3) +
  geom_errorbar(aes(ymin = lower_ci, ymax = upper_ci), width = 0.2, size = 3) +
  geom_text(aes(label = round(mean_galtan, 2), y = mean_galtan / 2), vjust = 0.5, size = 8) +
  labs(
    title = "B: GALTAN Ideology in Each Echo Chamber Category",
    x = "Echo Chamber Category",
    y = "GALTAN Mean"
  ) +
  theme_minimal(base_size = 18) +
  geom_hline(yintercept = medianGT, color = "red", linetype = "dashed", size = 2) +
  scale_y_continuous(limits = c(0, 10))

# Add significance annotations
h2_3 <- h2_3 +
  geom_signif(
    comparisons = pairwise_comparisons5,
    annotations = annotations5,
    y_position = max(summary_stats3$mean_galtan) + c(0, 0.5, 1),  # Adjust y_position to avoid overlap
    textsize = 8
  )

# Print the plot
print(h2_3)


ggarrange(h2_1,h2_3,h2_2, nrow = 1)




### echo chamber categories by party membership ###

username_categories5 <- edf %>%
  group_by(username, eu_party_abbr) %>%
  summarise(category = names(sort(table(ec), decreasing = TRUE))[1]) 


# Calculate proportions and confidence intervals
proportions3 <- username_categories5 %>%
  group_by(eu_party_abbr, category) %>%
  summarise(
    count = n(),
    .groups = 'drop'
  ) %>%
  group_by(eu_party_abbr) %>%
  mutate(
    total = sum(count),
    proportion = count / total
  ) %>%
  ungroup() %>%
  mutate(
    lower_ci = proportion - qt(0.975, total - 1) * sqrt((proportion * (1 - proportion)) / total),
    upper_ci = proportion + qt(0.975, total - 1) * sqrt((proportion * (1 - proportion)) / total)
  )

proportions3$category[proportions3$category == "Moderate Echo Chamber"] <- "Moderate EC"
proportions3$category[proportions3$category == "No Echo Chamber"] <- "No EC"
proportions3$category[proportions3$category == "Extreme Echo Chamber"] <- "Extreme EC"


# Create the plot
h2_4 <- ggplot(proportions3, aes(x = category, y = proportion, fill = category)) +
  geom_bar(stat = "identity", color = "black", width = 0.7, size = 1.5) +
  geom_errorbar(aes(ymin = lower_ci, ymax = upper_ci), width = 0.2, size = 1.5) +
  geom_text(aes(label = count, y = proportion / 2), vjust = 0.5, hjust = 1.3, size = 5) +
  facet_wrap(~ eu_party_abbr, scales = "free") +
  scale_y_continuous(limits = c(0, 1)) +
  labs(
    title = "A: Proportion of MEPs in Each Echo Chamber Category by EU Party Family",
    x = "Echo Chamber Category",
    y = "Proportion of MEPs"
  ) +
  theme_minimal(base_size = 18) +
  theme(legend.position = "none")


# Print the plot
print(h2_4)






### echo chamber categories by commission dummy ###

edf$commission[edf$commission_dummy == 1] <- "Commission"
edf$commission[edf$commission_dummy == 0] <- "Parliament"

username_categories6 <- edf %>%
  group_by(username, commission) %>%
  summarise(category = names(sort(table(ec), decreasing = TRUE))[1]) 


# Calculate proportions and confidence intervals
proportions4 <- username_categories6 %>%
  group_by(commission, category) %>%
  summarise(
    count = n(),
    .groups = 'drop'
  ) %>%
  group_by(commission) %>%
  mutate(
    total = sum(count),
    proportion = count / total
  ) %>%
  ungroup() %>%
  mutate(
    lower_ci = proportion - qt(0.975, total - 1) * sqrt((proportion * (1 - proportion)) / total),
    upper_ci = proportion + qt(0.975, total - 1) * sqrt((proportion * (1 - proportion)) / total)
  )

proportions4$category[proportions4$category == "Moderate Echo Chamber"] <- "Moderate EC"
proportions4$category[proportions4$category == "No Echo Chamber"] <- "No EC"
proportions4$category[proportions4$category == "Extreme Echo Chamber"] <- "Extreme EC"


# Create the plot
h2_5 <- ggplot(proportions4, aes(x = category, y = proportion, fill = category), show.legend = FALSE) +
  geom_bar(stat = "identity", color = "black", width = 0.7, size = 1.5) +
  geom_errorbar(aes(ymin = lower_ci, ymax = upper_ci), width = 0.2, size = 1.5) +
  geom_text(aes(label = count, y = proportion / 2), vjust = 0.5, hjust = 1.1, size = 5) +
  facet_wrap(~ commission, scales = "free") +
  scale_y_continuous(limits = c(0, 1)) +
  labs(
    title = "B: Proportion of Politicians in Each Echo Chamber Category by Institution",
    x = "Echo Chamber Category",
    y = "Proportion of Politicians"
  ) +
  theme_minimal(base_size = 20) +
  theme(
    legend.position = "none"
  )


# Print the plot
print(h2_5)


ggarrange(h2_4,h2_5)





### H3 ###

load("old_df1.RData")
load("old_df2.RData")
load("old_df3.RData")
old_df <- bind_rows(old_df1,old_df2,old_df3)


thin_df <- old_df %>% 
  select(username, created_at, public_metrics.retweet_count, public_metrics.reply_count, public_metrics.like_count, public_metrics.quote_count)

edf$created_at <- as.character(edf$created_at)

edf <- edf %>%
  mutate(created_at = ymd_hms(created_at))   # handles "2021-11-24 11:08:46"

thin_df <- thin_df %>%
  mutate(created_at = ymd_hms(created_at))   # handles ISO 8601 "2021-10-15T10:53:29.000Z"

thin_df <- thin_df %>%
  distinct(username, created_at, .keep_all = TRUE)


merged <- edf %>%
  left_join(thin_df, by = c("username", "created_at"), suffix = c("", "_thin"))


like <- feols(public_metrics.like_count ~ extreme_sentiment | username, 
      data = merged, 
      vcov = "cluster")

like

retweet <- feols(public_metrics.retweet_count ~ extreme_sentiment | username, 
              data = merged, 
              vcov = "cluster")

retweet

quote <- feols(public_metrics.quote_count ~ extreme_sentiment | username, 
              data = merged, 
              vcov = "cluster")

quote

reply <- feols(public_metrics.reply_count ~ extreme_sentiment | username, 
              data = merged, 
              vcov = "cluster")

reply



texreg(list(
  like, 
  retweet, 
  quote, 
  reply
),
custom.model.names = c("Likes", "Retweets", "Quotes", "Replies"),
stars = c(0.01, 0.05, 0.1),  # significance levels
label = "tab:sentiment_engagement",
booktabs = TRUE,   # nicer table formatting
use.packages = FALSE # don't load packages in LaTeX preamble
)






### H4 ###


## Flow Chart ##

## Sankey plot for general Echo Chambers before and after war
edf$gen1 <- "No pre-war EC"
edf$gen1[edf$community_period_1 == 0] <- "Moderate pre-war EC (0.65)"
edf$gen1[edf$community_period_1 == 1] <- "Extreme pre-war EC  (0.89)"

edf$gen2 <- "No post-war EC"
edf$gen2[edf$community_period_2 == 0] <- "Moderate post-war EC (0.60)"
edf$gen2[edf$community_period_2 == 1] <- "Extreme post-war EC (0.92)"


net2 <- edf %>% 
  group_by(name) %>% 
  slice(1)

table(net2$gen1, net2$gen2)

links2 <- data.frame(
  source=c("Moderate pre-war EC (0.65)","Moderate pre-war EC (0.65)", "Moderate pre-war EC (0.65)", "Extreme pre-war EC  (0.89)", "Extreme pre-war EC  (0.89)", "Extreme pre-war EC  (0.89)", "No pre-war EC", "No pre-war EC", "No pre-war EC"), 
  target=c("Moderate post-war EC (0.60)","Extreme post-war EC (0.92)", "No post-war EC", "Moderate post-war EC (0.60)", "Extreme post-war EC (0.92)", "No post-war EC", "Moderate post-war EC (0.60)", "Extreme post-war EC (0.92)", "No post-war EC"), 
  value=c(279,0, 32, 21, 35, 10, 76, 3, 179)
)

nodes2 <- data.frame(
  name=c(as.character(links2$source), 
         as.character(links2$target)) %>% unique()
)

links2$IDsource <- match(links2$source, nodes2$name)-1 
links2$IDtarget <- match(links2$target, nodes2$name)-1

p2 <- sankeyNetwork(
  Links = links2,
  Nodes = nodes2,
  Source = "IDsource",
  Target = "IDtarget",
  Value = "value",
  NodeID = "name",
  sinksRight = FALSE,
  fontSize = 14  # Adjust the font size as needed
)

print(p2)


## same plot with colors ##
# Add a 'group' column to each connection:
links2$group <- as.factor(c("1","1","1","2","2","2","no","no", "no"))

# Add a 'group' column to each node. Here I decide to put all of them in the same group to make them grey
nodes2$group <- as.factor(c("1","2","no", "3", "4", "no"))

# Give a color for each group:
my_color2 <- 'd3.scaleOrdinal() .domain(["1", "2", "no", "3", "4"]) .range(["#69b3a2", "tomato", "grey", "green", "red"])'

# Make the Network
p2c <- sankeyNetwork(Links = links2, 
                     Nodes = nodes2, 
                     Source = "IDsource", 
                     Target = "IDtarget", 
                     Value = "value", 
                     NodeID = "name", 
                     colourScale=my_color2, 
                     LinkGroup="group",
                     sinksRight = FALSE,
                     fontSize = 20)

p2c











# diff in diff


edf$extremely_negative <- 0
edf$extremely_negative[edf$extreme_sentiment == "extremely negative"] <- 1


edf$extremely_positive <- 0
edf$extremely_positive[edf$extreme_sentiment == "extremely positive"] <- 1

edf$date <- as.Date(edf$created_at, format="%Y-%m-%d %H:%M:%S")

edf$date <- as.numeric(edf$date) -19047

edf$after <- NA
edf$after[edf$date > -1] <- 1
edf$after[edf$date < 0] <- 0



didneg <- feols(extremely_negative ~ after * russo_ukraine | username, 
             data = edf, 
             vcov = "cluster")
summary(didneg)



didpos <- feols(extremely_positive ~ after * russo_ukraine | username, 
             data = edf, 
             vcov = "cluster")
summary(didpos)



didcomp <- feols(sentiment_compound ~ after * russo_ukraine | username, 
             data = edf, 
             vcov = "cluster")
summary(didcomp)

texreg(list(didneg, didpos, didcomp),
       file = "did.tex",
       caption = "Regression Results")



## DiD Plot ##


## for extremely negative sentiments ##
means <- edf %>%
  group_by(after, russo_ukraine) %>%
  summarize(
    mean_extremely_negative = mean(extremely_negative, na.rm = TRUE),
    se = sd(extremely_negative, na.rm = TRUE) / sqrt(n()),
    ci_low = mean_extremely_negative - 1.96 * se,
    ci_high = mean_extremely_negative + 1.96 * se
  ) %>%
  ungroup()

means$after[means$after == 1] <- "After Invasion"
means$after[means$after == 0] <- "Before Invasion"

means$after <- factor(means$after, levels = c("Before Invasion", "After Invasion"))



counterfactual_row_1 <- data.frame(
  after = "Before Invasion",
  russo_ukraine = 2,
  mean_extremely_negative = 0.15313036,
  se = NA,
  ci_low = NA,
  ci_high = NA
)

counterfactual_row_2 <- data.frame(
  after = "After Invasion",
  russo_ukraine = 2,
  mean_extremely_negative = 0.15313036 - (0.09716865 - 0.09023352),
  se = NA,
  ci_low = NA,
  ci_high = NA
)

# Combine the original data frame with the new rows
means_extended <- bind_rows(means, counterfactual_row_1, counterfactual_row_2)
means_extended$after <- factor(means_extended$after, levels = c("Before Invasion", "After Invasion"))



# Create the DiD plot with error bars
ggplot(means_extended, aes(x = after, y = mean_extremely_negative, color = factor(russo_ukraine), group = russo_ukraine)) +
  geom_line(size = 3) +
  
  # Draw grey points first (this will be the bottom layer)
  geom_point(data = subset(means_extended, russo_ukraine == 2), size = 8, color = "grey") +
  
  # Draw blue points second (this will be on top of the grey points)
  geom_point(data = subset(means_extended, russo_ukraine == 1), size = 8, color = "blue") +
  
  geom_errorbar(aes(ymin = ci_low, ymax = ci_high), width = 0.05, size = 3) +
  
  scale_color_manual(values = c("red", "blue", "grey"), labels = c("Other Topics", "Russia-Ukraine Topic", "Counterfactual")) +
  labs(
    x = "Time Period",
    y = "Proportion of Tweets with Extremely Negative Sentiment",
    title = "Difference-in-Differences Plot",
    color = "Tweets"
  ) +
  theme_minimal(base_size = 30) +
  
  geom_segment(
    aes(x = "After Invasion", xend = "After Invasion", 
        y = mean_extremely_negative[russo_ukraine == 2 & after == "After Invasion"], 
        yend = mean_extremely_negative[russo_ukraine == 1 & after == "After Invasion"]),
    color = "black",
    linetype = "dashed",
    size = 3
  ) +
  geom_text(aes(label = "ATT", y = 0.17,x = "After Invasion"), vjust = 0.5, hjust = -0.2, size = 8, color = "black")





# triple diff
edf$ec_dummy <- 1
edf$ec_dummy[edf$ec == "No Echo Chamber"] <- 0


tripdifneg <- feols(extremely_negative ~ after * russo_ukraine * ec_dummy| username, 
             data = edf, 
             vcov = "cluster")
summary(tripdifneg)


tripdifpos <- feols(extremely_positive ~ after * russo_ukraine * ec_dummy| username, 
                 data = edf, 
                 vcov = "cluster")
summary(tripdifpos)


tripdifcomp <- feols(sentiment_compound ~ after * russo_ukraine * ec_dummy| username, 
                 data = edf, 
                 vcov = "cluster")
summary(tripdifcomp)



texreg(list(tripdifneg, tripdifpos, tripdifcomp),
       file = "tripdif.tex",
       caption = "Regression Results")

