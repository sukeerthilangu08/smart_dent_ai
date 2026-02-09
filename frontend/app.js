// Smart Dent AI - Frontend JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Navigation functionality
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    
    hamburger.addEventListener('click', function() {
        navMenu.classList.toggle('active');
    });

    // Close menu when clicking on a link
    document.querySelectorAll('.nav-menu a').forEach(link => {
        link.addEventListener('click', () => {
            navMenu.classList.remove('active');
        });
    });

    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Camera and scanning functionality
    let stream = null;
    let capturedImage = null;
    const cameraFeed = document.getElementById('cameraFeed');
    const scanCanvas = document.getElementById('scanCanvas');
    const captureBtn = document.getElementById('captureBtn');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const resultsPanel = document.getElementById('results');
    const scanStatus = document.getElementById('scanStatus');
    const analysisResults = document.getElementById('analysisResults');
    const startScanBtn = document.getElementById('startScan');

    // Initialize camera when start scan is clicked
    startScanBtn.addEventListener('click', function() {
        document.getElementById('scan').scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
        setTimeout(initializeCamera, 500);
    });

    async function initializeCamera() {
        try {
            scanStatus.textContent = 'Accessing camera...';
            stream = await navigator.mediaDevices.getUserMedia({ 
                video: { 
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    facingMode: 'user'
                } 
            });
            cameraFeed.srcObject = stream;
            scanStatus.textContent = 'Position your mouth within the frame';
        } catch (error) {
            console.error('Error accessing camera:', error);
            scanStatus.textContent = 'Camera access denied. Please allow camera permissions.';
        }
    }

    // Capture image functionality
    captureBtn.addEventListener('click', function() {
        if (!stream) {
            initializeCamera();
            return;
        }

        const canvas = scanCanvas;
        const context = canvas.getContext('2d');
        
        canvas.width = cameraFeed.videoWidth;
        canvas.height = cameraFeed.videoHeight;
        
        context.drawImage(cameraFeed, 0, 0);
        capturedImage = canvas.toDataURL('image/jpeg');
        
        scanStatus.textContent = 'Image captured! Click Analyze to get results.';
        analyzeBtn.disabled = false;
        captureBtn.textContent = 'Retake';
    });

    // Analyze image functionality
    analyzeBtn.addEventListener('click', function() {
        if (!capturedImage) {
            alert('Please capture an image first!');
            return;
        }

        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<span class="loading"></span> Analyzing...';
        
        // Simulate AI analysis
        setTimeout(() => {
            performAnalysis();
        }, 3000);
    });

    function performAnalysis() {
        // Simulate AI analysis results
        const analysisData = generateMockAnalysis();
        
        displayResults(analysisData);
        resultsPanel.style.display = 'block';
        analyzeBtn.innerHTML = 'Analyze Again';
        analyzeBtn.disabled = false;
        
        // Update dashboard with new data
        updateDashboard(analysisData);
    }

    function generateMockAnalysis() {
        const conditions = [
            { name: 'Plaque Buildup', severity: 'moderate', confidence: 85 },
            { name: 'Gum Health', severity: 'good', confidence: 92 },
            { name: 'Tooth Alignment', severity: 'good', confidence: 78 },
            { name: 'Oral Hygiene', severity: 'needs_attention', confidence: 88 }
        ];

        const recommendations = [
            'Increase brushing frequency to 2x daily',
            'Focus on gum line cleaning',
            'Consider using an antimicrobial mouthwash',
            'Schedule a dental cleaning within 2 weeks'
        ];

        const overallScore = Math.floor(Math.random() * 30) + 70; // 70-100 range

        return {
            conditions,
            recommendations,
            overallScore,
            timestamp: new Date()
        };
    }

    function displayResults(data) {
        let resultsHTML = '<div class="analysis-summary">';
        resultsHTML += `<h4>Overall Oral Health Score: ${data.overallScore}%</h4>`;
        resultsHTML += '</div>';

        resultsHTML += '<div class="conditions-analysis">';
        resultsHTML += '<h4>Detected Conditions:</h4>';
        
        data.conditions.forEach(condition => {
            const severityClass = getSeverityClass(condition.severity);
            resultsHTML += `
                <div class="result-item ${severityClass}">
                    <strong>${condition.name}</strong>
                    <span style="float: right;">${condition.confidence}% confidence</span>
                    <br>
                    <small>Status: ${formatSeverity(condition.severity)}</small>
                </div>
            `;
        });
        resultsHTML += '</div>';

        resultsHTML += '<div class="recommendations">';
        resultsHTML += '<h4>Recommendations:</h4>';
        resultsHTML += '<ul>';
        data.recommendations.forEach(rec => {
            resultsHTML += `<li>${rec}</li>`;
        });
        resultsHTML += '</ul>';
        resultsHTML += '</div>';

        analysisResults.innerHTML = resultsHTML;
    }

    function getSeverityClass(severity) {
        switch(severity) {
            case 'good': return 'result-good';
            case 'moderate': 
            case 'needs_attention': return 'result-warning';
            case 'severe': return 'result-danger';
            default: return 'result-good';
        }
    }

    function formatSeverity(severity) {
        switch(severity) {
            case 'good': return 'Good';
            case 'moderate': return 'Moderate';
            case 'needs_attention': return 'Needs Attention';
            case 'severe': return 'Severe';
            default: return 'Unknown';
        }
    }

    function updateDashboard(analysisData) {
        // Update health score
        const healthScore = document.getElementById('healthScore');
        if (healthScore) {
            animateValue(healthScore, parseInt(healthScore.textContent), analysisData.overallScore, 1000);
        }

        // Update scan history
        const scanHistory = document.getElementById('scanHistory');
        if (scanHistory) {
            const newScan = document.createElement('div');
            newScan.className = 'scan-item';
            
            const status = analysisData.overallScore >= 85 ? 'good' : 
                          analysisData.overallScore >= 70 ? 'warning' : 'danger';
            const statusText = analysisData.overallScore >= 85 ? 'Excellent' : 
                              analysisData.overallScore >= 70 ? 'Good' : 'Needs Attention';
            
            newScan.innerHTML = `
                <span class="scan-date">Just Now</span>
                <span class="scan-result ${status}">${statusText}</span>
            `;
            
            scanHistory.insertBefore(newScan, scanHistory.firstChild);
            
            // Remove old entries if more than 5
            while (scanHistory.children.length > 5) {
                scanHistory.removeChild(scanHistory.lastChild);
            }
        }

        // Update daily tips based on analysis
        updateDailyTips(analysisData);
    }

    function updateDailyTips(analysisData) {
        const dailyTips = document.getElementById('dailyTips');
        if (!dailyTips) return;

        const tips = [];
        
        analysisData.conditions.forEach(condition => {
            if (condition.name === 'Plaque Buildup' && condition.severity !== 'good') {
                tips.push('⚠ Focus on thorough plaque removal');
            }
            if (condition.name === 'Gum Health' && condition.severity !== 'good') {
                tips.push('⚠ Gentle gum massage while brushing');
            }
            if (condition.name === 'Oral Hygiene' && condition.severity !== 'good') {
                tips.push('⚠ Increase brushing frequency');
            }
        });

        // Add some general tips
        tips.push('✓ Brush for 2 minutes minimum');
        tips.push('✓ Use fluoride toothpaste');
        tips.push('✓ Floss daily for optimal health');

        dailyTips.innerHTML = tips.slice(0, 5).map(tip => `<li>${tip}</li>`).join('');
    }

    function animateValue(element, start, end, duration) {
        const startTime = Date.now();
        const difference = end - start;
        
        function updateValue() {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const current = Math.floor(start + (difference * progress));
            
            element.textContent = current;
            
            if (progress < 1) {
                requestAnimationFrame(updateValue);
            }
        }
        
        updateValue();
    }

    // Contact form functionality
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(contactForm);
            const submitBtn = contactForm.querySelector('button[type="submit"]');
            
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="loading"></span> Sending...';
            
            // Simulate form submission
            setTimeout(() => {
                alert('Thank you for your interest! We will contact you soon.');
                contactForm.reset();
                submitBtn.disabled = false;
                submitBtn.textContent = 'Send Message';
            }, 2000);
        });
    }

    // Intersection Observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe elements for animation
    document.querySelectorAll('.feature-card, .dashboard-card, .stat').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });

    // Auto-update dashboard every 30 seconds (simulate real-time data)
    setInterval(() => {
        if (document.visibilityState === 'visible') {
            updateRandomMetrics();
        }
    }, 30000);

    function updateRandomMetrics() {
        // Simulate small changes in health metrics
        const healthScore = document.getElementById('healthScore');
        if (healthScore) {
            const currentScore = parseInt(healthScore.textContent);
            const newScore = Math.max(65, Math.min(100, currentScore + Math.floor(Math.random() * 6) - 3));
            if (newScore !== currentScore) {
                animateValue(healthScore, currentScore, newScore, 1000);
            }
        }
    }

    // Initialize dashboard with sample data
    setTimeout(() => {
        updateDashboard({
            overallScore: 85,
            conditions: [
                { name: 'Overall Health', severity: 'good', confidence: 90 }
            ],
            recommendations: [
                'Maintain current oral hygiene routine',
                'Regular dental checkups recommended'
            ]
        });
    }, 1000);

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey || e.metaKey) {
            switch(e.key) {
                case 's':
                    e.preventDefault();
                    document.getElementById('scan').scrollIntoView({ behavior: 'smooth' });
                    break;
                case 'h':
                    e.preventDefault();
                    document.getElementById('home').scrollIntoView({ behavior: 'smooth' });
                    break;
            }
        }
    });

    // Add tooltips for better UX
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });

    function showTooltip(e) {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = e.target.dataset.tooltip;
        document.body.appendChild(tooltip);
        
        const rect = e.target.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
    }

    function hideTooltip() {
        const tooltip = document.querySelector('.tooltip');
        if (tooltip) {
            tooltip.remove();
        }
    }

    // Performance monitoring
    if ('performance' in window) {
        window.addEventListener('load', () => {
            setTimeout(() => {
                const perfData = performance.getEntriesByType('navigation')[0];
                console.log('Page load time:', perfData.loadEventEnd - perfData.fetchStart, 'ms');
            }, 0);
        });
    }
});

// Service Worker registration for offline capabilities
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}