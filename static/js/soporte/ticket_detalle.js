document.addEventListener("DOMContentLoaded", function () {
    var chatBody = document.getElementById("chatBody");
    if (chatBody) {
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    var messageInput = document.getElementById("mensaje");
    if (messageInput) {
        messageInput.addEventListener("keydown", function (e) {
            if (e.key !== "Enter") return;
            if (e.shiftKey) return;

            e.preventDefault();

            var text = (messageInput.value || "").trim();
            var hasFile = false;
            var fileInputEl = document.getElementById("adjunto");
            if (fileInputEl && fileInputEl.files && fileInputEl.files.length > 0) {
                hasFile = true;
            }

            if (!text && !hasFile) {
                return;
            }

            var form = messageInput.closest("form");
            if (form) {
                form.requestSubmit();
            }
        });
    }

    var fileInput = document.getElementById("adjunto");
    var fileNameEl = document.getElementById("adjuntoNombre");
    if (fileInput) {
        fileInput.addEventListener("change", function () {
            if (!fileNameEl) return;
            if (fileInput.files && fileInput.files.length > 0) {
                var file = fileInput.files[0];
                var isImage = false;
                if (file.type && file.type.indexOf("image/") === 0) {
                    isImage = true;
                } else {
                    var name = (file.name || "").toLowerCase();
                    isImage = name.endsWith(".png") || name.endsWith(".jpg") || name.endsWith(".jpeg") || name.endsWith(".gif") || name.endsWith(".webp");
                }

                if (isImage) {
                    fileNameEl.textContent = "";
                    fileNameEl.hidden = true;
                } else {
                    fileNameEl.textContent = file.name;
                    fileNameEl.hidden = false;
                }
            } else {
                fileNameEl.textContent = "";
                fileNameEl.hidden = true;
            }
        });
    }
});
