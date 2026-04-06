from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.crawling.models import CrawlJobLog
from apps.crawling.services.crawl_service import crawl_product_review_target, crawl_search_target
from apps.crawling.services.target_selector import get_due_targets


class Command(BaseCommand):
    help = "스케줄링용 리뷰 크롤링 명령어. due product target만 limit 개수만큼 실행합니다."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=3,
            help="한 번 실행할 최대 target 개수"
        )
        parser.add_argument(
            "--review-limit",
            type=int,
            default=5,
            help="상품당 최대 리뷰 수집 개수"
        )
        parser.add_argument(
            "--target-type",
            type=str,
            default="product",
            help="기본값은 product"
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        review_limit = options["review_limit"]
        target_type = options["target_type"]

        targets = get_due_targets(limit=limit, target_type=target_type)
        total_targets = targets.count()

        success_count = 0
        fail_count = 0

        total_created = 0
        total_updated = 0

        site_summary = {}

        log = CrawlJobLog.objects.create(
            site="all",
            command_name="scheduled_crawl",
            status="success",
            total_targets=total_targets,
            success_count=0,
            fail_count=0,
            message=(
                f"scheduled_crawl 시작 "
                f"(limit={limit}, review_limit={review_limit}, target_type={target_type})"
            ),
        )

        self.stdout.write(self.style.SUCCESS("scheduled_crawl 시작"))

        if total_targets == 0:
            log.status = "success"
            log.message = "실행할 due target이 없습니다."
            log.finished_at = timezone.now()
            log.save()

            self.stdout.write("실행할 대상이 없습니다.")
            return

        for target in targets:
            self.stdout.write(f"\n[{target.site}] {target.url}")

            try:
                if target_type == "search":
                    result = crawl_search_target(target)
                else:
                    result = crawl_product_review_target(target, review_limit=review_limit)
                success_count += 1

                total_created += result["created_count"]
                total_updated += result["updated_count"]

                site_summary[target.site] = {
                    "targets": site_summary.get(target.site, {}).get("targets", 0) + 1,
                    "created": site_summary.get(target.site, {}).get("created", 0) + result["created_count"],
                    "updated": site_summary.get(target.site, {}).get("updated", 0) + result["updated_count"],
                    "reviews": site_summary.get(target.site, {}).get("reviews", 0) + result["review_count"],
                }

                self.stdout.write(
                    self.style.SUCCESS(
                        f"성공 - review_count={result['review_count']} / "
                        f"created={result['created_count']} / "
                        f"updated={result['updated_count']}"
                    )
                )

            except Exception as e:
                fail_count += 1
                self.stdout.write(self.style.ERROR(f"실패 - {str(e)}"))

        final_status = "success" if fail_count == 0 else "failed"

        log.status = final_status
        log.success_count = success_count
        log.fail_count = fail_count
        log.message = (
            f"사이트별 처리 수: {site_summary} | "
            f"전체 created={total_created}, updated={total_updated}"
        )
        log.finished_at = timezone.now()
        log.save()

        self.stdout.write("\nscheduled_crawl 종료")
        self.stdout.write(
            self.style.SUCCESS(
                f"총 {total_targets}개 / 성공 {success_count} / 실패 {fail_count} / "
                f"created {total_created} / updated {total_updated}"
            )
        )