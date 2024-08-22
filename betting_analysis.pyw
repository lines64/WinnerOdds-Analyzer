import pandas as pd
import plotly.express as px
import webbrowser
import threading
from tkinter import Tk, Label, Button, filedialog, messagebox, Frame, Canvas

def validate_csv(file_path):
    required_columns = ['Bookie', 'Profit', 'Stake', 'Odds', 'Winner', 'Bet', 'Bet date', 'Tournament']
    try:
        data = pd.read_csv(file_path, skipfooter=1, engine='python')
        if all(column in data.columns for column in required_columns):
            return True
        else:
            return False
    except Exception as e:
        return False

def classify_tournament(tournament_name):
    if 'ATP' in tournament_name:
        return 'ATP'
    elif 'WTA' in tournament_name:
        return 'WTA'
    elif 'Challenger' in tournament_name:
        return 'CH'
    elif 'ITF-M' in tournament_name:
        return 'ITF-M'
    elif 'ITF-W' in tournament_name:
        return 'ITF-W'
    else:
        return 'Other'

def classify_bookmaker(bookie):
    sharp = {'BetDAQ', 'Betfair Exchange', 'ISN', 'Sharpbet', 'Matchbook', '3ET', 'Pinnacle', 'IBC', 'penta88'}
    semi_sharp = {'Betonline', 'Lowvig', 'Tigergaming', 'Bookmaker', '5dimes'}
    offshore = {'Betonline', 'Lowvig', 'Tigergaming', 'Bookmaker', '5dimes', 'Mybookie', 'Everygame', 'WagerWeb', 'bodog', 'bovada'}
    betting_exchanges = {'BetDAQ', 'Betfair Exchange', 'Matchbook'}
    
    if bookie in sharp:
        return 'Sharp'
    elif bookie in semi_sharp:
        return 'Semi Sharp'
    elif bookie in offshore:
        return 'Offshore'
    elif bookie in betting_exchanges:
        return 'Betting Exchanges'
    else:
        return 'Soft'

def generate_report(file_path):
    data = pd.read_csv(file_path, skipfooter=1, engine='python')

    data['Tournament_Type'] = data['Tournament'].apply(classify_tournament)

    data['Bookmaker_Group'] = data['Bookie'].apply(classify_bookmaker)

    bookie_stats = data.groupby('Bookie').agg(
        Total_Profit=('Profit', 'sum'),
        Number_of_Bets=('Profit', 'count'),
        Total_Turnover=('Stake', 'sum'),
        Average_Odds=('Odds', 'mean')
    ).reset_index()

    bookie_stats['Yield'] = (bookie_stats['Total_Profit'] / bookie_stats['Total_Turnover']) * 100

    bookie_stats['Total_Turnover'] = bookie_stats['Total_Turnover'].apply(lambda x: f"${x:.2f}")
    bookie_stats['Yield'] = bookie_stats['Yield'].apply(lambda x: f"{x:.2f}%")
    bookie_stats['Average_Odds'] = bookie_stats['Average_Odds'].apply(lambda x: f"{x:.2f}")

    bookie_stats = bookie_stats.sort_values(by='Number_of_Bets', ascending=False)

    total_profit = data['Profit'].sum()
    total_turnover = data['Stake'].sum()
    total_number_of_bets = len(data)
    win_rate = (data['Winner'] == data['Bet']).mean() * 100

    data['Bet date'] = pd.to_datetime(data['Bet date'])
    profit_per_day = total_profit / (data['Bet date'].max() - data['Bet date'].min()).days

    won_bets = (data['Profit'] > 0).sum()
    lost_bets = (data['Profit'] < 0).sum()
    void_bets = (data['Profit'] == 0).sum()

    data_sorted = data.sort_values('Bet date')

    data_sorted['Cumulative Profit'] = data_sorted['Profit'].cumsum()

    best_bookie_by_profit = bookie_stats.loc[bookie_stats['Total_Profit'].idxmax()]['Bookie']
    worst_bookie_by_profit = bookie_stats.loc[bookie_stats['Total_Profit'].idxmin()]['Bookie']

    best_bookie_data = data_sorted[data_sorted['Bookie'] == best_bookie_by_profit].copy()
    best_bookie_data.loc[:, 'Cumulative Profit'] = best_bookie_data['Profit'].cumsum()

    worst_bookie_data = data_sorted[data_sorted['Bookie'] == worst_bookie_by_profit].copy()
    worst_bookie_data.loc[:, 'Cumulative Profit'] = worst_bookie_data['Profit'].cumsum()

    tournament_types = ['ATP', 'WTA', 'CH', 'ITF-M', 'ITF-W']
    tournament_profit_stats = data.groupby(['Bookie', 'Tournament_Type']).agg(Total_Profit=('Profit', 'sum')).unstack().fillna(0)
    tournament_profit_stats.columns = tournament_profit_stats.columns.droplevel(0)
    tournament_profit_stats['Total_Profit'] = tournament_profit_stats[tournament_types].sum(axis=1)
    tournament_profit_stats = tournament_profit_stats.sort_values(by='Total_Profit', ascending=False).reset_index()

    tournament_bets_turnover_stats = data.groupby(['Bookie', 'Tournament_Type']).agg(Number_of_Bets=('Profit', 'count'), Turnover=('Stake', 'sum')).unstack().fillna(0)
    tournament_bets_turnover_stats.columns = ['_'.join(col).strip() for col in tournament_bets_turnover_stats.columns.values]
    tournament_bets_turnover_stats['Total_Turnover'] = tournament_bets_turnover_stats.filter(like='Turnover').sum(axis=1)
    tournament_bets_turnover_stats = tournament_bets_turnover_stats.sort_values(by='Total_Turnover', ascending=False).reset_index()

    tournament_roi_stats = data.groupby('Tournament_Type').agg(Total_Profit=('Profit', 'sum'), Total_Stake=('Stake', 'sum'))
    tournament_roi_stats['ROI'] = (tournament_roi_stats['Total_Profit'] / tournament_roi_stats['Total_Stake']) * 100
    tournament_roi_stats = tournament_roi_stats['ROI'].reset_index().sort_values(by='ROI', ascending=False)

    bookmaker_group_stats = data.groupby('Bookmaker_Group').agg(
        Total_Profit=('Profit', 'sum'),
        Number_of_Bets=('Profit', 'count'),
        Total_Turnover=('Stake', 'sum')
    ).reset_index()
    bookmaker_group_stats['Yield'] = (bookmaker_group_stats['Total_Profit'] / bookmaker_group_stats['Total_Turnover']) * 100
    bookmaker_group_stats['Total_Turnover'] = bookmaker_group_stats['Total_Turnover'].apply(lambda x: f"${x:.2f}")
    bookmaker_group_stats['Yield'] = bookmaker_group_stats['Yield'].apply(lambda x: f"{x:.2f}%")
    bookmaker_group_stats['Total_Profit'] = bookmaker_group_stats['Total_Profit'].apply(lambda x: f"${x:.2f}")
    bookmaker_group_stats = bookmaker_group_stats.sort_values(by='Total_Profit', ascending=False)

    sharp_tooltip = "BetDAQ, Betfair Exchange, ISN, Sharpbet, Matchbook, 3ET, Pinnacle, IBC, penta88"
    semi_sharp_tooltip = "Betonline, Lowvig, Tigergaming, Bookmaker, 5dimes"
    offshore_tooltip = "Betonline, Lowvig, Tigergaming, Bookmaker, 5dimes, Mybookie, Everygame, WagerWeb, bodog, bovada"

    bookmaker_group_stats['Bookmaker_Group'] = bookmaker_group_stats['Bookmaker_Group'].apply(
        lambda x: f'<span title="{sharp_tooltip if x == "Sharp" else semi_sharp_tooltip if x == "Semi Sharp" else offshore_tooltip if x == "Offshore" else ""}">{x}</span>'
    )

    fig = px.line(data_sorted, x='Bet date', y='Cumulative Profit', title='Cumulative Profit Over Time')
    fig.add_scatter(x=best_bookie_data['Bet date'], y=best_bookie_data['Cumulative Profit'], mode='lines', name=f'Best Bookmaker ({best_bookie_by_profit})')
    fig.add_scatter(x=worst_bookie_data['Bet date'], y=worst_bookie_data['Cumulative Profit'], mode='lines', name=f'Worst Bookmaker ({worst_bookie_by_profit})')
    fig.update_layout(width=1200)
    fig.write_html('cumulative_profit_combined.html')

    generate_html_report(total_profit, win_rate, profit_per_day, total_turnover, total_number_of_bets, won_bets, lost_bets, void_bets, bookie_stats, best_bookie_by_profit, worst_bookie_by_profit, best_bookie_data, worst_bookie_data, data_sorted, tournament_profit_stats, tournament_bets_turnover_stats, tournament_roi_stats, bookmaker_group_stats)

def generate_html_report(total_profit, win_rate, profit_per_day, total_turnover, total_number_of_bets, won_bets, lost_bets, void_bets, bookie_stats, best_bookie_by_profit, worst_bookie_by_profit, best_bookie_data, worst_bookie_data, data_sorted, tournament_profit_stats, tournament_bets_turnover_stats, tournament_roi_stats, bookmaker_group_stats):
    summary_data = [
        ('Total Profit', f"${total_profit:.2f}"),
        ('Win Rate', f"{win_rate:.2f}%"),
        ('Profit per Day', f"${profit_per_day:.2f}"),
        ('Total Turnover', f"${total_turnover:.2f}"),
        ('Total Number of Bets', f"{total_number_of_bets}"),
        ('Won Bets', f"{won_bets}"),
        ('Lost Bets', f"{lost_bets}"),
        ('Void Bets', f"{void_bets}")
    ]

    best_bookie_summary_data = [
        ('Total Profit', f"${best_bookie_data['Profit'].sum():.2f}"),
        ('Win Rate', f"{(best_bookie_data['Winner'] == best_bookie_data['Bet']).mean() * 100:.2f}%"),
        ('Yield', f"{(best_bookie_data['Profit'].sum() / best_bookie_data['Stake'].sum()) * 100:.2f}%"),
        ('Total Turnover', f"${best_bookie_data['Stake'].sum():.2f}"),
        ('Total Number of Bets', f"{len(best_bookie_data)}"),
        ('Won Bets', f"{(best_bookie_data['Profit'] > 0).sum()}"),
        ('Lost Bets', f"{(best_bookie_data['Profit'] < 0).sum()}"),
        ('Void Bets', f"{(best_bookie_data['Profit'] == 0).sum()}")
    ]

    worst_bookie_summary_data = [
        ('Total Profit', f"${worst_bookie_data['Profit'].sum():.2f}"),
        ('Win Rate', f"{(worst_bookie_data['Winner'] == worst_bookie_data['Bet']).mean() * 100:.2f}%"),
        ('Yield', f"{(worst_bookie_data['Profit'].sum() / worst_bookie_data['Stake'].sum()) * 100:.2f}%"),
        ('Total Turnover', f"${worst_bookie_data['Stake'].sum():.2f}"),
        ('Total Number of Bets', f"{len(worst_bookie_data)}"),
        ('Won Bets', f"{(worst_bookie_data['Profit'] > 0).sum()}"),
        ('Lost Bets', f"{(worst_bookie_data['Profit'] < 0).sum()}"),
        ('Void Bets', f"{(worst_bookie_data['Profit'] == 0).sum()}")
    ]

    left_summary_data = summary_data[:4]
    right_summary_data = summary_data[4:]

    summary_html = """
    <div class="summary-container">
        <table class="summary-table">
            <tr><th>Metric</th><th>Value</th></tr>
    """
    summary_html += "".join(f"<tr><td>{key}</td><td>{value}</td></tr>" for key, value in left_summary_data)
    summary_html += """
        </table>
        <table class="summary-table">
            <tr><th>Metric</th><th>Value</th></tr>
    """
    summary_html += "".join(f"<tr><td>{key}</td><td>{value}</td></tr>" for key, value in right_summary_data)
    summary_html += """
        </table>
    </div>
    """

    best_bookie_html = f"""
    <div class="summary-container">
        <table class="summary-table">
            <tr><th>Metric</th><th>Value</th></tr>
    """
    best_bookie_html += "".join(f"<tr><td>{key}</td><td>{value}</td></tr>" for key, value in best_bookie_summary_data[:4])
    best_bookie_html += """
        </table>
        <table class="summary-table">
            <tr><th>Metric</th><th>Value</th></tr>
    """
    best_bookie_html += "".join(f"<tr><td>{key}</td><td>{value}</td></tr>" for key, value in best_bookie_summary_data[4:])
    best_bookie_html += """
        </table>
    </div>
    """

    worst_bookie_html = f"""
    <div class="summary-container">
        <table class="summary-table">
            <tr><th>Metric</th><th>Value</th></tr>
    """
    worst_bookie_html += "".join(f"<tr><td>{key}</td><td>{value}</td></tr>" for key, value in worst_bookie_summary_data[:4])
    worst_bookie_html += """
        </table>
        <table class="summary-table">
            <tr><th>Metric</th><th>Value</th></tr>
    """
    worst_bookie_html += "".join(f"<tr><td>{key}</td><td>{value}</td></tr>" for key, value in worst_bookie_summary_data[4:])
    worst_bookie_html += """
        </table>
    </div>
    """

    bookie_html = """
    <h2>Total Profit by Bookmaker</h2>
    <table class="bookie-table">
        <tr><th>Bookie</th><th>Total Profit</th><th>Number of Bets</th><th>Total Turnover</th><th>Yield</th><th>Average Odds</th></tr>
    """
    bookie_html += "".join(
        f"<tr><td>{row['Bookie']}</td><td>${row['Total_Profit']:.2f}</td><td>{row['Number_of_Bets']}</td><td>{row['Total_Turnover']}</td><td>{row['Yield']}</td><td>{row['Average_Odds']}</td></tr>"
        for _, row in bookie_stats.iterrows()
    )
    bookie_html += """
    </table>
    """

    tournament_html = """
    <h2>Profit Comparison per Tournament Type</h2>
    <table class="tournament-table">
        <tr><th>Bookie</th><th>ATP</th><th>WTA</th><th>Challenger</th><th>ITF-M</th><th>ITF-W</th><th>Total Profit</th></tr>
    """
    tournament_html += "".join(
        f"<tr><td>{row['Bookie']}</td><td>${row['ATP']:.2f}</td><td>${row['WTA']:.2f}</td><td>${row['CH']:.2f}</td><td>${row['ITF-M']:.2f}</td><td>${row['ITF-W']:.2f}</td><td>${row['Total_Profit']:.2f}</td></tr>"
        for _, row in tournament_profit_stats.iterrows()
    )
    tournament_html += """
    </table>
    """

    bets_turnover_html = """
    <h2>Turnover / Number of Bets per Tournament Type</h2>
    <table class="tournament-table">
        <tr><th>Bookie</th>
            <th>ATP</th><th>WTA</th><th>Challenger</th><th>ITF-M</th><th>ITF-W</th><th>Total Turnover</th></tr>
    """
    for _, row in tournament_bets_turnover_stats.iterrows():
        bets_turnover_html += f"<tr><td>{row['Bookie']}</td>"
        for tt in ['ATP', 'WTA', 'CH', 'ITF-M', 'ITF-W']:
            bets_turnover_html += f"<td>${row[f'Turnover_{tt}']:.2f} ({int(row[f'Number_of_Bets_{tt}'])})</td>"
        bets_turnover_html += f"<td>${row['Total_Turnover']:.2f}</td></tr>"
    bets_turnover_html += """
    </table>
    """

    roi_html = """
    <h2>ROI per Tournament Type</h2>
    <table class="roi-table">
        <tr><th>Tournament Type</th><th>ROI</th></tr>
    """
    roi_html += "".join(
        f"<tr><td>{row['Tournament_Type']}</td><td>{row['ROI']:.2f}%</td></tr>"
        for _, row in tournament_roi_stats.iterrows()
    )
    roi_html += """
    </table>
    """

    bookmaker_group_html = """
    <h2>Comparison between Different Groups of Bookmakers</h2>
    <table class="bookmaker-group-table">
        <tr><th>Bookmaker Group</th><th>Total Profit</th><th>Yield</th><th>Total Turnover</th><th>Number of Bets</th></tr>
    """
    bookmaker_group_html += "".join(
        f"<tr><td>{row['Bookmaker_Group']}</td><td>{row['Total_Profit']}</td><td>{row['Yield']}</td><td>{row['Total_Turnover']}</td><td>{row['Number_of_Bets']}</td></tr>"
        for _, row in bookmaker_group_stats.iterrows()
    )
    bookmaker_group_html += """
    </table>
    """

    html_content = f"""
    <html>
    <head>
        <title>WinnerOdds Tennis Betting History Analysis: Bookmakers Data</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
            }}
            h1, h2, h4 {{
                text-align: center;
            }}
            .summary-container {{
                display: flex;
                justify-content: center;
                margin-bottom: 20px;
            }}
            .summary-table {{
                width: 40%;
                margin: 0 20px;
                border-collapse: collapse;
            }}
            .summary-table th, .summary-table td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: center;
            }}
            .summary-table th {{
                background-color: #f2f2f2;
            }}
            .bookie-table {{
                width: 80%;
                margin: 20px auto;
                border-collapse: collapse;
            }}
            .bookie-table th, .bookie-table td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: center;
            }}
            .bookie-table th {{
                background-color: #f2f2f2;
            }}
            .tournament-table {{
                width: 80%;
                margin: 20px auto;
                border-collapse: collapse;
            }}
            .tournament-table th, .tournament-table td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: center;
            }}
            .tournament-table th {{
                background-color: #f2f2f2;
            }}
            .roi-table {{
                width: 80%;
                margin: 20px auto;
                border-collapse: collapse;
            }}
            .roi-table th, .roi-table td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: center;
            }}
            .roi-table th {{
                background-color: #f2f2f2;
            }}
            .bookmaker-group-table {{
                width: 80%;
                margin: 20px auto;
                border-collapse: collapse;
            }}
            .bookmaker-group-table th, .bookmaker-group-table td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: center;
            }}
            .bookmaker-group-table th {{
                background-color: #f2f2f2;
            }}
            .image-container {{
                text-align: center;
                margin-top: 20px;
                width: 80%;
                margin: 0 auto;
            }}
            span[title] {{
                border-bottom: 1px dotted black;
                cursor: help;
            }}
        </style>
    </head>
    <body>
        <h1>WinnerOdds Tennis Betting History Analysis: Bookmakers Data</h1>
        <h2>Summary</h2>
        {summary_html}
        <h4>Best Bookmaker: {best_bookie_by_profit}</h4>
        {best_bookie_html}
        <h4>Worst Bookmaker: {worst_bookie_by_profit}</h4>
        {worst_bookie_html}
        <div class="image-container">
            <iframe src="cumulative_profit_combined.html" width="100%" height="600"></iframe>
        </div>
        {bookie_html}
        {tournament_html}
        {bets_turnover_html}
        {roi_html}
        {bookmaker_group_html}
    </body>
    </html>
    """

    with open('WinnerOdds_Betting_History_Analysis.html', 'w') as f:
        f.write(html_content)

    webbrowser.open('WinnerOdds_Betting_History_Analysis.html')
    print("HTML report generated successfully. Press Enter to exit.")

def start_generation(file_path, root, select_button, exit_button):
    select_button.config(state="disabled")
    exit_button.config(state="disabled")
    generate_report(file_path)
    root.quit()
    root.destroy()

def select_file(root, select_button, exit_button):
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        if validate_csv(file_path):
            threading.Thread(target=start_generation, args=(file_path, root, select_button, exit_button)).start()
        else:
            messagebox.showerror("Error", "Invalid file format. Please select a WinnerOdds Tennis history CSV file.")
            select_button.config(state="normal")
            exit_button.config(state="normal")
    else:
        select_button.config(state="normal")
        exit_button.config(state="normal")

def open_url(url):
    webbrowser.open_new(url)

def main():
    root = Tk()
    root.title("WinnerOdds Tennis History Analyzer")

    window_width = 500
    window_height = 170
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    position_top = int(screen_height / 2 - window_height / 2)
    position_right = int(screen_width / 2 - window_width / 2)
    root.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

    label = Label(root, text="Select a CSV file to generate the report")
    label.pack(pady=10)

    select_button = Button(root, text="Select File", command=lambda: select_file(root, select_button, exit_button))
    select_button.pack(pady=5)

    exit_button = Button(root, text="Exit", command=root.quit)
    exit_button.pack(pady=5)

    canvas = Canvas(root, width=500, height=1, bg='black')
    canvas.pack(pady=5)

    footer_frame = Frame(root)
    footer_frame.pack(pady=5)

    btn1 = Button(footer_frame, text="Bookmaker Clones (coming soon)", command=lambda: open_url("#"))
    btn1.grid(row=0, column=0, padx=5)

    btn2 = Button(footer_frame, text="WinnerOdds", command=lambda: open_url("https://www.winnerodds.com/#lay64"))
    btn2.grid(row=0, column=1, padx=5)

    btn3 = Button(footer_frame, text="Betting Tools (coming soon)", command=lambda: open_url("#"))
    btn3.grid(row=0, column=2, padx=5)

    root.mainloop()

if __name__ == "__main__":
    main()