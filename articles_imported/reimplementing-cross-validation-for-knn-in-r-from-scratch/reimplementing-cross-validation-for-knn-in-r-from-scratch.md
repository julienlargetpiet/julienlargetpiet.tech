## Introduction

After reimplementing **K-Nearest Neighbors (KNN)** from scratch, I wanted to take things a step further: build a **cross-validation system** entirely in base R. This meant re-creating folds, evaluating accuracy across them, and tuning both `k` (the number of neighbors) and the training proportion. No caret, no external frameworks — just my own code.

## The Fold Function

The first step in cross-validation is creating training/test splits. For this, I wrote `v_Rmach_fold`, which generates `n_fold` pairs of train/test datasets. Each sample is stored in a small S4 class `sample_Rmach` with:

- `train`: the training dataframe
- `test`: the testing dataframe
- `train_ids`: row indices used for training
- `test_ids`: row indices used for testing

```r

lst_test <- v_Rmach_fold(inpt_datf = iris[1:25,],
                         train_prop = 0.7,
                         n_fold = 4)

print(lst_test$sample1@train)  # Training set
print(lst_test$sample1@test)   # Test set

```

This function essentially recreates what libraries like caret do internally, but in a transparent and lightweight way.

## Cross-Validation Over k

With `knn_Rmach_cross_validation_k`, I can test multiple values of `k` (neighbors) across multiple folds, returning the mean accuracy for each candidate value. Example:

```r

iris[, 5] <- as.character(iris[, 5])
print(knn_Rmach_cross_validation_k(
        inpt_datf = iris,
        col_vars = c(1:4),
        n_fold = 5,
        knn_v = c(3, 5, 7, 9, 11),
        class_col = 5,
        train_prop = 0.7
))
# [1] 0.9333333 0.9200000 0.9333333 0.9466667 0.9288889
# Optimal k = 9

```

Here, `k=9` gave the best cross-validated accuracy (~94.7%).

## Cross-Validation Over Training Proportions

I also implemented `knn_Rmach_cross_validation_train`, which instead of tuning `k` tunes the **training proportion**. This answers: _how much data should I use for training vs testing to maximize accuracy?_

```r

iris[, 5] <- as.character(iris[, 5])
print(knn_Rmach_cross_validation_train(
        inpt_datf = iris,
        col_vars = c(1:4),
        n_fold = 15,
        k = 7,
        class_col = 5,
        train_prop_v = c(0.7, 0.75, 0.8)
))
# [1] 0.4057143 0.3273810 0.2400000
# Optimal training proportion = 0.7

```

In this run, using 70% of the data for training gave the best results.

## What I Learned

- **Cross-validation isn’t magic:** it’s just repeated sampling and evaluation.
- **Flexibility:** writing my own folds gave me control over how training/testing is sampled.
- **Practical trade-offs:** increasing `n_fold` improves accuracy estimates but at the cost of execution time.

## Conclusion

By writing my own fold generator and cross-validation functions, I rebuilt the skeleton of what machine learning frameworks provide. It’s slower than optimized libraries, but it gave me a much deeper understanding of how cross-validation really works under the hood — and it integrates seamlessly with my home-grown `knn_Rmach` implementation.

## Source

repo: [https://github.com/julienlargetpiet/Rmach](https://github.com/julienlargetpiet/Rmach)

or here as a zip: [Rmach](/assets/common_files/Rmach.zip)