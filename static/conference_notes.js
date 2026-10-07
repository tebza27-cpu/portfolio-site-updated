(() => {
    const storageKey = "october-2026-conference-notes-v1";
    const actionList = document.getElementById("conference-action-list");
    const customList = document.getElementById("conference-custom-list");
    const form = document.getElementById("conference-custom-form");
    const progress = document.getElementById("conference-progress");
    const progressLabel = document.getElementById("conference-progress-label");

    if (!actionList || !customList || !form) return;

    const defaultState = {
        reflections: {
            impression: "Jesus Christ is the Deliverer, Comforter, and Light who can carry me through affliction, uncertainty, and discouragement. His promises and the pattern of covenant worship give me hope and steadiness.",
            change: "I will start by making covenant worship and prayer more deliberate, stop letting fear or discouragement drive my choices, and continue serving with integrity and purpose.",
            person: "A friend or family member who feels overlooked, discouraged, or burdened. I can reach out, listen, and offer specific help without waiting to be asked."
        },
        actions: {
            revisit: {
                complete: false,
                note: "I will study the talk 'Jesus Christ Is the Great Deliverer!' this week and write down one teaching I can apply immediately in my life."
            },
            "daily-worship": {
                complete: false,
                note: "I will strengthen my scripture study and prayer by setting aside 15 minutes each morning before work and asking for guidance to act with faith and humility."
            },
            compassion: {
                complete: false,
                note: "I will contact one person who feels alone and offer a specific act of kindness or encouragement by the end of the week."
            },
            peacemaker: {
                complete: false,
                note: "I will pause before responding in one difficult conversation and choose language that is both truthful and compassionate."
            },
            share: {
                complete: false,
                note: "I will share a simple testimony that Jesus Christ is a source of peace and deliverance with someone who is struggling or seeking hope."
            }
        },
        custom: [
            {
                id: "custom-default-action",
                text: "Complete one specific act of service or encouragement for someone who seems discouraged or overlooked.",
                due: "2026-10-10",
                complete: false
            }
        ]
    };

    let saved = {};
    try {
        saved = JSON.parse(localStorage.getItem(storageKey) || "{}") || {};
        if (!saved.reflections && !saved.actions && !saved.custom) {
            saved = defaultState;
        }
    } catch {
        saved = defaultState;
    }

    const mergedState = {
        reflections: { ...defaultState.reflections, ...(saved.reflections || {}) },
        actions: { ...defaultState.actions, ...(saved.actions || {}) },
        custom: Array.isArray(saved.custom) && saved.custom.length ? saved.custom : defaultState.custom
    };
    saved = mergedState;

    const save = () => {
        const state = {
            reflections: Object.fromEntries(
                [...document.querySelectorAll("[data-reflection]")].map((field) => [field.dataset.reflection, field.value])
            ),
            actions: Object.fromEntries(
                [...actionList.querySelectorAll("[data-action-id]")].map((card) => [
                    card.dataset.actionId,
                    {
                        complete: card.querySelector('input[type="checkbox"]').checked,
                        note: card.querySelector("[data-action-note]").value,
                    },
                ])
            ),
            custom: [...customList.querySelectorAll("[data-custom-id]")].map((row) => ({
                id: row.dataset.customId,
                text: row.querySelector("[data-custom-text]").textContent,
                due: row.dataset.due || "",
                complete: row.querySelector('input[type="checkbox"]').checked,
            })),
        };

        try {
            localStorage.setItem(storageKey, JSON.stringify(state));
        } catch {
            progressLabel.textContent = "Browser storage is unavailable; notes may not persist.";
        }
        updateProgress();
    };

    const updateProgress = () => {
        const fixedCards = [...actionList.querySelectorAll("[data-action-id]")];
        const customRows = [...customList.querySelectorAll("[data-custom-id]")];
        const total = fixedCards.length + customRows.length;
        const complete = [...fixedCards, ...customRows].filter((item) => item.querySelector('input[type="checkbox"]').checked).length;
        progress.max = Math.max(total, 1);
        progress.value = complete;
        progressLabel.textContent = `${complete} of ${total} complete`;
    };

    const renderCustom = (task) => {
        const row = document.createElement("div");
        row.className = "conference-custom-task";
        row.dataset.customId = task.id;
        row.dataset.due = task.due || "";

        const label = document.createElement("label");
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.checked = Boolean(task.complete);
        const text = document.createElement("span");
        text.dataset.customText = "";
        text.textContent = task.due ? `${task.text} (by ${task.due})` : task.text;
        label.append(checkbox, text);

        const remove = document.createElement("button");
        remove.type = "button";
        remove.className = "conference-remove-task";
        remove.textContent = "Remove";
        remove.setAttribute("aria-label", `Remove action: ${task.text}`);
        remove.addEventListener("click", () => {
            row.remove();
            save();
        });
        checkbox.addEventListener("change", () => {
            row.classList.toggle("is-complete", checkbox.checked);
            save();
        });
        row.classList.toggle("is-complete", checkbox.checked);
        row.append(label, remove);
        customList.append(row);
    };

    for (const field of document.querySelectorAll("[data-reflection]")) {
        field.value = saved.reflections?.[field.dataset.reflection] || defaultState.reflections[field.dataset.reflection] || "";
        field.addEventListener("input", save);
    }

    for (const card of actionList.querySelectorAll("[data-action-id]")) {
        const previous = saved.actions?.[card.dataset.actionId] || defaultState.actions[card.dataset.actionId] || {};
        const checkbox = card.querySelector('input[type="checkbox"]');
        const note = card.querySelector("[data-action-note]");
        checkbox.checked = Boolean(previous.complete);
        note.value = previous.note || defaultState.actions[card.dataset.actionId]?.note || "";
        card.classList.toggle("is-complete", checkbox.checked);
        checkbox.addEventListener("change", () => {
            card.classList.toggle("is-complete", checkbox.checked);
            save();
        });
        note.addEventListener("input", save);
    }

    for (const task of saved.custom || defaultState.custom) renderCustom(task);

    form.addEventListener("submit", (event) => {
        event.preventDefault();
        const data = new FormData(form);
        const text = String(data.get("action") || "").trim();
        if (!text) return;
        renderCustom({
            id: `custom-${Date.now()}`,
            text,
            due: String(data.get("due") || ""),
            complete: false,
        });
        form.reset();
        save();
        document.getElementById("conference-custom-text").focus();
    });

    document.getElementById("conference-print")?.addEventListener("click", () => window.print());
    updateProgress();
})();