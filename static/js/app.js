// Antigravity UI & Interactive Handlers

document.addEventListener('DOMContentLoaded', () => {
    // 1. Image Upload Live Preview
    const imageInput = document.getElementById('image-upload-input');
    const imagePreview = document.getElementById('image-preview');
    const imagePlaceholder = document.getElementById('image-placeholder');

    if (imageInput && imagePreview) {
        imageInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    imagePreview.src = event.target.result;
                    imagePreview.style.display = 'block';
                    if (imagePlaceholder) imagePlaceholder.style.display = 'none';
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // 2. Real-time Duplicate Detection on Report Page
    const titleInput = document.getElementById('report-title');
    const categorySelect = document.getElementById('report-category');
    const locationSelect = document.getElementById('report-location');
    const typeSelect = document.getElementById('report-type');
    const duplicateAlertBox = document.getElementById('duplicate-warning-box');
    const duplicateList = document.getElementById('duplicate-items-list');

    let debounceTimer = null;

    function checkDuplicates() {
        if (!titleInput || !duplicateAlertBox || !duplicateList) return;
        const title = titleInput.value.trim();
        if (title.length < 4) {
            duplicateAlertBox.style.display = 'none';
            return;
        }

        const payload = {
            title: title,
            category: categorySelect ? categorySelect.value : '',
            location: locationSelect ? locationSelect.value : '',
            type: typeSelect ? typeSelect.value : 'LOST'
        };

        fetch('/api/check-duplicates', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            if (data.duplicates && data.duplicates.length > 0) {
                duplicateList.innerHTML = '';
                data.duplicates.forEach(item => {
                    const li = document.createElement('li');
                    li.style.marginBottom = '6px';
                    li.innerHTML = `<strong>${escapeHtml(item.title)}</strong> (${item.score}% match) - reported at <em>${escapeHtml(item.location)}</em> <a href="/item/${item.id}" target="_blank" style="margin-left: 8px; text-decoration: underline;">View &rarr;</a>`;
                    duplicateList.appendChild(li);
                });
                duplicateAlertBox.style.display = 'block';
            } else {
                duplicateAlertBox.style.display = 'none';
            }
        })
        .catch(err => console.error("Duplicate check error:", err));
    }

    if (titleInput) {
        titleInput.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(checkDuplicates, 500);
        });
    }

    if (categorySelect) categorySelect.addEventListener('change', checkDuplicates);
    if (locationSelect) locationSelect.addEventListener('change', checkDuplicates);

    // 3. Bookmark / Save Item Toggle
    document.querySelectorAll('.ag-card-save-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const itemId = btn.dataset.itemId;
            if (!itemId) return;

            fetch(`/api/save-item/${itemId}`, {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    if (data.is_saved) {
                        btn.classList.add('active');
                        btn.title = "Saved to Bookmarks";
                        showToast("Saved to your bookmarks", "success");
                    } else {
                        btn.classList.remove('active');
                        btn.title = "Bookmark this item";
                        showToast("Removed from bookmarks", "info");
                    }
                }
            })
            .catch(err => {
                window.location.href = '/login';
            });
        });
    });

    // 4. Toast Notification System
    function showToast(message, type = 'info') {
        let container = document.getElementById('ag-toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'ag-toast-container';
            container.style.position = 'fixed';
            container.style.bottom = '24px';
            container.style.right = '24px';
            container.style.zIndex = '9999';
            container.style.display = 'flex';
            container.style.flexDirection = 'column';
            container.style.gap = '10px';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.className = `ag-alert ag-alert-${type}`;
        toast.style.margin = '0';
        toast.style.minWidth = '260px';
        toast.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.5)';
        toast.innerHTML = `<span>${escapeHtml(message)}</span>`;
        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(10px)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3200);
    }

    // Helper: Escape HTML
    function escapeHtml(text) {
        if (!text) return '';
        const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
        return text.toString().replace(/[&<>"']/g, m => map[m]);
    }
});
