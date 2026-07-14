/**
 * app.js – AI SQL Query Generator (Frontend Logic)
 * ==================================================
 * Handles user interactions: generating SQL, executing queries,
 * rendering results, and managing UI state.
 */

// ---------------------------------------------------------------------------
// DOM References
// ---------------------------------------------------------------------------
const questionInput  = document.getElementById("question-input");
const btnGenerate    = document.getElementById("btn-generate");
const btnExecute     = document.getElementById("btn-execute");
const btnClear       = document.getElementById("btn-clear");
const btnCopy        = document.getElementById("btn-copy");

const sqlSection     = document.getElementById("sql-section");
const sqlOutput      = document.getElementById("sql-output");

const resultsSection = document.getElementById("results-section");
const resultsHead    = document.getElementById("results-head");
const resultsBody    = document.getElementById("results-body");
const rowCount       = document.getElementById("row-count");

const errorSection   = document.getElementById("error-section");
const errorMessage   = document.getElementById("error-message");

const loadingOverlay = document.getElementById("loading");
const loadingText    = document.getElementById("loading-text");

// ---------------------------------------------------------------------------
// UI Helpers
// ---------------------------------------------------------------------------

/** Show an element with a slide-up animation. */
function showCard(el) {
    el.classList.remove("hidden");
    el.classList.add("show");
}

/** Hide an element. */
function hideCard(el) {
    el.classList.add("hidden");
    el.classList.remove("show");
}

/** Show the full-screen loading overlay. */
function showLoading(text = "Processing…") {
    loadingText.textContent = text;
    loadingOverlay.classList.remove("hidden");
}

/** Hide the loading overlay. */
function hideLoading() {
    loadingOverlay.classList.add("hidden");
}

/** Display a user-friendly error message. */
function showError(msg) {
    errorMessage.textContent = msg;
    showCard(errorSection);
}

/** Clear any visible error. */
function hideError() {
    hideCard(errorSection);
}

// ---------------------------------------------------------------------------
// API Calls
// ---------------------------------------------------------------------------

/**
 * POST to /generate — send the user's question to the backend,
 * which forwards it to the Groq LLM and returns SQL.
 */
async function generateSQL() {
    const question = questionInput.value.trim();

    // Validate input
    if (!question) {
        showError("Please enter a question first.");
        return;
    }

    hideError();
    hideCard(resultsSection);
    showLoading("Generating SQL…");

    try {
        const response = await fetch("/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question }),
        });

        const data = await response.json();

        if (data.success) {
            // Show the generated SQL
            sqlOutput.textContent = data.sql;
            showCard(sqlSection);
        } else {
            showError(data.message || "Failed to generate SQL.");
            hideCard(sqlSection);
        }
    } catch (err) {
        showError("Network error — could not reach the server.");
        console.error("Generate error:", err);
    } finally {
        hideLoading();
    }
}

/**
 * POST to /execute — send the generated SQL to the backend,
 * which runs it against SQLite and returns the results.
 */
async function executeSQL() {
    const sql = sqlOutput.textContent.trim();

    if (!sql) {
        showError("No SQL query to execute.");
        return;
    }

    hideError();
    showLoading("Executing query…");

    try {
        const response = await fetch("/execute", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ sql }),
        });

        const data = await response.json();

        if (data.success) {
            renderTable(data.columns, data.rows);
            showCard(resultsSection);
        } else {
            showError(data.message || "Query execution failed.");
            hideCard(resultsSection);
        }
    } catch (err) {
        showError("Network error — could not reach the server.");
        console.error("Execute error:", err);
    } finally {
        hideLoading();
    }
}

// ---------------------------------------------------------------------------
// Table Rendering
// ---------------------------------------------------------------------------

/**
 * Build the HTML for the results table from columns & rows arrays.
 */
function renderTable(columns, rows) {
    // Header row
    resultsHead.innerHTML = "<tr>" +
        columns.map(col => `<th>${escapeHtml(col)}</th>`).join("") +
        "</tr>";

    // Body rows
    if (rows.length === 0) {
        resultsBody.innerHTML =
            `<tr><td colspan="${columns.length}" style="text-align:center; color: var(--text-muted);">No results found.</td></tr>`;
    } else {
        resultsBody.innerHTML = rows.map(row =>
            "<tr>" +
            row.map(cell => `<td>${escapeHtml(String(cell ?? "NULL"))}</td>`).join("") +
            "</tr>"
        ).join("");
    }

    // Update row count badge
    rowCount.textContent = `${rows.length} row${rows.length !== 1 ? "s" : ""}`;
}

/** Simple HTML-escape to prevent XSS in table cells. */
function escapeHtml(str) {
    const div = document.createElement("div");
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
}

// ---------------------------------------------------------------------------
// Clear & Copy
// ---------------------------------------------------------------------------

/** Reset the entire form to its initial state. */
function clearAll() {
    questionInput.value = "";
    sqlOutput.textContent = "";
    resultsHead.innerHTML = "";
    resultsBody.innerHTML = "";
    rowCount.textContent = "";
    hideCard(sqlSection);
    hideCard(resultsSection);
    hideError();
    questionInput.focus();
}

/** Copy the generated SQL to the clipboard. */
async function copySQL() {
    const sql = sqlOutput.textContent.trim();
    if (!sql) return;

    try {
        await navigator.clipboard.writeText(sql);
        // Brief visual feedback
        const originalText = btnCopy.innerHTML;
        btnCopy.innerHTML = '<span class="btn-icon">✅</span> Copied!';
        setTimeout(() => { btnCopy.innerHTML = originalText; }, 1500);
    } catch {
        showError("Could not copy to clipboard.");
    }
}

// ---------------------------------------------------------------------------
// Event Listeners
// ---------------------------------------------------------------------------

btnGenerate.addEventListener("click", generateSQL);
btnExecute.addEventListener("click", executeSQL);
btnClear.addEventListener("click", clearAll);
btnCopy.addEventListener("click", copySQL);

// Example chips — clicking one fills the textarea
document.querySelectorAll(".chip").forEach(chip => {
    chip.addEventListener("click", () => {
        questionInput.value = chip.dataset.question;
        questionInput.focus();
    });
});

// Allow Ctrl+Enter to generate SQL from the textarea
questionInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        generateSQL();
    }
});

// ---------------------------------------------------------------------------
// Theme Management — Dark (Default) 🌙 | Light ☀️
// ---------------------------------------------------------------------------
(function initTheme() {
    const STORAGE_KEY = "sql-qg-theme";
    const btnToggle   = document.getElementById("btn-theme-toggle");
    if (!btnToggle) return;

    /** Apply theme choice. */
    function applyTheme(theme) {
        if (theme === "light") {
            document.documentElement.setAttribute("data-theme", "light");
            btnToggle.textContent = "🌙"; // Show moon icon in light mode
            btnToggle.title = "Switch to Dark Mode";
        } else {
            document.documentElement.removeAttribute("data-theme");
            btnToggle.textContent = "☀️"; // Show sun icon in dark mode
            btnToggle.title = "Switch to Light Mode";
        }
        try { localStorage.setItem(STORAGE_KEY, theme); } catch (_) {}
    }

    // Toggle theme on click
    btnToggle.addEventListener("click", () => {
        const current = document.documentElement.getAttribute("data-theme") === "light" ? "light" : "dark";
        const next = current === "light" ? "dark" : "light";
        applyTheme(next);
    });

    // Restore saved preference (default: dark)
    let saved = "dark";
    try { saved = localStorage.getItem(STORAGE_KEY) || "dark"; } catch (_) {}
    applyTheme(saved);
})();
