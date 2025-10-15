document.addEventListener("DOMContentLoaded", function () {
    const openUploadFilesModalBtn = document.getElementById("upload-from-excel-btn");
    const uploadFilesModal = document.getElementById("upload-files-modal-container");
    const uploadFilesContainer = document.getElementById("upload-files-container");
    const closeUploadFilesModalBtn = uploadFilesModal ? uploadFilesModal.querySelector(".close-modal-btn") : null;

    const fileInput = document.getElementById("file-input");
    const uploadedFilesList = document.querySelector(".uploaded-files-list");
    const fileText = document.getElementById("file-text");

    let allFiles = []; // keep track of all selected files

    // Open modal
    if (openUploadFilesModalBtn && uploadFilesModal) {
        openUploadFilesModalBtn.addEventListener("click", function () {
            uploadFilesModal.style.display = "flex";
        });
    }

    // Close modal
    if (closeUploadFilesModalBtn && uploadFilesModal) {
        closeUploadFilesModalBtn.addEventListener("click", function () {
            uploadFilesModal.style.display = "none";
        });
    }

    // Click entire container → open file dialog
    if (uploadFilesContainer && fileInput) {
        uploadFilesContainer.addEventListener("click", () => {
            fileInput.click();
        });
    }

    // Handle file selection
    if (fileInput && uploadedFilesList && fileText) {
        fileInput.addEventListener("change", (event) => {
            const newFiles = Array.from(event.target.files);
            if (newFiles.length === 0) return;

            // Merge new files into allFiles
            allFiles = [...allFiles, ...newFiles];

            // Render fresh list
            uploadedFilesList.innerHTML = "";
            allFiles.forEach((file, index) => {
                const li = document.createElement("li");
                li.innerHTML = `
                    <i class="fa-solid fa-file"></i>
                    <div class="details">
                        <strong>${file.name}</strong>
                        <p>${(file.size / 1024 / 1024).toFixed(2)} MB</p>
                    </div>
                    <i class="fa-solid fa-trash delete-file"></i>
                `;

                // Delete functionality
                li.querySelector(".delete-file").addEventListener("click", () => {
                    allFiles.splice(index, 1); // remove from array
                    li.remove();
                    if (allFiles.length === 0) {
                        fileText.textContent = "No file chosen yet.";
                    } else {
                        fileText.textContent = `(${allFiles.length}) files uploaded`;
                    }
                });

                uploadedFilesList.appendChild(li);
            });

            // Update text with count
            fileText.textContent = `(${allFiles.length}) files uploaded`;
        });
    }
});
