library(treeio)
library(ggplot2)
library(ggtree)

rawData <- read.csv(file = "")
n <- rawData[, c(3,1)]
n[,1] <- as.character(n[,1])
n[,1] <- gsub("\\s\\(.*\\)", "", n[,1])

w <- cbind("World", as.character(unique(n[,1])))

colnames(w) <- colnames(n)
edgelist <- rbind(n, w)

y <- as.phylo(edgelist)
ggtree(y, layout='circular') %<+% rawData +
  aes(color=superclass) + 
  geom_tippoint(aes(size=number), alpha=.6) + 
  geom_tiplab(aes(label=class), offset=.1, size = 3,) +
  guides(
    color = guide_legend(override.aes = list(label = ""))  
  ) +
  scale_color_discrete(na.translate = FALSE) +
  theme(legend.text = element_text(size =10),
        legend.title = element_text(size = 12, face = "bold"),
        legend.key.size = unit(0.5, "cm"),
        legend.box.spacing = unit(3, "cm"),
        legend.position = "right",
        plot.margin=margin(100,80,80,80))