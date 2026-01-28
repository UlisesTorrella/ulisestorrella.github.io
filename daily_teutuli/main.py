
import sys
from Reader import Reader

# Get the new id
# if len(sys.argv) < 2:
#     print("Usage: python3 main.py <RESULT_ID>")
#     sys.exit(1)

new_challenge_id = "FpxfEyXydTyi1Dtl"
# sys.argv[1]


reader = Reader(new_challenge_id, test=False)

leaderboard_df = reader.update_leaderboard()
processed_df = reader.update_teutulis()

reader.commit_changes(leaderboard_df, reader.leaderboard_filename)
reader.commit_changes(processed_df, reader.processed_csv)

reader.to_html(leaderboard_df)


