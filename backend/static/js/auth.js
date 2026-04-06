document.addEventListener("DOMContentLoaded", function () {
    const signupForm = document.getElementById("signupForm");
    const loginForm = document.getElementById("loginForm");
    const myInfoBox = document.getElementById("myInfoBox");

    // ------------------------------
    // 회원가입
    // POST /accounts/api/signup/
    // ------------------------------
    if (signupForm) {
        signupForm.addEventListener("submit", async function (e) {
            e.preventDefault();

            const payload = {
                username: document.getElementById("username").value,
                email: document.getElementById("email").value,
                password: document.getElementById("password").value,
                password_confirm: document.getElementById("password_confirm").value,
            };

            try {
                await axios.post("/accounts/api/signup/", payload);

                alert("회원가입이 완료되었습니다.");
                window.location.href = "/accounts/login/";
            } catch (error) {
                console.error("회원가입 실패:", error.response?.data || error);
                alert("회원가입에 실패했습니다: " + JSON.stringify(error.response?.data || {}));
            }
        });
    }

    // ------------------------------
    // 로그인
    // POST /accounts/api/login/
    // ------------------------------
    if (loginForm) {
        loginForm.addEventListener("submit", async function (e) {
            e.preventDefault();

            const payload = {
                username: document.getElementById("username").value,
                password: document.getElementById("password").value,
            };

            try {
                const response = await axios.post("/accounts/api/login/", payload);

                const access = response.data.access;
                const refresh = response.data.refresh;

                // 토큰 저장
                localStorage.setItem("access", access);
                localStorage.setItem("refresh", refresh);

                // authUtils가 있으면 같이 사용
                if (window.authUtils && typeof window.authUtils.setTokens === "function") {
                    window.authUtils.setTokens(access, refresh);
                }

                alert("로그인 성공");
                window.location.href = "/products/";
            } catch (error) {
                console.error("로그인 실패:", error.response?.data || error);
                alert("로그인에 실패했습니다: " + JSON.stringify(error.response?.data || {}));
            }
        });
    }

    // ------------------------------
    // 내 정보 조회
    // GET /accounts/api/me/
    // ------------------------------
    if (myInfoBox) {
        loadMyInfo();
    }

    async function loadMyInfo() {
        try {
            const token = localStorage.getItem("access");

            const response = await axios.get("/accounts/api/me/", {
                headers: token
                    ? { Authorization: `Bearer ${token}` }
                    : {}
            });

            const user = response.data;

            myInfoBox.innerHTML = `
                <p><strong>ID:</strong> ${user.id}</p>
                <p><strong>아이디:</strong> ${user.username}</p>
                <p><strong>이메일:</strong> ${user.email}</p>
                <p><strong>가입일:</strong> ${user.created_at || "-"}</p>
            `;
        } catch (error) {
            console.error("내 정보 조회 실패:", error.response?.data || error);
            myInfoBox.innerHTML = `<p>내 정보를 불러오지 못했습니다.</p>`;
        }
    }
});