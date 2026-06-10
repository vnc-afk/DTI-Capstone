document.addEventListener("DOMContentLoaded", () => {
  // Open popup when clicking verify button
  document.querySelectorAll(".approve-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const userId = btn.dataset.bsTarget.replace("#verifyModal", "");
      const popup = document.getElementById(`verifyPopup${userId}`);
      popup.classList.add("active");
    });
  });

  // Close popup
  document.querySelectorAll(".close-popup").forEach(btn => {
    btn.addEventListener("click", () => {
      const popupId = btn.dataset.popupId;
      document.getElementById(popupId).classList.remove("active");
    });
  });
});
