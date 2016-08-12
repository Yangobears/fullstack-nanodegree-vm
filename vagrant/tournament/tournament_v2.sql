DROP DATABASE IF EXISTS tournament_v2;
CREATE DATABASE tournament_v2;
\c tournament_v2;

CREATE TABLE Tournament
(
    id serial PRIMARY KEY,
    name text
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
    bye integer,
    PRIMARY KEY (tid, pid)
);


--if draw = 1, winner and loser both get 1 point
--if draw = 0, winner.score +3, loser.score + 0
CREATE TABLE Match
(
    id serial PRIMARY KEY,
    tid integer REFERENCES Tournament (id) ON DELETE CASCADE,
    draw integer,
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

--A view that captures how many draws each player has in certain tournament.

CREATE VIEW Draws as
(   SELECT
    COUNT(Match.tid) AS draw,
    Tournament_Player.pid AS pid,
    Tournament_Player.tid AS tid
    FROM Tournament_Player
    LEFT OUTER JOIN Match
    ON Tournament_Player.tid = Match.tid
    AND Match.draw = 1
    AND (Tournament_Player.pid = Match.winner
    OR Tournament_Player.pid = Match.loser)

    GROUP BY Tournament_Player.pid, Tournament_Player.tid
);

--A view that captures how many wins each player has in certain tournament.

CREATE VIEW Wins as
(   SELECT
    COUNT(Match.winner) + Tournament_Player.bye AS win,
    Tournament_Player.pid AS pid,
    Tournament_Player.tid AS tid
    FROM Tournament_Player
    LEFT OUTER JOIN Match
    ON Tournament_Player.pid = Match.winner
    AND Tournament_Player.tid = Match.tid
    AND Match.draw = 0
    GROUP BY Tournament_Player.pid, Tournament_Player.tid
);

--A view that captures how much draw each player has in certain tournament.

CREATE VIEW Scores as
(
    SELECT
    3 * Wins.win + 1 * Draws.draw as score,
    Tournament_Player.pid as pid,
    Tournament_Player.tid as tid,
    Player.name as name
    FROM Player
    LEFT OUTER JOIN Tournament_Player
    ON Player.id = Tournament_Player.pid
    LEFT OUTER JOIN Wins
    ON (Tournament_Player.pid = Wins.pid AND Tournament_Player.tid = Wins.tid)
    FULL OUTER JOIN DRAWS ON
    Tournament_Player.pid = Draws.pid AND Tournament_Player.tid = Draws.tid
    ORDER BY score DESC
);

CREATE VIEW NOT_YET_BYE as
(
    SELECT
    Tournament_Player.pid as pid,
    Tournament_Player.tid as tid
    FROM Tournament_Player
    WHERE Tournament_Player.bye = 0
);

