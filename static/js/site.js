document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-counter-input]").forEach((input) => {
    const counter = input.closest("form")?.querySelector("[data-counter]");
    if (!counter) return;
    const limit = Number(counter.dataset.limit || input.maxLength || 0);
    const update = () => {
      const length = input.value.length;
      counter.textContent = length + " / " + limit;
      counter.classList.toggle("near-limit", limit > 0 && length >= limit * 0.85);
      counter.classList.toggle("at-limit", limit > 0 && length >= limit);
    };
    input.addEventListener("input", update);
    update();
  });
  document.querySelectorAll("form[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (event) => {
      if (!window.confirm(form.dataset.confirm || "Are you sure?")) event.preventDefault();
    });
  });
});
