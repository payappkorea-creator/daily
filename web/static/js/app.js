function showToast(title, body, type) {
  type = type || 'primary';
  const container = document.getElementById('toast-container');
  const el = document.createElement('div');
  el.className = `toast align-items-center text-bg-${type} border-0`;
  el.setAttribute('role', 'alert');
  el.innerHTML = `
    <div class="d-flex">
      <div class="toast-body"><strong>${title}</strong><br>${body}</div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
    </div>`;
  container.appendChild(el);
  new bootstrap.Toast(el, { delay: 5000 }).show();
  el.addEventListener('hidden.bs.toast', () => el.remove());
}
