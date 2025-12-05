const API_BASE_URL = "http://127.0.0.1:8002";

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

// ======= Регистрация (без изменений, т.к. бэкенд не имеет этого эндпоинта) =======
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

// ======= Вход (без изменений) =======
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

// ======= Ticket actions (ИНТЕГРАЦИЯ С БЭКЕНДОМ) =======
async function submitTicket() {
    const textarea = document.getElementById("ticketText");
    const button = document.getElementById("submitBtn");
    const text = textarea?.value.trim();
    const resultBox = document.getElementById("resultBox");
    const user = storage.getUser();

    if (!text) {
        showToast("Введите текст заявки", "error");
        return;
    }

    button.disabled = true;
    button.innerText = "Отправляем...";

    resultBox.innerHTML = `<div class="loader"></div><p>AI анализирует заявку...</p>`;
    resultBox.className = "result-box pending";

    try {
        const response = await fetch(`${API_BASE_URL}/submit_ticket`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: user?.email || "anonymous", // Отправляем email пользователя
                problem_description: text,
                priority: "Medium", // Можно добавить выбор на UI
                category: "Technical" // Можно добавить выбор на UI
            })
        });

        if (!response.ok) {
            throw new Error(`Ошибка сервера: ${response.statusText}`);
        }

        const result = await response.json();

        // Отображаем результат от бэкенда
        if (result.status === "Closed") {
            resultBox.innerHTML = `Запрос закрыт автоматически. Ответ: ${result.message}`;
            resultBox.dataset.status = "success";
        } else {
            resultBox.innerHTML = `Заявка #${result.ticket_id} создана. Статус: ${result.status}. Очередь: ${result.queue}`;
            resultBox.dataset.status = "warning";
        }

        resultBox.classList.remove("pending");
        resultBox.classList.add("show");
        loadMetrics(); // Обновляем метрики после создания тикета

    } catch (error) {
        console.error("Submit ticket error:", error);
        showToast("Не удалось отправить заявку. Бэкенд запущен?", "error");
        resultBox.innerHTML = "Ошибка при отправке";
        resultBox.dataset.status = "error";
    } finally {
        button.disabled = false;
        button.innerText = "Отправить";
    }
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

// ======= Метрики (ИНТЕГРАЦИЯ С БЭКЕНДОМ) =======
async function loadMetrics() {
    try {
        const response = await fetch(`${API_BASE_URL}/metrics`);
        if (!response.ok) {
            throw new Error("Server error");
        }
        const metrics = await response.json();

        // Заполняем дашборд реальными данными
        const total = metrics.total_tickets || 0;
        const closed = metrics.closed_tickets || 0;
        const sla = total > 0 ? Math.round(((total - (metrics.tickets_by_queue.HighPriority || 0)) / total) * 100) : 100;

        setMetric("auto", total > 0 ? Math.round(((metrics.tickets_by_queue.Automated || 0) / total) * 100) : 0);
        setMetric("accuracy", sla - 2); // Имитация, т.к. нет такой метрики
        setMetric("sla", sla);
        setMetric("backlog", total - closed);

        showToast("Метрики обновлены с бэкенда", "success");
    } catch (error) {
        console.error("Failed to load metrics:", error);
        showToast("Не удалось загрузить метрики. Бэкенд запущен?", "error");
    }
}

// Функции для отображения метрик (без изменений)
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
