## Introduction

When working with data, Python and Pandas dominate the landscape. They provide an intuitive way to load, transform, and analyze datasets. But what if you need the same capabilities **inside a C++ pipeline**, without switching languages, and with full control over memory and type safety?

That’s the motivation behind **Tablo**, my implementation of DataFrames in modern C++. This project provides a flexible and performant way to manipulate tabular data directly in C++ — including CSV parsing, type inference, missing value handling, and column/row operations.

In this article, I’ll walk you through the **architecture**, **features**, and **next steps** of this implementation.

## Architecture Overview

The core idea of this project is simple:

- Each **column** of the DataFrame is stored as a `std::vector<T>`, where `T` is the inferred type of the column.
- Types are detected through **semantic analysis** when reading a CSV file. Supported types include:

  - `std::string`
  - `char`
  - `bool`
  - `int`
  - `unsigned int`
  - `double`

This allows the system to optimize storage and operations based on the actual data instead of storing everything as strings.

### Handling Missing Data (N/A)

Missing values are a common issue when dealing with real-world datasets. In this implementation:

- `N/A` is recognized during parsing.
- Missing entries are properly represented within their respective typed vectors, ensuring consistency and safety.

## Core Features

### 1\. Reading CSV Files with Type Inference

The library reads CSV files and builds a DataFrame where each column is typed according to its content. For example:

```cpp

    Tablo df("dataset.csv");

```

Here, each column will be imported into a typed

`std::vector<T>`.

### 2\. Writing DataFrames Back to CSV

DataFrames can be exported back into a CSV file, with customizable column delimiters:

```cpp

    df.to_csv("output.csv", ';');

```

This makes it easy to integrate with external tools while preserving type safety inside your C++ code.

### 3\. Selecting and Copying Rows/Columns

You can create a new DataFrame by selecting a subset of rows and columns from an existing one:

```cpp


  Tablo subset = df.copy({0, 2, 4}, {"Name", "Age"});


```

This produces a new DataFrame with only the chosen rows and columns.

### 4\. Extracting Columns as Typed Vectors

A column can be retrieved directly as a typed vector:

```cpp


  std::vector<int> ages = df.get_column<int>("Age");


```

This is extremely useful when you want to process the data using C++ algorithms or numerical libraries.

### 5\. Extracting Multiple Columns

You can also extract multiple columns at once as a vector of vectors:

```cpp


  auto selected = df.get_columns<int>({"Height", "Weight"});


```

This provides direct typed access to the data without conversions.

## Roadmap: Implementing Joins

The next big step for this project is **implementing joins** — allowing DataFrames to be merged based on keys, similar to SQL or Pandas. This will open the door to more advanced relational data operations directly in C++.

## Why C++ DataFrames?

You might ask: _Why not just use Python and Pandas?_

The answer lies in **performance and integration**.

- When working in a C++ codebase (e.g., simulation, high-performance computing, embedded analytics), switching to Python introduces overhead.
- With a native C++ DataFrame, you can:
  - Avoid unnecessary data conversions.
  - Benefit from strong typing and compile-time checks.
  - Leverage modern C++ features for performance.

This makes the library a good fit for projects where **speed and memory control matter**, but you still want the convenience of high-level tabular abstractions.

## Conclusion

With Tablo, I set out to bring the flexibility of Pandas-style DataFrames into the world of C++.

So far, the implementation supports:

- Reading CSVs with automatic type inference
- Handling missing values
- Writing to CSV with custom delimiters
- Copying subsets of rows and columns
- Extracting columns or sets of columns as typed vectors

The next milestone is implementing **joins**, which will significantly expand its capabilities.

If you’re interested, you can explore the full project here:

👉 [GitHub Repository: Tablo](https://github.com/julienlargetpiet/tablo)