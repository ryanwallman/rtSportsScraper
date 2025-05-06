import pandas as pd
import tkinter as tk
from tkinter import messagebox, ttk

# Load the Excel file containing player data
def load_player_data():
    return pd.read_excel('filtered_player_data_by_position_sorted.xlsx', sheet_name=None)

# Function to update the listbox based on the search query
def update_search_results(search_query, player_names, listbox):
    listbox.delete(0, tk.END)  # Clear previous search results
    # Filter player names that contain the search query (case-insensitive)
    matching_players = [player for player in player_names if search_query.lower() in player.lower()]
    # Insert the matching players into the listbox
    for player in matching_players:
        listbox.insert(tk.END, player)

# Function to display player info (total occurrences and starter occurrences)
def display_player_info(player_name, player_data, info_label):
    player_info = player_data[player_data['PLAYER'] == player_name]
    if not player_info.empty:
        total_occurrences = player_info['Occurrences'].values[0]
        total_starters = player_info['Starters'].values[0]
        info_label.config(text=f"Player: {player_name}\nTotal Occurrences: {total_occurrences}\nTotal Starters: {total_starters}")
    else:
        info_label.config(text="Player not found!")

# Function to handle player selection from the listbox
def on_player_select(event, listbox, player_data, info_label):
    selected_player = listbox.get(listbox.curselection())
    display_player_info(selected_player, player_data, info_label)

# Function to create the Tkinter GUI
def create_gui():
    root = tk.Tk()
    root.title("RTSports Player Search")

    # Load player data from Excel
    player_data_all = load_player_data()
    player_data = pd.concat(player_data_all.values(), ignore_index=True)  # Combine all sheets into one DataFrame
    player_names = player_data['PLAYER'].unique().tolist()  # List of all player names

    # Label for search entry
    search_label = tk.Label(root, text="Search Player:", font=("Helvetica", 14, "bold"))
    search_label.pack(padx=10, pady=5)

    # Search Entry widget
    search_entry = tk.Entry(root, width=60, font=("Helvetica", 14), bd=2, relief="solid")
    search_entry.pack(padx=10, pady=10)

    # Listbox for displaying filtered player names
    listbox = tk.Listbox(root, width=60, height=15, font=("Helvetica", 12), bd=2, relief="solid")
    listbox.pack(padx=10, pady=10)

    # Label to display player info (Total Occurrences and Starters)
    info_label = tk.Label(root, text="Select a player to see info.", font=("Helvetica", 14), justify="left", width=60, height=6, anchor="w", bd=2, relief="solid")
    info_label.pack(padx=10, pady=10)

    # Update the listbox based on search input
    def on_search_change(*args):
        search_query = search_entry.get()
        update_search_results(search_query, player_names, listbox)

    # Bind the search entry to update the listbox dynamically
    search_entry.bind("<KeyRelease>", on_search_change)

    # Bind the listbox selection event to display player info
    listbox.bind("<<ListboxSelect>>", lambda event: on_player_select(event, listbox, player_data, info_label))

    # Run the Tkinter loop
    root.mainloop()

# Run the GUI
create_gui()
