/**
 * app.js — NutriGuide Agentic AI Frontend
 * IBM Granite LLM · HAM Principles · Ethical AI
 */

/* =========================================================
   State
   ========================================================= */
const state = {
    currentPlan: null,
    savedFilename: null,
    userProfile: null,
    planSource: null,
};

/* =========================================================
   DOM References
   ========================================================= */
const $ = id => document.getElementById(id);

const userForm        = $("userForm");
const generateBtn     = $("generateBtn");
const planLoading     = $("planLoading");
const planWelcome     = $("planWelcome");
const planResult      = $("planResult");
const planContent     = $("planContent");
const planMeta        = $("planMeta");
const downloadBtn     = $("downloadBtn");
const copyBtn         = $("copyBtn");
const newPlanBtn      = $("newPlanBtn");
const formError       = $("formError");
const llmStatus       = $("llmStatus");
const queryInput      = $("queryInput");
const askBtn          = $("askBtn");
const qaLoading       = $("qaLoading");
const qaHistory       = $("qaHistory");
const qaError         = $("qaError");
const charCount       = $("charCount");

/* =========================================================
   Tabs
   ========================================================= */
document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        const target = btn.dataset.tab;
        document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
        document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
        btn.classList.add("active");
        $(target).classList.add("active");
    });
});

/* =========================================================
   Check LLM Status on Load
   ========================================================= */
async function checkHealth() {
    try {
        const res  = await fetch("/api/health");
        const data = await res.json();
        if (data.llm_connected) {
            llmStatus.innerHTML = `<span style="color:var(--green)">✅ IBM Granite connected (Watsonx.ai)</span>`;
        } else {
            llmStatus.innerHTML = `<span style="color:var(--orange)">⚠️ Demo mode — <a href="#" onclick="showApiHelp();return false">configure IBM Watsonx API key</a></span>`;
        }
    } catch {
        llmStatus.innerHTML = `<span style="color:var(--text-muted)">🔌 Server not reachable</span>`;
    }
}

function showApiHelp() {
    showToast("Copy .env.example to .env and fill in your WATSONX_API_KEY", 4000, "#f1620a");
}

/* =========================================================
   Form Validation
   ========================================================= */
function validateForm() {
    let valid = true;

    const fields = [
        { id: "name",             label: "Full Name",    test: v => v.length >= 2 && /^[A-Za-z\s\-']+$/.test(v) },
        { id: "age",              label: "Age",          test: v => { const n = parseInt(v); return !isNaN(n) && n >= 5 && n <= 110; } },
        { id: "diet_preference",  label: "Diet",         test: v => v !== "" },
        { id: "location_city",    label: "City",         test: v => v.length >= 2 },
        { id: "location_country", label: "Country",      test: v => v.length >= 2 },
    ];

    const errors = [];

    fields.forEach(f => {
        const el  = $(f.id);
        const val = el.value.trim();
        if (!f.test(val)) {
            el.classList.add("invalid");
            errors.push(f.label);
            valid = false;
        } else {
            el.classList.remove("invalid");
        }
    });

    if (!valid) {
        formError.textContent = `Please fix: ${errors.join(", ")}`;
        formError.classList.remove("hidden");
    } else {
        formError.classList.add("hidden");
    }

    return valid;
}

// Live validation clear
["name","age","diet_preference","location_city","location_country"].forEach(id => {
    const el = $(id);
    if (el) {
        el.addEventListener("input", () => {
            el.classList.remove("invalid");
            if (document.querySelectorAll(".invalid").length === 0) {
                formError.classList.add("hidden");
            }
        });
    }
});

/* =========================================================
   Generate Plan
   ========================================================= */
userForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    const profile = {
        name:             $("name").value.trim(),
        age:              parseInt($("age").value),
        diet_preference:  $("diet_preference").value,
        medical_history:  $("medical_history").value.trim() || "None",
        location_city:    $("location_city").value.trim(),
        location_country: $("location_country").value.trim(),
    };

    state.userProfile = profile;

    // Show loading
    planWelcome.classList.add("hidden");
    planResult.classList.add("hidden");
    planLoading.classList.remove("hidden");
    generateBtn.disabled = true;
    generateBtn.innerHTML = `<span class="btn-icon">⏳</span> Generating…`;

    // Switch to Plan tab
    document.querySelector('[data-tab="planTab"]').click();

    try {
        const res  = await fetch("/api/generate-plan", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(profile),
        });
        const data = await res.json();

        if (!res.ok) {
            throw new Error(data.error || "Failed to generate plan");
        }

        state.currentPlan   = data.plan;
        state.savedFilename = data.saved_file;
        state.planSource    = data.source;

        renderPlan(data, profile);

    } catch (err) {
        planLoading.classList.add("hidden");
        planWelcome.classList.remove("hidden");
        formError.textContent = "⚠️ " + (err.message || "Could not generate plan. Please try again.");
        formError.classList.remove("hidden");
    } finally {
        generateBtn.disabled = false;
        generateBtn.innerHTML = `<span class="btn-icon">✨</span> Generate My Nutrition Plan`;
    }
});

function renderPlan(data, profile) {
    planLoading.classList.add("hidden");

    // Meta bar
    const now = new Date().toLocaleString();
    const conditionWarning = data.flagged_conditions && data.flagged_conditions.length
        ? ` · ⚠️ High-risk conditions flagged: ${data.flagged_conditions.join(", ")}`
        : "";
    planMeta.innerHTML =
        `<span>👤 ${profile.name} · ${profile.age}yrs · ${profile.diet_preference}</span>` +
        `<span>📍 ${profile.location_city}, ${profile.location_country}</span>` +
        `<span>🤖 ${data.source}</span>` +
        `<span>🕐 ${now}${conditionWarning}</span>`;

    // Render Markdown
    planContent.innerHTML = marked.parse(data.plan || "No plan generated.");

    planResult.classList.remove("hidden");
    planContent.scrollTop = 0;
}

/* =========================================================
   Download Plan (.md)
   ========================================================= */
downloadBtn.addEventListener("click", () => {
    if (!state.savedFilename) {
        showToast("No plan saved yet — generate a plan first.", 3000, "#f1620a");
        return;
    }
    const link = document.createElement("a");
    link.href  = `/api/download-plan/${encodeURIComponent(state.savedFilename)}`;
    link.download = state.savedFilename;
    link.click();
    showToast("📥 Downloading your plan…");
});

/* =========================================================
   Copy to Clipboard
   ========================================================= */
copyBtn.addEventListener("click", async () => {
    if (!state.currentPlan) return;
    try {
        await navigator.clipboard.writeText(state.currentPlan);
        showToast("✅ Plan copied to clipboard!");
    } catch {
        showToast("Could not copy — please select and copy manually.", 3000, "#f1620a");
    }
});

/* =========================================================
   New Plan
   ========================================================= */
newPlanBtn.addEventListener("click", () => {
    planResult.classList.add("hidden");
    planWelcome.classList.remove("hidden");
    state.currentPlan   = null;
    state.savedFilename = null;
    userForm.reset();
    document.querySelectorAll(".invalid").forEach(el => el.classList.remove("invalid"));
    formError.classList.add("hidden");
    window.scrollTo({ top: 0, behavior: "smooth" });
});

/* =========================================================
   Q&A Agent
   ========================================================= */
queryInput.addEventListener("input", () => {
    const len = queryInput.value.length;
    charCount.textContent = `${len} / 500`;
    charCount.style.color = len > 450 ? "var(--red)" : "var(--text-muted)";
});

// Suggestion chips
document.querySelectorAll(".suggestion-chip").forEach(chip => {
    chip.addEventListener("click", () => {
        queryInput.value = chip.dataset.q;
        charCount.textContent = `${queryInput.value.length} / 500`;
        queryInput.focus();
    });
});

askBtn.addEventListener("click", submitQuery);
queryInput.addEventListener("keydown", e => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) submitQuery();
});

async function submitQuery() {
    const query = queryInput.value.trim();
    if (!query || query.length < 3) {
        qaError.textContent = "Please enter a question (at least 3 characters).";
        qaError.classList.remove("hidden");
        return;
    }
    qaError.classList.add("hidden");

    // Use current profile or defaults
    const profile = state.userProfile || {
        name: "User", age: 30, diet_preference: "", medical_history: "",
        location_city: "", location_country: "",
    };

    // Show loading
    qaLoading.classList.remove("hidden");
    askBtn.disabled = true;
    askBtn.innerHTML = `<span class="btn-icon">⏳</span> Thinking…`;

    const questionText = query;
    queryInput.value = "";
    charCount.textContent = "0 / 500";

    try {
        const res  = await fetch("/api/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: questionText, ...profile }),
        });
        const data = await res.json();

        if (!res.ok) {
            throw new Error(data.error || "Failed to get answer");
        }

        addQAItem(questionText, data.answer);

    } catch (err) {
        addQAItem(questionText,
            `⚠️ **Error**: ${err.message || "Could not get an answer. Please try again."}`
        );
    } finally {
        qaLoading.classList.add("hidden");
        askBtn.disabled = false;
        askBtn.innerHTML = `<span class="btn-icon">🤖</span> Ask IBM Granite`;
    }
}

function addQAItem(question, answer) {
    const now  = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    const item = document.createElement("div");
    item.className = "qa-item";

    // Render answer as markdown
    const renderedAnswer = marked.parse(answer || "");

    item.innerHTML = `
        <div class="qa-question">
            <span>🙋</span>
            <span>${escapeHtml(question)}</span>
        </div>
        <div class="qa-answer">
            <div class="qa-answer-content">${renderedAnswer}</div>
            <div class="qa-timestamp">🤖 IBM Granite · ${now}</div>
        </div>
    `;
    qaHistory.prepend(item);
}

function escapeHtml(str) {
    return str.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}

/* =========================================================
   Toast Notification
   ========================================================= */
function showToast(msg, duration = 2600, bg = "#24a148") {
    const existing = document.querySelector(".toast");
    if (existing) existing.remove();

    const t = document.createElement("div");
    t.className   = "toast";
    t.textContent = msg;
    t.style.background = bg;
    document.body.appendChild(t);
    setTimeout(() => t.remove(), duration + 400);
}

/* =========================================================
   Init
   ========================================================= */
checkHealth();
