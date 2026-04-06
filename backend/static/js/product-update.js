document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("productUpdateForm");

    const nameInput = document.getElementById("name");
    const descriptionInput = document.getElementById("description");
    const priceInput = document.getElementById("price");
    const imageInput = document.getElementById("image");
    const imagePreview = document.getElementById("imagePreview");

    // 현재 URL 예: /products/15/update/
    const pathParts = window.location.pathname.split("/").filter(Boolean);
    const productId = pathParts[1]; // ["products", "15", "update"]

    async function loadProduct() {
        try {
            const response = await axios.get(`/products/api/${productId}/`);
            const product = response.data;

            nameInput.value = product.name || "";
            descriptionInput.value = product.description || "";
            priceInput.value = product.price || "";

            if (product.image_url || product.image) {
                imagePreview.src = product.image_url || product.image;
                imagePreview.style.display = "block";
            } else {
                imagePreview.style.display = "none";
            }
        } catch (error) {
            console.error("상품 정보 조회 실패:", error.response?.data || error);
            alert("상품 정보를 불러오지 못했습니다.");
        }
    }

    if (imageInput) {
        imageInput.addEventListener("change", function () {
            const file = imageInput.files[0];

            if (!file) {
                imagePreview.style.display = "none";
                return;
            }

            const reader = new FileReader();
            reader.onload = function (event) {
                imagePreview.src = event.target.result;
                imagePreview.style.display = "block";
            };
            reader.readAsDataURL(file);
        });
    }

    if (form) {
        form.addEventListener("submit", async function (event) {
            event.preventDefault();

            const name = nameInput.value.trim();
            const description = descriptionInput.value.trim();
            const price = priceInput.value.trim();

            if (!name) {
                alert("상품 이름을 입력해주세요.");
                return;
            }

            if (!price) {
                alert("가격을 입력해주세요.");
                return;
            }

            try {
                const formData = new FormData();
                formData.append("name", name);
                formData.append("description", description);
                formData.append("price", price);

                if (imageInput.files.length > 0) {
                    formData.append("image", imageInput.files[0]);
                }

                const response = await axios.patch(
                    `/products/api/${productId}/`,
                    formData,
                    {
                        headers: {
                            "Content-Type": "multipart/form-data"
                        }
                    }
                );

                console.log("상품 수정 성공:", response.data);
                alert("상품이 수정되었습니다.");
                window.location.href = `/products/${productId}/`;
            } catch (error) {
                console.error("상품 수정 실패:", error.response?.data || error);
                alert("상품 수정에 실패했습니다.");
            }
        });
    }

    loadProduct();
});