# IV. Performance Evaluation & Experimental Results

---

## A. Experimental Setup & Evaluation Methodology

To rigorously validate the proposed multi-modal agricultural decision support framework, we constructed an automated, parallelized quantitative evaluation pipeline comprising **200 standardized benchmark test cases** divided equally into two core domain evaluations:

1. **Crop Yield & Economic Forecasting ($N = 100$ Cases)**: Assesses the accuracy of estimated harvest tonnage per acre, financial cost-benefit projections, and localized currency market alignment across diverse geographical regions (India, USA, Brazil, UK, Nigeria, Ghana, Malaysia) and farm scales (3 to 15 acres). Ground truth data was curated from official national agricultural statistics, including USDA NASS, India Ministry of Agriculture (2023–24), CONAB Brazil, and UK DEFRA.
2. **Plant Pathologist Disease Diagnosis ($N = 100$ Cases)**: Evaluates diagnostic precision, severity classification, pathogen attribution, and treatment recommendations across 35+ crop species and 6 major pathogen categories (Fungal Blight, Rusts & Mildews, Wilts & Vascular Rots, Smut & Galls, Bacterial Infections, and Viral/Vector Diseases).

All experiments were executed using Google's **`gemma-4-26b-a4b-it`** generative reasoning model interfaced with an Express.js backend and benchmarked against deterministic mathematical baseline calculations.

---

## B. Crop Yield & Financial Forecasting Evaluation

### 1) Agronomic Scaling Invariance
A critical agronomic principle enforced during evaluation is that **yield per acre is an intrinsic property** of the crop, soil, and microclimate combination, and must remain invariant regardless of total farm size. As shown in **Table I**, the model demonstrated linear scaling behavior: total estimated yield scaled precisely as:

$$\text{Total Estimated Yield (Tons)} = \text{Yield per Acre (Tons/Ac)} \times \text{Farm Size (Acres)}$$

```
+---------------------------------------------------------------------------------------------+
|                                           TABLE I                                           |
|                     REPRESENTATIVE CROP YIELD EVALUATION BENCHMARKS                         |
+-------------+---------------+----------+------------------+---------------+-----------------+
| Crop        | Region        | Size(Ac) | Predicted (T/Ac) | Actual (T/Ac) | Accuracy (%)    |
+-------------+---------------+----------+------------------+---------------+-----------------+
| Wheat       | Punjab, IN    |    5     |      2.04        |     2.00      |     98.0%       |
| Wheat       | Haryana, IN   |    9     |      1.92        |     1.90      |     98.9%       |
| Corn        | Iowa, US      |   10     |      4.76        |     4.80      |     99.2%       |
| Sugarcane   | Maharashtra   |   15     |     32.40        |    33.00      |     98.2%       |
| Rice        | W. Bengal, IN |    5     |      1.22        |     1.25      |     97.6%       |
| Soybeans    | Illinois, US  |    6     |      1.58        |     1.60      |     98.75%      |
| Potato      | Idaho, US     |    9     |     17.65        |    18.00      |     98.06%      |
+-------------+---------------+----------+------------------+---------------+-----------------+
```

### 2) Quantitative Accuracy Metrics
Across all $N = 100$ evaluation cases, the yield forecasting engine achieved:
* **Mean Absolute Error (MAE)**: $0.082 \text{ Tons/Acre}$
* **Average Model Yield Accuracy**: **$94.38\%$**
* **Local Currency Alignment**: $100\%$ compliance with regional currency units (e.g., INR ₹ for Indian mandis, USD $ for US commodities, BRL R$ for Brazilian markets) accompanied by explicit authority price citations.

---

## C. Plant Pathologist Disease Diagnostic Evaluation

### 1) Diagnostic Match Classification
Diagnostic predictions were classified into three match tiers:
* **Exact Match**: Full alignment with expected pathogen and clinical disease name.
* **Partial Match**: High-level genus/family match or acceptable clinical keyword resolution.
* **Mismatch**: Incorrect pathogen or physiological classification.

```
+---------------------------------------------------------------------------------------------+
|                                           TABLE II                                          |
|                     DIAGNOSTIC PERFORMANCE METRICS OVER 100 BENCHMARKS                      |
+------------------------------------+--------------------------+-----------------------------+
| Metric Category                    | Evaluation Value         | Percentage / Score          |
+------------------------------------+--------------------------+-----------------------------+
| Total Diagnostic Benchmark Cases   | N = 100                  | 100.0%                      |
| Exact Disease Matches              | 87 Cases                 | 87.0%                       |
| Partial Matches                    | 10 Cases                 | 10.0%                       |
| Mismatches                         | 3 Cases                  | 3.0%                        |
| Overall Advisory Accuracy Rate     | Exact + Partial          | 97.0%                       |
| Mean Model Confidence Score        | -                        | 0.96 / 1.00                 |
+------------------------------------+--------------------------+-----------------------------+
```

### 2) Confusion Matrix Analysis
As illustrated in the Confusion Matrix (**Figure 4**), performance across pathogen classes demonstrated high precision:
* **Fungal Blights & Mildews**: $94\%$ classification precision ($F_1\text{-score} = 0.95$).
* **Vascular Wilts & Rots**: $91\%$ precision ($F_1\text{-score} = 0.92$).
* **Bacterial Pathogens**: $88\%$ precision ($F_1\text{-score} = 0.89$).
* **Viral & Vector Diseases**: $95\%$ precision ($F_1\text{-score} = 0.96$).

The mean model confidence score across all diagnoses was calibrated at $\mu = 0.96$, showing strong correlation with empirical ground-truth accuracy.

---

## D. Deterministic Baseline Validation & System Resilience

### 1) Mathematical Bound Verification
The deterministic Python baseline model validates AI care predictions using temperature adjustment scaling:

$$\text{Adjusted Water} = \text{Base Water} + \left( (T_{\text{current}} - T_{\text{optimal\_max}}) \times \alpha_{\text{water}} \right)$$

$$\text{Adjusted N-P-K-Ca} = \text{Base Nutrition} + \left( (T_{\text{current}} - T_{\text{optimal\_max}}) \times \beta_{\text{nutrient}} \right)$$

Experimental testing confirmed $100\%$ of AI-generated daily water and N-P-K-Ca recommendations remained strictly bounded within $\pm 4.2\%$ of this mathematical formula, preventing dangerous over-irrigation or fertilizer toxicity recommendations under extreme heat conditions.

### 2) JSON Pipeline Resilience
Under Gemma-4's native "thinking mode", reasoning tokens precede the structured output. The custom `extractJSON` utility achieved a **$100\%$ structural parsing success rate** across all 200 automated benchmark queries, with zero JSON syntax errors or UI rendering crashes.
