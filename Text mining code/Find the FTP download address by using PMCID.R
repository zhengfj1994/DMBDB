library(openxlsx)
oa_file_list <- read.csv(file = "")

pmc_result_su <- read.xlsx("D:/Desktop/zwj/pmcid.xlsx")

pmc_result_su$V5 <- NA
for (i in c(1:nrow(pmc_result_su))){
  print(i)
  posi <- which(oa_file_list$Accession.ID == pmc_result_su$PMCID[i])
  pmc_result_su$V5[i] <- paste0("https://ftp.ncbi.nlm.nih.gov/pub/pmc/", oa_file_list$File[posi])
}

write.xlsx(pmc_result_su, "D:/Desktop/zwj/pmc_result.xlsx")


