from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import psycopg2

conn = psycopg2.connect(
    host="dpg-chusutu7avj345euun5g-a.frankfurt-postgres.render.com",
    database="projectcasino",
    user="projectcasino_user",
    password="8dHXowS97plyDW97mKAzabGbGNrRpzlD",
)

cursor = conn.cursor()


def remove_uppercase_words(s):
    words = s.split()
    filtered_words = [word for word in words if not word.isupper()]
    if (len(filtered_words) == 0):
        return s
    return ' '.join(filtered_words)


def add(r):
    print("Inserted: ", r)
    cursor.execute(
        """delete from Pariuri where echipa1 = %s and echipa2 = %s and sport = 'fotbal' and site = 'superbet' returning *""", (r[0], r[1]))
    print(*cursor.fetchall(), sep="\n")
    conn.commit()
    cursor.execute(
        """INSERT INTO Pariuri (echipa1, echipa2, cota_e1, cota_egal, cota_e2, sport, site) VALUES (%s, %s, %s, %s, %s, 'fotbal', 'superbet')""", r)
    conn.commit()


def cote(html, driver):
    try:
        buttons = driver.find_elements(By.CLASS_NAME, "actionable")
        nums = []
        for button in buttons:
            num = button.get_attribute('innerHTML').strip()
            try:
                n = float(num)
                nums.append(n)
            except ValueError:
                pass

        echipe = driver.find_elements(By.CLASS_NAME, "pick__description")
        lung = len(nums)
        for x in range(0, int(lung/8)):
            (cota_e1, cota_egal, cota_e2) = (
                nums[x*8 + 1], nums[x*8 + 3], nums[x*8 + 6])
            (e1, e2) = (
                echipe[x *
                       3].get_attribute('innerHTML').strip("câştigă meciul"),
                echipe[x * 3 +
                       2].get_attribute('innerHTML').strip("câştigă meciul"),
            )
            (e1, e2) = (remove_uppercase_words(e1), remove_uppercase_words(e2))
            if e2 < e1:
                (e1, e2) = (e2, e1)

            add((e1, e2, cota_e1, cota_egal, cota_e2))
    except:
        pass
    html.send_keys(Keys.PAGE_DOWN)
    html.send_keys(Keys.PAGE_DOWN)


def main():
    cursor.execute(
        "delete from Pariuri where site = 'superbet'")
    conn.commit()

    op = webdriver.ChromeOptions()
    op.add_argument('headless')
    driver = webdriver.Chrome(options=op)
    driver.get("https://superbet.ro/pariuri-sportive/fotbal/toate")
    time.sleep(7)
    html = driver.find_element(By.TAG_NAME, 'html')

    for i in range(0, 1000):
        cote(html, driver)


if __name__ == "__main__":

    main()

    # cursor.execute("SELECT * FROM Pariuri")
    # print(*cursor.fetchall(), sep="\n")
