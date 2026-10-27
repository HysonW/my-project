# Orange3 控件速查

> 控件名称、端口和参数会随 Orange 版本变化。此表以 Orange 3.3x 的常见布局为基准；实际以界面为准。
> 端口类型相同才能连接；一个输出可以接多个输入，一个输入通常只接一个输出。

## Data（数据）

| 控件 | 作用 | 输入 | 输出 | 关键设置 |
|---|---|---|---|---|
| File | 读取本地数据文件 | — | Data | 文件路径、分隔符、编码、列类型 |
| CSV File Import | 读取 CSV/TSV | — | Data | 分隔符、引号、编码、跳过行 |
| Datasets | 加载内置/在线数据集 | — | Data | 数据集选择 |
| SQL Table | 从数据库取数 | — | Data | 连接、SQL 查询 |
| Paint Data | 手工画点/生成数据 | — | Data | 坐标轴、类别 |
| Data Table | 表格查看/编辑 | Data | Data | 列显示、排序、筛选 |
| Data Info | 数据概况 | Data | — | 行数、列数、类型、缺失 |
| Feature Statistics | 单变量统计 | Data | — | 均值/中位数/分布 |
| Rank | 特征排序 | Data | Data | 信息增益、卡方、ReliefF 等 |
| Save Data | 保存数据 | Data | — | 格式（csv/tab/xlsx） |

## Transform（转换）

| 控件 | 作用 | 输入 | 输出 | 关键设置 |
|---|---|---|---|---|
| Select Columns | 选择特征/目标/meta | Data | Data | 勾选列，设置 target、meta |
| Select Rows | 按条件筛行 | Data | Data | 条件表达式、随机/手动选择 |
| Preprocess | 缺失值、标准化、编码 | Data | Data | Normalize、Impute、Continuize、Discretize |
| Impute | 缺失值填补 | Data | Data | 均值/中位数/众数/模型 |
| Feature Constructor | 构造新特征 | Data | Data | 表达式、聚合 |
| Discretize | 连续变量离散化 | Data | Data | 等宽/等频/熵 |
| Continuize | 类别变量数值化 | Data | Data | 独热/序数 |
| Merge Data | 按列合并 | Data ×2 | Data | 键列、连接方式 |
| Concatenate | 按行拼接 | Data ×2 | Data | 列对齐 |
| Transpose | 转置 | Data | Data | — |
| Edit Domain | 编辑变量元数据 | Data | Data | 名称、类型、角色 |
| Purge Domain | 清理无用变量 | Data | Data | — |
| Apply Domain | 套用已有 domain | Data + Template | Data | — |

## Visualize（可视化）

| 控件 | 作用 | 输入 | 输出 | 关键设置 |
|---|---|---|---|---|
| Distributions | 直方图/分布 | Data | Selected Data | 变量、分箱、按类别着色 |
| Box Plot | 箱线图 | Data | Selected Data | 变量、分组、须长度 |
| Violin Plot | 小提琴图 | Data | Selected Data | 变量、分组 |
| Scatter Plot | 散点图 | Data | Selected Data | x/y、颜色、大小、抖动 |
| Line Plot | 折线图 | Data | Selected Data | x/y、分组 |
| Bar Plot | 柱状图 | Data | Selected Data | 变量、聚合方式 |
| Heat Map | 热力图 | Data | Selected Data | 行/列、聚类、颜色 |
| Mosaic Display | 马赛克图 | Data | Selected Data | 两个类别变量 |
| Sieve Diagram | 筛图 | Data | Selected Data | 类别变量 |
| Tree Viewer | 决策树查看 | Tree | — | 树结构、样本路径 |
| CN2 Rule Viewer | 规则查看 | CN2 | — | 规则列表 |

## Model（模型）

| 控件 | 作用 | 输入 | 输出 | 关键设置 |
|---|---|---|---|---|
| kNN | k 近邻 | Data | Model | k、距离度量、权重 |
| Tree | 决策树 | Data | Model | 最大深度、最小叶样本、剪枝 |
| Random Forest | 随机森林 | Data | Model | 树数、最大深度、特征采样 |
| Logistic Regression | 逻辑回归 | Data | Model | 正则化、迭代 |
| Naive Bayes | 朴素贝叶斯 | Data | Model | 平滑 |
| SVM | 支持向量机 | Data | Model | 核、C、gamma |
| Neural Network | 多层感知机 | Data | Model | 隐藏层、激活、迭代、正则 |
| Gradient Boosting | 梯度提升 | Data | Model | 学习率、树数、深度 |
| Linear Regression | 线性回归 | Data | Model | 正则化 |
| AdaBoost | 提升 | Data | Model | 基学习器、轮数 |
| Constant | 常数基线 | Data | Model | 分类/回归 |

## Evaluate（评估）

| 控件 | 作用 | 输入 | 输出 | 关键设置 |
|---|---|---|---|---|
| Test & Score | 交叉验证/留出评估 | Data + Model | Test Results | 折数、抽样、指标 |
| Confusion Matrix | 混淆矩阵 | Test Results / Data | — | 阈值、类别 |
| ROC Analysis | ROC/AUC | Test Results | — | 正类、阈值 |
| Calibration Plot | 概率校准 | Test Results | — | 可靠性曲线 |
| Lift Curve | 提升曲线 | Test Results | — | 正类 |
| Predictions | 逐条预测 | Data + Model | Data | 预测列、概率列 |

## Unsupervised（无监督）

| 控件 | 作用 | 输入 | 输出 | 关键设置 |
|---|---|---|---|---|
| k-Means | K 均值聚类 | Data | Data + Centroids | k、初始化、迭代 |
| Hierarchical Clustering | 层次聚类 | Data / Distances | Data | 距离、连接方式、阈值 |
| DBSCAN | 密度聚类 | Data | Data | eps、min_samples |
| Mean Shift | 均值漂移 | Data | Data | 带宽 |
| PCA | 主成分分析 | Data | Data | 成分数、标准化 |
| t-SNE | 非线性降维 | Data / Distances | Data | 困惑度、迭代、perplexity |
| MDS | 多维缩放 | Distances | Data | 距离、维度 |
| Distances | 距离矩阵 | Data | Distances | 距离度量 |
| Distance Map | 距离可视化 | Distances | — | — |

## 文本/图像/地理（add-on）

| 控件 | 作用 | 说明 |
|---|---|---|
| Corpus | 读取文本 | Text add-on |
| Preprocess Text | 分词、去停用词、词干化 | Text add-on |
| Bag of Words | 词袋/TF-IDF | Text add-on |
| Topic Modelling | LDA 等主题模型 | Text add-on |
| Sentiment Analysis | 情感分析 | Text add-on |
| Image Embedding / Image Grid | 图像特征/浏览 | Image Analytics add-on |
| Geo Map / Geocoding | 地理可视化/编码 | Geo add-on |
| As Timeseries / Moving Transform | 时间序列 | Timeseries add-on |

## 端口与常见连线错误

- `File` 输出 Data；`Data Table` 输入 Data。想先看数据就接 `Data Table`。
- `Test & Score` 需要 Data 和 Model 两个输入；只接 Data 不会出结果。
- `Confusion Matrix`/`ROC Analysis` 接 `Test & Score` 的 Test Results，不是直接接 Data。
- `Predictions` 需要 Data + Model。
- `Preprocess` 输出仍是 Data；`Select Columns` 也输出 Data。
- 聚类/降维前通常先 `Preprocess` 标准化，否则量纲大的变量会主导距离。
