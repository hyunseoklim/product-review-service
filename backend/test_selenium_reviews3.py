import time
import traceback
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


def build_driver():
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.add_argument("--window-size=1400,1200")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/145.0.0.0 Safari/537.36"
    )

    driver = uc.Chrome(
        options=options,
        version_main=145,
        headless=False,
        use_subprocess=True,
    )
    return driver


def main():
    driver = None
    try:
        driver = build_driver()

        print("1. 화해 메인 접속")
        driver.get("https://www.hwahae.co.kr/")
        time.sleep(3)

        print("2. 상품 페이지 접속")
        driver.get("https://www.hwahae.co.kr/goods/70006")
        time.sleep(5)

        print("3. 페이지 아래로 스크롤")
        for _ in range(5):
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(1.5)

        print("4. 리뷰 관련 버튼/탭 찾기")
        buttons = driver.find_elements(By.XPATH, "//*[contains(text(),'리뷰')]")
        print("리뷰 텍스트 포함 요소 수:", len(buttons))

        for i, b in enumerate(buttons[:10], start=1):
            try:
                print(f"{i}. tag={b.tag_name} text={b.text[:50]!r}")
            except Exception:
                pass

        print("5. 첫 번째 리뷰 요소 클릭 시도")
        clicked = False
        for b in buttons:
            try:
                if "리뷰" in b.text:
                    driver.execute_script("arguments[0].click();", b)
                    clicked = True
                    print("리뷰 탭 클릭 성공")
                    break
            except Exception:
                continue

        if not clicked:
            print("리뷰 탭 클릭 실패")

        time.sleep(5)

        print("6. HTML 저장")
        html = driver.page_source
        with open("hwahae_after_review_click.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("저장 완료: hwahae_after_review_click.html")

        print("7. BeautifulSoup으로 긴 문장 후보 추출")
        soup = BeautifulSoup(html, "lxml")

        texts = []
        for tag in soup.find_all(["p", "span", "div"]):
            text = tag.get_text(" ", strip=True)
            if 20 <= len(text) <= 200:
                texts.append(text)

        # 중복 제거
        unique_texts = []
        seen = set()
        for t in texts:
            if t not in seen:
                seen.add(t)
                unique_texts.append(t)

        print("\n후보 텍스트 상위 30개:")
        for i, t in enumerate(unique_texts[:30], start=1):
            print(f"{i}. {t}")

        driver.save_screenshot("hwahae_review_debug.png")
        print("\n스크린샷 저장 완료: hwahae_review_debug.png")

    except Exception as e:
        print("\n[에러 발생]")
        print(type(e).__name__, str(e))
        traceback.print_exc()
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


if __name__ == "__main__":
    main()