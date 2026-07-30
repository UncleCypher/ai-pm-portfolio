const contactDialog = document.querySelector("#contactDialog");
const openContact = document.querySelector("#openContact");
const closeContact = document.querySelector("#closeContact");
const copyStatus = document.querySelector("#copyStatus");

openContact.addEventListener("click", () => {
  contactDialog.showModal();
});

closeContact.addEventListener("click", () => {
  contactDialog.close();
});

contactDialog.addEventListener("click", (event) => {
  if (event.target === contactDialog) contactDialog.close();
});

document.querySelectorAll("[data-copy]").forEach((button) => {
  button.addEventListener("click", async () => {
    const value = button.dataset.copy;
    try {
      await navigator.clipboard.writeText(value);
      copyStatus.textContent = `已复制：${value}`;
      button.textContent = "已复制";
      window.setTimeout(() => {
        button.textContent = "复制";
        copyStatus.textContent = "";
      }, 1800);
    } catch {
      copyStatus.textContent = `请手动复制：${value}`;
    }
  });
});
