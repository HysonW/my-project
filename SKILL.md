---
name: orange-data-mining
description: Design, explain, and reproduce Orange3 data-mining workflows — widget choice, preprocessing (Z-score/Min-Max), modeling, evaluation, .ows files, and Orange-style workflow diagrams. Use when a task mentions Orange, .ows, visual data mining, or asks for an Orange canvas image.
whenToUse: The user mentions Orange3 or Orange Canvas, asks for a data-mining workflow or .ows file, needs preprocessing/modeling/evaluation advice in Orange terms, or wants an Orange-style workflow image when the GUI is unavailable.
---

# Orange3 数据挖掘工作流

Orange3 是一个基于 Qt 的可视化数据挖掘工具：在画布上拖入控件（widget），用连线把数据、预处理、模型和可视化串起来。这个 skill 提供控件语义、常用工作流、预处理与评估口径，以及在**没有 Orange GUI** 时生成工作流示意图的可复用脚本。

## 第一原则：区分“设计”与“实际运行”

- 只有真的启动过 Orange、打开过工作流、看到过控件输出，才能写“在 Orange3 中运行/得到结果”。
- 仅根据控件逻辑画出的图，必须称为**工作流示意图**，不能称为“Orange 截图”。
- 没有 GUI 时，不要伪造截图。可以：
  1. 用 `scripts/orange_style_diagram.py` 生成示意图，并在图注写明“示意图”；
  2. 给出可复现的控件与参数步骤，让用户在本地 Orange 中复现；
  3. 请用户提供真实截图后再放入报告。
- 报告措辞建议：
  - 实际运行：`在 Orange3 3.x 中搭建了……工作流，得到……`
  - 仅设计：`按照 Orange3 的工作流逻辑设计了……流程，结构如图 x（示意）`
  - 数据分析由 Python 完成：`数值结果由 pandas/numpy 计算，Orange 工作流用于对照/复现`

## 先判断环境

运行：

```bash
python scripts/check_orange.py
```

输出会说明当前解释器是否安装了 `Orange`、PyQt、是否有可用的图形会话，并探测独立环境（`ORANGE_PYTHON`、`D:\orange` 等）。**Orange 常装在独立 conda 环境里，不要因为 DSH 自带 Python 没有就判断没装。**

如果发现独立环境，用它运行：

```bash
"D:\orange\python.exe" -m Orange.canvas
"D:\orange\python.exe" your_orange_script.py
```

也可以设置环境变量 `ORANGE_PYTHON` 指向该解释器。

安装与启动（Windows / macOS / Linux 桌面）：

```bash
python -m pip install orange3
python -m Orange.canvas
```

也可以在 Windows 上使用 Orange 官方安装包。Orange 依赖 PyQt；**无桌面的服务器无法显示画布，也不能截图**。

## 画布与基本操作

1. 左侧控件树按类别浏览，双击或拖入画布。
2. 控件右侧是输出端口，左侧是输入端口；同类型端口才能连接。
3. 选中控件后，左侧/右侧会显示参数面板；双击控件也可打开设置。
4. 右上角 `File > Save` 保存为 `.ows`；`File > Open` 打开。
5. 控件右上角的小箭头可以打开可视化；`Data Table` 可直接查看数据。

常见控件类别：Data（数据）、Transform（转换）、Visualize（可视化）、Model（模型）、Evaluate（评估）、Unsupervised（无监督）。

## 常用控件速查

完整表见 [references/widgets.md](references/widgets.md)。最常用的组合：

| 目的 | 控件链 |
|---|---|
| 读取 CSV | `File` 或 `CSV File Import` → `Data Table` |
| 选字段 | `File` → `Select Columns` → （后续） |
| 缺失值 | `File` → `Impute` → `Preprocess` |
| 标准化 | `File` → `Select Columns` → `Preprocess`（Normalize） |
| 看分布 | `File` → `Distributions` / `Box Plot` |
| 分类 | `File` → `Test & Score` + `kNN`/`Tree`/`Random Forest` → `Confusion Matrix`/`ROC Analysis` |
| 聚类 | `File` → `Preprocess` → `k-Means` → `Scatter Plot` |
| 降维 | `File` → `Preprocess` → `PCA` → `Scatter Plot` |

## 预处理口径

在 `Preprocess` 控件的 `Normalize` 下拉框中：

- **Standardize (μ=0, σ=1)**：`x′ = (x − μ) / σ`。适合 KNN、K-means、PCA、SVM、线性模型。
- **Scale to [0,1]**：`x′ = (x − min) / (max − min)`。适合神经网络、图像/有界输入。
- **Center**：只减均值，不缩放。
- **Sigmoid**：非线性压缩，较少用。
- 不同 Orange 版本的选项名称可能略有差异，以界面为准。
- 用 Python API 时（Orange 3.40）：Z-Score 用 `Normalize(norm_type=Normalize.NormalizeBySD)`；Min-Max 用 `Normalize(norm_type=Normalize.NormalizeBySpan, zero_based=True)`。`Orange.data.Table("housing")` 可直接加载内置数据。

要点：

- 两种变换都是**线性变换**：不改变分布形状、相对次序和 IQR 异常值，只改变坐标轴。
- Z-Score 的均值/标准差会被极端值拉大，可能产生“掩蔽效应”；Min-Max 对 min/max 敏感，零值会堆积在 0。
- 标准化参数应在**训练集**上估计，再应用到验证/测试集。Orange 的 `Preprocess` 若放在 `Test & Score` 之前，会对全量数据拟合，属于轻微数据泄露；严谨比较时要在每折内拟合，或用 Python/sklearn pipeline 交叉验证。
- 缺失值用 `Impute`（均值/中位数/最频繁值/模型）；类别变量用 `Continuize` 或 `Discretize` 处理。
- 重复记录、类别不平衡、异常值应在建模前单独检查。

## 建模与评估

- `Test & Score`：选择学习器，设置交叉验证折数（常用 5 或 10）和抽样方式；分类任务用分层交叉验证。
- 指标：`CA`（准确率）、`AUC`、`F1`、`Precision`、`Recall`、`MCC`。类别不平衡时不要只看 CA。
- `Confusion Matrix` 看每类错分；`ROC Analysis` 看阈值与 AUC；`Predictions` 看逐条预测。
- 回归：`Linear Regression` / `Random Forest` / `Gradient Boosting` + `Test & Score`（RMSE、MAE、R²）。
- 小样本（如 Boston 506 行）优先用交叉验证，不要只做一次留出法。

## 无监督

- `k-Means`：需要先标准化；`k` 通过肘部法/轮廓系数或业务含义选择。
- `Hierarchical Clustering`、`DBSCAN`：对距离尺度敏感，先标准化。
- `PCA`：先标准化；看解释方差与载荷。
- `Scatter Plot`/`Distributions` 按聚类着色检查结果。

## .ows 文件

`.ows` 是 Orange 的工作流文件（XML），包含控件节点、位置、参数和连线。

- 保存：`File > Save` / `Save As`。
- 打开：`File > Open`；也可把 `.ows` 拖进画布。
- **不要手写复杂的 `.ows`**：不同 Orange 版本 schema 有差异，手写容易打不开。需要模板时，先在 GUI 里搭一个最小工作流并保存，再复制/改参数。
- 迁移工作流时，`File` 控件里的数据路径通常需要重新选择；相对路径更稳。

## 生成 Orange 风格示意图（无 GUI 时）

```bash
python scripts/orange_style_diagram.py assets/housing_normalize.json out.png
```

- 脚本用 PIL 绘制点阵画布、控件卡片、端口、贝塞尔连线和设置说明框，风格接近 Orange Canvas。
- JSON 结构见 `assets/housing_normalize.json`：`widgets` 定义位置/标题/副标题/图标，`links` 用 id 连接。
- 生成的图必须标注为“示意图”，不要冒充截图。
- 如果要真实截图：在装有 Orange 的桌面上打开工作流，用系统截图工具截取画布，再替换报告中的图。

## 常见坑

1. **分隔符/编码**：葡萄酒数据常用 `;` 分隔；CSV 可能是 UTF-8 BOM；读入后先看 `Data Table` 的列名和类型。
2. **ID 列被当成特征**：`Select Columns` 里把 ID/名称设为 meta，不要当特征。
3. **Preprocess 位置**：放在 `Test & Score` 前会全量拟合；严谨评估要在折内拟合。
4. **类别不平衡**：CA 会虚高，改看 F1/AUC/Recall；必要时用权重/重采样。
5. **异常值**：标准化不会消除异常值；IQR 与 |Z|>3 的检出数量可能差很多。
6. **多重共线性**：回归/PCA 前看相关矩阵，必要时删冗余特征。
7. **小样本**：交叉验证折数不要超过最小类别样本数。
8. **版本差异**：控件名称和参数位置会随 Orange 版本变化；写报告时注明版本。

## 交付

- 给出控件链、关键参数、数据文件、评估设置，别人才能复现。
- 图注写清“Orange 工作流示意图”或“Orange 截图”，并注明版本。
- 若数值由 Python 计算、Orange 仅用于流程设计，要在报告中说明，避免“实际运行过 Orange”的误解。
