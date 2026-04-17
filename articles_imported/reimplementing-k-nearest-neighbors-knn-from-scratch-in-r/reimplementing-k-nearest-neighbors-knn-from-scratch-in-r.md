As part of my exploration of machine learning fundamentals, I decided to reimplement classic algorithms from scratch instead of relying directly on existing libraries. One of the first I tackled was **K-Nearest Neighbors (KNN)**, a simple yet powerful classification method.

## Why KNN?

KNN is often one of the first algorithms taught in machine learning because it’s intuitive:

- To classify a new point, look at the `k` closest points in your training data.
- Assign the most common class among those neighbors.

No training phase, no model building — just distance comparisons. This makes it perfect for reimplementing from scratch.

## The Implementation

I called my implementation `knn_Rmach`. It works with R data frames, allowing you to specify which columns are variables and which is the classification column. It also supports both numeric indices and column names.

```r

knn_Rmach(train, test, k,
          col_vars_train = c(),
          col_vars_test = c(),
          class_col)

```

### Key Features

- **Flexible column selection:** you can pass either column numbers or names.
- **Distance calculation:** uses a simple Manhattan-like distance (sum of absolute differences).
- **Voting system:** after finding the `k` nearest neighbors, the most frequent class is chosen.
- **Mode helper:** a small utility function `see_mode` ensures ties are handled by picking the most common label.

## Example with Iris Dataset

To test the algorithm, I used the classic `iris` dataset. I held out 45 random points for testing and trained on the rest. With `k = 3`, the classifier achieved about **95.5% accuracy**.

```r

cur_ids <- round(runif(n = 45, min = 1, max = 150))

vec <- knn_Rmach(train = iris[-cur_ids,],
                 test = iris[cur_ids, 1:4],
                 col_vars_train = c(1:4),
                 col_vars_test = c(1:4),
                 class_col = 5,
                 k = 3)

sum(vec == iris[cur_ids, 5]) / 45
# [1] 0.9555556

```

This shows that even a simple, hand-written version of KNN can classify the Iris flowers with strong accuracy.

## Limitations & Next Steps

- **Distance metric:** I used absolute differences; Euclidean distance or other metrics could improve results in some contexts.
- **Scalability:** KNN is slow for large datasets, since every test point compares against all training points. Indexing structures (KD-trees, ball trees) could speed it up.
- **Tie-breaking:** my mode function is simple; other tie-handling strategies could be explored.

## Conclusion

Reimplementing KNN from scratch in R was a rewarding exercise. It reinforced how the algorithm works under the hood and demonstrated that with just a few dozen lines of code, you can build a functional classifier. It also opens the door to extending or experimenting with KNN in ways that black-box libraries don’t allow.

## Source

The repo is available here: [https://github.com/julienlargetpiet/Rmach](https://github.com/julienlargetpiet/Rmach)