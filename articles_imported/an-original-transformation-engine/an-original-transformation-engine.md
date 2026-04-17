# Introduction

In this article i will introduce you, in short, how i've implemented transformation engine XSLT like from scratch (with C++).

[repo](https://github.com/julienlargetpiet/Moutarde)


Or download on this website:

[zip](/assets/common_files/Moutarde.zip)

Which means requesting a value using its path in the data structure, the introduction of conditions, loops and sorting algorithms to generate a html page that the user describes inside a file with query instructions.

Since i start from scratch, i have to create my own synthax to structure data.

I remember of an algorithm i've created 1 year ago now allowing to `tokenize` pairs of parentheses inside a string.

Bingo, for nested data XML, Json or even TOML like, pairs of parentheses design is great to describe their nesting.

How it looks:

```

(destination:

  (restaurant:

    (menu:
      (size:
        (weight:150g)
        (size:small)
      )

      (size:
        (weight:200g)
        (size:medium)
      )

      (size:
        (weight:250g)
        (size:large)
      )
    )

  )

  (bookstore:

    (book:
     (title:Everyday Italian)
     (author:Giadia De Laurentiis)
     (year:2005)
     (price:
       (country:
         (price:40.0)
         (country:France)
       )
       (country:
         (price:39.5)
         (country:UK)
       )
       (country:
         (price:38.0)
         (country:Italy)
       )
     )
     (sells:
       (country:
         (s:10840)
         (country:France)
       )
       (country:
         (s:96539)
         (country:UK)
       )
       (country:
         (s:38)
         (country:Italy)
       )
     )
    )

    (book:
     (title:Harry Poter)
     (author:J K Rowling)
     (year:2005)
     (price:
       (country:
         (price:20.0)
         (country:France)
       )
       (country:
         (price:37.5)
         (country:UK)
       )
       (country:
         (price:31.0)
         (country:Italy)
       )
     )
     (sells:
       (country:
         (s:10840)
         (country:France)
       )
       (country:
         (s:96539)
         (country:UK)
       )
       (country:
         (s:38)
         (country:Italy)
       )
     )
    )

    (book:
     (title:Learning XML)
     (author:Erik T. Ray)
     (year:2003)
     (price:
       (country:
         (price:49.0)
         (country:France)
       )
       (country:
         (price:305.0)
         (country:UK)
       )
       (country:
         (price:306.0)
         (country:Italy)
       )
     )
     (sells:
       (country:
         (s:10840)
         (country:France)
       )
       (country:
         (s:96539)
         (country:UK)
       )
       (country:
         (s:38)
         (country:Italy)
       )
     )
    )
  )
)

```

These files are used to store data have the `.moutarde` extension.

Ok,so i read the file and then i use my algorithm.

 The latter returns two vectors having a length equal to the number of parentheses inside the string made after reading the file. The first vector contains number from 0 to the number of pairs of parentheses and having as index their apparition order inside the string. For example:

`"(mdffg(gfgf)kl)dfd()" `

will have the following pair vector

`[1, 0, 0, 1, 2, 2]`

The second vector simply returns the index of each parenthesis inside the string.

So, in our example:

`[0, 6, 11, 14, 18, 19]`

There only to describe the synthax of the data queries, and no surprise it's based on pairs of parentheses:

```

<!DOCTYPE html>

<html lang="en">

<head>

        <title> Teste </title>

        <link rel = "stylesheet" href = "style.css">

        <meta charset="utf-8"/>

</head>

(<body>

         (f:destination:
         <b>(v:restaurant/menu/size/weight:)</b>
           (f:bookstore/book:+:title:
             (w:title:=[Everyday Italian,Harry Poter,Learning XML]
               <ul>
                 (f:price/country:-:price:
                   (w:country:=[UK,Italy]
                     <li>here 1: (v:price:)</li>
                   )
                 )

                 (w:sells/country/country:=[France]
                 (f:sells/country:
                   (w:country:=[Franc2e]
                       <li>here 2: (v:s:)</li>
                   )
                 )
                 )

                 (f:sells/country:+:s:
                   (w:country:=[France,Italy]
                     <li>here3: (v:s:)</li>
                   )
                 )

                 <li>(v:title:)</li>
                 <li>(v:author:)</li>
               </ul>
             )
           )
  <center>
          (f:restaurant/menu/size:-:weight:
            (w:size:=[large,small]
            <i>(v:weight:)</i>
            )
          )
          (v:restaurant/menu/size/weight:)
        )
  </center>
</body>
)

```

We notice the same structure as the html file we want to output and the given instructions are inside parentheses. These files used for html file generation according to the requested data have the `.instruct` instruction.



There are 4 instructions type:

# Value:

`(v:variable_path:) `

# Where / If:

`(w:to_evaluate_variable_path:=[X1,X2])
`

Note that the previous condition is validated if the variable is equal to at least one of the variable in the list `[X1,X2]`.

Comparisons can also be `>` (greater), `<` (lower) or `!` (not equal).

# For loop

```

(f:variable_path:
   other_instructions
)

```

Nesting is allowed.

# Sort

```

(f:variable_path:+:sorting_variable_path:
other_instructions
)

```

The character `+` is used to ascendly sort, `-` for the opposite.

Now, we'll tokenize the pairs of parenthesee of the instruct file.

# Value

Starting from the current path, we iterate over the opening parentheses of `.moutarde` to find the right variable name at the same depth. If we don't find it, we return `VALUE_ERROR: wrong path`

# For Loop

Same thing, we search for the right variable path on which we'll iterate, then the depth of the current path will be stored inside a variable we name `depth_pos`.

It's from the current path that the search of the value and the conditions evaluations will be done.

Note that inside a for loop, our variable that iterates over the opening parentheses of the `.moutarde` can't go back beyond the lask known position of the iteration variable. The last known position of our iteration variable should be stored inside a vector to allow for loop nesting. Indeed, when we'll get out of the loop, we'll `pop_back()` the last element of the vector that stores the last known position of the iterating variables.

If our depth inside the `.moutarde` (computed from the sum of encountered opening parentheses - sum of encountered closing parenthesis) is higher to the current path depth, we jump directly to the end position of the parenthesis that gave us a depth too big.

\- How to get out of the for loop?

When the iterating variable path does not appear anymore in the `.moutarde`.

The only instruction that can change the current path is the for loop `f`

# Where

The same method to find the value, except that when we found it, we take its value and compre it to the introduced elements inside the associated list `[]`.

If the condition is validated, we normaly continue inside the `.instruct` and the `.moutarde`, else we put the current depth of `.moutarde` to the previous one, before we've encountered the condition and, inside the `.instruct`, we directly jump after the condition.

# Sort

It's getting a little more complicated.

In fact, what we'l output in the html file is, at this stage, scattered inside a vector of vector of string type, we'll name `tracks_ref`.

Each vector of vector corresponds to all the requested iteraation data for the current crossed path. At a point in the algorithm, if we are inside a level 3 of nesting for loop, then the vector of vector will contain 3 vectors. The last vector correspond to the data of the current path. The last element of the last vector correspond to the stored data of the last loop iteration with the last current path.

It's when we get out of the for loop that we'll have to sort ascendingly or descendingly the last vector elements before adding them to the last element of the penultimate vector. Now we can remove the last vector from `tracks_ref`.