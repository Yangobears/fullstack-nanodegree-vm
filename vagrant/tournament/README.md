# Basic version of tournament:

###Setup database and run tests:

1.In tournament directory, run psql, enter psql console
2. run
```CREATE DATABASE tournament;
```
3. run
```
\i tournament_v2.sql;
```
4. Run test:
quit psql, go back to tournament directory
run
```
python tournament_test.py
```

#
Advanced version of tournament:
###Extra Features:
1. Support more than one tournament.
2. Prevent rematch between players while try match players with similar score.
3. Assign bye to the first player in the standing that hasnt been assigned bye before if
the size of the tournament is odd.
4. Support Draw, score: Win + 3, Lose +0, Draw +1, Bye = Win


###Setup database and run tests:

1.In tournament directory, run psql, enter psql console
2. run
```
CREATE DATABASE tournament_v2;
```
3. run
```
\i tournament_v2.sql;
```
4. Run test:
quit psql, go back to tournament directory
run
```
python tournament_v2_test.py
```


