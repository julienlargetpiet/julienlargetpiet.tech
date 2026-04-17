# 🦀 Metaprogramming in Rust: Exploring `macro_rules!` Power

Rust offers one of the most expressive and hygienic metaprogramming systems in modern languages.
Through **declarative macros** ( `macro_rules!`), we can generate functions, handle code repetition, and even emulate control-flow constructs — all at compile time.

In this article, we’ll explore **Rust metaprogramming** from basic macro pattern matching to complex variadic patterns and custom control structures — step by step, with working examples.

## 1\. Macro Pattern Matching and Expression Types

```rust



macro_rules! macr {
    () => {
        println!("Check out my macro!");
    };
    ($name:ident) => {
        println!("Hello, {}!", stringify!($name));
    };
    ($val:expr, $val2:expr) => {
        println!("2: {}, {}", $val, $val2);
    };
    ($val:expr) => {
        println!("3: {}", $val);
    };
}

fn main() {
    macr!();
    macr!(7777);
    macr!(7777, 8888);
    macr!(Alice);
}
```

### Output

```

Check out my macro!
3: 7777
2: 7777, 8888
Hello, Alice!


```

## 2\. Creating Functions Dynamically

```rust


macro_rules! fun_macr {
    ($x:ident, $x2:ty) => {
        fn $x(i: $x2) {
            println!("Evaluation: {}", i);
        }
    };
    ($x:expr) => {
        fn fun_func() {
            $x
        }
    };
    ($x:tt, $x2:ty, $x3:tt) => {
        fn fun_func2(_i: $x2) {
            println!("{}", $x + $x3)
        }
    };
}

fn main() {
    fun_macr!(foo, i32);
    foo(23);

    fun_macr!(println!("fun_func lool"));
    fun_func();

    fun_macr!(11, i32, 22);
    fun_func2(222);
}
```

### Output

```
  Evaluation: 23
fun_func lool
33
```

## 3\. Variadic Arguments in Macros

```rust


macro_rules! variadic_args1 {
    ($($x:expr),*) => {
        $( println!("arg: {}", $x); )*
    }
}

fn main() {
    variadic_args1!(
        1,
        2,
        3,
        if 1 > 0 { false } else { true },
        {"Hi"},
        "OOO"
    );
}
```

#### Output

```
arg: 1
arg: 2
arg: 3
arg: false
arg: Hi
arg: OOO
```

## 4\. Variadic Function Creation

```rust


macro_rules! variadic_args2 {
    ($($x:ident),*) => {
        $(
            fn $x(i: i32) {
                println!("Evaluation: {} {}", i, stringify!($x));
            }
        )*
    };
    ($($x:expr),*) => {
        $(
            println!("Evaluation2: {}", stringify!($x));
        )*
    };
}

fn main() {
    variadic_args2!(fun1, fun2);
    fun1(13);
    fun2(51);

    variadic_args2!(22 + 1, 33 + 1);
}
```

#### Output

```

Evaluation: 13 fun1
Evaluation: 51 fun2
Evaluation2: 22 + 1
Evaluation2: 33 + 1
```

## 5\. Executing Code Blocks

```rust


macro_rules! block_macr {
    ($x:block) => {
        $x
    }
}

fn main() {
    block_macr!({ println!("Ok") });

    block_macr!({
        if 1 > 0 {
            println!("{}", false);
        } else {
            println!("{}", true);
        }
    });
}
```

### Output

```
Ok
false
```

## 6\. Custom Match Implementation

```rust


macro_rules! minimal_match {
    ($result:expr => { $( $cmp_rslt:expr => $code_exec:block ),* }.$default_code:block) => {
        let x = $result;
        let mut alrd: bool = false;
        $( if x == $cmp_rslt { alrd = true; $code_exec } )*
        if !alrd {
            $default_code
        }
    }
}
```

### Example Usage

```rust


  fn main() {
    minimal_match!(
        2 - 1 => {
            1 => { println!("rslt 1") },
            1 => { println!("rslt 2") },
            3 => { println!("rslt 3") },
            0 => {
                let a = 1;
                println!("ok 0 {}", a)
            }
        }.{
            eprintln!("Something went wrong lol");
        }
    );
}
```

### Output

```
rslt 1
rslt 2
```

## Conclusion

Metaprogramming in Rust via `macro_rules!` blends **power**, **safety**, and **clarity**. Unlike C/C++ preprocessor macros, Rust macros expand into syntactically valid Rust code that the compiler checks **after expansion**, ensuring type safety and hygiene.