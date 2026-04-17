If you run Nginx in production, your access and error logs can grow fast. On most Linux systems, log rotation is handled
by **logrotate**. It periodically renames log files (e.g. `access.log` → `access.log.1`),
optionally compresses old ones, and (critically) tells Nginx to reopen its log file descriptors so it starts writing to the new files.


This article explains the most common directives you’ll see in `/etc/logrotate.d/nginx` (or similar),
why they exist, and how to safely switch from time-based rotation (daily/weekly) to **size-based rotation**.


## Where log rotation comes from

On Debian/Ubuntu systems, rotation typically runs via a `systemd` timer (or historically via cron).
The timer triggers `logrotate`, which reads configuration files under `/etc/logrotate.conf`
and `/etc/logrotate.d/*`.


## A typical Nginx logrotate config (daily rotation)

```conf


/var/log/nginx/*.log {
  daily
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

This rotates Nginx logs **daily**, keeps 14 rotations, compresses older logs, and runs a post-rotation command to make Nginx reopen logs.


## Switching to size-based rotation

If your traffic is bursty, a time-based schedule can produce either:


- Logs that are too big before rotation happens (disk pressure), or
- Lots of tiny rotated files when traffic is low.

A size-based rule rotates when the log reaches a threshold (e.g. 500MB).


```conf


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

With `size 500M`, rotation happens whenever the file crosses ~500MB (but only when logrotate is executed —
for example, daily by the system timer). In other words: the threshold is checked on each run.


## What each directive means

### missingok

**Meaning:** If a file doesn’t exist, don’t error — just skip it.


**Why it matters:** Some log files may be disabled, removed, or not created yet. Without `missingok`,
logrotate would complain (and depending on your environment, that could trigger alerts).


### notifempty

**Meaning:** Do not rotate the log file if it is empty (0 bytes).


**Why it matters:** Avoids producing lots of useless empty rotated files.


### sharedscripts

**Meaning:** Run `prerotate`/ `postrotate` scripts only **once**,
even if the pattern matches multiple files.


**Why it matters for Nginx:** Your log pattern is `/var/log/nginx/*.log`, which can match many files
(access, error, vhost logs). Without `sharedscripts`, `postrotate` could run once per file and trigger multiple Nginx reloads.
That’s noisy and unnecessary. With `sharedscripts`, Nginx is told to reopen logs a single time after all rotations are done.


### prerotate ... endscript

**Meaning:** Commands executed **before** log rotation starts.


In many distributions, this particular snippet is a compatibility hook used mainly for Apache-related setups. It checks for a directory:


```bash


if [ -d /etc/logrotate.d/httpd-prerotate ]; then
  run-parts /etc/logrotate.d/httpd-prerotate
fi


```

If that directory exists, it runs any scripts inside. For pure Nginx systems, it typically does nothing.
Leaving it in place is usually harmless.


### postrotate ... endscript

**Meaning:** Commands executed **after** log rotation completes.


This is the most important block for Nginx: it ensures Nginx stops writing to the old renamed file and starts writing to the new one.


```bash


invoke-rc.d nginx rotate >/dev/null 2>&1


```

Without a post-rotate reopen/reload action, the rotation may appear to happen (files renamed),
but Nginx can keep writing to the old file descriptor (now pointing to `access.log.1`), which defeats the point.


## Common gotchas (especially when doing analytics)

### Size-based rotation is checked only when logrotate runs

If logrotate runs once per day, the “size 500M” condition is evaluated once per day. If your logs jump from 100MB to 2GB in a few hours,
logrotate won’t rotate until its next run.


If you want tighter control, you can increase logrotate frequency (for example, run it hourly) while still using size-based rules.


### Your analytics might miss data if you only read access.log

If your processing pipeline only reads `/var/log/nginx/access.log`, rotation will move older content into
`access.log.1` (then `.2.gz`, etc.). To avoid missing requests, your parser should be able to read from
`access.log*` or track rotation state.


## Testing your config safely

You can test the logrotate configuration without actually rotating:


```bash


sudo logrotate -d /etc/logrotate.d/nginx


```

To force a rotation (use carefully):


```bash


sudo logrotate -f /etc/logrotate.d/nginx


```

## Summary

- `missingok`: skip missing log files without error.
- `notifempty`: don’t rotate empty files.
- `sharedscripts`: run scripts once for the whole block, not per file.
- `prerotate`: commands that run before rotation (often a distro hook).
- `postrotate`: commands that run after rotation (critical for Nginx to reopen logs).
- `size 500M`: rotate based on size threshold (evaluated whenever logrotate runs).

With these pieces understood, you can tune rotation to match your traffic, protect your disk, and keep your analytics consistent.