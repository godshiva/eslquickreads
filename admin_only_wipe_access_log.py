import mysql.connector


if __name__ == "__main__":

    my_pass = None
    with open('/home/algorithmguy/mysite/configdata/dbpassprod.txt', 'r') as f:
        my_pass = f.read().strip()

    assert my_pass is not None and len(my_pass) > 0, "Failed to load password!"

    conn = mysql.connector.connect(
        host='algorithmguy.mysql.pythonanywhere-services.com',
        user='algorithmguy',
        password=my_pass,
        database='algorithmguy$default'
    )
    cursor = conn.cursor()

    cursor.execute('''
        DELETE FROM access_granted;
    ''')

    conn.commit()
    conn.close()

    print("Done with task!")

