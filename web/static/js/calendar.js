document.addEventListener('DOMContentLoaded', function () {
  const calendarEl = document.getElementById('calendar');
  const modal = new bootstrap.Modal(document.getElementById('eventModal'));

  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'dayGridMonth',
    locale: 'ko',
    height: 'auto',
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek',
    },
    events: function (fetchInfo, successCallback, failureCallback) {
      const start = fetchInfo.startStr.slice(0, 10);
      const end = fetchInfo.endStr.slice(0, 10);
      fetch(`/api/calendar/events?start=${start}&end=${end}`)
        .then(r => r.json())
        .then(data => successCallback(data))
        .catch(err => failureCallback(err));
    },
    eventClick: function (info) {
      const p = info.event.extendedProps;
      const statusBadge = {
        '예정': 'primary', '진행중': 'warning', '완료': 'success', '취소': 'secondary'
      };
      const color = statusBadge[p.status] || 'secondary';

      document.getElementById('modal-title').textContent = info.event.title;
      document.getElementById('modal-body').innerHTML = `
        <dl class="row mb-0">
          <dt class="col-sm-4 text-muted">상태</dt>
          <dd class="col-sm-8"><span class="badge bg-${color}">${p.status}</span></dd>
          <dt class="col-sm-4 text-muted">시작</dt>
          <dd class="col-sm-8">${info.event.startStr?.slice(0, 16).replace('T', ' ') || ''}</dd>
          <dt class="col-sm-4 text-muted">지역</dt>
          <dd class="col-sm-8">${p.region}</dd>
          <dt class="col-sm-4 text-muted">버스</dt>
          <dd class="col-sm-8">${p.bus_number}</dd>
          <dt class="col-sm-4 text-muted">등록/수용</dt>
          <dd class="col-sm-8">${p.registered}/${p.capacity}명</dd>
          <dt class="col-sm-4 text-muted">서비스</dt>
          <dd class="col-sm-8">${(p.services || []).join(', ') || '—'}</dd>
        </dl>`;
      document.getElementById('modal-detail-link').href = `/schedules/${info.event.id}`;
      modal.show();
    },
  });

  calendar.render();
});
