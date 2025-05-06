from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.chrome.options import Options
import tkinter as tk
from tkinter import messagebox

def get_player_lineup_counts_by_pos(username, password, roster_url):
    """Logs in to RTSports site, retrieves roster data, counts player occurrences by POS 
       and 'Starter' occurrences, modifies WR and TE to WR/TE, filters occurrences by high to low, and saves to Excel."""
    
    # Step 1: Set Chrome options for headless mode (no UI)
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
    chrome_options.add_argument("--no-sandbox")  # Prevent sandbox issues
    
    # Step 2: Initialize the WebDriver with options
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # Step 3: Open the login page
    login_url = "https://www.rtsports.com/login"
    driver.get(login_url)

    # Step 4: Wait for the page to load and find the input elements
    driver.implicitly_wait(10)  # Implicit wait to ensure elements are loaded
    
    username_field = driver.find_element(By.NAME, "ACCOUNTID")
    password_field = driver.find_element(By.NAME, "PASSWORD")

    # Step 5: Fill in the login credentials
    username_field.send_keys(username)
    password_field.send_keys(password)

    # Step 6: Submit the form by pressing Enter
    password_field.send_keys(Keys.RETURN)

    # Step 7: Handle confirmation pop-up(s) after login
    try:
        # Wait until the confirmation pop-up appears (it may appear once or twice)
        WebDriverWait(driver, 1).until(EC.alert_is_present())
        alert = driver.switch_to.alert  # Switch to the alert
        alert.accept()  # Click the "OK" button on the first pop-up
        print("Successfully clicked 'OK' on the confirmation pop-up!")

        # Wait again in case there is a second pop-up
        WebDriverWait(driver, 1).until(EC.alert_is_present())
        alert = driver.switch_to.alert  # Switch to the second alert
        alert.accept()  # Click the "OK" button on the second pop-up (if it appears)
        print("Successfully clicked 'OK' on the second confirmation pop-up!")
        
    except Exception as e:
        print("No pop-ups appeared or an error occurred:", e)
    
    # Step 8: Open the page with the teams' roster data
    # roster_url = "https://www.rtsports.com/football/report-rosters.php?LID=24267&UID=m2r1f3tw177b2w8f7vd699y2v0hm2fo&X=233456"
    driver.get(roster_url)

    # Step 9: Retrieve the body content of the page
    body_element = driver.find_element(By.TAG_NAME, "body")
    body_content = body_element.get_attribute('innerHTML')

    # Step 10: Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(body_content, 'html.parser')

    # Step 11: Find all tables or sections that contain player data (not just the first one)
    tables = soup.find_all('table')  # Get all tables on the page

    if not tables:
        print("No tables found on the page.")
        driver.quit()
        return

    all_data = []
    headers = []

    # Loop through each table and extract data
    for table in tables:
        # Extract table headers (column names)
        header_row = table.find_all('th')
        if header_row:
            headers = [th.get_text(strip=True) for th in header_row]

        # Extract rows of player data
        rows = []
        for tr in table.find_all('tr')[1:]:  # Skip the header row
            cols = tr.find_all('td')
            row_data = [col.get_text(strip=True) for col in cols]
            if row_data:
                rows.append(row_data)

        # Add rows to all_data
        all_data.extend(rows)

    # Step 12: Create a DataFrame with the player data
    if headers:  # If headers exist, use them for the columns
        df = pd.DataFrame(all_data, columns=headers)
    else:
        # Fallback if no headers found (you can manually set column names if needed)
        df = pd.DataFrame(all_data)

    # Step 13: Filter relevant columns ("PLAYER", "POS", and "LINEUP")
    df_filtered = df[['PLAYER', 'POS', 'LINEUP']]  # Keep only PLAYER, POS, and LINEUP columns

    # Step 14: Modify WR and TE positions to "WR/TE"
    df_filtered['POS'] = df_filtered['POS'].replace({'WR': 'WR/TE', 'TE': 'WR/TE'})

    # Step 15: Count occurrences of each player by position and count "Starter" entries
    player_counts = df_filtered.groupby(['PLAYER', 'POS']).size().reset_index(name='Occurrences')
    starter_counts = df_filtered[df_filtered['LINEUP'] == 'Starter'].groupby(['PLAYER', 'POS']).size().reset_index(name='Starters')

    # Step 16: Merge the two dataframes on "PLAYER" and "POS"
    result_df = pd.merge(player_counts, starter_counts, on=['PLAYER', 'POS'], how='left')

    # Step 17: Fill NaN values for "Starters" (if no "Starter" is found for a player)
    result_df['Starters'].fillna(0, inplace=True)

    # Step 18: Sort by Occurrences (from high to low)
    result_df = result_df.sort_values(by='Occurrences', ascending=False)

    # Step 19: Filter the DataFrame by position and save separate sheets for each position
    positions = result_df['POS'].unique()  # Get unique positions
    
    with pd.ExcelWriter('filtered_player_data_by_position_sorted.xlsx') as writer:
        for pos in positions:
            # Clean the position name to be a valid Excel sheet name
            clean_pos = pos.replace('/', '_')  # Replace '/' with '_'

            # Filter the DataFrame for each position
            position_df = result_df[result_df['POS'] == pos]
            
            # Save the result to a new sheet in the Excel file
            position_df.to_excel(writer, sheet_name=clean_pos, index=False)

    print("Filtered player data by position (sorted) saved to 'filtered_player_data_by_position_sorted.xlsx'")

    # Step 20: Close the browser
    driver.quit()

# Test the function
# get_player_lineup_counts_by_pos("ryanwallman7@gmail.com", "03DecembeR12!@")

def create_gui():
    """Creates a Tkinter GUI to input the username, password, and roster URL."""
    root = tk.Tk()
    root.title("RTSports Scraper")

    # Username Label and Entry
    tk.Label(root, text="Username:").pack(padx=10, pady=5)
    username_entry = tk.Entry(root, width=50)
    username_entry.pack(padx=10, pady=5)

    # Password Label and Entry
    tk.Label(root, text="Password:").pack(padx=10, pady=5)
    password_entry = tk.Entry(root, width=50, show="*")
    password_entry.pack(padx=10, pady=5)

    # Roster URL Label and Entry
    tk.Label(root, text="Roster URL:").pack(padx=10, pady=5)
    roster_url_entry = tk.Entry(root, width=50)
    roster_url_entry.pack(padx=10, pady=5)

    # Submit Button
    def on_submit():
        username = username_entry.get()
        password = password_entry.get()
        roster_url = roster_url_entry.get()

        if not username or not password or not roster_url:
            messagebox.showwarning("Input Error", "All fields must be filled!")
        else:
            get_player_lineup_counts_by_pos(username, password, roster_url)
            
            # Show success message and close the GUI
            messagebox.showinfo("Success", "Player and lineup counts by position saved to 'player_lineup_counts_by_pos.xlsx'")
            
            # Close the Tkinter window after success
            root.quit()  # This stops the Tkinter main loop and closes the window

    submit_button = tk.Button(root, text="Submit", command=on_submit)
    submit_button.pack(padx=10, pady=20)

    # Run the Tkinter loop
    root.mainloop()

# Run the GUI
create_gui()