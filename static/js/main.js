/**
 * Main JavaScript file for Student Record Management System
 * Provides interactive functionality, form validation, and user experience enhancements
 */

// Global configuration
const config = {
    autoRefreshInterval: 30000, // 30 seconds
    animationDuration: 300,
    debounceDelay: 500,
    maxRetries: 3
};

// Utility functions
const utils = {
    /**
     * Debounce function to limit function calls
     */
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * Format grade with appropriate styling
     */
    formatGrade: function(grade) {
        const gradeNum = parseFloat(grade);
        let badgeClass = 'bg-danger';
        
        if (gradeNum >= 90) badgeClass = 'bg-success';
        else if (gradeNum >= 80) badgeClass = 'bg-info';
        else if (gradeNum >= 70) badgeClass = 'bg-warning';
        
        return `<span class="badge ${badgeClass}">${gradeNum.toFixed(1)}</span>`;
    },

    /**
     * Calculate average grade
     */
    calculateAverage: function(grades) {
        if (!grades || grades.length === 0) return 0;
        const sum = grades.reduce((acc, grade) => acc + parseFloat(grade), 0);
        return (sum / grades.length).toFixed(1);
    },

    /**
     * Show loading state
     */
    showLoading: function(element) {
        if (element) {
            element.classList.add('loading');
            element.style.pointerEvents = 'none';
        }
    },

    /**
     * Hide loading state
     */
    hideLoading: function(element) {
        if (element) {
            element.classList.remove('loading');
            element.style.pointerEvents = 'auto';
        }
    },

    /**
     * Show toast notification
     */
    showToast: function(message, type = 'info', duration = 3000) {
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${this.getIconForType(type)} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        // Add to toast container or create one
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }

        toastContainer.appendChild(toast);

        // Initialize and show toast
        const bsToast = new bootstrap.Toast(toast, { delay: duration });
        bsToast.show();

        // Remove toast after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    },

    /**
     * Get icon for toast type
     */
    getIconForType: function(type) {
        const icons = {
            'success': 'check-circle',
            'danger': 'exclamation-triangle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle',
            'primary': 'info-circle'
        };
        return icons[type] || 'info-circle';
    },

    /**
     * Validate email format
     */
    isValidEmail: function(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },

    /**
     * Validate roll number format
     */
    isValidRollNumber: function(rollNo) {
        return rollNo && rollNo.trim().length > 0;
    },

    /**
     * Parse courses from string
     */
    parseCourses: function(coursesStr) {
        return coursesStr.split(',').map(course => course.trim()).filter(course => course.length > 0);
    },

    /**
     * Parse grades from string
     */
    parseGrades: function(gradesStr) {
        return gradesStr.split(',').map(grade => {
            const num = parseFloat(grade.trim());
            return isNaN(num) ? null : num;
        }).filter(grade => grade !== null);
    }
};

// Form validation module
const formValidation = {
    /**
     * Initialize form validation
     */
    init: function() {
        const forms = document.querySelectorAll('.needs-validation');
        forms.forEach(form => {
            form.addEventListener('submit', this.handleSubmit.bind(this));
            
            // Add real-time validation
            const inputs = form.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                input.addEventListener('blur', this.validateField.bind(this));
                input.addEventListener('input', utils.debounce(this.validateField.bind(this), config.debounceDelay));
            });
        });

        // Initialize custom validators
        this.initCustomValidators();
    },

    /**
     * Handle form submission
     */
    handleSubmit: function(event) {
        const form = event.target;
        
        if (!form.checkValidity()) {
            event.preventDefault();
            event.stopPropagation();
            
            // Focus on first invalid field
            const firstInvalid = form.querySelector(':invalid');
            if (firstInvalid) {
                firstInvalid.focus();
                this.showFieldError(firstInvalid, 'Please correct this field');
            }
        }
        
        form.classList.add('was-validated');
    },

    /**
     * Validate individual field
     */
    validateField: function(event) {
        const field = event.target;
        const value = field.value.trim();
        
        // Clear previous errors
        this.clearFieldError(field);
        
        // Check required fields
        if (field.hasAttribute('required') && !value) {
            this.showFieldError(field, 'This field is required');
            return false;
        }

        // Email validation
        if (field.type === 'email' && value && !utils.isValidEmail(value)) {
            this.showFieldError(field, 'Please enter a valid email address');
            return false;
        }

        // Custom validation for courses and grades
        if (field.name === 'courses' && value) {
            const courses = utils.parseCourses(value);
            if (courses.length === 0) {
                this.showFieldError(field, 'Please enter at least one course');
                return false;
            }
        }

        if (field.name === 'grades' && value) {
            const grades = utils.parseGrades(value);
            if (grades.length === 0) {
                this.showFieldError(field, 'Please enter valid numeric grades');
                return false;
            }
        }

        // Validate courses and grades match
        if (field.name === 'courses' || field.name === 'grades') {
            this.validateCoursesGradesMatch();
        }

        field.classList.add('is-valid');
        return true;
    },

    /**
     * Validate that courses and grades match
     */
    validateCoursesGradesMatch: function() {
        const coursesField = document.querySelector('input[name="courses"]');
        const gradesField = document.querySelector('input[name="grades"]');
        
        if (!coursesField || !gradesField) return;

        const coursesValue = coursesField.value.trim();
        const gradesValue = gradesField.value.trim();

        if (coursesValue && gradesValue) {
            const courses = utils.parseCourses(coursesValue);
            const grades = utils.parseGrades(gradesValue);

            if (courses.length !== grades.length) {
                this.showFieldError(coursesField, 'Number of courses must match number of grades');
                this.showFieldError(gradesField, 'Number of grades must match number of courses');
                return false;
            } else {
                this.clearFieldError(coursesField);
                this.clearFieldError(gradesField);
                return true;
            }
        }
    },

    /**
     * Show field error
     */
    showFieldError: function(field, message) {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
        
        // Remove existing error message
        const existingError = field.parentNode.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.textContent = message;
        } else {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            errorDiv.textContent = message;
            field.parentNode.appendChild(errorDiv);
        }
    },

    /**
     * Clear field error
     */
    clearFieldError: function(field) {
        field.classList.remove('is-invalid');
        const errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (errorDiv && !field.hasAttribute('data-keep-error')) {
            errorDiv.remove();
        }
    },

    /**
     * Initialize custom validators
     */
    initCustomValidators: function() {
        // Roll number uniqueness validation would go here
        // Grade range validation (0-100)
        const gradeInputs = document.querySelectorAll('input[name="grades"]');
        gradeInputs.forEach(input => {
            input.addEventListener('input', function() {
                const grades = utils.parseGrades(this.value);
                const invalidGrades = grades.filter(grade => grade < 0 || grade > 100);
                
                if (invalidGrades.length > 0) {
                    formValidation.showFieldError(this, 'Grades must be between 0 and 100');
                }
            });
        });
    }
};

// Search and filter functionality
const searchFilter = {
    /**
     * Initialize search functionality
     */
    init: function() {
        const searchForm = document.querySelector('form[action*="search"]');
        if (searchForm) {
            const searchInput = searchForm.querySelector('input[name="search"]');
            if (searchInput) {
                searchInput.addEventListener('input', utils.debounce(this.handleSearch.bind(this), config.debounceDelay));
            }
        }

        // Initialize table filtering
        this.initTableFiltering();
    },

    /**
     * Handle search input
     */
    handleSearch: function(event) {
        const searchTerm = event.target.value.trim().toLowerCase();
        
        if (searchTerm.length >= 2) {
            this.filterTable(searchTerm);
        } else {
            this.clearTableFilter();
        }
    },

    /**
     * Filter table rows based on search term
     */
    filterTable: function(searchTerm) {
        const tableRows = document.querySelectorAll('table tbody tr');
        let visibleCount = 0;

        tableRows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const isVisible = text.includes(searchTerm);
            
            row.style.display = isVisible ? '' : 'none';
            if (isVisible) visibleCount++;
        });

        // Update results count
        this.updateResultsCount(visibleCount, tableRows.length);
    },

    /**
     * Clear table filter
     */
    clearTableFilter: function() {
        const tableRows = document.querySelectorAll('table tbody tr');
        tableRows.forEach(row => {
            row.style.display = '';
        });
        this.updateResultsCount(tableRows.length, tableRows.length);
    },

    /**
     * Update results count display
     */
    updateResultsCount: function(visible, total) {
        let countElement = document.querySelector('.results-count');
        if (!countElement) {
            countElement = document.createElement('div');
            countElement.className = 'results-count text-muted mb-2';
            const table = document.querySelector('table');
            if (table) {
                table.parentNode.insertBefore(countElement, table);
            }
        }
        
        if (visible < total) {
            countElement.textContent = `Showing ${visible} of ${total} students`;
        } else {
            countElement.textContent = '';
        }
    },

    /**
     * Initialize table filtering controls
     */
    initTableFiltering: function() {
        // Add filter controls if needed
        const tables = document.querySelectorAll('table');
        tables.forEach(table => {
            this.addTableControls(table);
        });
    },

    /**
     * Add controls to table
     */
    addTableControls: function(table) {
        // Add sort functionality to table headers
        const headers = table.querySelectorAll('th');
        headers.forEach((header, index) => {
            if (header.textContent.trim() && !header.querySelector('.sort-icon')) {
                header.style.cursor = 'pointer';
                header.classList.add('sortable');
                
                const sortIcon = document.createElement('i');
                sortIcon.className = 'fas fa-sort sort-icon ms-1';
                header.appendChild(sortIcon);
                
                header.addEventListener('click', () => this.sortTable(table, index));
            }
        });
    },

    /**
     * Sort table by column
     */
    sortTable: function(table, columnIndex) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const header = table.querySelectorAll('th')[columnIndex];
        const sortIcon = header.querySelector('.sort-icon');
        
        // Determine sort direction
        const isAscending = !header.classList.contains('sort-asc');
        
        // Clear all sort classes
        table.querySelectorAll('th').forEach(th => {
            th.classList.remove('sort-asc', 'sort-desc');
            const icon = th.querySelector('.sort-icon');
            if (icon) icon.className = 'fas fa-sort sort-icon ms-1';
        });
        
        // Sort rows
        rows.sort((a, b) => {
            const aValue = this.getCellValue(a, columnIndex);
            const bValue = this.getCellValue(b, columnIndex);
            
            const comparison = aValue.localeCompare(bValue, undefined, { numeric: true });
            return isAscending ? comparison : -comparison;
        });
        
        // Update UI
        header.classList.add(isAscending ? 'sort-asc' : 'sort-desc');
        sortIcon.className = `fas fa-sort-${isAscending ? 'up' : 'down'} sort-icon ms-1`;
        
        // Reorder rows
        rows.forEach(row => tbody.appendChild(row));
    },

    /**
     * Get cell value for sorting
     */
    getCellValue: function(row, columnIndex) {
        const cell = row.cells[columnIndex];
        const badge = cell.querySelector('.badge');
        
        if (badge) {
            const text = badge.textContent.trim();
            const number = parseFloat(text);
            return isNaN(number) ? text : number.toString().padStart(10, '0');
        }
        
        return cell.textContent.trim();
    }
};

// Dashboard functionality
const dashboard = {
    /**
     * Initialize dashboard
     */
    init: function() {
        this.initAutoRefresh();
        this.initStatistics();
        this.initInteractiveElements();
    },

    /**
     * Initialize auto-refresh for dashboard
     */
    initAutoRefresh: function() {
        if (window.location.pathname === '/' || window.location.pathname.includes('dashboard')) {
            setInterval(() => {
                if (!document.hidden && !document.querySelector('.modal.show')) {
                    // Only refresh if not searching
                    if (!window.location.search.includes('search=')) {
                        this.refreshStatistics();
                    }
                }
            }, config.autoRefreshInterval);
        }
    },

    /**
     * Refresh statistics
     */
    refreshStatistics: function() {
        const statsCards = document.querySelectorAll('.card .card-body h4, .card .card-body h3');
        statsCards.forEach(card => {
            utils.showLoading(card.closest('.card'));
        });

        // Simulate refresh (in real app, this would be an AJAX call)
        setTimeout(() => {
            statsCards.forEach(card => {
                utils.hideLoading(card.closest('.card'));
            });
        }, 1000);
    },

    /**
     * Initialize statistics animations
     */
    initStatistics: function() {
        const statNumbers = document.querySelectorAll('.card-body h3, .card-body h4');
        
        // Animate numbers on page load
        statNumbers.forEach(element => {
            const finalValue = parseFloat(element.textContent) || 0;
            this.animateNumber(element, 0, finalValue, 1500);
        });
    },

    /**
     * Animate number counting
     */
    animateNumber: function(element, start, end, duration) {
        const startTime = performance.now();
        const isFloat = end % 1 !== 0;
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const current = start + (end - start) * this.easeOutCubic(progress);
            element.textContent = isFloat ? current.toFixed(1) : Math.floor(current);
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    },

    /**
     * Easing function for animations
     */
    easeOutCubic: function(t) {
        return 1 - Math.pow(1 - t, 3);
    },

    /**
     * Initialize interactive elements
     */
    initInteractiveElements: function() {
        // Add hover effects to cards
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-2px)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
            });
        });

        // Initialize tooltips
        this.initTooltips();
    },

    /**
     * Initialize tooltips
     */
    initTooltips: function() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }
};

// Query interface functionality
const queryInterface = {
    /**
     * Initialize query interface
     */
    init: function() {
        if (window.location.pathname.includes('/query')) {
            this.initQueryEditor();
            this.initSampleQueries();
            this.initQueryHistory();
        }
    },

    /**
     * Initialize query editor
     */
    initQueryEditor: function() {
        const queryTextarea = document.querySelector('textarea[name="query"]');
        if (queryTextarea) {
            // Add syntax highlighting on keyup
            queryTextarea.addEventListener('keyup', utils.debounce(this.highlightSyntax.bind(this), 300));
            
            // Add auto-completion
            queryTextarea.addEventListener('keydown', this.handleKeyDown.bind(this));
            
            // Add line numbers (simple implementation)
            this.addLineNumbers(queryTextarea);
        }
    },

    /**
     * Simple syntax highlighting
     */
    highlightSyntax: function(event) {
        const textarea = event.target;
        const value = textarea.value;
        
        // Basic keyword highlighting by changing font weight
        const keywords = ['SELECT', 'FROM', 'WHERE', 'ORDER BY', 'GROUP BY', 'LIMIT', 'AND', 'OR', 'LIKE'];
        let highlightedValue = value;
        
        keywords.forEach(keyword => {
            const regex = new RegExp(`\\b${keyword}\\b`, 'gi');
            highlightedValue = highlightedValue.replace(regex, keyword.toUpperCase());
        });
        
        if (highlightedValue !== value) {
            const cursorPos = textarea.selectionStart;
            textarea.value = highlightedValue;
            textarea.setSelectionRange(cursorPos, cursorPos);
        }
    },

    /**
     * Handle key down for auto-completion
     */
    handleKeyDown: function(event) {
        const textarea = event.target;
        
        // Tab completion for common keywords
        if (event.key === 'Tab') {
            event.preventDefault();
            
            const cursorPos = textarea.selectionStart;
            const textBefore = textarea.value.substring(0, cursorPos);
            const words = textBefore.split(/\s+/);
            const lastWord = words[words.length - 1].toLowerCase();
            
            const completions = {
                'sel': 'SELECT ',
                'fr': 'FROM students ',
                'wh': 'WHERE ',
                'ord': 'ORDER BY ',
                'gr': 'GROUP BY ',
                'lim': 'LIMIT '
            };
            
            if (completions[lastWord]) {
                const before = textarea.value.substring(0, cursorPos - lastWord.length);
                const after = textarea.value.substring(cursorPos);
                textarea.value = before + completions[lastWord] + after;
                textarea.setSelectionRange(cursorPos - lastWord.length + completions[lastWord].length, cursorPos - lastWord.length + completions[lastWord].length);
            }
        }
    },

    /**
     * Add line numbers to textarea
     */
    addLineNumbers: function(textarea) {
        const wrapper = document.createElement('div');
        wrapper.className = 'query-editor-wrapper position-relative';
        textarea.parentNode.insertBefore(wrapper, textarea);
        wrapper.appendChild(textarea);
        
        const lineNumbers = document.createElement('div');
        lineNumbers.className = 'line-numbers position-absolute';
        lineNumbers.style.cssText = `
            left: 5px;
            top: 12px;
            color: var(--text-muted);
            font-family: monospace;
            font-size: 14px;
            line-height: 1.5;
            pointer-events: none;
            z-index: 1;
        `;
        wrapper.appendChild(lineNumbers);
        
        const updateLineNumbers = () => {
            const lines = textarea.value.split('\n').length;
            lineNumbers.innerHTML = Array.from({length: lines}, (_, i) => i + 1).join('<br>');
        };
        
        textarea.addEventListener('input', updateLineNumbers);
        textarea.addEventListener('scroll', () => {
            lineNumbers.style.top = (12 - textarea.scrollTop) + 'px';
        });
        
        updateLineNumbers();
    },

    /**
     * Initialize sample queries
     */
    initSampleQueries: function() {
        const sampleQueries = document.querySelectorAll('#samplesModal code');
        sampleQueries.forEach(code => {
            code.addEventListener('click', function() {
                const queryTextarea = document.querySelector('textarea[name="query"]');
                if (queryTextarea) {
                    queryTextarea.value = this.textContent;
                    queryTextarea.focus();
                }
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('samplesModal'));
                if (modal) modal.hide();
            });
        });
    },

    /**
     * Initialize query history
     */
    initQueryHistory: function() {
        this.loadQueryHistory();
        
        // Save query when form is submitted
        const queryForm = document.querySelector('form[method="POST"]');
        if (queryForm) {
            queryForm.addEventListener('submit', this.saveQuery.bind(this));
        }
    },

    /**
     * Save query to history
     */
    saveQuery: function(event) {
        const queryTextarea = document.querySelector('textarea[name="query"]');
        if (queryTextarea && queryTextarea.value.trim()) {
            const query = queryTextarea.value.trim();
            const history = this.getQueryHistory();
            
            // Add to beginning and limit to 10 queries
            history.unshift({
                query: query,
                timestamp: new Date().toISOString()
            });
            
            const limitedHistory = history.slice(0, 10);
            localStorage.setItem('queryHistory', JSON.stringify(limitedHistory));
        }
    },

    /**
     * Load query history
     */
    loadQueryHistory: function() {
        const history = this.getQueryHistory();
        if (history.length > 0) {
            this.displayQueryHistory(history);
        }
    },

    /**
     * Get query history from localStorage
     */
    getQueryHistory: function() {
        try {
            return JSON.parse(localStorage.getItem('queryHistory')) || [];
        } catch (e) {
            return [];
        }
    },

    /**
     * Display query history
     */
    displayQueryHistory: function(history) {
        const queryTextarea = document.querySelector('textarea[name="query"]');
        if (!queryTextarea) return;
        
        // Create history dropdown
        const historyButton = document.createElement('button');
        historyButton.type = 'button';
        historyButton.className = 'btn btn-outline-secondary dropdown-toggle';
        historyButton.textContent = 'History';
        historyButton.setAttribute('data-bs-toggle', 'dropdown');
        
        const historyDropdown = document.createElement('div');
        historyDropdown.className = 'dropdown-menu';
        
        history.forEach((item, index) => {
            const link = document.createElement('a');
            link.className = 'dropdown-item';
            link.href = '#';
            link.innerHTML = `
                <small class="text-muted">${new Date(item.timestamp).toLocaleString()}</small><br>
                <code>${item.query.substring(0, 50)}${item.query.length > 50 ? '...' : ''}</code>
            `;
            
            link.addEventListener('click', function(e) {
                e.preventDefault();
                queryTextarea.value = item.query;
                queryTextarea.focus();
            });
            
            historyDropdown.appendChild(link);
        });
        
        // Add to button group
        const buttonGroup = queryTextarea.closest('form').querySelector('.btn-group');
        if (buttonGroup) {
            const historyWrapper = document.createElement('div');
            historyWrapper.className = 'dropdown';
            historyWrapper.appendChild(historyButton);
            historyWrapper.appendChild(historyDropdown);
            buttonGroup.appendChild(historyWrapper);
        }
    }
};

// Reports functionality
const reports = {
    /**
     * Initialize reports
     */
    init: function() {
        if (window.location.pathname.includes('/reports')) {
            this.initCharts();
            this.initExportFunctions();
        }
    },

    /**
     * Initialize chart interactions
     */
    initCharts: function() {
        // Add chart interaction handlers if Chart.js is available
        if (typeof Chart !== 'undefined') {
            this.enhanceCharts();
        }
    },

    /**
     * Enhance charts with interactions
     */
    enhanceCharts: function() {
        // Add click handlers to chart elements
        const charts = Chart.instances;
        Object.values(charts).forEach(chart => {
            chart.options.onClick = (event, elements) => {
                if (elements.length > 0) {
                    const element = elements[0];
                    const datasetIndex = element.datasetIndex;
                    const index = element.index;
                    const value = chart.data.datasets[datasetIndex].data[index];
                    const label = chart.data.labels[index];
                    
                    utils.showToast(`${label}: ${value}`, 'info');
                }
            };
            
            chart.update();
        });
    },

    /**
     * Initialize export functions
     */
    initExportFunctions: function() {
        // Enhanced print function
        const printButton = document.querySelector('button[onclick="window.print()"]');
        if (printButton) {
            printButton.onclick = null;
            printButton.addEventListener('click', this.enhancedPrint.bind(this));
        }
    },

    /**
     * Enhanced print function
     */
    enhancedPrint: function() {
        // Hide unnecessary elements
        const elementsToHide = document.querySelectorAll('.btn, .navbar, .alert');
        elementsToHide.forEach(el => el.style.display = 'none');
        
        // Add print styles
        const printStyles = document.createElement('style');
        printStyles.innerHTML = `
            @media print {
                body { background: white !important; color: black !important; }
                .card { background: white !important; border: 1px solid #000 !important; }
                .table { color: black !important; }
                .badge { border: 1px solid #000 !important; background: white !important; color: black !important; }
            }
        `;
        document.head.appendChild(printStyles);
        
        // Print
        window.print();
        
        // Restore elements
        setTimeout(() => {
            elementsToHide.forEach(el => el.style.display = '');
            printStyles.remove();
        }, 1000);
    }
};

// Error handling
const errorHandler = {
    /**
     * Initialize error handling
     */
    init: function() {
        window.addEventListener('error', this.handleError.bind(this));
        window.addEventListener('unhandledrejection', this.handlePromiseRejection.bind(this));
    },

    /**
     * Handle JavaScript errors
     */
    handleError: function(event) {
        console.error('JavaScript error:', event.error);
        
        // Don't show error toast for minor errors
        if (!event.error.message.includes('Script error')) {
            utils.showToast('An error occurred. Please try again.', 'danger');
        }
    },

    /**
     * Handle promise rejections
     */
    handlePromiseRejection: function(event) {
        console.error('Promise rejection:', event.reason);
        utils.showToast('A network error occurred. Please check your connection.', 'warning');
    }
};

// Accessibility enhancements
const accessibility = {
    /**
     * Initialize accessibility features
     */
    init: function() {
        this.addKeyboardNavigation();
        this.addAriaLabels();
        this.addFocusManagement();
    },

    /**
     * Add keyboard navigation
     */
    addKeyboardNavigation: function() {
        // Add keyboard shortcuts
        document.addEventListener('keydown', function(event) {
            // Ctrl+/ for search focus
            if (event.ctrlKey && event.key === '/') {
                event.preventDefault();
                const searchInput = document.querySelector('input[name="search"]');
                if (searchInput) searchInput.focus();
            }
            
            // Escape to close modals
            if (event.key === 'Escape') {
                const openModal = document.querySelector('.modal.show');
                if (openModal) {
                    const modal = bootstrap.Modal.getInstance(openModal);
                    if (modal) modal.hide();
                }
            }
        });
    },

    /**
     * Add ARIA labels
     */
    addAriaLabels: function() {
        // Add labels to buttons without text
        const iconButtons = document.querySelectorAll('button:not([aria-label]) i.fas');
        iconButtons.forEach(icon => {
            const button = icon.closest('button');
            const iconClass = icon.className;
            
            if (iconClass.includes('fa-edit')) {
                button.setAttribute('aria-label', 'Edit');
            } else if (iconClass.includes('fa-trash')) {
                button.setAttribute('aria-label', 'Delete');
            } else if (iconClass.includes('fa-search')) {
                button.setAttribute('aria-label', 'Search');
            }
        });
    },

    /**
     * Add focus management
     */
    addFocusManagement: function() {
        // Focus management for modals
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.addEventListener('shown.bs.modal', function() {
                const firstInput = this.querySelector('input, textarea, select, button');
                if (firstInput) firstInput.focus();
            });
        });
    }
};

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all modules
    formValidation.init();
    searchFilter.init();
    dashboard.init();
    queryInterface.init();
    reports.init();
    errorHandler.init();
    accessibility.init();
    
    // Add fade-in animation to main content
    const mainContent = document.querySelector('.container-fluid');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }
    
    // Initialize any additional interactive elements
    initializeInteractiveElements();
    
    // Show welcome message on first visit
    showWelcomeMessage();
});

/**
 * Initialize additional interactive elements
 */
function initializeInteractiveElements() {
    // Add smooth scrolling to anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add loading states to form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                utils.showLoading(submitButton);
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Processing...';
            }
        });
    });
    
    // Add confirmation dialogs for delete actions
    const deleteLinks = document.querySelectorAll('a[href*="delete"]');
    deleteLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
}

/**
 * Show welcome message for new users
 */
function showWelcomeMessage() {
    const hasVisited = localStorage.getItem('hasVisited');
    
    if (!hasVisited && window.location.pathname === '/') {
        setTimeout(() => {
            utils.showToast('Welcome to Student Record Management System! Click "Add Student" to get started.', 'info', 5000);
            localStorage.setItem('hasVisited', 'true');
        }, 1000);
    }
}

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all modules
    formValidation.init();
    searchFilter.init();
    dashboard.init();
    queryInterface.init();
    reports.init();
    
    // Initialize other features
    initializeGeneralFeatures();
    showWelcomeMessage();
});

// Export utils for use in other scripts
window.StudentRecordsApp = {
    utils: utils,
    formValidation: formValidation,
    searchFilter: searchFilter,
    dashboard: dashboard,
    queryInterface: queryInterface,
    reports: reports
};
