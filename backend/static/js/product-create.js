document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("productCreateForm");

    if (!form) return;

    form.addEventListener("submit", async function (e) {
        e.preventDefault();

        const name = document.getElementById("name").value.trim();
        const description = document.getElementById("description").value.trim();
        const price = document.getElementById("price").value;
        const imageFile = document.getElementById("image").files[0];

        if (!name) {
            alert("상품 이름을 입력해주세요.");
            return;
        }

        if (!price) {
            alert("가격을 입력해주세요.");
            return;
        }

        const formData = new FormData();
        formData.append("name", name);
        formData.append("description", description);
        formData.append("price", price);

        if (imageFile) {
            formData.append("image", imageFile);
        }

        try {
            const response = await api.post("/products/api/", formData, {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            });

            alert("상품이 등록되었습니다.");
            window.location.href = "/products/";
        } catch (error) {
            console.error("상품 등록 실패:", error);

            if (error.response && error.response.data) {
                console.log("서버 응답:", error.response.data);
                alert("상품 등록 실패: " + JSON.stringify(error.response.data));
            } else {
                alert("상품 등록에 실패했습니다.");
            }
        }
    });
});