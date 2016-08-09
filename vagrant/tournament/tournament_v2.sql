CREATE TABLE Tournament
(
    id serial PRIMARY KEY,
    name text,
    size integer
);

CREATE TABLE Player
(
    id serial PRIMARY KEY,
    name text
);

--A table that depicts when a player enters a tournament,
--records which tournament, which player, how many matches,
--score, player score win +3, draw +1, bye +3, lost + 0
--bye, one user can have at most one bye per tournament
--the combo of tid and pid would make up of the primary key
CREATE TABLE Tournament_Player
(
    tid integer REFERENCES Tournament ON DELETE CASCADE,
    pid integer REFERENCES Player ON DELETE CASCADE,
    matches integer,
    score integer,
    bye integer,
    PRIMARY KEY (tid, pid)
);


--if draw = True, winner and loser both get 1 point
--if draw = False, winner.score +3, loser.score + 0
CREATE TABLE Match
(
    id serial PRIMARY KEY,
    tid integer REFERENCES Tournament (id) ON DELETE CASCADE,
    draw boolean,
    winner integer REFERENCES Player (id) ON DELETE CASCADE,
    loser integer REFERENCES Player (id) ON DELETE CASCADE
);

--A table that record the pairs in a tournament
--The unique index prevent rematch.
--While I realize this table is similar to Match, I could create a view of Match,
--I think it's cleaner to keep it seperate.

CREATE TABLE Pairs
(
    id serial PRIMARY KEY,
    tid integer REFERENCES Tournament (id) ON DELETE CASCADE,
    player1 integer REFERENCES Player (id) ON DELETE CASCADE,
    player2 integer REFERENCES Player (id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX  No_Rematch ON Pairs
(GREATEST(player1, player2), LEAST(player1, player2));





