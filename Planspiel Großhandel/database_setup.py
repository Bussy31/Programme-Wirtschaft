import sqlite3


def create_database():
    conn = sqlite3.connect('landhandel.db')
    c = conn.cursor()

    # 1. Spielstatus
    c.execute('''
              CREATE TABLE IF NOT EXISTS Game_State
              (
                  game_id
                  TEXT
                  PRIMARY
                  KEY,
                  current_round
                  INTEGER,
                  market_news
                  TEXT
              )
              ''')

    # 2. Teams (Nur noch Kontostand, das Lager wird ausgelagert)
    c.execute('''
              CREATE TABLE IF NOT EXISTS Teams
              (
                  team_name
                  TEXT
                  PRIMARY
                  KEY,
                  game_id
                  TEXT,
                  bank_balance
                  REAL
              )
              ''')

    # 3. Produkte (Unser Katalog)
    c.execute('''
              CREATE TABLE IF NOT EXISTS Products
              (
                  product_id
                  INTEGER
                  PRIMARY
                  KEY,
                  name
                  TEXT,
                  base_purchase_price
                  REAL,
                  storage_cost_per_unit
                  REAL
              )
              ''')

    # 4. Lagerbestand (Welches Team hat wie viel von welchem Produkt?)
    c.execute('''
              CREATE TABLE IF NOT EXISTS Inventory
              (
                  team_name
                  TEXT,
                  product_id
                  INTEGER,
                  quantity
                  INTEGER,
                  PRIMARY
                  KEY
              (
                  team_name,
                  product_id
              )
                  )
              ''')

    # 5. Entscheidungen pro Produkt in einer Runde
    c.execute('''
              CREATE TABLE IF NOT EXISTS Product_Decisions
              (
                  id
                  INTEGER
                  PRIMARY
                  KEY
                  AUTOINCREMENT,
                  team_name
                  TEXT,
                  round
                  INTEGER,
                  product_id
                  INTEGER,
                  order_quantity
                  INTEGER,
                  selling_price
                  REAL
              )
              ''')

    # 6. Allgemeine Team-Entscheidungen (z.B. Vertriebsbudget für alle Produkte zusammen)
    c.execute('''
              CREATE TABLE IF NOT EXISTS Global_Decisions
              (
                  id
                  INTEGER
                  PRIMARY
                  KEY
                  AUTOINCREMENT,
                  team_name
                  TEXT,
                  round
                  INTEGER,
                  advisory_budget
                  REAL
              )
              ''')

    # --- DATEN EINFÜGEN ---

    # Produkte anlegen (Preis pro Tonne/Einheit)
    products = [
        (1, 'Rinder-Mastfutter', 250.0, 5.0),
        (2, 'Schweine-Mastfutter', 280.0, 5.0),
        (3, 'Weizen-Saatgut', 450.0, 10.0),
        (4, 'NPK-Volldünger', 350.0, 8.0),
        (5, 'Pflanzenschutzmittel', 1200.0, 20.0)
    ]
    c.executemany("INSERT OR IGNORE INTO Products VALUES (?, ?, ?, ?)", products)

    # Spiel und Teams anlegen (Startkapital jetzt 100.000)
    c.execute("INSERT OR IGNORE INTO Game_State VALUES ('Klasse10B', 1, 'Start des neuen Quartals.')")
    c.execute("INSERT OR IGNORE INTO Teams VALUES ('Raiffeisen Nord', 'Klasse10B', 100000.0)")
    c.execute("INSERT OR IGNORE INTO Teams VALUES ('Agravis Süd', 'Klasse10B', 100000.0)")

    # Start-Lager auf 0 setzen für alle Produkte und Teams
    for team in ['Raiffeisen Nord', 'Agravis Süd']:
        for prod_id in range(1, 6):
            c.execute("INSERT OR IGNORE INTO Inventory VALUES (?, ?, 0)", (team, prod_id))

    conn.commit()
    conn.close()
    print("Multi-Produkt-Datenbank 'landhandel.db' erfolgreich erstellt!")


if __name__ == '__main__':
    create_database()