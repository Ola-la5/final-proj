from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pandas as pd
from time import sleep

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
try:
    driver.get("https://www.baseball-almanac.com/yearmenu.shtml")  # main page
    sleep(2)

# get years
    years = []
    try:
        year = driver.find_elements(By.CSS_SELECTOR, "a[href*='yearly/yr']")
        # take care of formatting
        for link in year:
            try:
                year_text = link.text.strip()
                year_url = link.get_attribute("href")
                if year_text and year_url:
                    years.append({"year": year_text, "url": year_url})
            except:
                continue
    except Exception as e:
        print(f"Can not get year links: {e}")
   
    print("Test :",years[:5])  # for debugging

    # events
    events = []

    # pagination is handled by going through each year link instead of clicking "next"
    for y in years[:20]:  #20 years events as showcase
        print(f"year {y['year']}")
        try:
            driver.get(y["url"])
            sleep(2)

            paragraphs = driver.find_elements(By.CSS_SELECTOR, "p")
            for p in paragraphs:
                text = p.text.strip()

                # do not include empty or short paragraphs
                if len(text) < 50:
                    continue

                # do not include paraghraphs with no events
                if (
                    "Where what happened yesterday" in text
                    or "Copyright" in text
                    or "Hosted by" in text
                    or "Baseball Almanac" in text
                    or "League Leaderboards" in text
                    or "Hitting Statistics" in text
                    or "Pitching Statistics" in text
                ):
                    continue

                # keep valid event paragraphs
                events.append({"year": y["year"], "event": text})

        except Exception as e:
            print(f"Error getting events for {y['year']}: {e}")
    # events to df to perform some cleaning
    events_df = pd.DataFrame(events).drop_duplicates(subset=['year', 'event'])
    # save events to CSV
    events_df.to_csv("events.csv", index=False)
    print(f"Events saved: {len(events_df)} rows")

    # statistics
    al_data = []

    # select few stats
    selected_stats = ["Base on Balls", "Batting Average", "Doubles", "Hits", "Home Runs"]
    # take care of fromatting numeric val, convert string stat to float, handles values like .382 
    def parse_stat_value(val):
        if not val or val.strip() == '-' or val.lower() in ['b', 'r', 'hr']:
            return None
        # take the first numeric part
        parts = val.split()
        for part in parts:
            try:
                return float(part.strip("()"))
            except:
                continue
        return None

    for y in years[:20]:  # loop over 20 years as a showcase
        print(f"Scraping stats for {y['year']}")
        try:
            driver.get(y["url"])
            sleep(2)  # wait for page to load

            # find all table rows
            rows = driver.find_elements(By.CSS_SELECTOR, "table tr")
            for row in rows[1:]:  # skip table header
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) < 4:
                    continue  # skip malformed rows

                stat_name = cols[0].text.strip()
                if stat_name not in selected_stats:
                    continue

                # american league
                al_player = cols[1].text.strip()
                al_team = cols[2].text.strip()
                al_value = parse_stat_value(cols[3].text.strip())
                if al_player and al_team and al_value is not None:
                    al_data.append({
                        "year": int(y["year"]),
                        "league": "American League",
                        "statistic": stat_name,
                        "player": al_player,
                        "value": al_value,
                        "team": al_team
                    })

                

        except Exception as e:
            print(f"Error scraping stats for {y['year']}: {e}")

    # stats to df, remove duplicates
    al_df = pd.DataFrame(al_data).drop_duplicates(subset=['year', 'league', 'statistic', 'player', 'team'])
   
    # save CSV
    al_df.to_csv("statistics_AL.csv", index=False)
    

    print("Scraping complete")# for debugging
    print(f"AL rows: {len(al_df)}")# for debugging
    
except Exception as e:
    print(f"An exception occurred: {type(e).__name__} {e}")

finally:
    driver.quit()