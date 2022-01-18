CREATE TABLE `Entry` (
    `id`    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    `concept`    TEXT NOT NULL,
    `entry`    TEXT NOT NULL,
    `mood_id`    INTEGER NOT NULL, FOREIGN KEY('mood_id') REFERENCES 'Mood'('id')

);

CREATE TABLE `Mood` (
    `id`    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    `label`    TEXT NOT NULL
);

CREATE TABLE `Tag` (
    `id`    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    `label`    TEXT NOT NULL
);


CREATE TABLE `EntryTag` (
    `id`    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    `entry_id`    INTEGER NOT NULL,
    `tag_id`    TEXT NOT NULL, 
    FOREIGN KEY('tag_id') REFERENCES 'Tag'('id'), FOREIGN KEY('entry_id') REFERENCES 'Entry'('id')
);

INSERT INTO "EntryTag" VALUES (null, 1, 1);
INSERT INTO "EntryTag" VALUES (null, 2, 6);
INSERT INTO "EntryTag" VALUES (null, 3, 5);
INSERT INTO "EntryTag" VALUES (null, 4, 4);

        SELECT
            e.id,
            e.concept,
            e.entry,
            e.mood_id,
            e.date,
            m.label mood_label,
            t.tag_id entry_tag_tag_id
        FROM Entry e
        JOIN Mood m
            ON m.id = e.mood_id
        JOIN EntryTag t
            ON t.entry_id = e.id
        WHERE e.id = 1

INSERT INTO "Entry" VALUES (null, "Python", "Python is named after the Monty Python comedy group from the UK. I'm sad because I thought it was named after the snake", 4, "Wed Sep 15 2021 10:11:33"); 

SELECT
    e.id,
    e.concept,
    e.entry,
    e.mood_id,
    e.date,
    m.label mood,
    tags
FROM Entry e
JOIN Mood m
    ON m.id = e.mood_id
    JOIN (
    SELECT et.entry_id AS id, group_concat(t.label) as tags
    FROM EntryTag et
    JOIN Tag t
        ON t.id = et.tag_id
    GROUP BY et.entry_id
) t USING (id)
;

SELECT *
FROM Entry e
JOIN Mood m
    ON m.id = e.mood_id
JOIN (
    SELECT et.entry_id AS id, group_concat(t.label) as tags
    FROM EntryTag et
    JOIN Tag t
        ON t.id = et.tag_id
    GROUP BY et.entry_id
) t USING (id)

SELECT
    t.id,
    t.label
FROM EntryTag et
JOIN Tag t
    ON t.id = et.tag_id
WHERE et.entry_id = 14
