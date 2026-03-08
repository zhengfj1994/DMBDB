library(treeio)
library(ggplot2)
library(ggtree)


rawData <- read.csv(file = "")
n <- rawData[, c(3,1)]
n[,1] <- as.character(n[,1])
n[,1] <- gsub("\\s\\(.*\\)", "", n[,1])

w <- cbind("World", as.character(unique(n[,1])))

colnames(w) <- colnames(n)
edgelist <- unique(rbind(n, w))

y <- ape::as.phylo(igraph::graph_from_data_frame(edgelist))

# -- Build complete data for drawing and ensure that the intermediate connections have color --
# 1. Tips Data: The superclass must be cleaned in the same way to ensure consistent color mapping
plot_data <- rawData
plot_data$superclass <- as.character(plot_data$superclass)
plot_data$superclass <- gsub("\\s\\(.*\\)", "", plot_data$superclass)
plot_data$id <- as.character(plot_data$id) # 确保 id 为字符型

# 2. Intermediate Node data (Superclass): Let them also have the superclass attribute so that the connection will have color
# The node name is the name of the superclass after cleaning
internal_nodes <- unique(plot_data$superclass)
internal_data <- data.frame(
  id = internal_nodes,
  class = internal_nodes,     
  superclass = internal_nodes, 
  number = NA                  
)

# 3. Root Node data
# Key Modification: Set class and superclass to NA to prevent "World" from appearing in tags or legends
root_data <- data.frame(id = "World", class = NA, superclass = NA, number = NA)

# 4. Merge
# Only merge the common columns
common_cols <- c("id", "class", "superclass", "number")
final_data <- rbind(plot_data[, common_cols], internal_data[, common_cols], root_data[, common_cols])

p <- ggtree(y, layout='circular', branch.length='none') %<+% final_data +
  geom_tree(aes(color=superclass), size=0.6) +
  geom_tippoint(aes(size=number, color=superclass), alpha=.7) + 
  geom_tiplab(aes(label=class, color=superclass), offset=0.2, size = 3.5, align = TRUE, linesize = 0.3) +
  guides(
    size = guide_legend(order = 1),
   
    color = guide_legend(order = 2, override.aes = list(label = "", size = 3, linewidth = 1))  
  ) +
  scale_color_discrete(na.translate = FALSE) +

  scale_size_continuous(range = c(2, 7)) +
  theme(legend.text = element_text(size = 15), 
        legend.title = element_text(size = 18, face = "bold"), 
        legend.key.size = unit(0.45, "cm"), 
        legend.key.height = unit(0.8, "cm"),
        legend.spacing.y = unit(0.3, "cm"),
        legend.box.spacing = unit(2, "cm"), 
        legend.position = "right",
        plot.margin=margin(45,5,-10,60)) + 
  xlim(-1.5, 3.3)

ggsave("treeplot.png", p, width = 16.2, height = 10, dpi = 600)