import sqlite3
import json
from models import Entry, Mood


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

    return json.dumps(new_entry)


def delete_entry(id):
    with sqlite3.connect("./dailyjournal.sqlite3") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute("""
        DELETE FROM entry
        WHERE id = ?
        """, (id, ))


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
            
            # Add the dictionary representation of the entry to the list
            entries.append(entry.__dict__)

    # Use `json` package to properly serialize list as JSON
    return json.dumps(entries)