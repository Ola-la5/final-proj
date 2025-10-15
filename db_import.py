import pandas as pd
import sqlite3

try:

    with sqlite3.connect("db/mlb_history.db") as conn:
        conn.execute("PRAGMA foreign_keys = 1")
        print("Database created and connected successfully")

        # events.csv
        try:
            df_events=pd.read_csv("events.csv")
            # before cleaning
            print(f"before cleaning events: {len(df_events)} rows")
            # cleaning
            df_events['year'] = pd.to_numeric(df_events['year'], errors='coerce')
            df_events.drop_duplicates(inplace=True)
            df_events.dropna(subset=['year', 'event'], inplace=True)
            # after cleaning
            print(f"after cleaning events: {len(df_events)} rows")
            df_events.to_sql("events", conn, if_exists="replace", index=False)
            print(f"events: imported {len(df_events)} rows")# debugging
        except Exception as e:
            print(f"Error importing events.csv: {type(e).__name__} - {e}")

        # statistics from american league
        try:
            df_al = pd.read_csv("statistics_AL.csv")
            # before cleaning
            print(f"before cleaning statistics: {len(df_al)} rows")
            # cleaning
            df_al['league'] = "American League"
            df_al['value'] = pd.to_numeric(df_al['value'], errors='coerce')
            df_al.drop_duplicates(inplace=True)
            df_al.dropna(subset=['year', 'player', 'value'], inplace=True)
            # after claning
            print(f"after cleaning statistics: {len(df_al)} rows")
            df_stats = pd.concat([df_al], ignore_index=True)
                       
            df_stats.to_sql("statistics", conn, if_exists="replace", index=False)
            print(f"stat: imported {len(df_stats)} rows")# debugging 
        except Exception as e:
            print(f"error importing statistics csvs: {type(e).__name__} - {e}")

except Exception as e:
    print(f"an exception occurred: {type(e).__name__} - {e}")