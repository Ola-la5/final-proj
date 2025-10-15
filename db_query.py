import pandas as pd
import sqlite3

try:
    with sqlite3.connect("db/mlb_history.db") as conn:
        conn.execute("PRAGMA foreign_keys = 1")
        print("Connected to database successfully")

        
        # join events and statistics by year
        sql_statement = """
        SELECT e.year,
               e.event,
               s.league,
               s.statistic,
               s.player,
               s.value,
               s.team
               
        FROM events e
        JOIN statistics s
        ON e.year = s.year
        ORDER BY e.year DESC;
        """

        df = pd.read_sql_query(sql_statement, conn)
        print(f"Joined {len(df)} rows")
        print(df.head(5))#debugging
    
    try:
        #filter by certain year, event,stat
        print("\nSelect to filter by year, event, or statistic ( press Enter to skip).")
        year = input("To filter by year please enter a year: ").strip()
        event = input("To filter by event pleas enter a keyword: ").strip()
        stat = input("To filter by statistics pleas enter a keyword  (e.g.,Base on Balls, Batting Average, Doubles, Hits, Home Runs): ").strip()
        
        filtered_df = df.copy()

        if year:
            filtered_df = filtered_df[filtered_df['year'] == int(year)]
        if event:
            filtered_df = filtered_df[filtered_df['event'].str.contains(event, case=False, na=False)]
        if stat:
            filtered_df = filtered_df[filtered_df['statistic'].str.contains(stat, case=False, na=False)]

            #results
        if len(filtered_df) > 0:
            print(f"\n{len(filtered_df)} matching rows:")
            print(filtered_df.head(10))
        else:
            print("\nNo results found for the given filters.")

    except Exception as e:
        print(f"Error during filtering: {type(e).__name__} - {e}")

        
except Exception as e:
    print(f"An exception occurred: {type(e).__name__} - {e}")