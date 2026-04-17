When comparing C++ and Go, one of the most interesting differences is not syntax,
not performance, and not even generics — it is **where the responsibility for dispatch logic lives**.

In C++, behavior is encoded into the _type system itself_.
In Go, behavior is often encoded into _consumers of metadata_.

Both approaches are powerful. They simply operate on different axes.

---

## 1\. Compile-Time Dispatch in C++

In modern C++, dispatch logic is typically resolved at compile time.
You use templates, `if constexpr`, traits, concepts, or
`std::variant` with `std::visit`.
The compiler generates the final branching code.
There is no runtime inspection.

### Example: Compile-Time Branching

Here, the compiler selects the branch at compile time based on `T`.
Only the valid branch is instantiated.

```cpp

#include <type_traits>
#include <iostream>

template <typename T>
void process(const T& x) {
    if constexpr (std::is_same_v<T, int>) {
        std::cout << "Processing int\n";
    } else if constexpr (std::is_same_v<T, std::string>) {
        std::cout << "Processing string\n";
    }
}

```

**What happens:**

- `std::is_same_v` is evaluated at compile time.
- The unused branches are discarded during compilation.
- No runtime type checking exists.

---

## 2\. Variant Dispatch in C++

`std::variant` is a type-safe union.
`std::visit` generates a static visitor table at compile time.

```cpp

#include <variant>
#include <iostream>

std::variant<int, std::string> v = 42;

std::visit([](auto&& arg) {
    std::cout << arg << "\n";
}, v);

```

**What happens:**

- The visitor is compiled for each alternative.
- Dispatch is resolved without reflection.
- All possible types must be known at compile time.

C++ pushes structural complexity into compilation.

---

## 3\. Go: Structural Runtime Introspection

Go takes a different approach.
Types describe structure.
Libraries interpret that structure at runtime using reflection.

```go

package main

import (
	"fmt"
	"reflect"
)

type User struct {
	Name string `json:"name"`
	Age  int    `json:"age"`
}

func main() {
	u := User{"Julien", 30}
	t := reflect.TypeOf(u)

	fmt.Println("Type:", t.Name())
	fmt.Println("Fields:", t.NumField())

	for i := 0; i < t.NumField(); i++ {
		field := t.Field(i)
		fmt.Println("Field:", field.Name)
		fmt.Println("Tag:", field.Tag.Get("json"))
	}
}

```

**What happens:**

- `reflect.TypeOf` retrieves runtime type metadata.
- `NumField()` counts struct fields.
- `Field(i)` returns a `StructField` descriptor.
- Tags are plain strings interpreted by libraries.

---

## 4\. Reflection in Go — Deep Dive into `reflect.Type`

`reflect.Type` describes the structure of a type.
It does not hold values — only metadata.

### TypeOf

```go

t := reflect.TypeOf(42)
fmt.Println(t)        // int
fmt.Println(t.Kind()) // int

```

Returns the dynamic type of a value.

### Name vs Kind

```go

type User struct{}
t := reflect.TypeOf(User{})

fmt.Println(t.Name()) // "User"
fmt.Println(t.Kind()) // struct

```

`Name()` returns the declared type name.
`Kind()` returns the underlying category (struct, slice, map, etc.).

### NumField and Field(i)

```go

type User struct {
	Name string `json:"name"`
	Age  int
}

t := reflect.TypeOf(User{})

for i := 0; i < t.NumField(); i++ {
	field := t.Field(i)
	fmt.Println(field.Name)
	fmt.Println(field.Type)
	fmt.Println(field.Tag)
}

```

`StructField` contains:

- Name
- Type
- Tag
- Index
- Offset
- Exported status

### NumMethod and Method(i)

```go

type User struct{}

func (User) Hello() {}

t := reflect.TypeOf(User{})
fmt.Println(t.NumMethod())

m := t.Method(0)
fmt.Println(m.Name)
fmt.Println(m.Type)

```

Only exported methods are visible.

### Elem()

```go

t := reflect.TypeOf(&User{})
fmt.Println(t.Kind())       // ptr
fmt.Println(t.Elem().Kind()) // struct

```

Used to unwrap pointers, slices, arrays, maps, and channels.

### Implements()

```go

type Speaker interface {
	Speak()
}

type Dog struct{}
func (Dog) Speak() {}

t := reflect.TypeOf(Dog{})
iface := reflect.TypeOf((*Speaker)(nil)).Elem()

fmt.Println(t.Implements(iface)) // true

```

Asks at runtime:
**"Does this type satisfy this interface structurally?"**

### AssignableTo()

```go

t1 := reflect.TypeOf(10)
t2 := reflect.TypeOf(0)

fmt.Println(t1.AssignableTo(t2)) // true

```

Returns true if Go would allow direct assignment:

```go

var a int = 10
var b int
b = a // assignable

```

### ConvertibleTo()

```go

t1 := reflect.TypeOf(10)
t2 := reflect.TypeOf(int64(0))

fmt.Println(t1.ConvertibleTo(t2)) // true

```

This matches Go conversion rules:

```go

var x int = 10
var y int64 = int64(x)

```

---

## 5\. `reflect.Value` — Working with Data

If `Type` is the schema, `Value` is the container.
It lets you inspect and modify data dynamically.

### ValueOf and Interface()

```go

v := reflect.ValueOf(42)

fmt.Println(v.Kind())       // int
fmt.Println(v.Interface())  // 42

```

### Field(i)

```go

u := User{"Julien", 30}
v := reflect.ValueOf(u)

fmt.Println(v.Field(0)) // Julien

```

### CanSet and Set\*

```go

u := User{"Julien", 30}
v := reflect.ValueOf(&u).Elem()

if v.Field(0).CanSet() {
	v.Field(0).SetString("Modified")
}

fmt.Println(u.Name) // Modified

```

Rules for setting:

- Must pass a pointer
- Must call `Elem()`
- Field must be exported
- `CanSet()` must be true

### IsZero()

```go

v := reflect.ValueOf(0)
fmt.Println(v.IsZero()) // true

```

### Call()

```go

type User struct{}
func (User) Hello() { fmt.Println("Hello") }

u := User{}
v := reflect.ValueOf(u)
m := v.MethodByName("Hello")
m.Call(nil)

```

This enables dynamic method invocation — used in RPC systems,
dependency injection, and frameworks.

---

## 6\. Dynamic Type Construction

```go

fields := []reflect.StructField{
	{
		Name: "Name",
		Type: reflect.TypeOf(""),
		Tag:  `json:"dynamic_name"`,
	},
}

t := reflect.StructOf(fields)
fmt.Println(t)

```

This creates a new struct type at runtime.
Rare in application code, powerful in frameworks.

---

## 7\. A Subtle Parallel with Haskell

Some reflection methods feel philosophically similar to Haskell’s type system.

- `Implements()` resembles checking for a typeclass instance.
- `AssignableTo()` resembles type compatibility checks.
- `ConvertibleTo()` resembles allowable coercions.

In Haskell, the compiler internally answers:

- Does type `a` satisfy constraint `C`?
- Can `a` unify with `b`?

The difference is timing:

- **Haskell:** Constraint solving happens at compile time.
- **Go:** Type relationship queries happen at runtime.

Haskell constructs proof evidence during compilation.
Go exposes structural metadata for runtime querying.

In a sense:

- C++ pushes everything into compilation.
- Haskell proves everything before execution.
- Go exposes the type system as data.

Same conceptual space. Different design philosophy.

---

## 8\. A Concrete Moment: When Reflection Became Necessary

The need for reflection often does not arise from theoretical curiosity.
It emerges when you write something practical and it “just works” —
and then you ask yourself: how?

Consider the following real-world example: generating a sitemap XML file.

```go

func (g *Generator) buildSitemap() error {
    type URL struct {
        Loc     string `xml:"loc"`
        LastMod string `xml:"lastmod,omitempty"`
    }

    type URLSet struct {
        XMLName xml.Name `xml:"urlset"`
        Xmlns   string   `xml:"xmlns,attr"`
        URLs    []URL    `xml:"url"`
    }

    base := "https://julienlargetpiet.tech"

    urls := []URL{
        {
            Loc:     base + "/",
            LastMod: time.Now().Format("2006-01-02"),
        },
    }

    for _, a := range g.Articles {
        urls = append(urls, URL{
            Loc:     fmt.Sprintf("%s/articles/%d.html", base, a.ID),
            LastMod: a.CreatedAt.Format("2006-01-02"),
        })
    }

    sitemap := URLSet{
        Xmlns: "http://www.sitemaps.org/schemas/sitemap/0.9",
        URLs:  urls,
    }

    data, err := xml.MarshalIndent(sitemap, "", "  ")
    if err != nil {
        return err
    }

    data = append([]byte(xml.Header), data...)

    filename := filepath.Join(g.OutDir, "sitemap.xml")
    return os.WriteFile(filename, data, 0644)
}

```

At first glance, this looks straightforward:

- You define structs.
- You annotate fields with `xml` tags.
- You call `xml.MarshalIndent`.
- You get correctly structured XML.

But here is the crucial question:
**How does `xml.MarshalIndent` know what to do?**

It inspects:

- The struct type.
- The field names.
- The struct tags ( `xml:"loc"`, `xml:"xmlns,attr"`).
- Whether fields are slices.
- Whether fields are zero values (for `omitempty`).

It does all of that using reflection.

The `encoding/xml` package:

- Calls `reflect.TypeOf` to inspect the struct.
- Iterates fields using `NumField()` and `Field(i)`.
- Reads struct tags via `StructField.Tag`.
- Uses `reflect.Value` to extract actual data.
- Checks zero values using `IsZero()`.

You did not write reflection.
But you relied on it.

That is often the first real encounter with reflection in Go:
not when writing a framework —
but when using one.

The struct does not contain serialization logic.
It merely describes structure.
The XML encoder interprets that structure at runtime.

This is the essence of Go’s design philosophy:

> Types declare shape.
> Libraries decide behavior.

---

## Final Perspective

C++ optimizes for zero runtime overhead and maximal compile-time power.
Haskell optimizes for provable correctness through static constraints.
Go optimizes for pragmatic runtime flexibility and simplicity.

Understanding where type reasoning lives — compiler or runtime —
clarifies why these ecosystems feel so different,
even when they solve similar conceptual problems.