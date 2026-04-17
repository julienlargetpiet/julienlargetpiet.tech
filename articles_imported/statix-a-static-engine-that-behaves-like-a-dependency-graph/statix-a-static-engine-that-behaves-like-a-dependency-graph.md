Most static site generators rebuild everything.

Statix doesn’t.

It rebuilds **exactly what changed — nothing more, nothing less**.

This article is a deep dive into how Statix actually works internally:

- Symlink-based runtime theming (no rebuilds)
- Localized builds driven by implicit dependency graphs
- The admin pipeline that orchestrates rebuilds
- The CLI and system integration philosophy

---

# 1\. Symlinks as Runtime State (Themes & Fonts)

Statix treats themes and fonts as **runtime configuration**, not build-time artifacts.

---

## 1.1 Filesystem as Source of Truth

Themes are discovered dynamically:

```go


func (s *Server) listThemes() ([]string, error) {
	base := "/var/www/go_blog/assets/css/themes"

	entries, err := os.ReadDir(base)
	if err != nil {
		return nil, err
	}

	var themes []string
	for _, e := range entries {
		if !e.IsDir() && strings.HasSuffix(e.Name(), ".css") {
			name := strings.TrimSuffix(e.Name(), ".css")
			themes = append(themes, name)
		}
	}

	sort.Strings(themes)
	return themes, nil
}


```

There is:

- no config file
- no registry
- no in-memory state

> The filesystem defines what exists.

Fonts follow the exact same pattern.

---

## 1.2 Current Theme = Symlink Target

```go


func (s *Server) currentTheme() string {
	link := "/var/www/go_blog/assets/css/theme.css"

	target, err := os.Readlink(link)
	if err != nil {
		return ""
	}

	base := filepath.Base(target)
	return strings.TrimSuffix(base, ".css")
}


```

The active theme is:

```text


theme.css → themes/dark.css


```

So:

- `Readlink` → resolves the pointer
- No DB
- No cache
- No config

> State is encoded directly in the filesystem.

---

## 1.3 Atomic Theme Switching

```go


func (s *Server) applyTheme(name string) error {
	baseCSS := "/var/www/go_blog/assets/css"
	baseFavicon := "/var/www/go_blog/assets"

	cssTarget := filepath.Join(baseCSS, "themes", name+".css")
	cssLink := filepath.Join(baseCSS, "theme.css")
	cssTmp := cssLink + ".tmp"

	favTarget := filepath.Join(baseFavicon, "favicons", name+".svg")
	favLink := filepath.Join(baseFavicon, "favicon.svg")
	favTmp := favLink + ".tmp"

	if _, err := os.Stat(cssTarget); err != nil {
		return err
	}
	if _, err := os.Stat(favTarget); err != nil {
		return err
	}

	os.Remove(cssTmp)
	if err := os.Symlink(cssTarget, cssTmp); err != nil {
		return err
	}
	if err := os.Rename(cssTmp, cssLink); err != nil {
		return err
	}

	os.Remove(favTmp)
	if err := os.Symlink(favTarget, favTmp); err != nil {
		return err
	}
	if err := os.Rename(favTmp, favLink); err != nil {
		return err
	}

	return nil
}


```

### Important detail: atomic swap

Instead of replacing directly:

```text


create temp → rename → swap


```

This guarantees:

- no partial state
- no race conditions
- instant switch

---

## 1.4 Key Principle

> If it doesn’t require recomputation, don’t rebuild it.

Themes and fonts are **not part of the build graph**.

---

# 2\. Localized Builds: The Core of Statix

This is where Statix becomes fundamentally different.

---

## 2.1 Full Build (Baseline)

```go


func (s *Server) rebuildSite() error {
	articleRepo := db.ArticleRepo{DB: s.DB}
	subjectRepo := db.SubjectRepo{DB: s.DB}
	authorRepo  := db.AuthorRepo{DB: s.DB}

	articles, _ := articleRepo.ListAll()
	subjects, _ := subjectRepo.ListAll()
	content, _ := authorRepo.GetContent()

	gen := generator.Generator{
        AuthorContent: template.HTML(content),
        ArticleRepo: articleRepo,
        SubjectRepo: subjectRepo,
		Articles: articles,
		Subjects: subjects,
		OutDir:   "dist",
	}

	gen.Build()
	gen.BuildRSS()
	gen.BuildAuthor()
	return gen.BuildSitemap()
}


```

This is the **full graph rebuild**.

Used only when necessary.

---

## 2.2 Localized Build Entry Point

```go


func (s *Server) rebuildSiteLocalize(
    title string,
    subject_id int64,
    sitemap_build bool,
    is_deletion bool,
) error {


```

This function is the **core of Statix’s incremental system**.

---

### Step 1 — Load global state

```go


articles, _ := articleRepo.ListAll()
subjects, _ := subjectRepo.ListAll()


```

Even for localized builds:

- full dataset is loaded
- but not fully rebuilt

Why?

> Because dependency resolution happens inside the generator.

---

### Step 2 — Initialize generator

```go


gen := generator.Generator{
    AuthorContent: template.HTML(""),
    ArticleRepo: articleRepo,
    SubjectRepo: subjectRepo,
    Articles: articles,
    Subjects: subjects,
    OutDir: "dist",
}


```

Notice:

- `AuthorContent` is empty → not rebuilding author page
- selective context = selective build

---

### Step 3 — Localized build

```go


gen.LocalizedBuild(title, subject_id, is_deletion)


```

This is where the dependency graph is applied.

---

## 2.3 What LocalizedBuild Implies

Given:

- `title`
- `subject_id`
- `is_deletion`

The generator can infer affected nodes:

### Always rebuilt:

1. **Article page**

```text


/article/<slug>.html


```

### Also rebuilt:

2. **Global index**

```text


/index.html


```

Because:

- title might change
- ordering might change

3. **Subject page**

```text


/subject/<slug>.html


```

Because:

- article belongs to subject
- listing must update

---

### If deletion:

- remove article page
- update index
- update subject

---

## 2.4 Conditional Global Artifacts

```go


if sitemap_build {
    gen.BuildRSS()
    return gen.BuildSitemap()
}


```

This is a **key optimization**.

RSS and sitemap are:

- global artifacts
- expensive relative to a single page

So they are:

- rebuilt only when needed
- explicitly controlled

---

## 2.5 Event-Based Builds

Statix defines **build entry points per event type**.

---

### Subject creation / deletion

```go


func (s *Server) rebuildSubjectEvent() error {
    gen.SubjectEventBuild()
    return gen.BuildSitemap()
}


```

---

### Subject edit

```go


func (s *Server) rebuildSubjectEdit(subject_id int64) error {
    gen.SubjectEditBuild(subject_id)
    gen.BuildRSS()
    return gen.BuildSitemap()
}


```

---

### Author update

```go


func (s *Server) rebuildAuthor() error {
	gen := generator.Generator{
        AuthorContent: template.HTML(content),
	}
	return gen.BuildAuthor()
}


```

---

## 2.6 This Is a Dependency Graph

Statix never declares a graph explicitly.

But it behaves like one:

```text


article → index
article → subject
subject → sitemap
subject → rss
author → author page


```

Each handler triggers:

- exactly the required edges
- nothing more

---

# 3\. Admin Layer = Build Orchestrator

The admin HTTP layer is not just CRUD.

It is the **trigger system for the build graph**.

---

## 3.1 Editing an Article

```go


repo.Update(id, title, subjectId, isPublic, html)

s.rebuildSiteLocalize(title, subjectId, false, false)


```

Key points:

- DB is updated first
- Then rebuild is triggered
- No async queue
- No background job

> The system is synchronous and deterministic

---

## 3.2 Creating an Article

```go


newID, _ := articleRepo.Create(...)

s.rebuildSiteLocalize(title, subjectId, true, false)


```

Difference:

- `sitemap_build = true`
- because new content affects discovery

---

## 3.3 Deleting an Article

```go


articleRepo.Delete(id)

s.rebuildSiteLocalize(article.Title, article.SubjectId, true, true)


```

Now:

- `is_deletion = true`
- generator handles removal logic

---

## 3.4 Subject Operations

Each subject operation maps to a specific rebuild path:



| Action | Function |
| --- | --- |
| Create/Delete | rebuildSubjectEvent |
| Edit | rebuildSubjectEdit |




---

## 3.5 Why This Matters

There is no:

- job queue
- background worker
- rebuild scheduler

Everything is:

> immediate, explicit, and predictable

---

# 4\. CLI: Externalizing the System

The `stx` CLI mirrors the admin API.

```text


stx publish --file FILE
stx create ...
stx edit ...
stx remove ...


```

It interacts with:

- HTTP endpoints
- token authentication ( `X-Statix-Token`)
- deterministic responses

Example:

```go


if r.Header.Get("X-Statix-Token") != "" {
    w.WriteHeader(http.StatusOK)
    w.Write([]byte("article edited\n"))
}


```

This enables:

- scripting
- automation
- integration with editors / pipelines

---

# 5\. NeoVm Integration

Statix is designed to run inside a controlled environment.

NeoVm provides:

- reproducibility
- isolation
- deterministic execution

This reinforces a key property:

> The same input always produces the same output.

---

# 6\. What Statix Really Is

Statix is not a static site generator.

It is:

> A deterministic build system for content, implemented on top of the filesystem.

---

# 7\. Core Design Principles

- Filesystem > configuration
- Symlinks > state
- Explicit rebuilds > implicit magic
- Localized computation > full rebuilds

And the most important one:

> You decide when you pay the cost — and why.