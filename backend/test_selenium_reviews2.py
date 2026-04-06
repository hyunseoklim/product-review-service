import time
import traceback
import undetected_chromedriver as uc


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

    # 현재 브라우저가 145라서 맞춰줍니다.
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
        print("1. 브라우저 생성 시작")
        driver = build_driver()
        print("2. 브라우저 생성 성공")

        print("3. Google 접속")
        driver.get("https://www.google.com")
        time.sleep(3)
        print("   Google title:", driver.title)

        print("4. 화해 메인 접속")
        driver.get("https://www.hwahae.co.kr")
        time.sleep(5)
        print("   현재 URL:", driver.current_url)
        print("   title:", driver.title)

        print("5. 화해 상품 페이지 접속")
        driver.get("https://www.hwahae.co.kr/goods/70006")
        time.sleep(8)
        print("   현재 URL:", driver.current_url)
        print("   title:", driver.title)

        print("6. 페이지 소스 길이 확인")
        html = driver.page_source
        print("   html length:", len(html))

        print("7. 스크린샷 저장")
        driver.save_screenshot("hwahae_debug.png")
        print("   저장 완료: hwahae_debug.png")

        print("완료")

    except Exception as e:
        print("\n[에러 발생]")
        print(type(e).__name__, str(e))
        traceback.print_exc()

        if driver:
            try:
                driver.save_screenshot("hwahae_error.png")
                print("에러 스크린샷 저장: hwahae_error.png")
            except Exception:
                pass
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


if __name__ == "__main__":
    main()