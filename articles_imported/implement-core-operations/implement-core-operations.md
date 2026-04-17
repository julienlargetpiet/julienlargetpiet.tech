I have just finished developing a library for manipulating numbers so large and/or precise that no conventional datatype can encode them.

You can find this library there:

[repo](https://github.com/julienlargetpiet/cherubin)

Or download on this website as zip:

[zip](/assets/common_files/cherubin.zip)

-Ok so if even a `long unsigned int`, `double`... can't represent my number, how do I? I'm not going to use `vecteur`, see a `deque`?

In fact, if one is obliged, but it requires the complete reimplementation from zero of the fundamental operators ( `+`, `-`, `*`, `/`, `%%`, `!`, `exp(x)`, `log(x)`...) taking into account the data structure with which we work.

# Addition

For example, we do the addition and then we can do the multiplication and division.

Example `"12" * "0.4" = "12" + "12" + "12" + "12"` then we moove the comma...

Also, `"5" / "2"` equals to how many times can I put `2` in `5`, and then how many times can I put `0.2` in `5` `-` (the number of times i have put `2` in `5` `* 2`).

From here it is not so complicated to make the whole powers as well as the factorials. Good still think about optimizing everything in the code but it would be too long to talk about it here.

# Floating exponants

\- Ok but logarithms and non-integer exponents, exponential??

At this stage, i'm armed with `addition`, `substraction`, `multiplication`, `division`, `positive int exponants`, `quotient`, `remainder` and `factorial`. So I want something that draws from these tools and gives me the result of an exponential for example.

# Exponential

At this point we've got 3 methods, either the formula `(1 + x/n) ^ n`, where when `n` increases, the result is precise, check this article: [https://betterexplained.com/articles/an-intuitive-guide-to-exponential-functions-e](https://betterexplained.com/articles/an-intuitive-guide-to-exponential-functions-e)

Or, we say that calculate exponential of `x` is the same as calculate `2.71...` to the power of `x`, so we don't fix the problem but we merge 2. (calculate a number with a floating exponant).

Or, we can use the `Taylor series` for the exponential that converges for all `x`.

In short, the `Taylor serie` is a method where we will approximate a function via a polynomial. The polynomial can technically be of an infinite degree (if the basic function can be derived to infinity) because it is made with the addition of derivatives from the base function.

Usually, the polynmial constant vary according to where we center `x` but since that for `exp(x)`, its `Taylor serie` converges everywhere, we'll simply search for its constant for `x = 0` and then the polynomial will be valid everywhere.

Watch this video for more informations: [https://www.youtube.com/watch?v=3d6DsjIBzJ4](https://www.youtube.com/watch?v=3d6DsjIBzJ4)

In summary for `exp(x)`, we got:

`1 + constante1*x^1/1! +constante2* x^2/2! + constante3*x^3/3! + ... `

=\>

`1 + x^1/1! + x^2/2! + x^3/3! + ... `

# Logarithm

Ok, now the `logarithm`.

\- Look `log(225) / log(15) = 2`\- Also, `log(2^8) / log(2) = 8`Let's take `x = 309` to find `log(x)` with `base = exp(1)` We will multiply our `base` with `original base` until the resultt is superior to `x`.

- `exp(1) * exp(1)` with `P = 1`
- `exp(2) * exp(1)` with `P = 2`
- `...`

After that, we got the integer part of `log(x)`.

Here we can say that the starting `x` is also `exp(log(158))` and we know that the found integer part `P` tells us that `exp(P) <= 309 <= exp(P + 1)`.

So we do `x / exp(P) `

Because `exp(n + 1) / exp(n)` is in fact `2.71... ^ n+1 / 2.71... ^ n` so just `2.71... = exp(1)` we know that the decimal part of the result is between `0` and `exp(1)`

Good, but i want between `0` and `1`. Strange, does a tool that proportionally converts a value between `0` and `2.71`... and `0` and `1` exist?

Yes, it is the `log`!

\- But i won't use a `log` to calculate another `log` right?

Don't worry it's just a `log` between `0` and `exp(1)` instead of `log(huge value)`.

In the example, the integer part is `5` and the decimal part is equal to `log(309 / exp(5)) = 0.7334...`

Yes `log(309)` is equal to `5.7334...`

Now, the non-integer exponants.

Just `x^d = exp(X)`

which is the same as `X = log(x) * d`

We know how to calculate the `logarithm`, the `exponential`, done.

-Eh not totaly!

What?

 -If i want to calculate `5^(-5.9)` :) ?

Yes, it is simply `1 / 5^5.9`

Also, i really have to create a global `inverse` function.

I'm not going to do an `inverse function` for each operation, i'm going to create an `inverse function` and then pass as a parameter the `function` from which i want the `inverse`.

Great, now i can know something that i've never asked myself such as `factorial of 1203`

```

110291182274320302868335540036971957964398761049288945189514522265495848012966079388748606697973923857953863340967082130666006801995552084113814868238243311858913795154784617153902296146662261034010473803827569767538493678138342890947302327880659767989629372970546995369789051829636976020229377210033943230084516335699249033857428772315591104623952693868236895725991085709158040233167679112351936991424971264582253948780887379967819939333395587783920859359861012157863588005375328833992235770831819662357991853643303111244309326324373091074509115218770474031745001085058150484834220026432804625434128103617316002317240235816361436134297139959662483729719647267876280118259712947551023653444555174490944979196787361320691724054489811739772152714191015590466907891601064590715046011898180534740537300129250803125492992577415551304378939332611237562776293561035832294489499225804565027267569023949255161282391174997210303446793139678706808650493259713137854061821137461397796722386790250701776810015961428197556815751881087003157545471521009580843663460817191196050241064752581934463558830010132138518790930470384585398937993248316524232578527264460878228840418064555725329100375022428626309365502567689206415068383514463527804702179358835752389190241844166925965937482139489983646084680324516474595845898026896254328710351184166557725020369476995517380367529937617113231359792819905104507614147780421528883484133295052608745099678446222414535404890949882402139712822530829693616183501644591032729707298565386443307563497032672316273198489049829030913715144490221271583537916723475841857831273842405894134590613795155682863064577984556748493737206351932583104172335734280226763088742592195979407131112600953429663256089713211540343880345163689494478845964979135658780819094129142572035559733121669788156352259750384591475246232016769075079376829857776400589333076596715030915886442811852204991104123222836145828125630564312184996547014552284493145574519304072039703973936965896586108737637067695497470660389631858282834386074427079639087770744487891233683053513892666630403886028137795177406237525249875396197418728093989786482185147005153853264518939124417226373486941967057099550815354237514275032081881610961521996825319734630187988769835736334129937206125352211558436128168257565762561098798685898910181724217378427847755791561092496954234588923027413794716484601714639867544884155288670222887376305424677401569213422442327166342634374955584061782891358081777309625180826661062844058991327824113050412205823174208534851051558677681043793002218008919992212282871525955992706178455492690945449945439208089933822268665877269583213533003120330908157497449182538729547002189479274597896996222446035150842524951733342788124468436353810664498768586798231949004761871215217176571499053572447150628068308187071772821239484551881596985264424435373729446965693122971789819834691063207833724791029760000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000

```

Done.