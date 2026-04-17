![](/assets/common_files/compression_algo.jpg)

_Ghost in the Shell, 1995_

**I've just finished implementing a simple text compression algorithm in C++, i will talk about its implementation in this article.**

The programm is available here [repo](https://github.com/julienlargetpiet/Simple_compression)

Or on this website as a zip [zip](/assets/common_files/Simple_compression.zip)

# Compression overview

A function will read the file to compress and will create a `std::string` of its content.

After, it will look for recurrent patterns.

## Recurrent patterns

A recurrent pattern as its name suggests is a sequence of character s that is present multiple times in the scaned `std::string` of the input file.

We can choose the length of the pattern to find. For example a pattern of length 2 is more commun than a pattern of length 3. In a sentence, we more often see "ou" than "oup".

## Compression level

Of course, the patterns frequence are often not equal.

So, here the `compression level` parameter means how many of the top most frequent patterns i will take in count to apply the compression algorithm?

## Compression key

The whole point of a compression algorithm is to replace the most frequen patterns taken in count with a **unique pattern** that have a lower length. For example "ou" can be replaced by "^" or "$" but there is no point in replacing it with "^$" or "$$" because the replacing patterns are of the same length of the pattern to replace.

The set of the compression key characters must bee out of the characters set used for writing input text. If we work with `ASCII` table only, we must keep in mind to choose the most unfrequent characters for the compression keys like `^<>$;[]-\\*`.

The input text must not contain these characters.

## Uniqueness of compression keys

So i've made an algorithm in the programm called `nb_to_letter()` that takes a number as input and returns an associated `std::string`. The output is different for all different inputs. For example with the set "abcd":

- input 1 -> "a"
- input 2 -> "b"
- ...
- input 5 -> "aa"
- input 6 -> "ab"
- ...

Choosing the length of the most frequent patterns to find is crucial. Indeed, the lower it is, the more "chances" we have to find some in a text, but from a certain value of `compression level`, it will begin to generate same length compression key, which is pointless.

If we choose a greater length for the most frequent pattern to find, we have less "chances" to find a lot of different patterns to compress, but on those we found, we can apply a greater compression level, which will compress more data.

## Out files

There are 2 outputed files by the compression function.

The first file is the compressed data itself.

The last file is the compression key file, where the compression key of the most frequent pattern to find is at the top, and it decreases at the bottom. The number of keys is linked to the compression level. If we choose a compression level of 4, we'll have 4 compression keys.

To find if the compression has been correctly done we can add the size of these files

To find their size:

```bash

$ wc -c compressed_data.txt

```

```bash

$ wc -c keys.txt

```

And compare it to the pre-compressed file:

```bash

$ wc -c pre_compressed_file.txt

```

# Decompresssion Overview

The decompression function will read the compression key file from bottom to top and begin to replace the compression key in compressed data from most unfrequent pattern to most frequent pattern.

# On directory

The same method is applied to compress an entire directory.

The main diference is that all the compression keys for all the files are again stored inside a single file, but to differenciate each file, a special character is added to distinguish them. I've chosen "\*".

The same goes for the compresed data.

Last, i've reimplemented the `tree` algorithm to list files recursively during compression and store them. The algo is available here [zip](/assets/common_files/mirador.zip) or here [repo](https://github.com/julienlargetpiet/mirador).

The path of each file is stored at the end of the compression key file.