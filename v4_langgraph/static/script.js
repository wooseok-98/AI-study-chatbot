// 채팅 동작 로직 (프론트엔드)

const messagesEl = document.getElementById("messages");
const formEl = document.getElementById("chat-form");
const inputEl = document.getElementById("input");
const buttonEl = formEl.querySelector("button");

// session_id 를 localStorage 에 고정 → 새로고침/재방문해도 같은 세션 유지
let sessionId = localStorage.getItem("session_id");
if (!sessionId) {
  sessionId = "web-" + Math.random().toString(36).slice(2, 10);
  localStorage.setItem("session_id", sessionId);
}

// 메시지 한 줄을 화면에 추가
function addMessage(text, sender) {
  const div = document.createElement("div");
  div.className = `msg ${sender}`;
  div.textContent = text;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight; // 맨 아래로 스크롤
  return div;
}

// 폼 제출(전송) 처리
formEl.addEventListener("submit", async (e) => {
  e.preventDefault();
  const question = inputEl.value.trim();
  if (!question) return;

  addMessage(question, "user"); // 내 메시지 표시
  inputEl.value = "";
  buttonEl.disabled = true;

  const loading = addMessage("…", "bot"); // 로딩 표시
  loading.classList.add("loading");

  try {
    // 백엔드 POST /chat 호출
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, session_id: sessionId }),
    });
    const data = await res.json();
    loading.classList.remove("loading");
    loading.textContent = data.answer; // 답변으로 교체
  } catch (err) {
    loading.classList.remove("loading");
    loading.textContent = "⚠️ 오류가 발생했어요. 서버를 확인해주세요.";
  } finally {
    buttonEl.disabled = false;
    inputEl.focus();
  }
});

// 페이지 열 때 DB에서 지난 대화를 불러와 화면에 복원
async function loadHistory() {
  const res = await fetch(`/chat/${sessionId}/history`);
  const history = await res.json(); // [{role, content}, ...]
  history.forEach((m) => {
    // role: user → 오른쪽(user) / assistant → 왼쪽(bot)
    addMessage(m.content, m.role === "user" ? "user" : "bot");
  });
}

loadHistory();
