# 常用 Orange3 工作流配方

> 每条配方都给出控件链、关键参数和结果检查点。先保证 `Data Table` 里的列类型正确，再往下接。

## 1. 连续属性标准化对比（Z-Score vs Min-Max）

**场景**：比较原始值、Z-Score、[0,1] 归一化在分布和异常值上的差异。

**控件链**

```text
File ── Select Columns ── Preprocess (Standardize) ── Box Plot
   │           │
   │           └─────── Preprocess (Scale to [0,1]) ── Distributions
   │
   └── Data Table
```

**参数**

- `File`：housing.csv，第一行为列名。
- `Select Columns`：只保留连续属性；ID/名称设为 meta。二值变量（如 CHAS）和序号变量（如 RAD）是否纳入要说明。
- `Preprocess`：`Normalize` 选 `Standardize (μ=0, σ=1)`；另一条选 `Scale to [0,1]`。
- `Box Plot`：变量选 1 个或多个；看须外红点。
- `Distributions`：变量选 1—2 个；分箱 20—30。

**检查点**

- 三种表示的直方图轮廓应一致，仅横轴刻度不同。
- 偏度、相关系数不变（线性变换）。
- IQR 异常值数量应一致；`|Z|>3` 数量可能更少（均值/标准差被极端值拉大）。
- Min-Max 后零值会堆在 0，极值会把其余样本压到很窄区间。

**报告措辞**

> 在 Orange3 的 Preprocess 控件中分别选择 Standardize 与 Scale to [0,1]，用 Box Plot/Distributions 对照。数值统计另用 Python 计算，结果一致。

## 2. 二分类与模型比较（葡萄酒）

**场景**：用葡萄酒理化指标预测红/白（Wine_Type），比较 kNN、树、随机森林。

**控件链**

```text
File ── Select Columns ── Preprocess ── Test & Score ── Confusion Matrix
                                      │                └─ ROC Analysis
                                      ├─ kNN
                                      ├─ Tree
                                      └─ Random Forest
```

**参数**

- `Select Columns`：`Wine_Type` 设为 target；其余理化指标为 features。
- `Preprocess`：`Impute` 处理缺失（若有）；标准化对 kNN/SVM 必要，对树模型可不做。
- `Test & Score`：交叉验证 5 或 10 折；分类任务用分层抽样；指标勾选 CA、AUC、F1、Precision、Recall。
- `Confusion Matrix`：看少数类（红葡萄酒）的召回与误判。
- `ROC Analysis`：看 AUC 与阈值。

**检查点**

- 类别不平衡（白约 75%、红约 25%）时，CA 会偏高；重点看 F1/AUC/Recall。
- 树模型不需要标准化；kNN/SVM 需要。
- 标准化若放在 `Test & Score` 前，会对全量数据拟合，属于轻微泄漏；严谨比较要折内拟合。

**报告措辞**

> 以 Wine_Type 为目标，在 Test & Score 中做 10 折分层交叉验证，比较 kNN、Tree、Random Forest 的 CA/AUC/F1。

## 3. 回归（波士顿房价）

**场景**：用 12 个连续属性预测 MEDV。

**控件链**

```text
File ── Select Columns ── Preprocess ── Test & Score ── Predictions
                                      ├─ Linear Regression
                                      └─ Random Forest
```

**参数**

- `Select Columns`：MEDV 设为 target；其余为 features；CHAS/RAD 视作类别/序号要说明。
- `Preprocess`：`Impute`（若有缺失）；标准化对线性回归/正则化有用，对树模型不必。
- `Test & Score`：10 折交叉验证；指标 RMSE、MAE、R²。
- `Predictions`：看预测值 vs 实际值；注意 MEDV 在 50 处截断。

**检查点**

- 目标变量右偏/截断会影响残差；可对 MEDV 做变换后对比。
- 多重共线性：TAX 与 RAD、NOX 与 INDUS 等相关较高。
- 小样本（506 行）不要只做一次留出法。

## 4. 聚类与降维（k-Means + PCA）

**场景**：无标签数据的群体划分与可视化。

**控件链**

```text
File ── Select Columns ── Preprocess ── k-Means ── Scatter Plot
                                      └─ PCA ────── Scatter Plot
```

**参数**

- `Preprocess`：必须标准化（Z-Score），否则量纲大的变量主导距离。
- `k-Means`：k 从 2 开始试；看肘部/轮廓/业务解释；固定随机种子便于复现。
- `PCA`：成分数 2—3；看解释方差。
- `Scatter Plot`：x/y 选 PCA 成分或原始变量；颜色选聚类标签。

**检查点**

- 聚类结果对标准化、k、初始化敏感；报告要写清。
- PCA 前必须标准化；载荷用于解释成分。
- 不要用聚类标签反推因果。

## 5. 缺失值与特征工程

**场景**：数据有缺失/类别变量/需要构造比率特征。

**控件链**

```text
File ── Impute ── Preprocess ── Feature Constructor ── Test & Score
```

**参数**

- `Impute`：数值用均值/中位数；类别用众数；缺失比例高（>40%）考虑删列。
- `Preprocess`：`Continuize` 处理类别变量（独热/序数）；`Discretize` 按需离散化。
- `Feature Constructor`：构造比率、差值、聚合特征；避免使用目标变量派生特征（泄漏）。

**检查点**

- 缺失是否随机（MCAR/MAR/MNAR）影响填补策略。
- 独热编码后维度膨胀；树模型可接受序数编码。
- 新特征必须在训练/测试划分内一致计算。

## 6. 文本分类（可选，Text add-on）

```text
Corpus ── Preprocess Text ── Bag of Words ── Test & Score ── Confusion Matrix
```

- `Preprocess Text`：分词、小写、去停用词、词干化。
- `Bag of Words`：TF-IDF 或计数；控制最小词频/最大词数。
- `Test & Score`：分层交叉验证；文本特征高维，注意过拟合。

## 通用检查清单

- [ ] `Data Table` 列类型正确（数值/类别/文本/meta）。
- [ ] target 设置正确，ID 不在特征里。
- [ ] 缺失值已处理或明确保留。
- [ ] 标准化只在需要时做，且注意拟合范围。
- [ ] 交叉验证折数合理，分类用分层。
- [ ] 指标与任务匹配（分类看 F1/AUC，回归看 RMSE/MAE/R²）。
- [ ] 图注写明“Orange 截图”还是“工作流示意图”。
