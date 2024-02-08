
import mysql.connector

try:
    mydb = mysql.connector.connect(
        host="192.168.0.15",
        port= 3306,
        user="root",
        password="123"
      )

    cursor = mydb.cursor()
    query = ("SELECT id, uri, client_id, requestTimeStamp, conditiontinerQuantity, conditionQuantity FROM EA_Discovery.uri;")

    cursor.execute(query)

    myresult = cursor.fetchall()
    """print("Total number of rows in table: ", myresult.rowcount)"""

    for row in myresult:
        print(row)
        print("Id = ", row[0])
        print("uri = ", row[1])

except mysql.connector.Error as e:
    print("Error reading data from MySQL table", e)
finally:
    if mydb.is_connected():
        mydb.close()
        cursor.close()
        print("MySQL connection is closed")
