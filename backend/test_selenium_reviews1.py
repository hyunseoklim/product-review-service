import undetected_chromedriver as uc
import time


def test_browser():

    print("브라우저 실행 테스트")

    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = uc.Chrome(options=options, version_main=146)

    driver.get("https://www.google.com")
    time.sleep(5)
    print("페이지 제목:", driver.title)
    driver.quit()


if __name__ == "__main__":
    test_browser()
