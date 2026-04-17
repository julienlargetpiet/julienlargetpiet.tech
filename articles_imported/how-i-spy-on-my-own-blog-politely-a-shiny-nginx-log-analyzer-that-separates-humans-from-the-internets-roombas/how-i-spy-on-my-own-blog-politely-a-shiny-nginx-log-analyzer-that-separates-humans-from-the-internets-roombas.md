I run a blog. People read it. Bots also “read” it — in the same way a vacuum cleaner “enjoys” a carpet.
So I built a small R Shiny app that ingests my Nginx access logs, extracts the interesting bits,
and applies a few pragmatic heuristics to answer the only question that matters:
**was this a human, or was this a script having a very busy day?**

## Note

By the way my blog and R shiny log analyzer is open-source at [https://github.com/julienlargetpiet/blog](https://github.com/julienlargetpiet/blog)

## The problem

On a static blog, you don’t get “analytics events”. You get requests. A lot of requests.
And if you do anything even mildly modern (like prefetching links), your own browser becomes
suspiciously productive.


Meanwhile, bots show up with a smile, download everything, and then leave without even pretending to scroll.
The goal isn’t to build a perfect classifier — it’s to get a dashboard that’s not 93% powered by
_AhrefsBot_ and friends.


## The logging substrate: Nginx, with one extra tell

The whole thing starts with a log format that is intentionally boring, except for one detail:
I add `$http_x_prefetch` at the end.


```nginx


log_format main '$remote_addr - $remote_user [$time_local] '
                '"$request" $status $body_bytes_sent '
                '"$http_referer" "$http_user_agent" '
                '"$http_x_prefetch"';

access_log /var/log/nginx/access.log main;
error_log /var/log/nginx/error.log warn;


```

Why the extra header? Because I have an aggressively helpful JS prefetcher that fetches URLs
shown inside a page. That’s nice for UX. It’s also a great way to contaminate your traffic metrics
with requests that look like real navigation, but aren’t.


So the design decision is simple:
**if I cause the request, I tag the request.**
Then my log analyzer can remove it deterministically, before it starts hallucinating bot behavior.


## Shiny-side design: treat logs like a dataset, not like a tragedy

The app is built around two reactive layers:


- **`raw_data()`**: read and parse the access log into a clean tibble
- **`filtered_data()`**: apply human/bot filters + scope to article traffic + time window

This separation matters. Parsing is a “pure-ish” transformation of bytes to columns.
Filtering is policy, and policy changes when you’re annoyed by a new crawler.


## Parsing the Nginx log: delimiter pragmatism

Nginx “combined-ish” logs are not CSV. They’re a space-delimited fever dream with quoted segments.
Here I use `read_delim(delim = " ", quote = '"')` because it’s simple and fast enough,
and because I only need a handful of fields anyway.


```r


file_path <- "/var/log/nginx/access.log"

raw_data <- reactive({
  fp <- file_path
  req(!is.null(fp))

  df <- read_delim(
    fp,
    delim = " ",
    quote = '"',
    col_names = FALSE,
    trim_ws = TRUE,
    progress = FALSE,
    col_types = cols(
      .default = col_character(),
      X7 = col_double(),
      X8 = col_double()
    )
  )

  # Safety: ensure we have enough columns
  req(ncol(df) >= 2)

  parsed <- tibble(
    ip = df[[1]],
    date_raw = paste(df[[4]], df[[5]]),
    request_raw = df[[6]],
    ua = df[[ncol(df) - 1]],        # second to last
    x_prefetch = df[[ncol(df)]]     # last column
  )

  parsed <- parsed %>%
    mutate(
      date = as.POSIXct(
        gsub("\\\\[|\\\\]", "", date_raw),
        format = "%d/%b/%Y:%H:%M:%S %z",
        tz = "UTC"
      ),
      target = extract_url(request_raw),
      is_prefetch = x_prefetch == "1"
    ) %>%
    select(ip, date, target, ua, is_prefetch)

  parsed %>%
    filter(!is.na(date), !is.na(target))
})


```

There are three intentional “I don’t trust logs” moves here:


- **Column safety checks** ( `req(ncol(df) >= 2)`): because production logs will eventually contain something weird.
- **Minimal projection**: I only keep `ip`, `date`, `target`, `ua`, and `is_prefetch`.
- **Early NA filtering**: broken timestamps and unparseable requests are not “mysterious users”, they’re just garbage.

## The prefetch problem: browsers that do things without telling you

Prefetch makes the site feel instant, and it’s genuinely useful. But it also creates requests
that are not user intent. If you don’t separate them, you end up “measuring” phantom pageviews.


That’s why filtering begins with:
**remove prefetch first.**
It’s not a heuristic. It’s an explicit signal. I literally stamped the request myself.


## Bot detection: a layered approach (because bots are creative)

The detection is intentionally multi-layered. No single rule is “the truth”.
Instead, I combine several cheap signals that, together, give me a high-signal filter.


### 1) UA regex: the classic “hello I am a bot” confession

Many bots self-identify. Some do it out of politeness. Some do it out of legal compliance.
Some do it because they are proud of their work. Either way: thanks.


### 2) Asset heuristic: suspiciously “HTML-only” behavior

Real browsers request a mix: HTML, CSS, JS, images, fonts. A lot of scrapers just pull HTML endpoints
(or they behave in oddly uniform patterns). The heuristic computes an “HTML ratio” per IP and flags
extreme cases.


### 3) Rate heuristic: requests-per-second spikes

Humans don’t click 40 times per second. If they do, they’re either:
(a) a bot, or (b) testing my site with a metronome. Either way, I filter them.


### 4) Reading-time heuristic: speedrunning long-form

This one is intentionally aggressive: if an IP hits an article URL and “moves on” in under 30 seconds,
I assume it’s automation.
Yes, this will occasionally punish the world’s fastest skimmer. I can live with that.


```r


filtered_data <- reactive({
  df <- raw_data()
  req(nrow(df) > 0)

  # -----------------------------
  # BOT DETECTION
  # -----------------------------
  if (!isTRUE(input$show_bots)) {

    bot_regex <- paste(
      c(
        "bot","crawler","spider",
        "ahrefs","semrush","mj12","dotbot",
        "googlebot","bingbot","yandex","baiduspider",
        "headless","phantomjs","selenium",
        "playwright","puppeteer",
        "node-fetch","axios",
        "go-http-client","libwww-perl","java/",
        "curl","wget","python-requests",
        "httpclient","scrapy"
      ),
      collapse = "|"
    )

    # 1️⃣ Remove prefetch first
    df <- df %>%
      filter(!is_prefetch)

    # 2️⃣ UA detection
    df <- df %>%
      mutate(is_bot_ua = grepl(bot_regex, ua,
                               ignore.case = TRUE,
                               perl = TRUE))

    # 3️⃣ Asset heuristic
    df <- df %>%
      group_by(ip) %>%
      mutate(
        total_requests = n(),
        html_requests = sum(grepl("\\\\.html$|/$", target)),
        asset_ratio = html_requests / total_requests,
        is_bot_asset = asset_ratio > 0.9
      ) %>%
      ungroup()

    # 4️⃣ Rate heuristic
    df <- df %>%
      group_by(ip, sec = floor_date(date, "second")) %>%
      mutate(req_per_sec = n()) %>%
      ungroup() %>%
      mutate(is_bot_rate = req_per_sec > 10)

    # 5️⃣ Reading-time heuristic (aggressive)
    df <- df %>%
      arrange(ip, date) %>%
      group_by(ip) %>%
      mutate(
        next_date = lead(date),
        time_on_page = as.numeric(difftime(next_date, date, units = "secs")),
        is_article = grepl("^/articles/.*\\\\.html$", target),
        is_bot_readtime = is_article &
                          !is.na(time_on_page) &
                          time_on_page < 30
      ) %>%
      ungroup()

    # 6 Final bot flag
    df <- df %>%
      mutate(is_bot = is_bot_ua | is_bot_rate | is_bot_asset | is_bot_readtime) %>%
      filter(!is_bot) %>%
      select(-is_bot_ua, -req_per_sec, -is_bot_rate,
             -is_bot_asset, -asset_ratio,
             -total_requests, -html_requests,
             -next_date,
             -is_article, -is_bot_readtime,
             -is_bot)
  }

  # -----------------------------
  # STATIC ASSET FILTER
  # -----------------------------
  if (!isTRUE(input$show_static)) {
    df <- df %>%
      filter(!grepl(
        "\\\\.(css|js|png|jpg|jpeg|gif|svg|ico|woff2?|ttf)(\\\\?|$)",
        target,
        ignore.case = TRUE
      ))
  }

  df <- df %>%
    mutate(target = sub("\\\\?.*$", "", target),
           target = trimws(target)) %>%
    filter(
      target == "/articles/" |
      grepl("^/articles/.*\\\\.html$", target)
    )

  # -----------------------------
  # TIME WINDOW FILTER
  # -----------------------------
  last <- input$last_n * mult_map[[input$time_unit]]

  if (nrow(df) == 0) return(df)
  cutoff <- max(df$date) - last

  df %>% filter(date >= cutoff)
})


```

The ordering is not accidental:


1. **Prefetch removal first** to avoid poisoning every other heuristic.
2. **Then easy flags** (UA, rate).
3. **Then behavior** (asset ratio, reading time), which is noisier but catches stealthier automation.

## Scope reduction: I only care about article traffic

I don’t want “requests to everything”. I want “reads of things I wrote”.
So after bot/static filtering, I aggressively narrow to:


- `/articles/` (the index)
- `/articles/*.html` (actual posts)

This is a deliberate design choice: fewer endpoints, fewer weird edge cases,
and the metrics match the story I’m trying to tell.


## Time windows: because nobody wants to render a million log lines in a reactive app

Shiny is reactive, not psychic. I apply a simple rolling cutoff computed from the latest timestamp
in the filtered dataset. That gives me “last N minutes/hours/days” style slicing.


This also keeps the app snappy without prematurely over-engineering storage, indexing,
or a full log pipeline. If I ever want that, I’ll ship logs to a database.
For now, a file on disk is perfectly adequate, and delightfully untrendy.


## Why this design works (and what it refuses to be)

This system is intentionally not a “bot detection product”. It’s a personal observability tool.
The rules are transparent, cheap to run, and easy to adjust when the internet invents a new crawler
with a slightly more polite user-agent string.


### What I like about it

- **Deterministic prefetch filtering** (because I tag my own prefetch requests).
- **Layered heuristics** instead of one brittle rule.
- **Focused scope**: articles only, not the entire asset universe.
- **Operational simplicity**: read one file, compute, display.

### Another note

I keep my log file at maximum 500M with `logrotate`

Log rotate is somethig that will rotate (never thought about it) the logs, it means compress and archive current logfile before `echo "" > ` on that thing.

This is based on certain rules and i keep 14 log archives.

here is my file at `/etc/logrotate.d/nginx`:

```languge-conf
    Copy

      /var/log/nginx/*.log {
        size 500M
        missingok
        rotate 14
        compress
        delaycompress
        notifempty
        create 0640 www-data adm
        sharedscripts
        prerotate
                if [ -d /etc/logrotate.d/httpd-prerotate ]; then \
                        run-parts /etc/logrotate.d/httpd-prerotate; \
                fi \
        endscript
        postrotate
                invoke-rc.d nginx rotate >/dev/null 2>&1
        endscript
      }


```

### What I accept as tradeoffs

- Some humans will be flagged (especially speed-readers).
- Some bots will slip through (especially well-behaved ones).
- NAT/shared IPs can blur “per-IP” behavior.

And that’s fine. The goal is not courtroom-grade attribution.
The goal is to stop bots from starring in my own traffic charts like they pay rent.


Repo: [julienlargetpiet/blog](https://github.com/julienlargetpiet/blog/)

If you’re reading this as a bot: please at least set a nice user-agent. We can have standards.