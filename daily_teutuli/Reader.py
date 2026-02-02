import json
import os
import webbrowser


from datetime import datetime, timedelta
import pandas as pd

import urllib.request

class Reader:

    headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0",
                "Cookie": os.environ['GEO_COOKIE'],  # <-- paste from your browser
            }

    leaderboard_filename = "leaderboard.csv"

    point_system = [25,18,15,12,10,8,6,4,2,1]

    maps = {
        "Monday" : {
                        "map": "67756e6c8d7eb43c58faeebe",
                        "timeLimit": 90,
                        "forbidMoving": True,
                        "forbidZooming": False,
                        "forbidRotating": False,
                        "accessLevel": 1,
                        "challengeType": 0,
                        "roundCount": 5,
                        "guessMapType": "roadmap"
                    },
        "Tuesday" : {
                        "map": "61c1d9be6f87f70001eb6055",
                        "timeLimit": 90,
                        "forbidMoving": True,
                        "forbidZooming": False,
                        "forbidRotating": False,
                        "accessLevel": 1,
                        "challengeType": 0,
                        "roundCount": 5,
                        "guessMapType": "roadmap"
                    },
        "Wednesday" : {
                        "map": "5be0de51fe3a84037ca36447",
                        "timeLimit": 90,
                        "forbidMoving": True,
                        "forbidZooming": False,
                        "forbidRotating": False,
                        "accessLevel": 1,
                        "challengeType": 0,
                        "roundCount": 5,
                        "guessMapType": "roadmap"
                    },
        "Thursday" : {
                        "map": "697a0d41ce2eb553139df2cf",
                        "timeLimit": 90,
                        "forbidMoving": True,
                        "forbidZooming": False,
                        "forbidRotating": False,
                        "accessLevel": 1,
                        "challengeType": 0,
                        "roundCount": 5,
                        "guessMapType": "roadmap"
                    },
        "Friday" : {
                        "map": "68b6d567786b461080bd7c7e",
                        "timeLimit": 90,
                        "forbidMoving": True,
                        "forbidZooming": False,
                        "forbidRotating": False,
                        "accessLevel": 1,
                        "challengeType": 0,
                        "roundCount": 5,
                        "guessMapType": "roadmap"
                    }
    }

    def __init__(self, test=False):
        self.processed_csv = "daily_teutulis.csv"
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.processed_df = pd.read_csv(self.processed_csv)

        if test:
            new_challenge_id = "JO0jBSkSkzm8u34z"
        else:
            new_challenge_id = self.create_challenge()

        self.new_challenge_id = new_challenge_id
        self.test = test

        if len(self.processed_df["ID"]) < 1:
            self.challenge_id = "JO0jBSkSkzm8u34z" # arbitrary challenge_id
        else:
            self.challenge_id = str(self.processed_df["ID"].iloc[-1])
            self.last_date = pd.to_datetime(self.processed_df["Date"].iloc[-1])

    def create_challenge(self):
        # Get today's day name (e.g. "Monday")
        today = datetime.now().strftime("%A")

        # Fetch the corresponding dictionary entry
        
        url = "https://www.geoguessr.com/api/v3/challenges"
        headers = self.headers | {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload = self.maps.get(today)

        req = urllib.request.Request(
            url=url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )

        with urllib.request.urlopen(req) as response:
            body = response.read().decode("utf-8")
        response = json.loads(body)
        return response["token"]
    
    
    def fetch(self, challenge_id):
        if self.test: 
            print("USING TEST DATA")
            with open('sample_payload.json', 'r') as file:
                data = json.load(file)
                return data
            raise Exception("coudn't read test file ")

        url = f"https://www.geoguessr.com/api/v3/results/highscores/{challenge_id}?limit=50"

        req = urllib.request.Request(
            url,
            headers=self.headers,
        )

        with urllib.request.urlopen(req) as response:
            data = json.load(response)
            return data
        raise Exception("coudn't open response")


    def update_leaderboard(self):
        print("Updating leaderboard")
        data = self.fetch(self.challenge_id)
        # Extract nicknames
        nicks = []
        points = []
        countryCodes = []
        if "items" in data:
            for item in data["items"]:
                ## Filter games played before 
                game = item["game"]
                player = game.get("player", {})
                nick = player.get("nick", "Unknown Player")
                # This should be done nicer, sorry
                date = pd.to_datetime(item["game"].get("rounds", [])[0].get("startTime", datetime.today()))
                # if date > self.deadline: 
                #     print(f"{nick} played late: {date}")
                # else: 
                # Deadline is when i run the script
                nicks.append(nick)
                totalScore = player.get("totalScore", {})
                countryCode = player.get("countryCode", "ar")
                pts = totalScore.get("amount", 0)
                points.append(int(pts))
                countryCodes.append(countryCode)
                
        # Assign inverse scores: first gets len(nicks), second len(nicks)-1, ...
        scores = [len(nicks) - i for i in range(len(nicks))]
        new_df = pd.DataFrame({"Player": nicks, "Score": scores, "Points" : points, "Country" : countryCodes})
        # Existing DataFrame
        # df = pd.DataFrame({"Player": nicks, "Score": scores})
        leaderboard_df = pd.read_csv(self.leaderboard_filename)

        # Merge new scores with existing leaderboard
        for idx, row in new_df.iterrows():
            nick = row["Player"]
            score = row["Score"]
            pts = row["Points"]
            country = row["Country"]

            if nick in leaderboard_df["Player"].values:
                # Add score to existing one
                leaderboard_df.loc[leaderboard_df["Player"] == nick, "Score"] += score
                leaderboard_df.loc[leaderboard_df["Player"] == nick, "Points"] += pts
                leaderboard_df.loc[leaderboard_df["Player"] == nick, "Country"] = country
            else:
                # Add new row
                leaderboard_df = pd.concat(
                    [leaderboard_df, pd.DataFrame([{"Player": nick, "Score": score, "Points": pts, "Country": country}])],
                    ignore_index=True,
                )

        # Optional: sort by score descending
        leaderboard_df = leaderboard_df.sort_values(by=["Score", "Points"], ascending=[False, False]).reset_index(
            drop=True
        )

        # Save updated leaderboard
        # leaderboard_df.to_csv(self.leaderboard_filename, index=False)
        # print(f"Updated leaderboard saved to {self.leaderboard_filename}")
        return leaderboard_df

    def commit_changes(self, df, filename):
        df.to_csv(filename, index=False)
        print(f"Successfully commited to {filename}")
        return True
        
    def current_leaderboard(self):
        return pd.read_csv(self.leaderboard_filename)

    # takes a list of challenges ids and returns the fetched data of each one of them
    def recover_data(self, challenges):
        challenge_data = []
        for challenge in challenges :
            data = self.fetch(challenge)
            challenge_data.append(data)
        return challenge_data
     

    def update_teutulis(self):
    # File to store processed challenge IDs
        # Append the new processed ID
        new_entry = pd.DataFrame([{"Date": self.today, "ID": self.new_challenge_id}])
        self.processed_df = pd.concat([self.processed_df, new_entry], ignore_index=True)
        # Save back to CSV
        # self.processed_df.to_csv(self.processed_csv, index=False)
        return self.processed_df

    def pretty_format(self, leaderboard_df):
        leaderboard_df['Player'] = leaderboard_df.apply(lambda x: f" {self.countrycode_to_flag(x['Country'])} {x['Player']}", axis=1)
        leaderboard_df['Position'] = range(1, len(leaderboard_df) + 1)
        # Reordering the columns
        leaderboard_df = leaderboard_df[['Position', 'Player', 'Score', 'Points']]
        leaderboard_df = leaderboard_df.rename(columns={'Position': ''})
        return leaderboard_df


    def to_html(self, leaderboard_df):
        # Generate the leaderboard table as an HTML string
    
        leaderboard_df = self.pretty_format(leaderboard_df)
        #leaderboard_df['Country'] = leaderboard_df['Country'].apply(self. countrycode_to_flag)
        leaderboard_html = leaderboard_df.to_html(
            index=False, border=0, justify="center", classes="leaderboard-table"
        )

        championship_df = pd.read_csv(self.
        championship_filename)
        championship_html = championship_df.to_html(
            header=True,
            index=False, border=0, justify="center", classes="leaderboard-table"
        )


        with open("style.css") as css_file:
            css = css_file.read()
            # HTML content with improved styling and blue theme
            html_content = f"""
            <html>
            <head>
                <style>
                {css}
                </style>
            </head>
            <body>
                <p>Daily teutuli of the day:</p>
                <a href="https://www.geoguessr.com/challenge/{self.new_challenge_id}">Challenge</a>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="vertical-align: top; padding: 10px;">
                            <div><h3> Current standings: </h3>
                            {leaderboard_html}</div>
                        </td>
                        <td style="vertical-align: top; padding: 10px;">
                            <div><h3> Guessers Championship standings:</h3>
                            {championship_html}</div>
                        </td>
                    </tr>
                </table>
            </body>
            </html>
            """

            # Write the HTML content to a file
            with open("output.html", "w") as file:
                file.write(html_content)

            print("HTML file has been written to output.html")

            # Open the HTML file in the default browser
            webbrowser.open(f"file://{os.path.abspath('output.html')}")

    championship_filename = "championship.csv"
    def week_results(self, standings_df):
        point_system_padded = self.point_system + [0]*(len(standings_df) - len(self.point_system))
        standings_df["ChampionshipPoints"] = point_system_padded
        championship_df = pd.read_csv(self.
        championship_filename)
        merged = pd.concat([championship_df, standings_df]).groupby("Player", as_index=False)["ChampionshipPoints"].sum()
        merged_sorted = merged.sort_values(by="ChampionshipPoints", ascending=False)
        # merged_sorted.to_csv(self.championship_filename, index=False) 
        # standings_df.drop(columns=["ChampionshipPoints"], inplace=True) # I'm not sure how useful this was
        print("Week results saved to the championship")
        return merged_sorted

    def countrycode_to_flag(self, code):
        try:
            code = code.upper()
            if code == "ZZ":
                return "🌍"
            # Validate: must be 2 letters
            if len(code) != 2 or not code.isalpha():
                return code
            # Convert to regional indicator symbols
            return ''.join(chr(127397 + ord(c)) for c in code)
        except:
            return code
    
    def print_podium(self, standings_df):

        leaderboard_df = self.pretty_format(standings_df)
        if not leaderboard_df.empty:
            if len(leaderboard_df) >= 1:
                leaderboard_df.iat[0, 0] = f"🥇"
            if len(leaderboard_df) >= 2:
                leaderboard_df.iat[1, 0] = f"🥈"
            if len(leaderboard_df) >= 3:
                leaderboard_df.iat[2, 0] = f"🥉"

        # Convert dataframe (with emojis) to HTML table
        leaderboard_html = leaderboard_df.to_html(
            header=True,
            index=False, border=0, justify="center", classes="leaderboard-table"
        )

        championship_df = pd.read_csv(self.
        championship_filename)
        championship_html = championship_df.to_html(
            header=True,
            index=False, border=0, justify="center", classes="leaderboard-table"
        )

        # HTML content with improved styling and blue theme
        html_content = f"""
        <html>
        <head>
            <style>
            </style>
        </head>
        <body>
            <p>Daily teutuli of the day:</p>
            <a href="https://www.geoguessr.com/challenge/{self.new_challenge_id}">Challenge</a>
            <div style="display: flex; gap: 20px;">
                <div><h3> Grand Prix results: </h3>
                {leaderboard_html}</div>
                <div><h3> Guessers Championship standings:</h3>
                {championship_html}</div>
            </div>
        </body>
        </html>
        """

        # Write the HTML content to a file
        with open("output.html", "w") as file:
            file.write(html_content)

        print("HTML file has been written to output.html")

        # Open the HTML file in the default browser
        webbrowser.open(f"file://{os.path.abspath('output.html')}")


    archive_folder = "archive"
    def archive_week(self):
        leaderboard_df = pd.read_csv(self.leaderboard_filename)
        # Get current ISO week number
        week_number = (datetime.now() - timedelta(days=7)).isocalendar()[1]
        year = datetime.now().year
        archive_filename = f"leaderboard_{year}_week_{week_number}.csv"
        archive_path = os.path.join(self.archive_folder, archive_filename)        
        leaderboard_df.to_csv(archive_path, index=False, encoding="utf-8")

        print(f"✅ Leaderboard archived at: {archive_path}")

        # Clear the leaderboard (keep only headers)
        empty_df = leaderboard_df.iloc[0:0]  # same columns, no rows
        empty_df.to_csv(self.leaderboard_filename, index=False, encoding="utf-8")
        print(f"✅ Leaderboard cleared at: {self.leaderboard_filename}")
