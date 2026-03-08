library(MetNormalizer)

new.path <- ""


metNor(
  ms1.data.name = "data.csv",          # Metabolite data Table name
  sample.info.name = "sample.info.csv",# Sample Information Table Name
  minfrac.qc = 0,                      # QC Retention threshold
  minfrac.sample = 0,                  # Sample Retention threshold
  optimization = TRUE,                 # Whether to optimize the correction parameters
  multiple = 5,                        # Optimize Multiples
  threads = 4,                         # Parallel Threads
  path = new.path                      # Path
)
