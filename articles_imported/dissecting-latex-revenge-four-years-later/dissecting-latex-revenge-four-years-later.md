When I was a chemist, I wrote my internship report in LaTeX.

It was at first a pain in the ass:

--\> weird syntax with no apparent coherence

Especially for drawing objects, graphs, shapes... (cf: PGFPlot, TikZ)

Then I moved on and never returned to LaTeX because I did not need it.

But I remember the painful hours spent trying to render a good TikZ graphic, and I do not want those hours to be wasted.

So 4 years later I returned to LaTeX to learn it, for real.

I wanted to build a really coherent mental model by learning all its invariants.

And I can say it has been a great success, I even built a mini Doom in LaTeX --> [Go to section](#finally-doom-in-latex)

This is not only an article, it's personal.

In this deep dive into LaTeX, you will learn the basics, text formatting, math formatting, graphs rendering, how it can be used as a dataframe (masks filtering, transformations), shapes rendering, 3D onto 2D projections, shades... and so much more.

But also most importantly a deep understanding that LaTeX is not just a static markup language.

The macros are hyper powerful.

You can even traverse a tree just by using it.

TeX is a Turing-complete language.

First, all the code I will reference comes from my repo here:

[SomeLaTeX](https://github.com/julienlargetpiet/SomeLaTeX)

## The prerequisites & Basic mental model

### The engine

I used `lualatex` as the engine that compiles LaTeX code into PDF.

On Debian/Ubuntu, install it with:

```bash


sudo apt-get install lualatex


```

This is a very fast and modern engine.

I started writing my tutorial using `pdflatex` engine which is fine, but this newer engine brings some features we'll discuss later.

Also, because the compile system is absolute GARBAGE, in the sense that when you modify something that impacts your TOC, or structure in general( `\listoffigures`, `\maketitle`, `\label` / `\ref`, `\hyperlink`, `\hyperlink`...), then you must compile twice (explained more later on the architectural discussion).

To handle this, I always compile with `latexmk`, which is effectively the LaTeX build system.

```bash


latexmk -pdflatex="lualatex" -shell-escape file.tex


```

### Other dependencies

```bash


sudo apt update && sudo apt install \
texlive-luatex \
texlive-latex-recommended \
texlive-latex-extra \
texlive-fonts-recommended \
texlive-fonts-extra \
texlive-pictures \
texlive-science \
texlive-bibtex-extra \
latexmk \
biber \
python3-pygments


```

### Understanding structure of LaTeX code

It is simple. In order, you have:

- document type definition (article, ...) which determines the dimensions of the output PDF (A3, A4...) in the tutorial we'll focus on `article` -\> A4

- the preamble, it is where you import packages, import packages of packages and so on, you can also define macro here, this is a good practice

- the document content, this is located between `\begin{document}` and `\end{document}`, it is where the content (as you preshot) is located, what will be displayed on the PDF


It is:

```latex



\documentclass{article}

\usepackage{X} %imports
\usepackage{Y}
\usepackage{Z}
...

% macro definition
\newcommand{\link}[2]{\href{#1}{#2}}
\newcommand{\mybloglink}{https://julienlargetpiet.tech}
\definecolor{linkcolor1}{HTML}{4F9AD6} % special macro for defining color
...

\begin{document}

...

\end{document}



```

### The imports

So in the preamble i have:

```latex


\usepackage{lipsum}  % add tests \lipsum
\usepackage{tikz}
\usepackage{amsmath}  % math
\usepackage{amsfonts}  % more math symbols
\usepackage{graphics} % images
\usepackage{hyperref} % links
\usepackage[
    top=2cm,
    bottom=2cm,
    left=3cm,
    right=3cm
]{geometry}           % margins
\usepackage{pgfplots} % simplify graphs
\usepackage{float}    % add directive on figures
\usepackage{placeins} % Add \FloatBarrier for figures
%\usepackage[section]{placeins} % or here, automatically insert a \FloatBarrier at the end of every sections
\usepackage{setspace} % better lines spacing (inside paragraphs) (more breathing space), triggered with \onehalfspacing...
\usepackage{parskip}  % removes paragraph indentation + add clean separation between paragrapgh, but we can
                      % still control vertical space manually withh \setlength{\parskip}{1em}...
\usepackage[T1]{fontenc} % use T1 font encoding -> accented character...
\usepackage{lmodern}     % Latin Modern font, supports well T1 encoding
\usepackage{microtype}   % better micro spacing (letters/words)
\usepackage{fancyhdr}    % page headers
\usepackage{titlesec}    % used for sections style here, \titleformat
\usepackage[table]{xcolor}      % colors text with \textcolor - [table] means extra load of function like \rowcolor...
\usepackage{tcolorbox}   % used to highlight text, literally a colored box
\usepackage{listings}    % used for code-blocks
\usepackage{minted}      % used for code-blocks (alternative) - more powerful but rely on python - require `pdflatex -shell-escape file.tex`
\usepackage{multicol}    % handle multicolumns cleanly
\usepackage{pgf-pie}     % pie-chart
\usepackage{xstring}     % better for string programming
\usepackage{chemfig}     % for drawing molecules
\usepackage{pgfplotstable} %read csv
\usepackage{booktabs} % nicer tabs
\usepackage{soul}

% for \path[name intersections={of=f and g}];
\usetikzlibrary{intersections}
\usetikzlibrary{trees} % you know its use just by its name lol
\usetikzlibrary{3d} % enables 3d coordinates system
\usetikzlibrary{shapes.geometric}
\usetikzlibrary{graphs}
\usetikzlibrary{graphdrawing}

\usegdlibrary{trees} % from graphdrawing
\usegdlibrary{force}

\usepgfplotslibrary{ternary} % ternary diagram


```

Wow, that is so much packages, do not worry i annotated why they are used, and later in the explanations i will describe which macro comes from which packages, so you got a good understanding of what fo what.

Note, you see thet LaTeX comments are declared with the `%` character. And there is no multiline comments sadly, so `%` everywhere :-(

And the preamble is not done yet, now let's see the real configurations setup:

But let's discuss already the importance of thse packages and what they do already quickly

##### lipsum

This package provides special Latin text you can use to test your formatting.

To use it in you interest sections, use:

- `\lipsum` -\> big text

Or just sequence as:

- `\lipsum[1]` -\> smaller text piece

- `\lipsum[1-2]` -\> medium text piece (first piece + second)


and so on...

##### TikZ

That is used to render all kinds of shapes: 2D, 3D projections onto 2D plan, shaders...

And that is the foundation of `PGFPlot` that is used to display graphs

##### amsmath & amsmfonts

Used to vastly enhance the math formatting (especially for equation solving), brings some useful features and `amsmfonts` brings more math symbols.

##### graphics

Is used to display images (JPG, PNG, JPEG...)

Example:

```text


\includegraphics[width=0.35\textwidth]{lynxcute.jpg}


```

![lynx1.png](../assets/common_files/images_latex/lynx1.png)

Remember the `include` keyword, because this is key for later.

We can also tweak dimensions, of course:

```latex


\includegraphics[height=4cm,
                 width=4cm]{lynxcute.jpg}


```

![lynx2.png](../assets/common_files/images_latex/lynx2.png)

##### hyperref

Brings the ability to display clickable links in a PDF viewer, (with `\href`).

##### Geometry

Look this is essential:

```latex


\usepackage[
    top=2cm,
    bottom=2cm,
    left=3cm,
    right=3cm
]{geometry}           % margins


```

Just loading the package with options between `[...]` defines the margins for the entire document.

##### PGFPlot

This package provides the PGFPlot macros, that are super useful to dislay pretty much al kind of graphs.

It is dependent on TikZ, that is also a good practice to import it after TikZ

##### float & placeins for figures

Here, it is a bit subtle.

In fact when you decide to draw a figure, basically a div in HTML, according to its dimension and its neighbors dimensions, LaTeX engine can optimize its placement, like on the next page, or even stack multiple figures.

With this package, you can use the keyword: `H` -\> here, no exception !

Good for predictable layouts:

```latex



...

\begin{figure}[H]
    \centering
    \includegraphics[width=0.5\textwidth]{lynxcute.jpg}
    \caption{Example Image}
\end{figure}

...



```

That puts the figure exactly HERE, where it is defined.

instead of:

```latex



...

\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.5\textwidth]{lynxcute.jpg}
    \caption{Example Image}
\end{figure}

...

\FloatBarrier


```

Where `[htbp]` -\> here, top, bottom, placement of figures (stack of figures with others)

So `[htpb]` are set of allowed placement the engine will look at and decide where to put this figure.

Note also that `placeins` provides `\FloatBarrier` that tells the figures defined before can not be placed after this barrier.

In fact `figure` is essential block for wrapping reference content.

You have to put `\caption{...}` inside figure for them to be referenced by the `\listoffigures` that is like the automatic TOC trigger (we'll discuss later) but for figures.

We will come back on that later.

Whe you add or remove a figure, you have to compile your document twice to `\listoffigure` take the changes into account.

```bash


latexmk -pdflatex="lualatex" -shell-escape main.tex
latexmk -pdflatex="lualatex" -shell-escape main.tex


```

Like TOC trigger `\tableofcontents` -\> TOC trigger does.

##### setspace

Brings `\onehalfspacing`, `\singlespacing`, `\doublespacing`

Affecting spacing between lines of text.

Spacing inside paragraphs.

Example:

```latex



Normal text

\onehalfspacing

This paragraph has more breathing space.

\doublespacing

This one is even more spaced.



```

Or scoped

```latex


\begin{spacing}{1.5}
This part only is spaced.
\end{spacing}


```

technically it works by modifying the simple Tex primitive `\baselineskip`

##### parskip

Just by including this package, it removes indentation for each paragraph

From:

```text


    This paragraph starts with an indent.


```

To:

```text


This paragraph starts with an indent.


```

Adds vertical spaces between paragraphs:

```latex


Paragraph 1.

Paragraph 2.



```

##### fontenc

Defines the encoding of the document character.

So here w euse `T1` encoding, the default being `O1`

```latex


\usepackage[T1]{fontenc}



```

Allowing accented character, vry common in french for example, like "é" etcetera

But here,because we are using `lualatex` as the engine, `T1` is not explicitly needed.

Indeed, this engine uses directly unicode encoding.

So it is necessary with `pdflatex` engine.

But with `lualatex`, we can remove it and instead replace it with:

```latex


\usepackage{fontspec} % use system fonts directly
\setmainfont{Latin Modern Roman} % set the font used, must be installed on your system


```

instead of providing font accpete by teh engine internally like after we did:

```latex


\usepackage{lmodern}     % Latin Modern font, supports well T1 encoding


```

##### microtype

Including this package automatically do the following.

It improves typographic quality automatically by adjusting:

spacing at a very fine (micro) level

The 3 main features

1. Character protrusion (margin kerning)

Letters slightly “hang” into the margin:

"Hello"

-\> Quotes or punctuation stick out a bit.

Why?
makes text edges visually aligned
avoids “ragged” margins

2. Font expansion

LaTeX can slightly stretch or shrink characters:

-\> like ±1–2%

This helps:

reduce bad line breaks
avoid big spaces between words

3. Better spacing (kerning + tracking)

It improves:

spacing between letters
spacing between words

-\> makes text more even and readable

Without:

- uneven spacing
- ugly justification
- large gaps between words

With:

- smooth text flow
- tighter, more consistent lines
- professional look

##### fancyhdr

Allows you to define a common page style (discussed later).

##### titlesec

Allows you to define a common style for section headings (discussed later).

##### xcolor

Allow to color text

Example:

```latex


\textcolor{blue}{Important}


```

We can define our own color like so, in the HTML coordinate system:

```latex


\definecolor{mycolor1}{HTML}{1E90FF}


```

and then use it:

```latex


\textcolor{mycolor1}{Important} % call to mycolor1 defined in preamble with \definecolor


```

or use it directly:

```latex


\textcolor[HTML]{FF5733}{Important} % inline call of HTML colors (hexadecimal)


```

You can also quickly define color doing so with `\colorlet`:

```latex


\colorlet{primary}{blue!60!black}
\colorlet{secondary}{orange!30}
\colorlet{accent}{green!40!black}


```

Note that it is `color1!percentage_of_color1!color2`

And when we do `orange!30` it means `orange!30!white`

Here we imported as:

`\usepackage[table]{xcolor}`

to load exra `xcolor` function such as `\rowcolor` which is super useful for the table, we will discuss it later.

##### soul

Obviously, we're not talking about music, but a simple manner to highlight text.

Just:

```latex


Hoo! \hl{highlighted} !!


```

![highlight1.png](../assets/common_files/images_latex/highlight1.png)

And you can change default highlight color doing so with `\sethlcolor{COLOR}`:

```latex


\sethlcolor{cyan}

Hoo! \hl{highlighted} !!


```

Note, this affects next color of all the next occurence of `\hl{TEXT}`, so reset it to yellow if you want ;)

![highlight2.png](../assets/common_files/images_latex/highlight2.png)

##### tcolorbox

Used to create a colored box wrapping text inside, like:

```latex



\begin{tcolorbox}
This is a highlighted block
\end{tcolorbox}

Customoized tcolorbox

\begin{tcolorbox}[
    colback=blue!10,
    colframe=blue!5!green
]
This is a second highlighted block
\end{tcolorbox}


```

![tcolorbox1.png](../assets/common_files/images_latex/tcolorbox1.png)

![tcolorbox1B.png](../assets/common_files/images_latex/tcolorbox1B.png)

```latex


Customoized 2 tcolorbox

\begin{tcolorbox}[
    colback=blue!10,
    colframe=mycolor1
]
This is a second highlighted block
\end{tcolorbox}


```

![tcolorbox2.png](../assets/common_files/images_latex/tcolorbox2.png)

As you see you can customize background and border color of the boxes.

But look, you can also give them a title ( `title`) and customize its title color ( `coltitle`) and title color background ( `colbacktitle`).

Inside the options `[...]` of this environment `tcolorbox`.

You can round the corner `arc`.

And `center title` -\> expands to `halign title=center` under the hood.

```latex


Customoized 3 tcolorbox

\begin{tcolorbox}[
    colback=gray!10,
    colframe=gray!50,
    coltitle=blue,
    colbacktitle=orange!5,
    arc=6pt,
    boxrule=0.5pt,
    title=Hell Yeah Title
]
Clean modern box
\end{tcolorbox}


```

![tcolorbox3.png](../assets/common_files/images_latex/tcolorbox3.png)

And tweak border width ( `boxrule`).

```latex


\begin{tcolorbox}[
    colback=gray!10,
    colframe=gray!50,
    coltitle=blue,
    colbacktitle=orange!5,
    arc=6pt,
    boxrule=2.5pt,
    title=Hell Yeah Title,
    center title
]
Clean modern box2
\end{tcolorbox}


```

![tcolorbox4.png](../assets/common_files/images_latex/tcolorbox4.png)

##### Listings For Code-Blocks

It is used for code-block

Basically it is a library that comes with this super powerful configuration setup that we can call in the `preamble`:

First we connect `tcolorbox` and `listings`

```latex


\tcbuselibrary{listings}


```

Then, look !

```latex



\newtcblisting{codebox1}{
    listing only,
    colback=gray!5,
    colframe=gray!30,
    arc=4pt,
    boxrule=0.5pt,
    listing options={
        language=C++,
        basicstyle=\ttfamily\small,
        keywordstyle=\color{blue},
        commentstyle=\color{gray},
        stringstyle=\color{green!50!black},
        breaklines=true,
        keepspaces=true,
        columns=fullflexible,
        showstringspaces=false
    }
}



```

We are defining an environment called `codebox1` (exactly what you think).

So we will able to call it like:

```latex


\begin{codebox1}
...
\end{codebox1}


```

Create a tcolorbox-based code environment using listings

`listing only`

Means:

the box contains only code
no extra text content

If you removed it, you could mix text + code inside the box.

Box appearance

```latex


colback=gray!5,
colframe=gray!30,
arc=4pt,
boxrule=0.5pt,


```

These are pure tcolorbox options:

- `colback=gray!5` -\> background color

- `colframe=gray!30` -\> border color

- `arc=4pt` -\> rounded corners

- `boxrule=0.5pt` -\> border thickness


The core: `listing options={...}`

This is where listings comes in

Language -> `language=C++`

Enables syntax highlighting for C++

Font

`basicstyle=\ttfamily\small `

- `\ttfamily` -\> monospace font

- `\small` → smaller size


Syntax highlighting

```latex



keywordstyle=\color{blue},
commentstyle=\color{gray},
stringstyle=\color{green!50!black},



```

Defines colors:

- `keywords` -\> blue (int, return, etc.)
- `comments` -\> gray
- `strings` -\> green-ish

Layout behavior

- `breaklines=true` -\> Long lines wrap automatically

- `keepspaces=true` -\> Preserves indentation (VERY important for code)

- `columns=fullflexible` -\> Better alignment of characters (prevents weird spacing issues in monospace)

- `showstringspaces=false` -\> Removes ugly markers for spaces inside strings


Mental model

Your environment is basically:

“A styled box + syntax-highlighted code renderer”

Instead of repeating this everywhere:

```latex


\begin{tcolorbox}
\begin{lstlisting}[... tons of options ...]
...
\end{lstlisting}
\end{tcolorbox}


```

You just write:

```latex


\begin{codebox1}
...
\end{codebox1}



```

Clean :)

![codeblocklisting.png](../assets/common_files/images_latex/codeblocklisting.png)

Much better than native code-blocks with:

```latex


\begin{verbatim}
int main() {
    return 0;
}
\end{verbatim}


```

![codeblockverbatim.png](../assets/common_files/images_latex/codeblockverbatim.png)

##### Minted

But wait, there's more !

Yess, more beautiful code-block

In the preamble we define the style / color sheme to be used for the code-blocks with:

```latex


\usemintedstyle{friendly}


```

Associated with `tcolorbox` box:

```latex



\begin{tcolorbox}[colback=gray!5,
                  colframe=gray!30,
                  arc=4pt]
\begin{minted}{cpp}
#include <iostream>

int main() {
    std::string x = "this is a string";
    std::cout << x << "\n";
    // comment
    return 0;
}
\end{minted}
\end{tcolorbox}


```

![codeblockminted.png](../assets/common_files/images_latex/codeblockminted.png)

Practically out-of-the-box.

Less work than with `listings`

##### multicol

Very simple concepts, just multiple column text in one page.

Look:

```latex


\begin{multicols}{2}

    \lipsum[1-3]

\end{multicols}


```

Here with 2 columns, which is most common.

![multicol.png](../assets/common_files/images_latex/multicol.png)

You can also manually break the text to make it appear on the next column

```latex


\begin{multicols}{2}

    This is col 1.

    \lipsum[1]

    \columnbreak

    This is col 2.

    \lipsum[2]

\end{multicols}


```

![multicolbreak.png](../assets/common_files/images_latex/multicolbreak.png)

##### pgf-pie

Bring pie-charts to pgfplot API, we'll discuss later.

##### xstring

Wowww, okok this one is super duper powerfull!!!

Basically, maybe i'm forshadowing a little about macro programming but fuck it, let's talk about that:

It basically brings some functions to compare string variables in LaTeX, such as:

- Comparisons

```latex


\def\a{Rémi} % variable definition -> \a = Rémi
\IfStrEq{\a}{Rémi}{Yes}{No} % -> Yes


```

Yep, you read it correctly string comparisons and ternary expression.

- Get if substr is present in another string

```latex


\IfSubStr{hello}{ell}{Yes}{No} % -> Yes


```

```latex


\IfSubStr{\a}{ell}{Yes}{No} % -> no


```

- Extract substring

```latex


\StrMid{abcd}{2}{4}{\result}


```

Now `\result` is `bcd`, yes we start from 1!

```latex


\StrLen{hello}{\len}


```

Now `\len` is `5`

We can after compares number as we'll discuss later.

```latex


\StrSubstitute{hello world}{world}{LaTeX}{\resultb}


```

Now `\resultb` is `hello LaTeX`

##### chemfig

A must have for drawing molecules (organic chemists)

With `\chemfig{...}`

Look:

```latex


\chemfig{C-C-O}


```

Draw bonds wide wise between nodes `C` `C` and `O`

![chem1.png](../assets/common_files/images_latex/chem1.png)

All 3 types of bonds (weakest to strongest):

```latex


\chemfig{C-C}

\chemfig{C=C}

\chemfig{C~C}


```

![chem2.png](../assets/common_files/images_latex/chem2.png)

Of course, it would not be a proper molecules drawing package if there were not a way to control angles between nodes.

```latex


\chemfig{-[:30]C-[:60]=O}
\chemfig{(H-)(H-)C(-H)(-[:55]H)-[:30]C=[:60]O}

\chemfig{C(=[:30]O)
          (=[:270]O)
          (=[:300]
             (H-)
             I
             (-H))
         -C
         }

Isopropanol:

\chemfig{
    CH_3-CH(-[:90]OH)-CH_3
}


```

Basically you add this `[:angle]` after each bond to dictate the angle

And yess, as you see of course a node can be linked to multiple nodes, we just, at the same level, defines all its connected nodes.

![chem3.png](../assets/common_files/images_latex/chem3.png)

Do not waste time to tweak bonds angle and add nodes to draw cycles, you can just simply do it with the `*N(-...-)` synthax.

```latex


Cyclohexane:

\chemfig{
    *6(------)
}


```

![chem4.png](../assets/common_files/images_latex/chem4.png)

Here we alternate link type.

```latex



Benzene:

\chemfig{
    *6(-=-=-=)
}



```

![chem5.png](../assets/common_files/images_latex/chem5.png)

```latex



Another example:

\chemfig{
    *6(-(-CH_3)=-(-OH)-=-)
}


```

![chem6.png](../assets/common_files/images_latex/chem6.png)

And of course, painfulless way to draw charges.

```latex



\chemfig{N^\oplus}

\chemfig{O^\ominus}

% to not collide with specific chemfig DSL link synthax, group the minus like "{-}"
% so now "-" is just a character, not a special chemfig synthax
\chemfig{O^{-}}
\chemfig{O^{+}}


```

![chem7.png](../assets/common_files/images_latex/chem7.png)

##### pgfplotstable

Ok, hear me out !

This is the feature that made me realize i could do some basic dataframe transformation inside LaTeX, which is absurdly cool.

But before diving to the `table` thing, first, it is just a simple way to bring data into plots, which is already... you guessed it , cool.

Take a look at this simple code:

```latex



\begin{tikzpicture}
\begin{axis}[xlabel=$x$,
             ylabel=$y$,
             domain=-2:2,
             grid=both,
             grid style=gray!20,
             legend pos=north west,
             width=10cm,
             height=6cm]

    \addplot[name path = f,
             color=blue,
             thick]{x^2};

    \addplot[name path = g,
             color=red,
             thick]{x^3};

    \draw[->] (axis cs:-1,1) -- (axis cs:1,2) node[right] {Point 2};
    \draw[->] (axis cs:-1,0) node[right] {Point 1} -- (axis cs:1,-2);

    \addplot[gray,
             fill opacity = 0.3
    ] fill between [
        of = f and g
    ];

    % the order of legend correspond to the order of the \addplot
    \addlegendentry{$x^2$}
    \addlegendentry{$x^3$}

\end{axis}
\end{tikzpicture}


```

![plot1.png](../assets/common_files/images_latex/plot1.png)

Alright, here we just draw 2 functions:

- `x^2`
- `x^3`

with `\addplot`

The options of each plot is located inside `[...]`

This is why we see `x^2` as blue and `x^3` as red.

We can also vary the width of the lines using `thick, thin...`, here it is **thick**

Also, nice thing e can name each plot, `f` -\> `x^2` and `g` -\> `x^3`

Why name it ?

because of the integral fill between those 2 functions we do with:

```text


\addplot[gray,
         fill opacity = 0.3
] fill between [
    of = f and g
];


```

If we would just draw the integral of `x^2` let's say, we would just draw a ghost function like `0` naming it `g`, name it and then draw like we did.

we would just add the _option_ `[draw=none]` to make `g` invisible

like:

```latex


\addplot[name path = g,
         draw=none]{0};


```

You also see that we put legends, simple enough, just:

```text


    \addlegendentry{$x^2$}
    \addlegendentry{$x^3$}



```

Note that here the legend match the color of what they represent, blue and then red.

This is coherent, because we first plotted `x^2` -\> blue and then `x^3` -\> red, and put the legends in the **same order**

Now, where the hell do the arrows come from ????

From:

```text


\draw[->] (axis cs:-1,1) -- (axis cs:1,2) node[right] {Point 2};
\draw[->] (axis cs:-1,0) node[right] {Point 1} -- (axis cs:1,-2);


```

In fact `\draw` is a TikZ primitive allowing to draw all kind of stuff, shapes...

For arrow, we use `[->]` as draw option

As you preshot, coordinates of arrow is `(x_start, y_start) -- (x_end, y_end)`

Here it is a little different because we draw arrow in `pgfplot` coordinate system that is not scaled with TikZ coordinate system, so we just tell it putting:

```latex


axis cs:


```

before each coordinate, `cs` -\> coordinate system

You can also print something next to each coordinate, like a `node` (more on that later)

So in that code for example:

```latex


\draw[->] (axis cs:-1,0) node[right] {Point 1} -- (axis cs:1,-2);


```

At the right of the starting point of the arrow, we print "Point 1".

Now, more on parameters options inside `[...]`

Why i want to discuss more about that ?

Because experimenting with this made me realize something really strange, look at that:

```text


[color=red!90, thick]


```

is the same as:

```text


[thick, color=red!90]


```

Why ?

Because in fact, LaTeX expands `thick` to `line width = 0.8pt`, so there is always an explicit parameter name assigment even if you do not see it!

And that overwhelming powerful for quick graphs in the urge !

Btw, different line width can be:

- `ultra thin`
- `very thin`
- `thin`
- `semithick`
- `thick`
- `very thick`
- `ultra thick`

Now, what about the axis ?

So as you se, to define a plot we first need to define a `tikzpicture`, because a pgfpot needs it.

Then we need to define an axis, this is...the axis, yeahh !

But like any **scene** in LaTeX, we can give it properties inside `[...]`

So here we did:

- define the labels on each axis `xlabel` / `ylabel`, here this is `x` and `y` respectively (math font)
- the domain over which the function is sampled with `domain`

We could also do that with:

- `xmin` / `xmax`

And equivalently for `y` domain:

- `ymin` / `ymax`

Now the grid:

We show it with `grid=both`, we could do `grid=none` to not display a grid.

to add specific `y` or `x` axis grid, we do it with these options:

- `xmajorgrids`
- `ymajorgrids`
- `xminorgrids`
- `yminorgrids`

And how do we anchor the legend ?

Justo doing:

- `north west`
- `south west`
- `north east`
- `south east`

And we can define the `width` and the `height` of the plot itself.

Here another plot:

```latex



\begin{tikzpicture}
\begin{axis}[xlabel=$x$,
             ylabel=$y$,
             domain=-2:2,
             grid=both,
             axis lines=right,
             axis line style={->},
             grid style=gray!20,
             legend pos=north west,
             width=10cm,
             height=6cm]

% axis ine options:
% left
% right
% middle
% center
% box
% none

    \addplot[name path = f,
             color=blue,
             thick,
             dotted]{x^2 - 2};

    \addplot[dashed]{1 + x^2};
    \addplot[dotted]{2 + x^2};
    \addplot[dashdotted]{x^2};

% Custom dash

    \addplot[
        dash pattern=on 5pt off 2pt,
        color=blue
    ]{x^1};

\end{axis}
\end{tikzpicture}


```

![plot2.png](../assets/common_files/images_latex/plot2.png)

What's new ?

First, we shifted the axis to the right:

```latex


axis lines=right


```

Added the arrow as the direction axis end:

```latex


axis line style={->}


```

We could have done that to change the direction:

```latex


axis line style={<-}


```

And modified the grid style color:

```latex


grid style=gray!20


```

Also, you see that we can change furtherly the style of the line, with the `dashed` option, that is expanded to `dash pattern = on 3pt off 3pt`

Then you can again further customize it with:

```latex


dash pattern=on 5pt off 2pt,


```

Now, we come closer to what's interesting in this topic, the tables.

For now, what to do if we want to plot real data coordinates ?

Just use `coordinates` lol

```latex


\begin{tikzpicture}
\begin{axis}[xlabel=$x$,
             ylabel=$y$,
             domain=-2:2,
             grid=both,
             legend pos=north west,
             width=10cm,
             height=6cm]

    \addplot[only marks,
             mark=*,
             color=purple] coordinates {
        (0, 0)
        (1, 1)
        (2, 4)
    };

    \addplot[mark=*,
             color=green!40!black,
             ] coordinates {
        (-2, -3)
        (1, 0.75)
        (1.5, 5)
        (2, 3)
    };

    \node at (axis cs:1,1.8) {Hello};

\end{axis}
\end{tikzpicture}


```

![plot3.png](../assets/common_files/images_latex/plot3.png)

Here, instead of printing a continuous function like `\addplot[...]{FUNCTION}`, the synthax is:

```latex


\addplot[...] coordinates { POINT1,
                            POINT2,
                            ... }


```

expanded to:

```latex


\addplot[...] coordinates { (x1, y1),
                            (x2, Y2),
                            ... }


```

Here, we can either print only points, with `only marks` or link them with not putting `only marks` option.

If we want a smooth line, to make the intermediates values more visualy expressive, just put `smooth`.

```text


\begin{tikzpicture}
\begin{axis}[xlabel=$x$,
             ylabel=$y$,
             domain=-2:2,
             grid=both,
             legend pos=north west,
             width=10cm,
             height=6cm]

    \addplot[only marks,
             mark=diamond*,
             color=purple] coordinates {
        (0, 0)
        (1, 1)
        (2, 4)
    };

    \addplot[mark=triangle,
             color=green!40!black,
             smooth] coordinates {
        (-2, -3)
        (1, 0.75)
        (1.5, 5)
        (2, 3)
    };

    \node at (axis cs:1,1.8) {Hello};

\end{axis}
\end{tikzpicture}


```

![plot4.png](../assets/common_files/images_latex/plot4.png)

Note that we can also change the mark shape, like:

- `*`
- `+`
- `X`
- `square` -\> empty square
- `triangle` -\> empty triangle
- `diamond` -\> empty diamond
- `pentagon` -\> empty pentagon
- `star` -\> empty star
- `square*` -\> filled square
- `triangle*` -\> filled triangle
- `diamond*` -\> filled diamond
- `pentagon*` -\> filled pentagon
- `star*` -\> filled star
- `o` -\> hollow
- `oplus` -\> hollow with plus sign
- `otimes` -\> hollow with cross sign

And even more whangling the triangle orientation:

```latex


triangle
triangle*
triangle down
triangle down*
triangle left
triangle right


```

Note: those requires `\usetikzlibrary{shapes.geometric}`.

Heeere we are my friends, the moment you were waiting, or maybe on of the moment, we still ave not talk about freaking DOOOOOM on LaTeX, don't worry it will come.

So for now `table` !!!!

You remember of `coordinates` ?

I hope so, it is just the section above lol ;)

Yess, it is great to have the ability to give realworld coordinates to construct a plot, but we all know that in... real world (haha), the data are big, scattered around different sources and the only one that can unite them is a reallllly strong format, the infamous CSV !!!!!

So in an ideal world, we would have a tool that could parse a CSV and stock it in memory to feed it to pgfplot.

We may are not in an ideal world, but we have this tool, just look!

```latex


\begin{tikzpicture}
\begin{axis}[xlabel=$x$,
             ylabel=$y$,
             domain=-2:2,
             grid=both,
             legend pos=north west,
             width=10cm,
             height=6cm]

    \addplot[mark=*,
             only marks,
             color=red!40!black] table[col sep=comma,
                                       x=x,
                                       y=y] {scatterplot.csv};

\end{axis}
\end{tikzpicture}


```

![plot5.png](../assets/common_files/images_latex/plot5.png)

The options are:

- `col sep = comma` -\> CSV column separator
- `x=colanme_corresponding_to_x`
- `y=colanme_corresponding_to_y`

here the csv is `scatterplot.csv`:

```text


x, y, y2
-2, -3, 4
-2, 2, 4
1, 0.75, 4
1, 1, 4
2, 3, 4
2, 2.4, 4


```

In the previous example, `y2` column was not used, but not there:

```latex


\begin{tikzpicture}
\begin{axis}[xlabel=$x$,
             ylabel=$y$,
             domain=-2:2,
             grid=both,
             legend pos=north west,
             width=10cm,
             height=6cm]

    \addplot[mark=*,
             only marks,
             color=red!40!black] table[col sep=comma,
                                       x=x,
                                       y expr=\thisrow{y} * 2 + \thisrow{y2}] {scatterplot.csv};

    \addplot[mark=*,
             only marks,
             color=blue!45] table[col sep=comma,
                                  x=x,
                                  y expr=\thisrow{y} * 2 * \thisrow{y2}] {scatterplot.csv};

    \addplot[mark=*,
             only marks,
             color=green!40] table[col sep=comma,
                                    x=x,
                                    y expr=\thisrow{y} * 2 + 2 * \thisrow{y2},
                                    restrict expr to domain={\thisrow{x}}{0:2}] {scatterplot.csv};
                            % `restrict expr to domain` expects two arguments:
                            %   1) an expression (here: \thisrow{x})
                            %   2) a domain interval (here: 0:2)
                            % Braces are required to delimit each argument explicitly,
                            % especially since \thisrow{x} is itself a macro with its own argument.
                            % So we write {\thisrow{x}}{0:2} to avoid ambiguity in TeX parsing.

\end{axis}
\end{tikzpicture}


```

![plot6.png](../assets/common_files/images_latex/plot6.png)

Hoo, what am i seeing ?

Transformations ?

YESSSS, this is it, with `y expr` option

You do:

```latex


y expr = Y OPERATOR Y2 ...


```

or whatever, that expands to:

```latex


y expr = \thisrow{y} OPERATOR \thisrow{y2} ...


```

Think of it as transformations are under the hood, happening row per row.

And you noticed ?

The domain filtering for a specific plot!!

```latex


restrict expr to domain={\thisrow{x}}{0:2}


```

Only f(x) which x belongs to 0 to 2 will be plotted for this plot.

Hohoho, but that is not done, in `table`, you can even filter by the y values, with a custom logic, that is what i call **REAL MASK FILTERING**

Leeeeeets's Gooo

```latex


\begin{tikzpicture}
\begin{axis}[xlabel=$x$,
             ylabel=$y$,
             domain=-2:2,
             grid=both,
             legend pos=north west,
             width=10cm,
             height=6cm]

    \addplot[mark=*,
             only marks,
             color=red!40] table[col sep=comma,
                                    y filter/.code = {
                                      \ifnum\thisrow{y}>2
                                      \def\pgfmathresult{nan}
                                      \fi
                                    },
                                    x=x,
                                    y expr=\thisrow{y} * 2 + 2 * \thisrow{y2}] {scatterplot.csv};

\end{axis}
\end{tikzpicture}


```

![plot7.png](../assets/common_files/images_latex/plot7.png)

It is introduced with:

```latex


y filter/.code = {
  \ifnum\thisrow{y}>2
  \def\pgfmathresult{nan}
  \fi
}


```

in the table option (and yess, a litte forshadowing of what is programming in LaTeX with `\ifnum\varOPERATORvalue`)

So, by just assigning special variable of pgfplot `\pgfmathresult` to `nan` with:

```latex


\def\pgfmathresult{nan}


```

I'm intentially omiting certain values.

But here i'm just filtering on raw CSV Y values, what if i want to filter on the transformation i'm aplying ?

Recall, the transformation is:

```latex


y expr=\thisrow{y} * 2 + 2 * \thisrow{y2}


```

Hmmmm, that is in fact totaly possible!

In fact the output of `table` if outputed to the input of `\addplot`, and that is there where we can aplly filter on the newly computed `y`

Then we do:

```latex


\begin{tikzpicture}
\begin{axis}[xlabel=$x$,
             ylabel=$y$,
             domain=-2:2,
             grid=both,
             legend pos=north west,
             width=10cm,
             height=6cm]

    \addplot[
        mark=*,
        only marks,
        color=blue!40,
        y filter/.expression={y > 10 ? nan : y},
        unbounded coords=discard
    ] table[
        col sep=comma,
        x=x,
        y expr=\thisrow{y} * 2 + 2 * \thisrow{y2}
    ] {scatterplot.csv};

\end{axis}
\end{tikzpicture}


```

![plot8.png](../assets/common_files/images_latex/plot8.png)

You see it ?

Right here in the addplot options:

```latex


y filter/.expression={y > 10 ? nan : y}


```

A super useful ternary expression that returns `nan` if `y` is superior to `10`

And after we put the option:

```latex


unbounded coords=discard


```

That tells to dot show coordinates that are `nan`, `inf` and `-inf`

That's neat

But now, what if multiple plots uses the same CSV, it would be a waste of computational ressources to parse it for each plot.

Don't worry:

```latex


\begin{tikzpicture}
\begin{axis}[title={Title Yess, a title},
             xlabel=$x$,
             ylabel=$y$,
             domain=-2:8,
             grid=both,
             legend pos=north west,
             width=10cm,
             height=6cm]

    % global tables
    \pgfplotstableread[col sep=comma]{scatterplot.csv}\mytable

    \pgfplotstableread[col sep=comma]{scatterplot2.csv}\mytableB

    %concat mytableB to mytable
    \pgfplotstablevertcat{\mytable}{\mytableB}

    \pgfplotstablecreatecol[
        create col/expr={\thisrow{y}^2 - \thisrow{y2}}
    ]{y3}{\mytable}

    \addplot[mark=*,
             only marks,
             color=blue!45] table[col sep=comma,
                                  x=x,
                                  y expr=\thisrow{y3} * 2\thisrow{y2}] {\mytable};

\end{axis}
\end{tikzpicture}


```

![plot9.png](../assets/common_files/images_latex/plot9.png)

Note, here we added a title with option `title = {...}`

`scatterplot2.csv`:

```text


x, y, y2
3, -3, 4
3, 2, 4
4, 0.75, 4
4, 1, 4
5, 3, 4
6, 2.4, 4


```

And yess we can define table object doing so:

```latex


\pgfplotstableread[col sep=comma]{scatterplot.csv}\mytable
\pgfplotstableread[col sep=comma]{scatterplot2.csv}\mytableB


```

We can even **concatenate** by row / vertialy (vertcat):

```latex


%concat mytableB to mytable
\pgfplotstablevertcat{\mytable}{\mytableB}


```

Now `\mytable` has rows of `\mytableB` concatenated.

That'not even done yet, we can modify this object creating a column as a transformation for example:

```latex


\pgfplotstablecreatecol[
    create col/expr={\thisrow{y}^2 - \thisrow{y2}}
]{y3}{\mytable}


```

and we could even filter the column creation by a mask:

```text


\begin{tikzpicture}
\begin{axis}[title={Title Yess, a title},
             xlabel=$x$,
             ylabel=$y$,
             domain=-2:8,
             grid=both,
             legend pos=north west,
             width=10cm,
             height=6cm]

    % global tables
    \pgfplotstableread[col sep=comma]{scatterplot.csv}\mytable

    \pgfplotstableread[col sep=comma]{scatterplot2.csv}\mytableB

    %concat mytableB to mytable
    \pgfplotstablevertcat{\mytable}{\mytableB}

    \pgfplotstablecreatecol[
        create col/expr={
            \thisrow{y} < 2 ? (\thisrow{y}^2 - \thisrow{y2}) : nan
        }
    ]{y3}{\mytable}

    \addplot[mark=*,
             only marks,
             color=blue!45,
             unbounded coords=discard
             ] table[col sep=comma,
                     x=x,
                     y expr=\thisrow{y3} * 2\thisrow{y2}] {\mytable};

\end{axis}
\end{tikzpicture}


```

![plot10.png](../assets/common_files/images_latex/plot10.png)

**That is some dataframe operation directly inside LaTeX ----> AWESOME**

##### intersections

Here, it is a TikZ library that we import:

```latex


\usetikzlibrary{intersections}


```

Allowing to do that in pgfplot for example:

```latex


\begin{tikzpicture}
\begin{axis}[domain=-1:2]

    \addplot[name path=f, blue]{x^2};
    \addplot[name path=g, red]{x};

    % create the intersections "intersection-N"
    \path[name intersections={of=f and g}];

    \fill (intersection-1) circle (2pt);
    \fill (intersection-2) circle (2pt);

    \node at (intersection-1) [above] {$x=0$};
    \node at (intersection-2) [above] {$x=1$};

\end{axis}
\end{tikzpicture}


```

![plot11.png](../assets/common_files/images_latex/plot11.png)

So nothing really new, naming plots, and after we just create ALL the intersections:

```latex


% create the intersections "intersection-N"
\path[name intersections={of=f and g}];


```

Whose name will be `intersection-INTEGER`.

After that we can do whatever we want with those intersections like creatng filed black (default color) circles.

```latex


\fill (intersection-1) circle (2pt);
\fill (intersection-2) circle (2pt);


```

Annotating them:

```latex


\node at (intersection-1) [above] {$x=0$};
\node at (intersection-2) [above] {$x=1$};


```

Note that it is an TikZ primitive, it means we can use it with TikZ shapes creation like so:

```latex


\begin{tikzpicture}

    % Define square
    \draw[name path=mysquare]
        (-1,-1) rectangle (1,1);

    % Define circle
    \draw[name path=mycircle]
        (0,0) circle (1.15);

    % Compute intersections
    \path[name intersections={of=mysquare and mycircle}];

    % Draw intersection points
    \foreach \i in {1,2,3,4,5,6,7,8} {
        \fill (intersection-\i) circle (2pt);
        \node at (intersection-\i) [above] {\i};
    }

\end{tikzpicture}


```

![plot12.png](../assets/common_files/images_latex/plot12.png)

Again some BIG foreshadowing when it comes to variables / lists and especially loops...

:=)

Note that writing the loop, you have to be sure to not be out of the actual intersections. Here, there are 8 (i looked the shape before), so i stopped 8, not 9.

It would have bee another story if the diameter of the circle changed obviously.

In fact here because the center of the square and the center of the circle coincide, so when circle diameter is small, 0 intersections, then there is a value of the diameter where there are 4 intersections points, then if we increase again, it increases to 8 intersections points, then 8, then 0.

##### trees & graphs & graphdrawing

Ok, one time or anotheryou will need trees, everybody loves tree, i even see trees just by my window, always was surounded by trees...

hmmHmm

Enough cheap talking, here are the basics of trees - TikZ native:

You got to understand 3 simple rules to get TikZ trees:

- start a tree `\node{NODENAME}`

- a `node` can have `n` childs, written contiguously

- a child synthax is `child{NODE}`

- `node` synthax is `node{NODENAME}`


So a simple tree looks like:

```latex


\begin{tikzpicture}
    \node{N1} child{ node{MM} } child{ node{V2} };
\end{tikzpicture}


```

![tree1.png](../assets/common_files/images_latex/tree1.png)

Look, it's evolving !

```latex


\begin{tikzpicture}

    \node{N1}
        child{ child{node{N2}}  }
        child{
            node{N3}
            node{N4}
                child {
                      node{N5}
                  }
            }
        child {
            node{N6} child {node{N7}} child {node{N8}}
        };

\end{tikzpicture}


```

![tree2.png](../assets/common_files/images_latex/tree2.png)

Not convinced, you are a Haskell fundamentalist and study Graph Theory, and you are asking:

"okok, nice stuff, but i need a more abstract way to represent links between nodes, i want to represent GRAPH!! Nodes that that are linked without an hierarchical order GODAMN !!!"

Wow wow wow, i get it and have exactly the right abstraction model for you!

But you got to use `lualatex` engine to compile to have this feature.

And also import those `graph` package in the preamble (yess, package from graph which is a package from TikZ lol).

```latex


\usegdlibrary{trees} % from graphdrawing
\usegdlibrary{force}
\usegdlibrary{layered}


```

Introducing `\graph`

```latex


\begin{tikzpicture}

    \graph[spring layout]{
        A -- B -- C -- D -- A;
        A -- C;
    };

\end{tikzpicture}


```

![graph1.png](../assets/common_files/images_latex/graph1.png)

You literally just represent the link between nodes.

Here in a tree layout:

```latex


\begin{tikzpicture}

    \graph[tree layout]{
        A -- B -- C -- D -- A;
        A -- C;
    };

\end{tikzpicture}


```

![graph2.png](../assets/common_files/images_latex/graph2.png)

Of course you can make directed graph, or part of graph with `->` or `<-`.

```latex


\begin{tikzpicture}

    \graph[spring layout]{
        A <- B -- C -- D -- A;
        A -> C;
    };

\end{tikzpicture}


```

![graph3.png](../assets/common_files/images_latex/graph3.png)

Or you can make undirected more explicit using `<->`.

```latex


\begin{tikzpicture}

    \graph[spring layout]{
        A <-> B -- C -- D -- A;
        A -> C;
    };

\end{tikzpicture}


```

![graph4.png](../assets/common_files/images_latex/graph4.png)

And going back to trees, you can draw it without pain like.

```latex


\begin{tikzpicture}

    \graph [tree layout] {
        A -> {B, C, D};
        B -> {E, F};
    };

\end{tikzpicture}


```

![tree3.png](../assets/common_files/images_latex/tree3.png)

No `node` / `child` concerns.

##### 3D Tikz Lib

More on that later.

##### booktabs

Tabs, tabs, tabs.

Let's start.

```latex


\begin{tabular}{|c|c|}
\hline
    A & B \\
\hline
    C & D \\
\hline
\end{tabular}


```

![table1.png](../assets/common_files/images_latex/table1.png)

Just defining an appropriate scope for it ( `tabular`), and enter the values:

```latex


|c|c|


```

or it could slightly differe:

```latex


\begin{tabular}{c|c|}
\hline
    A & B \\
\hline
    C & D \\
\hline
\end{tabular}


```

![table2.png](../assets/common_files/images_latex/table2.png)

```latex


\begin{tabular}{c|c}
\hline
    A & B \\
\hline
    C & D \\
\hline
\end{tabular}


```

![table3.png](../assets/common_files/images_latex/table3.png)

You can also color a specific cell using `\cellcolor{COLOR}`

```latex


\begin{tabular}{|c|c|}
\hline
    \cellcolor{red!30} A & B \\
\hline
    C & \cellcolor{blue!30} D \\
\hline
\end{tabular}


```

![table4.png](../assets/common_files/images_latex/table4.png)

Or color an entire row:

```latex


\begin{tabular}{|c|c|}
\hline
    \rowcolor{red!30}
    A & B \\
\hline
    \rowcolor{blue!30}
    C & D \\
\hline
\end{tabular}


```

![table5.png](../assets/common_files/images_latex/table5.png)

Or also column, with `>\columncolor{COLOR}`

```latex


\begin{tabular}{|>{\columncolor{blue!30}}c|>{\columncolor{red!30}}c|}
\hline
    A & B \\
\hline
    C & D \\
\hline
\end{tabular}


```

![table6.png](../assets/common_files/images_latex/table6.png)

You can alternate row color.

So you define:

```latex


\rowcolors{PATTERNLINESTART}{COLOR1}{COLOR2}


```

expanding to:

```latex


\rowcolors{1}{gray!20}{white}


```

for example.

And after just define a normal table:

```latex


\begin{tabular}{|c|c|}
\hline
    A & B \\
\hline
    C & D \\
\hline
    E & F \\
\hline
\end{tabular}


```

Note, you see `\hline`, just an horizontal line that can not be be used elsewhere.

It is not like `\hrule`.

```latex


dfd

\hrule

sfdf

\hrule


```

![hrule.png](../assets/common_files/images_latex/hrule.png)

And after please reset the pattern, to not conflict other codes, such as math matrices as we will see later.

```latex


\rowcolors{0}{}{} % RESET


```

![table7.png](../assets/common_files/images_latex/table7.png)

Another example (full).

```latex


\rowcolors{2}{blue!20}{red!20}

\begin{tabular}{|c|c|}
\hline
    A & B \\
\hline
    C & D \\
\hline
    E & F \\
\hline
    G & H \\
\hline
\end{tabular}

\rowcolors{0}{}{} % RESET


```

![table8.png](../assets/common_files/images_latex/table8.png)

Now, **booktabs**, finally !

It just bring those things:

- `\toprule`
- `\midrule`
- `\bottomrule`

that have better style than `\hline` for respectively:

- top line
- head separation
- botom line

```latex


\begin{tabular}{|cc|}
\toprule
A & B \\
\midrule
C & D \\
\hline
E & F \\
\hline
C & D \\
\hline
E & F \\
\hline
C & D \\
\hline
E & F \\
\hline
C & D \\
\hline
E & F \\
\hline
C & D \\
\hline
E & F \\
\bottomrule
\end{tabular}


```

![table9.png](../assets/common_files/images_latex/table9.png)

Note here the `|cc|` -\> No col separation, kind of weird but possible.

#### Configurations

```latex


%%%%%%% hyperref %%%%%%%
\hypersetup{colorlinks = true,
            linkcolor=blue,
            urlcolor=blue
}
%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%% fancyhdr %%%%%%%

\fancyhf{}
\pagestyle{fancy}

%%% page headers %%%
\fancyhead[L]{Doc}
\fancyhead[R]{J LP}
\fancyfoot[C]{\thepage}
\setlength{\headheight}{15pt}
%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%% titlesec %%%%%%%%%
\titleformat{\section}{\large\bfseries}{\thesection}{1em}{}
%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%% listings configurations %%%%

%\lstset{ % define globally, but risks of flickering
%    basicstyle=\ttfamily\small,
%    keywordstyle=\color{blue},
%    commentstyle=\color{red!70!black},
%    stringstyle=\color{green!50!black},
%    breaklines=true,
%    keepspaces=true,
%    showstringspaces=false,
%    backgroundcolor=\color{gray!50},
%    frame=single
%}

% or define a style variable

\tcbuselibrary{listings}

% no flickering
\newtcblisting{codebox1}{
    listing only,
    colback=gray!5,
    colframe=gray!30,
    arc=4pt,
    boxrule=0.5pt,
    listing options={
        language=C++,
        basicstyle=\ttfamily\small,
        keywordstyle=\color{blue},
        commentstyle=\color{gray},
        stringstyle=\color{green!50!black},
        breaklines=true,
        keepspaces=true,
        columns=fullflexible,
        showstringspaces=false
    }
}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%% minted %%%%%%

\usemintedstyle{friendly}
% friendly
% colorful
% murphy
% native
% monokai

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%% Multi-Column spacing %%%%%%%

\setlength{\columnsep}{1cm}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%% Footnote spacing %%%%%%%

\setlength{\skip\footins}{2em}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\usepgfplotslibrary{fillbetween}
\usepgfplotslibrary{statistics}
% \usepgfplotslibrary{colormaps} %cool theme colormap/themename

\pgfplotsset{compat=1.18}

\pgfplotsset{ %define custom pgfplot theme, heatmap
  colormap={inferno}{
    rgb255(0cm)=(0,0,4);
    rgb255(1cm)=(31,12,72);
    rgb255(2cm)=(85,15,109);
    rgb255(3cm)=(136,34,106);
    rgb255(4cm)=(186,54,85);
    rgb255(5cm)=(227,89,51);
    rgb255(6cm)=(249,140,10);
    rgb255(7cm)=(249,201,50);
    rgb255(8cm)=(252,255,164);
  }
}

\title{Doc}
\author{J LP}
\date{\today}

%%%% VARIABLES REGISTRATION %%%

\newcommand{\mybloglink}{https://julienlargetpiet.tech}
\newcommand{\mybloglinkraw}{\url{https://julienlargetpiet.tech}}

\definecolor{mycolor1}{HTML}{1E90FF}
\definecolor{linkcolor1}{HTML}{4F9AD6}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%% FUNCTIONS REGISTRATION %%%

\newcommand{\link}[2]{\href{#1}{#2}}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\includeonly{ici}

% Declare custom maths operators - symbols
\DeclareMathOperator{\Var}{VarCustom}
\DeclareMathOperator{\E}{ECustom}

%%%%%%%%%%%%%%%%%%%%%%



```

##### Hyperlinks

```latex


\hypersetup{colorlinks = true,
            linkcolor=blue,
            urlcolor=blue
}


```

As you see, here we define the style of the hyperlinks.

1. `colorlinks`

If false (default behavior), then links are surrounded by colored boxes and text stays black.

If true, no boxes and text itself is colored

2. `linkcolor`

Controls internal links:

- table of contents
- `\ref{...}`
- `\section links` \- more on that in `\maketitle` / TOC section
- figure references

Example:

```latex


\ref{fig:myfig}


```

--\> will appear in blue

3. `urlcolor`

Controls external links:

- `\url{...}`
- `\href{...}{...}`

Example:

```latex


\url{https://example.com}


```

The link will appear in blue.

```latex


\href{\mybloglink}{My-blog}

%% OR directly show url
\url{\mybloglink}

% with variable call

\mybloglinkraw

% with function call

\link{\mybloglink}{My-blog}


```

![link1.png](../assets/common_files/images_latex/link1.png)

##### PageStyle

After we define the format of each page, with `fancyhdr` configuration.

```latex


\pagestyle{fancy}

%%% page headers %%%
\fancyhead[L]{Doc}
\fancyhead[R]{J LP}
\fancyfoot[C]{\thepage}
\setlength{\headheight}{15pt}


```

So we define what is displayed at the top-left/header-left 'Doc', what is displayed at the top-right/header-right 'JLP'

And as its name does not suggest it, we can even define what is displayed at the footer.

Then here at the bottom-center, we put `\thepage` which is a special variable that display the current page number.

So you get this style:

![fig1.png](../assets/common_files/images_latex/fig1.png)

Notice the horizontal top line that comes from `\pagestyle{fancy}`

##### Sections

```section


\titleformat{\section}{\large\bfseries}{\thesection}{1em}{}


```

Here an important concept, the sections.

Sections are... sections of your document (wow, sherlock level here)

You can have sections, subsections and subsubsections and more (discussed later)

They are used to create the automatic Table Of Content (TOC), we will return on that later.

But here we just define their style. We want them to be written in `\large` which comes from the LaTeX font size system.

We also want them to use the `\bfseries` font.

##### TOC

How the Table Of Contents is built ?

Like seen before, just using the sections.

But we can choose where to pu here, ususally just after `\begin{document}`, like that:

```latex


{ % here we just do a scoping to define temporary hyperefsetup just used by \tableofcontents
  \hypersetup{linkcolor = black}
  \tableofcontents
}


```

Wow, wait a minute, why is that wrapped inside brackets ???

Simple enough.

In fact, remember this before ?

```latex


\hypersetup{colorlinks = true,
            linkcolor=blue,
            urlcolor=blue
}


```

Yeah, it appears we define the link color...

But do you knwo what is a link to in TOC and that should not be blue ??

Right, TOC itself...

Si in fact we just create a temporary context where we redefine the link color, and just after, in he same context, we **generate** the TOC.

Bom, all links are black, what is intended.

You just learn that LaTeX acts more an more as a "programing language", that's right, **scoping**

![TOC1.png](../assets/common_files/images_latex/TOC1.png)

##### Multicol

This one is straightforward, we spoke about multicol, but how to define column spacing ?

Just.

```latex


\setlength{\columnsep}{1cm}


```

But you get it ?

This demonstration brings a new concept --> **defining a length** !!

Hre it is global for current scope not sub-scope, (a bit subtle), but can be redifined later.

Like with scoping:

```latex


{
    \setlength{\columnsep}{2cm}

    \begin{multicols}{2}
    Content...
    \end{multicols}
}


```

First, here all the existing units, and there are for all, normal educated people unsing metric system.

- `mm` -\> milimiter (of course) -> 1/1000 of a meter
- `cm` -\> centimeter, 1/100 of a meter ;)
- `pt` -\> LaTeX special measurmeent unit (still better than inches)
- `bp` -\> PostScript measurmeent units
- `in` -\> unfortunately

And look:

```text


1in -> 72.27pt
1in -> 72bp


```

Specigic European typography units:

- `dd` -\> Didot point
- `cc` -\> Cicero point

Math units:

- `mu`

special variable describing the dimensions of the curent document page:

- `\textwidth` -\> width of the text area, set once by document type `article...` \+ `geometry`
- `\columnwidth` -\> width of 1 column, normally equals to `\textwidth`, but depends on the context it is called, like in `multicols` / `figures` / `minipage`

And look, we can even do maths with length units with `\dimexpr`:

```latex


\setlength{\parskip}{\dimexpr 1em + 2pt\relax}


```

`\parslip` is the default length between 2 paragraphs.

If you want to cretae you onw dimension, it is possible:

```latex


\newdimen\customdim
\customdim=2cm


```

And after use it:

```latex


\setlength{\parskip}{\dimexpr 2\customdim\relax}


```

or some more math on it:

Ho you can do division with non integer, so instead of:

```latex


\setlength{\parskip}{\dimexpr 2\customdim / 1.5cm + 1cm\relax}


```

do:

```latex


\setlength{\parskip}{\dimexpr 2\customdim*2 / 3 + 1cm\relax}


```

Even in TikZ:

```latex


\draw (0,0) -- (\dimexpr 2\customdim\relax, 0)


```

##### Metadata, informations about the doc

The author, the date and the document title are set like that in the preamble:

```latex


\title{DocYess}
\author{J LP Yess}
\date{\today}


```

![firstpage.png](../assets/common_files/images_latex/firstpage.png)

You see he variabke `\today` performs a system call under the hood asking for the current date (Month Day Year)

##### Includes

Here, we go from one file -> one document to a really structured project to output a ...PDF, yeah !!

Imagine your work is so big it can not fit in one file...

It is surely the worst description to announce the importance of file and folder separation for a project.

But you get it, everyone gets it.

When a project gets so big, we start separating the concerns to different location.

So here it is:

```latex


\include{ici.tex}


```

where `ici.tex` is a normal tex file, not defining an article, but just some tex code that fits inside a Tex document.

```latex


Je suis inclu


```

In the preamble you can define the infamous `\includeonly` list variable like that:

```latex



\includeonly{ici,ici2}


```

To only includes those files for example `ici.tex` and `ici2.tex`.

Then if you do:

```latex


\include{ici.tex}

\include{ici2.tex}


```

But have:

```latex


\includeonly{ici}


```

Only `ici` will be displayed.

Here, even if the content in each included file is just one line, an include will at least take one entire page.

To solve this problem you can just use raw `\input`.

```latex


\input{ici.tex}

\input{ici2.tex}


```

Note: there is no `\inputonly` native concept.

![input.png](../assets/common_files/images_latex/input.png)

## More on basic yet important stuffs

### Internal Links: Citations & References

You saw hyperlink:

-\> someone click on the link and suddenly he is transported in the INTERNET to the websites the link is referencing woow!

But let's do something less fancy.

Just refenrence areas on the same PDF page, still useful when PDF is big right ?

We do it like that:

```latex


\hyperlink{ID}{DISOPLAYTEXT1}
...
\hypertarget{ID}{DISPLAYTEXT2}


```

expanding to for example:

```latex


\hyperlink{citationID1}{my first citation}
...
\hypertarget{citationID1}{Citatttttttion1}


```

Is is very useful for _citations_.

But in LaTeX citations are conceptualy simple but pratically just horrible, we have to use `bibtex` that is a tool that kind of structure your citation, like autmatically increment all the citations id.

But to be fair, that is where LaTeX engineering faled misearably.

WE DO NOT NEED BIBTEX!

_hopefully_

Look at what we can simply do:

```latex


\newcount\citecounter
\citecounter=0

\newcommand{\mycite}[1]{%
  \advance\citecounter by 1
  \edef\temp{\the\citecounter}%
  \hyperlink{#1}{[\temp]}
}



```

So we just use it as:

```latex


\mycite{ID1}

\mycite{ID2}


```

expanding to, for example:

```latex


\mycite{cit1}

\mycite{cit2}


```

![cite1.png](../assets/common_files/images_latex/cite1.png)

And at the end of our document, for instance after a `\newpage`, that creates a newpage (lol):

```latex


\hypertarget{cit1}{Citatttttttion1}

\hypertarget{cit2}{Citatttttttion2}


```

![cite2.png](../assets/common_files/images_latex/cite2.png)

And after that you tell bibtex is not a scam, common !!

We just define a global counter, and define a command/function that will automatically increment this counter when used before using it as a display citation reference with the inputed parameter which is the id `#1` -\> first paramter an only.

In fact you just learn the structure of function in LaTeX:

```text


\newcommand{\FUNCTIONNAME}[NUMBER OF ARGUMENTS]{
  FUNCTION LOGIC
}


```

And you use parameters as `#1`, `#2` ...

### Sections, subsections...

Again again, some basic but unavoidable concepts, the compartimentin of you document by **sections**:

The TOC, with `\maketitle` will lookk to those sections, subsections... to create the TOC.

So you heve:

N1 `\section{TEXT}` containing N2 `\subsection{TEXT}` containing N3 `\subsubsections{TEXT}`.

And iy is not yet the end.

You can even got deeper !!

You can even give more or ess importance to your paragraphs inside sub/subsub/sections, doing so:

```latex


\paragraph{Important paragraph}

A paragraph yeah a paragraph haha, lol i dk what to write here so i rpetend just to write sentences that make sens whil it is pure nonsens.
Comon we do it again
A paragraph yeah a paragraph haha, lol i dk what to write here so i rpetend just to write sentences that make sens whil it is pure nonsens.

\subparagraph{Important sub-paragraph}

A sub-paragraph yeah a sub-paragraph haha, lol i dk what to write here so i rpetend just to write sentences that make sens whil it is pure nonsens.
Comon we do it again
A paragraph yeah a paragraph haha, lol i dk what to write here so i rpetend just to write sentences that make sens whil it is pure nonsens.


```

So an end result can look like that:

```latex


\section{Basics - sections, subsections, paragraphs...}
\subsection{Normal}

Hello Normal

\subsubsection{Normal}

A paragraph yeah a paragraph haha, lol i dk what to write here so i rpetend just to write sentences that make sens whil it is pure nonsens.

\subsubsection{Normal2}

Comon we do it again
A paragraph yeah a paragraph haha, lol i dk what to write here so i rpetend just to write sentences that make sens whil it is pure nonsens.

\paragraph{Important paragraph}

A paragraph yeah a paragraph haha, lol i dk what to write here so i rpetend just to write sentences that make sens whil it is pure nonsens.
Comon we do it again
A paragraph yeah a paragraph haha, lol i dk what to write here so i rpetend just to write sentences that make sens whil it is pure nonsens.

\subparagraph{Important sub-paragraph}

A sub-paragraph yeah a sub-paragraph haha, lol i dk what to write here so i rpetend just to write sentences that make sens whil it is pure nonsens.
Comon we do it again
A paragraph yeah a paragraph haha, lol i dk what to write here so i rpetend just to write sentences that make sens whil it is pure nonsens.


```

![section1.png](../assets/common_files/images_latex/section1.png)

![section2.png](../assets/common_files/images_latex/section2.png)

You find it at the TOC level here:

![section3.png](../assets/common_files/images_latex/section3.png)

#### Paragraphs

Hmmm, lol more than 2K lines and we have not talked about the most basic thing, the textual representation model of LaTeX, basically:

```latex


This is a sentence.

This is another a sentence.


```

![par1.png](../assets/common_files/images_latex/par1.png)

```latex


This is a sentenceinside a par.
This is a sentence inside a par.


```

![par2.png](../assets/common_files/images_latex/par2.png)

```latex


This is a sentenceinside a par too. This is a sentence inside a par too.


```

![par4.png](../assets/common_files/images_latex/par4.png)

\* **This is not like HTML, it is more visual than it**

It is more like markdown for this particular concept.

Also more space is not equal more space...

```latex


This is a sentenceinside a par.
This is a sentence inside a par.

This is a sentenceinside a par too. This is a sentence inside a par too.


```

![par5.png](../assets/common_files/images_latex/par5.png)

You can break a paragraph with `\\`.

```latex


This is a sentenceinside a par too.\\ This is a sentence inside a par too.


```

![par6.png](../assets/common_files/images_latex/par6.png)

Or same:

```latex


This is a sentenceinside a par too.
\\
This is a sentence inside a par too.


```

![par7.png](../assets/common_files/images_latex/par7.png)

And you can double break it like so:

```latex


This is a sentenceinside a par too. \\

This is a sentence inside a par too.


```

![par8.png](../assets/common_files/images_latex/par8.png)

Or same:

```latex


This is a sentenceinside a par too. \\

This is a sentence inside a par too.


```

![par9.png](../assets/common_files/images_latex/par9.png)

But you can break only what can be broke (wow, neat sentence):

```latex


This is a sentenceinside a par too.

\\

This is a sentence inside a par too.


```

-\> ERROR

But look at this weird thing:

```latex


This is a sentenceinside a par too. \\ \\ \\
This is a sentence inside a par too.

Separation

This is a sentenceinside a par too. \\ \\ \\ \\
This is a sentence inside a par too.


```

![par10.png](../assets/common_files/images_latex/par10.png)

Why does it work as intended ??

Because `\\` is allowed inside a paragraph, but not outside

That is why this worked:

```latex


This is a sentenceinside a par too.
\\
This is a sentence inside a par too.


```

Because remmber:

```latex


sentence1
sentence2


```

Are the **same** paragraph :)

Also `\\` does not realy give the same amount of spaces than natural paragraphs separation, so:

```latex


sentence1

sentence2


```

Gives `\parskip` separation length. -> Annouces **another** paragraph.

Not like

```latex


sentence1 \\
sentence2


```

Gives `\baselineskip` -\> Typographic spacing but actually in the **same** paragraph.

So recall that:

**Blank line -> NEW PARAGRAPH**

### Spaces

#### Vertical

This is straightforward, just:

```latex


\vspace{LENGTH}


```

So like:

```text


Ok

\vspace{1cm}

Ok


```

![vpsace1.png](../assets/common_files/images_latex/vspace1.png)

Note that this does not work because on the same paragraph:

```latex


Ok
\vspace{1cm}
Ok


```

Or

```latex


Ok \vspace{1cm} Ok


```

![vpsace2.png](../assets/common_files/images_latex/vspace2.png)

#### Horizontal

This is as straightforward as vertical spaces.

```latex


Ok \hspace{1cm} Ok


```

![hpsace1.png](../assets/common_files/images_latex/hspace1.png)

Ans for the next paragraph, the horizontal space is of course canceled.

```latex


Ok \hspace{1cm} Ok

Ok


```

![hpsace2.png](../assets/common_files/images_latex/hpace2.png)

### Text style

##### Bold

Just:

```latex


\textbf{Hello in bold}


```

![bf.png](../assets/common_files/images_latex/bf.png)

##### Italic

```latex


\textit{Hello in italic}


```

![it.png](../assets/common_files/images_latex/it.png)

##### Underline

```latex


\underline{Hello underlined}


```

![und.png](../assets/common_files/images_latex/und.png)

##### Combinations of style

```latex


\underline{\textbf{\textit{Hello all}}}


```

![stylecomb.png](../assets/common_files/images_latex/stylecomb.png)

### Font Sizes

#### Predefined font sizes

LaTeX is generous and comes with predefined variable you can use to tweak font sizes.

```latex


{\tiny tiny}

{\footnotesize footnotesize}

{\small small}

{\normalsize normalsize}

{\large large}

{\Large Large}

{\huge huge}

{\Huge Huge}


```

![fsize1.png](../assets/common_files/images_latex/fsize1.png)

Note that i always scoped the call of changing tthe font size because one call of any of those macros affects the rest of the text.

Look an example:

```latex


\tiny tiny

\normalsize

Mee

\footnotesize footnotesize

\normalsize

Mee

\small small

\normalsize

Mee

\normalsize normalsize

Mee

\large large

\normalsize

Mee

\Large Large

\normalsize

Mee

\huge huge

\normalsize

Mee

\Huge Huge

\normalsize

Mee



```

![fsize2.png](../assets/common_files/images_latex/fsize2.png)

Because look if i had not did it:

```latex


\tiny tiny

Mee

\footnotesize footnotesize

Mee

\small small

Mee

\normalsize normalsize

Mee

\large large

Mee

\Large Large

Mee

\huge huge

Mee

\Huge Huge

Mee

\normalsize


```

![fsize3.png](../assets/common_files/images_latex/fsize3.png)

##### Custom font sizes

So a fontsize is defined by those 2 variables:

- `size` -\> actual size of the font
- `baselineskip` -\> the infamous `\\` value

So we do a scoping like that:

```latex


{\fontsize{FONTSIZE}{BASELINESKIPSIZE}\selectfont
This is a sentence with my custom font !!!
}


```

exapnding to for example:

```latex


{\fontsize{14pt}{18pt}\selectfont
This is a sentence with my custom font !!!
}


```

So you get that this:

`\fontsize{FONTSIZE}{BASELINESKIPSIZE}` -\> prepares the font, sets the configuration, and the call to `\selectfont` actually activate the font for the next texts.

### FootNotes

Just:

```latex


CONTENT1\footnote{DEFINITION1}

CONTENT2\footnote{DEFINITION2}


```

expanding to, for example:

```latex


Hell0\footnote{this is a first footnote}

Hell02\footnote{this is a second footnote}


```

![footnote1.png](../assets/common_files/images_latex/footnote1.png)

And at the bottom of the page, the associated definitions:

![footnote2.png](../assets/common_files/images_latex/footnote2.png)

### Lists

#### Unnumbered

We do unordered lists with `itemize` context.

```latex


\begin{itemize}
    \item First
    \item Second
\end{itemize}


```

![list1.png](../assets/common_files/images_latex/list1.png)

#### Numbered

```latex


\begin{enumerate}
    \item First
    \item Second
\end{enumerate}


```

![list2.png](../assets/common_files/images_latex/list2.png)

### Horizontal Lines

Very direct:

```latex


dfd

\hrule

sfdf

\hrule


```

![hrule1.png](../assets/common_files/images_latex/hrule1.png)

### Maths

Hoooo, now we enter the section that was the motivation for the creation of TeX

To have special maths notations, special math font etcetera etcetera.

This is the maths you put inside normal text:

```latex


here some inlined maths $f(x) = x^2$


```

![math1.png](../assets/common_files/images_latex/math1.png)

Here you see that to declare an exponent, we do `^` -\> very common.

Now when we want to grat the honors to maths, we need to center it right ?

That's done with:

```latex


\[
 MATHS HERE
\]


```

expanding to, for example:

```latex


\[
f(x) = x^2
\]


```

![math2.png](../assets/common_files/images_latex/math2.png)

Now, more about notations:

```latex


\[
x^2,\quad x_1,\quad x^{10},\quad x_{i,j}
\]


```

![math3.png](../assets/common_files/images_latex/math3.png)

Wait, what's going on here ??

First, what are `\quad` ??

They are simple horizontal spaces, from a greater family of horizontal spaces in **math mode** that we'll encounter later.

Juts to tell you that we can have indices with `_`

And if we want to make the exponent or indices more complex, make sure to scope them with `{}`.

That's why we got:

```latex


x_{i,j}


```

For example

A multiplication is expressed with `\cdot`.

```latex


\[
  3 \cdot 2 + 1 - 1 = 6
\]


```

![math4.png](../assets/common_files/images_latex/math4.png)

Fractions now:

```latex


\[
    \frac{DIVIDED}{DIVIDER}
\]


```

expanding to, for example:

```latex


\[
    \frac{a}{b}
\]


```

![math5.png](../assets/common_files/images_latex/math5.png)

You want some integrals ?

```latex


\int_START^END


```

here `^` is not an exponent, but rather meaning "to"

So, for example, it expands to:

```latex


\[
    \int_0^1 x^2 \, dx
\]


```

![math6.png](../assets/common_files/images_latex/math6.png)

OR

```latex


\[
    \int_{0}^{\frac{a}{b}} x^2 \, dx
\]


```

![math7.png](../assets/common_files/images_latex/math7.png)

`\int` -\> not like type but as abreviation for "integral" :)

Now Sum ;)

```latex


\[
    \sum_{i=1}^{n} i^2
\]


```

![math8.png](../assets/common_files/images_latex/math8.png)

Same semantics...

Now some limits, yeahhh !!

```latex


\[
    \lim_{x \to \infty} \frac{1}{x} = 0
\]


```

![math9.png](../assets/common_files/images_latex/math9.png)

And what about parenthesis ?

That comes with `\left` and `\right`.

```latex


\[
    \left( \frac{1}{2} \right)
\]

\[
    \left[ \frac{1}{2} \right]
\]


```

![math10.png](../assets/common_files/images_latex/math10.png)

You see, we announce the parenthesis with either `\left` or `\right`, and after we put the symbol "(", ")", "\[" or "\]".

What would be math without matrices ?

We certianly would not have linear algebra as we know today, what an horror right ??

So here we are, matrices:

```latex


\[
\begin{matrix}
    1 & 2 \\
    3 & 4
\end{matrix}
\]


```

![math11.png](../assets/common_files/images_latex/math11.png)

With parenthesis ;)

```latex


\[
\begin{pmatrix}
    1 & 2 \\
    3 & 4
\end{pmatrix}
\]


```

![math12.png](../assets/common_files/images_latex/math12.png)

Now with "\[".

```latex


\[
\begin{bmatrix}
    1 & 2 \\
    3 & 4
\end{bmatrix}
\]


```

![math12B.png](../assets/common_files/images_latex/math12B.png)

Or you can do it manualy, but seriously ??

```text


\[
\left(
\begin{matrix}
    1 & 2 \\
    3 & 4
\end{matrix}
\right)
\]

\[
\left[
\begin{matrix}
    1 & 2 \\
    3 & 4
\end{matrix}
\right]
\]


```

![math13.png](../assets/common_files/images_latex/math13.png)

Oh, almost forgot, but you can make them with bars too:

```latex


\[
\begin{vmatrix}
    1 & 2 \\
    3 & 4
\end{vmatrix}
\]


```

![math14.png](../assets/common_files/images_latex/math14.png)

and its manual equivalent...

```latex


\[
\left|
\begin{matrix}
    1 & 2 \\
    3 & 4
\end{matrix}
\right|
\]


```

![math15.png](../assets/common_files/images_latex/math15.png)

Now, speaking about equations developmenent !!

A great environment to develop an equation is the `align` environment.

```latex


\begin{align}
f(x) &= x^2 + 1 \\
     &= (x+1)(x-1) + 2
\end{align}


```

![math16.png](../assets/common_files/images_latex/math16.png)

You see each development is numbered at the right, very practical !

Now conditional outputs from function, youpi, algorithms ;)

The environment we use is called `cases`, explicit enough, each line is apossible output.

Like:

```latex


\[
f(x) =
\begin{cases}
    OUTPUT1 & CONDITION1 \\
    OUTPUT2 & CONDITION2 \\
    ...
    ...
    ...
\end{cases}
\]


```

expanding to, for example:

```latex


\[
f(x) =
\begin{cases}
    x^2 & \text{if } x > 0 \\
    x & \text{if } x == 2 \\
    0 & \text{otherwise}
\end{cases}
\]


```

![math17.png](../assets/common_files/images_latex/math17.png)

It now brings the text inside math context, it is the contrary as `$some maths$` in text mode.

And as already described it is using `\text{...}`:

```latex


\[
x^2 \text{ is positive}
\]


```

![math18.png](../assets/common_files/images_latex/math18.png)

There are also many horizontal spacing commons we can use:

Small:

```latex


\[
x^2 \, x
\]


```

Just `\,`

![math19.png](../assets/common_files/images_latex/math19.png)

Medium:

```latex


\[
x^2 \; x
\]


```

Just `\;`

![math20.png](../assets/common_files/images_latex/math20.png)

Large:

```latex


\[
x^2 \quad x
\]


```

Just `\quad`

![math21.png](../assets/common_files/images_latex/math21.png)

Would you mind take some maths symbols ?

I'll assume, "YES"

```latex


\begin{align}
\alpha, \beta \\
\lambda, \pi
\end{align}


```

![math22.png](../assets/common_files/images_latex/math22.png)

Note, for whatever reason i used `align` environment, i do random stuff sometimes...

And for number theorists, you will love those:

```latex


\begin{align}
\mathbb{N}, \mathbb{R} \\
\mathbb{Q}, \mathbb{Z}
\end{align}


```

![math23.png](../assets/common_files/images_latex/math23.png)

Some derivatives, with `\partial`

```latex


\[
\frac{\partial f}{\partial x}
\]


```

![math24.png](../assets/common_files/images_latex/math24.png)

You can also box maths !

EMPHASING TIIIME, with `\boxed{SOMEMATHS}`

```latex


\[
\boxed{E = mc^2}
\]


```

![math25.png](../assets/common_files/images_latex/math25.png)

Technically, it work even in normal context, not only in math mode:

```latex


\boxed{BOOOOXE}


```

![math26.png](../assets/common_files/images_latex/math26.png)

And finally, you can even define your custom maths symbols in the prembule doing so:

```latex


\DeclareMathOperator{VARIABLENAME1}{CONTENT}
\DeclareMathOperator{VARIABLENAME2}{CONTENT}


```

expanding to, for example:

```latex


\DeclareMathOperator{\Var}{VarCustom}
\DeclareMathOperator{\E}{ECustom}


```

Now we can use them like any other symbol.

```latex


\[
\Var(X), \quad \E[X]
\]


```

![math27.png](../assets/common_files/images_latex/math27.png)

### Structure

#### fbox & makebox

First, `\makebox[...]{...}`, what is it ?

Think of it like a div n HTML.

You can stack them and they will appear stacked to the right.

Look:

```latex


\makebox[5cm][l]{Hello}
\makebox[5cm][c]{Hello}
\makebox[5cm][r]{Hello}


```

![box1.png](../assets/common_files/images_latex/box1.png)

Ho, maybe you do not see it yet, so i will wrap them inside `\fbox{...}`.

```latex


\fbox{\makebox[5cm][l]{Hello}}
\fbox{\makebox[5cm][c]{Hello}}
\fbox{\makebox[5cm][r]{Hello}}


```

![box2.png](../assets/common_files/images_latex/box2.png)

Here you see !

So you can control the centering, left ( `l`) center ( `c`) or right ( `r`) in the second option context of the `\makebox`

And also the width in the first option context.

Here what it does if i increase it on an A4 type document.

```latex


\makebox[8cm][l]{Hello}
\makebox[8cm][c]{Hello}
\makebox[8cm][r]{Hello}


```

![box3.png](../assets/common_files/images_latex/box3.png)

You may ask why not all in 1 option context like `[]`.

That is a good question that i also asked !

Because here that is just `[opt1][opt2]`.

Which is TeX desing, the foundation of LaTeX.

TeX was developped in the 1970s, so at this time we even should think not only in term of runtime cost, but also COMPILE costs.

And guess what, a simple parsing like `[opt1][opt2]` is way less compute intensive than something non positional like `[opt1=..., opt2=...]` that can be `[opt2=..., opt1=...]` etcetera...

So yeah in LaTeX, you will still see some legacy TeX functions that have this design haha.

Hoo alsmost forgot, of course you are not forced to put boxes on the same paragraph lol:

```latex


\fbox{\makebox[5cm][l]{Hello}}

\fbox{\makebox[5cm][c]{Hello}}

\fbox{\makebox[5cm][r]{Hello}}


```

![box4.png](../assets/common_files/images_latex/box4.png)

#### Minipage

It is a bit lie multicol, but in a greater way.

Let me explain.

In fact in multicol, it as very easy to use, but you could just integrated text, now in minipage, you can also integrate figures, like TikZ pictures...

```latex


\begin{minipage}{0.48\textwidth}

\lipsum[1]

\end{minipage}
\hfill
\begin{minipage}{0.48\textwidth}

    \centering
    \includegraphics[width=0.35\textwidth]{lynxcute.jpg}

    %\vspace{1cm}
    \bigskip

    \begin{tikzpicture}
    \begin{axis}

        \addplot{x^2};

    \end{axis}
    \end{tikzpicture}

\end{minipage}


```

![minipage.png](../assets/common_files/images_latex/minipage.png)

What's going on here ?

We just define a first minipage environment!

```latex


\begin{minipage}{0.48\textwidth}

\lipsum[1]

\end{minipage}


```

With a width of 48% of the total page width.

where we put some text from lipsum.

After that we, on the same paragraph, make a call to `\hfill`, we'll discuss after what it is doing currently.

And, again, on the same paragraph, we define a second minipage environment of also 48% of total page width.

Where we put a picture and a plot.

```latex


\begin{minipage}{0.48\textwidth}

    \centering
    \includegraphics[width=0.35\textwidth]{lynxcute.jpg}

    \bigskip

    \begin{tikzpicture}
    \begin{axis}

        \addplot{x^2};

    \end{axis}
    \end{tikzpicture}

\end{minipage}


```

So technically, 4% of width space reminds, that is why between those 2 minipage environment, we introduced `\hfill` that fills the remaining spaces, in theis case 4% of width sae between those 2 minipage environments.

## More on PGFPlot

So we'll start where we lastly end the discussion on PGFPlot.

### BarPlot

Lets's talk about barplot.

here an example:

```latex


\begin{tikzpicture}
\begin{axis}[
    ybar,
    symbolic x coords={A,B,C},
    xtick=data
]

    \addplot coordinates {
        (A,10)
        (B,3)
        (C,15)
    };

\end{axis}
\end{tikzpicture}


```

![barplot1.png](../assets/common_files/images_latex/barplot1.png)

So you notice that we must precise the type of the plot directly in the axis, here it is a barplot, it will show bar, vertically, so we just put `ybar`.

Because that is a plotbar, so that is quantitative values over qualitative ones, we must tell the axis, the qualitative values, in order.

Here it is `symbolic x coords={A,B,C}`, note that that is all the set containing all the possible qualitative values we have in `coordinates`.

After we do this `xtick=data`.

Why ?

Because default tick accuracy is maybe like 0 -> 0.5 -> 1 -> 1.5 ...

Then, ok at this point it knows it whould use set (1,B,C) to name ticks but at what accuracy ??

Look what hapens if we do not provide this option:

```latex


\begin{tikzpicture}
\begin{axis}[
    ybar,
    symbolic x coords={A,B,C}
]

    \addplot coordinates {
        (A,10)
        (B,3)
        (C,15)
    };

\end{axis}
\end{tikzpicture}


```

![barplot2.png](../assets/common_files/images_latex/barplot2.png)

In fact it does this:

- get the default x interval, let's say \[0, 2\]

- then gets all the symbolic coords -> A,B,C

- interpolate xtick naming, and map it


So it is like undefined behaviour a bit, but here we see it did:

0 -> A

0.5 -> ?

1 -> B

1.5 -> ?

2 -> C

And replaced the "?" with interpolated qualitative value.

Haa let's do another try with a much bigger set of qualitative values and get the interpolation.

```latex


\begin{tikzpicture}
\begin{axis}[
    ybar,
    symbolic x coords={A,B,C,D,E,F,G,H,I,J}
]

    \addplot coordinates {
        (A,10)
        (B,3)
        (C,15)
        (D,10)
        (E,3)
        (F,15)
        (G,10)
        (H,3)
        (I,15)
        (J,15)
    };

\end{axis}
\end{tikzpicture}


```

![barplot3.png](../assets/common_files/images_latex/barplot3.png)

Okok weird, but still interpolation, we just do not see the full accuracy.

Also look at that, if a value is not used but still defined in the possible `symbolic x coords`, it is not used in graph.

```latex


\begin{tikzpicture}
\begin{axis}[
    ybar,
    symbolic x coords={A,B,C,D,E,F,G,H,I,J}
]

    \addplot coordinates {
        (A,10)
        (B,3)
        (C,15)
    };

\end{axis}
\end{tikzpicture}


```

![barplot4.png](../assets/common_files/images_latex/barplot4.png)

Here with CSV -> `table`:

```latex


\begin{tikzpicture}
\begin{axis}[
    ybar,
    symbolic x coords={A,B,C},
    xtick=data
]

    \addplot[color=blue!50,
             fill=blue!50] table[col sep=comma,
                                 x=label,
                                 y=value] {barplot.csv};

\end{axis}
\end{tikzpicture}


```

barplot.csv:

```text


label,value
A,10
B,3
C,15


```

![barplot5.png](../assets/common_files/images_latex/barplot5.png)

Now horizontal barplot, you may have guessed it, we'll just use `xbar`.

And change to `symbolic y coords` and `ytick=data` and change tabel parameters in consequence.

```latex


\begin{tikzpicture}
\begin{axis}[
    xbar,
    symbolic y coords={A,B,C},
    ytick=data
]

    \addplot[color=blue!50,
             fill=blue!50] table[col sep=comma,
                                 y=label,
                                 x=value] {barplot.csv};

\end{axis}
\end{tikzpicture}


```

![barplot6.png](../assets/common_files/images_latex/barplot6.png)

Now, how to display groups ?

It is a grouped barplot !!

```latex


\begin{tikzpicture}
\begin{axis}[
    ybar,
    symbolic x coords={A,B,C},
    xtick=data,
    enlargelimits=0.15
]

    \addplot[color=blue!50,
             fill=blue!50] coordinates {
        (A,10)
        (B,3)
        (C,15)
    };

    \addplot[color=mycolor1,
             fill=mycolor1] coordinates {
        (A,4)
        (B,8)
        (C,5)
    };

    \addplot[color=red!50,
             fill=red!50] coordinates {
        (A,14)
        (B,18)
        (C,15)
    };

    \node at (axis cs:A,14) [above] {Point 1};
    \node at (axis cs:B,18) [above] {Point 2};
    \draw[->] (axis cs:B,18) -- (axis cs:C,15) node[below] {Point 3};

\end{axis}
\end{tikzpicture}


```

![barplot7.png](../assets/common_files/images_latex/barplot7.png)

You literally just add more `\addplot` and change colors.

Here i just added some node anotations for fun haha, i like having fun doi some random stuff...

Btw, note that `enlargelimits` ?

Look what happens at default `enlargelimuts`, default to 0.

```latex


\begin{tikzpicture}
\begin{axis}[
    ybar,
    symbolic x coords={A,B,C},
    xtick=data,
    enlargelimits=0
]

    \addplot[color=blue!50,
             fill=blue!50] coordinates {
        (A,10)
        (B,3)
        (C,15)
    };

    \addplot[color=mycolor1,
             fill=mycolor1] coordinates {
        (A,4)
        (B,8)
        (C,5)
    };

    \addplot[color=red!50,
             fill=red!50] coordinates {
        (A,14)
        (B,18)
        (C,15)
    };

    \node at (axis cs:A,14) [above] {Point 1};
    \node at (axis cs:B,18) [above] {Point 2};
    \draw[->] (axis cs:B,18) -- (axis cs:C,15) node[below] {Point 3};

\end{axis}
\end{tikzpicture}


```

![barplot8.png](../assets/common_files/images_latex/barplot8.png)

That's right, awful interval cutting !!

So we just provides some breathing space for each plot, it increses height breathing space, we do not care but why not, but especially width space for each plot, which we care about to have good plots !

Yess that is something weird about PGFPlot engine...

And here an horizontal grouped barplot.

```latex


\begin{tikzpicture}
\begin{axis}[
    xbar,
    symbolic y coords={A,B,C},
    ytick=data,
    enlargelimits=0.15
]

    \addplot[color=blue!50,
             fill=blue!50] coordinates {
        (10,A)
        (3,B)
        (15,C)
    };

    \addplot[color=mycolor1,
             fill=mycolor1] coordinates {
        (4,A)
        (8,B)
        (5,C)
    };

    \addplot[color=red!50,
             fill=red!50] coordinates {
        (14,A)
        (18,B)
        (15,C)
    };

\end{axis}
\end{tikzpicture}


```

![barplot9.png](../assets/common_files/images_latex/barplot9.png)

Also, note tha because we shifted to horizontal barlot, the coordinates are shifted.

So instead of `(A,10)` we got `(10,A)` and so on.

### Histogram

Here we want to represent quantitative values over quantitatives values.

More precisely density over quantitives values.

Maybe like Probability Density Function (PDF lol, i crack some jokes sometimes).

here is the file, histogramm.csv:

```text


value
1
2
2
2.5
3
3.5
3.6
3.6
4
4
5
6
7


```

And an example.

```latex


\begin{tikzpicture}
\begin{axis}

    \addplot[
        hist={bins=5, data min=1, data max=7, density},
        fill=blue!30,
        draw=black,
    ] table[col sep=comma,
            y=value] {histogramm.csv};

\end{axis}
\end{tikzpicture}


```

![hist1.png](../assets/common_files/images_latex/hist1.png)

What is going on here ?

The sum of the area of the bins is equal to 1.

With `density` option, all is normalized between 0 and 1.

We got some bars, but nothing requires modifying the axis options, why is that ?

Because of course it is quantitatives over quantitatives.

So do not even try defining a set of possible values at x axis, it is impossible, there are an infinity.

For that the `\addplot` has a very special option, as you may have spotted, the `hist`.

What's in that ?

You just tell the number of `bins` -\> represnet the accuracy, not too many, because it will flatten, not not enough -> loose of accuracy

`data min` \- `data max` represents the x interval, here it is not defined directly in axis environment option, but directly via this option.

Why we do like that ?

Because that s the most predictable and accurate way, look again the histogramm.csv file, there is no notion of x values here, just y values, so using this hist options is the right way to do it, it fixes boudaries for compute !

Here, we draw bins lines in black `draw=black`.

and of course, you can add Kernel Density Estimation (KDE, i got no joke here sadly... :( ).

```latex


\begin{tikzpicture}
\begin{axis}

    \addplot+[
        hist={bins=5, data min=1, data max=7, density},
        fill=blue!30,
        draw=black,
        mark=none
    ] table[col sep=comma,
            y=value] {histogramm.csv};

    \addplot[
        smooth, thick, color=red
    ] table[
        col sep=comma, x=x, y=density
    ]{histogramm_kde.csv}; % never escapes "_" in filenames, only in text where we do "\_"

\end{axis}
\end{tikzpicture}


```

![hist2.png](../assets/common_files/images_latex/hist2.png)

That is very manual, just adding a smooth plot from a precomputed KDE file values (with R or Python).

histogramm\_kde.csv:

```text


x,density
1.5,0.230769230769231
2.5,0.153846153846154
3.5,0.384615384615385
4.5,0.0769230769230769
5.5,0.0769230769230769
6.5,0.0769230769230769


```

### Constant plot

Good way to display Cumulative Probability Distribution for example.

cnst.csv

```text


x,y
0,0.1
0.1,0.15
0.2,0.5
0.3,0.62
0.4,0.66
0.5,0.68
0.6,0.75
0.7,0.8
0.8,0.88
0.9,0.95
1,1


```

Code.

```latex


\begin{tikzpicture}
\begin{axis}

    \addplot[const plot,
             mark=square*,
             color=blue]
      table [col sep=comma, x=x, y=y] {cnst.csv};

\end{axis}
\end{tikzpicture}


```

![cnst1.png](../assets/common_files/images_latex/cnst1.png)

`const plot` is in fact just expanded to a bunch of options.

Internaly it does something like that.

```text


(1,2)
(2,3)
(3,1)


```

```text


(1,2)
(2,2)
(2,3)
(3,3)
(3,1)


```

And link those points with straingt line.

Thats all.

#### pgfplotsset

Look we can declare our own options name !

Here we wrapp `const plot` and add other options.

```latex


\begin{tikzpicture}
\begin{axis}

    \pgfplotsset{
        STYLENAME/.style={
            STYLE1,
            STYLE2,
            ...
            ...
            ...
        }
    }

    \addplot[my step plot]
    table [col sep=comma, x=x, y=y] {cnst.csv};

\end{axis}
\end{tikzpicture}



```

expanding to, for example:

```latex


\begin{tikzpicture}
\begin{axis}

    \pgfplotsset{
        my step plot/.style={
            const plot,
            mark=*,
            color=blue,
            thick
        }
    }

    \addplot[my step plot]
    table [col sep=comma, x=x, y=y] {cnst.csv};

\end{axis}
\end{tikzpicture}


```

![pgfplotsset1.png](../assets/common_files/images_latex/pgfplotsset1.png)

We will discuss more about `pgfplotsset` and TikZ equivalent later.

### BoxPlots

BoxPlots are used to display Quantiles - Q1, median, Q3 and outliers, no surprise the default is horizontal, like for the hisogramm (representing for example Probability Density Function), but here, Quantiles...

```latex


\begin{tikzpicture}
\begin{axis}

    \addplot[
        boxplot
    ] table[col sep=comma,
            y=value] {boxplot.csv};

\end{axis}
\end{tikzpicture}


```

![boxplot1.png](../assets/common_files/images_latex/boxplot1.png)

boxplot.csv

```text


value
1
2
2
3
4
4
5
6
7


```

Here you see that some values have different occurences.

Btw, same story as `hist` here but with `boxplot`.

And there is no `density` option, their purpose diverges here.

Here some grouped horizontal boxplots.

```latex


\begin{tikzpicture}
\begin{axis}[
        ytick={1,2,3},
        yticklabels={A,B,C}
    ]

    \addplot[
        boxplot,
        boxplot/draw position=1,
        fill=blue!20
    ] table[col sep=comma,
            y=value] {boxplot.csv};

    \addplot[
        boxplot,
        boxplot/draw position=2,
        fill=red!20
    ] table[col sep=comma,
            y=value] {boxplot.csv};

    \addplot[
        boxplot,
        boxplot/draw position=3,
        fill=orange!20
    ] table[col sep=comma,
            y=value] {boxplot.csv};

\end{axis}
\end{tikzpicture}


```

![boxplot2.png](../assets/common_files/images_latex/boxplot2.png)

Hooooo, what am i seeiiing ????

Yess, we can in fact define ticks accuracy `ytick={1,2,3}` \- for example, could be anything evenly spaced, i omited this point earlier....

And by doing that, we can easily labelize it, mapping them to names.

Doing so:

```latex


yticklabels={A,B,C}


```

- 1 -> A
- 2 -> B
- 3 -> C

Youpiiii !

And the infamous addplot option:

```latex


boxplot/draw position=N


```

where N is one value of `ytick`

Map them to the plot.

Here at y = 1, we got the blue one, at y = 2, the red one and finally at y=3, the orange one.

Now, some vertical boxplots, more common.

```latex


\begin{tikzpicture}
\begin{axis}[
        xtick={1,2,3},
        xticklabels={A,B,C}
    ]

    \addplot[
        boxplot,
        boxplot/draw direction=y,
        boxplot/draw position=1,
        fill=blue!20
    ] table[col sep=comma,
            y=value] {boxplot.csv};

    \addplot[
        boxplot,
        boxplot/draw direction=y,
        boxplot/draw position=2,
        fill=red!20
    ] table[col sep=comma,
            y=value] {boxplot.csv};

    \addplot[
        boxplot,
        boxplot/draw direction=y,
        boxplot/draw position=3,
        fill=orange!20
    ] table[col sep=comma,
            y=value] {boxplot.csv};

\end{axis}
\end{tikzpicture}


```

![boxplot3.png](../assets/common_files/images_latex/boxplot3.png)

Same semantics, we just invert axis, relacing `ytick` by `xtick` and so on...

And most importantly we add the option `boxplot/draw direction=y` -\> Make them vertical.

### Pie Chart

Approximately the same goal as barplot...

Look:

```latex


\begin{tikzpicture}
    \pie[
        color={blue!20, red!20,purple!20},
        text=inside
    ] {10/A, 35/B, 15/C}
\end{tikzpicture}


```

![pie1.png](../assets/common_files/images_latex/pie1.png)

So, that's done with `\pie`.

You see ?

- It is not anymore in an `axis` environment, because in fact there is no axis, that is just a shape...

- We just map color to the proportions.


such as:

```latex


color={blue!20, red!20, purple!20},


```

maps to:

```latex


{10/A, 35/B, 15/C}


```

The whole default annotations text are A/PERCENTAGE, B/PERCENTAGE and so on...

We deliberately put in inside what's called text, That is A, B, C.

If we have not, with `text=pin`:

```latex


\begin{tikzpicture}
    \pie[
        color={blue!20, red!20,purple!20},
        text=pin,
        explode=0.1
    ]{10/A, 35/B, 55/C}
\end{tikzpicture}


```

![pie2.png](../assets/common_files/images_latex/pie2.png)

Hoo of course, you just noted that we can draw incomplete circles, the first was just 10+35+15 = 60 % of a tour -> 1Pi + 10%PI

But here the second is complete because 10 + 35 + 55 = 100% -> whole tour -> 2Pi !

Also note that we can emphase each part with `explode=0.1`, that is a value approximately "detaching" each part more and more when they get bigger.

In fact it is more like, if 2 parts are big -> they will look more far appart than 2 small parts.

You guess what triggers me ??

`\pie` does not support `table`, what a shame !!! BHOOOOOO!!

We can not do the following:

```latex


\begin{tikzpicture}

    \pie[
        color={blue!20, red!20,purple!20},
        text=pin,
        explode=0.1
    ] table[col sep=comma, label=label, value=value] {pie.csv}

\end{tikzpicture}


```

-\> ERROR

BHOOOOO!!! _Again_

So at this point, and it is very common in latex, we have to pull up an external scripting language like Python or Bash to generate the LaTeX Code and put it in an include or input Tex File... Sadly.

But hopefully, pie charts often does not represent much qualitative values ;)

### Multi Kind Plots - overlayed

What about plotting different kind of plot together, that could be useful in a barplot for example, when we also want to represent the mean of each plot at each value.

```latex


\begin{tikzpicture}
\begin{axis}[
    ybar,
    symbolic x coords={A,B,C},
    xtick=data,
    enlargelimits=0.2,
    bar width=10pt,
    ymin=0
]

    \addplot[fill=blue!50] coordinates {(A,10) (B,3) (C,15)};
    \addplot[fill=orange!70] coordinates {(A,4) (B,8) (C,5)};
    \addplot[fill=red!50] coordinates {(A,14) (B,18) (C,15)};

    \addplot[
        blue,
        thick,
        mark=*,
        smooth
    ] coordinates {
        (A,9.33)
        (B,9.67)
        (C,11.67)
    };

    \addplot[
        orange,
        thick,
        mark=*,
        smooth
    ] coordinates {
        (A,8.33)
        (B,9.07)
        (C,10.67)
    };

    \addplot[
        red,
        thick,
        mark=*,
        smooth
    ] coordinates {
        (A,8.93)
        (B,7.07)
        (C,12.67)
    };

\end{axis}
\end{tikzpicture}


```

![multiplot1.png](../assets/common_files/images_latex/multiplot1.png)

Here, that's done with the:

```latex


\addplot[
    blue,
    thick,
    mark=*,
    smooth
] coordinates {
    (A,9.33)
    (B,9.67)
    (C,11.67)
};
...
...
...


```

Look, thanks to `symbolic x coords` we can use them as real x coordinates:

```latex


coordinates {
    (A,9.33)
    (B,9.67)
    (C,11.67)
}


```

Hmmm, and what about plotting in batch, the evolutions of values, yess, that is for you finance people...

```latex


\begin{tikzpicture}
\begin{axis}[
    width=12cm,
    height=8cm,
    xtick={1,2,3},
    xticklabels={[0--1],[1--2],[2--3]},
    xlabel={X bins},
    ylabel={Y values},
]

    \addplot[
        boxplot,
        boxplot/draw direction=y,
        boxplot/draw position=1,
        fill=blue!20
    ] table[col sep=comma, y=y] {bin1.csv};

    \addplot[
        boxplot,
        boxplot/draw direction=y,
        boxplot/draw position=2,
        fill=red!20
    ] table[col sep=comma, y=y] {bin2.csv};

    \addplot[
        boxplot,
        boxplot/draw direction=y,
        boxplot/draw position=3,
        fill=orange!20
    ] table[col sep=comma, y=y] {bin3.csv};

    \addplot[
        only marks,
        mark=*,
        opacity=0.6
    ]
    table[
        col sep=comma,
        x expr=floor(\thisrow{x}) + 1 + 0.15*(rand-0.5),
        y=y
    ] {data.csv};

\end{axis}
\end{tikzpicture}


```

![multiplot2.png](../assets/common_files/images_latex/multiplot2.png)

bin1.csv

```text


y
5
7
6
3
4


```

bin2.csv

```text


y
8
6
7
5
9


```

bin3.csv

```text


y
4
3
6
5
7


```

data.csv

```text


x,y
0.1,5
0.2,7
0.4,6
0.8,3
0.9,4  <-- END OF BIN1
1.1,8
1.2,6
1.4,7
1.7,5
1.9,9  <-- END OF BIN2
2.1,4
2.2,3
2.5,6
2.7,5
2.9,7  <-- END OF BIN3


```

Yeah, yeah, that is very _manual_, a lot of pre-word to do it, bit still possible...

With manual scripting generating LaTeX code in an input or include tex file.

But that is an excuse to show you the `floor` and `rand` functions.

Yess, because look:

- the boxplots takes a batch of values

- those values have an x values associated with them in `data.csv`

- but they loose those informations in binN.csv, what a drama !


So how do i convert the boxplots coordinate system with scatterplot one ?

I just go over the x values `\thisrow{x}`, floor them `floor(\thisrow{x})` and add some noises with `rand`.

`rand` gives random values between 0 and 1, and you see that i substract 0.5 to those generaed values, so noises belongs to -0.5, 0.5 --> Illusion of local scatterplot, which they are, but we just recreated the local scatterlot with x axis noises.

### HeatMaps

HeatMaps, heatmaps, heatmaps...

Here we need an axis context, of course.

```latex


\begin{tikzpicture}
\begin{axis}[colorbar,
             colormap name = viridis]

    % matrix plot* do color interpolation, it means that a cell colored is given
    % but still can get influenced by neighbors
    \addplot[matrix plot*,
             mesh/cols=3,
             point meta=explicit] coordinates {
        (0,0) [4] (1,0) [14] (2,0) [13]
        (0,1) [13] (1,1) [13] (2,1) [14]
        (0,2) [13] (1,2) [4] (2,2) [5]
    };

\end{axis}
\end{tikzpicture}


```

![heatmap1.png](../assets/common_files/images_latex/heatmap1.png)

There are a lot going on here.

First `mesh/cols=3` -\> data should be interpredted as a grid with 3 column per row

Then, `point meta=explicit` means that i provide manually the color, look in `coordinates`:

```latex


coordinates {
        (X1,Y1) [COLOR1] (X2,Y2) [COLOR2] ...
        (X3,Y3) [COLOR3] ... ...
        (X4,Y4) [COLOR4] ... ...
}


```

expands to:

```latex


coordinates {
        (0,0) [4] (1,0) [14] (2,0) [13]
        (0,1) [13] (1,1) [13] (2,1) [14]
        (0,2) [13] (1,2) [4] (2,2) [5]
}


```

Color value are **normalized** considering the **min** and **max** of your input color value.

And importantly `matrix plot*` -\> means do **color interpolation**

Meaning do not take the exact color of a cell, but check its neighboor and iterpolates its color, if neighboor got high color value, it will interpolate a pretty high color value even thos its current color is mid.

To display true color, and not do color interpolation, we do just `matrix plot`.

```latex


\begin{tikzpicture}
\begin{axis}[colorbar,
             colormap name = viridis]

    \addplot[matrix plot,
             mesh/cols=3,
             point meta=explicit] coordinates {
        (0,0) [4] (1,0) [14] (2,0) [13]
        (0,1) [13] (1,1) [13] (2,1) [14]
        (0,2) [13] (1,2) [4] (2,2) [5]
    };

\end{axis}
\end{tikzpicture}


```

![heatmap1B.png](../assets/common_files/images_latex/heatmap1B.png)

Now the options in the axis !

```latex


\begin{axis}[colorbar,
             colormap name = viridis]


```

`colorbar` just print at the right the infamous ... colorbar heat

And we can change the theme, so here we assign `viridis` to `colormap name`.

Look without color interpolation and using `table` (huura!! it supports it):

```latex


\begin{tikzpicture}
\begin{axis}[colorbar,
             colormap name=inferno]

    \addplot[matrix plot,
             mesh/cols=3,
             point meta=explicit
    ] table[col sep=comma,
            x=x,
            y=y,
            meta=value] {heatmap.csv};

\end{axis}
\end{tikzpicture}


```

- `meta` -\> tells the associated color

![heatmap2.png](../assets/common_files/images_latex/heatmap2.png)

heatmap.csv

```text


x,y,value
0,0,4
1,0,14
2,0,13
0,1,13
1,1,13
2,1,14
0,2,13
1,2,4
2,2,5


```

#### Custom themes

You can define your own theme doing so with, yet again `pgfplotsset`.

```text


\pgfplotsset{ %define custom pgfplot theme, heatmap
  colormap={myinferno}{
    rgb255(0cm)=(0,0,4);
    rgb255(1cm)=(31,12,72);
    rgb255(2cm)=(85,15,109);
    rgb255(3cm)=(136,34,106);
    rgb255(4cm)=(186,54,85);
    rgb255(5cm)=(227,89,51);
    rgb255(6cm)=(249,140,10);
    rgb255(7cm)=(249,201,50);
    rgb255(8cm)=(252,255,164);
  }
}


```

Here i defined a **gradient**.

So from the bottom of the color gradient bar ( `0cm`), the lowest color value is: `(0,0,4)`

Meaning 0 Red, 0 Blue, 4 Green

It is the RGB space, so each values has 256 values in the range of 0 -> 255 -> 256 bits ;)

I could furtherly fine tune my gradient defining more intermediate color values, like at `0.5cm`, `1.5cm`...

Then use it in heatmap for example.

```latex


\begin{tikzpicture}
\begin{axis}[colorbar,
             colormap name=myinferno]

    \addplot[matrix plot,
             mesh/cols=3,
             point meta=explicit
    ] table[col sep=comma,
            x=x,
            y=y,
            meta=value] {heatmap.csv};

\end{axis}
\end{tikzpicture}


```

![heatmap3.png](../assets/common_files/images_latex/heatmap3.png)

## 3D Tikz Lib & TikZ - Finally

Soo finally, we come closer to realizing Doom in LaTeX - DooMTeX !

So first let's talsk about basics 2D shapes.

First define a tikz environment, what a spoil !!

And, another spoil, use the `\draw` command.

"Hoooooo, never thought about it! That is not what we saw in N examples before."

You may say.

But that's not exact yet.

Now i'll stop being skizophrenic and start being normal.

```latex


\begin{tikzpicture}

    \draw (0, 0) -- (1,1) -- (2,0) -- (0,0);

    %% or cycle back automatically
    \draw (0, -2) -- (1,-1) -- (2,-2) -- cycle;

\end{tikzpicture}


```

You see, that is literally:

```latex


\begin{tikzpicture}

    \draw POINT1 -- POINT2 -- ...;

\end{tikzpicture}


```

![triangle1.png](../assets/common_files/images_latex/triangle1.png)

expanding to:

```latex


\begin{tikzpicture}

    \draw (x1, y1) -- (x2,y2) -- ...;

\end{tikzpicture}


```

Drawing lines betwen points.

And if you want the last line to go back to the fist point, you want to do a cycle, so use `cycle`, neat !

```latex


\begin{tikzpicture}

    \draw POINT1 -- POINT2 -- ... -- cycle;

\end{tikzpicture}


```

expanding to...you know what ;)

So for drawing a rectangle you just add another points and tweaks coordinates.

```latex


\begin{tikzpicture}

    \draw (0, 0) -- (0,2) -- (3,2) -- (3,0) -- cycle;

\end{tikzpicture}


```

![rectangle1.png](../assets/common_files/images_latex/rectangle1.png)

By this time we just draw straight lines, but how to draw **round** lines ?

You know to do something called a cirlce.

Hmm, when we got a good default code we use it, for this purpose we just have to defne the circle center and after use `circle`.

```latex


\begin{tikzpicture}

    \draw STARTPOINT circle RADIUS;

\end{tikzpicture}


```

expanding to, for example:

```latex


\begin{tikzpicture}

    \draw (0, 0) circle (2);

\end{tikzpicture}


```

![cricle1.png](../assets/common_files/images_latex/circle1.png)

Special keywords is something you come accross often in latex to help you, like also `rectangle`..

Yeah, prev rectangle was more complicated than it needed to be.

```latex


\begin{tikzpicture}

    \draw LEFTBOTTOMPOINT rectangle TOPRIGHTPOINT;

\end{tikzpicture}


```

expanding to, for example:

```latex


\begin{tikzpicture}

    \draw (0, 0) rectangle (3,2);

\end{tikzpicture}


```

![rectangle2.png](../assets/common_files/images_latex/rectangle2.png)

In fact when some point can be infered, you can be sure to find a shape keyword for it.

This is a good pental model.

Look, we can define our own macro for TikZ shape, a simple one is for `rectangle`.

We'll use the good TikZ coordinate parsing synthax, the infamous `|-`.

`A|-B`

Where `A` is `(xA,yA)` and B is `(xB,yB)`

Meaning, take `xA` and `yB`.

So `B|-A` means take `xB` and `yA`.

And also, `A-|B` -\> takes `yA` and `xB`.

Sothis works:

```latex


\newcommand{\myrectangle}[2]{
    \draw (#1) -- (#2|-#1) -- (#2) -- (#1|-#2) -- cycle;
}

\begin{tikzpicture}

    \myrectangle{0,0}{3,2};

\end{tikzpicture}


```

![rectangle3.png](../assets/common_files/images_latex/rectangle3.png)

But we can go further and make a more perfect clone of `rectangle` macro using `tikzset`.

```latex


\makeatletter
\tikzset{
    my rectangle/.style={
        to path={
            -- (\tikztotarget|- \tikztostart)
            -- (\tikztotarget)
            -- (\tikztostart|- \tikztotarget)
            -- cycle
        }
    }
}
\makeatother

\begin{tikzpicture}

    \draw (0,0) to[my rectangle] (3,2);

\end{tikzpicture}


```

![rectangle4.png](../assets/common_files/images_latex/rectangle4.png)

What is that ?

First, you recognize the pattern:

```latex


-- (COORDINATES2|-COORDINATES1)
-- (COORDINATES2)
-- (COORDINATES1|-COORDINATES2)
-- cycle


```

expanding to:

```latex


-- (\tikztotarget|- \tikztostart)
-- (\tikztotarget)
-- (\tikztostart|- \tikztotarget)
-- cycle


```

Now you can also infere that `\tikztostart` -\> `COORDINATES1` and `\tikztotarget` -\> `COORDINATES2`.

Now you can say:

"Yess, i infered correctly, but pleeaseee , i'm begging you, tell me why the fuck do we need to wrap this code between those macro call `\makeatother` ?"

And you'll be right, especially for the begging part.

Internally TikZ (and LaTeX) use @ in macro names.

`\makeatletter` tells TeX to treat "@" as a letter during tokenization, so those internal macros can be read correctly.

This happens before TikZ processes anything.

Since my code does not use any macros containing "@", `\makeatletter` is not strictly required here.

```latex


\tikzset{
    my rectangle/.style={
        to path={
            -- (\tikztotarget|- \tikztostart)
            -- (\tikztotarget)
            -- (\tikztostart|- \tikztotarget)
            -- cycle
        }
    }
}

\begin{tikzpicture}

    \draw (0,0) to[my rectangle] (3,2);

\end{tikzpicture}


```

Now some fun example so you start getting when we'll speak about "programming in TikZ", the \* **EXPANSION**.

This works.

```latex


\newcommand{\mysuperrectangle}{
    to[my rectangle]
}

\begin{tikzpicture}

    \draw (0,0) \mysuperrectangle (3,2);

\end{tikzpicture}


```

Or even.

```latex


\def\mysuperrectangleb{
    to[my rectangle]
}

\begin{tikzpicture}

    \draw (0,0) \mysuperrectangleb (3,2);

\end{tikzpicture}


```

because in fact each:

```latex


\draw (0,0) \mysuperrectangleb (3,2);


```

Just **expands** to:

```latex


\draw (0,0) to[my rectangle] (3,2);


```

Which of course works like we've seen previously.

But this won't work:

```latex


\newcommand{\mysuperrectangle}{
    \newcommand{\mysuperrectangle}{
        \tikzset{
            my rectangle/.style={
                to path={
                    -- (\tikztotarget|- \tikztostart)
                    -- (\tikztotarget)
                    -- (\tikztostart|- \tikztotarget)
                    -- cycle
                }
            }
        }
    }
}

\begin{tikzpicture}

    \draw (0,0) \mysuperrectangle (3,2);

\end{tikzpicture}


```

Or with `\def`.

Why because it expands to:

```latex


\draw (0,0) \tikzset... (3,2);


```

Which is nonsense in TikZ perspective.

Because in TikZ, we define something, like A is X, the use A, but not using directly X in a tikzpicture, which is what TeX expansion with `\newcommand`, `\def` etcetera (basically all TeX definition) literally do.

So here, we define some style, macro the style **as intended to be used**, and use this macro.

You knwo that `\newcommand` is just a fancy, with extra logic for arguments, `\def` :)

Wowowow, we did already massive foreshadowing for what is coming after, so we go back to shapes, just shapes haha.

So now **Ellispe** !

Look:

```latex


\begin{tikzpicture}

    \draw CENTERPOINT ellipse (XRADIUS and YRADIUS);

\end{tikzpicture}


```

expanding to, for example:

```latex


\begin{tikzpicture}

    \draw (0, 0) ellipse (3 and 1);

\end{tikzpicture}


```

![ellipse1.png](../assets/common_files/images_latex/ellipse1.png)

Nothing too complicated, i dare say nothing complicated !

But can we tel the same thing about the **arcs** ??

What is an arc... an arc.

Okok, maybe that is not the right question.

What are the minimum coordinates we can provide to a system to draw whatever arcs we want, to make a system in fact **arc-turing-complete**, kind of haha.

Hmm, so we need to have the radius and the angle !

Okok, but now we got to place the arc.

So yeah we got the intuition to provide a starting point, like we did for basically al shapes.

But here it is complicating, we need to provide the radius and to draw it everywhere possible from the starting point that we also, btw placed everywhere we want.

So now what, just provides its length and what ?

"Its ... _angle_ ?"

Yup, can you developp ?

Its angle from the starting point that is placed on an imaginary horizontal plane, so this is a standard trigonometric circle angle.

after we provided that, we can be proud of being able to draw a ... line!

Wow !

But let's not forget the goal, the **arc**.

So now **Einstein time** !

Yup make use of relativity, or empathy or chatever is the concept that describes the best the fact of considering the perspective of the ending point of the newly drawed line / radius.

Now that "you are" at the ending point of the radius. You can visualize this point just circling around of the central point, like a pendulum that circles lol.

so this is key, because this is now where you can define the **arc path**, with angle, the line you just draw and the **future** endig line !

Here the example, you'll see some redundances in value, but its TikZ being himself, don't blame it, he's just...different, poor kid.

```latex


\begin{tikzpicture}

    \draw[fill=blue!20] CENTERPOINT -- (STARTANGLE:RADIUS) arc (STARTINGANGLE:ENDINGANGLE:RADIUS) -- cycle;

\end{tikzpicture}


```

Expanding to, for example:

```latex


\begin{tikzpicture}

    \draw[fill=blue!20] (0,0) -- (80:2) arc (80:90:2) -- cycle;

\end{tikzpicture}


```

![arc1.png](../assets/common_files/images_latex/arc1.png)

or

```latex


\begin{tikzpicture}

    \draw[fill=blue!20] (0,0) -- (0:2) arc (0:20:2) -- cycle;

\end{tikzpicture}


```

![arc2.png](../assets/common_files/images_latex/arc2.png)

you can see the `fill` parameter in action, coloring the interior of the shape, in fact the shape, because des a shape has an interior ?

I mean is this a property it automatically inherits ?

I think yes - no proof just trust be bro.

Here a more complete example.

```latex


\begin{tikzpicture}

    % starts at 0,0, go to angle 0, radius 2, shape the arc from angle 0 to angle 90 with radius 2
    \draw[fill=blue!20] (0,0) -- (0:2) arc (0:90:2) -- cycle;

    \draw[fill=red!20]  (0,0) -- (90:2) arc (90:180:2) -- cycle;
    \draw[fill=orange!20, shift={(4,0)}]  (0,0) -- (180:2) arc (180:270:2) -- cycle;

    \node at (4,0.1) {Point 1};

\end{tikzpicture}


```

![arc3.png](../assets/common_files/images_latex/arc3.png)

Hmm let's create a macro that actually makes sense for arc.

```latex


\newcommand{\myarc}[3]{
    (#1:#2) arc (#1:#3:#2) -- cycle
}


```

and use it like:

```latex


\begin{tikzpicture}

    \draw[fill=blue!20] (0,0) -- \myarc{STARTANGLE}{RADIUS}{ENDANGLE};

\end{tikzpicture}


```

expanding to, for example:

```latex


\begin{tikzpicture}

    \draw[fill=blue!20] (0,0) -- \myarc{0}{2}{20};

\end{tikzpicture}


```

![arc4.png](../assets/common_files/images_latex/arc4.png)

Like that, we just define start angle, radius, end angle. -- Macro commands are just expansions !

We can connect Shapes very easily, not ending mentaly hilled after tweaking for hours the arrow coordinates for the pixel perfect arrow starting from shape A to B and so on.

remember, there is `\draw`, but also `\node`, and `\node` can be named to better manipulate them.

And we can also provide node a shape, inheriting from `draw` properties that we put in node options.

We then define its `shape` in shae option.

Those 2 properrties make them perfect for constructing easily a diagram !

Look:

```latex


\begin{tikzpicture}

    \node[draw,
          shape=circle,
          minimum size=2.1cm,
          inner sep=0pt] (Z) at (0,0) {A};
    \node[draw,
          shape=rectangle,
          minimum size=2.1cm,
          inner sep=0pt] (Y) at (6,0) {B};

    \draw[->] (Z) -- (Y);

\end{tikzpicture}


```

![nodeshape1.png](../assets/common_files/images_latex/nodeshape1.png)

If we do not precise the `shape`, it defaults to square.

```latex


\begin{tikzpicture}

    \node[draw,
          minimum size=2.1cm,
          inner sep=0pt] (Z) at (0,0) {A};
    \node[draw,
          minimum size=2.1cm,
          inner sep=0pt] (Y) at (6,0) {B};

    \draw[->] (Z) -- (Y);

\end{tikzpicture}


```

![nodeshape2.png](../assets/common_files/images_latex/nodeshape2.png)

And if we do not even precise `draw` in options, shapes has no effetc because no shapes are even draw.

```latex


\begin{tikzpicture}

    \node[shape=circle,
          minimum size=2.1cm,
          inner sep=0pt] (Z) at (0,0) {A};
    \node[shape=rectangle,
          minimum size=2.1cm,
          inner sep=0pt] (Y) at (6,0) {B};

    \draw[->] (Z) -- (Y);

\end{tikzpicture}


```

![nodeshape3.png](../assets/common_files/images_latex/nodeshape3.png)

- `inner sep=xcm` -\> the node will be at minimum x cm wide

- `inner sep=xpt` -\> the padding between the text and the border of the node


In fact node size is content size + 2 \* inner sep.

If content size is smaler than controled size with `minimum size` and `inner sep` equals to 0, then the node size will be exactly `minimum size`.

Here a last example concerning that subject:

```latex


\begin{tikzpicture}[
    % Global style for all nodes
    every node/.style={
        draw,
        minimum size=2.1cm,
        inner sep=0pt,
        align=center
    },
    edgeLabel/.style={
        draw=none,
        fill=none,
        minimum size=0pt,
        inner sep=2pt,
        font=\small
    },
    % Custom styles
    circleNode/.style={circle, fill=blue!20},
    rectNode/.style={rectangle, fill=green!20},
    diamondNode/.style={diamond, aspect=2, fill=orange!20},
    arrow/.style={->, thick}
]

    % Main nodes
    \node[circleNode] (Z) at (0,0) {Start};
    \node[diamondNode] (D) at (4,0) {Condition};
    \node[rectNode] (Y) at (8,2) {Action 1};
    \node[rectNode] (W) at (8,-2) {Action 2};

    % Extra node
    \node[rectNode] (End) at (12,0) {End};

    % Connections
    \draw[arrow] (Z) -- (D);
    \draw[arrow] (D) -- node[edgeLabel, above]{Yes} (Y);
    \draw[arrow] (D) -- node[edgeLabel, below]{No} (W);

    \draw[arrow] (Y) -- (End);
    \draw[arrow] (W) -- (End);

\end{tikzpicture}


```

![nodeshape4.png](../assets/common_files/images_latex/nodeshape4.png)

You see that we can define lobal style in `tikzpicture` option.

```latex


every node/.style={
    draw,
    minimum size=2.1cm,
    inner sep=0pt,
    align=center
}


```

Nothing new here apart from the `align=center` option definition that does what you think, center text content inside the node.

And what about ?

```latex


edgeLabel/.style={
    draw=none,
    fill=none,
    minimum size=0pt,
    inner sep=2pt,
    font=\small
}


```

This is specifically for those nodes:

```latex


\draw[arrow] (D) -- node[edgeLabel, above]{Yes} (Y);
\draw[arrow] (D) -- node[edgeLabel, below]{No} (W);


```

Not for this one for example:

```latex


\draw[arrow] (Z) -- (D);


```

At this point you tell me.

"Wait, but after expansion, i do not see the difference !"

You are right but here that is not quite the right mental model.

You have to think again, about definition, then usage, not just pure expansion.

And for the last one i already defined the node here:

```latex


\node[circleNode] (Z) at (0,0) {Start};
\node[diamondNode] (D) at (4,0) {Condition};


```

So, i repeat but `edgeLabel` options aplies only on nodes that are knd of defined "on the fly" using the draw command !

And at this point there is no new options we have not seen.

### Geometric Transformations

Now geometric **transfrmations** !!!

Yessss !!!

Look:

```latex


\begin{tikzpicture}

    \draw[shift={(4,0)}, rotate=45, scale=0.5]
      (0,0) ellipse (3 and 1);

    \draw[shift={(12,0)}, rotate=45, scale=0.5]
      (0,0) ellipse (3 and 1);

\end{tikzpicture}


```

![transfo1.png](../assets/common_files/images_latex/transfo1.png)

`shift={(COORDINATES)}` -\> `shift={x,y}` is just an internal option way to choose the starting point of a draw

Instead of doing precising the coordinates after:

```latex


\begin{tikzpicture}

    \draw[rotate=45, scale=0.5]
      (4,0) ellipse (3 and 1);

\end{tikzpicture}


```

![transfo2.png](../assets/common_files/images_latex/transfo2.png)

`rotate` is just te rotation of the figure, (following trigonometri circle).

This is a key part of TikZ, allows extremely more easily way to draw some shapes in space.

`scale` -\> Fancy way to ... scale / change dimensions proportionaly of a shape, 1 is the base scale value.

Look at this example emphasing the role of scale:

```latex


\begin{tikzpicture}

    \draw[shift={(4,0)}, rotate=45, scale=0.5]
      (0,0) ellipse (3 and 1);

    \draw[shift={(12,0)}, rotate=135, scale=1]
      (0,0) ellipse (3 and 1);

\end{tikzpicture}


```

![transfo3.png](../assets/common_files/images_latex/transfo3.png)

Instead of:

```latex


\begin{tikzpicture}

    \draw[shift={(4,0)}, rotate=45, scale=0.5]
      (0,0) ellipse (3 and 1);

    \draw[shift={(12,0)}, rotate=135, scale=0.5]
      (0,0) ellipse (6 and 2);

\end{tikzpicture}


```

![transfo4.png](../assets/common_files/images_latex/transfo4.png)

### 3D

Yess, 3D !!!

Look at that 3D axis demo:

```latex


\begin{tikzpicture}
    \draw[->] (X1,Y1,Z1) -- (X2,Y1,Z1); % x axis
    \draw[->] (X1,Y1,Z1) -- (X1,Y2,Z1); % y axis
    \draw[->] (X1,Y1,Z1) -- (X1,Y1,Z2); % z axis
\end{tikzpicture}


```

expanding to, for example:

```latex


\begin{tikzpicture}
    \draw[->] (0,0,0) -- (2,0,0); % x axis
    \draw[->] (0,0,0) -- (0,2,0); % y axis
    \draw[->] (0,0,0) -- (0,0,2); % z axis
\end{tikzpicture}


```

![3D1.png](../assets/common_files/images_latex/3D1.png)

Yup, thanks to `\usetikzlibrary{3d}` in the preamble, TikZ interprets 3D coordinates systems (internally it does a take those 3D coordinates, and projects it on a 2D plane)

Look another exampe -> the cube !

```latex


\begin{tikzpicture}

    \fill[gray!20] (0,0,0) -- (2,0,0) -- (2,2,0) -- (0,2,0) -- cycle;


    \draw (0,0,0) -- (2,0,0) -- (2,2,0) -- (0,2,0) -- cycle;
    \draw (0,0,2) -- (2,0,2) -- (2,2,2) -- (0,2,2) -- cycle;

    \draw (0,0,0) -- (0,0,2);
    \draw (2,0,0) -- (2,0,2);
    \draw (2,2,0) -- (2,2,2);
    \draw (0,2,0) -- (0,2,2);

\end{tikzpicture}


```

![3D2.png](../assets/common_files/images_latex/3D2.png)

You see it is technically possible to do it in raw 2D coordinate system, but at the cost of much more work. And a cube is the simplest 3D shape...

Here, the introduction of `\fill` that acts like draw for everything apart that it fills a **closed** area, not drawing any shapes.

By the way we can name coordinates, also posible in 2D of course, but it may be more useful in 3D, look.

```latex


\begin{tikzpicture}
\begin{scope}

    \coordinate (NAME1) at (POINT1);
    \coordinate (NAME2) at (POINT2);
    \coordinate (NAME3) at (POINT3);
    \coordinate (NAME4) at (POINT4);

    \coordinate (NAME5) at (POINT5);

    \fill[gray!20] (A) -- (B) -- (C) -- (D) -- cycle;
    \fill[gray!30] (S) -- (A) -- (B) -- cycle;
    \fill[gray!40] (S) -- (B) -- (C) -- cycle;
    \fill[gray!25] (S) -- (C) -- (D) -- cycle;

    \draw (A) -- (B) -- (C) -- (D) -- cycle;
    \draw (S) -- (A);
    \draw (S) -- (B);
    \draw (S) -- (C);
    \draw[dashed] (S) -- (D); % hidden edge

\end{scope}
\end{tikzpicture}


```

Expanding to, for example:

```latex


\begin{tikzpicture}
\begin{scope}

    \coordinate (A) at (0,0,0);
    \coordinate (B) at (2,0,0);
    \coordinate (C) at (2,2,0);
    \coordinate (D) at (0,2,0);

    \coordinate (S) at (1,1,2);

    \fill[gray!20] (A) -- (B) -- (C) -- (D) -- cycle;
    \fill[gray!30] (S) -- (A) -- (B) -- cycle;
    \fill[gray!40] (S) -- (B) -- (C) -- cycle;
    \fill[gray!25] (S) -- (C) -- (D) -- cycle;

    \draw (A) -- (B) -- (C) -- (D) -- cycle;
    \draw (S) -- (A);
    \draw (S) -- (B);
    \draw (S) -- (C);
    \draw[dashed] (S) -- (D); % hidden edge

\end{scope}
\end{tikzpicture}


```

![3D3.png](../assets/common_files/images_latex/3D3.png)

Usefull, when we want to reuse coordinates.

Why do we define a `scope` environment ?

Look at this:

```latex


\begin{tikzpicture}
\begin{scope}[rotate around x = 45, rotate around y = 45, rotate around z = 45]

    \coordinate (A) at (0,0,0);
    \coordinate (B) at (2,0,0);
    \coordinate (C) at (2,2,0);
    \coordinate (D) at (0,2,0);

    \coordinate (S) at (1,1,2);

    \fill[gray!20] (A) -- (B) -- (C) -- (D) -- cycle;
    \fill[gray!30] (S) -- (A) -- (B) -- cycle;
    \fill[gray!40] (S) -- (B) -- (C) -- cycle;
    \fill[gray!25] (S) -- (C) -- (D) -- cycle;

    \draw (A) -- (B) -- (C) -- (D) -- cycle;
    \draw (S) -- (A);
    \draw (S) -- (B);
    \draw (S) -- (C);
    \draw[dashed] (S) -- (D); % hidden edge

\end{scope}
\end{tikzpicture}


```

![3D4.png](../assets/common_files/images_latex/3D4.png)

We can rotate the sceeene !!

Think of it like defining an axis in PGFPlot.

Massive PGFPlot 3D foreshadowing here:

```latex


\begin{tikzpicture}
\begin{axis}[xlabel=$x$,
             ylabel=$y$,
             zlabel=$z$,
             colorbar,
             colormap name=myinferno]

    \addplot3[surf,
              domain=-2:2,
              y domain = -2:2,
              samples=30, % samples -> how accurate it is (you can choose x and y samples / intervals)
              samples y=30
    ]{sin(deg(x)) * cos(deg(x))};

\end{axis}
\end{tikzpicture}


```

![3D5.png](../assets/common_files/images_latex/3D5.png)

Keep in mind, the x axis, is the "width", the y axis is the "depth" and the z axis is the "height".

And we use `\addplot3` for 3D plot in PGFPlot.

Sme infrmations about this plot, you are discovering just these new option: `samples` and `samples y`.

They are like the number of intervals the engine takes in count to draw this surface, the more there are the more accurate it is.

- `samples` -\> x samples

- `samples y` -\> y samples


When does the samples are used in the PGFPlot engine ?

**BEFORE** the projection on the 2D plan.

Look, we are defining a surface:

```latex


sin(deg(x)) * cos(deg(x))


```

HERE, it is sampling, that is why we got x and y samples but not z samples.

Take a look at how the resolution gets worse here:

```latex


\begin{tikzpicture}
\begin{axis}[xlabel=$x$,
             ylabel=$y$,
             zlabel=$z$,
             colorbar,
             colormap name=myinferno]

    \addplot3[surf,
              domain=-2:2,
              y domain = -2:2,
              samples=15,
              samples y=30,
    ]{sin(deg(x)) * cos(deg(x))};

\end{axis}
\end{tikzpicture}


```

![3D6.png](../assets/common_files/images_latex/3D6.png)

So now that we have the axis direction in mind, we go back to the scope rotation for the shapes.

Here a simple example, rotating a line.

```latex


\begin{tikzpicture}[rotate around x=45,
                    rotate around y=45,
                    rotate around z=0
                    ]
    \draw (0,0,0) -- (2,0,0);

\end{tikzpicture}


```

![3D7.png](../assets/common_files/images_latex/3D7.png)

```latex


\begin{tikzpicture}[rotate around x=0,
                    rotate around y=0,
                    rotate around z=45
                    ]
    \draw (0,0,0) -- (2,0,0);
\end{tikzpicture}



```

![3D8.png](../assets/common_files/images_latex/3D8.png)

```latex


\begin{tikzpicture}[rotate around x=0,
                    rotate around y=45,
                    rotate around z=0
                    ]
    \draw (0,0,0) -- (2,0,0);

\end{tikzpicture}



```

![3D9.png](../assets/common_files/images_latex/3D9.png)

```latex


\begin{tikzpicture}[rotate around y=45,
                    rotate around x=45,
                    rotate around z=0
                    ]
    \draw (0,0,0) -- (2,0,0);

\end{tikzpicture}


```

![3D10.png](../assets/common_files/images_latex/3D10.png)

At this point you are trying to emergeinvariants in your head about what the rotations actually do.

We are aligned that we draw a straight line perfectly parallel to the x axis.

So a rotation of X degree around this axis does nothing, that's right, but just fr this particular rotation.

You'll see later.

You also notice that the rotations have an order we can control, like so:

```latex


\begin{tikzpicture}[rotate around x=0,
                    rotate around y=45,
                    rotate around z=0
...


```

-\> Rotate around x then around y

And:

```latex


\begin{tikzpicture}[rotate around y=45,
                    rotate around x=45,
                    rotate around z=0
                    ]
    \draw (0,0,0) -- (2,0,0);
...


```

-\> Rotate around y then around x

And you also note that rotation **ARE NOT COMMUTATIVE**.

`R1 * R2 != R2 * R1`

Look this:

```latex


\begin{tikzpicture}[rotate around x=45,
                    rotate around y=45,
                    rotate around z=0
                    ]
    \draw (0,0,0) -- (2,0,0);

\end{tikzpicture}


```

![3D7.png](../assets/common_files/images_latex/3D7.png)

Does not equal:

```latex


\begin{tikzpicture}[rotate around y=45,
                    rotate around x=45,
                    rotate around z=0
                    ]
    \draw (0,0,0) -- (2,0,0);

\end{tikzpicture}


```

![3D10.png](../assets/common_files/images_latex/3D10.png)

Why ??

It is not simply because, **"straight line aligned to x, so x rotation does nothing first and then y, so yeah different than y rotation first and then x"**.

That was also my first interpretation but here this mental model breaks hard, if that was true then those would output the same thing:

```latex


\begin{tikzpicture}[rotate around x=45,
                    rotate around y=45,
                    rotate around z=0
                    ]
    \draw (0,0,0) -- (2,0,0);

\end{tikzpicture}


```

![3D7.png](../assets/common_files/images_latex/3D7.png)

```latex


\begin{tikzpicture}[rotate around x=0,
                    rotate around y=45,
                    rotate around z=0
                    ]
    \draw (0,0,0) -- (2,0,0);

\end{tikzpicture}



```

![3D9.png](../assets/common_files/images_latex/3D9.png)

But that is **obviously not the case** !

So what ?

In fact, this is not a rotation of the object arround the axis, but a rotation of the **ENTIIIIRE AXISES** around a particular axis, that is the game changer, and freaking counter intuitive and particularly dumb, one of the dumbest shit TikZ provides, that is ridiculously dumb design choice --> that totaly breaks easy predictability of geometric transformation...

That is not rotation in a fixed coordinate system.

In both case, rotations are not comutatives, but at least, in a fixed coordinate system, it is often far easizer to predict the output of a sequence of rotations.

I got an enormous amount of crystal hate for this design choice, i will train to the gym and come back.

...

Here i am !

I'll pretend this never happened and continue.

Look at that we can also define the literal meaning of the axis, in fact the direction of the axis, thanks to scope `x`, `y` and `z` options.

```latex


\begin{tikzpicture}
\begin{scope}[x={(MOOVERIGHT1,MOOVEUP1)}, % moving by 1 X unit -> moves right by 1cm and do not moves up or down
              y={(MOOVERIGHT2,MOOVEUP2)}, % moving by one Y unit -> moves right by 0.5cm and up by 0.5cm
              z={(MOOVERIGHT3,MOOVEUP3)}] % moving by 1 Z unit -> moves right by 0cm and up by 1cm

    \coordinate (A) at (0,0,0);
    \coordinate (B) at (2,0,0);
    \coordinate (C) at (2,2,0);
    \coordinate (D) at (0,2,0);

    \coordinate (S) at (1,1,2);

    \fill[gray!20] (A) -- (B) -- (C) -- (D) -- cycle;
    \fill[gray!30] (S) -- (A) -- (B) -- cycle;
    \fill[gray!40] (S) -- (B) -- (C) -- cycle;
    \fill[gray!25] (S) -- (C) -- (D) -- cycle;

    \draw (A) -- (B) -- (C) -- (D) -- cycle;
    \draw (S) -- (A);
    \draw (S) -- (B);
    \draw (S) -- (C);
    \draw[dashed] (S) -- (D); % hidden edge

\end{scope}
\end{tikzpicture}


```

expanding to, for example:

```latex


\begin{tikzpicture}
\begin{scope}[x={(1.2cm,0cm)}, % moving by 1 X unit -> moves right by 1cm and do not moves up or down
              y={(0.5cm,0.5cm)}, % moving by one Y unit -> moves right by 0.5cm and up by 0.5cm
              z={(0cm,1cm)}] % moving by 1 Z unit -> moves right by 0cm and up by 1cm

    \coordinate (A) at (0,0,0);
    \coordinate (B) at (2,0,0);
    \coordinate (C) at (2,2,0);
    \coordinate (D) at (0,2,0);

    \coordinate (S) at (1,1,2);

    \fill[gray!20] (A) -- (B) -- (C) -- (D) -- cycle;
    \fill[gray!30] (S) -- (A) -- (B) -- cycle;
    \fill[gray!40] (S) -- (B) -- (C) -- cycle;
    \fill[gray!25] (S) -- (C) -- (D) -- cycle;

    \draw (A) -- (B) -- (C) -- (D) -- cycle;
    \draw (S) -- (A);
    \draw (S) -- (B);
    \draw (S) -- (C);
    \draw[dashed] (S) -- (D); % hidden edge

\end{scope}
\end{tikzpicture}


```

![3D11.png](../assets/common_files/images_latex/3D11.png)

Yup, we can do that :)

### Shades

Now, spheres !

```latex


\begin{tikzpicture}

    \shade[shape=ball, color=red!20!white] (0,0) circle (2cm);

    \shade[shape=ball, color=red!20!white] (8cm,0) circle (4cm);

\end{tikzpicture}


```

![shade1.png](../assets/common_files/images_latex/shade1.png)

```latex


\begin{tikzpicture}

    \shade[color=red!20!white] (0,0) circle (2cm);

    \shade[color=red!20!white] (8cm,0) circle (4cm);

\end{tikzpicture}


```

![shade2.png](../assets/common_files/images_latex/shade2.png)

```latex


\begin{tikzpicture}

    \shade[ball color=red!20!white] (0,0) circle (2cm);

    \shade[ball color=red!20!white] (8cm,0) circle (4cm);

\end{tikzpicture}


```

![shade3.png](../assets/common_files/images_latex/shade3.png)

```latex


\begin{tikzpicture}

    \shade[shape=ball, ball color=red!20!white] (0,0) circle (2cm);

    \shade[shape=ball, ball color=red!20!white] (8cm,0) circle (4cm);

\end{tikzpicture}


```

![shade4.png](../assets/common_files/images_latex/shade4.png)

Okok, that is A LOT.

First, `\shade` is a fancy `\fill`.

`\fill` just declare outputs a color onto a closed area, `\shade` outputs a controled variation of colors onto a closed area.

We will learn how to control the variations later.

Second, about parameters, this is where it first gets confusing.

The first example, made TikZ shade engine ignore the shade color, because we declared the option `color`, that makes it behave weirdly and just use default greyish shade color --> Just API bad design IMO. So it still render the shade as a ball surface area, but not with intended color.

Same problem in second example.

To actually make it use the intended color, we need to use the option `ball color`.

So that is why 3 and 3 examples works as intended.

And why the example 4 is actually redundant, we provide the shape with `shape=ball`, and redeclare shape in `ball color`.

So 3 wins.

The synthax is actually:

```latex


\begin{tikzpicture}

    \shade[SHADEAPPLICATIONDEFINITION] AREADEFINITION;

\end{tikzpicture}


```

So where it is applied as in the actual "draw" and how it is applied (algorithm) in the options.

We can also provide cool parameters, like how the color must be on the outer and on the inner:

```latex


\begin{tikzpicture}
    \shade[inner color=red!20,
           outer color=blue!20] (0,0) circle (2cm);

\end{tikzpicture}


```

![shade5.png](../assets/common_files/images_latex/shade5.png)

Now, one of the last thing we should be able to control, is "how the color spread".

First, we need to define the coordinate system we are working on, for a ball, so a circle area, it is a `radial`.

So we define our custom shading as defining a custom color gradient and a starting point:

```latex


\pgfplotdeclareradialshading{STARTPOINT}{
    color(DISTANCEFROMSTARTPOINT1)=(COLOR1);
    color(DISTANCEFROMSTARTPOINT2)=(COLOR2)
}


```

expanding to, for example:

```latex


\pgfdeclareradialshading{myshade}{\pgfpoint{0.5cm}{0.5cm}}{
  color(0cm)=(red!40);
  color(1cm)=(blue!50)
}


```

and using it like:

```latex


\begin{tikzpicture}
    \shade[shading=myshade] (0,0) circle (2cm);
\end{tikzpicture}


```

![shade6.png](../assets/common_files/images_latex/shade6.png)

We define a radial with `\pgfplotdeclareradialshading`, because that tells the shading algorithm the gradient of color must "sparse" according to a radial coordinate system.

That is why the starting point is normal 2D point `(x,y)`.

But what if we want to shift the ball ?

like if we shift x doing so:

```latex


\begin{tikzpicture}
    \shade[shading=myshade] (8cm,0) circle (2cm);
\end{tikzpicture}


```

Dos this works ?

No

This is weird but nothing changes here.

In fact we need to also proved the `shading transform` option with the same shift, and we do not touch our custom shade `myshade`.

```latex


\begin{tikzpicture}
    \shade[
        shading=myshade,
        transform canvas={shift={(8cm,0)}}
    ] (8cm,0) circle (2cm);
\end{tikzpicture}


```

![shade7.png](../assets/common_files/images_latex/shade7.png)

Now, all is coherent according to TikZ API.

That is some good stuff, but in fact shade can be applied in any way, so yess, next thing to do is apply them in a rectangle, why not ?

So here we work with `shading=axis`.

Here an example that is the equivalent of the `inner / outer` color shading one for the ball.

Of course, geometrically different but you get the idea.

here with `shading angle = 0`.

```latex


\begin{tikzpicture}

    \shade[shading=axis,
           left color=red,
           right color=blue,
           shading angle=0]
    (0,0) rectangle (3,2);

\end{tikzpicture}


```

![shade8.png](../assets/common_files/images_latex/shade8.png)

Here with `shading angle=40`.

```latex


\begin{tikzpicture}

    \shade[shading=axis,
           left color=red,
           right color=blue,
           shading angle=40]
    (0,0) rectangle (3,2);

\end{tikzpicture}


```

![shade9.png](../assets/common_files/images_latex/shade9.png)

Here with `shading angle=90`.

```latex


\begin{tikzpicture}

    \shade[shading=axis,
           left color=red,
           right color=blue,
           shading angle=90]
    (0,0) rectangle (3,2);

\end{tikzpicture}


```

![shade10.png](../assets/common_files/images_latex/shade10.png)

Here with `shading angle=190`.

```latex


\begin{tikzpicture}

    \shade[shading=axis,
           left color=red,
           right color=blue,
           shading angle=190]
    (0,0) rectangle (3,2);

\end{tikzpicture}


```

![shade11.png](../assets/common_files/images_latex/shade11.png)

You get the idea, an x axis we rotate (angle according to a tigonmetric circle).

If you want bilinear shading, a cool trick is to do the following overlay.

```latex


\begin{tikzpicture}
    % base gradient
    \shade[shading=axis, left color=blue, right color=red]
        (0,0) rectangle (4,3);

    % overlay vertical gradient with transparency
    \shade[shading=axis, top color=yellow, bottom color=green, opacity=0.5]
        (0,0) rectangle (4,3);
\end{tikzpicture}


```

![shade12.png](../assets/common_files/images_latex/shade12.png)

Which is equivalent of:

```latex


\begin{tikzpicture}

    \shade[shading=axis, top color=yellow, bottom color=green]
        (0,0) rectangle (4,3);

    \shade[shading=axis, left color=blue, right color=red, opacity=0.5]
        (0,0) rectangle (4,3);

\end{tikzpicture}


```

![shade13.png](../assets/common_files/images_latex/shade13.png)

Because that is sad, but mixing left / right color with top / bottom color does not work in TikZ, what a shame, look at that !

```latex


\begin{tikzpicture}

    \shade[shading=axis,
           top color=yellow,
           bottom color=green,
           left color=blue,
           right color=red]
        (0,0) rectangle (4,3);

\end{tikzpicture}


```

![shade14.png](../assets/common_files/images_latex/shade14.png)

```latex


\begin{tikzpicture}

    \shade[shading=axis,
           left color=blue,
           right color=red,
           top color=yellow,
           bottom color=green
           ]
        (0,0) rectangle (4,3);

\end{tikzpicture}


```

![shade15.png](../assets/common_files/images_latex/shade15.png)

Only two last parameters are taken in count.

Hmm, wonder what will hapen if:

```latex


\begin{tikzpicture}

    \shade[shading=axis,
           left color=blue,
           top color=yellow,
           bottom color=green,
           right color=red
           ]
        (0,0) rectangle (4,3);

\end{tikzpicture}


```

![shade16.png](../assets/common_files/images_latex/shade16.png)

WTF...

Just want to shut down my brain sometimes and stop seing theses disturbing things...

Ha, maybe it takes the color pair of he first pair it finds, that would explain it.

Woooo some spanish punctations now !

## Again Some 3D Plots

Now, we're going back to shapes, and while we've seen tha using a 3D coordinate system abstraction can be valuable when it comes to creating certain shapes, for some other shapes it can be vastly counter-productive and counter-efficient.

The **cone** example.

```latex


\begin{tikzpicture}
\begin{scope}[x={(1cm,0cm)},
              y={(0.5cm,0.5cm)},
              z={(0cm,1cm)}]

    \def\rx{1.5}

    \pgfmathsetmacro{\startangle}{180} % min = 180
    \pgfmathsetmacro{\endangle}{300} % max = 360

    \pgfmathsetmacro{\baselength}{(cos(\startangle - 180) + cos(360 - \endangle)) * \rx}

    \pgfmathsetmacro{\xapex}{\baselength / 2}
    \pgfmathsetmacro{\yapex}{2}

    \coordinate (S) at (\xapex, \yapex, 3);

    \fill [ color=red!60
          ] (0,0,0) arc[start angle = 180,
                        end angle = 360,
                        x radius = \rx cm,
                        y radius = \rx cm]
                    -- (S)
                    -- cycle;

    \fill [ color=gray!60
          ] (0,0,0) arc[start angle = \startangle,
                        end angle = \endangle,
                        x radius = \rx cm,
                        y radius = \rx cm]
                    -- (S)
                    -- cycle;

\end{scope}
\end{tikzpicture}


```

![3DB1.png](../assets/common_files/images_latex/3DB1.png)

Wow, there is A LOT going on there.

First, some macro definitions.

The radius for the cone base -> arc.

```latex


\def\rx{1.5}


```

Second, we define the arc start and end angle of the arc?

```latex


\pgfmathsetmacro{\startangle}{180}
\pgfmathsetmacro{\endangle}{300}


```

After, we will do something very weird, but in fact it is to keep the apex exactly at the center of the arc base.

so, we just compulte the total length of the base with the angles chosen.

```latex


\pgfmathsetmacro{\baselength}{(cos(\startangle - 180) + cos(360 - \endangle)) * \rx}


```

This is the length for the left part of the arc.

```latex


cos(\startangle - 180)


```

`\startangle` belongs to 180 - 270, so the greater it is, the closer `\startangle - 180` is to 90, so the closer `cos(\startangle - 180)` is to 0.

We just apply the same logic for the second part of the arc.

```latex


cos(360 - \endangle))


```

But here, obviously, the greater `\endangle` is, the greater the distance is, so we do this substraction `360 - \endangle`.

Because `\endangle` belongs to 270 to 360.

And of course the apex x is:

```latex


\pgfmathsetmacro{\xapex}{\baselength / 2}


```

And y is fixed to `2`, for example.

You see that this motiv repeats itself 2 times.

```latex


\fill [ color=red!60
      ] (0,0,0) arc[start angle = ANGLE1,
                    end angle = ANGLE2,
                    x radius = \rx cm,
                    y radius = \rx cm]
                -- (S)
                -- cycle;


```

With, of course, `ANGLE2 > ANGLE1`.

There is in fact an overlay of 2 shapes.

We first create a full red base cone:

```latex


\fill [ color=red!60
      ] (0,0,0) arc[start angle = 0,
                    end angle = 360,
                    x radius = \rx cm,
                    y radius = \rx cm]
                -- (S)
                -- cycle;


```

And then overlay the greyish cone that is at maximum as wide as the first, but often narrower, according to the angles chosen.

```latex


\fill [ color=gray!60
      ] (0,0,0) arc[start angle = \startangle,
                    end angle = \endangle,
                    x radius = \rx cm,
                    y radius = \rx cm]
                -- (S)
                -- cycle;


```

To mimic a rotation, we just tweak the angles of the base.

```latex


\begin{tikzpicture}
\begin{scope}[x={(1cm,0cm)},
              y={(0.5cm,0.5cm)},
              z={(0cm,1cm)}]

    \def\rx{1.5}

    \pgfmathsetmacro{\startangle}{180} % min = 180
    \pgfmathsetmacro{\endangle}{350} % max = 360

    \pgfmathsetmacro{\baselength}{(cos(\startangle - 180) + cos(360 - \endangle)) * \rx}

    \pgfmathsetmacro{\xapex}{\baselength / 2}
    \pgfmathsetmacro{\yapex}{2}

    \coordinate (S) at (\xapex, \yapex, 3);

    \fill[ color=red!60
          ] (0,0,0) arc[start angle = 180,
                        end angle = 360,
                        x radius = \rx cm,
                        y radius = \rx cm]
                    -- (S)
                    -- cycle;

    \fill[ color=gray!60
          ] (0,0,0) arc[start angle = \startangle,
                        end angle = \endangle,
                        x radius = \rx cm,
                        y radius = \rx cm]
                    -- (S)
                    -- cycle;

\end{scope}
\end{tikzpicture}


```

![3DB2.png](../assets/common_files/images_latex/3DB2.png)

But you see ?

The result is not really convincing.

So here, that is an examle where a good plain 2D coordinate system is vastly superior to mimic 3D.

But just before doing that, did you see this ?

```latex


\fill[ color=red!60
] (0,0,0) arc[start angle = 180,
                        end angle = 360,
                        x radius = \rx cm,
                        y radius = \rx cm]
                    -- (S)
                    -- cycle;



```

Woow, the **arc** API inside the `\fill` function is much more eleguant than what we have for the same shape but in the `\draw` command !!!!

No redundances, all informations insideoptions.

Btw, we can also use it in draw, that is not specific, here just the interesting part lol.

```latex


\begin{tikzpicture}

    \def\rx{2}
    \def\ry{0.6}
    \def\h{3}

    \coordinate (S) at (0,\h);
    \coordinate (O) at (0,0);

    \draw (-\rx,0) arc[start angle = 180,
                 end angle = 360,
                 x radius = \rx cm,
                 y radius = \ry cm]
    -- (S)
    -- cycle;

\end{tikzpicture}


```

![3DB2B.png](../assets/common_files/images_latex/3DB2B.png)

Also, you see that each node of a shape, can either be a simple point, or a shape itself !!!

```latex


POINT SHAPE -- POINT -- ...


```

Expanding to, for example:

```latex


(0,0,0) arc[start angle = 180,
                        end angle = 360,
                        x radius = \rx cm,
                        y radius = \rx cm]
                    -- (S)
                    -- cycle;


```

--\> "FORMIDABLE !"

Cone now !

```latex


\begin{tikzpicture}

    \def\rx{2}
    \def\ry{0.6}
    \def\h{3}

    \coordinate (S) at (0,\h);
    \coordinate (O) at (0,0);

    \shade[
        left color=gray!50,
        right color=gray!50
    ]
    (-\rx,0) arc[start angle = 180,
                 end angle = 270,
                 x radius = \rx cm,
                 y radius = \ry cm]
    -- (S)
    -- cycle;

    \shade[
       left color=red!50,
       right color=red!50,
    ]
    (\rx,0) arc[start angle = 0,
                 end angle = -90,
                 x radius = \rx cm,
                 y radius = \ry cm]
    -- (S)
    -- cycle;

    \draw (-\rx,0) arc(180:360:\rx cm and \ry cm);

    \draw[dashed] (\rx,0) arc(0:180:\rx cm and \ry cm);

    % edges
    \draw (S) -- (-\rx,0);
    \draw (S) -- (\rx,0);

\end{tikzpicture}


```

![3DB3.png](../assets/common_files/images_latex/3DB3.png)

Same good arc API than for `\fill`, but here with `\shade`, because why not.

This is pretty much the exact same principle than before, but here no weird scoping rules defining the meaning of x, y and z axis.

Just raw 2D coordinates.

Which simplifies A LOT the APEX x coordinate.

Btw, TikZ exposes a `rotate` option.

```latex


\begin{tikzpicture}[rotate=45]

    \def\rx{2}
    \def\ry{0.6}
    \def\h{3}

    \coordinate (S) at (0,\h);
    \coordinate (O) at (0,0);

    \shade[
        left color=gray!50,
        right color=gray!50
    ]
    (-\rx,0) arc[start angle = 180,
                 end angle = 270,
                 x radius = \rx cm,
                 y radius = \ry cm]
    -- (S)
    -- cycle;

    \shade[
       left color=red!50,
       right color=red!50,
    ]
    (\rx,0) arc[start angle = 0,
                 end angle = -90,
                 x radius = \rx cm,
                 y radius = \ry cm]
    -- (S)
    -- cycle;

    \draw (-\rx,0) arc(180:360:\rx cm and \ry cm);

    \draw[dashed] (\rx,0) arc(0:180:\rx cm and \ry cm);

    % edges
    \draw (S) -- (-\rx,0);
    \draw (S) -- (\rx,0);

\end{tikzpicture}


```

![3DB4.png](../assets/common_files/images_latex/3DB4.png)

But, more importantly, we can rotate around our own point in the tikZ picture, which is insanely good !

Check this, we rotate around the apex that we already named `S`.

```latex


\begin{tikzpicture}[rotate around={45:(S)}]

    \def\rx{2}
    \def\ry{0.6}
    \def\h{3}

    \coordinate (S) at (0,\h);
    \coordinate (O) at (0,0);

    \shade[
        left color=gray!50,
        right color=gray!50
    ]
    (-\rx,0) arc[start angle = 180,
                 end angle = 270,
                 x radius = \rx cm,
                 y radius = \ry cm]
    -- (S)
    -- cycle;

    \shade[
       left color=red!50,
       right color=red!50,
    ]
    (\rx,0) arc[start angle = 0,
                 end angle = -90,
                 x radius = \rx cm,
                 y radius = \ry cm]
    -- (S)
    -- cycle;

    \draw (-\rx,0) arc(180:360:\rx cm and \ry cm);

    \draw[dashed] (\rx,0) arc(0:180:\rx cm and \ry cm);

    % edges
    \draw (S) -- (-\rx,0);
    \draw (S) -- (\rx,0);

\end{tikzpicture}


```

![3DB5.png](../assets/common_files/images_latex/3DB5.png)

But how to mimic a rotation "in deph" --> around x axis.

Look at that, a mimic to a negative rotation around x axis, approximately 45 degrees, (not exact maths).

```latex


\begin{tikzpicture}

    \def\rx{2}
    \def\ry{0.7}
    \def\h{2}

    \coordinate (S) at (0,\h);
    \coordinate (O) at (0,0);

    \fill[
        color=white
    ]
    (-\rx,0) arc[start angle = 180,
                 end angle = 360,
                 x radius = \rx cm,
                 y radius = \ry cm]
    -- (S)
    -- cycle;

    \draw[thin] (-\rx,0) arc(180:360:\rx cm and \ry cm);

    \draw[thick] (\rx,0) arc(0:180:\rx cm and \ry cm);

    % edges
    \draw (S) -- (-\rx,0);
    \draw (S) -- (\rx,0);

    \draw[thick] (S) -- (0,\ry);
    \draw[thick, dashed] (0, \ry) -- (0,-\ry);

\end{tikzpicture}


```

![3DB6.png](../assets/common_files/images_latex/3DB6.png)

We just tweak the apex coordinates and the x and y radius of the base, to give them approximated coordinates after a rotation around x by 45 degrees.

If we want the exact maths:

Because height is 3, so here it is `cos(PI / 4) * 3` (in general case, but can be `sin(PI / 4) * 3` here, because of special rotation value where cos(PI / 4) = sin(PI / 4)) approximately `2.12`.

And x radius does not change, obviously.

But `\ry` goes from `0.6` to `0.6 * (1 + sin(PI / 4))`, so approximately `1.02`.

```latex


\begin{tikzpicture}

    \def\rx{2}
    \def\ry{1.02}
    \def\h{2.12}

    \coordinate (S) at (0,\h);
    \coordinate (O) at (0,0);

    \fill[
        color=white
    ]
    (-\rx,0) arc[start angle = 180,
                 end angle = 360,
                 x radius = \rx cm,
                 y radius = \ry cm]
    -- (S)
    -- cycle;

    \draw[thin] (-\rx,0) arc(180:360:\rx cm and \ry cm);

    \draw[thick] (\rx,0) arc(0:180:\rx cm and \ry cm);

    % edges
    \draw (S) -- (-\rx,0);
    \draw (S) -- (\rx,0);

    \draw[thick] (S) -- (0,\ry);
    \draw[thick, dashed] (0, \ry) -- (0,-\ry);

\end{tikzpicture}


```

![3DB7.png](../assets/common_files/images_latex/3DB7.png)

--\> Much more convincing ! -- now you just have to fil some area with more or les dark color to make full illusion

And, remember your geometry courses, all rotations we can do aound x, y and z axis in a fixed or not fixed coordinate system CAN be done in a sequence of rotations on simply x and y axis !!

We've seen we can do y rotation, and now x rotation, so this is actually **rotation complete**.

Isn't that beautiful ?

Now, some other shapes.

Cylinder.

```latex


\begin{tikzpicture}
\begin{scope}[x={(1cm,0cm)},
              y={(0.5cm,0.5cm)},
              z={(0cm,1cm)}]

    \coordinate (O) at (0,0,0);
    \coordinate (T) at (0,0,3);

    \def\rx{1.5}
    \def\ry{0.5}

    \draw (O) ellipse (\rx cm and \ry cm);
    \draw (T) ellipse (\rx cm and \ry cm);

    \draw (-\rx, 0, 0) -- (-\rx, 0, 3);
    \draw (\rx, 0, 0) -- (\rx, 0, 3);

\end{scope}
\end{tikzpicture}


```

![3DB8.png](../assets/common_files/images_latex/3DB8.png)

Nothing to add, you now understand all of this code.

Another cylinder example.

```latex


\begin{tikzpicture}
\begin{scope}[x={(1cm,0cm)},
              y={(0.5cm,0.5cm)},
              z={(0cm,1cm)}]

    \coordinate (O) at (0,0,0);
    \coordinate (T) at (6,1,1);

    \def\rx{0.65}
    \def\ry{1}

    \fill[color=gray!80]
                     (0, 0, \ry)
                     arc[start angle = 90,
                          end angle = 270,
                          x radius = \rx cm,
                          y radius = \ry cm]
                      -- (6, 1, 1 - \ry )
                      arc[start angle = -90,
                          end angle = 90,
                          x radius = \rx cm,
                          y radius = \ry cm]
                      -- (0, 0, \ry);

    \draw (6, 1, \ry + 1)
          arc[start angle=90,
              end angle=-90,
              x radius=\rx cm,
              y radius=\ry cm]
          -- (6, 1, 1 - \ry);

    \draw[fill=black,
          opacity=0.5] (O) ellipse (\rx cm and \ry cm);

    \draw (0, 0, \ry)
           -- (6, 1, \ry + 1);
    \draw (6, 1, 1 - \ry)
          -- (0, 0, -\ry);

\end{scope}
\end{tikzpicture}


```

![3DB9.png](../assets/common_files/images_latex/3DB9.png)

Again, overlays.

The shape.

```latex


\begin{tikzpicture}
\begin{scope}[x={(1cm,0cm)},
              y={(0.5cm,0.5cm)},
              z={(0cm,1cm)}]

    \coordinate (O) at (0,0,0);
    \coordinate (T) at (6,1,1);

    \def\rx{0.65}
    \def\ry{1}

    \draw (6, 1, \ry + 1)
          arc[start angle=90,
              end angle=-90,
              x radius=\rx cm,
              y radius=\ry cm]
          -- (6, 1, 1 - \ry);

    \draw[fill=black,
          opacity=0.5] (O) ellipse (\rx cm and \ry cm);

    \draw (0, 0, \ry)
           -- (6, 1, \ry + 1);
    \draw (6, 1, 1 - \ry)
          -- (0, 0, -\ry);

\end{scope}
\end{tikzpicture}


```

![3DB10.png](../assets/common_files/images_latex/3DB10.png)

And, the "Texture".

```latex


\begin{tikzpicture}
\begin{scope}[x={(1cm,0cm)},
              y={(0.5cm,0.5cm)},
              z={(0cm,1cm)}]

    \coordinate (O) at (0,0,0);
    \coordinate (T) at (6,1,1);

    \def\rx{0.65}
    \def\ry{1}

    \fill[color=gray!80]
                     (0, 0, \ry)
                     arc[start angle = 90,
                          end angle = 270,
                          x radius = \rx cm,
                          y radius = \ry cm]
                      -- (6, 1, 1 - \ry )
                      arc[start angle = -90,
                          end angle = 90,
                          x radius = \rx cm,
                          y radius = \ry cm]
                      -- (0, 0, \ry);

\end{scope}
\end{tikzpicture}


```

![3DB11.png](../assets/common_files/images_latex/3DB11.png)

## PGFPlot, again

Now, we can speak more about 3D PGFPLOT.

Look.

```latex


\begin{tikzpicture}
\begin{axis}[
    hide axis,
]
    \addplot3[
        surf,
        domain=0:180,
        y domain=0:180,
    ]
    ({cos(x)},
     {sin(x)},
     {1});
\end{axis}
\end{tikzpicture}


```

![PGF1.png](../assets/common_files/images_latex/PGF1.png)

```latex


\begin{tikzpicture}
\begin{axis}[
    hide axis,
]
    \addplot3[
        surf,
        domain=0:180,
        y domain=0:180,
    ]
    ({cos(x)},
     {sin(x)},
     {cos(y)});
\end{axis}
\end{tikzpicture}


```

![PGF2.png](../assets/common_files/images_latex/PGF2.png)

```latex


\begin{tikzpicture}
\begin{axis}[
    hide axis,
]
    \addplot3[
        surf,
        domain=0:180,
        y domain=0:180,
    ]
    ({cos(x)},
     {sin(x)},
     {sin(y)});
\end{axis}
\end{tikzpicture}


```

![PGF3.png](../assets/common_files/images_latex/PGF3.png)

What is going on here ?

Well, yo just defining Surface points.

In fact that is basically:

- FX(input) = X --> `cos(x)`

- FY(input) = Y --> `sin(x)`


And here Z is just a constant 1, this is why first exampe just output, not a surface but a demi-circle.

But the key to surfaces is Z axis.

That is why in the second example, we got a surface.

Multiple points on Z axis are computed for each points on x and y axis. --> Surface.

And we got a nice color gradient indicating the z axis, even if not visually indicated elsewhere because of `hide axis` option in `axis` environment.

Now, why the second example looks like it output the same surface in different camera angle.

In fact that is exactly the same angle.

But the illusion is **PGFPlot painter algorithm ORDER**

Look, in the second example, we provided for z, `cos(y)`.

So at first y is `sin(x)` -\> 0.

Then, at first `cos(y)` -\> tends to 1.

So the top lines lines / meshes are painted first.

That is exactly the opposite order of the third example where z is defined as: `sin(y)`.

Now, i want to make this article sort of "interractive", could you explain what is going on here ?

```latex


\begin{tikzpicture}
\begin{axis}[
    hide axis,
]
    \addplot3[
        surf,
        domain=0:180,
        y domain=0:180,
    ]
    ({sin(x)},
     {cos(x)},
     {sin(y)});
\end{axis}
\end{tikzpicture}


```

![PGF4.png](../assets/common_files/images_latex/PGF4.png)

### Camera angles !

First look at this surface.

```latex


\begin{tikzpicture}
\begin{axis}

    \addplot3[surf,
              samples = 30,
              samples y = 30] {x^2 + y^2};

\end{axis}
\end{tikzpicture}


```

![PGF5.png](../assets/common_files/images_latex/PGF5.png)

By the way , we got an hint on how the samples are created, it first is segmanted according to the distance on the concenred axis, x for `samples` and y for `samples y`. Then, the meshes are distorted following the other axis values.

That is why meshes at the edges of the x axis looks wider then the meshes in the center.

Around x = -4.

![PGF6.png](../assets/common_files/images_latex/PGF6.png)

Around x = 0.

![PGF7.png](../assets/common_files/images_latex/PGF7.png)

But, we are here to discuss the camera angles of a PGFPlot.

Take a look.

```latex


\begin{tikzpicture}
\begin{axis}[view={50}{50}]

    \addplot3[surf] {x^2 + y^2};

\end{axis}
\end{tikzpicture}


```

![PGF8.png](../assets/common_files/images_latex/PGF8.png)

Maybe that you get it, you surely do because you are smart, how do i know that ? -- you are reading my article, that's enough.

It is:

```latex


\begin{axis}[view={Z_AXIS_ROTATION}{X_AXIS_ROTATION}]


```

Expanding to, for example.

```latex


\begin{axis}[view={50}{50}]


```

Another example witth x = -50 degrees.

```latex


\begin{tikzpicture}
\begin{axis}[view={50}{-50}]

    \addplot3[surf] {x^2 + y^2};

\end{axis}
\end{tikzpicture}


```

![PGF9.png](../assets/common_files/images_latex/PGF9.png)

### 3D Plots

#### BarPlots

Nothing new, you already should be able to read this like it's your native language.

```latex


\begin{tikzpicture}
\begin{axis}[xlabel=$x$,
             ylabel=$y$,
             zlabel=$z$]

    \addplot3[only marks,
              scatter,
              scatter src = explicit,
              mark=*,
              colormap name=myinferno] coordinates {
    (1,2,3) [0.6]
    (2,1,4) [0.2]
    (3,3,2) [0.9]
    (4,2,5) [0.4]
              };

\end{axis}
\end{tikzpicture}


```

![PGF10.png](../assets/common_files/images_latex/PGF10.png)

Ooor, maybe not.

Yess, what is `scatter src = explicit` ?

And why the gradient option with `colormap name=myinferno`.

Remember that `myinferno` is a preamble defined colormap gradient as:

```latex


\pgfplotsset{ %define custom pgfplot theme, heatmap
  colormap={myinferno}{
    rgb255(0cm)=(0,0,4);
    rgb255(1cm)=(31,12,72);
    rgb255(2cm)=(85,15,109);
    rgb255(3cm)=(136,34,106);
    rgb255(4cm)=(186,54,85);
    rgb255(5cm)=(227,89,51);
    rgb255(6cm)=(249,140,10);
    rgb255(7cm)=(249,201,50);
    rgb255(8cm)=(252,255,164);
  }
}


```

Great !

We can anwser those questions with the same response.

You see that in `coordinates`, we defined points not only with their coordinates, but with an attached value between "\[" and "\]".

That is the color scale, that (recall) is normalized by the engine taking in count the min and max value.

So putting the `scatter src = explicit` tells that WE control the color of EACH point.

That is not the engine responsability here to infere their color based on their location on the coordinate system.

Or with the infamous `table`.

```latex


\begin{tikzpicture}
\begin{axis}[xlabel=$x$,
             ylabel=$y$,
             zlabel=$z$]

    \addplot3[only marks,
              mark=*,
              scatter,
              scatter src = explicit
    ] table[col sep=comma,
            y=y,
            x=x,
            z=z,
            meta=color] {scatterplot3D.csv};

\end{axis}
\end{tikzpicture}


```

![PGF11.png](../assets/common_files/images_latex/PGF11.png)

scatterplot3D.csv:

```text


x,y,z,color
1,2,3,0.1
2,1,4,0.6
3,3,2,0.2
4,2,5,0.9


```

The color is a metadata information, that's why we used `meta=color` in option of `table` function.

In the following, this is the engine responsability to map color to each points.

```latex


\begin{tikzpicture}
\begin{axis}[xlabel=$x$,
             ylabel=$y$,
             zlabel=$z$]

    \addplot3[only marks,
              scatter,
              mark=*,
              colormap name=myinferno] coordinates {
    (1,2,3)
    (2,1,4)
    (3,3,2)
    (4,2,5)
              };

\end{axis}
\end{tikzpicture}


```

![PGF12.png](../assets/common_files/images_latex/PGF12.png)

You see that we see a lot of the gradient color.

In fact what it does is very straight forward and very coherent from what we've seen so far.

Computes the lower and uper bounds of the z axis, samples the colors of the gradient between these bounds, and just map the gradient color to the points according to their z coordinates.

Experimenting with this plot, i found that it can be very good for representing the evolution of the positions of an object. Just adding a smooth line between **contiguous points**.

```latex


\begin{tikzpicture}
\begin{axis}[xlabel=$x$,
             ylabel=$y$,
             zlabel=$z$]

    \addplot3[mark=*,
              scatter,
              scatter src = explicit,
              smooth
    ] table[col sep=comma,
            y=y,
            x=x,
            z=z,
            meta=color] {scatterplot3D2.csv};

\end{axis}
\end{tikzpicture}


```

![PGF13.png](../assets/common_files/images_latex/PGF13.png)

We've seen surfaces before, but the meshes were filled, here a surface where meshes arenot filled !

We do that by putting the option `mesh`.

```latex


\begin{tikzpicture}
\begin{axis}[grid=major,view={210}{30}]

    \addplot3+[mesh,
               samples=10,domain=0:1]
		{5*x*sin(2*deg(x)) * y*(1-y)};

\end{axis}
\end{tikzpicture}


```

![PGF14.png](../assets/common_files/images_latex/PGF14.png)

You see that the edges color of the meshes are also computes according to z coordinate.

We have to add the parameter `scatter` to make also the points color behave like the edges color.

```latex


\begin{tikzpicture}
\begin{axis}[grid=major,view={210}{30}]

    \addplot3+[mesh,
               scatter,
               samples=10,domain=0:1]
		{5*x*sin(2*deg(x)) * y*(1-y)};

\end{axis}
\end{tikzpicture}


```

![PGF15.png](../assets/common_files/images_latex/PGF15.png)

### 3D BarPlots

Now, some 3D barplots.

```latex


\begin{tikzpicture}
\begin{axis}[
    xlabel=$x axis$,
    zlabel=$values$,
    ylabel=$y axis$,
    symbolic x coords={A,B,C},
    symbolic y coords={X,Y,Z},
    xtick=data,
    ytick=data,
    enlargelimits=0.15
]

    \addplot3[
        ybar,
        fill=blue!50,
    ]
    table[
        col sep=comma,
        x=xlabel,
        y=zlabel,
        z=value
    ] {barplot3D.csv};

\end{axis}
\end{tikzpicture}


```

![PGF16.png](../assets/common_files/images_latex/PGF16.png)

In fact the only thing new here, is the combination of the `ybar` option in the `\addplot3` function.

barplot3D.csv

```text


xlabel,zlabel,value
A,X,33
A,Y,2
A,Z,67
B,X,23
B,Y,12
B,Z,17
C,X,32
C,Y,22
C,Z,37


```

### Ternary Diagramm

Now, some memories of when i was chemist, the infamous ternary diagrams.

I found this example on Christian Feuersänger website: [https://pgfplots.net/author/christian/](https://pgfplots.net/author/christian/), the author of PGFPlot.

```latex


\begin{tikzpicture}
\begin{ternaryaxis}[
	title=Want--be--Stainless Steel,
	xlabel=Weight Percent Chromium,
	ylabel=Weight Percent Iron,
	zlabel=Weight Percent Nickel,
	label style=sloped,
	area style,
  ]
	\addplot3 table {
	1 0 0
	0.5 0.4 0.1
	0.45 0.52 0.03
	0.36 0.6 0.04
	0.1 0.9 0
	};
	\addlegendentry{Cr}

	\addplot3 table {
	1 0 0
	0.5 0.4 0.1
	0.28 0.35 0.37
	0.4 0 0.6
	};
	\addlegendentry{Cr+$\gamma$FeNi}

	\addplot3 table {
	0.4 0 0.6
	0.28 0.35 0.37
	0.25 0.6 0.15
	0.1 0.9 0
	0 1 0
	0 0 1
	};
	\addlegendentry{$\gamma$FeNi}

	\addplot3 table {
	0.1 0.9 0
	0.36 0.6 0.04
	0.25 0.6 0.15
	};
	\addlegendentry{Cr+$\gamma$FeNi}

	\addplot3 table {
	0.5 0.4 0.1
	0.45 0.52 0.03
	0.36 0.6 0.04
	0.25 0.6 0.15
	0.28 0.35 0.37
	};
	\addlegendentry{$\sigma$+$\gamma$FeNi}

	\node[inner sep=0.5pt,
          circle,
          draw,
          fill=white,
	      pin=-15:\footnotesize Stainless Steel
    ] at (axis cs:0.18,0.74,0.08) {};

\end{ternaryaxis}
\end{tikzpicture}


```

![PGF17.png](../assets/common_files/images_latex/PGF17.png)

First, what does this represent ?

It represent the compositions (in percentage) of a "solution" by 3 elements.

One elemnt at each apex of the triangle.

How to determine the composition of a solution if i pin point you a random point on the triangle area ?

Take this point for example:

![PGF18.png](../assets/common_files/images_latex/PGF18.png)

Now, i want to get its composition.

For this, you have to associate its lines directions to an element.

You see ?

There are 3 lines directions.

One horizontal, this is perrfectly parallel to the base,

Now, to which element does it map ?

Easy one, you just look at when this line crosses the 0 of one of the elment (edge).

For this one it is the bottom right apex, it maps to **Chromium**.

So we got the information that this solution is made of 20% of mass of Chromium.

The same logic applies for the 2 remaining lines direction.

The line that has a "negative" (top to bottom) direction maps to **Iron**.

So the element is made of 40% of Iron.

We can deduce that this solution is also made of 40% of **Nickel** (to make up to 100%).

And to get the "properties" / "details" of this solution, just look at the legend of the color the solution point is in.

Here it is beige, so gammaFeNi, whatever it means, don't ask me lol.

Now let's dissect the code.

The new thing is this `ternaryaxis` environment, required for drawing this.

This is also very common to add it the option `area style` which is much better for results interpretations, because if not provided, areas are not filled.

```latex


\begin{tikzpicture}
\begin{ternaryaxis}[
	title=Want--be--Stainless Steel,
	xlabel=Weight Percent Chromium,
	ylabel=Weight Percent Iron,
	zlabel=Weight Percent Nickel,
	label style=sloped,
  ]
	\addplot3 table {
	1 0 0
	0.5 0.4 0.1
	0.45 0.52 0.03
	0.36 0.6 0.04
	0.1 0.9 0
	};
	\addlegendentry{Cr}

	\addplot3 table {
	1 0 0
	0.5 0.4 0.1
	0.28 0.35 0.37
	0.4 0 0.6
	};
	\addlegendentry{Cr+$\gamma$FeNi}

	\addplot3 table {
	0.4 0 0.6
	0.28 0.35 0.37
	0.25 0.6 0.15
	0.1 0.9 0
	0 1 0
	0 0 1
	};
	\addlegendentry{$\gamma$FeNi}

	\addplot3 table {
	0.1 0.9 0
	0.36 0.6 0.04
	0.25 0.6 0.15
	};
	\addlegendentry{Cr+$\gamma$FeNi}

	\addplot3 table {
	0.5 0.4 0.1
	0.45 0.52 0.03
	0.36 0.6 0.04
	0.25 0.6 0.15
	0.28 0.35 0.37
	};
	\addlegendentry{$\sigma$+$\gamma$FeNi}

	\node[inner sep=0.5pt,
          circle,
          draw,
          fill=white,
	      pin=-15:\footnotesize Stainless Steel
    ] at (axis cs:0.18,0.74,0.08) {};

\end{ternaryaxis}
\end{tikzpicture}


```

![PGF19.png](../assets/common_files/images_latex/PGF19.png)

And now look at that it will make sense for the area drawing:

```latex


xlabel=Weight Percent Chromium,
ylabel=Weight Percent Iron,
zlabel=Weight Percent Nickel,


```

Now you get the mapping of element to axis.

so you can easily undertand the blue area definition (the first one, the one that is long and not wide at the left edge).

```latex


\addplot3 table {
1 0 0
0.5 0.4 0.1
0.45 0.52 0.03
0.36 0.6 0.04
0.1 0.9 0
};
\addlegendentry{Cr}


```

We put enough point entries to samle the area as precisely aswe can (data from experiments).

The `label style=sloped` option is aso very common, it make the label parallel to the axis, if not set, it can easily become a mess.

### PolarAxis

for this one, you have to import the `polar` PGFPlot library.

```latex


\usepgfplotslibrary{polar}


```

Code:

```latex


\begin{tikzpicture}
\begin{polaraxis}

	\addplot[mark=none,domain=0:180,samples=600]
		{sin(x)};

\end{polaraxis}
\end{tikzpicture}


```

![PGF20.png](../assets/common_files/images_latex/PGF20.png)

Some maths did not kill anyone right ? Right ?

Basically, we are in a polar axis.

X (as in `sin(x)`) is the angle `theta`.

What we have control of here is the formula that computes the radius `r`, and here we put `sin(x) = theta`.

"Okok, wtf, `theta`, `r` whatever, how is that linked to the 2D plots, because at the end of the day the engine **must compute actual x and y coordinates in a cartesian coordinate system**."

You are right.

Simple enough the relation is:

- `x (hidden cartesian coordinate system)` -\> `r * cos(theta)`

- `y (hidden cartesian coordinate system)` -\> `r * sin(theta)`


So in the particular case where `theta = sin(x)`, that is:

- `x = sin(theta) * cos(theta)`

- `y = sin^2(theta)`


Look, you see the absolute max x values are `0.5`, because at `PI / 4 approx 0.70` we have `x = 0.70*0.70 = 0.5`.

That's all.

We already drew the right half of the circle just with `theta` being between `0` and `90`.

And with `theta` being between `90` and `180`, we just draw the left half of the circle.

Look, if we want to draw the first quarter:

```latex


\begin{tikzpicture}
\begin{polaraxis}

	\addplot[mark=none,domain=0:45,samples=600]
		{sin(x)};

\end{polaraxis}
\end{tikzpicture}


```

![PGF21.png](../assets/common_files/images_latex/PGF21.png)

Look at the evolution of the x coordinates:

```latex


\begin{tikzpicture}
    \begin{axis}[domain=-3.14:3.14]

    \addplot[samples = 200] {sin(deg(x)) * cos(deg(x))};

\end{axis}
\end{tikzpicture}


```

![PGF22.png](../assets/common_files/images_latex/PGF22.png)

Here, because the `cos` and `sin` functions takes degrees, we convert radians ( `-3.14` to `3.14`) to degrees with `deg(...)`.

If we zoom in from `0` to `PI / 2` approx `1.57`, we see that it has the range to do a full pattern, from `y = 0` to `y = 0`.

```latex


\begin{tikzpicture}
    \begin{axis}[domain=0:1.57]

    \addplot[samples = 200] {sin(deg(x)) * cos(deg(x))};

\end{axis}
\end{tikzpicture}


```

![PGF23.png](../assets/common_files/images_latex/PGF23.png)

That is coherent with what was ouputed in the `polaraxis`.

Here, we have:

`sin(x) * cos(x)` -\> `sin(x) * sin(PI / 2 - x)`

We got the identity:

`sinA * sinB = 1/2[cos(A - B) - cos(A + B)]`

So we just replace.

`1/2 * [cos(x - (PI / 2 - x)) - cos(x + (PI / 2 - x))]`

-\> `1/2 * [cos(-(PI / 2) + 2x) - cos(PI / 2)]`

-\> `1/2 * cos(-(PI / 2) + 2x)`

-\> `1/2 * cos(2x - (PI / 2))`

again the first relation we used...

-\> `1/2 * sin(PI / 2 - (2x - (PI / 2)))`

-\> `1/2 * sin(PI - 2x)`

And because of the mirroring that gives `sin(PI - u) = sin(u)`, we have:

-\> `1/2 * sin(2x)`

It has a greater frequence (but smaller amplitude) than standard `sin(x)`.

Look, on the same domain `-5:5`.

```latex


\begin{tikzpicture}
\begin{axis}[domain=-5:5]
    \addplot[samples=200] {sin(deg(x))};
\end{axis}
\end{tikzpicture}


```

![osc1.png](../assets/common_files/images_latex/osc1.png)

```latex


\begin{tikzpicture}
\begin{axis}[domain=-5:5]
    \addplot[samples=200] {0.5 * sin(deg(2 * x))};
\end{axis}
\end{tikzpicture}


```

![osc2.png](../assets/common_files/images_latex/osc2.png)

I'm gonna give you another example.

Now you can think about this beautiful example.

```latex


\begin{tikzpicture}
\begin{polaraxis}

	\addplot[mark=none,domain=0:720,samples=600]
		{sin(x) * cos(x)};

\end{polaraxis}
\end{tikzpicture}


```

![PGF24.png](../assets/common_files/images_latex/PGF24.png)

Or this one.

```latex


\begin{tikzpicture}
\begin{polaraxis}

	\addplot[mark=none,domain=0:720,samples=600]
		{sin(2*x) * cos(2*x)};

\end{polaraxis}
\end{tikzpicture}


```

![PGF25.png](../assets/common_files/images_latex/PGF25.png)

## LaTeX is more than just markup

Even if i have massively anouced what we can do in LaTeX macro, here we'll go further.

First, recall the basics.

```latex


\def\a{Rémi}
\def\b{Julien}


```

Then, use it as:

```latex


Bonjour \a\ et \b.

Bonjour \a{} et \b.


```

Each one outputs the same result.

"Bonjour Rémi et Julien."

And yess, that is strange that we can call the variable like a comand with empty `{}`.

Speaking of commands, they are in fact, like said before, fancy variables with fancy logic.

```latex


\newcommand{\hello}[3]{Hello #1, #2 et #3}


```

Used like:

```latex


\hello{Rémi}{Julien}{Lucas}


```

Output: "Hello rémi, julien et Lucas"

This stays pure expansions...

Now most confusing part of LaTeX.

How to reassign a value to a variable ?

Maybe, you think this is done simply by.

```latex


\def\a{\b}


```

It works if you just use the `\a` variable after just to outputs its value, it does raw expansion.

```latex


\a


```

Expands to "Julien".

BUT !

When you use it in comparisons functions such as:

```latex


\ifx\a\b
OUI
\else
NO
\fi


```

Is `\a` **definitions** equals to `\b`. -\> "NO"

It is another thing entirely.

In fact this function does not expand any of the variabe, but just checks for the last definition value.

So, the right way to **REDEFINE**, that's the word lol, a variable, is using `\edef`.

Example:

```latex


\edef\a{\b}

\ifx\a\b
OUI
\else
NO
\fi


```

Outputs "OUI".

`\gdef` is like `\def` but survives any scope `{...}`

`\xdef` is like `\edef` but survives any scope `{...}`

I already introduced you to comparisons function with `\ifx`.

Its synthax is:

```latex


\ifx\VAR\OTHERVAR
CODE1
\else
CODE2
\fi


```

Or just.

```latex


\ifx\VAR\OTHERVAR
CODE1
\fi


```

From `xstring` package we can use this function too:

```latex


\IfStrEq{CONTENT1}{CONTENT2}{CODESUCCESS}{CODEFAILURE}


```

Expanding, for example to:

```latex


\IfStrEq{\a}{Rémi}{YES}{NO}


```

Often better practice.

"For now, that is just for variable raw definition comparison, but would'nt it be cool if we had smarter comparisons functions that gets the type of what we are comparing and accept operators ??"

"Idk, maybe like comparing variables that can be interpreted as numbers right ?"

It EXISTS !

Introducing `\ifnum`.

```latex


\ifnum 5 > 3
OUI
\else
NO
\fi


```

--\> "OUI"

```latex


\ifnum 5 = 3
OUI
\else
NO
\fi


```

--\> "NO"

```latex


\ifnum 5 < 3
OUI
\else
NO
\fi


```

--\> "NO"

You can also compare length, neat, but i can not find a comon scenario where it is necessary.

Maybe when you have a work and that you change dimensions (stored in a variable) on the fly to see what formatting works the best.

```latex


\ifdim 2cm>1cm
OUI
\else
NO
\fi


```

--\> "OUI"

Now introducing the most basic `if` comparison function... the `\ifBOOLEAN`.

```latex


\iftrue
OUI\_A
\fi


```

--\> "OUI\_A"

```latex


\iffalse
OUI\_B
\fi


```

--\> NOTHING

Why am i bringing that onto the table, because of a way to manipulate boolean variables.

We declare them like that:

```latex


\newif\ifcool


```

The variable name is `cool`.

The synthax is weird:

```latex


\newif\ifVARNAME


```

Now we set its boolean value doing so:

```latex


\VARNAMEBOOLEANVALUE


```

Expanding to, for example:

```latex


\cooltrue


```

And after its expansions that does not even require the infamous `\`, we can use it in basic boolean comparison `if`.

```latex


\ifcool
OUI
\else
NO
\fi


```

--\> "OUI"

After.

```latex


\coolfalse

\ifcool
OUI
\else
NO
\fi


```

--\> "NO"

Now look at that.

```latex


\def\coolbtrue{\let\coolb\iftrue}
\def\coolbfalse{\let\coolb\iffalse}

\coolbtrue

\coolb
OUIA
\else
NOA
\fi

\coolbfalse

\coolb
OUIB
\else
NONB
\fi


```

First, outputs "OUIA" then "NONB".

Why ?

Because we used `\let`.

```latex


\let\a\b


```

Tells TeX to make `\a` behave exactly the same as `\b`. --\> **SAME TOKEN**

Now a basic thing, check emptyness of variable.

```latex


\def\x{}

\ifx\x\empty
EMPTY
\else
NOT EMPTY
\fi


```

--\> "EMPTY"

### Loops

```latex


\foreach \xb in {1,2,3,4} {
    \IfStrEq{\xb}{4}{END}{Value: \xb \\}
}


```

Outputs:

```text


Value: 1
Value: 2
Value: 3
END


```

Or we can also define the variable list we will iterate on.

```latex


\def\lst{1A,2B,3C,4E}

\foreach \xb in \lst {
    \IfStrEq{\xb}{4}{END}{Value: \xb \\}
}


```

Outputs:

```text


Value: 1A
Value: 2B
Value: 3C
Value: 4D


```

So, you get it, elements must be separated by a comma.

You can even append to a list, look we create `\lstb` list and append elements to it using the **expansion property** of `\edef`.

```latex


\def\lstb{}
\edef\lstb{\lstb 1}
\edef\lstb{\lstb,2}
\edef\lstb{\lstb,2}
\edef\lstb{\lstb,3}

\foreach \xb in \lstb {
    \IfStrEq{\xb}{4}{END}{Value: \xb \\}
}


```

Outputs:

```text


Value: 1
Value: 2
Value: 3
Value: 4


```

Neat !

But, wait wait wait, there is so much more, hope you are ready !

### Pattern Matching

Hang up your belt, because here we enter a special zone.

Look at this:

We first define a list containing key values pairs, defined as `(key/value)`.

Note the `/` --\> IMPORTANT !!!

```latex


\def\pairs{{A/1},{B/2},{C/3},{D/4}}


```

Then the loop.

```latex


\foreach \x/\y in \pairs {
    \x : \y \\
}


```

Outputs:

```text


A: 1
B: 2
C: 3
D: 4


```

YESSS, Pattern matching, that's right !!

That opens an enormous amount of possibilities !

At this point it is a bit like haskell haha.

To emphasize this concept i made this example.

```latex


\def\pairsb{{A/1/A1},{B/2/B2},{C/3/C3},{D/4/D4}}

\foreach \x/\y/\z in \pairsb {
    \x : \y : \z \\
}


```

Outputs:

```text


A: 1: A1
B: 2: B2
C: 3: C3
D: 4: D4


```

Or this one.

```latex


\def\pairsb{{A/{1/A1}},{B/{2/B2}},{C/{3/C3}},{D/{4/D4}}}


```

Note that here, we don't mind `\edef` because what matters in the loop is the value, not the last definition, because the pattern matching automatically **expands** the element.

Also note that here instead of having all on the same level, we scoped the inner level between `{...}` allowing for the TeX tokenizer to match a whole group as one entity and to pass this entity to a function ( `\splittemp`) that will discover further subgroups with pattern matching (decomposition).

Then, we declare a macro that does pattern matching on its input literally, not even a `\newcommand`, no just plain old `\def`.

```latex


\def\splittemp#1/#2-{
    \x : #1 - #2 \\
}


```

It actually **splits** its input by the pattern matching in finds and assign a variable position to each group it made after the patter match ( `#1` and `#2`).

So, finaly the loop:

```latex


\foreach \x/\temp in \pairsb {
    \expandafter\splittemp\temp-
}


```

Yess it is literally giving the input to the macro expanding the group pattern matched by the loop, so it expands `\temp` to its actual value.

Normally when we call a macro, we expects it to be automatically expanded, but here `\expandafter` is an insurance.

Thanks to `\expandafter\A\B` that does expands `\B` before giving it to `\A`.

Here:

```latex


\expandafter\splittemp\temp-


```

Note that we gave a last separator, being `-` at the end to correcty create the group `#2`.

Ouputs:

```text


A: 1 - A1
B: 2 - B2
C: 3 - C3
D: 4 - D4


```

We could have done the `-` trick with a token that is used often to do that, it has no visual existance, it just exists in the TeX tokenizer.

Introducing `\relax`.

```latex


\def\splittemp#1/#2\relax{
    \x : #1 - #2 \\
}

\foreach \x/\temp in \pairsb {
    \expandafter\splittemp\temp\relax
}


```

Ouputs:

```text


A: 1 - A1
B: 2 - B2
C: 3 - C3
D: 4 - D4


```

### Tree Expansion Example

Okok, here is a list of trees:

```latex


\def\pairsc{{N1/{L/V1}},{N2/{R/V2}},{N3/{{L/V3}/{R/V4}}},{N4/{{L/{{L/V5}/{R/V6}}}/{R/V7}}}}


```

Each tree is:

```latex


{NODE/{(L/NODE)/(R/NODE)}}


```

Where a `NODE` is a subtree, so it is also:

```latex


{NODE/{(L/NODE)/(R/NODE)}}


```

Expanding to, for example:

```latex


{N4/{{L/{{L/V5}/{R/V6}}}/{R/V7}}}


```

You note that each subtree has its **own scope**.

Now, the recursivity traversal, how do we think about it ?

First, we think about what is going on when we encounter a leaf, the end path for the tree.

There are two possibilities for a leaf with this tree semantics, wether we encounter the final `Side` or `Value`.

So the macro should be.

```latex


\newcommand{\treeleaf}[1]{
    \IfStrEq{#1}{L}
        {Side: #1}
        {
            \IfStrEq{#1}{R}
                {Side: #1}
                {Value: #1}
        }
}


```

If `L` -\> that is a `Side`, so we output "Side: " and its side, wether "L" (Left) or "R" (Right).

And if no "L" or "R", then that's the value, so "Value: " and its value is outputed.

So the missing piece for enabling a recursivity is a macro that cals itself with, as input the subhroup it just find after the patter matching, or calls `\treeleaf` if it detects that the subgroup is a leaf.

It is exactly what we are going to do except that we will declare two macros that will call eachother following this logic.

```latex


\newcommand{\treesplit}[1]{
    \IfSubStr{#1}{/}
        {
            \expandafter\treesplitaux#1\relax
        }
        {
            \treeleaf{#1}
        }
}

\def\treesplitaux#1/#2\relax{
    (
    \treesplit{#1}
    /
    \treesplit{#2}
    )
}


```

Nothing more to add, you should be able to understand what is going on.

"Wait a minute, are you sure about that?"

"Think again, about the distinction between scoping and raw toekns."

And yess, the subtelty, if we keep this code unchanged, we make a big mistake.

at this stage, you are maybe thinking, that it makes perfect sense, the grouping decomposition made by the patter matching here is fine:

```latex


\expandafter\treesplitaux#1\relax


```

Where `\treesplitaux` is just:

```latex


\def\treesplitaux#1/#2\relax{
    (
    \treesplit{#1}
    /
    \treesplit{#2}
    )
}


```

But in fact this is not.

In fact, here the `\expandafter` is necessary but not sufficient.

It correctly is an insurance to make `#1` expands to its value to something like: `{1/A1}`.

But, it stays scoped !

So this part:

```latex


\treesplitaux#1/#2\relax


```

Never sees the `/`, so it can not do a proper group decomposition.

Then, the chance we have is that `{` and `}` are character, like others.

So, we can manually descope the content to make the function behave as intended.

Because, if we do not do that, we will have weird results, and maybe even outputing some unconsumed tokens --> not in the expected formatting.

The correct code is:

```latex


\newcommand{\treesplit}[1]{%
    \def\TreeTmp{#1}
    \IfBeginWith{\TreeTmp}{\{}{
        \StrGobbleLeft{\TreeTmp}{1}[\TreeTmpA]
        \StrGobbleRight{\TreeTmpA}{1}[\TreeTmp]
    }{}
    \IfSubStr{\TreeTmp}{/}
        {
            \expandafter\treesplitaux\TreeTmp\relax
        }
        {
            \treeleaf{\TreeTmp}
        }
}

\def\treesplitaux#1/#2\relax{%
    ( \treesplit{#1} | \treesplit{#2} )%
}


```

No changes to `\treesplitaux`, but what are the changes brought to `\treesplit`?

First we just assign the parameter to a value:

```latex


\def\TreeTmp{#1}


```

And what do we do with it ?

If it begins with `{` --\> scoped --> need to descope manualy removing manualy first (left) and last (right) char.

That's why we got this in the conditional code.

```latex


\StrGobbleLeft{\TreeTmp}{1}[\TreeTmpA]
\StrGobbleRight{\TreeTmpA}{1}[\TreeTmp]


```

We assign to newly created variable `\TreeTmpA` the `\TreeTmp` variable without its first character ( `1` and `Left`) ( `{`).

Then we assign `\TreeTmpA` back to `\TreeTmp` without its last character ( `1` and `Right`).

After, we apply logic to get if we are at leaf or not, so we continue recursive call.

For this, we have to check if `/` is a **substring** of `\TreeTmp`.

```latex


\IfSubStr{\TreeTmp}{/}
    {
        \expandafter\treesplitaux\TreeTmp\relax
    }
    {
        \treeleaf{\TreeTmp}
    }


```

Now, the real question "What came first ? The egg or the chicken ?"

Idk, but the analogy for those 2 macros is of course `\treesplit`, because we theorically could have a tree composed only with a leaf.

So, in the loop for traversing all the trees, we do the following:

```latex


\foreach \x/\temp in \pairsc {
    \x : \expandafter\treesplit\temp \\
}


```

Hmm, not exactly right.

Why because here **incorrect argument passing**, it is like this example:

```latex


\def\B{123}
\def\A#1{[#1]}

\expandafter\A\B


```

Which outputs:

```text


[1]23


```

Why, because it has no meaning of what the argument is, because ther is no scoping for that argument which is as we know `123`.

But here acts weirdly, at first thinks it is the first letter `1` and for the second call, gets the rest of the letters `23`.

Then maybe try.

```text


\foreach \x/\temp in \pairsc {
    \x : \treesplit{\temp}\par
}


```

--\> FAILS

In fact in `\foreach` ( `pgffor` package), the passing of macro created by `pgffor` are a little weird so when we pass it to a `\newcommand`, we do that:

```latex


\foreach \x/\temp in \pairsc {
    \x : \expandafter\treesplit\expandafter{\temp} \\
}


```

Expands `\temp` after the token `{` and then add token `}`. --\> Literally like a `\treesplit{...}` arg passing but here we just assure that the expansion hapens on `\temp`.

Final beautiful tree output:

```latex


N1: ( Side: L | Value: V1 )
N2: ( Side: R | Value: V2 )
N3: ( ( Side: L | Value: V3 ) | ( Side: R | Value: V4 ) )
N4: ( ( Side: L | ( ( Side: L | Value: V5 ) | ( Side: R | Value: V6
) ) ) | ( Side: R | Value: V7 ) )


```

WOW, traversing a Tree in LateX, something i will remember !

## Finally Doom in LaTeX

How did i create the game ?

First, the architecture.

We have a bash loop script ( `loop.sh`) that waits for inputs.

When it receives input, it updates a `state.tex` variables.

This file is in fact an `\input{...}` of the main LaTeX file `main.tex`.

We won't focus on the bash file, but here is its code:

```bash


#!/bin/bash

# --- INPUT SETUP ---
exec 3</dev/tty
stty -icanon -echo
trap "stty sane" EXIT

# --- STATE ---
step=0
scaleval=0.5
shoot=0
demon=0
gameover=0
lst="0,1,2"
score=0

# --- SCALE PER STEP ---
update_scale() {
  case $step in
    0) scaleval=0.5 ;;
    1) scaleval=0.9 ;;
    2) scaleval=1.4 ;;
  esac
}

# --- DEMON SPAWN ---
spawn_demon() {
  # 30% chance
  if (( RANDOM % 100 < 70 )); then
    demon=1
    echo "DEMON SPAWN"
  else
    demon=0
  fi
}

# --- RESET ---
reset_game() {
  step=0
  shoot=0
  demon=0
  gameover=0
  turndir=0
  lst="0,1,2"
  score=0
  update_scale
}

# --- WRITE STATE ---
write_state() {
cat > state.tex <<EOF
\def\step{$step}
\def\lst{$lst}
\def\scaleval{$scaleval}
\def\shoot{$shoot}
\def\demon{$demon}
\def\gameover{$gameover}
\def\score{$score}
\def\turndir{$turndir}
EOF
}

# --- RENDER ---
render() {
  pdflatex -interaction=nonstopmode main.tex > /dev/null < /dev/null
}

# --- INIT ---
reset_game
update_scale
write_state
render

while true; do

  update=0

  key=""
  read -u 3 -rsn1 -t 0.1 key

  # reset shoot each frame
  shoot=0

  turndir=0

  case "$key" in
    k) # forward
      if [ "$gameover" -eq 0 ]; then
        if [ "$step" -lt 2 ]; then
          step=$((step + 1))
          echo "FORWARD -> step=$step"

          if [ "$step" -eq 2 ]; then
            spawn_demon
          fi
        fi
      fi
      update=1
      ;;
    j) # backward
      if [ "$gameover" -eq 0 ]; then
        if [ "$step" -gt 0 ]; then

          # leaving step 2 -> check demon
          if [ "$step" -eq 2 ] && [ "$demon" -eq 1 ]; then
            echo "DEMON GOT YOU"
            gameover=1
          fi

          step=$((step - 1))
          echo "BACK -> step=$step"
        fi
      fi
      update=1
      ;;
    l) # right turn
      if [ "$step" -eq 2 ] && [ "$gameover" -eq 0 ]; then

        if [ "$demon" -eq 1 ]; then
          echo "TURNED WITH DEMON -> DEAD"
          gameover=1
        else
          echo "TURN RIGHT"
          turndir=2
          write_state
          render
          turndir=0
          sleep 0.3
          step=0
        fi
      fi
      update=1
      ;;
    h) # left turn
      if [ "$step" -eq 2 ] && [ "$gameover" -eq 0 ]; then

        if [ "$demon" -eq 1 ]; then
          echo "TURNED WITH DEMON -> DEAD"
          gameover=1
        else
          echo "TURN LEFT"
          turndir=1
          write_state
          render
          turndir=0
          sleep 0.5
          step=0
        fi
      fi
      update=1
      ;;
    s) # shoot
      if [ "$step" -eq 2 ] && [ "$demon" -eq 1 ]; then
        echo "DEMON KILLED"
        demon=0
        shoot=1
        score=$((score+1))
      fi
      update=1
      ;;
    r)
      echo "RESET"
      reset_game
      update=1
      ;;
    q)
      echo "QUIT"
      exit 0
      ;;
  esac

  if [[ "$step" -eq 0 ]]; then
    lst="0,1,2"
  fi
  if [[ "$step" -eq 1 ]]; then
    lst="0,1"
  fi
  if [[ "$step" -eq 2 ]]; then
    lst="0"
  fi

  if [[ "$update" -eq 1 ]]; then
    update_scale
    write_state
    render
    sleep 0.1
  fi

done



```

Now the LaTeX file.

```latex


\documentclass{article}
\usepackage{tikz}
\usepackage{pgfplots}
\usepackage{xcolor}
\usepackage{graphicx}

\pgfplotsset{compat=1.18}

\pagecolor{red!20!black}

\begin{document}

\input{state.tex}

\begin{center}

\begin{tikzpicture}[scale=\scaleval]

    \pgfmathsetmacro{\W}{15}
    \pgfmathsetmacro{\H}{8}

    %\fill[red!20!black] (-0.0 * \W, -0.9 * \H) rectangle (\W + 0.0 * \W, \H + 0.9 * \H);

    \pgfmathsetmacro{\N}{9 - 2*\step}
    \pgfmathsetmacro{\cell}{\W / \N}

    \pgfmathsetmacro{\mid}{(\N - 1) / 2}

    \pgfmathsetmacro{\xA}{\mid * \cell}
    \pgfmathsetmacro{\xB}{(\mid + 1) * \cell}

    % make it square
    \pgfmathsetmacro{\size}{\xB - \xA}

    \pgfmathsetmacro{\yA}{(\H - \size)/2}
    \pgfmathsetmacro{\yB}{\yA + \size}

    \draw[thick, fill=red!15!black] (\xA,\yA) rectangle (\xB,\yB);

    % drawing wall

    \pgfmathsetmacro{\sizeRef}{\size}

    \pgfmathsetmacro{\xALast}{\xA}
    \pgfmathsetmacro{\xBLast}{\xB}
    \pgfmathsetmacro{\yALast}{\yA}
    \pgfmathsetmacro{\yBLast}{\yB}

    \foreach \i in \lst {

        \pgfmathsetmacro{\offset}{\size * (2^\i)}
        \pgfmathsetmacro{\yext}{\offset / 2}

        \ifcase\i
            \def\wallcolor{black}
        \else
            \pgfmathsetmacro{\shade}{int(2 + 15*\i)}
            \edef\wallcolor{red!\shade!black}
        \fi

        % LEFT
        \pgfmathsetmacro{\xAi}{\xALast - \offset}
        \fill[fill=\wallcolor, draw=black]
            (\xAi,\yALast-\yext)
            -- (\xAi,\yBLast+\yext)
            -- (\xALast,\yBLast)
            -- (\xALast,\yALast)
            -- cycle;

        % RIGHT
        \pgfmathsetmacro{\xBi}{\xBLast + \offset}
        \fill[fill=\wallcolor, draw=black]
            (\xBi,\yALast-\yext)
            -- (\xBi,\yBLast+\yext)
            -- (\xBLast,\yBLast)
            -- (\xBLast,\yALast)
            -- cycle;

        % GROUND
        \fill[fill=red!20!black, draw=black]
            (\xALast,\yALast)
            -- (\xBLast,\yALast)
            -- (\xBi,\yALast - \yext)
            -- (\xAi,\yALast - \yext)
            -- cycle;

        % CEILING
        \fill[fill=red!20!black, draw=black]
            (\xALast,\yBLast)
            -- (\xBLast,\yBLast)
            -- (\xBi,\yBLast + \yext)
            -- (\xAi,\yBLast + \yext)
            -- cycle;

        \pgfmathparse{\xALast - \offset}
        \xdef\xALast{\pgfmathresult}

        \pgfmathparse{\xBLast + \offset}
        \xdef\xBLast{\pgfmathresult}

        \pgfmathparse{\yALast - \yext}
        \xdef\yALast{\pgfmathresult}

        \pgfmathparse{\yBLast + \yext}
        \xdef\yBLast{\pgfmathresult}

    }

    \pgfmathsetmacro{\weaponY}{\yALast / \scaleval}
    \pgfmathsetmacro{\demonY}{\weaponY + 0.1 * \H}

    \ifnum\demon=1
    \node at ({\W/2}, {\demonY}) {
        \includegraphics[width=6 cm]{demon.png}
    };
    \fi

    \ifnum\shoot=0
    \node at ({\W/2}, {\weaponY}) {
        \includegraphics[width=6 cm]{weapon.png}
    };
    \else
    \node at ({\W/2}, {\weaponY}) {
        \includegraphics[width=6 cm]{weapon_shoot.png}
    };
    \fi

    \ifnum\gameover=1
    \node[white, scale=3] at ({\W/2}, {\H/2}) {GAME OVER};
    \node[red!70!black, scale=3] at ({\W/2}, {\H/2 + 1}) {SCORE: \score};
    \fi

    \ifnum\turndir=1
        \fill[white]
            ({\W/2 - 2}, {\H/2})
            -- ({\W/2}, {\H/2 + 1})
            -- ({\W/2}, {\H/2 - 1})
            -- cycle;
    \fi

    \ifnum\turndir=2
        \fill[white]
            ({\W/2 + 2}, {\H/2})
            -- ({\W/2}, {\H/2 + 1})
            -- ({\W/2}, {\H/2 - 1})
            -- cycle;
    \fi

\end{tikzpicture}
\end{center}

\end{document}


```

There is really no new thing when it comes to the synthax apart from:

```latex


\pagecolor{red!20!black}


```

Allowing to change the **ENTIRE** background color of the document --> redish here.

All is based on **vanishing line** to create depth illusion.

So the basic idea is to draw a centered square, and 4 vanishing lines that starts at each square corner and that ... vanishes to the exterior.

- top-left corner -> vanishing line that goes to top-left

- top-right corner -> vanishing line that goes to top-right

- bottom-left corner -> vanishing line that goes to bottom-left

- bottom-right corner -> vanishing line that goes to bottom-right


First, we declare a Width ( `W`) and a Height ( `H`) variables, assign them respectively max Width and respectable Height value.

```latex


\pgfmathsetmacro{\W}{15}
\pgfmathsetmacro{\H}{8}


```

After that we calculates `N`.

```latex


\pgfmathsetmacro{\N}{9 - 2*\step}


```

What is `N` ?

Its value whole purpose is to compute the coordinates of the centered square.

I explain.

If you are in front of a wall, it will apear bigger (width and height proportionally) than when you are farer from it.

Because we will use `N` as:

```latex


\pgfmathsetmacro{\cell}{\W / \N}


```

Which gives us **width of units** (called `\cell`) we can work with.

The more there are units, the less wide they become ( `\W` is a constant = 15).

Also, note that the more steps we have done, the closer we get to the wall / square.

Then, the lower is `N` the less width units are and they are wider.

I spoke about units, so now, the trick is to compute the middle that tells, how many units i need to get to the middle unit.

```latex


\pgfmathsetmacro{\mid}{(\N - 1) / 2}


```

Here is the thing, i do not mean middle, i said the unit that is in the middle, like the median of you will.

This is key, because the start coordinate of the middle unit when i'm close to the wall (so step is high), is the coordinate of one of the firsts units when i'm far from the wall (step made lower).

After realizing that, it's simple, i just compute the x coordinate of the startig unit and ending x of the width --> x start and end of the square.

```latex


\pgfmathsetmacro{\xA}{\mid * \cell}
\pgfmathsetmacro{\xB}{(\mid + 1) * \cell}


```

You see, x end of the square is just the x start of the next width unit.

```latex


(\mid + 1) * \cell


```

So, the size of the edges of the square is just the difference.

```latex


\pgfmathsetmacro{\size}{\xB - \xA}


```

Now we compute y start and y end.

```latex


\pgfmathsetmacro{\yA}{(\H - \size)/2}
\pgfmathsetmacro{\yB}{\yA + \size}


```

So ( `\xA,\yA`) is actually bottom-left of the square.

After that, we draw the square.

```latex


\draw[thick, fill=red!15!black] (\xA,\yA) rectangle (\xB,\yB);


```

### Wall - Vanishing lines

Now most interesting part.

Look at the state.tex file:

```latex


\def\step{1}
\def\lst{0,1}
\def\scaleval{0.9}
\def\shoot{0}
\def\demon{1}
\def\gameover{1}
\def\score{2}
\def\turndir{0}


```

What is important is the evolution of `\step`, `\lst` and `\scaleval`

For `\step` == 0.

- `\scaleval` = 0.5
- `\lst` = 0,1,2 --> **3 walls**

For `\step` == 1.

- `\scaleval` = 0.9
- `\lst` = 0,1 --> **2 walls**

For `\step` == 2.

- `\scaleval` = 1.4
- `\lst` = 0,1,2 --> **1 wall**

`\lst` is just a list of numbers, what is important is its length, so it defines the iteration number in the next loop.

`\scaleval` is also important, because wo so not want the user to zoom in the PDF viewer (like zathura) we scale appropriately the scenes.

The `\scaleval` are "trust me bros" variables, but works.

The only "trust me bro" part in this article :)

Now the drawing walls part.

```latex


\pgfmathsetmacro{\xALast}{\xA}
\pgfmathsetmacro{\xBLast}{\xB}
\pgfmathsetmacro{\yALast}{\yA}
\pgfmathsetmacro{\yBLast}{\yB}

\foreach \i in \lst {

    \pgfmathsetmacro{\offset}{\size * (2^\i)}
    \pgfmathsetmacro{\yext}{\offset / 2}

    \ifcase\i
        \def\wallcolor{black}
    \else
        \pgfmathsetmacro{\shade}{int(2 + 15*\i)}
        \edef\wallcolor{red!\shade!black}
    \fi

    % LEFT
    \pgfmathsetmacro{\xAi}{\xALast - \offset}
    \fill[fill=\wallcolor, draw=black]
        (\xAi,\yALast-\yext)
        -- (\xAi,\yBLast+\yext)
        -- (\xALast,\yBLast)
        -- (\xALast,\yALast)
        -- cycle;

    % RIGHT
    \pgfmathsetmacro{\xBi}{\xBLast + \offset}
    \fill[fill=\wallcolor, draw=black]
        (\xBi,\yALast-\yext)
        -- (\xBi,\yBLast+\yext)
        -- (\xBLast,\yBLast)
        -- (\xBLast,\yALast)
        -- cycle;

    % GROUND
    \fill[fill=red!20!black, draw=black]
        (\xALast,\yALast)
        -- (\xBLast,\yALast)
        -- (\xBi,\yALast - \yext)
        -- (\xAi,\yALast - \yext)
        -- cycle;

    % CEILING
    \fill[fill=red!20!black, draw=black]
        (\xALast,\yBLast)
        -- (\xBLast,\yBLast)
        -- (\xBi,\yBLast + \yext)
        -- (\xAi,\yBLast + \yext)
        -- cycle;

    \pgfmathparse{\xALast - \offset}
    \xdef\xALast{\pgfmathresult}

    \pgfmathparse{\xBLast + \offset}
    \xdef\xBLast{\pgfmathresult}

    \pgfmathparse{\yALast - \yext}
    \xdef\yALast{\pgfmathresult}

    \pgfmathparse{\yBLast + \yext}
    \xdef\yBLast{\pgfmathresult}

}


```

In fact, it computes x offset and y offset that is the half of the first.

x offset evolves as 2^step, and that is just the offset from the last wall ! --> Strong vanishing lines

```latex


\pgfmathsetmacro{\offset}{\size * (2^\i)}
\pgfmathsetmacro{\yext}{\offset / 2}


```

"Why are they computed ?"

To compuet wall coordinates and drawing them.

```latex


% LEFT
\pgfmathsetmacro{\xAi}{\xALast - \offset}
\fill[fill=\wallcolor, draw=black]
    (\xAi,\yALast-\yext)
    -- (\xAi,\yBLast+\yext)
    -- (\xALast,\yBLast)
    -- (\xALast,\yALast)
    -- cycle;



```

After that, the variables are of course updated thanks to `\pgfmathparse` that alows to compute formulas, and `\xdef` for the definition.

```latex


\pgfmathparse{\xALast - \offset}
\xdef\xALast{\pgfmathresult}

\pgfmathparse{\xBLast + \offset}
\xdef\xBLast{\pgfmathresult}

\pgfmathparse{\yALast - \yext}
\xdef\yALast{\pgfmathresult}

\pgfmathparse{\yBLast + \yext}
\xdef\yBLast{\pgfmathresult}


```

We also compute a color gradient of the right and left walls by their depth - step made.

```latex


\ifcase\i
    \def\wallcolor{black}
\else
    \pgfmathsetmacro{\shade}{int(2 + 15*\i)}
    \edef\wallcolor{red!\shade!black}
\fi


```

At this point, i discovered that if i do the same for the top and bottom, it really gets awful visually, so i keep the same color for whole bottom and top and just apply gradient for walls.

For other stuffs.

We got some basics boolean logic.

Add the deamon png.

```latex


\ifnum\demon=1
\node at ({\W/2}, {\demonY}) {
    \includegraphics[width=6 cm]{demon.png}
};
\fi


```

When firering the weapon, we replace the png for certain amounts of frames by the a variant png.

```latex


\ifnum\shoot=0
\node at ({\W/2}, {\weaponY}) {
    \includegraphics[width=6 cm]{weapon.png}
};
\else
\node at ({\W/2}, {\weaponY}) {
    \includegraphics[width=6 cm]{weapon_shoot.png}
};
\fi


```

Same for making appear a left or right arrow when choosing a direction.

```latex


\ifnum\turndir=1
    \fill[white]
        ({\W/2 - 2}, {\H/2})
        -- ({\W/2}, {\H/2 + 1})
        -- ({\W/2}, {\H/2 - 1})
        -- cycle;
\fi

\ifnum\turndir=2
    \fill[white]
        ({\W/2 + 2}, {\H/2})
        -- ({\W/2}, {\H/2 + 1})
        -- ({\W/2}, {\H/2 - 1})
        -- cycle;
\fi


```

And gameover screen, with score.

```latex


\ifnum\gameover=1
\node[white, scale=3] at ({\W/2}, {\H/2}) {GAME OVER};
\node[red!70!black, scale=3] at ({\W/2}, {\H/2 + 1}) {SCORE: \score};
\fi


```

Hope you found this article useful !

!! Ciao Ciao !!