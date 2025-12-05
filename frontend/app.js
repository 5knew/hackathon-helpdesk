// ======= Helpers =======
const storage = {
    saveUser(email, password) {
        localStorage.setItem("user", JSON.stringify({ email, password }));
    },
    getUser() {
        const raw = localStorage.getItem("user");
        return raw ? JSON.parse(raw) : null;
    },
    setLogged(flag) {
        localStorage.setItem("logged", flag ? "1" : "0");
    },
    isLogged() {
        return localStorage.getItem("logged") === "1";
    }
};

document.addEventListener("DOMContentLoaded", initPage);

function initPage() {
    const path = window.location.pathname;

    if (path.includes("dashboard")) {
        protectDashboard();
        hydrateUserChip();
        loadMetrics();
    }
}

// ======= Регистрация =======
function register() {
    const email = document.getElementById("regEmail")?.value.trim();
    const password = document.getElementById("regPassword")?.value.trim();

    if (!email || !password) {
        showToast("Введите email и пароль", "error");
        return;
    }

    storage.saveUser(email, password);
    storage.setLogged(true);

    showToast("Регистрация успешна", "success");
    setTimeout(() => window.location.href = "dashboard.html", 600);
}

// ======= Вход =======
function login() {
    const email = document.getElementById("loginEmail")?.value.trim();
    const password = document.getElementById("loginPassword")?.value.trim();
    const user = storage.getUser();

    if (!user || user.email !== email || user.password !== password) {
        showToast("Неверный логин или пароль", "error");
        return;
    }

    storage.setLogged(true);
    showToast("Успешный вход!", "success");
    setTimeout(() => window.location.href = "dashboard.html", 500);
}

// ======= Выход =======
function logout() {
    storage.setLogged(false);
    window.location.href = "index.html";
}

// ======= Guard =======
function protectDashboard() {
    if (!storage.isLogged()) {
        window.location.href = "index.html";
    }
}

// ======= Ticket actions =======
function submitTicket() {
    const textarea = document.getElementById("ticketText");
    const button = document.getElementById("submitBtn");
    const text = textarea?.value.trim();
    const resultBox = document.getElementById("resultBox");

    if (!text) {
        showToast("Введите текст заявки", "error");
        return;
    }

    button.disabled = true;
    button.innerText = "Отправляем...";

    resultBox.innerHTML = `<div class="loader"></div><p>AI анализирует заявку...</p>`;
    resultBox.classList.add("pending");

    setTimeout(() => {
        const departments = ["IT", "HR", "Финансы", "Техподдержка"];
        const isAuto = text.toLowerCase().includes("пароль") || text.toLowerCase().includes("войти");
        const dept = departments[Math.floor(Math.random() * departments.length)];

        if (isAuto) {
            resultBox.innerHTML = "Запрос закрыт автоматически (AI)";
            resultBox.dataset.status = "success";
        } else {
            resultBox.innerHTML = `Передано в отдел: ${dept}`;
            resultBox.dataset.status = "warning";
        }

        resultBox.classList.remove("pending");
        resultBox.classList.add("show");

        button.disabled = false;
        button.innerText = "Отправить";
    }, 1300);
}

function clearTicket() {
    const textarea = document.getElementById("ticketText");
    const resultBox = document.getElementById("resultBox");
    if (textarea) textarea.value = "";
    if (resultBox) {
        resultBox.innerHTML = "Пока нет результата";
        resultBox.dataset.status = "";
        resultBox.classList.remove("show", "pending");
    }
}

function prefillTicket() {
    const examples = [
        "Не могу войти в корпоративную почту, пишет неверный пароль.",
        "Нужно перенести отпуск в системе HR.",
        "Ошибка 500 в CRM при открытии карточки клиента.",
        "Хочу подключить новый проект в Jira."
    ];
    const textarea = document.getElementById("ticketText");
    textarea.value = examples[Math.floor(Math.random() * examples.length)];
}

// ======= Метрики (имитация /metrics) =======
function loadMetrics() {
    const metrics = mockMetrics();
    setMetric("auto", metrics.auto);
    setMetric("accuracy", metrics.accuracy);
    setMetric("sla", metrics.sla);
    setMetric("backlog", metrics.backlog);
    showToast("Метрики обновлены", "success");
}

function mockMetrics() {
    return {
        auto: randomRange(68, 93),
        accuracy: randomRange(84, 97),
        sla: randomRange(95, 99),
        backlog: randomRange(8, 32)
    };
}

function setMetric(key, value) {
    if (key === "backlog") {
        setValue("backlogValue", `${value} заявок`);
        setWidth("backlogBar", Math.min(value * 3, 100));
        return;
    }
    setValue(`${key}Percent`, `${value}%`);
    setValue(`${key}PercentHero`, `${value}%`);
    setWidth(`${key}Bar`, value);
}

function setValue(id, text) {
    const el = document.getElementById(id);
    if (el) el.innerText = text;
}

function setWidth(id, value) {
    const el = document.getElementById(id);
    if (el) el.style.width = `${value}%`;
}

function randomRange(min, max) {
    return Math.round(Math.random() * (max - min) + min);
}

function hydrateUserChip() {
    const user = storage.getUser();
    const chip = document.getElementById("userEmailChip");
    if (chip && user?.email) chip.innerText = user.email;
}

// ======= Toast (уведомления) =======
function showToast(message, type = "info") {
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.innerText = message;

    document.body.appendChild(toast);

    setTimeout(() => toast.classList.add("show"), 10);
    setTimeout(() => {
        toast.classList.remove("show");
        setTimeout(() => toast.remove(), 260);
    }, 2400);
}
