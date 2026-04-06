from django.test import TestCase

from apps.crawling.models import CrawlRawData, CrawlTarget
from apps.crawling.services.save_service import save_review_result


class SaveReviewResultTest(TestCase):
    def setUp(self):
        self.target = CrawlTarget.objects.create(
            site="hwahae",
            target_type="product",
            keyword="수분크림",
            title="화해 수분크림 상품",
            url="https://www.hwahae.co.kr/goods/70006",
        )

        self.reviews = [
            {
                "source": "hwahae",
                "url": self.target.url,
                "author_info": "user1 20대/복합성 2026.03.12",
                "review": "무난한 수분크림이고 보습감은 적당했습니다.",
            },
            {
                "source": "hwahae",
                "url": self.target.url,
                "author_info": "user2 30대/건성 2026.03.11",
                "review": "발림성은 좋았지만 아주 강한 보습은 아니었습니다.",
            },
        ]

    def test_first_save_creates_rows(self):
        summary = save_review_result(self.target, self.reviews)

        self.assertEqual(summary["created_count"], 2)
        self.assertEqual(summary["updated_count"], 0)
        self.assertEqual(CrawlRawData.objects.count(), 2)

    def test_second_save_updates_not_duplicates(self):
        save_review_result(self.target, self.reviews)
        summary = save_review_result(self.target, self.reviews)

        self.assertEqual(summary["created_count"], 0)
        self.assertEqual(summary["updated_count"], 2)
        self.assertEqual(CrawlRawData.objects.count(), 2)

    def test_review_text_changes_should_create_new_hash(self):
        save_review_result(self.target, self.reviews)

        modified_reviews = [
            {
                "source": "hwahae",
                "url": self.target.url,
                "author_info": "user1 20대/복합성 2026.03.12",
                "review": "무난한 수분크림인데 생각보다 흡수가 빨랐습니다.",
            }
        ]

        summary = save_review_result(self.target, modified_reviews)

        self.assertEqual(summary["created_count"], 1)
        self.assertEqual(CrawlRawData.objects.count(), 3)