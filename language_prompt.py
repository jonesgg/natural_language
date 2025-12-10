import mysql.connector
from openai import OpenAI
from config import DB_CONFIG, OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

# Schema for prompt
SCHEMA_CONTEXT = """
Tables in the database:

Person (PersonID INT PK, FirstName VARCHAR, LastName VARCHAR, BirthDate DATE, HeightCM INT, WeightKG INT)
Team (TeamID INT PK, TeamName VARCHAR, City VARCHAR, HomeArena VARCHAR)
Player (PlayerID INT PK/FK->Person, TeamID FK->Team, JerseyNumber INT, Position VARCHAR)
Coach (CoachID INT PK/FK->Person, TeamID FK->Team, Role VARCHAR)
Game (GameID INT PK, HomeTeamID FK->Team, AwayTeamID FK->Team, GameDate DATETIME, Location VARCHAR, HomeScore INT, AwayScore INT)

IMPORTANT: When searching for teams by name, use LIKE with wildcards for partial matches (e.g., WHERE TeamName LIKE '%Stingers%').
"""

def connect_db():
    return mysql.connector.connect(**DB_CONFIG)

def get_sql_query(user_question: str) -> str:
    """Ask ChatGPT to generate a SQL query from the user's question."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"""You are a SQL expert. Given the following database schema, generate ONLY a valid MySQL query to answer the user's question. 
Return ONLY the SQL query, no explanations, no markdown, no code blocks.

{SCHEMA_CONTEXT}"""
            },
            {
                "role": "user",
                "content": user_question
            }
        ],
        temperature=0
    )
    return response.choices[0].message.content.strip()

def execute_query(query: str):
    """Execute the SQL query and return results."""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        return columns, rows, None
    except Exception as e:
        return None, None, str(e)
    finally:
        cursor.close()
        conn.close()

def explain_results(user_question: str, query: str, columns: list, rows: list) -> str:
    """Ask ChatGPT to explain the query results in natural language."""
    
    if not rows:
        results_str = "No results found."
    else:
        results_str = f"Columns: {columns}\nRows:\n"
        for row in rows:
            results_str += f"  {row}\n"
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that explains database query results in clear, natural language. Be concise but informative."
            },
            {
                "role": "user",
                "content": f"""The user asked: "{user_question}"

I ran this SQL query:
{query}

Here are the results:
{results_str}

Please explain these results in a friendly, easy-to-understand way."""
            }
        ],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def main():
    print('Welcome to BallerSQL! Your one stop for all basketball team quesitons.')
    print("Ask questions about players, teams, coaches, and games!")
    print("Type 'quit' to exit.\n")
    
    while True:
        user_input = input("Your question: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
        
        if not user_input:
            continue
        
        print("\nGenerating SQL query...")
        sql_query = get_sql_query(user_input)
        print(f"Query: {sql_query}\n")
        
        print("Executing query...")
        columns, rows, error = execute_query(sql_query)
        
        if error:
            print(f"Error: {error}\n")
            continue
        
        print(f"Found {len(rows)} result(s)\n")
        
        print("Analyzing results...")
        explanation = explain_results(user_input, sql_query, columns, rows)
        print(f"\nAnswer:\n{explanation}\n")

if __name__ == "__main__":
    main()

