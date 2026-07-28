const API_BASE = "http://localhost:8000";

let sessionId = null;

// -----------------------------------------------------
// Elements
// -----------------------------------------------------

const chatMessages = document.getElementById("chatMessages");
const sourcesContainer = document.getElementById("sourcesContainer");

const pdfFile = document.getElementById("pdfFile");
const urlInput = document.getElementById("urlInput");
const questionInput = document.getElementById("questionInput");

const uploadPdfBtn = document.getElementById("uploadPdfBtn");
const uploadUrlBtn = document.getElementById("uploadUrlBtn");
const sendBtn = document.getElementById("sendBtn");

const newSessionBtn = document.getElementById("newSessionBtn");
const clearChatBtn = document.getElementById("clearChatBtn");
const clearCacheBtn = document.getElementById("clearCacheBtn");
const deleteKbBtn = document.getElementById("deleteKbBtn");

const loadingOverlay = document.getElementById("loadingOverlay");
const loadingText = document.getElementById("loadingText");

const toast = document.getElementById("toast");
const toastMessage = document.getElementById("toastMessage");

const sessionLabel = document.getElementById("sessionId");
const chunkLabel = document.getElementById("chunkCount");
const serverStatus = document.getElementById("serverStatus");

// -----------------------------------------------------
// Helpers
// -----------------------------------------------------

function showLoading(message = "Processing...") {
    loadingText.textContent = message;
    loadingOverlay.classList.remove("hidden");
}

function hideLoading() {
    loadingOverlay.classList.add("hidden");
}

function showToast(message) {

    toastMessage.textContent = message;

    toast.classList.remove("hidden");

    setTimeout(() => {

        toast.classList.add("hidden");

    }, 3000);
}

function scrollBottom() {

    chatMessages.scrollTop = chatMessages.scrollHeight;

}

// -----------------------------------------------------
// Session
// -----------------------------------------------------

async function createSession() {

    try {

        const response = await fetch(`${API_BASE}/session/new`);

        const data = await response.json();

        sessionId = data.session_id;

        sessionLabel.textContent = sessionId;

    } catch (err) {

        console.error(err);

        showToast("Unable to create session.");

    }

}

// -----------------------------------------------------
// Chat UI
// -----------------------------------------------------

function addMessage(role, text) {

    const template = document
        .getElementById("messageTemplate")
        .content
        .cloneNode(true);

    const message = template.querySelector(".message");

    const avatar = template.querySelector(".avatar");

    const bubble = template.querySelector(".bubble");

    message.classList.add(role);

    avatar.textContent = role === "user" ? "🧑" : "🤖";

    bubble.textContent = text;

    chatMessages.appendChild(template);

    scrollBottom();

}

function clearMessages() {

    chatMessages.innerHTML = "";

}

function renderSources(sources = []) {

    sourcesContainer.innerHTML = "";

    if (!sources.length) {

        sourcesContainer.textContent = "No sources found.";

        return;

    }

    const template = document.getElementById("sourceTemplate");

    sources.forEach(source => {

        const node = template.content.cloneNode(true);

        node.querySelector(".source-title").textContent =
            source.source || source.file || "Document";

        node.querySelector(".source-page").textContent =
            source.page
                ? `Page ${source.page}`
                : "";

        sourcesContainer.appendChild(node);

    });

}

// -----------------------------------------------------
// Upload PDF
// -----------------------------------------------------

async function uploadPDF() {

    if (!pdfFile.files.length) {

        showToast("Select a PDF first.");

        return;

    }

    const form = new FormData();

    form.append("file", pdfFile.files[0]);

    showLoading("Uploading PDF...");

    try {

        const response = await fetch(`${API_BASE}/upload/pdf`, {

            method: "POST",

            body: form

        });

        const data = await response.json();

        hideLoading();

        if (!response.ok) {

            showToast(data.detail || "Upload failed.");

            return;

        }

        showToast("PDF uploaded successfully.");

        await refreshHealth();

    }

    catch (err) {

        hideLoading();

        console.error(err);

        showToast("Upload failed.");

    }

}

// -----------------------------------------------------
// Upload URL
// -----------------------------------------------------

async function uploadURL() {

    const url = urlInput.value.trim();

    if (!url) {

        showToast("Enter a URL.");

        return;

    }

    showLoading("Loading Website...");

    try {

        const response = await fetch(`${API_BASE}/upload/url`, {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify({

                url: url

            })

        });

        const data = await response.json();

        hideLoading();

        if (!response.ok) {

            showToast(data.detail || "URL upload failed.");

            return;

        }

        showToast("Website indexed.");

        urlInput.value = "";

        await refreshHealth();

    }

    catch (err) {

        hideLoading();

        console.error(err);

        showToast("Upload failed.");

    }

}
// -----------------------------------------------------
// Chat
// -----------------------------------------------------

async function sendMessage() {

    const question = questionInput.value.trim();

    if (!question) {
        return;
    }

    addMessage("user", question);

    questionInput.value = "";

    showLoading("Thinking...");

    try {

        const response = await fetch(`${API_BASE}/chat`, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                session_id: sessionId,
                question: question
            })

        });

        const data = await response.json();

        hideLoading();

        if (!response.ok) {

            addMessage("assistant", data.detail || "Something went wrong.");

            return;

        }

        addMessage(
            "assistant",
            data.answer || "No response received."
        );

        renderSources(data.sources || []);

    } catch (err) {

        hideLoading();

        console.error(err);

        addMessage(
            "assistant",
            "Unable to connect to the backend."
        );

    }

}

// -----------------------------------------------------
// History
// -----------------------------------------------------

async function loadHistory() {

    if (!sessionId) return;

    try {

        const response = await fetch(
            `${API_BASE}/history/${sessionId}`
        );

        if (!response.ok) return;

        const data = await response.json();

        clearMessages();

        (data.history || []).forEach(msg => {

            addMessage(
                msg.role,
                msg.content
            );

        });

    } catch (err) {

        console.error(err);

    }

}

// -----------------------------------------------------
// Health
// -----------------------------------------------------

async function refreshHealth() {

    try {

        const response = await fetch(`${API_BASE}/health`);

        if (!response.ok) return;

        const data = await response.json();

        serverStatus.textContent =
            data.status || "Unknown";

        chunkLabel.textContent =
            data.indexed_chunks ?? 0;

    } catch (err) {

        serverStatus.textContent = "Offline";

    }

}

// -----------------------------------------------------
// Buttons
// -----------------------------------------------------

async function clearChat() {

    clearMessages();

    renderSources([]);

    questionInput.value = "";

}

async function clearCache() {

    try {

        await fetch(`${API_BASE}/cache`, {

            method: "DELETE"

        });

        showToast("Cache cleared.");

    } catch (err) {

        showToast("Unable to clear cache.");

    }

}

async function deleteKnowledgeBase() {

    const confirmed = confirm(
        "Delete the complete knowledge base?"
    );

    if (!confirmed) return;

    showLoading("Deleting...");

    try {

        await fetch(`${API_BASE}/knowledge-base`, {

            method: "DELETE"

        });

        hideLoading();

        renderSources([]);

        chunkLabel.textContent = "0";

        showToast("Knowledge base deleted.");

    } catch (err) {

        hideLoading();

        showToast("Unable to delete knowledge base.");

    }

}

async function startNewSession() {

    clearMessages();

    renderSources([]);

    await createSession();

    showToast("New session created.");

}

// -----------------------------------------------------
// Events
// -----------------------------------------------------

uploadPdfBtn.addEventListener(
    "click",
    uploadPDF
);

uploadUrlBtn.addEventListener(
    "click",
    uploadURL
);

sendBtn.addEventListener(
    "click",
    sendMessage
);

newSessionBtn.addEventListener(
    "click",
    startNewSession
);

clearChatBtn.addEventListener(
    "click",
    clearChat
);

clearCacheBtn.addEventListener(
    "click",
    clearCache
);

deleteKbBtn.addEventListener(
    "click",
    deleteKnowledgeBase
);

questionInput.addEventListener(
    "keydown",
    event => {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            sendMessage();

        }

    }
);

// -----------------------------------------------------
// Initialize
// -----------------------------------------------------

async function initialize() {

    await createSession();

    await refreshHealth();

    await loadHistory();

}

initialize();

setInterval(
    refreshHealth,
    10000
);