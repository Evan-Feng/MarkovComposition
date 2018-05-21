# MarkovComposition
A python program that generates music by Markov Chain.

### Requirements

```
python 3.6
music21 5.1.0
prettytable 0.7.2
```

### Usage

```bash
>>> python compose.py --help

usage: compose.py [-h] [-l LENGTH] [--play] [--score] [-o ORDER] [--original]
                  [-d] [-v] (-j JSON | -m MIDI | -c CORPUS)

optional arguments:
  -h, --help            show this help message and exit
  -l LENGTH, --length LENGTH
                        length of the new piece (number of notes)
  --play                play soundtrack
  --score               display score in a MusicXML reader
  -o ORDER, --order ORDER
                        order of Markov chain (default: 1)
  --original            present the original piece of music
  -d, --with-duration   treats notes with the same pitch and different
                        duration as different notes
  -v, --verbose         increase verbosity level
  -j JSON, --json JSON  load form Json format
  -m MIDI, --midi MIDI  load from .midi file
  -c CORPUS, --corpus CORPUS
                        load from music21 corpus
```

Parse existing music from a Json file and generate a new piece of music consisting 200 notes(and rests), prints the Markov transition matrix and display score in a MusicXML reader (such as MuseScore):

```bash
>>> python compose.py -j example.txt -l 200 --score

+------+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
|      |  A4 |  A5 |  B5 | F#5 |  G5 |  E5 |  D5 |  D6 |  B4 | G#4 |
+------+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
| A4,  |  0  |  1  |  0  |  0  |  0  |  0  |  0  |  0  |  0  |  0  |
| A5,  | 2/9 |  0  | 2/9 | 2/9 | 1/3 |  0  |  0  |  0  |  0  |  0  |
| B5,  |  0  |  1  |  0  |  0  |  0  |  0  |  0  |  0  |  0  |  0  |
| F#5, |  0  |  0  |  0  |  0  | 3/5 |  0  | 2/5 |  0  |  0  |  0  |
| G5,  |  0  | 3/7 |  0  | 1/7 |  0  | 3/7 |  0  |  0  |  0  |  0  |
| E5,  |  0  | 1/4 |  0  | 1/4 |  0  |  0  | 1/2 |  0  |  0  |  0  |
| D5,  |  0  |  0  |  0  | 1/7 | 1/7 | 1/7 |  0  | 2/7 | 2/7 |  0  |
| D6,  |  0  |  0  |  0  |  0  |  0  |  0  |  1  |  0  |  0  |  0  |
| B4,  |  0  |  0  |  0  |  0  |  0  |  0  | 1/2 |  0  |  0  | 1/2 |
| G#4, |  1  |  0  |  0  |  0  |  0  |  0  |  0  |  0  |  0  |  0  |
+------+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
```

I simply want to view the score of a famous work, say Scott Joplin's *Maple Leaf Rag* , and analyze its second-order Markov transition matrix:

```bash
>>> python compose.py -c joplin/maple_leaf_rag --score -o 2

+---------+------+------+-----+-----+----+------+-----+------+------+  ...
|         | C-5  |  G5  | D-6 | E-4 | F6 | A-5  | F-5 |  G4  | D-5  |
+---------+------+------+-----+-----+----+------+-----+------+------+
|  A-5,R  |  0   |  0   |  0  |  0  | 0  | 2/3  |  0  |  0   |  0   |
|   R,R   |  0   | 1/8  |  0  |  0  | 0  |  0   |  0  |  0   |  0   |
|  R,A-4  | 6/11 |  0   |  0  |  0  | 0  |  0   |  0  |  0   |  0   |
| A-4,E-5 |  0   |  0   |  0  |  0  | 0  | 1/7  |  0  |  0   |  0   |
| E-5,A-4 |  0   |  0   |  0  |  0  | 0  |  0   |  0  |  0   | 2/7  |
|  A-4,C5 |  0   |  0   |  0  |  0  | 0  |  0   |  0  |  0   |  0   |
|  C5,E-5 |  0   |  0   |  0  |  0  | 0  | 1/21 |  0  | 4/21 | 1/21 |  ...

...                     ...                     ...                    ...

```

Generate music from *Maple Leaf Rag*, stores the Markov transition matrix to a local file, and play the sound track of the new piece:

```bash
>>> python compose.py -c joplin/maple_leaf_rag --play > output.txt
```

Generate music from a Joplin piano piece and take the note duration into consideration:

```bash
>>> python compose.py -c joplin/maple_leaf_rag -d --score

+-------------+---------+----------+------------+------------+-----------+  ...
|             | (R,0.5) | (R,0.25) | (A-4,0.25) | (E-5,0.25) | (C5,0.25) |
+-------------+---------+----------+------------+------------+-----------+
|   (R,0.5),  |   1/8   |   3/8    |     0      |     0      |    1/8    |
|  (R,0.25),  |    0    |    0     |   11/37    |   11/37    |    4/37   |
| (A-4,0.25), |    0    |   1/42   |    1/6     |    2/21    |    1/6    |
| (E-5,0.25), |   2/61  |   8/61   |    6/61    |     0      |     0     |
|  (C5,0.25), |    0    |   1/42   |    5/42    |    8/21    |    1/14   |
|  (E-5,0.5), |    0    |   3/14   |     0      |     0      |     0     |  ...

...                     ...                     ...                         ...
```

### Todo

1.  Support for .midi files
2.  Support for LaTeX-style output





