const api = axios.create({
    timeout: 10000,
});

// ------------------------------
// 토큰 유틸 함수
// ------------------------------
function getAccessToken() {
    return localStorage.getItem("access_token");
}

function getRefreshToken() {
    return localStorage.getItem("refresh_token");
}

function setTokens(access, refresh = null) {
    if (access) {
        localStorage.setItem("access_token", access);
    }
    if (refresh) {
        localStorage.setItem("refresh_token", refresh);
    }
}

function clearTokens() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
}

// ------------------------------
// 요청 인터셉터
// access token 자동 첨부
// ------------------------------
api.interceptors.request.use(
    function (config) {
        const token = getAccessToken();

        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        return config;
    },
    function (error) {
        return Promise.reject(error);
    }
);

// ------------------------------
// refresh 중복 처리 방지
// ------------------------------
let isRefreshing = false;
let failedQueue = [];

function processQueue(error, token = null) {
    failedQueue.forEach((promise) => {
        if (error) {
            promise.reject(error);
        } else {
            promise.resolve(token);
        }
    });

    failedQueue = [];
}

// ------------------------------
// 응답 인터셉터
// 401이면 refresh 시도
// ------------------------------
api.interceptors.response.use(
    function (response) {
        return response;
    },
    async function (error) {
        const originalRequest = error.config;

        if (!error.response) {
            return Promise.reject(error);
        }

        if (error.response.status === 401 && !originalRequest._retry) {
            const refreshToken = getRefreshToken();

            if (!refreshToken) {
                clearTokens();
                window.location.href = "/accounts/login/";
                return Promise.reject(error);
            }

            if (isRefreshing) {
                return new Promise(function (resolve, reject) {
                    failedQueue.push({ resolve, reject });
                })
                    .then((token) => {
                        originalRequest.headers.Authorization = `Bearer ${token}`;
                        return api(originalRequest);
                    })
                    .catch((err) => Promise.reject(err));
            }

            originalRequest._retry = true;
            isRefreshing = true;

            try {
                const response = await axios.post("/accounts/api/token/refresh/", {
                    refresh: refreshToken,
                });

                const newAccess = response.data.access;
                setTokens(newAccess);

                originalRequest.headers.Authorization = `Bearer ${newAccess}`;
                processQueue(null, newAccess);

                return api(originalRequest);
            } catch (refreshError) {
                processQueue(refreshError, null);
                clearTokens();
                window.location.href = "/accounts/login/";
                return Promise.reject(refreshError);
            } finally {
                isRefreshing = false;
            }
        }

        return Promise.reject(error);
    }
);

// ------------------------------
// 로그아웃 공통 처리
// ------------------------------
document.addEventListener("DOMContentLoaded", function () {
    const logoutBtn = document.getElementById("logoutBtn");

    if (logoutBtn) {
        logoutBtn.addEventListener("click", function () {
            clearTokens();
            alert("로그아웃 되었습니다.");
            window.location.href = "/accounts/login/";
        });
    }
});

// 전역으로 사용 가능하게 등록
window.api = api;
window.authUtils = {
    getAccessToken,
    getRefreshToken,
    setTokens,
    clearTokens,
};