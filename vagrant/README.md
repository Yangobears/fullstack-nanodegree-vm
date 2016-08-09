# Basic version of tournament:

###Setup database and run tests:

1.Change into tournament directory.

2.Enter psql console, do

```
psql
```

3.To create database called "tournament"

```
CREATE DATABASE tournament;
```

4.To create table predefined:

```
\i tournament.sql;
```

5. Change back into tournament directory.

To run unit test

```
python tournament_test.py
```




#
Advanced version of tournament:

###Extra Features:
```
1. Support more than one tournament.

2. Prevent rematch between players while try match players with similar score.

3. Assign bye to the first player in the standing that hasnt been assigned bye before if
the size of the tournament is odd.

4. Support Draw, score: Win + 3, Lose +0, Draw +1, Bye = Win
```


###Setup database and run tests:

1.Change into tournament directory.

2.Enter psql console, do

```
psql
```

3.To create database called "tournament_v2"

```
CREATE DATABASE tournament_v2;
```

4.To create table predefined:

```
\i tournament_v2.sql;
```

5. Change back into tournament directory.

To run unit test

```
python tournament_v2_test.py
```

