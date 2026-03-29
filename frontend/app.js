const goalForm = document.getElementById("goal-form");
const goalList = document.getElementById("goal-list");
const statusText = document.getElementById("status");
const refreshBtn = document.getElementById("refresh-btn");

async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    let message = "Request failed";
    try {
      const errorBody = await response.json();
      message = errorBody.error || errorBody.detail || message;
    } catch (error) {
      // Ignore JSON parsing errors and use fallback message.
    }
    throw new Error(message);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

function setStatus(message, isError = false) {
  statusText.textContent = message;
  statusText.style.color = isError ? "#b91c1c" : "#6b7280";
}

function formatDate(rawDate) {
  if (!rawDate) {
    return "No target date";
  }
  return new Date(rawDate).toLocaleDateString();
}

function renderGoals(goals) {
  goalList.innerHTML = "";

  if (goals.length === 0) {
    const emptyItem = document.createElement("li");
    emptyItem.textContent = "No goals added yet.";
    goalList.appendChild(emptyItem);
    return;
  }

  goals.forEach((goal) => {
    const item = document.createElement("li");
    item.className = `goal-item${goal.completed ? " completed" : ""}`;

    const title = document.createElement("p");
    title.className = "goal-title";
    title.textContent = goal.title;

    const meta = document.createElement("p");
    meta.className = "goal-meta";
    const description = goal.description || "No description";
    meta.textContent = `${description} • ${formatDate(goal.target_date)}`;

    const actions = document.createElement("div");
    actions.className = "goal-actions";

    const toggleBtn = document.createElement("button");
    toggleBtn.type = "button";
    toggleBtn.textContent = goal.completed ? "Mark Open" : "Mark Done";
    toggleBtn.addEventListener("click", async () => {
      try {
        await requestJson(`/api/goals/${goal.id}`, {
          method: "PUT",
          body: JSON.stringify({ completed: !goal.completed }),
        });
        setStatus("Goal updated.");
        await loadGoals();
      } catch (error) {
        setStatus(error.message, true);
      }
    });

    const deleteBtn = document.createElement("button");
    deleteBtn.type = "button";
    deleteBtn.className = "delete";
    deleteBtn.textContent = "Delete";
    deleteBtn.addEventListener("click", async () => {
      try {
        await requestJson(`/api/goals/${goal.id}`, { method: "DELETE" });
        setStatus("Goal deleted.");
        await loadGoals();
      } catch (error) {
        setStatus(error.message, true);
      }
    });

    actions.append(toggleBtn, deleteBtn);
    item.append(title, meta, actions);
    goalList.appendChild(item);
  });
}

async function loadGoals() {
  try {
    const goals = await requestJson("/api/goals");
    renderGoals(goals);
  } catch (error) {
    setStatus(error.message, true);
  }
}

goalForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const formData = new FormData(goalForm);
  const payload = {
    title: String(formData.get("title") || "").trim(),
    description: String(formData.get("description") || "").trim(),
    target_date: String(formData.get("target_date") || "").trim(),
  };

  try {
    await requestJson("/api/goals", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    goalForm.reset();
    setStatus("Goal added.");
    await loadGoals();
  } catch (error) {
    setStatus(error.message, true);
  }
});

refreshBtn.addEventListener("click", () => {
  loadGoals();
  setStatus("Refreshed.");
});

loadGoals();
