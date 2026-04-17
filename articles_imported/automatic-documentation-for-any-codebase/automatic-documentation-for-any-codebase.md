## Introduction

When working with R, I loved how **Roxygen** lets you generate clean documentation directly from comments in your source code. But I often wished there was something similar for _every language_, not just R. That’s why I built **[simple\_doc](https://github.com/julienlargetpiet/simple_doc)**: a lightweight documentation tool that works on any codebase.

## The Idea

Instead of maintaining separate README files, wiki pages, or doc websites, you can write structured comments directly in your code. `simple_doc` then parses those comments and generates clean, human-readable documentation automatically.

## How It Works

In your code, you add special annotations (inspired by Roxygen style):

```

// @T dcauchy
// @U std::vector<double> dcauchy(std::vector<double>
// @U &x, double location = 0, double scale = 1)
// @D Returns the probability distribution of the Cauchy distribution.
// @A x : vector of values
// @A location : center of the distribution
// @A scale : scale parameter
// @E Example usage
// @X

```

`simple_doc` reads these annotations and generates documentation with:

- **Function signatures**
- **Parameter descriptions**
- **Examples**
- **Explanations**

It’s language-agnostic: it doesn’t matter if you’re writing in C++, Python, R, or something else — as long as you include the tags, `simple_doc` can parse them.

## Why It’s Useful

- **Universal:** works across programming languages.
- **Lightweight:** no heavy framework, just annotated comments.
- **Automatic:** one command generates docs for your entire project.
- **Close to the code:** documentation stays right where you define functions, so it’s harder to forget updating it.

## Example

After running `simple_doc`, you get nicely structured documentation that could be rendered into HTML. It is worth mentioning that special characters like `<` and `>` must be coded into `&lt;` and `&gt;` for a good conversion.

Example here in the README.md: [https://github.com/julienlargetpiet/fulgurance/](https://github.com/julienlargetpiet/fulgurance/)

Another example, the annotated C++ function above becomes:

```

dcauchy
--------
Usage:
  std::vector<double> dcauchy(std::vector<double> &x,
                              double location = 0,
                              double scale = 1)

Description:
  Returns the probability distribution of the Cauchy distribution.

Arguments:
  x         vector of values
  location  center of the distribution
  scale     scale parameter

Example:
  dcauchy({-2, -1, 0, 1, 2});

```

## Conclusion

With **simple\_doc**, you can generate clear, structured documentation for any codebase without leaving your source files. It’s like Roxygen, but universal. The result: less friction, more consistent docs, and a smoother workflow across all your projects.

👉 Try it out here: [GitHub Repository: simple\_doc](https://github.com/julienlargetpiet/simple_doc)