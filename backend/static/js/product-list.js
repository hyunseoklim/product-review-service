document.addEventListener("DOMContentLoaded", function () {
    const productList = document.getElementById("productList");
    const prevBtn = document.getElementById("prevBtn");
    const nextBtn = document.getElementById("nextBtn");
    const pageInfo = document.getElementById("pageInfo");

    let currentPage = 1;
    let nextPageExists = false;

    function getAccessToken() {
        return localStorage.getItem("access");
    }

    function getAuthHeaders() {
        const token = getAccessToken();

        if (!token) {
            return {};
        }

        return {
            Authorization: `Bearer ${token}`
        };
    }

    // =========================
    // [기존]
    // 상품별 리뷰 조회
    // =========================
    async function fetchReviewsByProduct(productId) {
        try {
            const response = await axios.get(`/reviews/?product=${productId}`, {
                headers: getAuthHeaders()
            });

            const data = response.data;

            if (Array.isArray(data)) {
                return data;
            }

            if (Array.isArray(data.results)) {
                return data.results;
            }

            return [];
        } catch (error) {
            console.error(`상품 ${productId} 리뷰 불러오기 실패:`, error.response?.data || error);
            return [];
        }
    }

    // =========================================================
    // [인터랙티브 추가]
    // 리뷰별 댓글 목록 조회
    // GET /interactions/comments/<review_id>/
    // =========================================================
    async function fetchCommentsByReview(reviewId) {
        try {
            const response = await axios.get(`/interactions/comments/${reviewId}/`, {
                headers: getAuthHeaders()
            });

            const data = response.data;

            if (Array.isArray(data)) {
                return data;
            }

            if (Array.isArray(data.results)) {
                return data.results;
            }

            return [];
        } catch (error) {
            console.error(`리뷰 ${reviewId} 댓글 불러오기 실패:`, error.response?.data || error);
            return [];
        }
    }

    // =========================================================
    // [인터랙티브 추가]
    // 좋아요 토글
    // POST /interactions/like/<review_id>/
    // =========================================================
    async function toggleLike(reviewId) {
        return await axios.post(
            `/interactions/like/${reviewId}/`,
            {},
            {
                headers: getAuthHeaders()
            }
        );
    }

    // =========================================================
    // [인터랙티브 추가]
    // 북마크 토글
    // POST /interactions/bookmark/<review_id>/
    // =========================================================
    async function toggleBookmark(reviewId) {
        return await axios.post(
            `/interactions/bookmark/${reviewId}/`,
            {},
            {
                headers: getAuthHeaders()
            }
        );
    }

    // =========================================================
    // [인터랙티브 추가]
    // 댓글 작성
    // POST /interactions/comment/<review_id>/
    // =========================================================
    async function createComment(reviewId, content) {
        return await axios.post(
            `/interactions/comment/${reviewId}/`,
            { content: content },
            {
                headers: {
                    "Content-Type": "application/json",
                    ...getAuthHeaders()
                }
            }
        );
    }

    // =========================================================
    // [인터랙티브 추가]
    // 신고 작성
    // POST /interactions/report/<review_id>/
    // =========================================================
    async function createReport(reviewId, reason) {
        return await axios.post(
            `/interactions/report/${reviewId}/`,
            { reason: reason },
            {
                headers: {
                    "Content-Type": "application/json",
                    ...getAuthHeaders()
                }
            }
        );
    }

    // =========================================================
    // [인터랙티브 추가]
    // 댓글 1개를 화면에 표시할 HTML 생성
    // =========================================================
    function createCommentHTML(comment) {
        return `
            <div class="comment-item" style="padding:6px 0; border-top:1px solid #eee;">
                <strong>${comment.username || "익명"}</strong>
                <span class="muted" style="margin-left:6px;">
                    ${comment.created_at ? new Date(comment.created_at).toLocaleString() : ""}
                </span>
                <div style="margin-top:4px;">${comment.content || ""}</div>
            </div>
        `;
    }

    // =========================================================
    // [인터랙티브 추가]
    // 리뷰 HTML 안에
    // - 좋아요 버튼
    // - 북마크 버튼
    // - 신고 버튼
    // - 댓글 입력창
    // - 댓글 목록
    // 을 함께 렌더링하도록 확장된 부분
    // =========================================================
    function createReviewHTML(review, productId, commentsHTML = "") {
        return `
            <div class="review-item" data-review-id="${review.id}" data-product-id="${productId}">
                <div class="review-top">
                    <strong>${review.username || review.user_name || "익명"}</strong>
                    <span class="muted">평점: ${review.rating ?? "-"}</span>
                </div>

                <p class="review-content">${review.content || ""}</p>

                <!-- [인터랙티브 추가] 좋아요 / 북마크 / 신고 버튼 -->
                <div class="review-actions">
                    <button type="button" class="like-btn action-btn">
                        <span class="action-label">
                            ${review.is_liked ? "💖 취소" : "🤍 좋아요"}
                        </span>
                        <span class="action-count">${review.likes_count ?? 0}</span>
                    </button>

                    <button type="button" class="bookmark-btn action-btn">
                        <span class="action-label">
                            ${review.is_bookmarked ? "🔖 취소" : "📑 북마크"}
                        </span>
                        <span class="action-count">${review.bookmarks_count ?? 0}</span>
                    </button>

                    <button type="button" class="report-btn action-btn report-action-btn">
                        <span class="action-label">🚨 신고하기</span>
                    </button>
                </div>

                <!-- [인터랙티브 추가] 댓글 작성 폼 -->
                <div class="comment-form" style="margin-top:10px; display:flex; gap:6px;">
                    <input
                        type="text"
                        class="comment-input"
                        placeholder="댓글을 입력하세요"
                        style="flex:1;"
                    >
                    <button type="button" class="comment-btn">댓글 등록</button>
                </div>

                <!-- [인터랙티브 추가] 댓글 목록 렌더링 영역 -->
                <div class="comment-list" style="margin-top:10px;">
                    ${commentsHTML || `<p class="muted">등록된 댓글이 없습니다.</p>`}
                </div>
            </div>
        `;
    }

    // =========================================================
    // [인터랙티브 추가]
    // 상품에 달린 리뷰를 불러오고,
    // 각 리뷰의 댓글까지 함께 불러와서
    // 최종 리뷰 HTML을 조합하는 함수
    // =========================================================
    async function buildReviewsHTML(productId) {
        const reviews = await fetchReviewsByProduct(productId);

        if (reviews.length === 0) {
            return `<p class="muted">등록된 리뷰가 없습니다.</p>`;
        }

        const reviewHtmlList = await Promise.all(
            reviews.map(async (review) => {
                const comments = await fetchCommentsByReview(review.id);
                const commentsHTML = comments.length > 0
                    ? comments.map(createCommentHTML).join("")
                    : `<p class="muted">등록된 댓글이 없습니다.</p>`;

                return createReviewHTML(review, productId, commentsHTML);
            })
        );

        return reviewHtmlList.join("");
    }

    // =========================================================
    // [인터랙티브 추가]
    // 특정 상품 카드 안의 리뷰 영역을
    // 리뷰 + 댓글 포함해서 다시 렌더링하는 함수
    // 좋아요, 북마크, 댓글 작성 후 즉시 새로고침할 때 사용
    // =========================================================
    async function refreshReviewBox(card, productId) {
        const reviewBox = card.querySelector(".review-box");
        if (!reviewBox) {
            return;
        }

        const reviewsHTML = await buildReviewsHTML(productId);

        reviewBox.innerHTML = `
            <h4>리뷰</h4>
            ${reviewsHTML}
        `;
    }

    // =========================================================
    // [인터랙티브 추가]
    // 상품 카드 렌더링 시
    // 상품 정보만이 아니라 리뷰 + 댓글 영역까지 같이 그림
    // =========================================================
    async function renderProductCard(product) {
        const card = document.createElement("div");
        card.className = "product-card";
        card.dataset.productId = product.id;

        const reviewsHTML = await buildReviewsHTML(product.id);

        card.innerHTML = `
            <a href="/products/${product.id}/" class="product-link">
                <img src="${product.image_url || ""}" alt="${product.name}" class="thumb">
                <h3>${product.name}</h3>
                <p class="muted">${product.description || ""}</p>
                <p><strong>${Number(product.price).toLocaleString()}원</strong></p>
            </a>

            <div class="review-box">
                <h4>리뷰</h4>
                ${reviewsHTML}
            </div>
        `;

        return card;
    }

    // =========================================================
    // [인터랙티브 추가]
    // 이벤트 위임으로
    // - 좋아요 클릭
    // - 북마크 클릭
    // - 댓글 등록 클릭
    // - 신고 클릭
    // 을 처리하는 핵심 이벤트 로직
    // =========================================================
    productList.addEventListener("click", async function (event) {
        const likeBtn = event.target.closest(".like-btn");
        const bookmarkBtn = event.target.closest(".bookmark-btn");
        const commentBtn = event.target.closest(".comment-btn");
        const reportBtn = event.target.closest(".report-btn");

        if (likeBtn || bookmarkBtn || commentBtn || reportBtn) {
            event.preventDefault();
            event.stopPropagation();
        }

        // =====================================================
        // [인터랙티브 추가]
        // 좋아요 처리 후 리뷰 영역 다시 렌더링
        // =====================================================
        if (likeBtn) {
            const reviewItem = likeBtn.closest(".review-item");
            const reviewId = reviewItem.dataset.reviewId;
            const productId = reviewItem.dataset.productId;
            const card = likeBtn.closest(".product-card");

            try {
                await toggleLike(reviewId);
                await refreshReviewBox(card, productId);
            } catch (error) {
                console.error("좋아요 에러:", error.response?.data || error);

                if (error.response?.status === 401) {
                    alert("로그인이 필요합니다.");
                    return;
                }

                alert("좋아요 처리에 실패했습니다.");
            }

            return;
        }

        // =====================================================
        // [인터랙티브 추가]
        // 북마크 처리 후 리뷰 영역 다시 렌더링
        // =====================================================
        if (bookmarkBtn) {
            const reviewItem = bookmarkBtn.closest(".review-item");
            const reviewId = reviewItem.dataset.reviewId;
            const productId = reviewItem.dataset.productId;
            const card = bookmarkBtn.closest(".product-card");

            try {
                await toggleBookmark(reviewId);
                await refreshReviewBox(card, productId);
            } catch (error) {
                console.error("북마크 에러:", error.response?.data || error);

                if (error.response?.status === 401) {
                    alert("로그인이 필요합니다.");
                    return;
                }

                alert("북마크 처리에 실패했습니다.");
            }

            return;
        }

        // =====================================================
        // [인터랙티브 추가]
        // 댓글 등록 처리 후 리뷰 + 댓글 전체 다시 렌더링
        // =====================================================
        if (commentBtn) {
            const reviewItem = commentBtn.closest(".review-item");
            const reviewId = reviewItem.dataset.reviewId;
            const productId = reviewItem.dataset.productId;
            const card = commentBtn.closest(".product-card");
            const input = reviewItem.querySelector(".comment-input");

            const content = input.value.trim();

            if (!content) {
                alert("댓글 내용을 입력해주세요.");
                return;
            }

            try {
                await createComment(reviewId, content);

                input.value = "";
                alert("댓글이 등록되었습니다.");

                await refreshReviewBox(card, productId);
            } catch (error) {
                console.error("댓글 등록 에러:", error.response?.data || error);

                if (error.response?.status === 401) {
                    alert("로그인이 필요합니다.");
                    return;
                }

                alert("댓글 등록에 실패했습니다.");
            }

            return;
        }

        // =====================================================
        // [인터랙티브 추가]
        // 신고 처리
        // =====================================================
        if (reportBtn) {
            const reviewItem = reportBtn.closest(".review-item");
            const reviewId = reviewItem.dataset.reviewId;

            const reason = prompt("신고 사유를 입력해주세요.");

            if (!reason || !reason.trim()) {
                return;
            }

            try {
                await createReport(reviewId, reason.trim());
                alert("신고가 접수되었습니다.");
            } catch (error) {
                console.error("신고 에러:", error.response?.data || error);

                if (error.response?.status === 401) {
                    alert("로그인이 필요합니다.");
                    return;
                }

                alert("신고 처리에 실패했습니다.");
            }

            return;
        }
    });

    // =========================
    // [기존]
    // 상품 목록 로드 + 페이지네이션
    // =========================
    async function loadProducts(page = 1) {
        try {
            const response = await axios.get(`/products/api/?page=${page}`);
            const data = response.data;

            console.log("상품 응답:", data);

            productList.innerHTML = "";

            const products = Array.isArray(data) ? data : (data.results || []);

            if (products.length === 0) {
                productList.innerHTML = "<p>등록된 상품이 없습니다.</p>";
            } else {
                for (const product of products) {
                    const card = await renderProductCard(product);
                    productList.appendChild(card);
                }
            }

            currentPage = page;
            nextPageExists = !!data.next;

            pageInfo.textContent = `${currentPage} 페이지`;
            prevBtn.disabled = currentPage <= 1;
            nextBtn.disabled = !nextPageExists;

        } catch (error) {
            console.error("상품 목록 불러오기 에러:", error.response?.data || error);
            alert("상품 목록을 불러오지 못했습니다.");
        }
    }

    prevBtn.addEventListener("click", function () {
        if (currentPage > 1) {
            loadProducts(currentPage - 1);
        }
    });

    nextBtn.addEventListener("click", function () {
        if (nextPageExists) {
            loadProducts(currentPage + 1);
        }
    });

    loadProducts(1);
});