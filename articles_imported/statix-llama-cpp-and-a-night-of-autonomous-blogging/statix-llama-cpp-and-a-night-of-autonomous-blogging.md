This article is about this repo:

[autoBlog](https://github.com/julienlargetpiet/autoBlog)

There is a particular kind of joy in software engineering that does not come from polished products, investor slides, or framework trend cycles. It comes from taking a few simple parts, each understandable on its own, and connecting them until something unexpectedly alive emerges.

That is exactly what happened here.

The starting point was not "let's build an AI startup," nor "let's automate content at scale," nor even "let's use a large language model." The starting point was much simpler and much more honest: I already had Statix, my own publishing system, with its own CLI. I had full control over content publication. I had a local machine. I had curiosity. And one evening, a thought appeared that was too tempting not to try:

What if the blog could publish articles by itself while I sleep?

That single question ended up connecting several engineering dots in a way that felt deeply satisfying. A local model. A local inference server. A Python automation loop. A custom publishing CLI. A database-backed website. And finally, a stream of automatically generated articles flowing into a dedicated subject on the blog.

No cloud service. No paid API. No hidden SaaS dependency. Just local compute, an existing toolchain, and the pleasure of making systems talk to each other.

## The intuition: Statix already made the hard part possible

The key reason this experiment became possible so quickly is that Statix already existed.

That point matters a lot.

When people think about "AI content pipelines," they usually imagine that the hard part is generating text. It is not. Text generation is only one component. The hard part is everything around it: where the text goes, how it is named, how it is categorized, how it is published, how the publishing system identifies it, how the local environment tracks it, and how all of this can be automated without manual intervention.

Because Statix already had a CLI, all those capabilities were already available as composable building blocks.

The commands looked like this:

```text


stx set-credentials --url URL --password TOKEN
stx publish --file FILE [NAME]
stx nickname create --title TITLE --subject_id ID --is_public true|false NAME
stx nickname import ARTICLE_ID NAME
stx nickname import-content [--markdown] ARTICLE_ID NAME
stx nickname edit [--title TITLE] [--subject_id ID] [--is_public true|false] NAME
stx nickname remove [--sync] NAME
stx nickname list
stx nickname rename OLD_NAME NEW_NAME
stx file upload FILE...
stx file delete FILE
stx file list
stx articles
stx subjects
stx subject add NAME
stx subject delete NAME
stx subject rename OLD_NAME NEW_NAME
stx dumpdb
stx completion [bash|zsh]


```

Once a publishing system exposes itself this way, a lot of doors open. The CLI becomes more than a convenience. It becomes an interface layer, a programmable surface. And once you have a programmable surface, automation stops being a fantasy and becomes an exercise in orchestration.

That is the deeper engineering lesson here: when you build a proper CLI for your own system, you are not just making administration easier; you are making future experiments possible.

Statix made the experiment possible before the experiment itself was even imagined.

## Creating the dedicated subject

The first practical step was to create a dedicated subject on the blog for these generated articles. This mattered both structurally and philosophically.

Structurally, it separated AI-generated content from the rest of the blog. Philosophically, it acknowledged that this was an experiment, not an attempt to blur authorship.

The subject created for this purpose was:

**AI-Generated Experiment**

In the database, this subject ended up with the identifier:

```text


24


```

That ID became the anchor point of the entire automation pipeline.

Every generated article would be attached to `subject_id = 24`.

At that point, the blog had a target. The missing piece was content generation.

## Choosing the local model path

There are many ways to use language models today, but most of them route through hosted APIs. That was never the spirit of this experiment.

The goal was local control.

That meant downloading an open model in GGUF format and running it through llama.cpp. This path is elegant for a systems-minded developer because it removes a lot of abstraction. The model becomes a file. The runtime becomes a binary. Inference becomes a local process. The server becomes a local HTTP endpoint. The entire stack becomes inspectable.

A model was downloaded in quantized format:

**Llama 3.1 8B Instruct Q4\_K\_M**

This turned out to be a good practical balance for local CPU inference: small enough to run on a 16 GB RAM machine, large enough to produce usable content.

That detail about memory mattered more than it might seem at first.

## The first confrontation with reality: memory

Running local models is one of those experiences that instantly strips away hype and replaces it with engineering facts.

The first attempt to run the model failed. Not due to some mysterious AI issue, but because the process got killed by the operating system. The kernel logs made it clear: the machine had run out of memory.

That was the first meaningful lesson of the experiment.

A model is not just its file size. Running it also requires memory for context, buffers, and KV cache. On a 16 GB machine, careless defaults can kill the process immediately.

The problem became obvious once the context size was inspected. Without explicitly setting a lower context size, the server tried to allocate an enormous KV cache corresponding to the model's maximum context capability. That was far beyond what the machine could comfortably hold.

The fix was simple and very telling:

```text


./build/bin/llama-server \
  -m ../models/Llama-3.1-8B-Q4_K_M.gguf \
  -c 1024 \
  -t 12


```

The essential flag here was:

```text


-c 1024


```

That single value changed the memory profile enough to make the system stable.

This is one of those moments where a model stops feeling like magic and starts feeling like a normal system component. You tune it. You constrain it. You make it fit the machine. You do engineering.

`-t` is the number of CPU threads that will be used to run the model.

## Building llama.cpp and exposing a local API

Once the build system change from Make to CMake was accounted for, compiling `llama.cpp` was straightforward:

```text


sudo apt update
sudo apt install -y build-essential cmake
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
cmake -B build -DGGML_NATIVE=ON
cmake --build build -j


```

The relevant binary for this experiment was:

```text


./build/bin/llama-server


```

Once launched successfully, the model exposed an HTTP endpoint:

```text


http://127.0.0.1:8080


```

This was the turning point.

As soon as the model could be queried over HTTP, it could be treated like any other service in a local pipeline. The LLM stopped being "that binary you manually invoke in a terminal" and became "a component that can be called programmatically."

A simple test confirmed it was working:

```text


curl http://127.0.0.1:8080/completion \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a short paragraph about AI agents",
    "n_predict": 200
  }'


```

That request returned JSON, including a `"content"` field containing generated text.

That field became the bridge between the model and the rest of the publishing system.

At this point, the model is no longer something you interact with manually. It is not a REPL. It is not a black box. It is simply a local HTTP service.

When llama-server is running, it exposes an endpoint:

`http://127.0.0.1:8080/completion`

From there, interacting with the model becomes indistinguishable from interacting with any other service in a system.

A simple request looks like this:

```text


curl http://127.0.0.1:8080/completion \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a short paragraph about AI agents",
    "n_predict": 200
  }'


```

This is not “AI magic.”

This is:

an `HTTP POST`

with a `JSON` payload

sent to a local process

which returns `JSON`

Nothing more, nothing less.

The request structure

The payload itself is straightforward:

```text


{
  "prompt": "Write a short paragraph about AI agents",
  "n_predict": 200
}


```

`prompt` → the input text

`n_predict` → how many tokens to generate

From a systems perspective, this is simply:

a function call over HTTP:
`f(prompt, parameters) → response`

The response: structured, not mystical

The server responds with JSON, for example:

```text


{
  "content": "AI agents can be used to improve the security of software systems...",
  "tokens_predicted": 200,
  ...
}


```

The only field that really matters for the pipeline is:

"content"

That field contains the generated text.

And that’s the key moment:

this "content" field becomes the bridge between
model inference and your publishing system

The mental shift

This is where the experiment becomes interesting from an engineering standpoint.

You are no longer:

“using an AI”

You are:

calling a local service with HTTP
and consuming its output like any other system component

That shift matters.

Because once the model is seen as:

HTTP service → JSON in / JSON out

it becomes composable.

You can:

call it from Python

pipe it into a CLI

store results in a database

retry on failure

wrap it in automation loops

At that point, the LLM stops being special.

It becomes just another node in your architecture.

## The Python script: where everything came together

The heart of the experiment became a small Python script: `autoBlog.py`.

This script did not try to be clever. That is precisely why it worked.

Its job was simple:

1. Choose a topic.
2. Build a prompt from a prompt template.
3. Send that prompt to the local llama.cpp server.
4. Parse the JSON response.
5. Extract a title from the generated Markdown.
6. Save the body into a local file.
7. Use the Statix CLI to create a nickname and publish the file.
8. Sleep.
9. Repeat.

That loop is almost embarrassingly simple when written down. But simplicity is part of the beauty here. A complex system emerged from a chain of ordinary operations.

## Command-line configurability

The script evolved into a configurable CLI tool using `argparse`.

It accepted:

- whether articles should be public or private,
- the target Statix subject ID,
- the LLM request timeout,
- the local LLM endpoint URL,
- the topics file,
- the prompt file.

That design choice matters because it turned the script from a one-off hack into an actual tool. It could now be reused, rerun, and adapted without code edits.

## Topics as external data

The list of topics was not hardcoded forever. It was moved into a `topics.txt` file.

That may look like a minor detail, but it reflects an important engineering instinct: separate code from data wherever it improves flexibility.

A typical `topics.txt` looked like this:

```text


# Core AI trends
AI agents in 2026
The evolution of autonomous systems
How LLMs are reshaping software engineering
The limits of artificial intelligence
AI and the future of work

# Engineering-focused
Building reliable AI systems in production
Memory management challenges in LLM inference
Latency vs quality tradeoffs in local LLMs
How AI changes debugging workflows
Designing deterministic systems with probabilistic models

# Systems & performance
Optimizing LLM inference on CPU
Understanding KV cache and memory bottlenecks
Tradeoffs between quantization levels
Scaling local AI systems without GPUs
Threading and performance in AI inference engines


```

The script loaded that file once at startup, ignored blank lines and comments, and randomly selected topics as it looped.

## Prompt as external data

The prompt was also moved out of the code and into `prompt.txt`.

Again, that may seem small, but it makes iterative prompt engineering much easier. The script could now evolve independently from the instructions given to the model.

At startup, the script loaded the prompt template once into memory, then replaced a `{{TOPIC}}` placeholder for each iteration. This avoided repeatedly reading the file and reduced the amount of variability and failure inside the hot loop.

That is a small optimization, but it reflects a larger principle: configuration should be loaded once, not re-read on every iteration unless hot reload is explicitly required.

## Hardened request logic

The function responsible for querying the model was hardened to handle several failure modes:

- prompt file missing or unreadable,
- LLM server not running,
- request timeout,
- HTTP-level errors,
- malformed JSON responses,
- empty content.

This matters because the difference between "a script that works once" and "a script that can run through the night" is not fancy architecture. It is failure handling.

The model request path became resilient enough to skip failed iterations rather than crash the entire process.

That is the kind of engineering detail that readers rarely see when they encounter "AI automation," but it is exactly what makes the system feel real.

## Markdown generation and title extraction

The output format chosen for generated articles was Markdown, with a very specific constraint:

- the title had to be the only `#` top-level heading,
- section headings could use `##`,
- the generated title would be extracted and removed from the body before publishing.

This led to a neat little function that parsed the generated content line by line.

The logic was:

- If the first title line is found as `# Title`, capture it.
- Remove that line from the content.
- If the model failed to format things exactly right, fall back to the first non-empty line and strip any heading markers from it.

That fallback is worth highlighting. It is one of those small defensive mechanisms that make probabilistic systems manageable. The model is not perfectly obedient, so the consuming code must remain slightly forgiving without becoming sloppy.

Once extracted, the title fed directly into the Statix nickname creation command.

## Slug generation

The extracted title was converted into a nickname using a `slugify` function. That function lowercased the text, replaced non-alphanumeric spans with dashes, and trimmed the ends.

That slug became both:

- the nickname in Statix,
- the filename inside the local `articles/` folder.

That led to files such as:

```text


articles/understanding-kv-cache-and-memory-bottlenecks.md
articles/threading-and-performance-in-ai-inference-engines.md


```

This is the kind of small consistency that makes automation pleasant: one canonical title-derived identifier, reused across file naming and publication naming.

## The publishing step: where the system became real

Once the title and content were ready, the Python script called the Statix CLI twice.

First, it created the nickname:

```text


stx nickname create --title "Some Title" --subject_id 24 --is_public true some-title


```

Then it published the file:

```text


stx publish --file articles/some-title.md some-title


```

At that point, there was no longer a conceptual gap between "AI generated content" and "published article." The system had crossed that boundary. Generated text became a real article in the real site database, reachable through a real URL.

That is the moment where an experiment becomes emotionally satisfying. The terminal command stops being a toy. It writes into the actual world of the application.

Statix, once again, was the reason this felt so smooth. The CLI had already solved the publishing layer. The AI layer only had to plug itself into it.

## The generated articles

The experiment produced a series of AI-generated articles that were published under the dedicated subject.

Among them were:

- `initialize-a-model-and-tokenizer.html`
- `ai-agents-in-2026-revolutionizing-industries.html`
- `the-future-of-autonomous-systems.html`
- `limits-of-artificial-intelligence.html`
- `use-of-for-subheaders.html`
- `llms-and-the-future-of-software-engineering.html`
- `autonomous-systems-the-future-of-transportation-and-beyond.html`
- `how-llms-change-software-engineering.html`
- `bold-and-italic-supported.html`
- `introduction.html`
- `image-links-are-not-allowed-use-image-description-instead.html`
- `no-in-the-text.html`
- `use-of-emojis-to-enhance-readability.html`
- `threading-and-performance-in-ai-inference-engines.html`
- `a-minimum-of-3-subheadings.html`
- `title-must-be-the-death-of-traditional-blogging.html`
- `understanding-kv-cache-and-memory-bottlenecks.html`
- `dfdfdf.html`
- `can-ai-systems-be-exploited.html`
- `and-header-will-be.html`
- `this-is-a-valid-markdown-header.html`

And they can be seen here:

- [link2](https://julienlargetpiet.tech/articles/initialize-a-model-and-tokenizer.html)
- [link3](https://julienlargetpiet.tech/articles/ai-agents-in-2026-revolutionizing-industries.html)
- [link4](https://julienlargetpiet.tech/articles/the-future-of-autonomous-systems.html)
- [link5](https://julienlargetpiet.tech/articles/limits-of-artificial-intelligence.html)
- [link6](https://julienlargetpiet.tech/articles/use-of-for-subheaders.html)
- [link7](https://julienlargetpiet.tech/articles/llms-and-the-future-of-software-engineering.html)
- [link8](https://julienlargetpiet.tech/articles/autonomous-systems-the-future-of-transportation-and-beyond.html)
- [link9](https://julienlargetpiet.tech/articles/how-llms-change-software-engineering.html)
- [link10](https://julienlargetpiet.tech/articles/bold-and-italic-supported.html)
- [link11](https://julienlargetpiet.tech/articles/introduction.html)
- [link12](https://julienlargetpiet.tech/articles/image-links-are-not-allowed-use-image-description-instead.html)
- [link13](https://julienlargetpiet.tech/articles/no-in-the-text.html)
- [link14](https://julienlargetpiet.tech/articles/use-of-emojis-to-enhance-readability.html)
- [link15](https://julienlargetpiet.tech/articles/threading-and-performance-in-ai-inference-engines.html)
- [link16](https://julienlargetpiet.tech/articles/a-minimum-of-3-subheadings.html)
- [link17](https://julienlargetpiet.tech/articles/title-must-be-the-death-of-traditional-blogging.html)
- [link18](https://julienlargetpiet.tech/articles/understanding-kv-cache-and-memory-bottlenecks.html)
- [link19](https://julienlargetpiet.tech/articles/dfdfdf.html)
- [link20](https://julienlargetpiet.tech/articles/can-ai-systems-be-exploited.html)
- [link21](https://julienlargetpiet.tech/articles/and-header-will-be.html)
- [link22](https://julienlargetpiet.tech/articles/this-is-a-valid-markdown-header.html)

The list itself tells a story.

Some titles are serious and relevant. Some are malformed. Some clearly reflect prompt leakage. Some reveal formatting instructions accidentally turned into content. Some are surprisingly on-topic. Some are chaotic.

That is not a flaw in the experiment. It is the experiment.

It shows exactly what happens when a local language model is plugged into a real publishing pipeline with only partial guardrails. You do not get science fiction. You get a mixture of signal, slippage, emergent humor, and genuine usefulness.

And that mixture is fascinating.

## Querying the database directly

Because the site is backed by a database, it was also possible to inspect the results directly through SQL.

The query used to list generated article URLs by subject was:

```sql


SELECT title_url FROM articles WHERE subject_id = 24;


```

That is an important detail because it proves something fundamental: the generated articles were not floating in some in-memory demo state. They were properly persisted as first-class content entries in the application database.

Once those rows were exported into a file, a small Unix pipeline was used to append the `.html` suffix to each line:

```text


cat links.txt | sed 's/[[:space:]]*$/.html/' > link_filtered.txt


```

This is a delightfully old-school moment in the middle of an AI project. A local model generates content, a custom CLI publishes it, a relational database stores it, and then a `sed` command tidies up exported URLs. That contrast is part of the charm. Real systems are built out of layers from different eras of computing, and when they work together cleanly, it feels wonderful.

## The hidden elegance of the local state file

Another interesting piece that emerged naturally in the process was the local file:

```text


.statix_articles.json


```

This file exists because the Statix CLI keeps local state about published articles and nickname mappings.

That matters. Automation is not only about sending commands. It is also about preserving a coherent relationship between local actions and remote state. The CLI's local cache makes that relationship explicit.

In other words, the experiment did not only generate and publish content. It also participated in the same state-tracking model as the rest of the system.

That is another sign that this was not a toy hack glued on top of the blog. It became a genuine part of the publishing ecosystem.

## The emotional side of the engineering

What makes this experiment satisfying is not merely that it worked. It is that the path from idea to execution followed a series of understandable engineering moves.

First came the realization that Statix already exposed everything necessary through a CLI.

Then came the local model setup, including the practical lessons about quantization, context size, and RAM limits.

Then came the shift from terminal experimentation to HTTP-based local inference.

Then came the Python glue, which translated generated text into publishable content.

Then came the database query, which confirmed that the articles were truly there.

At every step, the next move felt natural. Nothing required a leap of faith. The dots connected because each component had been built or chosen in a way that respected composability.

And that may be the most important takeaway of all.

When your tools are built with clear boundaries and proper interfaces, unexpected experiments become possible. A static blog system becomes a programmable publishing engine. A local model runtime becomes a content backend. A short Python loop becomes an autonomous article factory.

This is not about AI replacing authorship. It is about what becomes possible when software is designed so that its parts can be rearranged into new systems.

## What the experiment revealed

The experiment revealed several things at once.

It showed that local LLM inference is not mystical. It is a resource-constrained systems problem that can be reasoned about and tuned.

It showed that a well-designed CLI transforms a product into a platform.

It showed that automation becomes truly interesting when it acts on a system you actually own.

It showed that language models, when connected to a real publishing path, generate not only content but also artifacts of their own constraints: malformed titles, leaked instructions, accidental comedy, and moments of genuine relevance.

It showed that the distance between "I wonder if this is possible" and "this is running against my real database" can be surprisingly short when the interfaces are good.

Most of all, it reinforced a simple conviction:

> Once you have a CLI, everything becomes possible.

Not because the CLI is magic, but because it forces your system to become composable. And composability is what lets experiments turn into tools.

## Closing thought

There is something deeply satisfying about watching a machine on your desk generate text, save files, invoke your own CLI, update your own publishing system, and fill a dedicated subject on your site while you sleep.

Not because the generated content is perfect. It isn't.

Not because the experiment proves some grand theory about the future. It doesn't.

But because it demonstrates, in a very concrete way, what happens when software components are designed to connect cleanly. A blog engine, a model server, a Python script, a database query, and a few shell commands became a coherent autonomous publishing loop.

That is the real story here.

The model was interesting. The generated articles were amusing. The malformed outputs were revealing. But the most beautiful part was architectural:

Statix already made it possible. The local LLM only completed the circuit.