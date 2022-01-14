import sqlite3
import json
from models import Entry_Tag


def get_all_entry_tags():
    # Open a connection to the database
    with sqlite3.connect("./dailyjournal.sqlite3") as conn:

        # Just use these. It's a Black Box.
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # Write the SQL query to get the information you want
        db_cursor.execute("""
        SELECT
            t.id,
            t.entry_id,
            t.tag_id
        FROM EntryTag t
        ORDER BY id DESC
        """)

        # Initialize an empty list to hold all entry_tag representations
        entry_tags = []

        # Convert rows of data into a Python list
        dataset = db_cursor.fetchall()

        # Iterate list of data returned from database
        for row in dataset:

            # Create an entry_tag instance from the current row.
            # Note that the database fields are specified in
            # exact order of the parameters defined in the
            # entry_Tag class above.
            entry_tag = Entry_Tag(row['id'], row['entry_id'], row['tag_id'])
            
           
            # Add the dictionary representation of the entry_tag to the list
            entry_tags.append(entry_tag.__dict__)

    # Use `json` package to properly serialize list as JSON
    return json.dumps(entry_tags)

# Function with a single parameter


def get_single_entry_tag(id):
    with sqlite3.connect("./dailyjournal.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # Use a ? parameter to inject a variable's value
        # into the SQL statement.
        db_cursor.execute("""
        SELECT
            t.id,
            t.entry_id,
            t.tag_id
        FROM EntryTag t
        WHERE t.id = ?
        """, (id, ))

        # Load the single result into memory
        data = db_cursor.fetchone()

        # Create an entry_tag instance from the current row
        entry_tag = Entry_Tag(data['id'], data['entry_id'], data['tag_id'])

        return json.dumps(entry_tag.__dict__)


def create_entry_tag(new_entry_tag):
    with sqlite3.connect("./dailyjournal.sqlite3") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute("""
        INSERT INTO EntryTag
            ( entry_id, tag_id )
        VALUES
            ( ?, ? );
        """, (new_entry_tag['entry_id'], new_entry_tag['tag_id']))

        # The `lastrowid` property on the cursor will return
        # the primary key of the last thing that got added to
        # the database.
        id = db_cursor.lastrowid

        # Add the `id` property to the entry_tag dictionary that
        # was sent by the client so that the client sees the
        # primary key in the response.
        new_entry_tag['id'] = id

    return json.dumps(new_entry_tag)


def delete_entry_tag(id):
    with sqlite3.connect("./dailyjournal.sqlite3") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute("""
        DELETE FROM EntryTag
        WHERE id = ?
        """, (id, ))


def update_entry_tag(id, new_entry_tag):
    with sqlite3.connect("./dailyjournal.sqlite3") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute("""
        UPDATE EntryTag
            SET
                entry_id = ?
                tag_id = ?
        WHERE id = ?
        """, (new_entry_tag['entry_id'], new_entry_tag['tag_id'], id, ))

        # Were any rows affected?
        # Did the client send an `id` that exists?
        rows_affected = db_cursor.rowcount

    if rows_affected == 0:
        # Forces 404 response by main module
        return False
    else:
        # Forces 204 response by main module
        return True