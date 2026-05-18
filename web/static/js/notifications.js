const POLL_INTERVAL = 5 * 60 * 1000;
const STORAGE_KEY = 'hapbusSeen';

function getSeenIds() {
  try { return new Set(JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')); }
  catch (e) { return new Set(); }
}

function saveSeenIds(ids) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify([...ids]));
}

async function checkNotifications() {
  try {
    const res = await fetch('/api/notifications/upcoming?days=7');
    if (!res.ok) return;
    const data = await res.json();

    const badge = document.getElementById('notif-badge');
    if (badge) {
      badge.textContent = data.count;
      badge.style.display = data.count > 0 ? 'inline' : 'none';
    }

    const seenIds = getSeenIds();
    const newItems = data.schedules.filter(s => !seenIds.has(s.id));
    newItems.forEach(s => {
      if (typeof showToast === 'function') {
        showToast(
          `[${s.region}] ${s.location}`,
          `${s.date} ${s.time} — ${s.status}`,
          'primary'
        );
      }
    });

    data.schedules.forEach(s => seenIds.add(s.id));
    saveSeenIds(seenIds);
  } catch (e) {
    // 네트워크 오류 무시
  }
}

document.addEventListener('DOMContentLoaded', function () {
  checkNotifications();
  setInterval(checkNotifications, POLL_INTERVAL);
});
