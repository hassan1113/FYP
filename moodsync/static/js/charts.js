// Enhanced Charts.js - Handles chart creation and data visualization for MoodSync

document.addEventListener('DOMContentLoaded', function() {
    console.log('MoodSync enhanced charts initialized');
    
    // Initialize all charts with error handling
    try {
        initMoodTrendsChart();
        initEmotionDistributionChart();
        initMoodIntensityChart();
        initSuggestionEffectivenessChart();
        initStatsCounters();
    } catch (error) {
        console.error('Error initializing charts:', error);
    }
});

// Initialize stats counters with animations
function initStatsCounters() {
    const statElements = document.querySelectorAll('.stat-number');
    
    statElements.forEach(element => {
        const target = parseInt(element.textContent);
        const duration = 2000; // Animation duration in ms
        const steps = 60; // Number of steps
        const stepValue = target / steps;
        let current = 0;
        
        const counter = setInterval(() => {
            current += stepValue;
            if (current >= target) {
                element.textContent = target;
                clearInterval(counter);
                
                // Add animation complete class
                element.classList.add('count-complete');
            } else {
                element.textContent = Math.round(current);
            }
        }, duration / steps);
    });
    
    console.log(`Initialized ${statElements.length} animated counters`);
}

// Enhanced Mood Trends Chart with animations
function initMoodTrendsChart() {
    const chartContainer = document.getElementById('mood-trends-chart');
    if (!chartContainer) return;
    
    // Get chart data from the data attribute
    let chartData;
    try {
        chartData = JSON.parse(chartContainer.dataset.chartData || '{}');
    } catch (e) {
        console.error('Error parsing mood trends chart data:', e);
        showChartError(chartContainer, 'Failed to load mood trends data');
        return;
    }
    
    const dates = chartData.dates || [];
    const emotions = chartData.emotions || [];
    const intensities = chartData.intensities || [];
    
    // Create the chart with enhanced options
    const ctx = chartContainer.getContext('2d');
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Mood Intensity',
                data: intensities,
                backgroundColor: 'rgba(108, 99, 255, 0.1)',
                borderColor: 'rgba(108, 99, 255, 1)',
                pointBackgroundColor: function(context) {
                    const emotion = emotions[context.dataIndex];
                    return getEmotionColor(emotion);
                },
                pointBorderColor: function(context) {
                    const emotion = emotions[context.dataIndex];
                    return getEmotionColor(emotion);
                },
                pointRadius: 6,
                pointHoverRadius: 8,
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointHoverBackgroundColor: function(context) {
                    const emotion = emotions[context.dataIndex];
                    return getEmotionColor(emotion);
                },
                pointHoverBorderColor: '#fff',
                pointHoverBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 2000,
                easing: 'easeOutQuart'
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 10,
                    title: {
                        display: true,
                        text: 'Intensity',
                        font: {
                            weight: 'bold'
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Date',
                        font: {
                            weight: 'bold'
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                }
            },
            plugins: {
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 13
                    },
                    callbacks: {
                        label: function(context) {
                            const dataIndex = context.dataIndex;
                            return [
                                `Emotion: ${emotions[dataIndex]}`,
                                `Intensity: ${intensities[dataIndex]}`
                            ];
                        },
                        title: function(context) {
                            return `Date: ${context[0].label}`;
                        }
                    }
                },
                legend: {
                    display: false
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
    
    // Add chart instance to window for potential external access
    window.moodTrendsChart = chart;
    
    console.log('Mood trends chart initialized with animation');
}

// Enhanced Emotion Distribution Chart
function initEmotionDistributionChart() {
    const chartContainer = document.getElementById('emotion-distribution-chart');
    if (!chartContainer) return;
    
    // Get chart data from the data attribute
    let chartData;
    try {
        chartData = JSON.parse(chartContainer.dataset.chartData || '{}');
    } catch (e) {
        console.error('Error parsing emotion distribution chart data:', e);
        showChartError(chartContainer, 'Failed to load emotion distribution data');
        return;
    }
    
    const emotions = chartData.emotions || [];
    const counts = chartData.counts || [];
    
    // Create the chart with enhanced options
    const ctx = chartContainer.getContext('2d');
    const chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: emotions,
            datasets: [{
                data: counts,
                backgroundColor: emotions.map(emotion => getEmotionColor(emotion)),
                borderColor: emotions.map(emotion => getEmotionColor(emotion, 1)),
                borderWidth: 2,
                hoverBackgroundColor: emotions.map(emotion => getEmotionColor(emotion, 0.8)),
                hoverBorderColor: '#fff',
                hoverBorderWidth: 3,
                borderRadius: 6,
                hoverOffset: 15
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                animateScale: true,
                animateRotate: true,
                duration: 2000,
                easing: 'easeOutQuart'
            },
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        padding: 20,
                        usePointStyle: true,
                        pointStyle: 'circle',
                        font: {
                            size: 12,
                            weight: '500'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 15,
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            },
            cutout: '65%'
        }
    });
    
    // Add chart instance to window for potential external access
    window.emotionDistributionChart = chart;
    
    console.log('Emotion distribution chart initialized with animation');
}

// Enhanced Mood Intensity by Context Chart
function initMoodIntensityChart() {
    const chartContainer = document.getElementById('mood-intensity-chart');
    if (!chartContainer) return;
    
    // Get chart data from the data attribute
    let chartData;
    try {
        chartData = JSON.parse(chartContainer.dataset.chartData || '{}');
    } catch (e) {
        console.error('Error parsing mood intensity chart data:', e);
        showChartError(chartContainer, 'Failed to load mood intensity data');
        return;
    }
    
    const contexts = chartData.contexts || [];
    const datasets = chartData.datasets || [];
    
    // Create the chart with enhanced options
    const ctx = chartContainer.getContext('2d');
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: contexts,
            datasets: datasets.map(dataset => ({
                label: dataset.emotion,
                data: dataset.intensities,
                backgroundColor: getEmotionColor(dataset.emotion, 0.7),
                borderColor: getEmotionColor(dataset.emotion),
                borderWidth: 1,
                borderRadius: 6,
                hoverBackgroundColor: getEmotionColor(dataset.emotion, 0.9),
                hoverBorderColor: getEmotionColor(dataset.emotion),
                hoverBorderWidth: 2
            }))
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 2000,
                easing: 'easeOutQuart'
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 10,
                    title: {
                        display: true,
                        text: 'Average Intensity',
                        font: {
                            weight: 'bold'
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Context',
                        font: {
                            weight: 'bold'
                        }
                    },
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        pointStyle: 'circle',
                        padding: 20,
                        font: {
                            weight: '500'
                        }
                    }
                }
            }
        }
    });
    
    // Add chart instance to window for potential external access
    window.moodIntensityChart = chart;
    
    console.log('Mood intensity chart initialized with animation');
}

// Enhanced Suggestion Effectiveness Chart
function initSuggestionEffectivenessChart() {
    const chartContainer = document.getElementById('suggestion-effectiveness-chart');
    if (!chartContainer) return;
    
    // Get chart data from the data attribute
    let chartData;
    try {
        chartData = JSON.parse(chartContainer.dataset.chartData || '{}');
    } catch (e) {
        console.error('Error parsing suggestion effectiveness chart data:', e);
        showChartError(chartContainer, 'Failed to load suggestion effectiveness data');
        return;
    }
    
    const suggestionTypes = chartData.types || [];
    const ratings = chartData.ratings || [];
    
    // Create the chart with enhanced options
    const ctx = chartContainer.getContext('2d');
    const chart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: suggestionTypes,
            datasets: [{
                label: 'Average Rating',
                data: ratings,
                backgroundColor: 'rgba(108, 99, 255, 0.2)',
                borderColor: 'rgba(108, 99, 255, 1)',
                pointBackgroundColor: 'rgba(108, 99, 255, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(108, 99, 255, 1)',
                borderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 2000,
                easing: 'easeOutQuart'
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 5,
                    ticks: {
                        stepSize: 1,
                        backdropColor: 'transparent'
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    angleLines: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    pointLabels: {
                        font: {
                            weight: '500'
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        font: {
                            weight: '500'
                        }
                    }
                }
            }
        }
    });
    
    // Add chart instance to window for potential external access
    window.suggestionEffectivenessChart = chart;
    
    console.log('Suggestion effectiveness chart initialized with animation');
}

// Enhanced helper function to get color for each emotion
function getEmotionColor(emotion, alpha = 1) {
    const colors = {
        'Happy': `rgba(28, 200, 138, ${alpha})`,
        'Sad': `rgba(78, 115, 223, ${alpha})`,
        'Angry': `rgba(231, 74, 59, ${alpha})`,
        'Neutral': `rgba(133, 135, 150, ${alpha})`,
        'Fear': `rgba(246, 194, 62, ${alpha})`,
        'Disgust': `rgba(156, 39, 176, ${alpha})`,
        'Surprise': `rgba(54, 185, 204, ${alpha})`,
        'Calm': `rgba(76, 175, 80, ${alpha})`,
        'Energetic': `rgba(255, 152, 0, ${alpha})`,
        'Tired': `rgba(121, 85, 72, ${alpha})`,
        'Anxious': `rgba(233, 30, 99, ${alpha})`
    };
    
    return colors[emotion] || `rgba(133, 135, 150, ${alpha})`;
}

// Function to show error message in chart container
function showChartError(container, message) {
    container.innerHTML = `
        <div class="chart-error">
            <i class="bi bi-exclamation-triangle"></i>
            <p>${message}</p>
        </div>
    `;
    
    console.error(`Chart error: ${message}`);
}

// Export functions for use in other modules
window.MoodSyncCharts = {
    initMoodTrendsChart,
    initEmotionDistributionChart,
    initMoodIntensityChart,
    initSuggestionEffectivenessChart,
    getEmotionColor
};