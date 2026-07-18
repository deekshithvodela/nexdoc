// AnalyticsPanel Component for NexDoc

let typeChartInstance = null;
let specialtyChartInstance = null;

export const AnalyticsPanel = {
  render(filteredData) {
    // 1. Process data for Type Chart (Government vs Deemed vs Private)
    const typeCounts = {};
    const specialtyCounts = {};

    filteredData.forEach(row => {
      const type = row.college_type;
      const specialty = row.course;
      const seats = row.seats;

      typeCounts[type] = (typeCounts[type] || 0) + seats;
      specialtyCounts[specialty] = (specialtyCounts[specialty] || 0) + seats;
    });

    // Destroy existing chart instances to re-render cleanly
    if (typeChartInstance) {
      typeChartInstance.destroy();
    }
    if (specialtyChartInstance) {
      specialtyChartInstance.destroy();
    }

    // Chart.js global configurations for styling
    const chartFontColor = '#94a3b8';
    const chartGridColor = 'rgba(255, 255, 255, 0.05)';

    // Render Type Chart (Doughnut)
    const typeCanvas = document.getElementById('typeChart');
    if (typeCanvas) {
      const typeCtx = typeCanvas.getContext('2d');
      if (typeCtx) {
        const typeLabels = Object.keys(typeCounts);
        const typeValues = Object.values(typeCounts);
        const typeColors = typeLabels.map(t => {
          if (t === 'Government') return '#00d2ff';
          if (t === 'Deemed') return '#a155ff';
          return '#ff7e47'; // Private
        });

        typeChartInstance = new Chart(typeCtx, {
          type: 'doughnut',
          data: {
            labels: typeLabels,
            datasets: [{
              data: typeValues,
              backgroundColor: typeColors,
              borderWidth: 1,
              borderColor: '#131a26'
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'bottom',
                labels: {
                  color: chartFontColor,
                  font: { family: 'Outfit', size: 12, weight: 600 }
                }
              },
              tooltip: {
                backgroundColor: '#0d1527',
                titleColor: '#ffffff',
                bodyColor: '#cbd5e1',
                borderColor: 'rgba(255, 255, 255, 0.1)',
                borderWidth: 1
              }
            }
          }
        });
      }
    }

    // Render Specialty Chart (Horizontal Bar)
    const specCanvas = document.getElementById('specialtyChart');
    if (specCanvas) {
      const specCtx = specCanvas.getContext('2d');
      if (specCtx) {
        const sortedSpecs = Object.entries(specialtyCounts).sort((a, b) => b[1] - a[1]);
        const maxSpecialties = 15;
        const topSpecs = sortedSpecs.slice(0, maxSpecialties);
        if (sortedSpecs.length > maxSpecialties) {
          const otherSeats = sortedSpecs.slice(maxSpecialties).reduce((sum, s) => sum + s[1], 0);
          topSpecs.push(["Other Specialties", otherSeats]);
        }
        const specLabels = topSpecs.map(s => s[0]);
        const specValues = topSpecs.map(s => s[1]);

        specialtyChartInstance = new Chart(specCtx, {
          type: 'bar',
          data: {
            labels: specLabels,
            datasets: [{
              label: 'Total Seats Available',
              data: specValues,
              backgroundColor: 'rgba(0, 245, 160, 0.25)',
              borderColor: '#00f5a0',
              borderWidth: 1.5,
              borderRadius: 6
            }]
          },
          options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                display: false
              },
              tooltip: {
                backgroundColor: '#0d1527',
                titleColor: '#ffffff',
                bodyColor: '#cbd5e1',
                borderColor: 'rgba(255, 255, 255, 0.1)',
                borderWidth: 1
              }
            },
            scales: {
              x: {
                grid: { color: chartGridColor },
                ticks: { color: chartFontColor, font: { family: 'Inter' } }
              },
              y: {
                grid: { display: false },
                ticks: { color: chartFontColor, font: { family: 'Outfit', size: 11, weight: 500 } }
              }
            }
          }
        });
      }
    }
  }
};
