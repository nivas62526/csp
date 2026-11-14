/**
 * ADCONNECT Main Application Scripts
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Notification & Unread Badge Polling
    initBadgePolling();

    // 2. Setup Video Preview Modals
    setupVideoModal();

    // 3. Setup Star Rating inputs if present
    setupStarRating();
});

function initBadgePolling() {
    function fetchCounts() {
        fetch('/api/unread-counts')
            .then(res => res.json())
            .then(data => {
                const notifBadge = document.getElementById('navbar-notif-badge');
                if (notifBadge) {
                    if (data.unread_notifications > 0) {
                        notifBadge.innerText = data.unread_notifications;
                        notifBadge.classList.remove('hidden');
                    } else {
                        notifBadge.classList.add('hidden');
                    }
                }

                const msgBadge = document.getElementById('navbar-msg-badge');
                if (msgBadge) {
                    if (data.unread_messages > 0) {
                        msgBadge.innerText = data.unread_messages;
                        msgBadge.classList.remove('hidden');
                    } else {
                        msgBadge.classList.add('hidden');
                    }
                }
            })
            .catch(() => {});
    }

    fetchCounts();
    setInterval(fetchCounts, 8000);
}

// Global Video Modal Handler
function playVideoModal(videoUrl, title, creatorName) {
    const modal = document.getElementById('global-video-modal');
    const player = document.getElementById('global-video-player');
    const videoSource = document.getElementById('global-video-source');
    const modalTitle = document.getElementById('global-video-title');
    const modalCreator = document.getElementById('global-video-creator');

    if (!modal || !player) return;

    if (modalTitle) modalTitle.innerText = title || "Advertisement Preview";
    if (modalCreator) modalCreator.innerText = creatorName ? `Created by ${creatorName}` : "";

    videoSource.src = videoUrl;
    player.load();
    player.play().catch(() => {});

    modal.classList.remove('hidden');
    modal.classList.add('flex');
}

function closeVideoModal() {
    const modal = document.getElementById('global-video-modal');
    const player = document.getElementById('global-video-player');
    if (!modal) return;

    if (player) {
        player.pause();
        player.currentTime = 0;
    }

    modal.classList.add('hidden');
    modal.classList.remove('flex');
}

function setupVideoModal() {
    // Close modal on backdrop click or Escape key
    const modal = document.getElementById('global-video-modal');
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeVideoModal();
            }
        });
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeVideoModal();
        }
    });
}

function setupStarRating() {
    const starContainers = document.querySelectorAll('.star-rating-input');
    starContainers.forEach(container => {
        const stars = container.querySelectorAll('.star-btn');
        const hiddenInput = container.querySelector('input[name="rating"]');

        stars.forEach((star, index) => {
            star.addEventListener('click', () => {
                const rating = index + 1;
                if (hiddenInput) hiddenInput.value = rating;

                stars.forEach((s, i) => {
                    if (i < rating) {
                        s.classList.add('text-amber-400', 'fill-amber-400');
                        s.classList.remove('text-slate-300');
                    } else {
                        s.classList.remove('text-amber-400', 'fill-amber-400');
                        s.classList.add('text-slate-300');
                    }
                });
            });
        });
    });
}
