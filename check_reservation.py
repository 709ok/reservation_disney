from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def wait_until_queue_is_over(driver, timeout=600):
    print("[待機] 順番待ち画面か確認します")
    start = time.time()

    while True:
        # 順番待ちのURLが含まれているか、または「ただいまサイトが混雑しております」の文言を含むか
        if "reserve-q.tokyodisneyresort.jp" in driver.current_url or "順番にご案内します" in driver.page_source:
            print("[待機中] 順番待ち画面です... リロードして待機します")
            time.sleep(10)
            driver.refresh()
            if time.time() - start > timeout:
                raise Exception("順番待ちが長すぎます。タイムアウトしました。")
        else:
            print("[成功] 順番待ちを抜けました！処理を再開します")
            break

def check_reservation(
    url: str = "",
    hotel_code: str = "DHM",
    room_code: str = "HODHMTGD0004N", 
    num_adults: int = 2,
    num_rooms: int = 1,
    num_days: int = 1,
    target_month: str = "2025,7"
):
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)

    try:
        if not url:
            url = f"https://reserve.tokyodisneyresort.jp/sp/hotel/list/?hotelRoomCd={room_code}&searchHotelCD={hotel_code}&displayType=hotel-search"
        print("[開始] URLへアクセス:", url)
        driver.get(url)
        wait_until_queue_is_over(driver)
        time.sleep(5)  # ページ全体の読み込みを待機

        # 大人設定
        Select(driver.find_element(By.ID, "adultNum")).select_by_value(str(num_adults))
        print(f"[成功] 大人を{num_adults}人に設定しました")

        # 部屋数設定
        Select(driver.find_element(By.ID, "roomsNum")).select_by_value(str(num_rooms))
        print(f"[成功] 部屋数を{num_rooms}に設定しました")

        # 泊数設定
        Select(driver.find_element(By.ID, "stayDays")).select_by_value(str(num_days))
        print(f"[成功] 泊数を{num_days}に設定しました")

        # 「次へ」クリック
        driver.find_element(By.CSS_SELECTOR, 'button.next.js-conditionHide').click()
        print("[成功] 次へボタンをクリックしました")

        # カレンダー月選択まで待機
        calendar_select = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "boxCalendarSelect"))
        )
        time.sleep(5)

        # ここは ID 自体が <select> の場合にだけ Select() を使用可能
        Select(calendar_select).select_by_value(target_month)
        print(f"[成功] カレンダー月を {target_month} に変更しました")
        time.sleep(5)

        # ○× 状態の取得
        cells = driver.find_elements(By.CSS_SELECTOR, "td")
        time.sleep(5)
        print("\n[出力] ○×一覧:")
        for cell in cells:
            try:
                date_elem = cell.find_element(By.CLASS_NAME, "calendarDate")
                date = date_elem.text.strip()

                img_elem = cell.find_element(By.CLASS_NAME, "calendarImage").find_element(By.TAG_NAME, "img")
                src = img_elem.get_attribute("src")

                status = "×" if "batsu" in src else "○"
                print(f" - {date}日: {status}")
            except Exception:
                continue

    except Exception as e:
        print("[エラー] 処理中に例外が発生:", e)
    finally:
        print("\n[完了] テスト終了（確認後にEnterで閉じてください）")
        input(">> 確認できたら Enter を押してください")
        driver.quit()

if __name__ == "__main__":
    hotel_code = "DHM" # ミラコスタ
    room_code = "TGD0004N"
    check_reservation(hotel_code = hotel_code, room_code = room_code)