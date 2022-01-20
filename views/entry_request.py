import sqlite3
import json
from models import Entry, Mood, Tag
from .entry_tag_request import create_entry_tag


def get_all_entries():
    # Open a connection to the database
    with sqlite3.connect("./dailyjournal.sqlite3") as conn:

        # Just use these. It's a Black Box.
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # Write the SQL query to get the information you want
        db_cursor.execute("""
        SELECT
            e.id,
            e.concept,
            e.entry,
            e.mood_id,
            e.date,
            m.label mood_label
        FROM Entry e
        JOIN Mood m
            ON m.id = e.mood_id
        ORDER BY e.id DESC
        """)
        
        

        # Initialize an empty list to hold all entry representations
        entries = []

        # Convert rows of data into a Python list
        dataset = db_cursor.fetchall()

        # Iterate list of data returned from database
        for row in dataset:

            # Create an entry instance from the current row.
            # Note that the database fields are specified in
            # exact order of the parameters defined in the
            # Entry class above.
            entry = Entry(row['id'], row['concept'], row['entry'],
                            row['mood_id'], row['date'])

            # Create a mood instance from the current row
            mood = Mood(row['mood_id'], row['mood_label'])
            
            # Add the dictionary representation of the customer to the entry
            entry.mood = mood.__dict__
            
            # execute sql again to select all tags associated with entry
            # fetch all, then for each tag_item in tag_data
            # create a tag instance and append it to a tags list
            # entry.tags = the completed tags list
            db_cursor.execute("""
            SELECT
                t.id,
                t.label
            FROM EntryTag et
            JOIN Tag t
                ON t.id = et.tag_id
            WHERE et.entry_id = ?
            """, (row['id'] , ))
            
            tag_data = db_cursor.fetchall()
            
            tags_list = []
            for tag_item in tag_data:
                tag = Tag(tag_item['id'], tag_item['label'])
                tags_list.append(tag.__dict__)
            
            entry.tags = tags_list
            
            # Add the dictionary representation of the entry to the list
            entries.append(entry.__dict__)

    # Use `json` package to properly serialize list as JSON
    return json.dumps(entries)

# Function with a single parameter


def get_single_entry(id):
    with sqlite3.connect("./dailyjournal.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # Use a ? parameter to inject a variable's value
        # into the SQL statement.
        db_cursor.execute("""
        SELECT
            e.id,
            e.concept,
            e.entry,
            e.mood_id,
            e.date,
            m.label mood_label
        FROM Entry e
        JOIN Mood m
            ON m.id = e.mood_id
        WHERE e.id = ?
        """, (id, ))

        # Load the single result into memory
        data = db_cursor.fetchone()

        # Create an entry instance from the current row
        entry = Entry(data['id'], data['concept'], data['entry'],
                      data['mood_id'], data['date'])
        
        mood = Mood(data['mood_id'], data['mood_label'])
        entry.mood = mood.__dict__
        
            # execute sql again to select all tags associated with entry
            # fetch all, then for each tag_item in tag_data
            # create a tag instance and append it to a tags list
            # entry.tags = the completed tags list
        db_cursor.execute("""
        SELECT
            t.id,
            t.label
        FROM EntryTag et
        JOIN Tag t
            ON t.id = et.tag_id
        WHERE et.entry_id = ?
        """, (data['id'] , ))
            
        tag_data = db_cursor.fetchall()
            
        tags_list = []
        for tag_item in tag_data:
            tag = Tag(tag_item['id'], tag_item['label'])
            tags_list.append(tag.__dict__)
            
        entry.tags = tags_list

        return json.dumps(entry.__dict__)


def create_entry(new_entry):
    with sqlite3.connect("./dailyjournal.sqlite3") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute("""
        INSERT INTO Entry
            ( concept, entry, mood_id, date)
        VALUES
            ( ?, ?, ?, ? );
        """, (new_entry['concept'], new_entry['entry'],
              new_entry['mood_id'], new_entry['date']))

        # The `lastrowid` property on the cursor will return
        # the primary key of the last thing that got added to
        # the database.
        id = db_cursor.lastrowid

        # Add the `id` property to the entry dictionary that
        # was sent by the client so that the client sees the
        # primary key in the response.
        new_entry['id'] = id
        
        if 'tags' in new_entry:
            for tag in new_entry['tags']:
                db_cursor.execute("""
                INSERT INTO EntryTag
                    ( entry_id, tag_id )
                VALUES
                    ( ?, ? );
                """, (new_entry['id'], tag))

    return json.dumps(new_entry)


def delete_entry(id):
    # with-as automatically closes the connection when done
    with sqlite3.connect("./dailyjournal.sqlite3") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute("""
        DELETE FROM entry
        WHERE id = ?
        """, (id, ))
        
        db_cursor.execute("""
        SELECT
            et.id
        FROM EntryTag et
        WHERE et.entry_id = ?
        """, (id , ))
            
        et_ids = db_cursor.fetchall()
        
        for et_id in et_ids:
            db_cursor.execute("""
            DELETE FROM EntryTag
            WHERE id = ?
            """, (et_id[0], ))


def update_entry(id, new_entry):
    with sqlite3.connect("./dailyjournal.sqlite3") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute("""
        UPDATE Entry
            SET
                concept = ?,
                entry = ?,
                mood_id = ?,
                date = ?
        WHERE id = ?
        """, (new_entry['concept'], new_entry['entry'],
              new_entry['mood_id'], new_entry['date'],
              id, ))


        # Get all current entry tags with entry_id == id
        # compare to new_entry['tags']
        # if it exists in current entry tags but not new tags, delete
        # if it exists in new tags but not current entry tags, insert
        db_cursor.execute("""
            SELECT * FROM EntryTag et
            WHERE et.entry_id = ?
        """, (id, ))
        
        existing_entry_tags = db_cursor.fetchall()
        
        if 'tags' in new_entry:
            for tag in existing_entry_tags:
            # For each row of existing entry tags, check if the value
            # of tag_id exists in the new_entry's tags array
            # If not: delete that entry tag from the database
                if tag[2] not in new_entry['tags']:
                    db_cursor.execute("""
                        DELETE FROM EntryTag
                        WHERE id = ?
                        """, (tag[0], ))
            
            # For each tagId in the new_entry's tag array, check if that
            # combo of entry_id and tag_id exists in the database
            for tag_id in new_entry['tags']:
                db_cursor.execute("""
                    SELECT * FROM EntryTag
                    WHERE entry_id = ? AND tag_id = ?
                    """, (new_entry['id'], tag_id))
                # If no matches come back, create a a new entry tag
                if len(db_cursor.fetchall()) == 0:
                    db_cursor.execute("""
                    INSERT INTO EntryTag
                        ( entry_id, tag_id )
                    VALUES
                        ( ?, ? );
                    """, (new_entry['id'], tag_id))
            

        # Were any rows affected?
        # Did the client send an `id` that exists?
        rows_affected = db_cursor.rowcount

    if rows_affected == 0:
        # Forces 404 response by main module
        return False
    else:
        # Forces 204 response by main module
        return True

def get_entry_search_results(search_term):
    # Open a connection to the database
    with sqlite3.connect("./dailyjournal.sqlite3") as conn:

        # Just use these. It's a Black Box.
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # Write the SQL query to get the information you want
        db_cursor.execute("""
        SELECT
            e.id,
            e.concept,
            e.entry,
            e.mood_id,
            e.date,
            m.label mood_label
        FROM Entry e
        JOIN Mood m
            ON m.id = e.mood_id
        WHERE e.entry LIKE ?
        ORDER BY e.id DESC
        """, ('%' + search_term + '%', ))

        # Initialize an empty list to hold all entry representations
        entries = []

        # Convert rows of data into a Python list
        dataset = db_cursor.fetchall()

        # Iterate list of data returned from database
        for row in dataset:

            # Create an entry instance from the current row.
            # Note that the database fields are specified in
            # exact order of the parameters defined in the
            # Entry class above.
            entry = Entry(row['id'], row['concept'], row['entry'],
                            row['mood_id'], row['date'])

            # Create a mood instance from the current row
            mood = Mood(row['id'], row['mood_label'])
            
            # Add the dictionary representation of the customer to the entry
            entry.mood = mood.__dict__
            
                        # execute sql again to select all tags associated with entry
            # fetch all, then for each tag_item in tag_data
            # create a tag instance and append it to a tags list
            # entry.tags = the completed tags list
            db_cursor.execute("""
            SELECT
                t.id,
                t.label
            FROM EntryTag et
            JOIN Tag t
                ON t.id = et.tag_id
            WHERE et.entry_id = ?
            """, (row['id'] , ))
            
            tag_data = db_cursor.fetchall()
            
            tags_list = []
            for tag_item in tag_data:
                tag = Tag(tag_item['id'], tag_item['label'])
                tags_list.append(tag.__dict__)
            
            entry.tags = tags_list
            
            # Add the dictionary representation of the entry to the list
            entries.append(entry.__dict__)

    # Use `json` package to properly serialize list as JSON
    return json.dumps(entries)