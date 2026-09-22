
## Introduction

In this article, we'll detail the different package managers in Linux (and OpenBSD).

We'll see the great principles that lead to designing a package managers and how they philosophy can differ a bit.

## `pacman`, the Arch familly

`pacman` is the default package managers of the Arch Linux familly (Arch Linux, Cachy OS, Garuda Linux...).

So first, let's decompose a `pacman` command, because we have primary flags describing the operation familly and secondary flags that will describe the command, and we can have arguments at the end.

Here's a quick summary of them:

```

-S    # sync
-R    # remove
-Q    # query local package database
-U    # upgrade/install a package file 
-F    # querying files database
-D    # package database manipulation, administrative metadata
-T    # versioning dependency test

```

### the `-S` flag

The simplest use of this command is to download and install a package as:

```bash

pacman -S pkg

```

This will download the package into `/var/cache/pacman/pkg` under a compressed archive `.package.tar.zst`.

`.zst` is the extension of files compressed with Zstandard `zstd`.

For example:

```bash

zstd file.tar

```

produces:

```

file.tar.zst

```

And decompression:

```bash

unzstd file.tar.zst

```

or equivalently:

```bash

zstd -d file.tar.zst

```

Btw, here are the different extensions related to their compression format:

- `.gz` -> gzip

- `.bz2` -> bzip2

- `.xz` -> xz / LZMA2

- `.zst` -> zstd

- `.zip` -> ZIP format

Then `-S pkg` will install it into the system.

We can only download `pkg` into `/var/cache/pacman/pkg`using the `w` secondary flag, so:

```bash

pacman -Sw pkg

```

And then later you could install that local package archive with:

```bash

sudo pacman -U /var/cache/pacman/pkg/pkg-<version>-x86_64.pkg.tar.zst

```

One particularly useful variant is:

```bash

pacman -Sp pkgA

```

which doesn't even download it: it prints the URL(s) pacman would use. So you can think of the progression as:

- `pacman -Sp pkgA` -> tell me where it would come from

- `pacman -Sw pkgA` -> download it, don't install it

- `pacman -S  pkgA` -> download + install it

Now, we'll use `-S` for updating.

First, we can use the `y` secondary flag to only update the repository databases:

```bash

sudo pacman -Sy

```

These synchronized repository databases are stored under:

```

/var/lib/pacman/sync/

```

They contain metadata about the packages currently available in the configured repositories, including their versions and dependencies.

After refreshing them, it is generally a good idea to proceed directly with the system upgrade, meaning downloading and installing newer versions of packages already installed on the system:

```bash

sudo pacman -Su

```

The reason we usually upgrade immediately after refreshing the databases is that Arch Linux does not support partial upgrades.

After `pacman -Sy`, `pacman` now knows about the newest state of the repositories, while the packages installed on our system may still belong to an older repository state.

This can cause current packages to break in the future.

For example, imagine that our system currently contains:

```

pkgA v1 -> depends on libX v1
libX v1

```

After refreshing the repository databases, the repositories may now contain:

```

pkgA v2 -> depends on libX v2
libX v2

```

If we refresh the databases but do not upgrade the system, and then install another package requiring `libX v2` (for example `pkgB v2`), `pacman` may upgrade `libX` because it sees that the current installed version is too old but still leaves `pkgA v1` installed because it's not its scope.

And "upgrade" means replacing the newer version by the new one, so effectively deleting the old versions some packages still have a depedency to.

We could therefore end up with something conceptually like:

```

pkgA v1 -> libX v1
             X no longer installed

pkgB v2 -> libX v2

```

This is why running:

```bash

sudo pacman -Sy

```

alone is generally **discouraged**.

Instead, the usual operation is:

```bash

sudo pacman -Syu

```

where:

- `S` -> synchronization operation

- `y` -> refresh repository databases

- `u` -> upgrade installed packages

This keeps the installed system synchronized with the same repository state described by the newly downloaded databases.

Now imagine the following case:

I have `A` and `B` installed and both depends on `libX v1`.

But now I run:

```bash

pacman -Syu 

```

But it seems that `B` now depends on `libX v2`, but `A` still depends on `libX v1`.

What would happen, does 2 versions of the same package will stay installed to satisfied its dependents ?

Nope, in practice one of a few things happen:

- the library maintains ABI compatibility, so both packages can use the newer libX

- the distribution provides parallel library packages under different package names, such as `libX1` and `libX2`

- or `pacman` **refuses** the transaction because the dependency requirements cannot all be satisfied

For example, this is fine:

```

pkgA v2 -> libX v2

pkgB v4 -> libX v2

```

But this cannot normally coexist:

```

pkgA -> libX=1

pkgB -> libX=2

```

What's installed:

```

libX = ???

```

There is only one installed version of package `libX`.

There is, however, an important distinction between package versions and library `.so` names. A package called `libX` might contain something like:

```

/usr/lib/libX.so.2

```

and, during a transition, a compatibility package (it supposes it has another name) could provide:

```

/usr/lib/libX.so.1

```

Then both generations can coexist.

To search if a package exist in the configured repository, we do use the secondary  `s` flag:

```bash

pacman -Ss pkg

```

We can also query package metadata from repos, for exmaple:

```bash

pacman -Si firefox

```

Outputs something like:

```

Repository      : extra
Name            : firefox
Version         : 143.0-1
Description     : Fast, Private & Safe Web Browser
Architecture    : x86_64
URL             : https://www.mozilla.org/firefox/
Licenses        : MPL-2.0
Groups          : None
Provides        : None
Depends On      : glibc  gtk3  libx11  libxcomposite  libxdamage
                  libxfixes  libxrandr  nss  nspr  dbus
Optional Deps   : hunspell: spell checking support
                  libnotify: desktop notifications
Conflicts With  : None
Replaces        : None
Download Size   : 78.42 MiB
Installed Size  : 265.31 MiB
Packager        : Arch Linux Package Maintainer <maintainer@archlinux.org>
Build Date      : Sun 13 Sep 2026 14:21:03
Validated By    : SHA-256 Sum  Signature

```

`Conflicts With` are all the packages `pacman` won't allow the queried package to coexist with.

## The `-R` flag

That's the remove operation.

So first, the most used command will certainly be this one:

```bash

pacman -R pkg

```

Which will remove a `pkg`.

We could also add its configuration file with the secondary `n` (`--nosave`) flag:

```bash

pacman -Rn pkg

```

Indeed, without this flag, the package's configuration file that are tracked as backup files (`Backup` field that we'll see later on) and have been modified may be preserved by `pacman` by preserved by renaming them into something like:

```

/etc/pkg.someconf.pacsave

```

A usefull command is also this one:

```bash

pacman -Rdd pkg

```

This is usefull when `pkg` is a depedency.

Indeed, the first `d` flag tells `pacman` to ignore depedency **version** constraints.

For example:

```

A depends on foo=2

```

And we have:

```

pkgX
Provides: foo=2

pkgY
Provides: foo=1

```

Here `pkgX` and `pkgY` are different package names, so they can potentially coexist.

Normally, if we remove `pkgX`:

```bash

pacman -R pkgX

```

`pacman` sees:

```

A requires foo=2

```

So we have:

```

pkgX provided foo=2 <- being removed
pkgY provides foo=1 <- wrong version

```

and refuses.

But with:

```bash

pacman -Rd pkgX

```

`pacman` ignores the version constraint. The requirement is effectively checked as:

```

A requires foo

```

This also gives us an opportunity to look more closely at what we mean by a "dependency".

Suppose that `A` depends on a provision called `libx.so`, and that both `pkg1` and `pkg2` advertise that provision:

```

pkg1
Provides: libx.so

pkg2
Provides: libx.so

A
Depends on: libx.so

```

If both packages are installed, then:

```bash

pacman -R pkg1

```

can succeed because removing `pkg1` does not leave the dependency unsatisfied: `pkg2` still provides `libx.so`.

The important point is that `pacman` is not simply checking whether a file named `libx.so` physically remains somewhere on the filesystem. Dependency resolution is based on package metadata: package names, provides entries....

Indeed, `pacman` can represent dependencies on shared-library SONAMEs. For example, a package may provide:

```

lib:libx.so.2

```

While another package may depend on exactly:

```

lib:libx.so.2

```

Also, in that case, `lib:libx.so.1` and `lib:libx.so.2` are distinct dependency identities: providing one does not satisfy a dependency on the other.

So pacman supports several forms of dependency relations, including ordinary package dependencies and SONAME-based dependencies used to express shared-library requirements.

Now, we also have the `s` flag that removes recursively a package and its depedencies that are unneeded by others packages:

```bash

pacman -Rs pkg

```

If:

```

pkg -> A 
pkg -> B 
pkg -> C -> D
pkg2 -> B

```

If `A, C` and `D` were installed as depedencies, then removing `pkg` with the last command will remove them.

So `-Rs` recursively walks through the dependency graph, but only removes dependencies that are no longer required elsewhere and that are not marked as explicitly installed.

But to also removes depedencies that are marked as explicitely installed, we use second `s` flag:

```bash

pacman -Rss pkg

```

A depedency explicitely installed isn't an oxymoron

For example:

```bash

pacman -S A

```

We explicitly install `A`, so `pacman` records:

```

A
Install reason: Explicit

```

Later you install:

```bash

pacman -S B

```

and `B` happens to depend on `A`:

```

B -> A

```

Now `A` is simultaneously 

```

A is a dependency of B

```

AND:

```

A is marked as explicitly installed

```

Those are perfectly compatible statements.

Indeed, we must distinct 2 type of "depedency" metadata; the reason why a package was installed (explicit or dep), and its role in the true depedency graph (nodep, dep, optdep).

Also, the optional depedencies of a package are not automatically installed with `pacman -S`, so if I have `B` installed that optionally depends on `A`, and that later I explicitely install `A` (with `pacman -S A`), then `A` is marked as explicitely installed and is an optional depedency of `B`.

Back to the `-R` flags.

A very common operation is combining `n` and `s`:

```bash

pacman -Rns pkg

```

The operation that goes in the opposite direction (in the depedency graph) of `-Rs` is `-Rc`.

Indeed, it'll go up in the dependency graph and remove what it traverses, but it doesn't take the optional depedency as relationship in the dep graph. 

For example, if we have:

```

A (optional depedency) -> B -> C -> D

```

And that I do:

```bash

pacman -Rc D

```

Then `D`, `C` and `B` will be removed but not `A`.

## The `-Q` flag

This is the flag to query informations on the local database.

For example, we got a nice symetry with `-S` for the `i` flag, indeed we also can retrieve informations on the installed package, for example:

```bash

pacman -Qi firefox

```

Outputs something like:

```

Name            : firefox
Version         : 143.0-1
Description     : Fast, Private & Safe Web Browser
Architecture    : x86_64
URL             : https://www.mozilla.org/firefox/
Licenses        : MPL-2.0
Groups          : None
Provides        : None
Depends On      : glibc  gtk3  libx11  libxcomposite  libxdamage
                  libxfixes  libxrandr  nss  nspr  dbus
Optional Deps   : hunspell: spell checking support
                  libnotify: desktop notifications
Required By     : None
Optional For    : some-other-package
Conflicts With  : None
Replaces        : None
Installed Size  : 265.31 MiB
Packager        : Arch Linux Package Maintainer <maintainer@archlinux.org>
Build Date      : Sun 13 Sep 2026 14:21:03
Install Date    : Mon 14 Sep 2026 09:42:17
Install Reason  : Explicitly installed
Install Script  : No
Validated By    : Signature

```

We also have the `s` variant flag to search for an installed package:

```bash

pacman -Qs firefox

```

A possible output:

```

local/firefox 143.0-1
    Fast, Private & Safe Web Browser

```

We can see depedencies with:

```bash

pacman -Qd

```

Possible output:

```

acl 2.3.2-1
at-spi2-core 2.56.3-1
brotli 1.1.0-3
cairo 1.18.4-1
dbus 1.16.2-1
expat 2.7.1-1
fontconfig 2:2.16.2-1
freetype2 2.13.3-1
glib2 2.84.4-1
graphite 1:1.3.14-4
harfbuzz 11.4.1-1
libpng 1.6.50-1
libx11 1.8.12-1
libxcb 1.17.0-1
pcre2 10.46-1
zlib 1:1.3.1-2

```

We can add the `q` flag to only have the names, which can be usefull in bash scripting for reasons we'll see later:

```bash

pacma,n -Qdq

```

Possible output:

```

acl 
at-spi2-core 
brotli 
cairo 
dbus 
expat 
fontconfig 
freetype2 
glib2 
graphite 
harfbuzz 
libpng 
libx11 
libxcb 
pcre2 
zlib 

```

It's also time to introduce the concept of optional dependencies more deeply.

An optional dependency describes a relationship between packages. For example:

```bash

pkgA --optdepends--> pkgB

```

This relationship is declared in `pkgA`'s package metadata.

However, this relationship is completely separate from `pkgB`'s installation reason.

Pacman records an installed package as either:

```

Explicitly installed

```

or:

```

Installed as a dependency

```

Therefore, a package can be marked as "installed as a dependency" even if its only current relationship with another installed package is an optional dependency.

For example, we can deliberately install `pkgB` with:

```bash

pacman -S --asdeps pkgB

```

Pacman then records:

```

pkgB
Install Reason: Installed as a dependency

```

while the dependency graph may contain only:

```

pkgA --optdepends--> pkgB

```

These two pieces of information describe different things:

```

pkgA --optdepends--> pkgB

```

describes the relationship between the packages, while:

```

pkgB: Install Reason = dependency

```

describes how pacman should classify pkgB on the local system.

Therefore, "installed as a dependency" does not necessarily mean that the package is currently a hard dependency of another installed package.

And with `-Qd` it only returns packages whose installation reason is depedency.

We can even download a package as a dependency but isn't used by any of installed package on the system.

The contrary to `-d` is the `-e` flag that tells `pacman` to return only explicitely marked packages:

```bash

pacman -Qe

```

Now, we must also have a way to inspect the graphs to list packages that are not required by any of the installed packages, it's in fact detecting orphans.

For that we use the `-t` flag.

Indeed, this will inspect the depedency flag and return exactly what we described.

```bash

pacman -Qt

```

A common options to clean a system is by removing its orphans, so a good command is:

```bash

pacman -Rns $(pacman -Qdtq)

```

Now, if you want to go a step further in the cleaning process, you can also mark the optional depedencies as needed to be remove, we do that by adding a `t`.

So the related command is:

```bash

pacman -Rns $(pacman -Qdttq)

```

We also have `-Ql` to list the files belonging to an installed package:

```bash

pacman -Ql glibc

```

Output:

```

glibc usr/
glibc usr/bin/
glibc usr/bin/ldd
glibc usr/include/
glibc usr/include/stdio.h
glibc usr/lib/
glibc usr/lib/libc.so.6
...

```

To get which installed package own a particular file, we do:

```bash

pacman -Qo path/to/some/file

```

May output something like:

```

/path/to/some/file is owned by coreutils 9.7-1

```

We won't have multiple matches for one file because `pacman` does not allow two installed packages to own the same filesystem path at the same time.

But we can give multiple files to the command:

```bash

pacman -Qo /usr/bin/ls /usr/bin/bash /usr/lib/libcrypto.so.3

```

May output something like:

```

/usr/bin/ls is owned by coreutils 9.7-1
/usr/bin/bash is owned by bash 5.3.3-1
/usr/lib/libcrypto.so.3 is owned by openssl 3.5.2-1

```

Also, if we are currently in:

```

/usr/bin

```

then:

```bash

pacman -Qo ls

```

can resolve to `/usr/bin/ls`.

But using the absolute path instead of relative is much clearer and less ambiguous.

We can also verify that a package is healthy with the `-k` (check) flag.

checks whether the files that belong to an installed package are still present on disk.

For example:

```bash

pacman -Qk openssl

```

might output:

```

openssl: 312 total files, 0 missing files

```

If some files are missing:

```

openssl: 312 total files, 2 missing files

```

With double `k`:

```bash

pacman -Qkk openssl

```

`pacman` performs a more detailed check, including file properties such as permissions, ownership, size, and modification time for files with metadata available. 

For example:

```

warning: openssl: /usr/bin/openssl (Permissions mismatch)
warning: openssl: /usr/lib/libcrypto.so.3 (Size mismatch)
openssl: 312 total files, 2 altered files

```

So the distinction is roughly:

- `-Qk` -> are package files present?

- `-Qkk` -> are they present, and do their recorded metadata still match ?

## The `-F` flag

This is for the file-package relation oriented operations.

The goal of this command is to provide a way to discover file(s)-package(s) relationship before even installing the package because it will ask the repositories servers to answer our questions.

Indeed, we can update the local databases containing the relationships under `/var/lib/pacman/sync` with the `-y` flag:

```bash

pacman -Fy

```

We can even force the update even if `pacman` thinks that all is still synced:

```bash

pacman -Fyy

```

As we saw earlier, the normal sync database refreshed by:

```bash

pacman -Sy

```

It's the `repo.db` side. 

The file database is refreshed separately with the commands we just saw.

That separation makes sense because file lists are much larger. Pacman **does not need the complete list of every file contained** in every repository package just to resolve dependencies or install packages.

Now, we have the plain `-F` which will search for package(s) that contain the input filename, for example:

```bash

pacman -F libcrypto.so

```

May output something like:

```

core/openssl 3.5.2-1
    usr/lib/libcrypto.so

extra/openssl-1.1 1.1.1w-3
    usr/lib/openssl-1.1/libcrypto.so

extra/some-sdk 4.2-1
    opt/some-sdk/lib/libcrypto.so

```

We can also narrow the query by giving the absolute path.

And to be more flexible about the filename, we can even use RegEx with the `-x` flag, for example:

```bash

pacman -Fx 'libcrypto\.so(\.[0-9]+)*$'

```

May output something like:

```

core/openssl 3.5.2-1
    usr/lib/libcrypto.so
    usr/lib/libcrypto.so.3

extra/openssl-1.1 1.1.1w-3
    usr/lib/openssl-1.1/libcrypto.so.1.1

```

Btw, we can add the `-q` flag to flatten the output (like for `-Qq`):

```bash

pacman -Fqx 'libcrypto\.so(\.[0-9]+)*$'

```

Output:

```

openssl
openssl-1.1

```

`--machinereadable` flag make the result separated by null separators:

```bash

pacman -Fx --machinereadable 'libcrypto\.so(\.[0-9]+)*$'

```

Output:

```

repository\0package\0version\0path\n

```

Until now, we talked about the file(s) -> package(s) commands, but we also have a nice symetry with `-Ql` thanks to `-Fl` that allows to search for file(s) contained in a repository package:

```bash

pacman -Fl openssl

```

Could output:

```

openssl usr/
openssl usr/bin/
openssl usr/bin/openssl
openssl usr/include/
openssl usr/include/openssl/
openssl usr/lib/
openssl usr/lib/libcrypto.so
openssl usr/lib/libcrypto.so.3
openssl usr/lib/libssl.so
openssl usr/lib/libssl.so.3

```

And:

```bash

pacman -Flq openssl

```

Removes the package name and gives just the paths:

```

usr/
usr/bin/
usr/bin/openssl
usr/include/
usr/include/openssl/
usr/lib/
usr/lib/libcrypto.so
usr/lib/libcrypto.so.3
usr/lib/libssl.so
usr/lib/libssl.so.3

```

## The `-D` flag

This command controls the metadata of a package, more precisely the reason why a package was installed, for example we can change a package that was installed as a depedency by another package as explicitely installed:

```bash

pacman -D --asexplicit dep

```

Or the opposite:

```bash

pacman -D --asdeps pkg

```

We can also check if the local package database against the installed system is healthy with the `-k` flag (a nice symetry to `-Qk`).

More precisely, it verifies things like: if required package files are present, installed dependencies are satisfied, installed packages do not conflict, and if multiple installed packages do not claim the same file.

```bash

pacman -Dk

```

On a healthy system, we may simply get:

```

No database errors have been found!

```

If something is wrong, we could conceptually see messages such as:

```

error: missing 'libfoo.so=2' dependency for 'pkgA'
error: file owned by 'pkgA' and 'pkgB': usr/lib/libfoo.so
error: required file missing for package 'pkgC'

```

Now:

```bash

sudo pacman -Dkk

```

does the same local consistency check **and additionally checks the sync databases (repos)** to make sure the dependencies declared by packages are available from the configured repositories.

For example, imagine our installed system has:

```

pkgA -> depends on libfoo

```

and `libfoo` is currently installed, so locally everything is fine.

Then:

```bash

pacman -Dk

```

Succeeds:

```

No database errors have been found!

```

But suppose none of our currently configured repositories contains `libfoo` anymore.

Then:

```bash

pacman -Dkk

```

could report a problem:

```

error: dependency 'libfoo' required by 'pkgA' is not available in sync databases

```

So conceptually:

- `-Dk` -> check local installed state

- `-Dkk` -> check local installed state + check whether required dependencies are available in the configured repositories

A nice example is a package installed from the AUR or from an old repository:

```

installed:
    pkgA
    libfoo

configured repositories:
    core
    extra

```

But `libfoo` no longer exists in either repository

But `-Dkk` additionally can flag it.

## The `-T` flag

Its job is simple:

**Take one or more dependency expressions and print only the ones that are not currently satisfied on the installed system.**

For example:

```bash

pacman -T qt 'bash>=3.2'

```

If both dependencies are satisfied, `pacman` prints nothing and exits successfully.

If `qt` is missing but it satisfies `"bash>=3.2"`, the output would be:

```

qt

```

If both are unsatisfied:

```

qt
bash>=3.2

```

We can test version constraints such as:

```bash

pacman -T 'foo=2'
pacman -T 'foo>=2'
pacman -T 'foo<=2'
pacman -T 'foo>2'
pacman -T 'foo<2'

```

A very useful scripting pattern is:

```bash

missing=$(pacman -T 'openssl>=3' zlib)

if [ -n "$missing" ]; then
    printf 'Missing dependencies:\n%s\n' "$missing"
fi

```

Indeed, in Bash `-n` checks if a string has a non-zero length:

```bash

SOMEVAR="yes"

[ -n $SOMEVAR ] && echo "$SOMEVAR" || echo "no"

```

Output:

```

yes

```

## `pactree`

We install `pactree` with:

```bash

pacman -S pacman-contrib

```

`pactree` is basically a small depedency-graph explorer around `pacman`'s database package.

To see the normal recursive depedency tree of a package (for example the ones `-Rss` will remove), we do:

```bash

pactree pkg

```

Possible output:

```

pkg
└─A
  └─B

```

To see the reverse depedency tree (the ones that depends on `pkg`), we do:

```bash

pactree -r pkg

```

Possible output:

```

pkg
└─C
  └─D

```


We can also limit depth with `-d X` where `X` is an integer, for example:

```bash

pactree -d 1 -r pkg 

```

Possible output:

```

pkg
└─C

```

Because in a graph we can have something like:

```

  A
 /\
B  C
 \/
 D
 
```

So if I do:

```bash

pactree A

```

I have:

```

A
└─B
| └─D
└─C
  └─D

```

So if I want to only list **unique** depedencies, I do:

```

pactree -u A

```

Then, I only get:

```

A
B
C
D

```

Until now, we only listed hard depedencies, but we can also include optional depedencies in the results with the `-o` flag.

So if:

```

A -> B
A --optdepends--> C

```

Then:

```

pactree -o pkg

```

Includes `C`.

We can couple that with `-r` to ask either hard-depend or optionally depends on the input package:

```bash

pactree -u -r -o pkg

```

We can even use the above commands on packages we did not even installed, just by looking into the local metadata package database thanks to the `-s` flag.

For example, to see the depedency graph of `firefox` and that we've not yet installed it, we can do:

```bash

pactree -s firefox

```

But it's preferable to update the local metadata package datababase first with:

```bash

pacman -Sy

```

Because `pactree -s pkg` does not directly ask the repos.

We can even generate a real SVG or PNG image of a package depedency graph thanks to the combination of `pactree -g somepkg` and the `dot` command provided by GraphViz.

So, we install GraphViz with:

```bash

pacman -S graphviz

```

Now we can generate the file necessary to GrapghViz:

```bash

pactree -g pkg > pkg.dot

```

This file contains DOT language content, something like:

DOT is specifically a language for describing graphs with nodes and edges.

```

digraph G {
    "pkg" -> "libA";
    "pkg" -> "libB";
    "libB" -> "libC";
}

```

And now we provide its content to the `dot` command as:

```bash

dot -Tsvg pkg.dot -o pkg.svg

```

to obtain the SVG representing the dep graph of `pkg`.

For others image formats, we have:

```bash

-Tpng
-Tjpeg
-Tjpg
-Tpdf
...

```

Cf: `man dot`.

We can also directly provides `stdout` of the `pactree` command to the `stdin` of the `dot` command:

```bash

pactree -g pkg | dot -Tsvg -o pkg.svg

```

## `apt` & `dpkg`, the Debian familly

`apt` and `dpkg` are the default package managers of the Debian familly (Debian, Ubuntu, Linux Mint...).

### Architecture

In fact, we have 2 layers.

`apt` is the higher-level package manager that understands repositories, dependency resolution, upgrades, and transactions.

`dpkg` is the low-level local package manager. It knows how to install/remove/configure `.deb` packages and maintain the local package database.

The equivalent of `/var/lib/pacman/sync` is `/var/lib/apt/lists`.

The files in `/var/lib/apt/lists` contain packages metadata (one file per source containing all its available packages) such as packages names, versions, dependencies, descriptions, architecture, and the repository path to their related `.deb`. They are called package indexes files.

For example, we can search the Bash package metadata in the local synced metadata database (for the `noble` source, the one making it available):

```bash

grep -A 25 '^Package: bash$'   /var/lib/apt/lists/*noble*Packages

```

I get the output for the `amd64` and the `i386` CPU architecture:

```

/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-amd64_Packages:Package: bash
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-amd64_Packages-Architecture: amd64
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-amd64_Packages-Version: 5.2.21-2ubuntu4
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-amd64_Packages-Multi-Arch: foreign
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-amd64_Packages-Priority: required
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-amd64_Packages-Essential: yes
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-amd64_Packages-Section: shells
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-amd64_Packages-Origin: Ubuntu
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-amd64_Packages-Maintainer: Ubuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-amd64_Packages-Original-Maintainer: Matthias Klose <doko@debian.org>
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-amd64_Packages-Bugs: https://bugs.launchpad.net/ubuntu/+filebug
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-amd64_Packages-Installed-Size: 1900
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-amd64_Packages-Pre-Depends: libc6 (>= 2.38), libtinfo6 (>= 6)
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-amd64_Packages-Depends: base-files (>= 2.1.12), debianutils (>= 5.6-0.1)
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-amd64_Packages-Recommends: bash-completion
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-amd64_Packages-Suggests: bash-doc
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-amd64_Packages-Filename: pool/main/b/bash/bash_5.2.21-2ubuntu4_amd64.deb
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-amd64_Packages-Size: 794086
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-amd64_Packages-MD5sum: 627cdbb775b1a60dadd502e96e0426b1
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-amd64_Packages-SHA1: 8065b79389fc555b38cf71e297a259773b09c38e
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-amd64_Packages-SHA256: 73de311a21e094e29ac01527d2b52226cc87fde0a5b57032902251b426d92c66
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-amd64_Packages-SHA512: c14c2c8fa0d1ae7530efa0375845257b4ec0baa5bc42982efca2d7fa860b4e4ea3f04d31cfa328d2f250b2baeac3795c8b31aa5ff2d514ed16a5cf8c3132a590
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-amd64_Packages-Homepage: http://tiswww.case.edu/php/chet/bash/bashtop.html
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-amd64_Packages-Description: GNU Bourne Again SHell
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-amd64_Packages-Task: minimal
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-amd64_Packages-Description-md5: 3522aa7b4374048d6450e348a5bb45d9
--
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-i386_Packages:Package: bash
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-i386_Packages-Architecture: i386
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-i386_Packages-Version: 5.2.21-2ubuntu4
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-i386_Packages-Multi-Arch: foreign
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-i386_Packages-Priority: required
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-i386_Packages-Essential: yes
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-i386_Packages-Section: shells
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-i386_Packages-Origin: Ubuntu
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-i386_Packages-Maintainer: Ubuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-i386_Packages-Original-Maintainer: Matthias Klose <doko@debian.org>
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-i386_Packages-Bugs: https://bugs.launchpad.net/ubuntu/+filebug
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-i386_Packages-Installed-Size: 1872
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-i386_Packages-Pre-Depends: libc6 (>= 2.38), libtinfo6 (>= 6)
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-i386_Packages-Depends: base-files (>= 2.1.12), debianutils (>= 5.6-0.1)
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-i386_Packages-Recommends: bash-completion
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-i386_Packages-Suggests: bash-doc
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-i386_Packages-Filename: pool/main/b/bash/bash_5.2.21-2ubuntu4_i386.deb
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-i386_Packages-Size: 766700
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-i386_Packages-MD5sum: 812906d1bb2b172d44ef9152a077ffa9
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-i386_Packages-SHA1: 6354f03b8937bfb23a1ab1df054024a0d1395d5f
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-i386_Packages-SHA256: f1e68b898f37325c94798b4e02fdcbe1c24995c4c2680dbc46d33fc843f3486f
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-i386_Packages-SHA512: 12d7d0d38088870b975f7ead08345fe08d0ea6494e6d68456ca8280d988647386c796569a40a66718c2bcdc7d106cfd7a04a6c104ef754721a64127de4a31ae1
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-i386_Packages-Homepage: http://tiswww.case.edu/php/chet/bash/bashtop.html
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-i386_Packages-Description: GNU Bourne Again SHell
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-i386_Packages-Task: minimal
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-i386_Packages-Description-md5: 3522aa7b4374048d6450e348a5bb45d9

```

Btw, I printed out the next 25 lines above the line where the match has been made thanks to `-A 25`.

Here, with the filenames containing the results, I know that Bahs comes from the `https://archive.ubuntu.com/ubuntu` repo, and the `Filename` for `amd64` for example is:

```

pool/main/b/bash/bash_5.2.21-2ubuntu4_amd64.deb

```

Therefore, the URL it'll be downloaded is:

```

https://archive.ubuntu.com/ubuntu/pool/main/b/bash/bash_5.2.21-2ubuntu4_amd64.deb

```

From the metadata filename we also see the distribution sources it comes from, in that case it's from:

```

deb http://archive.ubuntu.com/ubuntu noble main

```

Which appears in `/etc/apt/sources.list.d/official-package-repositories.list` alongside with `restricted`, `universe` and `multiverse` variants:

```

deb http://archive.ubuntu.com/ubuntu noble main restricted universe multiverse

```

Now, back to the metadata.

Interrestings fields are the one describing the edges of the depedency graph.

`Pre-Depends` is stronger than a normal `Depends`; those packages must already be configured before the targeted package itself is unpacked/configured. 

`Depends` are the ordinary hard dependencies, they are installed in the targeted package installation process. 

`Recommends` are weaker than hard dependencies but, by default, `apt` usually installs them. 

`Suggests` are weaker and are normally not installed automatically.

Those are metadata stored in the indexes files describing the packages relationship.

But, such as for `pacman`, the metadata concerning the reason why a package was installed also exists, for that we only have `manual`and `automatic`.

Also, like for the `pacman` metadata we have the `Installed-Size` of the package and the `Size` of the `.deb` file.

And the equivalent of `/var/cache/pacman/pkg` is `/var/cache/apt/archives` (stagging dir).

Where the `.deb` (the files actually containing the package) are temporary downloaded to be installed (see later).

#### The `.deb` format

A `.deb` file is a Debian-familly-specific structure.

Indeed, a modern `.deb` is essentially an `ar` archive containing three main members, conceptually:

```

package.deb
├── debian-binary
├── control.tar.*
└── data.tar.*

```

`ar` means archiver. It is a very simple container format.

`tar`, by contrast, was designed to archive a filesystem tree while preserving file-oriented metadata such as paths, directory structure, permissions, ownership, timestamps, symlinks, etc.

So inside the `.deb`, Debian uses `tar` for the parts that actually need to represent directory trees like `control.tar` and `data.tar`.

`debian-binary` is a tiny text file describing the `.deb` format version, for example:

"This archive uses Debian binary package format version 2.0."

`control.tar.*` contains the package’s own control metadata and maintainer scripts.

Typical contents look like:

```

control.tar.xz
├── control
├── md5sums
├── preinst   |
├── postinst  |__ maintainer scripts
├── prerm     |
└── postrm    |

```

- `preinst` -> run before the package’s files are unpacked/installed.

- `postinst` -> run after the package has been unpacked, typically to finish configuration.

- `prerm` -> run before removing or replacing the package’s installed files.

- `postrm` -> run after removal; may also run during `purge`/`upgrade-related` cleanup.

The important one is:

```

control

```

That file contains metadata such as:

```

Package: bash
Version: 5.2.21-2ubuntu4
Architecture: amd64
Depends: ...
Recommends: ...
Description: ...

```

So it resembles what we saw in:

```

/var/lib/apt/lists/...

```

`data.tar.*` contains the actual filesystem payload: binaries, libraries, docs, config files, and so on. The inner tar archives may be compressed with `gzip`, `xz`, `zstd`, or left uncompressed, depending on the package/tooling.

### The `apt install` command

This si the direct equivalent of `pacman -S`, to install a package we do:

```bash

apt install pkg

```

Here, APT mainly resolves `pkg` using the local repository metadata.

We can of course specify the exact version to install:

```bash

apt install bash=5.2.21-2ubuntu4

```

or target a specific download suite:

```bash

apt install bash/noble

```

or with this form:

```bash

apt install -t noble bash

```

And to combine both we do:

```bash

apt install -t noble bash=5.2.21-2ubuntu4

```

With Pacman, we can only precise the repository:

```bash

sudo pacman -S core/bash

```

or:

```bash

sudo pacman -S extra/pkg

```

That's why we have the opportunity to download an arbitrary `.tar.zst` file and directly download the inner package with `pacman -U`.

When the package is already installed but there's a newer version available, then it upgrades it.

We also can force to reinstall the package with the `--reinstall` flag, that's the equivalent of what `pacman -S` natively does, by the way I knwo we are in the `apt` part, but to skip reinstalling, we can also do:

```bash

pacman -S --needed pkg

```

Pacman has a similar behavior. But as discussed earlier in the `pacman` part; refreshing with `pacman -Sy` and after `pacman -S pkg` can cause a partial upgrade, so that's better to a full upgrade `pacman -Syu`.

We also can pass multiple packages to this command such as:

```bash

apt install pkg1 pkg2 ...

```

That's the case for most "scoped" operations such as `remove`, `purge`, `download`...

And we can also download a package without installing it.

### The `apt download` command

Indeed, withthis command we directly download the `.deb` in the current working directory:

```bash

apt download pkg

```

So I get its latest `.deb` file known to my local database.

I can now also use the `apt install` command to install the manually downloaded `.deb` file onto my system:

```bash

apt install pkg.deb

```

### The `apt update` command

In order to update the indexes files under (`/var/lib/apt/lists`), we do:

```bash

apt update

```

That's a good moment to speak more about the architecture under `/var/lib/apt/lists`.

Indeed, until now we spoke about a specific type of indexes files, that is the `Packages` files.

It contains one stanza per binary package/version/architecture, with fields like `Package`, `Version`, `Depends`, `Filename`, `Size`, `hashes` like we saw before etc. It is what APT primarily uses to resolve and download `.deb` packages.

But, we also have the `InRelease` files for the repos.

It describes the repository release itself and is cryptographically signed. Think of it as the authenticated manifest for a suite such as `noble` or `noble-updates`. It includes information about the suite and checksums for index files beneath it. Older layouts can use:

```

Release
Release.gpg

```

instead of the combined signed `InRelease`.

For example, on my systemI have:

```bash

ls /var/lib/apt/lists/*InRelease*

```

Output:

```

/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble-backports_InRelease
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_InRelease
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble-updates_InRelease
/var/lib/apt/lists/brave-browser-apt-release.s3.brave.com_dists_stable_InRelease
/var/lib/apt/lists/dl.google.com_linux_chrome-stable_deb_dists_stable_InRelease
/var/lib/apt/lists/download.docker.com_linux_ubuntu_dists_noble_InRelease
/var/lib/apt/lists/download.virtualbox.org_virtualbox_debian_dists_noble_InRelease
/var/lib/apt/lists/ppa.launchpadcontent.net_neovim-ppa_stable_ubuntu_dists_noble_InRelease
/var/lib/apt/lists/ppa.launchpadcontent.net_obsproject_obs-studio_ubuntu_dists_noble_InRelease
/var/lib/apt/lists/repository.mullvad.net_deb_stable_dists_stable_InRelease
/var/lib/apt/lists/security.ubuntu.com_ubuntu_dists_noble-security_InRelease

```

Corresponding to sources configured in `/etc/apt/sources.list.d`.

And in `/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble-backports_InRelease` I have:

```

-----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA512

Origin: Ubuntu
Label: Ubuntu
Suite: noble-backports
Version: 24.04
Codename: noble
Date: Fri, 18 Sep 2026  9:51:49 UTC
Architectures: amd64 arm64 armhf i386 ppc64el riscv64 s390x
Components: main restricted universe multiverse
Description: Ubuntu Noble Backports
NotAutomatic: yes
ButAutomaticUpgrades: yes
MD5Sum:
 5411412b905e9e1e02916ec0392ba99b         13983948 Contents-amd64
 f1230d81f3b242467fdd49e351c525d6           787282 Contents-amd64.gz
 9fd34264f8d3897914557b9e745dbf8c         13984006 Contents-arm64
 db8a6c1774a31b89a098055826a0e4a5           787237 Contents-arm64.gz
 fcdb2d8f5cc59ff6f2ab04d84a69f97f         13993054 Contents-armhf
 764137197933b155e59adc12739d1537           787556 Contents-armhf.gz
 1a23e10fbaeacdc7eee59e3b17df9717         13692747 Contents-i386
 0eb4d420a431ccbd265dbd3c80389ed1           765737 Contents-i386.gz
 6afbcd30d6511235f41f424c962db54b         13845889 Contents-ppc64el
 9cc95b8b57d92500b9f196e233440ce2           778306 Contents-ppc64el.gz
 ebd7a9b106dd37f2a33e55a41a621870         13834906 Contents-riscv64
 4ad86b0910edacb6840467b99149e2cb           777758 Contents-riscv64.gz
 14d11d791d530764db819caf4ca49b08         13977389 Contents-s390x
 cd9784cfa9798f50acc5a8291929d72d           786595 Contents-s390x.gz
 452bb7eaff9030d56be9267049aa2c90           458763 main/binary-amd64/Packages
 e7bc1964980b200d652cfb41df5c5615            78515 main/binary-amd64/Packages.gz
 ced56a0198f9cf3ed46195c2f36057f6            65852 main/binary-amd64/Packages.xz
...

SHA1:
 d90f92d8858d50ad998968e50a397fc96984f03f         13983948 Contents-amd64
 70e2d32d2b0b1609f92dbd5c67a265e09ca257ab           787282 Contents-amd64.gz
 047ce43d4159df4ca8635bccf8a32752b8ae5f4d         13984006 Contents-arm64
 a79430c001a7e87d34a3a4cba9e0774334132d66           787237 Contents-arm64.gz
 bbe4a598b4f5742c500b7ffc2685c70946af9045         13993054 Contents-armhf
 e746bba5d0e19a54027a755ef985b6ab1b0548ed           787556 Contents-armhf.gz
 a0c55ed52dcd51fc01442f4c9cb49cf3f3f5d061         13692747 Contents-i386
 a7ec7faa2f90f982d81248a31d2fef1f5ae200e2           765737 Contents-i386.gz
 aa30ac4faca6d31d2dbb462c99dcfc741961c231         13845889 Contents-ppc64el
 7639db0a4210479ec8efd83e7bcb874f100eab01           778306 Contents-ppc64el.gz
 3de1e19cf52bdb9b9f719ba5912dd0197c1aa153         13834906 Contents-riscv64
 a7665556b9624e392972ebea5895b3dec40434b9           777758 Contents-riscv64.gz
 2162f6a4ee66a80cf352ceb63be33aef5f29f001         13977389 Contents-s390x
 da052001e1ca53c94c2461a9c40b43971ad89a62           786595 Contents-s390x.gz
 190aba181cb538c7404e310952d0ada102badbca           458763 main/binary-amd64/Packages
 dd0e83aaf3172cb1c06593137f03739f43cc5c05            78515 main/binary-amd64/Packages.gz
 92b72275f907330db4ca0937ac4753a02aa3cbe2            65852 main/binary-amd64/Packages.xz
 ...
SHA256:
 1b74788a0e65cf17c069a8f64017f889a7e8fb41d043033f91b08e52d172d5d0         13983948 Contents-amd64
 b8bc378605901b9918ec0e8f0dc3bd4e111407528bdb896c6e52708e6d8e2f17           787282 Contents-amd64.gz
 ed54771351ccfaf8f9cb9c5c7ef6f528779ae7a412a5e83c48a020382a0febbd         13984006 Contents-arm64
 17da1af7a1f5727ceb8930ea5dc1f81fa594f9428bec2ee5148351baac1f85e3           787237 Contents-arm64.gz
 283a4b39027087b213b39b9213b971bee36ea43aca1c18a45103810f156a8876         13993054 Contents-armhf
 c374cc2dd01b8c3022845c5144c02a6aac32c0fc54b0545e50061e949828b2c5           787556 Contents-armhf.gz
 3ee766fadc39d64e0802ab7a143b9f3b81164ce7150884199ed788fba61b3d00         13692747 Contents-i386
 0338098492149f076108f4b5f4c82cc997ad323b385cdab98bcfb0f00a2621f5           765737 Contents-i386.gz
 888238e91efbeb68dddc997b1f62e8c2d5a3eb9f70e7f696f17f31e611a62b2c         13845889 Contents-ppc64el
 bcd092cd2fe82a394ec90cbcb54ebb365ee17571ca3c8ba9b68a764a0c6853d0           778306 Contents-ppc64el.gz
 653690d5e651fc8dcefefe4abbb1a4a7e735eca1098c52a74e2c9da504fb4913         13834906 Contents-riscv64
 aa6c41006f788499aa3b296ccc4385cabab14cd0a1e4351e84e9011adb3785ca           777758 Contents-riscv64.gz
 233286559029e010672d6afef1bb23b556891d9a044a46fb872e7cf2c6c1e8dd         13977389 Contents-s390x
 b45e59afe297e4436dc851e5b50317516f04da82403aa879f9cce2007bbb497a           786595 Contents-s390x.gz
 0dbf7352fd30157619fb060ff2e39143fde22f0017b2a09b249bdd297c7c31fe           458763 main/binary-amd64/Packages
 ...
Acquire-By-Hash: yes
-----BEGIN PGP SIGNATURE-----

...

-----END PGP SIGNATURE-----

```

The key is that there are two different hash layers, and they protect different things.

In our `InRelease`, lines like:

```

MD5Sum:
 452bb7eaff9030d56be9267049aa2c90  458763 main/binary-amd64/Packages
 e7bc1964980b200d652cfb41df5c5615   78515 main/binary-amd64/Packages.gz
 ced56a0198f9cf3ed46195c2f36057f6   65852 main/binary-amd64/Packages.xz

```

are not hashes of individual `.deb` packages.

They are hashes of the **repository index files themselves**:

```

main/binary-amd64/Packages
main/binary-amd64/Packages.gz
main/binary-amd64/Packages.xz
Contents-amd64
...

```

Here, the filenames does not necessarly match the local indexes files on the system because the remote repository currently exposes the index such as:

```

dists/noble/main/binary-i386/Packages.gz
dists/noble/main/binary-i386/Packages.xz

```

(for reconstructing the URL where they are exposed)

APT downloads those compressed indexes, verifies them against the hashes recorded in the related `InRelease`, then may store the decompressed result locally as:

```

..._main_binary-i386_Packages

```

So searching the `InRelease` for the **literal local filename won’t work**.

Back to the architecture of a `InRelease` file:

Each hash line is basically:

```

HASH                  SIZE      FILE

```

The signed `InRelease` therefore authenticates **those indexes**.

Then inside the authenticated `Packages` file, we have another layer:

```

Package: bash
...
Filename: pool/main/b/bash/bash_5.2.21-2ubuntu4_amd64.deb
Size: 794086
SHA256: 73de311a21e094e29ac01527d2b52226cc87fde0a5b57032902251b426d92c66
SHA512: ...

```

Those hashes are the hashes of the individual `.deb` file.

There is also `Translation` files.

They contain translated package descriptions. Instead of duplicating translated descriptions inside every architecture-specific Packages index, repositories can distribute separate translation indexes such as:

```

Translation-en
Translation-fr

```

I can see them for example:

```bash

ls /var/lib/apt/lists/*Translation*

```

Output:

```

/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble-backports_main_i18n_Translation-en
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble-backports_multiverse_i18n_Translation-en
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble-backports_universe_i18n_Translation-en
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_i18n_Translation-en
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_i18n_Translation-fr
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_multiverse_i18n_Translation-en
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_multiverse_i18n_Translation-fr
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_restricted_i18n_Translation-en
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_restricted_i18n_Translation-fr
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_universe_i18n_Translation-en
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_universe_i18n_Translation-fr
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble-updates_main_i18n_Translation-en
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble-updates_multiverse_i18n_Translation-en
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble-updates_restricted_i18n_Translation-en
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble-updates_universe_i18n_Translation-en
/var/lib/apt/lists/ppa.launchpadcontent.net_neovim-ppa_stable_ubuntu_dists_noble_main_i18n_Translation-en
/var/lib/apt/lists/ppa.launchpadcontent.net_obsproject_obs-studio_ubuntu_dists_noble_main_i18n_Translation-en
/var/lib/apt/lists/security.ubuntu.com_ubuntu_dists_noble-security_main_i18n_Translation-en
/var/lib/apt/lists/security.ubuntu.com_ubuntu_dists_noble-security_multiverse_i18n_Translation-en
/var/lib/apt/lists/security.ubuntu.com_ubuntu_dists_noble-security_restricted_i18n_Translation-en
/var/lib/apt/lists/security.ubuntu.com_ubuntu_dists_noble-security_universe_i18n_Translation-en

```

Now, `Contents` indexes answer a different question:

“Which repository package contains this file?”

For example, `apt-file search foo.h` searches repository `Contents` indexes. This is why `apt-file` is roughly the Debian equivalent of `pacman -F`.

Indeed, after installing `apt-file` with:

```bash

apt install apt-file 

```

And updating the system to have the `Contents` files:

```bash

apt update

```

Then, we'll see what's concretely a `Contents` file, so I take one and decompress one.

```bash

cp /var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_Contents-i386.lz4 test_Contents.lz4

lz4 -d test_Contents.lz4 test_Contents

```

And we can finally look into it.

In fact it's just a simple file-path -> package name (of the related source) mapping.

Here's a sample:

```

bin/btrfs						    admin/btrfs-progs
bin/btrfs-convert					    admin/btrfs-progs
bin/btrfs-find-root					    admin/btrfs-progs
bin/btrfs-image						    admin/btrfs-progs
bin/btrfs-map-logical					    admin/btrfs-progs
bin/btrfs-select-super					    admin/btrfs-progs
bin/btrfsck						    admin/btrfs-progs
bin/btrfstune						    admin/btrfs-progs
bin/cgroups-mount					    universe/admin/cgroup-lite
bin/cgroups-umount					    universe/admin/cgroup-lite
bin/ed							    editors/ed
bin/fusermount						    utils/fuse3,universe/utils/fuse
bin/fusermount3						    utils/fuse3
bin/ip							    net/iproute2

```

Now, there are the `cnf_Commands`indexes files.

Those are the files used by the Ububntu "Command notfound" system.

Their purposes is to map shell command names to the packages that provide them.

Here's a list of the `cnf_Commands` indexes files I have on my system:

```bash

ls /var/lib/apt/lists/*cnf*

```

Output:

```

/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble-backports_main_cnf_Commands-amd64
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble-backports_multiverse_cnf_Commands-amd64
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble-backports_restricted_cnf_Commands-amd64
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble-backports_universe_cnf_Commands-amd64
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_cnf_Commands-amd64
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_multiverse_cnf_Commands-amd64
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_restricted_cnf_Commands-amd64
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_universe_cnf_Commands-amd64
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble-updates_main_cnf_Commands-amd64
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble-updates_multiverse_cnf_Commands-amd64
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble-updates_restricted_cnf_Commands-amd64
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble-updates_universe_cnf_Commands-amd64
/var/lib/apt/lists/security.ubuntu.com_ubuntu_dists_noble-security_main_cnf_Commands-amd64
/var/lib/apt/lists/security.ubuntu.com_ubuntu_dists_noble-security_multiverse_cnf_Commands-amd64
/var/lib/apt/lists/security.ubuntu.com_ubuntu_dists_noble-security_restricted_cnf_Commands-amd64
/var/lib/apt/lists/security.ubuntu.com_ubuntu_dists_noble-security_universe_cnf_Commands-amd64

```

And for example, in:

```

/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_cnf_Commands-amd64

```

I have this structure:

```

suite: noble
component: main
arch: amd64


name: acct
version: 6.6.4-5
commands: ac,accton,dump-acct,dump-utmp,lastcomm,sa

name: acl
version: 2.3.1-3
commands: chacl,getfacl,setfacl

name: acpid
version: 1:2.0.34-1ubuntu1
commands: acpi_listen,acpid

name: adcli
version: 0.9.2-1ubuntu1
commands: adcli

```

The first block (header) just describes to which repo source it belongs to.

Now, the body is composed of multiple blocks.

One block describes the package, its version and the commands it provides.

### The `apt upgrade` command

This is just the command to install the package(s) APT sees a newer version for by comparing the current installed version to the related one in its database.

It will temporally download the associated `.deb` file in `/var/cache/apt/archives` and install it from there.

We also have the `full-upgrade` equivalent that is allowed to remove others installed package(s) is that's necessary to complete the installation.

Indeed, we can summarize the distinction as:

```

apt upgrade
-> upgrades packages
-> may install new dependencies
-> avoids removing already-installed packages

apt full-upgrade
-> upgrades packages
-> may install new dependencies
-> may remove other packages if dependency changes require it

```

The key distinction is **other** packages. Because of course a normal `upgrade`, will for example remove the old `pkgA` to replace it with its newer version. But what about conflicts between `pkgA` and `pkgB` ?

Take this example:

```

installed:
pkgA 1.0
pkgB 1.0

```

And:

```

new repository state:
pkgA 2.0 Depends: pkgC
pkgA 2.0 Conflicts: pkgB

```

With:

```bash

sudo apt upgrade

```

APT may hold A back, because upgrading it would require removing `pkgB`.

With:

```bash

sudo apt full-upgrade

```

APT is allowed to choose:

```

remove pkgB
install pkgC
upgrade pkgA → 2.0

```

So `full-upgrade` gives APT more freedom to reshape the dependency graph.

Pacman does not have an `upgrade` vs `full-upgrade` split like APT.

If a package transition requires another package to be replaced or removed because of conflicts / replaces, `pacman` can handle that as part of the transaction, usually prompting us.

### The `apt remove` command

This is the equivament of `pacman -R pkg`, we just run:

```bash

apt remove pkg

```

The associated config files are not removed neither its depedencies.

### The `apt purge` command

This is the command that removes a package and its config files, or just its config files if already removed (see the example).

So this is the standard way:

```bash

apt purge pkg

```

But imagine we already removed the package (with `apt remove pkg`) and now we want to remove its config files, will the `purge` work ?

Yes.

You can just run:

```bash

apt purge pkg

```

Indeed, with just:

```bash

apt remove pkg

```

Its package-managed configuration files may remain. `dpkg` can keep the package in a state often described as “removed config-files remain”.

We can see such packages with:

```bash

dpkg -l

```

To list installed packages and their states (see later).

where the status may begin with:

```

rc

```

meaning roughly:

```

r = removed
c = config files remain

```

Pacman does not provide a way to remove a package's config files after removing it, we must directly use `pacman -Rn pkg`.

But because with `pacman -R pkg`, the associated config files are often renamed with the `.pacsave` extensions, we can just list them and remove them:

```bash

find /etc/ -name '*.pacsave' -exec rm {} +

```

### The `apt autoremove` command

This command is the closest to:

```bash

pacman -Rns $(pacman -Qdtq)

```

Telling to remove packages that were installed autmatically and are no longer needed.

### The `apt search` command

This searches the local APT repository metadata for packages that match the given expression, for example:

```bash

sudo apt search bash

```

On my system, this returns the following:

```

i   bash                                                                   - GNU Bourne Again SHell (interpréteur de commandes dérivé de celui de S. Bourne)
p   bash:i386                                                              - GNU Bourne Again SHell (interpréteur de commandes dérivé de celui de S. Bourne)
p   bash-argsparse                                                         - High level argument parsing library for bash
p   bash-builtins                                                          - Fonctions incorporables dans Bash : en-têtes et exemples
p   bash-builtins:i386                                                     - Fonctions incorporables dans Bash : en-têtes et exemples
i   bash-completion                                                        - complétions programmables pour l'interpréteur bash
v   bash-completion:i386                                                   -
p   bash-doc                                                               - Documentation et exemples pour BASH (« Bourne Again SHell », interpréteur de scr
p   bash-static                                                            - GNU Bourne Again SHell − version statique
p   bash-static:i386                                                       - GNU Bourne Again SHell − version statique
p   bashtop                                                                - Resource monitor that shows usage and stats
v   dh-sequence-bash-completion                                            -
p   elpa-bash-completion                                                   - add programmable bash completion to Emacs shell-mode
p   libbash                                                                - bibliothèques bash partagées de style dynamique
p   libbash-doc                                                            - bash dynamic-like shared libraries - documentation
p   netdata-plugins-bash                                                   - real-time performance monitoring (bash plugins)
p   node-bash                                                              - Utilities for using bash from node.js
p   node-bash-color                                                        - wrap strings in color codes for pretty printing in bash
p   node-bash-match                                                        - Node module to match strings using bash
p   oem-sutton-bash-meta                                                   - hardware support for Lenovo ThinkStation P5
p   python-bashate-doc                                                     - bash script style guide checker - doc
p   python3-bashate                                                        - contrôleur de guide de style pour script bash –⋅Python 3.x
p   python3-colcon-bash                                                    - collective construction meta build tool - bash extension

```

But we can also give RegEx.

```bash

sudo apt search '^bash$'

```

Returns the following:

```

i   bash                                                                   - GNU Bourne Again SHell (interpréteur de commandes dérivé de celui de S. Bourne)
p   bash:i386                                                              - GNU Bourne Again SHell (interpréteur de commandes dérivé de celui de S. Bourne)

```

The second line still refers to the `bash` package, while the `:i386` is just architecture qualifier added to the displayed layout.

### The `apt show` command

This is the command to query informations about an installed package, it's a little bit like looking into the `Packages` index file containing the package infos but with additional infromations concerning the status of tha package on the system.

For example:

```bash

apt show bash

```

Returns:

```

Package: bash
Version: 5.2.21-2ubuntu4
Priority: required
Essential: yes
Section: shells
Origin: Ubuntu
Maintainer: Ubuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>
Original-Maintainer: Matthias Klose <doko@debian.org>
Bugs: https://bugs.launchpad.net/ubuntu/+filebug
Installed-Size: 1 946 kB
Pre-Depends: libc6 (>= 2.38), libtinfo6 (>= 6)
Depends: base-files (>= 2.1.12), debianutils (>= 5.6-0.1)
Recommends: bash-completion
Suggests: bash-doc
Homepage: http://tiswww.case.edu/php/chet/bash/bashtop.html
Task: minimal
Download-Size: 794 kB
APT-Manual-Installed: yes
APT-Sources: http://archive.ubuntu.com/ubuntu noble/main amd64 Packages
Description: ...

```

Also, that's a good moment to talk about the 2 lasting fields we have not talked about.

First, the `Priority` flag.

As its name suggest, it describe how much the package is important to the system.

Typical values are:

```

required
important
standard
optional
extra

```

`Task` groups packages into system installation purposes.

For example:

```

Task: minimal

```

means the package belongs to the minimal task set, in other terms the set of packages intended for a **minimal system**.

Possible values are:

```

minimal
standard
desktop
server
ssh-server
ubuntu-desktop
kubuntu-desktop
xubuntu-desktop
language-related tasks

```

A package can belong to one or more tasks.

`Priority` and `Taks` are therefore different concepts but there's a strong correlation between them, for example a package belonging to the **minimal set** has a lot of "chances" of being **high priority**.

### The `apt-get` familly

`apt-get`, `apt-cache`, and `apt-mark` are older/specialized APT tools.

`apt` covers most of the operations of those one but not all, that's what we'll see.

`apt-file` is also specialized, but it is a separate utility rather than just an older frontend superseded by `apt`.

So I prefere 

So, back to `apt-get`.

We have the equivalent of `apt update`:

```bash

apt-get update

```

But `apt-get upgrade` is more conservative than `apt upgrade`.

Indeed, it installs packages when that can be done **without installing new packages or removing other installed ones**. If a set of packages require a graph change, then they are kept back and those who don't are normally upgraded.

That's why we have the more agressive:

```bash

apt-get dist-upgrade

```

Indeed, it upgrades the system while allowing dependency changes, including installing/removing packages when needed. This is the historical `apt-get` counterpart of `apt full-upgrade`.

Now, we have a perfect equivalent of `apt install pkg` with `apt-get install pkg`.

Also, the perfect equivalent of `apt remove pkg` with `apt-get remove pkg`, `apt download` with `apt-get download` and `apt purge pkg` with `apt-get purge pkg` such as `apt autoremove` with `apt-get autoremove`.

But with `apt-get`, we can even mix the behavior of `purge` and `autoremove` with:

```bash

apt-get autopurge

```

Or the other form:

```bash

apt-get autoremove --purge

```

Here, we apply the un-scoped `autoremove` operation and the `purge` operation that is here scoped to the package(s) `autoremove` did remove contrary to being just scoped to one or few input package(s) with standard `apt purge pkg1 pkg2 ...`.

Now, we also have this command:

```bash

apt-get source pkg

```

That won't download the `.deb` file of the associated package but its source package, in other terms the files that were used to make the corresponding `.deb` file.


It requires to configure a source package repository entry.

Indeed, a `.deb` entry is like:

```

deb-src http://archive.ubuntu.com/ubuntu noble main restricted universe multiverse

```

So, a source package entry is like:

```

deb-src http://archive.ubuntu.com/ubuntu noble main restricted universe multiverse

```

A typical non-native Debian source package using the 3.0 (quilt) format consists of three main files:

```

foo_1.2.3-1.dsc
foo_1.2.3.orig.tar.*
foo_1.2.3-1.debian.tar.*

```

Their roles are:

- `.dsc` -> contains hashes of the source-package files (like the `.tar.*` files) ans is OpenPGP signed

- `.orig.tar.*` -> original upstream source code

- `.debian.tar.*` -> Debian/Ubuntu packaging material + maintainer scripts/templates, etc.

Indeed, at first the developper has something like:

```

foo-1.2.3/
|-- src/
|   |-- main.c
|   |-- foo.c
|   |-- util.c
|-- include/
|   |-- foo.h
|   |-- util.h
|-- docs/
|-- tests/
|-- Makefile
|-- configure
|-- README
|-- LICENSE
|-- debian/
    |-- control
    |-- rules
    |-- changelog
    |-- patches/
    |   ├── series
    |   └── fix-something.patch
        |-- fix-something2.patch
    |-- foo.install
    |-- foo-doc.install

```

The source package is split conceptually into:

```

foo_1.2.3.orig.tar.xz

```

containing upstream material:

```

src/
include/
docs/
tests/
Makefile
configure
README
LICENSE
...

```

and:

```

foo_1.2.3-1.debian.tar.xz

```

containing Debian packaging:

```

debian/
|-- control
|-- rules
|-- changelog
|-- patches/
|-- foo.install
|-- ...

```

plus:

```

foo_1.2.3-1.dsc

```

Together, they constitute the Debian source package.

Then the build server unpacks them.

It applies the patch(es) in the order `debian/patches/series` describe.

Then it invokes the Debian build process, typically through something like:

```bash

dpkg-buildpackage

```

Which eventually runs `debian/rules`.

`debian/rules` exists because the upstream Makefile and Debian packaging solve different problems.

The upstream Makefile answers:

**How do I build this software (being distro agnostic) ?**

For example:

```bash

make
make test
make install

```

But Debian needs a higher-level recipe that answers:

**How do I turn this upstream project into Debian packages ?**

That includes things like:

- how Debian wants to invoke the build

- which flags Debian wants

- which staging directories to use 

- which binary packages to produce

- which `debhelper` (`dh` command see later) steps to run

So `debian/rules` is basically the Debian packaging Makefile / build driver.

For an old-style package it might contain explicit targets like:

```bash

#!/usr/bin/make -f

build:
	./configure --prefix=/usr
	$(MAKE)

install:
	$(MAKE) install DESTDIR=$(CURDIR)/debian/tmp

clean:
	$(MAKE) clean

binary:
	...

```

Here `debian/rules` is calling the project's own:

- `configure`

- `Makefile`

Technically, we could put Debian-specific packaging logic into the upstream Makefile. But it would be a poor separation of concerns.

The upstream Makefile is supposed to describe how to build the software in a distro-neutral way.

A `debian/*.install` file tells Debian packaging tools which built/**staged** files should go into a given binary package, and where they should end up inside that package.

For example:

```

# debian/foo.install

usr/bin/foo usr/bin/
usr/bin/foo-helper usr/lib/foo/

```

means:

Take `debian/tmp/usr/bin/foo` and put it in `debian/foo/usr/bin/foo/`.

Take `debian/tmp/usr/bin/foo-helper` and put it in `debian/foo/usr/lib/foo/`.

Indeed, `dh_install` treats those source paths as coming from the temporary staging area such as `debian/tmp`, then copies them into the package build directory, which by default is `debian/foo/`.

So the resulting package staging tree becomes roughly:

```

debian/foo/
|-- usr/
|   |-- bin/
|   |   |-- foo
|   |-- lib/
|       |-- foo/
|           |-- foo-helper

```

And that is the tree that ultimately becomes the payload of `.deb's data.tar.*`. It will tell to install the files in the user system at, respectively `/usr/bin/foo`and `/usr/lib/foo`.

In the `dpkg-buildpackage` process, after compiling and before putting the binaries into the stagging location, the upstream build process can end up puting compiled programms into `builds` for example, so we end up with:

```

foo-1.2.3/
├── src/
├── include/
├── debian/
└── build/          <- created by CMake/Meson/etc.
    ├── foo
    ├── foo.o
    └── ...

```

This **is not the same** as `debian/tmp/`, which is the temporary staging area used by the Debian packaging process (before `debian/foo`).

We can describe the separations with:

```

build/
-> upstream compilation output
-> e.g. build/foo, build/foo.o

debian/tmp/
-> temporary installation staging tree
-> e.g. debian/tmp/usr/bin/foo

debian/foo/
-> final staging tree for binary package foo
-> its contents become data.tar.*

```

A last file we have not covered for the package sources is `debian/changelog`.

It records the packaging history and also supplies important current-build metadata, especially the package version.

Example:

```

foo (1.2.3-2) noble; urgency=medium

  * Fix build with GCC 15.
  * Add patch for bug #12345.

 -- Jane Doe <jane@example.com>  Sun, 20 Sep 2026 15:30:00 +0200

```

Back to the `apt-get` familly.

To resolve and instlall depedencies required to **build** a package from its source files we run:

```bash

apt-get build-dep pkg

```

or:

```

apt build-dep pkg

```

For example, if the package declares:

```

Build-Depends: gcc, make, libssl-dev, pkg-config

```

Then, it will resolve and normally install those dependencies.

If one or more of the required packages conflicts with installed package(s), then they are removed.

We also have the `apt-get satisfy` command.

This is a powerfull command that will try to modify the system and depedencies graph to satisfy the input expression, such as installing a certain version of a package:

```bash

apt-get satisfy 'foo (>= 2.0)'

```

Or having a system state where a package is absent:

```bash

apt-get satisfy 'Conflicts: bar'

```

We can even do multiple at once:

```bash

apt-get satisfy 'foo (>= 2.0)' 'Conflicts: bar'

```

It will prompt you the changes to accept or refuse them.

Or you can just test if the proposed expressions can be satisfied by just simulating the effect:

```bash

apt-get satisfy -s 'foo (>= 2.0)' 'Conflicts: bar'

```

or:

```bash

apt-get satisfy --simulate 'foo (>= 2.0)' 'Conflicts: bar'

```

If you give contradictory expressions such as `foo (>= 2.0)` that needs `bar` but you also say `Conflicts: bar`, then the command will fail and report why it failed.

So `apt-get satisfy` is useful not only to make constraints true, but also to test whether a requested dependency state is actually solvable.

To check if you have broken packages and/or depedencies system wide, you can use:

```bash

apt-get check

```

or:

```bash

apt check

```

The equivalent `pacman` command is:

```bash

pacman -Dk

```

and we can extend those checks using the sync database as we've discussed earlier ith double `k`:

```bash

pacman -Dkk

```

To remove downloaded `.deb` files from `/var/cache/apt/archives` and `/var/cache/apt/archives/partial`, we run:

```bash

apt-get clean

```

or:

```bash

apt clean

```

Btw, that's a good moment to introduce you to the lockfile concept that we have across a lot (if that's not all) package managers.

Indeed, for APT the file is permant and is at this location:

```

/var/cache/apt/archives/lock

```

Its state can change between held when an APT process is running and not held when no APT process is running.

Indeed, at the start of an APT commad, the latter will see the state of this lockfile and if it's held, then another APT process is running and to avoid race conditions it'll stop. 

We have the same concept for `pacman`, but differs in meaning.

Here, its location is at:

```

/var/lib/pacman/db.lck

```

And is only present when a Pacman process is running.

This is also a good moment to introduce the lock-file concept used by package managers to prevent concurrent operations from modifying the same package-management state.

APT uses several lock files for different resources. One of them is:

```

/var/cache/apt/archives/lock

```

which protects access to the package archive cache.

With APT, the lock file itself can remain permanently on disk. What matters is whether a process currently holds an operating-system-level lock on it.

Before performing an operation requiring that resource, APT attempts to acquire the corresponding lock. If another package-management process already holds it, APT cannot safely perform the conflicting operation until that lock becomes available.

Pacman uses a slightly different mechanism for its package database:

```

/var/lib/pacman/db.lck

```

When pacman is about to modify its package database, for example during an installation, upgrade, or removal, it creates this file to prevent another `pacman` transaction from modifying the database simultaneously.

Unlike APT's persistent lock files, `pacman`'s `db.lck` is normally removed when the transaction finishes.

Therefore:

```

APT
lock file can permanently exist
-> the important state is whether the file is currently locked

pacman
db.lck normally exists while a database-modifying transaction is active
-> its presence itself normally indicates that the database is locked

```

If `pacman` is interrupted or crashes, `db.lck` may remain even though no pacman process is running. This is known as a stale lock file.

Ok, a less agressive command for cleaning the cache is:

```bash

apt-get autoclean

```

or:

```bash

apt autoclean

```

It removes cached `.deb` files that can no longer be downloaded from configured repositories, while retaining still-current cached packages.

Now, a very specialized but somewhat usefull command when you want to shrink your image/filesystem before distributing it to ,for example, a container is the one that removes most of the indexes files.

This one:

```bash

apt-get distclean

```

removes `Translations`, `Contents` and `Packages` indexes files, it only keep the `InRelease` ones.

Then, after we have distributed the image, when we'll run `apt update` so `/var/lib/apt/lists` will be populated by the required indexes files that have been previously removed.


We have more specialized commands such as:

```bash

apt-get changelog pkg

```

Or:

```bash

apt changelog pkg

```

That will download and display the package's changelog through a pager.

Therefore, the package doesn't even have to be installed to audit the changelogs.

Now, we have a command that allow to return metadata about the index files APT knows how to fetch:

```bash

apt-get indextargets

```

Inded, APT regroup them into class instances and give them different values related to their nature.

They are also assigned a template identifier, for example:

```

deb::Contents-deb

```

And importantly a filename convention which will be used like a key to retreive files that have the same nature, such as:

```

flatMetaKey "Contents-$(ARCHITECTURE)";

```

Which correspond to these files for example:

```

/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_Contents-amd64.lz4
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble-backports_Contents-i386.lz4
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_Contents-amd64.lz4
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_Contents-i386.lz4

```

Several special values exists, such as if files must be compressed or not. 

We can check inside `/etc/apt/apt.conf.d/50apt-file.conf` this class for example:

```

deb::Contents-deb  {
    MetaKey "$(COMPONENT)/Contents-$(ARCHITECTURE)";
    ShortDescription "Contents-$(ARCHITECTURE)";
    Description "$(RELEASE)/$(COMPONENT) $(ARCHITECTURE) Contents (deb)";

    flatMetaKey "Contents-$(ARCHITECTURE)";
    flatDescription "$(RELEASE) Contents (deb)";
    PDiffs "true";
    KeepCompressed "true";
};

```

It describes the files given above (among others).

The `PDiffs` field means **package index diffs**: incremental updates for repository index files.

Instead of always downloading a whole new index like:

```

Contents-amd64
Packages

```

APT can sometimes download only the differences between our old local copy and the new repository version.

Conceptually:

```

old Packages + small diff(s) = new Packages

```

So with:

```

PDiffs "true";

```

APT is allowed to use those incremental patch files when the repository provides them.

That can save bandwidth when an index is large but only a small portion changed.

Without `PDiffs`, the update is more like:

```

download entire new Packages.xz
-> replace old local index

```

With PDiffs:

```

download small incremental patches
-> apply them to old index
-> reconstruct current index

```

### The `apt-cache` familly


`apt-cache` is the read/query side of APT. 

It does not install, remove, or upgrade packages.

Indeed, it inspects APT’s local package metadata/cache, which is built from the repository indexes downloaded by `apt update`. Because it works from local metadata, it can still answer queries even when the repositories are temporarily unreachable

First, we have:

```bash

apt-cache search SOME-REGEX

```

It performs a text search over package names and description, so if the RegEx matches the package name and/or the related description then the package name and its summary are returned, for example:

```bash

sudo apt-cache search ssh

```


Outputs:

```

libpam-fingwit - Smart PAM module for fingerprint authentication
backuppc - système à hautes performances de sauvegarde de PC en entreprise
byobu - gestionnaire de fenêtre en mode texte, multiplexeur de shells, environnement DevOps intégré
dbus-user-session - simple interprocess messaging system (systemd --user integration)
erlang-ssh - mise en œuvre en Erlang/OTP du protocole SSH
gnome-keyring - Services de porte-clés de GNOME (démon et outils)
gnome-keyring-pkcs11 - Module de trousseau de clés GNOME pour la bibliothèque de chargement du module PKCS#11
libpam-gnome-keyring - Module PAM pour déverrouiller le trousseau de GNOME lors de la connexion
libssh-4 - tiny C SSH library (OpenSSL flavor)
libssh-dev - tiny C SSH library - Development files (OpenSSL flavor)
libssh-doc - tiny C SSH library - Documentation files
libssh-gcrypt-4 - tiny C SSH library (gcrypt flavor)
libssh-gcrypt-dev - tiny C SSH library - Development files (gcrypt flavor)
libssh2-1-dev - SSH2 client-side library (development headers)
libssh2-1t64 - Bibliothèque client SSH2
openssh-client - Client shell (SSH), pour accèder de manière sécurisée à des machines distantes
openssh-server - Serveur Secure Shell (SSH), pour un accès sécurisé à partir de machines distantes
paramiko-doc - Effectuer des connexions SSH v2 avec Python (Documentation)

```

Then, we can query the famous information block for a package and its downloaded versions using:

```bash

apt-cache show pkg

```

For example:

```bash

apt-cache show ssh

```

Outputs:

```

Package: ssh
Source: openssh
Priority: optional
Section: net
Installed-Size: 58
Maintainer: Ubuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>
Architecture: all
Version: 1:9.6p1-3ubuntu13.19
Depends: openssh-client (>= 1:9.6p1-3ubuntu13.19), openssh-server (>= 1:9.6p1-3ubuntu13.19)
Filename: pool/main/o/openssh/ssh_9.6p1-3ubuntu13.19_all.deb
Size: 4658
MD5sum: fd5bc288bd9f1909ca24e0a6e87f3d20
SHA1: 79de0e7d2738694d98f8e50a0428fb9964157615
SHA256: 413a26c1ba964619715d871acbe212c6ac17349409a14a1d61055b9e75e936be
SHA512: 67318f4919e7b8b06e169fe18bf33826528ceec5820c2153a6aca963a8bc396c9f84fa75aca63be50eb689cc195b3c0e4c12e38f03192b5783e0d562935da61a
Homepage: https://www.openssh.com/
Description-fr: client et serveur shell sécurisé –⋅métapaquet
 Ce métapaquet est une manière pratique d'installer à la fois le client et
 le serveur OpenSSH. Il ne fournit rien en lui-même, aussi il peut être
 supprimé si aucun paquet ne dépend de lui.
Description-md5: b00e309365895c14a10af55945efb136
Multi-Arch: foreign
Original-Maintainer: Debian OpenSSH Maintainers <debian-ssh@lists.debian.org>
Origin: Ubuntu
Bugs: https://bugs.launchpad.net/ubuntu/+filebug

Package: ssh
Architecture: all
Version: 1:9.6p1-3ubuntu13
Multi-Arch: foreign
Priority: optional
Section: net
Source: openssh
Origin: Ubuntu
Maintainer: Ubuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>
Original-Maintainer: Debian OpenSSH Maintainers <debian-ssh@lists.debian.org>
Bugs: https://bugs.launchpad.net/ubuntu/+filebug
Installed-Size: 56
Depends: openssh-client (>= 1:9.6p1-3ubuntu13), openssh-server (>= 1:9.6p1-3ubuntu13)
Filename: pool/main/o/openssh/ssh_9.6p1-3ubuntu13_all.deb
Size: 4650
MD5sum: a28fa73500ea0d2c093c5313831d0e16
SHA1: 55e960cc4f0a1c3ad8977abfce94ead1e1d85e5f
SHA256: dabdba578184f38c1b5525174ee96de35ea810c8e289eae7a4e10e6972858647
SHA512: 141a3783919618ab8e0766e64a63e38df04078e3c1bf5288a55df864e49f53955ba3f52cd0ddaaf27b8c59255448e63db9a872cf0f3474906c3b9d522f3a4bb9
Homepage: https://www.openssh.com/
Description-fr: client et serveur shell sécurisé –⋅métapaquet
 Ce métapaquet est une manière pratique d'installer à la fois le client et
 le serveur OpenSSH. Il ne fournit rien en lui-même, aussi il peut être
 supprimé si aucun paquet ne dépend de lui.
Description-md5: b00e309365895c14a10af55945efb136

```

We can limit to just return the info block for the candidate versions with the `--no-all-versions` flag:

```bash

sudo apt-cache --no-all-versions show ssh

```

Outputs:

```

Package: ssh
Source: openssh
Priority: optional
Section: net
Installed-Size: 58
Maintainer: Ubuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>
Architecture: all
Version: 1:9.6p1-3ubuntu13.19
Depends: openssh-client (>= 1:9.6p1-3ubuntu13.19), openssh-server (>= 1:9.6p1-3ubuntu13.19)
Filename: pool/main/o/openssh/ssh_9.6p1-3ubuntu13.19_all.deb
Size: 4658
MD5sum: fd5bc288bd9f1909ca24e0a6e87f3d20
SHA1: 79de0e7d2738694d98f8e50a0428fb9964157615
SHA256: 413a26c1ba964619715d871acbe212c6ac17349409a14a1d61055b9e75e936be
SHA512: 67318f4919e7b8b06e169fe18bf33826528ceec5820c2153a6aca963a8bc396c9f84fa75aca63be50eb689cc195b3c0e4c12e38f03192b5783e0d562935da61a
Homepage: https://www.openssh.com/
Description-fr: client et serveur shell sécurisé –⋅métapaquet
 Ce métapaquet est une manière pratique d'installer à la fois le client et
 le serveur OpenSSH. Il ne fournit rien en lui-même, aussi il peut être
 supprimé si aucun paquet ne dépend de lui.
Description-md5: b00e309365895c14a10af55945efb136
Multi-Arch: foreign
Original-Maintainer: Debian OpenSSH Maintainers <debian-ssh@lists.debian.org>
Origin: Ubuntu
Bugs: https://bugs.launchpad.net/ubuntu/+filebug

N: Il y a 1 enregistrement supplémentaire. Veuillez utiliser l'opérande « -a » pour le voir

```

The candidate version is the version APT would currently choose if we ran:

```

sudo apt install pkg

```

It may differ from the version actually installed.

Now, we can also have a more depedencies graph focused output of the role of a package in the system with:

```bash

apt-cache showpkg pkg

```

It outputs information about the package's known versions, direct dependencies, reverse dependencies, packages that provide it, and some of the APT index files from which its package and description metadata were loaded, such as `Packages` and `Translation-*` indexes.

```bash

apt-cache showpkg ssh

```

Outputs:

```

1:9.6p1-3ubuntu13.19 (/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble-updates_main_binary-amd64_Packages) (/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble-updates_main_binary-i386_Packages) (/var/lib/apt/lists/security.ubuntu.com_ubuntu_dists_noble-security_main_binary-amd64_Packages) (/var/lib/apt/lists/security.ubuntu.com_ubuntu_dists_noble-security_main_binary-i386_Packages)
 Description Language:
                 File: /var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-amd64_Packages
                  MD5: b00e309365895c14a10af55945efb136
 Description Language: fr
                 File: /var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_i18n_Translation-fr
                  MD5: b00e309365895c14a10af55945efb136
 Description Language: en
                 File: /var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_i18n_Translation-en
                  MD5: b00e309365895c14a10af55945efb136
 Description Language:
                 File: /var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble-updates_main_binary-amd64_Packages
                  MD5: b00e309365895c14a10af55945efb136

1:9.6p1-3ubuntu13 (/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-amd64_Packages) (/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-i386_Packages)
 Description Language:
                 File: /var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_binary-amd64_Packages
                  MD5: b00e309365895c14a10af55945efb136
 Description Language: fr
                 File: /var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_i18n_Translation-fr
                  MD5: b00e309365895c14a10af55945efb136
 Description Language: en
                 File: /var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_i18n_Translation-en
                  MD5: b00e309365895c14a10af55945efb136
 Description Language:
                 File: /var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble-updates_main_binary-amd64_Packages
                  MD5: b00e309365895c14a10af55945efb136


Reverse Depends:
  ssh-askpass-gnome,ssh 1:3.5p1-3
  openssh-client,ssh
  ssh-askpass-gnome:i386,ssh 1:3.5p1-3
  ubuntu-boot-test,ssh
  ssh-askpass-gnome,ssh 1:3.5p1-3
  ssh-askpass-gnome,ssh 1:1.2pre7-4
  openssh-server:i386,ssh
  openssh-client:i386,ssh
  openssh-server,ssh
  openssh-client,ssh
  ssh-askpass-gnome:i386,ssh 1:3.5p1-3
  xtightvncviewer,ssh
  ubuntu-boot-test,ssh
  ssh-askpass-gnome,ssh 1:1.2pre7-4
  pdsh,ssh 1:3.8.1p1-9
  slbackup-php,ssh
  slbackup,ssh
  runoverssh,ssh
  rancid,ssh
  proxytunnel,ssh
  dirvish,ssh 3.4p1
  mrbayes-mpi,ssh
  mew-beta,ssh
  mew,ssh
  mandos-client,ssh
  maildirsync,ssh
  im,ssh
  hdup,ssh
  dish,ssh
  dupload,ssh
  chake,ssh
  cedar-backup3,ssh
  bootcd,ssh
  openssh-server:i386,ssh
  openssh-client:i386,ssh
  openssh-server,ssh
  openssh-client,ssh
Dependencies:
1:9.6p1-3ubuntu13.19 - openssh-client (2 1:9.6p1-3ubuntu13.19) openssh-server (2 1:9.6p1-3ubuntu13.19)
1:9.6p1-3ubuntu13 - openssh-client (2 1:9.6p1-3ubuntu13) openssh-server (2 1:9.6p1-3ubuntu13)
Provides:
1:9.6p1-3ubuntu13.19 - ssh:i386 (= 1:9.6p1-3ubuntu13.19)
1:9.6p1-3ubuntu13 - ssh:i386 (= 1:9.6p1-3ubuntu13)
Reverse Provides:

```

A quick summary between `Provides` and `Reverse-Provides` concept:

- `Provides` -> virtual-package names that THIS package provides

- `Reverse Provides` -> packages that provide THIS package name

A virtual package is a package name that does not necessarily correspond to a real `.deb` file by itself. Instead, other real packages declare that they provide that capability/name.

Classic example:

```

mail-transport-agent

```

There may be no actual:

```

mail-transport-agent_....deb

```

Instead, packages such as:

```

postfix
exim4-daemon-light

```

can declare:

```

Provides: mail-transport-agent

```

Then another package can depend on the **generic capability**:

```

Depends: mail-transport-agent

```

rather than hard-coding:

```

Depends: postfix

```

APT can then satisfy that dependency with any suitable provider.

`pacman` has essentially the same concept through provides.

Now, we have a way to see a package depedency relationships and possible package(s) to satisfy it with:

```bash

apt-cache depends pkg

```

That's a bit like:

```bash

apt-get satisfy --simulate pkg

```

 but the latter retruns the **required transaction(s)** while the first is just descriptive.

 For example:

```bash

apt-cache depends ssh

```

Returns:

```

ssh
  Dépend: openssh-client
    openssh-client:i386
  Dépend: openssh-server
    openssh-server:i386

```

Here, the fields such as `Pre-Depends`, `Recommends`, `Suggests` and `Conflicts` are not returned because they are empty.

We can filter dependency relationship types with flags such as:

```

--no-depends
--no-pre-depends
--no-recommends
--no-suggests
--no-conflicts
--no-breaks
--no-replaces
--no-enhances

```

`Conflicts` is the strongest one. If package `A` says:

```

Conflicts: B

```

then `A` and `B` are not allowed to be unpacked/installed on the system at the same time. 

Installing one generally requires removing the other first. Debian Policy explicitly describes `Conflicts` as stronger than `Breaks`. 

Debian `Breaks` is weaker and usually version-scoped. If:

```

Breaks: B (<< 2.0)

```

that means that this version of `A` makes old versions of `B` unusable or unconfigurable.

But a sufficiently new `B` may coexist perfectly fine:

```

A
Breaks: B (<< 2.0)

B 1.5 no
B 2.0 yes
B 3.0 yes

```

That’s why Debian prefers `Breaks` for transitions ... or situations where only older versions are incompatible. It gives the resolver more freedom to upgrade `B` instead of requiring its complete removal. 

So the semantic difference is basically:

- `Conflicts` -> these packages fundamentally cannot coexist

- `Breaks` -> this package breaks certain versions of another package

That distinction matters a lot during upgrades.

`Replaces` is different again. It is primarily about file ownership/overwriting.

For example, suppose installed package `A` owns:

```

/usr/bin/foo

```

and package `B` is being updated so that now `B` should own that same file.

Then `B` may declare:

```

Replaces: A

```

Which tells `dpkg` that `B` is allowed to overwrite files that previously belonged to `A`. 

Two packages can not simutaneously own the same file.

Therefore, `Replaces` is not a subset of `Conflicts`.

We can also see the following together:

```

Breaks: A (<< 2.0)
Replaces: A (<< 2.0)

```

Meaning that old `A` cannot remain configured with this `B` and `B` is also allowed to take ownership of files previously owned by `A`.

Or sometimes:

```

Conflicts: A
Replaces: A

```

For a true mutually exclusive replacement.

Now the `Enhances` value.

`Enhances` is closely related to `Suggests`, but in the opposite direction. 

Suppose:

```

Package: foo
Suggests: foo-plugin

```

That means:

“Users of `foo` may benefit from installing `foo-plugin`.”

The arrow is:

```

foo
  |-- Suggests → foo-plugin

```

With `Enhances`, the plugin can instead declare:

```

Package: foo-plugin
Enhances: foo

```

meaning:

“Installing me adds/enhances functionality of `foo`.”

So:

```

foo-plugin
    |-- Enhances → foo

```

They describe roughly the same optional relationship from opposite viewpoints.

From the values, we saw, the only one Pacman has no direct equivalent to is `Breaks`.

Now, the command used to inspect **reverse** dependency relationships is:

```bash

apt-cache rdepends pkg

```

For example:

```bash

apt-cache rdepends ssh

```

may output:

```

ssh
Reverse Depends:
  ssh-askpass-gnome
  openssh-client
  ubuntu-boot-test
  ...

```

Unlike `apt-cache depends`, the output does not label every result with a visible relationship type such as `Depends`, `Recommends`, or `Suggests`. However, these relationship types still affect which reverse relationships are selected, and they can be filtered with the `--no-*` options above.

For example:

```bash

apt-cache rdepends ssh | wc -l

```

may return:

```

33

```

while:

```bash

apt-cache rdepends --no-recommends ssh | wc -l

```

may return:

```

25

```

This shows that some of the reverse relationships included in the default output came from `Recommends` relationships rather than strict `Depends` relationships.

`apt-cache policy pkg` shows the installed version, the candidate version selected by APT, all known available versions, their pin priorities, and the repository indexes from which those versions are available.

For example!

```bash

sudo apt-cache policy ssh

```

Outputs:

```

ssh:
  Installé : (aucun)
  Candidate : 1:9.6p1-3ubuntu13.19
 Table de version :
     1:9.6p1-3ubuntu13.19 500
        500 http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages
        500 http://archive.ubuntu.com/ubuntu noble-updates/main i386 Packages
        500 http://security.ubuntu.com/ubuntu noble-security/main amd64 Packages
        500 http://security.ubuntu.com/ubuntu noble-security/main i386 Packages
     1:9.6p1-3ubuntu13 500
        500 http://archive.ubuntu.com/ubuntu noble/main amd64 Packages
        500 http://archive.ubuntu.com/ubuntu noble/main i386 Packages

```

Here, we see that each versions have multiple providers.

We also see that both versions have the same `500` priority, so APT will still prefere the newer versions that is `1:9.6p1-3ubuntu13.19 500`. That's why we see it in `Candidate`.

The very confusing field is:

```

Installé : (aucun)

```

In english meaning:

```

Installed : (none)

```

The missing pience is that there are **two different packages**:

```

ssh
openssh-client

```

The package `ssh` exists in the repositories, so:

```bash

apt-cache policy ssh

```

can correctly report:

```

Candidate: 1:9.6p1-3ubuntu13.19
Version table:
...

```

because APT finds a package record literally named `ssh` in the `Packages` indexes files.

But that package is not installed locally, hence:

```

Installed: (none)

```

We also have:

```bash

apt-cache madison pkg

```

that gives a compact table of repositories that provides it, for example:

```bash

apt-cache madison pkg

```

Gives:

```

ssh | 1:9.6p1-3ubuntu13.19 | http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages
ssh | 1:9.6p1-3ubuntu13.19 | http://archive.ubuntu.com/ubuntu noble-updates/main i386 Packages
ssh | 1:9.6p1-3ubuntu13.19 | http://security.ubuntu.com/ubuntu noble-security/main amd64 Packages
ssh | 1:9.6p1-3ubuntu13.19 | http://security.ubuntu.com/ubuntu noble-security/main i386 Packages
ssh | 1:9.6p1-3ubuntu13 | http://archive.ubuntu.com/ubuntu noble/main amd64 Packages
ssh | 1:9.6p1-3ubuntu13 | http://archive.ubuntu.com/ubuntu noble/main i386 Packages

```

There is no way to filter an explicit version neither a provider by giving a certain pattern/format. For that we'll use `grep` or`awk`.

We also have:

```

apt-cache pkgnames [prefix]

```

That prints package names APT knows about, optionally restricted by prefix (does not support RegEx). This includes names that may be virtual.

For example here I list packages whose prefix begins with "cup":

```bash

apt-cache pkgnames cup

```

This returns:

```

cups-filters
cups-backend-bjnp
cup
cups-bsd
cups-common
cupt-dbg
cups-client
cups-ppdc
cups-daemon
cups-x2go
cups-browsed-tests
cups-filters-core-drivers
cups-ipp-utils
cups-tea4cups
cupp3
cups-browsed
cups-pk-helper
cups-core-drivers
cupp
cups
cupt
cups-server-common

```

We also can see a bunch of statistics of APT with:

```bash

apt-cache stats

```

This returns:

```

Total package names: 165741 (4,641 k)
Total package structures: 159560 (7,021 k)
  Normal packages: 88270
  Pure virtual packages: 3329
  Single virtual packages: 51537
  Mixed virtual packages: 3718
  Missing: 12706
Total distinct versions: 110211 (9,699 k)
Total distinct descriptions: 243853 (5,852 k)
Total dependencies: 709203/181127 (17.1 M)
Total ver/file relations: 46320 (1,112 k)
Total desc/file relations: 47245 (1,134 k)
Total Provides mappings: 85160 (2,044 k)
Total globbed strings: 290123 (7,404 k)
Total dependency version space: 100 k
Total slack space: 100 k
Total space accounted for: 57.7 M
Total buckets in PkgHashTable: 196613
  Unused: 91212
  Used: 105401
  Utilization: 53.6084%
  Average entries: 1.51384
  Longest: 20
  Shortest: 1
Total buckets in GrpHashTable: 196613
  Unused: 84516
  Used: 112097
  Utilization: 57.014%
  Average entries: 1.47855
  Longest: 7
  Shortest: 1

```

`Total package names:` is the number of package names APT knows about in its cache. This is not the number of installed packages. It can include real packages, virtual package names...


Remainder, here we reference the APT's cache that is not a throw away memory but rather the semi-permanant files under:

```

/var/lib/apt/lists

```

This can be viewed as a "cache" from the repositories servers perspective.

Btw, wee see their sizes in bytes inside the related parenthesis, for this one it occupies `4 641 k`.

The `4,641 k` is associated with the APT cache structures for those package-name entries (structures, pointers, strings...), not with the sizes of the actual `.deb` packages.

`Total package structures:` is an internal APT count of package objects/structures allocated in the cache. It's an APT internal.

Now, `Normal packages:` means ordinary real package names with a straightforward package-name relationship. These are the normal packages we think of, such as `bash`, `coreutils`, `openssh-client`, etc.


`Pure virtual packages:` means names that exist only as virtual capabilities. There is no real package with that exact name.

`Single virtual packages` means virtual names that have exactly one provider. So conceptually:

```

virtual-name
    ^
    |
provided by exactly one real package

```

APT still treats the name as virtual, but there is no ambiguity about which real package provides it.

`Mixed virtual packages:` is an interesting case: a name exists as an actual package and is also provided by another package.

Conceptually:

```

...
Package: foo
...

```

exists as a real package, but another package can also say:

```

...
Provides: foo
...

```

So `foo` is both a real package name and a provided/virtual name.

`Missing:` means APT has encountered package names in dependency-like relationships but no package currently provides them.

For example, some metadata might contain:

```

Breaks: old-foo

```

but no repository we currently have configured contains or provides `old-foo`.

Then, `Total distinct versions:` counts package-version objects known to APT.

For example, one package name could have:

```

foo 1.0
foo 1.1
foo 2.0

```

That is 1 package name and 3 distinct versions.

Because we have several suites such as `noble`, `noble-updates`, `noble-security`, etc., the same package may contribute multiple known versions.

`Total distinct descriptions:` counts distinct package description records. This can be much larger than the package count because APT can have descriptions for multiple versions and languages as we saw earlier with the `Translation` indexes files.

`Total dependencies: 709203/181127` is about dependency relationship objects in APT's cache.

This includes relationships such as:

```

Depends
Pre-Depends
Recommends
Suggests
Conflicts
Breaks
Replaces
Enhances

```

The first number represents the dependency records; the second is related to APT's internal dependency grouping/unique structures. This is one of those fields where the exact internal distinction is more implementation-oriented than user-facing.

`Total ver/file relations:` means mappings between package records and `Packages` index files.

That is exactly the sort of relationship we saw with `apt-cache showpkg`.

Similarly `Total desc/file relations:` counts mappings between description records and index files, such as:

```

French bash description
    |
    V comes from
..._Translation-fr

```

Then `Total Provides mapping:` is the count of the `Provides` relationships (that often gives virtual packages).

`Total dependency version space:` is memory reserved for the version constraints attached to dependency relationships.

So this value is specifically the space used for the version-expression side of dependencies, not for all dependency objects themselves. The main dependency structures are already counted separately under:

```

Total dependencies: ...

```

`Total globbed strings:` is one of the more implementation-specific APT statistics.

It refers to strings that APT stores in a shared/deduplicated form inside its package cache. The idea is that many package records repeat the same text fragments—package names, versions, architecture names, dependency target names, and similar strings; so APT can store one copy and have many structures refer to it instead of duplicating the same bytes over and over.

`Total slack space:` is unused space inside the cache allocation/layout. APT’s binary cache is organized into allocated regions/structures, and not every allocated byte ends up containing useful data.

And `Total space accounted for:` is essentially the **grand total** of the cache space that `apt-cache stats` has accounted for across all those categories.

Finally the hash-table sections:

```

PkgHashTable
GrpHashTable

```

are APT's internal hash tables used for fast package/group lookups.

For example:

```

Total buckets: 196613
Unused: 91212
Used: 105401
Utilization: 53.6%
Average entries: 1.51
Longest: 20
Shortest: 1

```

means APT allocated `196,613` hash buckets, about `53.6%` contain entries, and occupied buckets contain about `1.51` entries on average.

Longest: `20` means the longest collision chain/bucket contains 20 entries.

We also have:

```bash

apt-cache unmet

```

This walks through APT's current package cache and reports dependency relationships that cannot currently be satisfied by the providers known to APT.

For example, if a package version declares a dependency such as:

```

Depends: foo (>= 2.0)

```

and APT cannot find a suitable version or provider satisfying that relationship, `apt-cache unmet` can report the package and the unmet dependency.

We also have the `-i` flag (or `--important`), which restricts the output to `Pre-Depends` and `Depends` relationships only.

For example:

```bash

apt-cache unmet | wc -l

```

may return:

```

16670

```

While:

```bash

apt-cache unmet --important | wc -l

```

May return:

```

4601

```

Now, let's discuss:

```bash

apt-cache dump

```


And:

```bash

apt-cache dumpavail

```

Both commands read from APT's current package cache, which is built from the local metadata downloaded from the configured repositories.

Their difference is mainly in how that information is presented.

`apt-cache dump` prints a short, debugging-oriented representation of every package in the cache. In particular, it makes relationships between package versions, dependency records, descriptions, and the index files from which they originated explicit.

For example:

```bash

apt-cache dump | head

```

Output:

```

Using Versioning System: Standard .deb
Package: gobjc++-11-multilib-mipsel-linux-gnu
 Version: 11.5.0-1ubuntu1~24.04cross1
     File: /var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble-updates_universe_binary-amd64_Packages
  Depends: gcc-11-mipsel-linux-gnu-base 11.5.0-1ubuntu1~24.04cross1
  Depends: gobjc++-11-mipsel-linux-gnu 11.5.0-1ubuntu1~24.04cross1
  Depends: g++-11-multilib-mipsel-linux-gnu 11.5.0-1ubuntu1~24.04cross1
  Depends: gobjc-11-multilib-mipsel-linux-gnu 11.5.0-1ubuntu1~24.04cross1
 Description Language:
                 File: /var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_universe_binary-amd64_Packages

```

While:

```bash

apt-cache dumpavail | head

```

Output:

```

Package: brave-browser
Priority: optional
Section: web
Installed-Size: 473603
Maintainer: Brave Software <support@brave.com>
Architecture: amd64
Version: 1.95.104
Provides: www-browser
Depends: brave-keyring, ca-certificates, fonts-liberation, libasound2 (>= 1.0.17), libatk-bridge2.0-0 (>= 2.5.3), libatk1.0-0 (>= 2.11.90), libatspi2.0-0 (>= 2.9.90), libc6 (>= 2.25), libcairo2 (>= 1.14.0), libcups2 (>= 1.7.0), libcurl3-gnutls | libcurl3-nss | libcurl4 | libcurl3, libdbus-1-3 (>= 1.9.14), libexpat1 (>= 2.1~beta3), libgbm1 (>= 17.1.0~rc2), libglib2.0-0 (>= 2.39.4), libgtk-3-0 (>= 3.9.10) | libgtk-4-1, libnspr4 (>= 2:4.9-2~), libnss3 (>= 2:3.35), libpango-1.0-0 (>= 1.14.0), libudev1 (>= 183), libvulkan1, libx11-6 (>= 2:1.4.99.1), libxcb1 (>= 1.9.2), libxcomposite1 (>= 1:0.4.4-1), libxdamage1 (>= 1:1.1), libxext6, libxfixes3, libxkbcommon0 (>= 0.5.0), libxrandr2, wget, xdg-utils (>= 1.0.2)
Pre-Depends: dpkg (>= 1.14.0)

```

Also, this is the time to introduce you to:

```

/var/lib/apt/pkgcache.bin
/var/lib/apt/srcpkgcache.bin

```

They are the binaries that efficiently store the packages's metadata and package's relations.

The key distinction is:

```

srcpkgcache.bin
-> parsed repository-side package metadata
-> built from the package/release files referenced by your APT sources
-> does NOT include /var/lib/dpkg/status

pkgcache.bin
-> fuller package cache used by normal APT operations
-> includes the repository information
-> plus local installed-package state from /var/lib/dpkg/status

```

The separation exists mainly for performance and reuse.

Indeed, APT has two kinds of information that change at very different rates:

```

repository metadata
-> changes when we run apt update

```

And:

```

installed-system state
-> changes whenever dpkg/apt installs, removes, configures, etc.

```

APT therefore keeps a parsed cache of the relatively stable repository side:

```

srcpkgcache.bin

```

and can then combine that with:

```

/var/lib/dpkg/status

```

to build:

```

pkgcache.bin

```

And where do they get the data ?

From the indexes files.

And that's here that I introduce you to:

```bash

apt-cache gencaches

```

That explicitely generates those binaries from the indexes files.

Those files are used by many APT operations to optimize queries.

We can think the build process as:

```

/var/lib/apt/lists/*Packages
/var/lib/apt/lists/*Release / InRelease
        |
        V
srcpkgcache.bin
        |
        | + /var/lib/dpkg/status
        V
pkgcache.bin

```

And yes `/var/lib/dpkg/status` contains standard metadata block about installed packages only.

Normally we don’t need to run this because commands that require the cache create/regenerate it automatically when needed.

Now, to get the informations about the source files that were used to build the input package (and potentially others), we use:

```bash

apt-cache showsrc pkg

```

Or:

```bash

apt showsrc pkg

```

That will work only if we have set up a `deb-src` provider suite in the `/etc/apt/sources.list` file on in one file under `/etc/apt/sources.list.d/`.

For example:

```

deb-src http://archive.ubuntu.com/ubuntu noble main restricted universe multiverse

```

Then we run:

```bash

apt update

```

to download the `/var/lib/apt/lists/*source_Sources*` indexes files.

On my system, I can show them:

```bash

ls /var/lib/apt/lists/*source_Sources*

```

Which outputs:

```

/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_main_source_Sources
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_multiverse_source_Sources
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_restricted_source_Sources
/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_noble_universe_source_Sources

```

Now, the `apt-cache pkg` command should work, for example:

```bash

apt-cache showsrc ssh

```

Which outputs:

```bash

Package: openssh
Format: 3.0 (quilt)
Binary: openssh-client, openssh-server, openssh-sftp-server, openssh-tests, ssh, ssh-askpass-gnome, openssh-client-udeb, openssh-server-udeb
Architecture: any all
Version: 1:9.6p1-3ubuntu13
Priority: standard
Section: net
Maintainer: Ubuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>
Original-Maintainer: Debian OpenSSH Maintainers <debian-ssh@lists.debian.org>
Uploaders: Colin Watson <cjwatson@debian.org>, Matthew Vernon <matthew@debian.org>,
Standards-Version: 4.6.2
Build-Depends: debhelper (>= 13.1~), debhelper-compat (= 13), dh-exec, dh-runit (>= 2.8.8), dh-sequence-movetousr, libaudit-dev [linux-any], libedit-dev, libfido2-dev (>= 1.5.0) [linux-any], libgtk-3-dev <!pkg.openssh.nognome>, libkrb5-dev | heimdal-dev, libpam0g-dev | libpam-dev, libselinux1-dev [linux-any], libssl-dev (>= 1.1.1), libwrap0-dev | libwrap-dev, pkg-config, zlib1g-dev, systemd-dev
Testsuite: autopkgtest
Testsuite-Triggers: devscripts, dropbear, haveged, krb5-admin-server, krb5-kdc, openssl, putty-tools, python3-twisted, sudo, systemd, sysvinit-utils
Homepage: https://www.openssh.com/
Vcs-Browser: https://salsa.debian.org/ssh-team/openssh
Vcs-Git: https://salsa.debian.org/ssh-team/openssh.git
Directory: pool/main/o/openssh
Package-List:
 openssh-client deb net standard arch=any
 openssh-client-udeb udeb debian-installer optional arch=any profile=!noudeb
 openssh-server deb net optional arch=any
 openssh-server-udeb udeb debian-installer optional arch=any profile=!noudeb
 openssh-sftp-server deb net optional arch=any
 openssh-tests deb net optional arch=any
 ssh deb net optional arch=all
 ssh-askpass-gnome deb gnome optional arch=any profile=!pkg.openssh.nognome
Files:
 af048ba3e30ff18118768df92040e3d7 3334 openssh_9.6p1-3ubuntu13.dsc
 5e90def5af3ffb27e149ca6fff12bef3 1857862 openssh_9.6p1.orig.tar.gz
 a9aaf09b36b23327431072ed804d7094 833 openssh_9.6p1.orig.tar.gz.asc
 8655501e95e2b68e023be73776694686 203240 openssh_9.6p1-3ubuntu13.debian.tar.xz
Checksums-Sha1:
 391755e1b3f8d95ec763513f7732b29fba5c4ead 3334 openssh_9.6p1-3ubuntu13.dsc
 de300d09ec79fdbf37de4e6672cce4161439f2c3 1857862 openssh_9.6p1.orig.tar.gz
 63c241035c665da9284965575cd96e0467bf09c1 833 openssh_9.6p1.orig.tar.gz.asc
 a1e8d5723b838b729532f5702f7f5a578a04a746 203240 openssh_9.6p1-3ubuntu13.debian.tar.xz
Checksums-Sha256:
 046369010a2c8bd26252292dd487285c93ad0bf75b712c1e95ce9695eed17d85 3334 openssh_9.6p1-3ubuntu13.dsc
 910211c07255a8c5ad654391b40ee59800710dd8119dd5362de09385aa7a777c 1857862 openssh_9.6p1.orig.tar.gz
 9b1e931cbc811f02e91f7eacd55f8211cc45dade11975462f4b0dcdad29927aa 833 openssh_9.6p1.orig.tar.gz.asc
 2e7736d76ac31b98e2be99b833b7280f65e4a6af3cbeef25e9e836dd93792385 203240 openssh_9.6p1-3ubuntu13.debian.tar.xz
Checksums-Sha512:
 0a91899087eafeca575d76d90b8b3ad6c05434886b5956398f9d8bb4d0e4a9cddd288572fe2ce2bdbde759dfd8ba41fb92095228ebf0c03a533189125116015a 3334 openssh_9.6p1-3ubuntu13.dsc
 0ebf81e39914c3a90d7777a001ec7376a94b37e6024baf3e972c58f0982b7ddef942315f5e01d56c00ff95603b4a20ee561ab918ecc55511df007ac138160509 1857862 openssh_9.6p1.orig.tar.gz
 aec5a5bd6ce480a8e5b5879dc55f8186aec90fe61f085aa92ad7d07f324574aa781be09c83b7443a32848d091fd44fb12c1842d49cee77afc351e550ffcc096d 833 openssh_9.6p1.orig.tar.gz.asc
 1b25983f4bee107363cc201f9289efd57b4bf1f28be78cb985647c9187bba37cf638f2d008a60976e89457d9865f70d97315a7be2cb0ca32b4f66c651d0755c4 203240 openssh_9.6p1-3ubuntu13.debian.tar.xz

```

Indeed, it made the relations by looking in the `Binary` field where we see that `ssh` appears.

Now, we also have the equivalent to:

```bash

pactree -g pkg 

```

with

```bash

apt-cache dotty pkg

```

That will output a DOT structured output for the `dot` utility to convert it to an SVG, PNG, JPEG, JPG, PDF etcetera...

So, we can do the following:

```bash

apt-cache dotty brave-browser > brave.dot

```

And then:

```bash

dot -Tpdf brave.dot -o brave-graph.pdf

```

But often, when the depedencies graph is huge, this will fail (core dumped).

Indeed, for example look at the number of depedencies of `brave-browser`:

```bash

apt-cache dotty brave-browser | wc -l

```

Returns:

```

8677

```

In order to reduce this graph-size problem, we can temporarily override one of APT's configuration options.

APT exposes many configuration keys that its commands read at runtime to determine their behavior. They generally follow a hierarchical naming scheme such as:

```

APT::Cache::Field

```

and can be overridden for a single command with:

```

-o Key=Value

```

For `apt-cache dotty`, one useful option is:

```

APT::Cache::GivenOnly=true|false

```

By default, `dotty` recursively follows dependency relationships starting from the packages given on the command line.

When:

```

APT::Cache::GivenOnly=true

```

APT restricts the graph to the packages explicitly supplied as arguments instead of recursively expanding the dependency tree.

We can therefore use:

```bash

apt-cache -o APT::Cache::GivenOnly=true dotty brave-browser | wc -l

```

which may return a much smaller result, for example:

```

77

```

We can then generate a much smaller DOT file:

```bash

apt-cache -o APT::Cache::GivenOnly=true dotty brave-browser > brave.dot

```

This temporary override applies only to that invocation of `apt-cache`; it does not permanently modify APT's configuration files.














