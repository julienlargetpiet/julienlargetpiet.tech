> A comprehensive technical reference — from JVM internals to streams, lambdas, and the philosophy behind Java's design choices.

---

## Table of Contents

01. [Introduction & Philosophy](#1-introduction--philosophy)
02. [Everything is a Class](#2-everything-is-a-class)
03. [Memory Model: Stack, Heap & Metaspace](#3-memory-model-stack-heap--metaspace)
04. [The `static` Keyword — Java vs C++](#4-the-static-keyword--java-vs-c)
05. [Constructors & Method Overloading](#5-constructors--method-overloading)
06. [Encapsulation: Getters & Setters](#6-encapsulation-getters--setters)
07. [Inheritance, Virtual Dispatch & vtables](#7-inheritance-virtual-dispatch--vtables)
08. [Overriding `toString()` — Why It Matters](#8-overriding-tostring--why-it-matters)
09. [Interfaces, Lambdas & Functional Programming](#9-interfaces-lambdas--functional-programming)
10. [Primitive Types vs Wrapper Classes](#10-primitive-types-vs-wrapper-classes)
11. [Comparators as Objects — Everything is a Class](#11-comparators-as-objects--everything-is-a-class)
12. [Collections, Maps & Sets](#12-collections-maps--sets)
13. [The Stream API](#13-the-stream-api)
14. [Type Inference in Java](#14-type-inference-in-java)
15. [Summary Diagram](#15-summary-diagram)

---

## 1\. Introduction & Philosophy

Java was released by Sun Microsystems in 1995, designed with a clear motto: **"Write Once, Run Anywhere"**. Unlike C or C++, Java programs do not compile to native machine code directly. Instead they compile to **bytecode**, which the **Java Virtual Machine (JVM)** interprets and JIT-compiles at runtime on any platform.

This gives Java several fundamental properties:

- **Platform independence**: The JVM abstracts the underlying OS and hardware.
- **Automatic memory management**: The Garbage Collector (GC) reclaims unused heap objects.
- **Strong type safety**: Types are enforced both at compile time and runtime.
- **Pure object-orientation**: Almost everything lives inside a class.

### Core Design Choices

Java made several opinionated choices that distinguish it from C++:



| Design Choice | Java | C++ |
| --- | --- | --- |
| Memory management | Automatic (GC) | Manual (<code>new</code>/<code>delete</code>) |
| Multiple inheritance | No (interfaces only) | Yes |
| Pointers | Not exposed | Full pointer arithmetic |
| All methods | Virtual by default (polymorphic) | Non-virtual by default |
| Primitive types | Still exist (<code>int</code>, <code>float</code>...) | Full low-level primitives |
| Entry point | <code>public static void main</code> inside a class | Free function <code>main()</code> |




These choices make Java safer and more portable, at the cost of some raw performance and control.

---

## 2\. Everything is a Class

In Java, **every piece of code must belong to a class**. There are no free functions, no global variables. This is not just a stylistic choice — it is enforced by the compiler and the JVM.

```java


public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}


```

Even `main()` is a method of a class. Even `System.out.println` is a method call on a static field `out` of the class `System`, which itself is a class.

### What "class" means at the JVM level

When the JVM loads a `.class` file, it:

1. Reads the **bytecode** compiled from your `.java` source.
2. Creates a **Class object** (an instance of `java.lang.Class`) in **Metaspace** that describes the class structure.
3. Allocates space for **static fields** in Metaspace.
4. Makes the class available for instantiation on the **Heap**.

Every object you create with `new` is an instance of a class. Every method call goes through the class definition stored in Metaspace.

### The implicit superclass: `Object`

Every class in Java — unless it explicitly extends another — implicitly extends `java.lang.Object`. This means every object has by default:

- `toString()` — text representation
- `equals(Object o)` — equality check
- `hashCode()` — hash for use in `HashMap`, `HashSet`
- `getClass()` — runtime class info
- `clone()` — shallow copy (requires `Cloneable`)

This is why you can call `System.out.println(anyObject)` and get _something_ — it uses `toString()` from `Object` as a fallback.

---

## 3\. Memory Model: Stack, Heap & Metaspace

Understanding where things live in memory is critical for writing correct, efficient Java. The JVM divides memory into three key regions.

### 3.1 Overview



| Criterion | Stack (Thread Stack) | Heap | Metaspace |
| --- | --- | --- | --- |
| <strong>Role</strong> | Method execution | Object storage | Class metadata |
| <strong>Scope</strong> | Per thread | Global (shared) | Global (per classloader) |
| <strong>Contents</strong> | Local variables, references, call frames | Objects (<code>new</code>), arrays, instances | Class structures, methods, bytecode, runtime constants |
| <strong>Allocation</strong> | Automatic on method call | Dynamic (<code>new</code>) | Class loading |
| <strong>Release</strong> | Automatic on method return | Garbage Collector | GC (class unloading) |
| <strong>Structure</strong> | LIFO (stack) | Free graph of objects | Structured by classloader |
| <strong>Speed</strong> | ⚡ Very fast | ⚡⚡ Medium | ⚡ Medium |
| <strong>Size</strong> | Limited (<code>-Xss</code>) | Configurable (<code>-Xmx</code>) | Dynamic (<code>-XX:MaxMetaspaceSize</code>) |
| <strong>Typical error</strong> | <code>StackOverflowError</code> | <code>OutOfMemoryError: Java heap space</code> | <code>OutOfMemoryError: Metaspace</code> |
| <strong>GC involvement</strong> | None | Yes (G1, ZGC, etc.) | Indirect (class unloading) |
| <strong>CPU locality</strong> | Excellent | Medium | Medium |
| <strong>Example</strong> | <code>int x = 5;</code> | <code>new Object()</code> | <code>class MyClass {}</code> |




### 3.2 The Stack

The Stack is the region where **method execution happens**. Each thread has its own stack. Every time a method is called, a new **stack frame** is pushed:

```text


STACK (thread 1)
┌───────────────────────┐
│  example() frame      │  ← top (current method)
│    int a = 10         │
│    String s = <ref>   │  ← reference (pointer to heap)
├───────────────────────┤
│  main() frame         │
│    args = <ref>       │
└───────────────────────┘


```

When the method returns, the frame is **popped** automatically. This is why local variables are "freed" without any GC involvement — the stack pointer simply moves back.

**What lives on the stack:**

- Primitive local variables ( `int`, `float`, `boolean`, etc.)
- **References** (pointers) to objects on the heap
- Method parameters
- Return addresses

**What does NOT live on the stack:**

- Objects (they are always on the heap)
- The content of strings or arrays

### 3.3 The Heap

The Heap is where all **objects** live. When you write `new SomeClass(...)`, Java:

1. Allocates memory on the heap.
2. Initializes the object fields.
3. Returns a **reference** (stored on the stack or in another heap object).

```java


void example() {
    int a = 10;                   // Stack: primitive value
    String s = new String("hi");  // Stack: reference 's'
                                  // Heap: String object containing "hi"
}


```

The heap is managed by the **Garbage Collector**. Java uses sophisticated GC algorithms:

- **G1 GC** (default since Java 9) — generational, low pause
- **ZGC** — near-zero pause, scalable to terabytes
- **Shenandoah** — concurrent compaction

The GC periodically finds **unreachable objects** (no live references pointing to them) and reclaims their memory.

The Heap is separated into **2 generations**

### 1\. Young Generation (Young Gen)

This is where **new objects are allocated**.

It is divided into:

- **Eden Space** → all new objects start here
- **Survivor Spaces (S0 and S1)** → hold objects that survived at least one GC cycle

#### Behavior:

- Uses **Minor GC** (fast, frequent)
- Allocation is extremely fast (pointer bumping)
- Most objects die here quickly (short-lived objects)

#### Lifecycle:

1. Objects are created in Eden
2. When Eden is full → **Minor GC occurs**
3. Surviving objects are copied to a Survivor space
4. After several GC cycles, surviving objects are **promoted to Old Gen**

---

### 2\. Old Generation (Tenured Gen)

This stores **long-lived objects** that survived multiple GC cycles.

#### Behavior:

- Uses **Major GC / Full GC** (slower, less frequent)
- Contains objects with longer lifetimes (caches, large structures, singletons)
- More expensive to collect because it is larger and objects live longer

---

### Why Generations Exist

This design is based on the **weak generational hypothesis**:

> Most objects die young.

So the JVM optimizes:

- Young Gen → frequent, fast cleanup
- Old Gen → infrequent, more thorough cleanup

---

### Minor GC vs Major GC

- **Minor GC**
  - Only affects Young Generation
  - Very fast
  - Happens frequently
- **Major GC / Full GC**
  - Affects Old Generation (and sometimes entire heap)
  - Much slower
  - Can cause noticeable pauses

---

### Notes on Modern Collectors

- **G1 GC**
  - Still generational but uses **regions instead of contiguous spaces**
  - Performs incremental and parallel collection
- **ZGC / Shenandoah**
  - Region-based and highly concurrent
  - Designed for **very low pause times**
  - Generational separation is less strict (though generational ZGC exists in newer Java versions)

---

### Summary

- Heap = managed memory area for objects
- Split into **Young Gen** (short-lived) and **Old Gen** (long-lived)
- GC focuses on reclaiming memory efficiently based on object lifetime

### 3.4 Metaspace

Metaspace (introduced in Java 8, replacing the old PermGen) is where the JVM stores **class-level metadata**. This includes:

- The class definition itself (field names, types, access modifiers)
- Method signatures and bytecode
- Static field values
- Runtime constant pool
- Interface tables (used for virtual dispatch — see section 7)

When you write:

```java


class MyClass {}


```

The JVM loads the class descriptor into Metaspace. This happens only **once per classloader**, regardless of how many instances you create.

**Key difference:** you can create a million `MyClass` objects on the Heap, but the class description in Metaspace exists only once.

### 3.5 Concrete Example: All Three Regions

```java


void example() {
    int a = 10;                  // Stack: primitive integer, value = 10
    String s = new String("hi"); // Stack: reference 's'
                                 // Heap: String object { value = ['h','i'] }
}


```

Behind the scenes:

- The `String` **class** is loaded into **Metaspace** (class description, methods like `length()`, `charAt()`, etc.)
- The `"hi"` **object** lives on the **Heap**
- The variable `s` (a reference/pointer) lives on the **Stack**

When `example()` returns:

- `s` is popped off the stack
- The `String` object on the heap becomes **unreachable** → eligible for GC
- The `String` class in Metaspace stays (as long as the classloader is alive)

---

## 4\. The `static` Keyword — Java vs C++

The word `static` in Java and C++ share the same spelling but carry **very different meanings**. In Java, `static` is fundamentally about **independence from instances**.

### 4.1 `static` in C++ (memory duration)

In C++, `static` primarily controls **storage duration** and **linkage**:

```cpp


// C++
static int x = 5;        // file-scoped, not visible outside translation unit
void func() {
    static int count = 0; // persists across calls
    count++;
}
class Foo {
    static int bar;       // shared across all instances (similar to Java)
};


```

### 4.2 `static` in Java (class-level membership)

In Java, `static` means: **"this belongs to the class, not to any instance"**.

```java


class Counter {
    static int count = 0;    // belongs to Counter class, shared
    int instanceId;          // belongs to each individual object

    Counter() {
        count++;
        instanceId = count;
    }
}


```

- `Counter.count` — accessible via the class name, no object needed
- `new Counter().instanceId` — only accessible through an instance

### 4.3 `static` methods

A `static` method can be called without creating an object:

```java


class MathUtils {
    static int add(int a, int b) {
        return a + b;
    }
}

// Call without an instance:
int result = MathUtils.add(3, 5);


```

This is equivalent to a free function in C++. The method lives in Metaspace; no object is involved.

**Limitation:** a `static` method cannot access non-static fields or call non-static methods — because there is no `this` reference.

### 4.4 `static` for auto-incrementing IDs (real pattern)

A common Java pattern using `static`:

```java


public class Employe {
    static public Integer id = 0;

    static public Integer make_id() {
        return id++;
    }

    private Integer idInt;

    public Employe(String nom, double salaire) {
        this.idInt = make_id(); // each new Employe gets a unique ID
    }
}


```

`id` is shared across all instances. Every `new Employe(...)` increments it. The counter lives in **Metaspace** alongside the class.

### 4.5 Static vs Non-Static Inner Classes

This is one of the most subtle and important distinctions in Java.

#### Non-static inner class

```java


class Outer {
    String outerField = "hello";

    class Inner {
        void print() {
            System.out.println(outerField); // ✅ access to Outer's fields
        }
    }
}

// Usage:
Outer o = new Outer();
Outer.Inner i = o.new Inner(); // MUST have an Outer instance


```

A non-static inner class:

- Is **tied to a specific instance of the outer class**
- Holds an **implicit hidden reference** to the outer object ( `this$0` internally)
- Can access **all** fields and methods of the outer class, even `private` ones
- Increases **memory usage** — every inner object holds a reference to the outer object

#### Static inner class

```java


class Outer {
    static class Inner {
        static int add(int a, int b) {
            return a + b;
        }
    }
}

// Usage:
Outer.Inner i = new Outer.Inner(); // No Outer instance needed


```

A static inner class:

- Is **independent** of any outer class instance
- Has **no access** to non-static fields of `Outer`
- Is essentially a normal class **namespaced inside** `Outer`
- Has **no hidden reference** — lighter in memory

#### Comparison Table



| Property | Inner (non-static) | static Inner |
| --- | --- | --- |
| Needs <code>Outer</code> instance | ✅ Yes | ❌ No |
| Access to non-static <code>Outer</code> fields | ✅ Yes | ❌ No |
| Hidden <code>this$0</code> reference | ✅ Yes | ❌ No |
| Typical use | Business logic tied to parent object | Utility / helper / data class |




#### The classic `main` method trap

```java


public class HelloWorld1 {
    public class Test {                        // ❌ non-static inner class
        public static void main(String[] args) {
            // This won't work as an entry point!
        }
    }
}


```

`main` is a static method. But `Test` is a non-static inner class, so the JVM would need an instance of `HelloWorld1` to access `Test` — which it doesn't have at startup. Fix:

```java


public class HelloWorld1 {
    static class Test {                        // ✅ static inner class
        public static void main(String[] args) {
            Float f = 34.0f;
            System.out.println(f);
        }
    }
}
// Launch: java HelloWorld1$Test


```

#### Rule of thumb

> If the inner class does not need access to instance data of the outer class, always make it `static`. It is lighter, clearer, and avoids accidental memory leaks.

---

## 5\. Constructors & Method Overloading

Java allows **multiple constructors** for the same class, distinguished by the number and types of their parameters. The compiler resolves which constructor to call based on the **method signature**.

```java


public class Employe {
    private int idEmploye;
    private String nom;
    private String prenom;

    // Constructor 1: (int, String, String)
    public Employe(int id, String nom, String prenom) {
        this.idEmploye = id;
        this.nom = nom;
        this.prenom = prenom;
    }

    // Constructor 2: (String, String, int) — different parameter ORDER
    public Employe(String nom, String prenom, int id) {
        this(id, nom, prenom); // delegate to constructor 1 using this(...)
    }

    // Constructor 3: no arguments — interactive input
    public Employe() {
        Scanner scan = new Scanner(System.in);
        System.out.print("Enter employee ID: ");
        this.idEmploye = scan.nextInt();
        scan.nextLine();
        System.out.print("Enter last name: ");
        this.nom = scan.nextLine();
        System.out.print("Enter first name: ");
        this.prenom = scan.nextLine();
    }

    // Constructor 4: only ID, fill defaults
    public Employe(int id) {
        this(id, "nom par défaut", "prenom par défaut");
    }
}


```

**Usage:**

```java


Employe empl1 = new Employe(1, "Paul", "Sho");       // → Constructor 1
Employe empl2 = new Employe("Jean", "Sho", 2);        // → Constructor 2
Employe empl3 = new Employe();                         // → Constructor 3
Employe empl4 = new Employe(3);                        // → Constructor 4


```

The compiler selects the constructor based on the **types and order** of the arguments. This is called **overload resolution**.

### `this(...)` — Constructor chaining

`this(...)` inside a constructor **delegates** to another constructor of the same class. It must be the **first statement** in the constructor body. This avoids code duplication.

### Constructor in inheritance: `super(...)`

When a subclass is constructed, the parent constructor must be called first:

```java


public class Personne {
    public String nom;
    public String prenom;

    public Personne(String nom, String prenom) {
        this.nom = nom;
        this.prenom = prenom;
    }
}

public class Employe extends Personne {
    private int idEmploye;

    public Employe(int idEmploye, String nom, String prenom) {
        super(nom, prenom);  // ← must be first: calls Personne constructor
        this.idEmploye = idEmploye;
    }
}


```

If you forget `super(...)`, Java will try to call a no-argument constructor on the parent — and fail if none exists.

---

## 6\. Encapsulation: Getters & Setters

Java convention: fields are `private`, accessed through `public` getter and setter methods. This is the principle of **encapsulation** — hiding internal state, exposing behavior.

Note that here that no explicit constructor are defined, so it will be:

- `new Employe()`

So attributes will be at **default values** ( `0` for `int`, `false` for `boolean`, `null` for `String`...)

```java


public class Employe {
    private Integer idInt;
    private String nom;
    private Double salaire;

    // Getter — returns the value
    public Integer getIdInt() {
        return idInt;
    }

    public String getNom() {
        return nom;
    }

    public Double getSalaire() {
        return salaire;
    }

    // Setter — sets the value (could include validation)
    public void setSalaire(Double salaire) {
        if (salaire < 0) throw new IllegalArgumentException("Salary cannot be negative");
        this.salaire = salaire;
    }
}


```

**Why not just use `public` fields?**

- You can add **validation logic** inside setters.
- You can make fields **read-only** (getter only, no setter).
- You can change the internal representation without breaking external code.
- Tools like serialization frameworks, ORM libraries, and IDEs rely on this convention.

---

## 7\. Inheritance, Virtual Dispatch & vtables

### 7.1 Inheritance basics

Java supports **single inheritance** for classes (a class can extend one parent), but **multiple inheritance** via interfaces.

```java


public class Personne {
    public String nom;
    public String prenom;

    public void demanderFormation(String nom_formation) {
        System.out.println("cette personne ne peut pas demander une formation car pas employe");
    }

    public int travailler() {
        return 0;
    }
}

public class Employe extends Personne {
    private int idEmploye;
    private int heures;
    private int salaire_horraire;

    @Override
    public void demanderFormation(String nom_formation) {
        System.out.println("l'employé: " + idEmploye + " " + nom +
                           " demande une formation: " + nom_formation);
    }

    @Override
    public int travailler() {
        return salaire_horraire * heures;
    }
}


```

### 7.2 Polymorphism: the reference type vs the actual type

One of Java's most powerful features:

```java


Personne empl2 = new Employe(2, "Stéphane", "Shu");


```

The **reference type** is `Personne`. The **actual object type** is `Employe`.

```java


Personne[] tableauObj = new Personne[]{ empl1, empl2 };

for (Personne pers : tableauObj) {
    System.out.println(pers); // calls Employe.toString() if pers is an Employe!
}


```

This is **polymorphism**: the method called depends on the **actual runtime type** of the object, not the declared type of the reference. This is called **dynamic dispatch** or **late binding**.

### 7.3 Virtual Dispatch & vtables

To implement dynamic dispatch efficiently, the JVM uses a structure called the **vtable** (virtual method table).

#### How vtables work

Every class has a vtable — a table of function pointers, one entry per virtual method. At runtime, calling a method on an object means:

1. Look at the object's header to find its vtable pointer (stored in the object's class word on the heap).
2. Index into the vtable to find the correct method implementation.
3. Call it.

```text


Object on Heap:
┌─────────────────────────────────┐
│ class word → vtable pointer     │  ← points to Employe's vtable in Metaspace
│ idEmploye: 2                    │
│ nom: "Stéphane"                 │
│ heures: 0                       │
└─────────────────────────────────┘

Employe vtable (in Metaspace):
┌──────────────────────────────────────────────┐
│ [0] toString()      → Employe.toString()     │
│ [1] demanderFormation() → Employe.demanderF  │
│ [2] travailler()    → Employe.travailler()   │
│ [3] equals()        → Object.equals()        │
│ [4] hashCode()      → Employe.hashCode()     │
└──────────────────────────────────────────────┘


```

If you had a plain `Personne` object, its vtable entry for `travailler()` would point to `Personne.travailler()` (returns 0). But for an `Employe`, it points to `Employe.travailler()` (computes the actual salary).

#### Java vs C++: virtual by default

In **C++**, methods are **non-virtual by default**. You must explicitly write `virtual` to enable dynamic dispatch. In **Java**, all instance methods are **virtual by default**. The `@Override` annotation does not change the dispatch mechanism — it just tells the compiler to verify that you are actually overriding something.

```cpp


// C++
class Personne {
public:
    void travailler() { ... }          // NOT virtual — static dispatch
    virtual void demanderFormation() { ... } // virtual — dynamic dispatch
};


```

```java


// Java — all methods are virtual
class Personne {
    public void travailler() { return 0; }         // virtual
    public void demanderFormation(String s) { ... } // virtual
}


```

This is why Java programs have slightly more overhead per method call than equivalent C++ code — every call goes through the vtable lookup. The JVM JIT compiler often **inlines** these calls when it can determine the actual type statically (called **devirtualization**), eliminating the overhead.

### 7.4 Upcasting and Downcasting

```java


// Upcasting (implicit, always safe):
Personne p = new Employe(1, "Paul", "Sho");

// Downcasting (explicit, may throw ClassCastException):
Employe e = (Employe) p;

// Safe pattern with instanceof check:
if (p instanceof Employe) {
    Employe e2 = (Employe) p;
}


```

When you store an `Employe` in a `Personne` reference, you **lose access** to `Employe`-specific methods like `set_info_salaire`. You need to downcast to get them back. The JVM verifies the cast at runtime.

---

## 8\. Overriding `toString()` — Why It Matters

Every class inherits `toString()` from `Object`. The default implementation returns something like `proj40.Employe@1b6d3586` — a class name and a hex hash code. **Not useful.**

Overriding it gives you meaningful debug output:

```java


// Personne:
@Override
public String toString() {
    return "nom: " + nom + " prenom: " + prenom;
}

// Employe extends Personne:
@Override
public String toString() {
    return super.toString() + " idEmploye: " + idEmploye;
    // → "nom: Paul prenom: Sho idEmploye: 1"
}


```

### Why `System.out.println` uses it

```java


System.out.println(empl1);


```

This compiles to:

```java


System.out.println(empl1.toString());


```

`PrintStream.println(Object o)` calls `String.valueOf(o)`, which calls `o.toString()`. Because `toString()` is virtual, the JVM dispatches to the most specific override — `Employe.toString()` if the object is an `Employe`, even if the reference type is `Personne`.

This means the for-loop:

```java


for (Personne pers : tableauObj) {
    System.out.println(pers);  // prints Employe representation for Employe objects
}


```

...correctly prints employee information even when iterating through a `Personne[]`, because dynamic dispatch applies to `toString()`.

### String concatenation also calls `toString()`

```java


"Employee: " + empl1   // calls empl1.toString() implicitly


```

The `+` operator on strings with an object argument calls `toString()` on the object. This is syntactic sugar for `StringBuilder.append(empl1.toString())`.

---

## 9\. Interfaces, Lambdas & Functional Programming

### 9.1 What is an interface?

An interface in Java defines a **contract**: a set of method signatures that any implementing class must provide. It does not contain instance data.

```java


public interface CalculSalaire {
    float calcul_salaire(int nb_hr, float tarif_hr);
}


```

Any class that implements `CalculSalaire` must provide a `calcul_salaire` method. This enables **programming to an abstraction**, not to a concrete implementation.

### 9.2 Implementing an interface

```java


public class CalculateurSimple implements CalculSalaire {
    @Override
    public float calcul_salaire(int nb_hr, float tarif_hr) {
        return nb_hr * tarif_hr;
    }
}

CalculSalaire calcul = new CalculateurSimple();
float sal = calcul.calcul_salaire(8, 25f); // 200.0


```

### 9.3 Anonymous Classes

Java allows you to create a **one-off implementation** of an interface inline, without declaring a named class. This is called an **anonymous class**:

```java


CalculSalaire calcul2 = new CalculSalaire() {  // creates an anonymous class
    @Override
    public float calcul_salaire(int nb, float sal) {
        return nb * sal;
    }
};


```

Under the hood, the compiler generates a hidden class file (e.g., `Proj111$1.class`) that implements `CalculSalaire`. This class has:

- A vtable entry for `calcul_salaire`
- An implicit reference to the enclosing scope (if it uses variables from the outer method — those must be effectively `final`)

Anonymous classes are the historical way of doing callbacks in Java. They are verbose but powerful.

### 9.4 Lambda Expressions

Since Java 8, **functional interfaces** (interfaces with exactly one abstract method) can be implemented using **lambda expressions** — a concise syntax that avoids the boilerplate of anonymous classes.

```java


// Verbose anonymous class:
CalculSalaire calcul2 = new CalculSalaire() {
    @Override
    public float calcul_salaire(int nb, float sal) {
        return nb * sal;
    }
};

// Equivalent lambda:
CalculSalaire calcul = (int nb_hr, float tarif_hr) -> nb_hr * tarif_hr;

// Or with type inference:
CalculSalaire calcul = (nb_hr, tarif_hr) -> nb_hr * tarif_hr;


```

The lambda `(nb_hr, tarif_hr) -> nb_hr * tarif_hr` is **technically an anonymous implementation** of the single abstract method of `CalculSalaire`. The compiler infers the parameter types from the interface definition.

**Lambda syntax:**

```text


(parameters) -> expression
(parameters) -> { statements; return value; }


```

**Single-expression lambdas** (like the one above) have an implicit `return`.

### 9.5 Method References

An even more concise form when the lambda just calls an existing method:

```java


// Lambda form:
clients.forEach(cl -> System.out.println(cl));

// Method reference form:
clients.forEach(System.out::println);

// Lambda:
clients.stream().mapToDouble(cl -> cl.getDepenses()).sum();

// Method reference:
clients.stream().mapToDouble(Client::getDepenses).sum();


```

`System.out::println` is a method reference to the `println` method of the `System.out` object.
`Client::getDepenses` is an instance method reference — for each `Client` in the stream, call `.getDepenses()`.

### 9.6 `@FunctionalInterface`

You can annotate an interface to declare it as functional:

```java


@FunctionalInterface
public interface CalculSalaire {
    float calcul_salaire(int nb_hr, float tarif_hr);
    // Adding a second abstract method would cause a compile error
}


```

This is optional but good practice — it makes intent clear and catches errors at compile time.

---

## 10\. Primitive Types vs Wrapper Classes

### 10.1 Primitives: lightweight and fast

Java has 8 primitive types that are **not objects**. They live directly on the stack (or inline in arrays/objects on the heap):



| Primitive | Size | Wrapper class |
| --- | --- | --- |
| <code>boolean</code> | 1 bit (JVM: 1 byte) | <code>Boolean</code> |
| <code>byte</code> | 8 bits | <code>Byte</code> |
| <code>short</code> | 16 bits | <code>Short</code> |
| <code>int</code> | 32 bits | <code>Integer</code> |
| <code>long</code> | 64 bits | <code>Long</code> |
| <code>float</code> | 32 bits | <code>Float</code> |
| <code>double</code> | 64 bits | <code>Double</code> |
| <code>char</code> | 16 bits (UTF-16) | <code>Character</code> |




A primitive `int` is just 4 bytes of raw data. No header, no vtable pointer, no GC overhead, but also no methods then.

So bare type, no fancy things.

### 10.2 Wrapper classes: objects with methods

`Integer`, `Double`, etc. are full Java objects. They wrap a primitive and add:

- Methods: `Integer.parseInt("42")`, `Integer.MAX_VALUE`, `.compareTo()`, `.hashCode()`
- Nullability: an `Integer` can be `null`, an `int` cannot
- Usability in collections: `List<Integer>` works, `List<int>` does not

```java


Integer idObj = 42;        // Object on heap, ~16 bytes + overhead
int idPrim = 42;           // 4 bytes on stack, no object, no GC


```

An `Integer` object on a 64-bit JVM takes approximately **16 bytes** just for the object header, plus 4 bytes for the int value — 4× heavier than the primitive.

### 10.3 Autoboxing and Unboxing

Java automatically converts between primitives and wrappers:

```java


Integer i = 5;         // autoboxing: int 5 → Integer object
int j = i;             // unboxing:  Integer object → int 5
Double d = 3.14;       // autoboxing
double e = d;          // unboxing


```

This is convenient but **has a cost**: every autoboxing creates a new object on the heap. In performance-critical loops, prefer primitives.

```java


// Inefficient — autoboxing in every iteration:
Double tot = 0.0;
for (Employe emp : tabl) {
    tot += emp.getSalaire();  // unboxes tot, adds, reboxes into new Double
}

// Efficient:
double tot = 0.0;
for (Employe emp : tabl) {
    tot += emp.getSalaire();  // pure primitive arithmetic
}


```

### 10.4 `==` vs `.equals()` — a critical trap

```java


Integer a = 1000;
Integer b = 1000;
System.out.println(a == b);      // false! Different objects on heap
System.out.println(a.equals(b)); // true  — value comparison


```

**`==` on objects compares references (addresses), not values.** Always use `.equals()` for value comparison of wrapper types.

Note: Java caches `Integer` objects for values -128 to 127, so `Integer a = 127; Integer b = 127; a == b` is `true` — but this is an implementation detail you should never rely on.

---

## 11\. Comparators as Objects — Everything is a Class

One of the most instructive examples that "everything is a class" in Java is `Comparator`.

### 11.1 What is a Comparator?

`Comparator<T>` is an **interface** with a single abstract method:

```java


public interface Comparator<T> {
    int compare(T o1, T o2);
    // returns negative if o1 < o2, 0 if equal, positive if o1 > o2
}


```

`Collections.sort()` takes a `List` and a `Comparator`. You define _how_ to compare, and the sorting algorithm uses it.

### 11.2 Overriding the comparator method with an anonymous class

```java


Collections.sort(tabl, new Comparator<Employe>() {
    @Override
    public int compare(Employe e1, Employe e2) {
        return e1.getSalaire().compareTo(e2.getSalaire());
    }
});


```

This creates an anonymous class that implements `Comparator<Employe>`. The `compare` method is overridden to compare by salary. The anonymous class object is passed to `sort`, which calls `compare(a, b)` on every pair during sorting.

You can sort by different criteria by creating different comparators:

```java


// Sort by salary:
Collections.sort(tabl, new Comparator<Employe>() {
    @Override
    public int compare(Employe e1, Employe e2) {
        return e1.getSalaire().compareTo(e2.getSalaire());
    }
});

// Sort by name:
Collections.sort(tabl, new Comparator<Employe>() {
    @Override
    public int compare(Employe e1, Employe e2) {
        return e1.getNom().compareTo(e2.getNom());
    }
});


```

With lambdas (since `Comparator` is a functional interface):

```java


Collections.sort(tabl, (e1, e2) -> e1.getSalaire().compareTo(e2.getSalaire()));

// Or even more concise:
tabl.sort(Comparator.comparingDouble(Employe::getSalaire));


```

### 11.3 `equals()` and `hashCode()` — the contract

When using objects in `HashSet` or as `HashMap` keys, Java needs two methods:

- `hashCode()` — returns an integer "bucket number"
- `equals()` — confirms two objects are actually equal

**Contract:** if `a.equals(b)` then `a.hashCode() == b.hashCode()`.

```java


@Override
public boolean equals(Object o) {
    if (o == null || getClass() != o.getClass()) return false;
    if (this == o) return true;
    Employe employe = (Employe) o;
    return idInt.equals(employe.idInt);  // equal if same ID
}

@Override
public int hashCode() {
    return idInt.hashCode();
}


```

Without overriding these, `HashSet` would consider two `Employe` objects with the same ID as different elements:

```java


Set<Employe> setEmployes = new HashSet<>(tabl2);
System.out.println("Size list: " + tabl2.size()); // 6 (with duplicate)
System.out.println("Size set: " + setEmployes.size());  // 5 (duplicate removed)


```

The `HashSet` uses `hashCode()` to find the bucket and `equals()` to detect the duplicate.

---

## 12\. Collections, Maps & Sets

Java's `java.util` package provides a rich collection framework.

### 12.1 `List` vs Array

```java


Integer[] tab = new Integer[]{1, 2, 3};      // fixed size, low-level
List<Integer> lst = Arrays.asList(tab);       // fixed-size List view
List<Integer> lst2 = new ArrayList<>(Arrays.asList(tab)); // resizable


```

- An array ( `T[]`) is a primitive construct: fixed size, stored contiguously on the heap.
- `List<T>` is an interface. `ArrayList<T>` is a resizable implementation backed by an array.
- `Arrays.asList()` returns a **fixed-size** list (backed directly by the array). Calling `.add()` on it throws `UnsupportedOperationException`.

### 12.2 `Map` — key-value store

```java


Map<Integer, Employe> mp = new HashMap<>();
mp.put(emp1.getIdInt(), emp1);
mp.put(emp2.getIdInt(), emp2);

Employe found = mp.get(3);  // O(1) lookup by ID


```

`HashMap` uses `hashCode()` to find the bucket and `equals()` to resolve collisions. This is why overriding both correctly is critical when using objects as keys.

### 12.3 `Set` — no duplicates

```java


Set<Employe> setEmployes = new HashSet<>(tabl2);


```

`HashSet` is backed by a `HashMap`. It stores elements as keys with a dummy value. Duplicate detection uses `hashCode()` \+ `equals()`.

---

## 13\. The Stream API

The Stream API (Java 8+) allows processing collections in a **declarative, functional style** — describing _what_ to compute, not _how_.

### 13.1 Reading a CSV and building a List with streams

```java


clients = reader.lines()
    .skip(1)                            // skip header line
    .map(line -> line.split(","))       // each line → String[]
    .map(data -> new Client(            // String[] → Client object
        Integer.parseInt(data[0]),
        data[1],
        data[2],
        Integer.parseInt(data[3]),
        Float.parseFloat(data[4])
    ))
    .collect(Collectors.toList());      // terminate stream → List<Client>


```

This is a **pipeline**: each operation returns a new stream. Nothing is executed until a **terminal operation** ( `collect`, `sum`, `forEach`, etc.) is called.

Whole code is:

```java



       List<Client> clients;

        try (
            InputStream is = JavaApplication12.class
                    .getClassLoader()
                    .getResourceAsStream("ressources/Clients.csv");
            BufferedReader reader = new BufferedReader(new InputStreamReader(is))
        ) {
            if (is == null) {
                System.out.println("Fichier introuvable !");
                return;
            }

            // On assigne directement à la liste
            clients = reader.lines()
                    .skip(1) // ignore l'en-tête
                    .map(line -> line.split(","))
                    .map(data -> new Client(
                            Integer.parseInt(data[0]),
                            data[1],
                            data[2],
                            Integer.parseInt(data[3]),
                            Float.parseFloat(data[4])
                    ))
                    .collect(Collectors.toList());

        } catch (IOException e) {
            e.printStackTrace();
            return;
        }



```

### 13.2 Pipeline structure

```text


Source            Intermediate ops (lazy)           Terminal op (eager)
 ──────     ─────────────────────────────────────     ──────────────────
 .stream()  .filter()  .map()  .sorted()  .limit()    .collect()
                                                       .forEach()
                                                       .sum()
                                                       .count()
                                                       .max()
                                                       .average()


```

**Lazy evaluation**: intermediate operations are not executed until a terminal operation forces them. This allows optimizations like short-circuiting.

### 13.3 `forEach` vs `stream().forEach()`

```java


clients.forEach(System.out::println);          // direct Iterable.forEach
clients.stream().forEach(System.out::println); // same result via stream


```

For simple iteration, `forEach` directly on the list is equivalent. The stream version is useful when you want to combine with filtering, mapping, etc.

### 13.4 `mapToDouble` and numeric streams

```java


double totalDepenses = clients.stream()
    .mapToDouble(cl -> cl.getDepenses())
    .sum();

// Equivalent using method reference:
double totalDepenses = clients.stream()
    .mapToDouble(Client::getDepenses)
    .sum();


```

`.mapToDouble()` returns a `DoubleStream` — a specialized stream for `double` values that provides `.sum()`, `.average()`, `.min()`, `.max()` directly, without boxing overhead.

Similarly: `.mapToInt()` → `IntStream`, `.mapToLong()` → `LongStream`.

### 13.5 `max()` — a special filter

```java


Client maxClient = clients.stream()
    .max(Comparator.comparingDouble(cl -> cl.getDepenses()))
    .get();

// Or with method reference:
Client maxClient2 = clients.stream()
    .max(Comparator.comparingDouble(Client::getDepenses))
    .orElse(null);


```

`max()` takes a `Comparator` and returns an `Optional<T>`. It is internally a special **reduction**: it applies the comparator to find the maximum element. `.orElse(null)` safely handles an empty stream.

`Optional<T>` is a container that may or may not contain a value. It forces you to handle the "no result" case explicitly, avoiding `NullPointerException`.

### 13.6 `collect()` — the terminal collector

`collect()` is the most powerful terminal operation. It takes a `Collector` that describes how to accumulate results.

**Common collectors:**

```java


// To a List:
List<Client> result = stream.collect(Collectors.toList());

// To a Set:
Set<Client> result = stream.collect(Collectors.toSet());

// Group by city, summing expenses:
Map<String, Double> depensesParVille = clients.stream()
    .collect(Collectors.groupingBy(
        Client::getVille,                       // key extractor
        Collectors.summingDouble(Client::getDepenses)  // value aggregation
    ));


```

`Collectors.groupingBy()` creates a `HashMap` on the fly, grouping elements by a key function and applying a downstream collector to each group. This replaces the verbose imperative loop:

```java


// Imperative version (equivalent):
Map<String, Double> depensesParVille = new HashMap<>();
for (Client cl : clients) {
    String ville = cl.getVille();
    double dep = cl.getDepenses();
    if (depensesParVille.containsKey(ville)) {
        depensesParVille.put(ville, depensesParVille.get(ville) + dep);
    } else {
        depensesParVille.put(ville, dep);
    }
}


```

Both produce the same result. The stream version is more **declarative** and composable.

### 13.7 `average()` — a collector returning Optional

```java


double meanAge = clients
    .stream()
    .mapToInt(cl -> cl.getAge())
    .average()       // returns OptionalDouble
    .orElse(0);      // default if stream is empty


```

`.average()` is a terminal operation on `IntStream`/ `DoubleStream` that returns an `OptionalDouble`. The `.orElse(0)` provides a fallback for the empty stream case.

### 13.8 Iterating over a Map

```java


// Using forEach on Map with a BiConsumer lambda:
depensesParVille.forEach((ville, total) ->
    System.out.println(ville + " : " + total)
);


```

`Map.forEach()` takes a `BiConsumer<K, V>` — a functional interface with two parameters. The lambda `(ville, total) -> ...` is the implementation.

---

## 14\. Type Inference in Java

Java has progressively added more type inference. Understanding where the compiler can infer types saves boilerplate without sacrificing safety.

### 14.1 Lambda parameter inference

When a lambda implements a known functional interface, the compiler knows the parameter types from the interface definition:

```java


// Interface:
public interface CalculSalaire {
    float calcul_salaire(int nb_hr, float tarif_hr);
}

// Explicit types (redundant but valid):
CalculSalaire calcul = (int nb_hr, float tarif_hr) -> nb_hr * tarif_hr;

// Inferred types (compiler knows from CalculSalaire):
CalculSalaire calcul = (nb_hr, tarif_hr) -> nb_hr * tarif_hr;


```

The compiler sees that `calcul_salaire` takes `int` and `float`, so it infers the lambda parameters are `int nb_hr` and `float tarif_hr`.

### 14.2 Generic type inference

```java


// Without inference (verbose):
List<Employe> tabl = new ArrayList<Employe>();

// With diamond operator (Java 7+):
List<Employe> tabl = new ArrayList<>();  // <> infers Employe from left side


```

### 14.3 `var` (Java 10+)

```java


var clients = new ArrayList<Client>();   // compiler infers ArrayList<Client>
var total = 0.0;                         // compiler infers double
var stream = clients.stream();           // compiler infers Stream<Client>


```

`var` only works for **local variables** (not fields, parameters, or return types). The type is still static — it's determined at compile time, not runtime.

### 14.4 Stream and Comparator inference

```java


clients.stream()
    .max(Comparator.comparingDouble(Client::getDepenses))
    // Comparator.comparingDouble infers Comparator<Client> from context


```

The compiler chains inference across multiple generic method calls. This is why the stream API code can be so concise without sacrificing type safety.

---

## 15\. Summary Diagram

```text


┌─────────────────────────────────────────────────────────┐
│                    JVM MEMORY LAYOUT                    │
├─────────────┬────────────────────────┬──────────────────┤
│    STACK    │         HEAP           │    METASPACE      │
│  (per thread)│       (shared GC)     │  (class metadata) │
├─────────────┼────────────────────────┼──────────────────┤
│ int a = 10  │ new Employe(...)       │ class Employe {}  │
│ String ref→─┼→ "hello" String object │ class Personne {} │
│ call frames │ new int[]{1,2,3}       │ vtables           │
│ local vars  │ ArrayList<Client>      │ static fields     │
│             │                        │ bytecode          │
├─────────────┼────────────────────────┼──────────────────┤
│ StackOverflow│ OutOfMemoryError:     │ OutOfMemoryError: │
│   Error     │  Java heap space       │   Metaspace       │
└─────────────┴────────────────────────┴──────────────────┘

Object on Heap:
┌─────────────────────────────────────────┐
│ class word ──→ vtable (in Metaspace)    │
│ field: idEmploye = 1                    │
│ field: nom = ref ──→ "Paul" (Heap)      │
│ field: salaire = 2000.0                 │
└─────────────────────────────────────────┘

vtable (in Metaspace):
┌─────────────────────────────────────────┐
│ toString()         → Employe.toString() │
│ equals()           → Employe.equals()   │
│ hashCode()         → Employe.hashCode() │
│ demanderFormation()→ Employe.demanderF. │
│ travailler()       → Employe.travailler │
└─────────────────────────────────────────┘


```

### Key Principles to Remember

- Every executable statement lives inside a class — always.
- Objects live on the **Heap**, references live on the **Stack**, class descriptions live in **Metaspace**.
- `static` means **class-level** — no instance needed, exists once.
- All instance methods are **virtual by default** — dynamic dispatch via vtable.
- Override `toString()`, `equals()`, and `hashCode()` whenever it matters for your class semantics.
- Prefer `int` over `Integer` when you don't need nullability or collection use — it's 4× cheaper.
- Lambdas are syntactic sugar for anonymous classes implementing a functional interface.
- The Stream API is lazy — it only executes when a terminal operation is called.
- `Comparator`, `Collector`, `Consumer` — everything is an interface; everything can be overridden.

---

_Article written as a technical reference for Java learners with a background in C/C++._