# sutom
A way to cheat at SUTOM (the hard way). Because writing this program was more
fun than playing [SUTOM](https://sutom.nocle.fr/) :P

## How to cheat

That's all good, but how do I cheat??

Well, at the very start, just call `sutom/sutom.py` (or `sutom.py` relatively
to wherever you are and wherever you cloned/installed it).

Like so:
```sh
$ sutom/sutom.py
usage: sutom.py [-h] [-n LETTERS] [-m PATTERN] SEARCH PATTERN with dots
sutom.py: error: the following arguments are required: SEARCH PATTERN with dots
$ _
```
Now, as you can see, you get an error message, informing you that an argument
is missing: the "search pattern with dots".

Let's assume you are playing with the following SUTOM grid:

![Empty SUTOM grid with the pattern "P......"](README_imgs/sutom1.png)

All you have to start with is literally using `P......` as the parameter:

```sh
$ sutom/sutom.py P......
PARIEES (0.5766549868917589)
$ _
```

And then, input that word in the grid, and validate. Let's assume now that the
result is the following grid:

![SUTOM grid with the first line completed with "PARIEES" and being valid for
the "P" and "I", having the "S" misplaced, and every other letter
invalid](README_imgs/sutom2.png)

Now, you have to refine the search, using the newly obtained information:

```sh
$ sutom/sutom.py P..I... -n ARE -m ......S
POSITON (0.40320747847670774)
$ _
```

I'll explain what we got here:

1. The valid pattern changed. Initially, we had `P......`, but with the
   additional `I` letter, it becomes `P..I...`.
2. The letters `A`, `R`, and `E` are absent from the final word, so we add them
   to the `-n` argument (in one "word", with letters appearing only once, like
   so: `ARE`. `REA`, `AER`, etc are also all perfectly valid). `n` initially
   stood for "negated" as in "negated match".
3. The letter `S` is misplaced. Since the position of the misplaced letter
   matters, it needs to be input using a "dot-pattern", like the main search
   pattern.

> [!NOTE]
> *Nota Bene: Multiple "misplaced patterns" can be used, in order to always be
> able to represent the game state accurately; but different lines can be
> "aggregated" in one line, if the positions don't conflict. For instance, the
> patterns `A...` and `...S` can be represented as `A..S`. **This isn't
> possible with the `-n` argument, which MUST be a single word and must be
> present only once.***

Ok, let's input that word in the second line, then.

Let's, this time, assume we obtain the following grid:

![SUTOM grid with the first and second lines completed, and "POSIT" being valid
for the entire beginning of the pattern, followed by "ON" being marked both
invalid](README_imgs/sutom3.png)

This time, as you can see, most of the word matches. There's also another
important gotcha: the second letter `O` is marked as "invalid", but the first
one as "valid".

> [!CAUTION]
> **It is extremely important not to add any *subsequent* invalid letter to the
> `-n` "word". If you do, you will get incorrect matches.**

So, it is better *not* to represent a "subsequent invalid" letter than to add
it to the `-n` "word".

However, there is a way to represent it anyway: a "subsequent invalid" letter
is technically simply a "misplaced" one. If it was not already marked as
"valid" in the rest of the world, it would indeed be marked as "misplaced".

> [!TIP]
> It is possible to represent an "invalid letter" that has a match elsewhere in
> the pattern using the `-m` flag and a positional pattern for that letter,
> since it is technically a "misplaced" letter, not an "invalid" one.

> [!NOTE]
> *Nota Bene: The game reporting a "misplaced" letter that also has a "match"
> elsewhere in the pattern means that there are two occurrences of that
> specific letter. There is currently no way to represent that in this cheat
> script. One way would be to input the letter twice in a single mismatched
> pattern, and another way would be to introduce a new flag to set the number
> of known occurrences per letter.  However, given the low incidence of that
> scenario, and the relatively high effort of implementation, I have elected
> not to implement it.*

So, let's add the `N` letter (which is entirely absent) to the `-n` argument,
and the second `O` letter to a second "misplaced" argument:

```sh
$ sutom/sutom.py POSIT.. -n AREN -m ......S -m .....O.
POSITIF (0.35231437278876243)
$ _
```

We could have, of course, "aggregated" both `-m` arguments, as seen above, for
the same result:

```sh
$ sutom/sutom.py POSIT.. -n AREN -m .....OS
POSITIF (0.35231437278876243)
$ _
```

Input that word, and there you go!

![SUTOM grid with three lines completed, and the last line "POSITIF" being
entirely valid](README_imgs/sutom4.png)

Hey, would you look at that, you won! Congratulations!! :partying_face:

# Why the hard way?

Because it's more interesting. Because it cannot be detected. But also because
I can.

## How to cheat the easy way, anyway?

So you want to have that perfect "first try" score, every day? Fine.

The game grabs the word of the day from a text file, and generates its URL via
the `btoa` JavaScript function, using a predefined `GUID` and the date of the
day in the `YYYY-MM-DD` notation; and suffixing `.txt` to it.

The `GUID` is literally the default one from the
<https://sutom.nocle.fr/js/instanceConfiguration.js> file, and the date of the
day is, well, the date of the day.

> [!NOTE]
> In the following code snippets, everything is more or less designed to be
> impevious to change, except for one very hardcoded constant: the line number
> of the `GUID` in the JavaScript file.
>
> This line is the line 16 at the time of writing (see the `[15]` in the
> JavaScript browser console code, and the `'16!d` `sed` expression in the
> shell code; because sed counts from 1), but it could very well change with
> time.

So, if you wanna cheat the *easy* way, just run this in your browser's console:

```js
fetch("/js/instanceConfiguration.js")
  .then(r=>r.text())
  .then(t=>t.split('\n')[15].split("=")[1].replaceAll(/[ ";]/g, ""))
  .then(g=>btoa(g+'-'+(new Date).toISOString().substring(0,10)))
  .then(b=>fetch('/mots/'+b+'.txt')
    .then(r=>r.text())
    .then(o=>console.log(o)));
```
If you feel like getting the word from tomorrow, or any other day, you can also
put a date in the Date constructor, like so: `...(new Date('2024-01-01'))...`

If you want to do the same in a terminal, run this:

```sh
$ curl -SsL 'https://sutom.nocle.fr/js/instanceConfiguration.js' \
  | sed '16!d; s/^[^=]*=[^0-9ac]*//; s/";$/-/' \
  | xargs -I_ date '+_%F' | tr -d '\n' | base64 \
  | xargs -I_ curl -SsL 'https://sutom.nocle.fr/mots/_.txt'
```

Enjoy.
