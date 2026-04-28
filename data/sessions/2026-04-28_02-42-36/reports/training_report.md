# Training Report — Sentiment Classification

## Dataset
- **File:** clean.csv (20,000 rows × 6 columns)
- **Target:** `Positive` (binary: 0=Negative, 1=Positive)
- **Class imbalance:** 76.2% Positive (3.2:1 ratio)
- **Split:** 80% train (16,000) / 20% test (4,000), stratified

## Feature Engineering
- **TF-IDF:** `clean_reviewText`, max_features=10,000, ngram_range=(1,2), sublinear_tf=True, min_df=5
- **Meta features:** `review_length`, `word_count`, `exclamation_count` (StandardScaler)
- **Combined matrix:** TF-IDF + scaled meta → 10,003 features

## Models Compared

| Model                        | CV AUC | Test F1 | Test AUC | Test Acc |
|------------------------------|--------|---------|----------|----------|
| LogisticRegression (C=5.0)   | 0.9609 | 0.9486  | 0.9646   | 0.9203   |
| MultinomialNB (alpha=0.5)    | 0.9602 | 0.9406  | 0.9627   | 0.9065   |

## Hyperparameter Tuning
- **Method:** GridSearchCV, 3-fold StratifiedKFold, scoring=roc_auc
- **LR grid:** C ∈ {0.1, 0.5, 1.0, 5.0, 10.0} × class_weight ∈ {balanced, None}
- **Best params:** C=5.0, class_weight=None, penalty=l2, solver=liblinear
- **NB grid:** alpha ∈ {0.01, 0.05, 0.1, 0.5, 1.0} → best alpha=0.5

## Final Model: LogisticRegression
- **Accuracy:**  0.9203
- **F1 (pos):**  0.9486
- **Precision:** 0.9314
- **Recall:**    0.9665
- **ROC-AUC:**   0.9646

## Class Imbalance Handling
- Evaluated both `class_weight='balanced'` and `None`; tuning showed `None` performed better
  (TF-IDF features already provide sufficient signal for the minority class)
- Reported F1 and ROC-AUC as primary metrics (not just accuracy)

## Saved Artifact
- **Path:** models/model.pkl
- **Contents:** {model, tfidf, scaler, feature_names, target, best_params}
