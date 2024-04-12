import sqlite3
import random
import string

def flight_add(flight_date, flight_destination, flight_time, deluxe_price, first_class_price,economy_class_price):
    
    con = sqlite3.connect("cloudway_airlines.db")
    cur = con.cursor()

    source = string.digits + string.ascii_lowercase + string.ascii_uppercase
    id = (''.join(random.choice(source) for ctr in range(12)))

    date = flight_date
    time = flight_time
    destination = flight_destination

    cur.execute("INSERT INTO flight_list (id, date, time, destination, seats, status) VALUES (?, ?, ?, ?, ?, ?)", (id, date, time, destination, 0, "ongoing"))
    con.commit()

    deluxe = ["A1", "A2","A3", "B1", "B2","B3", "C1", "C2","C3", "D1", "D2","D3"]
    first = ["A4","A5","A6","A7","A8", "B4","B5","B6","B7","B8", "C4","C5","C6","C7","C8", 
            "D4","D5","D6","D7","D8", "E4","E5","E6","E7","E8", "F4","F5","F6","F7","F8",]
    economy = ["A9","A10","A11","A12","A13","A14","A15","A16","A17","A18",
                "B9","B10","B11","B12","B13","B14","B15","B16","B17","B18",
                "C9","C10","C11","C12","C13","C14","C15","C16","C17","C18",
                "D9","D10","D11","D12","D13","D14","D15","D16","D17","D18",
                "E9","E10","E11","E12","E13","E14","E15","E16","E17","E18",
                "F9","F10","F11","F12","F13","F14","F15","F16","F17","F18",
                "G9","G10","G11","G12","G13","G14","G15","G16","G17","G18",
                "H9","H10","H11","H12","H13","H14","H15","H16","H17","H18"]

    price = deluxe_price

    for d in deluxe:
        cur.execute("INSERT INTO flight_seat (id, seat, type, price, status) VALUES (?, ?, ?, ?, ?)", (id, d, "Deluxe Seat", price, "free"))
        con.commit()

    price = first_class_price

    for f in first:
        cur.execute("INSERT INTO flight_seat (id, seat, type, price, status) VALUES (?, ?, ?, ?, ?)", (id, f, "First Class", price, "free"))
        con.commit()

    price = economy_class_price

    for e in economy:
        cur.execute("INSERT INTO flight_seat (id, seat, type, price, status) VALUES (?, ?, ?, ?, ?)", (id, e, "Economy Class", price, "free"))
        con.commit()