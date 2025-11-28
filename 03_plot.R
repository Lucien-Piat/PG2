library(ggplot2)

# Load edges
edges <- read.csv("data/cytoscape_edges.csv")

# Count occurrences of each weight
weight_counts <- as.data.frame(table(edges$weight))
colnames(weight_counts) <- c("weight", "count")

# Plot
ggplot(weight_counts, aes(x = weight, y = count)) +
  geom_bar(stat = "identity", fill = "steelblue") +
  geom_text(aes(label = count), vjust = -0.5, size = 3) +
  labs(
    title = "Distribution of Co-authorship Weights",
    x = "Weight (number of shared articles)",
    y = "Count"
  ) +
  theme_minimal() +
  ylim(0, max(weight_counts$count) * 1.1)

# Save plot
ggsave("plot/weight_distribution.png", width = 10, height = 6, dpi = 150)

print("Saved to plot/weight_distribution.png")