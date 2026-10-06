
This article is about several mathematical puzzles which will sharpen your reasoning.

There will be several well-known ones, such as the Monty Hall problem, but also lesser-known ones, such as the mechanical scale and the balls.

Each answer will be detailed.

## The lake and the water lily

We have a lake and some water lilies on it.

We know that the number of water lilies doubles every day and that on the 48th day, half of the lake is covered by water lilies.

```
-----------
|XXXXX     |
|XXXXX     |
|XXXXX     |
-----------

```

Now the question is: on which day will the lake be fully covered by water lilies?

The reasoning is simple, indeed we know that each water lily doubles within a day.

Also, doubling half of something gives you the whole thing.

Therefore, the answer is the next day, the 49th day.

## The chair machines 

This one is trickier because it requires us to take a risk by making the simplest assumption, and, as we know, making a problem more difficult than it really is can be more appealing than reducing it to a simple form.

We have 5 machines that produce 5 chairs in 5 minutes, and the question is in how many minutes 100 machines will produce 100 chairs ?

The reasoning is the following. 

The tricky part is that we can easily think that we don't have the necessary information.

Indeed the crucial question is:

**Are the machines identical ?**

And as written before we have to implicitly answer in the affirmative because it makes the problem simple.

If all machines are identical, then we can assume that each machine produces 1 chair.

And if it can produce a chair on its own, then if we have 5 machines and 5 chairs to produce, then we can think that each machine produce 1 chair because otherwise, one or more machines wouldn't be used.

So we have:

```

Machine 1 -> Chair 
Machine 2 -> Chair 
Machine 3 -> Chair 
Machine 4 -> Chair 
Machine 5 -> Chair 

```

This is a one-to-one mapping.

And we know that the entire process takes 5 minutes, so it's the same as saying that a machine takes 5 minutes to produce a chair.

For the question:

**How much time will it take for 100 machines to produce 100 chairs?**

We also can make a one-to-one mapping.

Therefore, the answer is 5 minutes.

If the question were:

**How much time will it take for 100 machines to produce 200 chairs?**

It would then take 10 minutes, because each machine produces 2 chairs, so it takes 5 minutes times 2 -> 10 minutes.

It would also take 10 minutes if the same 100 machines had to produce 101 chairs.

Indeed, at the end of the first 100 chairs production, one machine will be assigned to produce a second chair.

Then, the entire process would take 10 minutes.

## The mechanical scale and the balls

We have 9 visually identical balls.

They all weigh the same, except for one that is slightly heavier than the others

We can't detect which one by just lifting it, we have to use a scale.

The only scale we have is a balance scale, meaning we can compare the weights of two objects or groups of objects.

And the question is:

**What is the minimum number of weighings needed to be sure to identify the heavier ball?**

If we're lucky, we can find it on the first weighing, but here we want to be sure to identify it, not merely have a chance of doing so.

By the way, the probability of detecting the heavier ball at a given weighing is:

$$
\begin{aligned}
f(n)=
\begin{cases}
\dfrac{1}{9-2n}+\dfrac{1}{8-2n}, & n\in[0,3],\\[6pt]
1, & n\in[4,+\infty).
\end{cases}
\end{aligned}
$$

where `n` is the weighing number.

So what do we do ?

We might think that the answer is 8, by weighing the same ball against each of the other 8 balls.

But this is far from optimal.

First, we have to explicitly formulate what happens at each weighing.

We have 3 different outputs.

- The left ball is heavier

- The right ball is heavier

- Neither, so the heavier ball is in the untested balls

Also, nothing prevents us from weighing one group of balls against another..

And what do we notice from the number `9` ?

It's divisible by 3 and `9 / 3 = 3` which is exactly the number of possible outcomes.

So what we can do is randomly form 3 groups of 3 balls, then randomly take two groups and weigh them against each other..

Now, either the groups have the same weight, meaning the heavier ball is still in the last untested group, or one of the weighed groups is heavier, meaning that the heavier ball is in the heavier group.

Whatever the result is, we randomly weigh 2 balls belonging to the heavier group.

And it is this last weighing that will tell us which ball is heavier.

Indeed, it is either the left one, the right one, or the untested one.

So we can be sure to identify the heavier ball with just 2 weighings.

## The right-handed people

We have a room of 100 people.

99 are right-handed and 1 is left-handed.

The question is:

**How many people must leave, and who, to bring the percentage of right-handed people down to 98%?**

Again, here we have to visualize the problem.

So the room is:

```

LRRRRRRRRR -
RRRRRRRRRR  |
RRRRRRRRRR  |
RRRRRRRRRR  |
RRRRRRRRRR  |
RRRRRRRRRR  |--100 people
RRRRRRRRRR  |
RRRRRRRRRR  |
RRRRRRRRRR  |
RRRRRRRRRR -

```

- `R` -> right-handed

- `L` -> left-handed

So at first, we know that 99% of the people in the room are right-handed.

Only right-handed people must leave to lower the right-handed percentage.

Good, we've half-answered the question, but now the tricky part is how many right-handed people must leave?

For this problem I like to think of it this way.

If 99% of the people are right-handed and that we want to bring this percentage to 98%, it means that we want to double the proportion of left-handed in the room.

So no more `1/100`, but `2/100`, but we cannot bring another left-handed person into the room, so how can we represent `2/100` with a numerator of `1` ?

That's just `1/50` !

Therefore, 50 right-handed must leave.

Indeed, there is now 50 people, 49 right-handed and 1 left-handed.

## The poisoned wine bottle

We have 1000 wine bottles, and one is potentially poisoned.

We also have several scientists who work one after the other to detect the poisoned bottle.

The first one can test 999 bottles, the second, 499, the third, 249 and so on.

So each scientist can test:

$$
\begin{aligned}
f(n)=
\begin{cases}
\dfrac{n+1}{2}-1, & \text{if } (n+1)\bmod 2 = 0, \\[6pt]
\left\lfloor \dfrac{n+1}{2}-1 \right\rfloor, & \text{otherwise.}
\end{cases}
\end{aligned}
$$

When they hand over to the next scientist, they can only tell their `(n + 1) / 2` tested bottles to the next scientist.

Hence, the first scientist can tell half plus one of its tested bottles (`(999 + 1) / 2 = 500`), the second can also tell the third scientist half plus one of its tested bottles (`(499 + 1) / 2 = 250`) plus the previously tested bottles (`500`) and so on.

The question is the following:

**With how many scientists can we be sure to detect whether the stock contains a poisoned bottle?**

We can translate tto the following question:

**How many scientists do we need to be sure that all the bottles are tested?**

Again, the trick is just to see that each new scientist has to test approximately half as many bottles as the previous scientist.

And the `-1` in this formula:

```

(n + 1) / 2 - 1

```

Is just to be sure that before a certain number of scientists, the potentially poisoned bottle remains untested.

The trick is to make a good enough model.

So we can model it this way:

$$
\begin{aligned}
f(scientist) = 1000 / 2^{scientist}
\end{aligned}
$$

This is not an exact model because it does not exactly reproduce the algorithm but it should at least return the good result.

So we just have to find the smallest value of `scientist` such that:

$$
\begin{aligned}
2^{scientist} >= 1000
\end{aligned}
$$

And the anwser is `10`, indeed `2^10 = 1024`.

We can verify the answer with this Python script:

```python

from math import floor

v = 999
cnt = 1

while v > 1:
    if (v + 1) % 2 == 0:
        v = (v + 1) / 2 - 1
    else:
        v = floor((v + 1) / 2)
    cnt += 1
    print(cnt, v)

```

Output:

```

2 499.0
3 249.0
4 124.0
5 62
6 31
7 15.0
8 7.0
9 3.0
10 1.0

```

The same logic applies if we have a different number of bottles.

For example, with `2000` bottles, the answer would be `11` (because `2^11 = 2048`).

We can test it:

```python

from math import floor

v = 1999
cnt = 1

while v > 1:
    if (v + 1) % 2 == 0:
        v = (v + 1) / 2 - 1
    else:
        v = floor((v + 1) / 2)
    cnt += 1
    print(cnt, v)

```

Output:

```

2 999.0
3 499.0
4 249.0
5 124.0
6 62
7 31
8 15.0
9 7.0
10 3.0
11 1.0

```

## The Monty Hall problem

You are surely familiar with this problem, but here's an explanation that should make it click.

So you participate in a TV show, there are 3 doors.

Behind two of them are goats, while behind the other is a Ferrari.

You want the Ferrari (what a weirdo).

So at first you randomly choose a door among the 3.

At this point you obviously have a one-in-three chance to have chosen the right door.

```

  F
 /
/
---G
\
 \
  G

```

Once you have chosen a door, the host opens another door behind which there is a goat and asks you if you want to switch to the other door.

Now the question is simply:

**Would you switch doors?**

you might say that it doesn't matter because you have 1 chance over 2 of having chosen the right door.

But wait, let's try to visualize the problem.

In fact, we have:

```
      /G
     F
    / \F 
   /   
  /   
 /     F
/     / 
-----G
\     \
 \     G
  \    
   \   F
    \ /
     G
      \G


```

So we have to think about it this way:

If we have chosen the wrong door, which we have a 2/3 chance of doing, then switching doors is the optimal choice because, in `2/3` of cases, we end up choosing the correct door.

## The tails problem

I have a fair coin that I launch 4 times, what is the probability to have exactly 3 tails ?

It's possible to visualize the outcomes in a probability tree but a bit difficult because there is `2^4 = 16` branches.

So the thing is just to visualize the branches that have exactly 3 tails:

```

T-T-T-H
H-T-T-T
T-H-T-T
T-T-H-T

```

The number of such outcomes is given by the binomial coefficient:

$$
\begin{aligned}
\binom{4}{3}
=
\frac{4!}{3!(4-3)!}
\end{aligned}
$$

So the answer is `4 / 16 = 1 / 4`.

By the way, the probability of a branch can be formally expressed as:

$$
\begin{aligned}
p^k \cdot (1-p)^{n-k}
&= (0.5)^3 \cdot (0.5)^1 \\
&= 0.0625
\end{aligned}
$$

And there is 4 branches so that's 

```

0.125 * 4 = 0.25

```

## Conclusion

Hope this article was usefull ;)

























