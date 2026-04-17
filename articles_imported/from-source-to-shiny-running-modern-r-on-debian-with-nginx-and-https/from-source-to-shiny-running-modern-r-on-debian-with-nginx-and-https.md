## 1\. Introduction

I recently deployed an R Shiny app on my Debian server, but hit a wall early:
Debian 11 ships **R 4.0.4**, while most CRAN packages (like `devtools` or `ragg`) now require **R ≥ 4.1**.

Rather than upgrade the entire OS, I decided to:

- Compile **R 4.4.1** from source
- Use a **custom user library folder** ( `~/.local/share/R/library`)
- Run a Shiny app on port **8081**
- Serve it securely via **NGINX + HTTPS**, alongside my Flask site

This post walks through every step of that setup.

## 2\. Installing R 4.4.1 from Source on Debian

Debian stable is famously conservative, so its repositories only have R 4.0.x.
To get the latest R, I built it myself from the official CRAN tarball.

```bash

sudo apt update
sudo apt install -y build-essential gfortran libreadline-dev libx11-dev libxt-dev \
  libpng-dev libjpeg-dev libcairo2-dev libssl-dev libbz2-dev liblzma-dev \
  libzstd-dev libcurl4-openssl-dev libpcre2-dev zlib1g-dev

wget https://cran.r-project.org/src/base/R-4/R-4.4.1.tar.gz
tar -xf R-4.4.1.tar.gz
cd R-4.4.1
./configure --enable-R-shlib --prefix=/usr/local
make -j$(nproc)
sudo make install

```

You can safely ignore:

```
*** Cannot find any Java interpreter
Error 1 (ignored)

```

That just means Java support was skipped (it’s optional).

## 3\. Making `/usr/local/bin/R` the Default

Debian already had `/usr/bin/R` (version 4.0.4), so the system still ran the old one.
I fixed this by prioritizing `/usr/local/bin`:

```bash

echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

```

Now `R --version` shows:

```
R version 4.4.1 (2025-05-10)

```

## 4\. Using a Custom Library Folder

Instead of installing packages into system paths, I created my own library folder:
`~/.local/share/R/library`

This keeps my packages:

- Independent of system R updates
- Writable without sudo
- Portable across R upgrades

My `~/.Rprofile`:

```r

dir.create("~/.local/share/R/library", recursive = TRUE, showWarnings = FALSE)
.libPaths("~/.local/share/R/library")
options(repos = c(CRAN = "https://cloud.r-project.org"))

```

Now every package I install goes to:

```
~/.local/share/R/library/<package_name>

```

and `.libPaths()` confirms:

```
[1] "/home/julien/.local/share/R/library"

```

### 🧠 Tip: Verify a package’s installation path

To confirm whether a package was correctly installed to your custom library, you can use the built-in function `find.package()`:

```r


find.package("ggplot2")

```

Example output:

```
[1] "/home/julien/.local/share/R/library/ggplot2"

```

## 5\. Installing devtools (and Fixing Compilation Errors)

After upgrading R, installing `devtools` failed due to missing system headers.
I installed all required development libraries:

```bash

  sudo apt install -y \
  libxml2-dev libcurl4-openssl-dev libssl-dev \
  libfreetype6-dev libpng-dev libtiff5-dev libjpeg-dev libwebp-dev \
  libharfbuzz-dev libfribidi-dev pkg-config

```

Then retried:

```r

install.packages("devtools", dependencies = TRUE)

```

## 6\. Note for Users on Other Linux Distributions

If you’re building R or compiling CRAN packages on **Fedora**, **Arch**, or newer **Ubuntu** releases,
your compiler (GCC 12+, Clang 17+) might use **stricter C++ flags by default**.
Some packages treat warnings as fatal errors ( `-Werror`) or fail due to “format-security” enforcement.

You can relax these compiler flags by editing (or creating) the **Makevars** file in your R configuration directory:

```
~/.R/Makevars

```

Here’s what I use personally on Arch (works great across distros):

```

# Fix GCC 14+ "format-security" and -Werror issues on Arch
CXXFLAGS    += -O2 -Wno-error=format-security -Wno-error -Wno-deprecated-declarations
CXX11FLAGS  += -O2 -Wno-error=format-security -Wno-error -Wno-deprecated-declarations
CXX14FLAGS  += -O2 -Wno-error=format-security -Wno-error -Wno-deprecated-declarations
CXX17FLAGS  += -O2 -Wno-error=format-security -Wno-error -Wno-deprecated-declarations
CFLAGS      += -O2 -Wno-error=format-security -Wno-error

```

## 7\. Running a Shiny App

With R ready, I started my Shiny app on port 8081:

```r

library(shiny)
runApp("myapp", host = "0.0.0.0", port = 8081)

```

## 8\. Reverse Proxy via NGINX + HTTPS

I already had NGINX serving my Flask site ( `julienlargetpiet.tech`).
I added a block to proxy `/shiny/` to my Shiny backend:

```nginx

  location /shiny/ {
    proxy_pass http://127.0.0.1:8081/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 20d;
    proxy_buffering off;
    proxy_redirect off;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

```

Reloaded NGINX:

```bash

sudo nginx -t && sudo systemctl reload nginx

```

## 9\. (Optional) Start Shiny Automatically at Boot

I added a simple `systemd` service to make the Shiny app start automatically:

```systemd

[Unit]
Description=R Shiny App
After=network.target

[Service]
ExecStart=/usr/local/bin/R -e "shiny::runApp('/home/julien/myapp', host='127.0.0.1', port=8081)"
Restart=always
User=www-data
WorkingDirectory=/home/julien/myapp

[Install]
WantedBy=multi-user.target

```

Enable it:

```bash

sudo systemctl enable --now shinyapp.service

```

## 10\. Conclusion

This setup gave me a **clean, isolated R environment**:

- R 4.4.1 built from source in `/usr/local`
- All packages stored in `~/.local/share/R/library`
- Verified package paths via `find.package("pkgname")`
- Relaxed compiler flags in `~/.R/Makevars` for modern GCC/Clang
- Shiny app proxied via NGINX with HTTPS on port 8081
- Flask and Shiny coexisting under one domain

It’s lightweight, reproducible, and robust — a setup any R developer can trust on Debian or any modern Linux distribution.