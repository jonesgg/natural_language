import mysql.connector
from config import DB_CONFIG

def connect_db():
    return mysql.connector.connect(**DB_CONFIG)

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    # ----- PERSON -----
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Person (
            PersonID INT PRIMARY KEY AUTO_INCREMENT,
            FirstName VARCHAR(30) NOT NULL,
            LastName VARCHAR(30) NOT NULL,
            BirthDate DATE,
            HeightCM INT,
            WeightKG INT
        );
    """)

    # ----- TEAM -----
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Team (
            TeamID INT PRIMARY KEY AUTO_INCREMENT,
            TeamName VARCHAR(50) NOT NULL,
            City VARCHAR(50),
            HomeArena VARCHAR(50)
        );
    """)

    # ----- PLAYER -----
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Player (
            PlayerID INT PRIMARY KEY,
            TeamID INT NOT NULL,
            JerseyNumber INT NOT NULL,
            Position VARCHAR(20),
            FOREIGN KEY (PlayerID) REFERENCES Person(PersonID),
            FOREIGN KEY (TeamID) REFERENCES Team(TeamID)
        );
    """)

    # ----- COACH -----
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Coach (
            CoachID INT PRIMARY KEY,
            TeamID INT NOT NULL,
            Role VARCHAR(30),
            FOREIGN KEY (CoachID) REFERENCES Person(PersonID),
            FOREIGN KEY (TeamID) REFERENCES Team(TeamID)
        );
    """)

    # ----- GAME -----
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Game (
            GameID INT PRIMARY KEY AUTO_INCREMENT,
            HomeTeamID INT NOT NULL,
            AwayTeamID INT NOT NULL,
            GameDate DATETIME NOT NULL,
            Location VARCHAR(50),
            HomeScore INT DEFAULT 0,
            AwayScore INT DEFAULT 0,
            FOREIGN KEY (HomeTeamID) REFERENCES Team(TeamID),
            FOREIGN KEY (AwayTeamID) REFERENCES Team(TeamID)
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Tables created")

def clear_tables():
    """Clear all data from tables (in correct order due to foreign keys)."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Game")
    cursor.execute("DELETE FROM Coach")
    cursor.execute("DELETE FROM Player")
    cursor.execute("DELETE FROM Person")
    cursor.execute("DELETE FROM Team")

    cursor.execute("ALTER TABLE Person AUTO_INCREMENT = 1")
    cursor.execute("ALTER TABLE Team AUTO_INCREMENT = 1")
    cursor.execute("ALTER TABLE Game AUTO_INCREMENT = 1")
    conn.commit()
    cursor.close()
    conn.close()
    print("Tables cleared")

def insert_sample_data():
    conn = connect_db()
    cursor = conn.cursor()

    # Clear existing data first
    clear_tables()

    # ----- INSERT 3 TEAMS -----
    teams = [
        ("Provo Wildcats", "Provo", "Marriott Center"),
        ("Salt Lake Stingers", "Salt Lake City", "Delta Center"),
        ("Ogden Thunder", "Ogden", "Dee Events Center"),
    ]
    cursor.executemany(
        "INSERT INTO Team (TeamName, City, HomeArena) VALUES (%s, %s, %s)", teams
    )
    print("3 teams inserted")

    # ----- INSERT PERSONS (15 players + 6 coaches = 21 people) -----
    persons = [
        # Team 1 Players (PersonID 1-5)
        ("Marcus", "Johnson", "1998-03-15", 196, 93),
        ("Tyler", "Williams", "2000-07-22", 188, 82),
        ("DeShawn", "Carter", "1999-11-08", 201, 98),
        ("Kyle", "Anderson", "2001-02-14", 193, 88),
        ("Jamal", "Thompson", "1997-09-30", 185, 79),
        # Team 2 Players (PersonID 6-10)
        ("Brandon", "Davis", "1999-05-11", 198, 95),
        ("Chris", "Martinez", "2000-01-25", 191, 86),
        ("Andre", "Wilson", "1998-08-19", 203, 102),
        ("Terrence", "Moore", "2001-04-07", 187, 81),
        ("Malik", "Taylor", "1997-12-03", 195, 91),
        # Team 3 Players (PersonID 11-15)
        ("Jordan", "Brown", "1999-06-28", 199, 97),
        ("Isaiah", "Garcia", "2000-10-14", 186, 80),
        ("Darius", "Robinson", "1998-02-20", 205, 105),
        ("Kevin", "Lee", "2001-07-16", 190, 84),
        ("Aaron", "Clark", "1997-11-09", 194, 89),
        # Team 1 Coaches (PersonID 16-17)
        ("Robert", "Stevens", "1970-04-12", 185, 88),
        ("Michael", "Foster", "1975-08-23", 180, 82),
        # Team 2 Coaches (PersonID 18-19)
        ("James", "Mitchell", "1968-01-30", 183, 90),
        ("David", "Campbell", "1972-06-17", 178, 79),
        # Team 3 Coaches (PersonID 20-21)
        ("William", "Rivera", "1965-09-05", 181, 85),
        ("Richard", "Phillips", "1973-03-28", 176, 77),
    ]
    cursor.executemany(
        "INSERT INTO Person (FirstName, LastName, BirthDate, HeightCM, WeightKG) VALUES (%s, %s, %s, %s, %s)",
        persons
    )
    print("21 persons inserted")

    # ----- INSERT 15 PLAYERS (5 per team) -----
    players = [
        # Team 1 (TeamID=1)
        (1, 1, 23, "Point Guard"),
        (2, 1, 11, "Shooting Guard"),
        (3, 1, 34, "Center"),
        (4, 1, 5, "Small Forward"),
        (5, 1, 22, "Power Forward"),
        # Team 2 (TeamID=2)
        (6, 2, 7, "Point Guard"),
        (7, 2, 14, "Shooting Guard"),
        (8, 2, 42, "Center"),
        (9, 2, 3, "Small Forward"),
        (10, 2, 21, "Power Forward"),
        # Team 3 (TeamID=3)
        (11, 3, 10, "Point Guard"),
        (12, 3, 24, "Shooting Guard"),
        (13, 3, 55, "Center"),
        (14, 3, 8, "Small Forward"),
        (15, 3, 33, "Power Forward"),
    ]
    cursor.executemany(
        "INSERT INTO Player (PlayerID, TeamID, JerseyNumber, Position) VALUES (%s, %s, %s, %s)",
        players
    )
    print("15 players inserted")

    # ----- INSERT 6 COACHES (2 per team) -----
    coaches = [
        (16, 1, "Head Coach"),
        (17, 1, "Assistant Coach"),
        (18, 2, "Head Coach"),
        (19, 2, "Assistant Coach"),
        (20, 3, "Head Coach"),
        (21, 3, "Assistant Coach"),
    ]
    cursor.executemany(
        "INSERT INTO Coach (CoachID, TeamID, Role) VALUES (%s, %s, %s)",
        coaches
    )
    print("6 coaches inserted")

    # ----- INSERT 9 GAMES (each team plays 6 games, 3 home / 3 away) -----
    games = [
        # Team 1 vs Team 2 (3 games)
        (1, 2, "2025-01-10 19:00:00", "Marriott Center", 88, 79),
        (2, 1, "2025-01-24 18:30:00", "Delta Center", 92, 95),
        (1, 2, "2025-02-14 19:00:00", "Marriott Center", 101, 98),
        # Team 1 vs Team 3 (3 games)
        (1, 3, "2025-01-17 20:00:00", "Marriott Center", 85, 82),
        (3, 1, "2025-02-01 17:00:00", "Dee Events Center", 78, 81),
        (3, 1, "2025-02-28 19:30:00", "Dee Events Center", 89, 87),
        # Team 2 vs Team 3 (3 games)
        (2, 3, "2025-01-31 18:00:00", "Delta Center", 94, 88),
        (3, 2, "2025-02-07 19:00:00", "Dee Events Center", 76, 83),
        (2, 3, "2025-02-21 20:00:00", "Delta Center", 99, 102),
    ]
    cursor.executemany(
        "INSERT INTO Game (HomeTeamID, AwayTeamID, GameDate, Location, HomeScore, AwayScore) VALUES (%s, %s, %s, %s, %s, %s)",
        games
    )
    print("9 games inserted")

    conn.commit()
    cursor.close()
    conn.close()
    print("All sample data inserted")

def get_all_players_with_teams():
    """Query all players with their team names."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            p.FirstName,
            p.LastName,
            t.TeamName,
            pl.JerseyNumber,
            pl.Position
        FROM Player pl
        JOIN Person p ON pl.PlayerID = p.PersonID
        JOIN Team t ON pl.TeamID = t.TeamID
        ORDER BY t.TeamName, pl.Position
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    print("\n--- All Players with Teams ---")
    current_team = None
    for first, last, team, jersey, position in rows:
        if team != current_team:
            print(f"\n{team}:")
            current_team = team
        print(f"  #{jersey} {first} {last} - {position}")
    print()

# ----- RUN EVERYTHING -----
if __name__ == "__main__":
    # create_tables()
    # insert_sample_data()
    get_all_players_with_teams()