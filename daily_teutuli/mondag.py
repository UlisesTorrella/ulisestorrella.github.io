

import sys
from Reader import Reader

# Get the new id
if len(sys.argv) < 2:
    print("Usage: python3 main.py <RESULT_ID>")
    sys.exit(1)

new_challenge_id = sys.argv[1]


reader = Reader(new_challenge_id, test=False)

results = reader.update_leaderboard()
processed_df = reader.update_teutulis()

reader.commit_changes(results, reader.leaderboard_filename) 
reader.commit_changes(processed_df, reader.processed_csv)

championship_df = reader.week_results(results)
reader.commit_changes(championship_df, reader.championship_filename)

reader.print_podium(results)

reader.archive_week()

