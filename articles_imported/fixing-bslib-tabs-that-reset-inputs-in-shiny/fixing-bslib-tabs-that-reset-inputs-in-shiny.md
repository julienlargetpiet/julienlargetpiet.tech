**The problem:**

When using `bslib::navset_tab()`, each tab panel is dynamically created and destroyed as you switch between them. This means that any inputs (like `selectInput()`) in inactive tabs are removed from the DOM. As a result, trying to update them from the server with `updateSelectInput()` or similar functions fails or causes infinite loops.

```r


  navset_tab(
    nav_panel("Panel 1", selectInput("filter_ip1", ...)),
    nav_panel("Panel 2", selectInput("filter_ip2", ...))
  )

```

Here, only one of these `selectInput()` elements exists at a time. When you switch tabs, the other is destroyed and recreated later. So if you try this:

```r


observeEvent(input$filter_ip1, {
  updateSelectInput(session, "filter_ip2", selected = input$filter_ip1)
})

```

it won’t work — because when Panel 1 is active, `filter_ip2` simply doesn’t exist.

### The fix — keep your tabs alive

`bslib` has an option called `keep_alive` that tells Shiny to keep all tab panels in memory instead of destroying them when hidden. This allows inputs to persist and be updated normally.

```r

navset_tab(
  id = "main_tabs",
  keep_alive = TRUE,
  nav_panel("Panel 1", selectInput("filter_ip1", "IP to exclude (panel 1):", choices = NULL)),
  nav_panel("Panel 2", selectInput("filter_ip2", "IP to exclude (panel 2):", choices = NULL))
)

```

Now the synchronization works perfectly:

```r


observeEvent(input$filter_ip1, ignoreInit = TRUE, {
  updateSelectInput(session, "filter_ip2", selected = input$filter_ip1)
})

observeEvent(input$filter_ip2, ignoreInit = TRUE, {
  updateSelectInput(session, "filter_ip1", selected = input$filter_ip2)
})

```

### Result

- Inputs are no longer destroyed when switching tabs
- `updateSelectInput()` and `observeEvent()` work normally
- Values persist across panels — no infinite loops

### Summary



| Tab switching | Destroys hidden tab | Keeps all tabs alive |
| Inputs | Recreated every time | Persistent |
| <code>updateSelectInput()</code> | Fails or loops | Works normally |
| Use case | Lightweight UIs | Dashboards / Interactive apps |




**TL;DR:** If your Shiny app uses `bslib::navset_tab()` and you need to share state or update inputs across tabs, add `keep_alive = TRUE` and everything will just work.