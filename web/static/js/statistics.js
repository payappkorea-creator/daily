document.addEventListener('DOMContentLoaded', function () {
  const statsEl = document.getElementById('stats-data');
  if (!statsEl) return;
  const stats = JSON.parse(statsEl.dataset.stats);

  // 1. 상태별 도넛 차트
  const statusCtx = document.getElementById('statusChart').getContext('2d');
  const statusLabels = Object.keys(stats.status_breakdown);
  const statusColors = { '예정': '#0d6efd', '진행중': '#fd7e14', '완료': '#198754', '취소': '#6c757d' };
  new Chart(statusCtx, {
    type: 'doughnut',
    data: {
      labels: statusLabels,
      datasets: [{
        data: Object.values(stats.status_breakdown),
        backgroundColor: statusLabels.map(l => statusColors[l] || '#adb5bd'),
      }],
    },
    options: {
      plugins: { legend: { position: 'bottom' } },
    },
  });

  // 2. 이용률 바 차트
  const utilCtx = document.getElementById('utilizationChart').getContext('2d');
  new Chart(utilCtx, {
    type: 'bar',
    data: {
      labels: ['전체 인원 현황'],
      datasets: [
        { label: '수용 인원', data: [stats.total_capacity], backgroundColor: '#dee2e6' },
        { label: '등록 인원', data: [stats.total_registered], backgroundColor: '#0d6efd' },
      ],
    },
    options: {
      plugins: {
        title: { display: true, text: `이용률: ${stats.utilization_rate}` },
        legend: { position: 'bottom' },
      },
      scales: { y: { beginAtZero: true } },
    },
  });

  // 3. 지역별 수평 바 차트
  const regionCtx = document.getElementById('regionChart').getContext('2d');
  const sorted = Object.entries(stats.region_breakdown).sort((a, b) => b[1] - a[1]);
  new Chart(regionCtx, {
    type: 'bar',
    data: {
      labels: sorted.map(r => r[0]),
      datasets: [{
        label: '일정 수',
        data: sorted.map(r => r[1]),
        backgroundColor: '#0d6efd',
      }],
    },
    options: {
      indexAxis: 'y',
      plugins: { legend: { display: false } },
      scales: { x: { beginAtZero: true, ticks: { stepSize: 1 } } },
    },
  });
});
