Let me clarify something immediately.


First the repo is here lol: [https://github.com/julienlargetpiet/Statix](https://github.com/julienlargetpiet/Statix), and second

This is not a “framework”.
This is not a “platform”.
This is not “the future of publishing”.


It’s just called **blog**.


And it does one thing extremely well:
it lets me create, edit, update, and delete articles directly in the browser
without negotiating with a build pipeline, a folder structure, or a philosophical manifesto.


## The Problem With Static Generators (Yes, All of Them)

Static site generators are brilliant.
Until you actually want to change something.


Want to fix a typo?
Open your editor → find the file → edit Markdown → rebuild → deploy → commit → push.


Want to delete an article?
Remove the file → rebuild → redeploy → invalidate cache → hope you didn’t break a list page.


Want to add a table?
Remember the generator’s preferred flavor of Markdown.


Want to change structure?
Now you’re reasoning about layouts, archetypes, content trees, taxonomies,
and whatever mental model the generator designer decided you should adopt.


No.


I refuse.


## The Design Principle: Zero Cognitive Overhead

My blog has:


- A Go admin backend
- A relational database
- A static `dist/` output
- A browser UI

That’s it.


You open `/admin`.
You log in.
You write.
You click save.
It’s live.


No rebuild step.
No git push.
No external dependency.
No “mental compilation”.


## Architecture: NGINX Does the Heavy Lifting

The public site is served **only by NGINX**.


Readers never touch the Go server.
They never hit the database.
They never trigger runtime rendering.


They request static files.
NGINX serves static files.
End of story.


The Go backend exists almost exclusively for me:


- Writing articles
- Editing content
- Uploading files
- Deleting posts
- Administrative tasks

Most of the time, the Go process is idle.
It is not a high-traffic web server.
It is a content management tool that wakes up when I need it.


That separation keeps the architecture:


- Predictable
- Fast
- Operationally simple
- Easy to reason about

## Ease of Updating: Literally Replace the Binary

```bash

CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -ldflags="-s -w" -o go_blog_admin

sudo systemctl stop go_blog
sudo mv go_blog_admin /var/www/go_blog/go_blog_admin
sudo chown goblog:goblog /var/www/go_blog/go_blog_admin
sudo chmod 0755 /var/www/go_blog/go_blog_admin
sudo systemctl start go_blog

```

Replace binary.
Restart service.
Done.


No dependency trees exploding.
No plugin incompatibilities.
No fragile theme ecosystem.


## Adding and Deleting Articles: The Barrier Is Zero

Adding an article:


- Open browser
- Write
- Click save

Deleting an article:


- Select
- Click delete
- Gone

No filesystem archaeology.
No rebuild step.
No manual cache invalidation.


The UI handles it.
The database updates.
The static output regenerates.
NGINX serves.


That’s the whole pipeline.


## Database Dump Button (Because Backups Should Not Be Ceremonial)

There is a button in the admin panel to dump the entire database.


Not a wiki page explaining how to SSH.
Not a 12-step backup ritual.
A button.


Click.
Export.
Done.


The philosophy is simple:


- Backups should be trivial.
- Backups should not require remembering commands.
- Backups should not depend on external dashboards.

If you can write an article in two clicks,
you should be able to back up the entire site in one.


Infrastructure seriousness does not require UX punishment.


## Built-In Log Analyzer (Because Static Blogs Attract Robots)

The blog also comes with its own NGINX log analyzer.


Not a SaaS tracker.
Not embedded surveillance JavaScript.
Just raw logs and deterministic filtering.


It applies bot detection tailored specifically for static blogs:


- User-Agent inspection
- Request rate anomalies
- HTML-to-asset ratio heuristics
- Reading-time plausibility
- Explicit prefetch tagging

The result is actual human traffic metrics,
not a celebration of how many SEO crawlers discovered your RSS feed.


## No Forced Mental Model

An article is:


- A title
- HTML content
- A timestamp

That’s it.


If I need more structure,
I add a column.


It’s a database.
Not a belief system.


## Barrier to Entry: Zero

The most important feature is not performance.
It’s not architecture.
It’s not purity.


It’s the absence of friction.


I open a browser and write.


No build step.
No cognitive overhead.
No ritual.


And for a blog,
that’s everything.


It’s not trying to be universal.
It’s not trying to be extensible.
It’s not trying to be trendy.


It’s just my blog.
And it finally removed every excuse not to write.