-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

CREATE TABLE Player
(
    id serial NOT NULL PRIMARY KEY,
    name text,
    wins integer,
    matches integer
);

CREATE TABLE Match
(
    id serial NOT NULL PRIMARY KEY,
    winner integer REFERENCES Player (id),
    loser integer REFERENCES Player (id)
);

