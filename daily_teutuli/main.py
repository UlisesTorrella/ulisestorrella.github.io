
from Reader import Reader

from datetime import datetime

today = datetime.today().weekday()
# Monday = 0, Sunday = 6

if today == 0:
    # Monday    
    reader = Reader(test=False)
    results = reader.update_leaderboard()
    processed_df = reader.update_teutulis()
    reader.commit_changes(results, reader.leaderboard_filename) 
    reader.commit_changes(processed_df, reader.processed_csv)
    championship_df = reader.week_results(results)
    reader.commit_changes(championship_df, reader.championship_filename)
    reader.print_podium(results)
    reader.archive_week()

elif today in (1, 2, 3, 4):
    # Tuesday–Friday
    reader = Reader(test=False)
    leaderboard_df = reader.update_leaderboard()
    processed_df = reader.update_teutulis()
    reader.commit_changes(leaderboard_df, reader.leaderboard_filename)
    reader.commit_changes(processed_df, reader.processed_csv)
    reader.to_html(leaderboard_df)

else:
    # Go to church 
    pass  
