// Logique du chatbot, partagée par la page /chat et les pages de détail.
const cfg = window.CHAT_CONFIG;
const log = document.getElementById("chat-log");
const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");
const level = document.getElementById("level");
let history = [];

function addMessage(role, text) {
  const div = document.createElement("div");
  div.className = "msg " + role;
  div.textContent = text;           // textContent : pas d'injection HTML
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
  return div;
}

async function send(question) {
  addMessage("user", question);
  const wait = addMessage("bot", "…");
  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, history, slug: cfg.slug, year: cfg.year, level: level.value }),
    });
    const data = await res.json();
    wait.textContent = data.answer || data.error || "Erreur inconnue.";
    history.push({ role: "user", content: question }, { role: "assistant", content: wait.textContent });
  } catch (e) {
    wait.textContent = "Connexion impossible avec le serveur.";
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const q = input.value.trim();
  if (q) { input.value = ""; send(q); }
});

const explainBtn = document.getElementById("explain-btn");
if (explainBtn) {
  explainBtn.addEventListener("click", () =>
    send(`Explique-moi l'origine, la signification et les traditions de : ${cfg.name}.`));
}
document.querySelectorAll(".chip").forEach((c) =>
  c.addEventListener("click", () => send(c.textContent)));
