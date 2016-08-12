-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

--Create and Connect to db.
DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament;

--Create predefined tables.
CREATE TABLE Player
(
    id serial NOT NULL PRIMARY KEY,
    name text
);

CREATE TABLE Match
(
    id serial NOT NULL PRIMARY KEY,
    winner integer REFERENCES Player (id),
    loser integer REFERENCES Player (id)
);

--Create views.
--A view that captures how many wins each player has .
CREATE VIEW Wins as
(   SELECT COUNT(Match.winner) AS time, Player.id AS id
    FROM Player
    LEFT OUTER JOIN Match
    ON Player.id = Match.winner
    GROUP BY Player.id
);

--A view that captures how many loses each player has .
CREATE VIEW Loses as
(
    SELECT COUNT(Match.loser) AS time, Player.id AS id
    FROM Player
    LEFT OUTER JOIN Match
    ON Player.id = Match.loser
    GROUP BY Player.id
);

--A view that captures how many matches and wins each player has .
CREATE VIEW Count as
(
    SELECT Loses.time + Wins.time as matches, wins.time as wins
    , Player.id as id, Player.name as name
    FROM Player
    LEFT OUTER JOIN Loses
    ON Loses.id = Player.id
    LEFT OUTER JOIN Wins
    ON Player.id = Wins.id
);



