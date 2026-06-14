/* LearnHub frontend — vanilla JS single-page app.
 * Talks to the FastAPI backend at /api. State kept in localStorage. */

const API = "/api";
const State = {
  get token() { return localStorage.getItem("lh_token"); },
  set token(v) { v ? localStorage.setItem("lh_token", v) : localStorage.removeItem("lh_token"); },
  get user() { return JSON.parse(localStorage.getItem("lh_user") || "null"); },
  set user(v) { v ? localStorage.setItem("lh_user", JSON.stringify(v)) : localStorage.removeItem("lh_user"); },
};

/* ---------- API helper ---------- */
async function api(path, { method = "GET", body } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (State.token) headers.Authorization = `Bearer ${State.token}`;
  const res = await fetch(API + path, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (res.status === 204) return null;
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "Request failed");
  return data;
}

/* ---------- UI helpers ---------- */
function toast(msg, isErr = false) {
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.className = "toast show" + (isErr ? " err" : "");
  setTimeout(() => (t.className = "toast"), 2600);
}
const el = (id) => document.getElementById(id);
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

function renderNav() {
  const nav = el("nav");
  const u = State.user;
  if (u) {
    nav.innerHTML = `
      <span class="muted">${esc(u.full_name || u.email)} · ${u.role}</span>
      <button class="ghost" onclick="Views.show('dashboard')">My Learning</button>
      ${u.role !== "learner" ? `<button class="ghost" onclick="Views.show('create')">+ Course</button>` : ""}
      <button class="ghost" onclick="logout()">Logout</button>`;
  } else {
    nav.innerHTML = `<button class="primary" onclick="Views.show('login')">Login</button>`;
  }
}

function logout() {
  State.token = null;
  State.user = null;
  renderNav();
  Views.show("catalog");
  toast("Logged out");
}

/* ---------- Views ---------- */
const Views = {
  show(name, arg) {
    renderNav();
    (this[name] || this.catalog)(arg);
  },

  async catalog() {
    const view = el("view");
    view.innerHTML = `<h1>Course Catalog</h1>
      <div class="row"><input id="q" placeholder="Search courses..." style="max-width:340px"
        oninput="Views.catalog._debounce(this.value)" /></div>
      <div id="courses" class="grid">Loading…</div>`;
    const load = async (q = "") => {
      try {
        const courses = await api(`/courses${q ? "?q=" + encodeURIComponent(q) : ""}`);
        el("courses").innerHTML = courses.length
          ? courses.map(courseCard).join("")
          : `<p class="muted">No courses found.</p>`;
      } catch (e) { toast(e.message, true); }
    };
    let timer;
    Views.catalog._debounce = (v) => { clearTimeout(timer); timer = setTimeout(() => load(v), 250); };
    load();
  },

  async detail(id) {
    const view = el("view");
    view.innerHTML = "Loading…";
    try {
      const c = await api(`/courses/${id}`);
      const lessons = c.sections.flatMap((s) =>
        [`<div class="muted" style="margin-top:10px"><b>${esc(s.title)}</b></div>`]
          .concat(s.lessons.map((l) => `<div class="lesson"><span>▶ ${esc(l.title)}</span>
            <span class="muted">${Math.round(l.duration / 60)} min${l.is_free_preview ? " · free" : ""}</span></div>`)));
      view.innerHTML = `
        <a class="link" onclick="Views.show('catalog')">← Catalog</a>
        <div class="spread"><h1>${esc(c.title)}</h1>
          <span class="badge ${c.is_free ? "free" : "paid"}">${c.is_free ? "Free" : "₹" + c.price}</span></div>
        <p class="muted">${esc(c.description)}</p>
        <div class="meta muted">⭐ ${c.rating_avg} (${c.review_count}) · ${esc(c.category)}</div>
        <div class="row" style="margin:16px 0">
          <button class="primary" onclick="enroll(${c.id})">Enroll</button>
          ${State.user && State.user.role !== "learner" ? `<button onclick="Views.show('quizBuilder', ${c.id})">+ Add Quiz</button>` : ""}
        </div>
        <div class="panel">${lessons.join("") || "<span class='muted'>No lessons yet.</span>"}</div>
        ${c.quizzes && c.quizzes.length ? `<h3 style="margin-top:24px">Quizzes</h3>
          <div class="panel">${c.quizzes.map((qz) => `<div class="lesson">
            <span>📝 ${esc(qz.title)}</span>
            <button class="ghost" onclick="Views.show('quiz', ${qz.id})">Take Quiz</button></div>`).join("")}</div>` : ""}`;
    } catch (e) { toast(e.message, true); }
  },

  async dashboard() {
    if (!State.user) return Views.show("login");
    const view = el("view");
    view.innerHTML = "Loading…";
    try {
      const enrollments = await api("/enrollments");
      view.innerHTML = `<h1>My Learning</h1>
        ${enrollments.length === 0 ? `<p class="muted">Not enrolled yet. <a class="link" onclick="Views.show('catalog')">Browse courses</a></p>` : ""}
        <div class="grid">${enrollments.map(enrollmentCard).join("")}</div>`;
    } catch (e) { toast(e.message, true); }
  },

  login() {
    el("view").innerHTML = `
      <div class="auth-box panel">
        <h1>Login</h1>
        <input id="email" placeholder="Email" value="learner@learnhub.dev" />
        <input id="password" type="password" placeholder="Password" value="Passw0rd!" />
        <button class="primary" style="width:100%" onclick="doLogin()">Login</button>
        <p class="muted" style="margin-top:14px">No account? <a class="link" onclick="Views.show('register')">Register</a></p>
        <p class="muted" style="font-size:12px">Demo: learner@ / instructor@ / admin@learnhub.dev · Passw0rd!</p>
      </div>`;
  },

  register() {
    el("view").innerHTML = `
      <div class="auth-box panel">
        <h1>Create account</h1>
        <input id="full_name" placeholder="Full name" />
        <input id="email" placeholder="Email" />
        <input id="password" type="password" placeholder="Password" />
        <select id="role"><option value="learner">Learner</option><option value="instructor">Instructor</option></select>
        <button class="primary" style="width:100%" onclick="doRegister()">Register</button>
        <p class="muted" style="margin-top:14px">Have an account? <a class="link" onclick="Views.show('login')">Login</a></p>
      </div>`;
  },

  create() {
    if (!State.user || State.user.role === "learner") return Views.show("login");
    el("view").innerHTML = `
      <div class="auth-box panel" style="max-width:520px">
        <h1>New Course</h1>
        <input id="title" placeholder="Course title" />
        <textarea id="description" placeholder="Description" rows="3"></textarea>
        <input id="category" placeholder="Category" value="General" />
        <div class="row">
          <label class="row"><input type="checkbox" id="is_free" checked style="width:auto" /> Free</label>
          <input id="price" type="number" placeholder="Price (₹)" value="0" style="max-width:140px" />
        </div>
        <button class="primary" style="width:100%" onclick="doCreateCourse()">Create</button>
      </div>`;
  },

  quizBuilder(courseId) {
    el("view").innerHTML = `
      <div class="auth-box panel" style="max-width:560px">
        <h1>Add Quiz</h1>
        <input id="quizTitle" placeholder="Quiz title" value="Module Quiz" />
        <p class="muted">One question per line: <code>prompt | optA,optB,optC | correct</code></p>
        <textarea id="quizQs" rows="5" placeholder="Which keyword defines a function? | func,def,lambda | def"></textarea>
        <button class="primary" style="width:100%" onclick="doCreateQuiz(${courseId})">Save Quiz</button>
      </div>`;
  },

  async quiz(quizId) {
    el("view").innerHTML = "Loading…";
    try {
      const quiz = await api(`/quizzes/${quizId}`);
      el("view").innerHTML = `
        <h1>${esc(quiz.title)}</h1>
        <p class="muted">Pass mark: ${quiz.pass_mark}% · Max attempts: ${quiz.max_attempts}</p>
        <div id="qs">${quiz.questions.map((q, i) => `
          <div class="qcard"><b>Q${i + 1}. ${esc(q.prompt)}</b>
            ${q.options.map((o) => `<label class="opt">
              <input type="radio" name="q${q.id}" value="${esc(o)}" style="width:auto" /> ${esc(o)}</label>`).join("")}
          </div>`).join("")}</div>
        <button class="primary" onclick='submitQuiz(${quizId}, ${JSON.stringify(quiz.questions.map((q) => q.id))})'>Submit</button>
        <div id="quizResult" style="margin-top:18px"></div>`;
    } catch (e) { toast(e.message, true); }
  },
};

/* ---------- Card renderers ---------- */
function courseCard(c) {
  return `<div class="card" onclick="Views.show('detail', ${c.id})" style="cursor:pointer">
    <div class="spread"><h3>${esc(c.title)}</h3>
      <span class="badge ${c.is_free ? "free" : "paid"}">${c.is_free ? "Free" : "₹" + c.price}</span></div>
    <p class="muted" style="font-size:14px">${esc(c.description.slice(0, 90))}…</p>
    <div class="meta">⭐ ${c.rating_avg} (${c.review_count}) · ${esc(c.category)}</div>
  </div>`;
}

function enrollmentCard(e) {
  const c = e.course || {};
  return `<div class="card">
    <h3>${esc(c.title || "Course #" + e.course_id)}</h3>
    <div class="progress"><div style="width:${e.progress}%"></div></div>
    <div class="meta">${e.progress}% complete</div>
    <div class="row" style="margin-top:12px">
      <button onclick="bumpProgress(${e.id}, ${Math.min(100, e.progress + 25)})">+25% progress</button>
      <button class="ghost" onclick="Views.show('detail', ${e.course_id})">Open Course</button>
    </div>
  </div>`;
}

/* ---------- Actions ---------- */
async function doLogin() {
  try {
    const r = await api("/auth/login", { method: "POST", body: { email: el("email").value, password: el("password").value } });
    State.token = r.access_token; State.user = r.user;
    toast("Welcome back!"); Views.show("dashboard");
  } catch (e) { toast(e.message, true); }
}

async function doRegister() {
  try {
    const r = await api("/auth/register", { method: "POST", body: {
      full_name: el("full_name").value, email: el("email").value,
      password: el("password").value, role: el("role").value } });
    State.token = r.access_token; State.user = r.user;
    toast("Account created!"); Views.show("dashboard");
  } catch (e) { toast(e.message, true); }
}

async function doCreateCourse() {
  try {
    const c = await api("/courses", { method: "POST", body: {
      title: el("title").value, description: el("description").value,
      category: el("category").value, is_free: el("is_free").checked,
      price: parseFloat(el("price").value) || 0 } });
    toast("Course created!"); Views.show("detail", c.id);
  } catch (e) { toast(e.message, true); }
}

async function doCreateQuiz(courseId) {
  const lines = el("quizQs").value.split("\n").map((l) => l.trim()).filter(Boolean);
  const questions = lines.map((line, i) => {
    const [prompt, opts, correct] = line.split("|").map((p) => p.trim());
    return { type: "mcq", prompt, options: (opts || "").split(",").map((o) => o.trim()), correct_answer: correct, position: i + 1 };
  });
  try {
    await api(`/courses/${courseId}/quizzes`, { method: "POST", body: { title: el("quizTitle").value, questions } });
    toast("Quiz saved!"); Views.show("detail", courseId);
  } catch (e) { toast(e.message, true); }
}

async function enroll(courseId) {
  if (!State.user) return Views.show("login");
  try {
    await api(`/enrollments/${courseId}`, { method: "POST" });
    toast("Enrolled!"); Views.show("dashboard");
  } catch (e) { toast(e.message, true); }
}

async function bumpProgress(enrollmentId, value) {
  try {
    await api(`/enrollments/${enrollmentId}/progress`, { method: "PATCH", body: { progress: value } });
    Views.show("dashboard");
  } catch (e) { toast(e.message, true); }
}

async function submitQuiz(quizId, questionIds) {
  const answers = questionIds.map((id) => {
    const sel = document.querySelector(`input[name="q${id}"]:checked`);
    return { question_id: id, answer: sel ? sel.value : "" };
  });
  try {
    const r = await api(`/quizzes/${quizId}/submit`, { method: "POST", body: { answers } });
    el("quizResult").innerHTML = `<div class="result-banner ${r.passed ? "pass" : "fail"}">
      ${r.passed ? "✅ Passed" : "❌ Failed"} — ${r.score}% (${r.correct}/${r.total}) · attempt ${r.attempt_number}</div>`;
  } catch (e) { toast(e.message, true); }
}

/* ---------- Boot ---------- */
renderNav();
// Simple hash routing — supports deep links like #login, #dashboard, #catalog.
const _initial = location.hash.slice(1);
Views.show(["login", "register", "dashboard", "create"].includes(_initial) ? _initial : "catalog");
