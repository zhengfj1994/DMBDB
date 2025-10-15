library(MetNormalizer)

new.path <- "D:/Desktop/normalization"

# 一键运行 metNor
metNor(
  ms1.data.name = "data.csv",          # 代谢物数据表名
  sample.info.name = "sample.info.csv",# 样本信息表名
  minfrac.qc = 0,                      # QC 保留阈值
  minfrac.sample = 0,                  # 样本保留阈值
  optimization = TRUE,                 # 是否优化校正参数
  multiple = 5,                        # 优化倍数
  threads = 4,                         # 并行线程
  path = new.path                      # 路径
)
