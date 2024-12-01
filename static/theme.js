// theme.js
document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');

    // Check for saved theme preference or default to 'light'
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateIcon(savedTheme);

    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';

        // Update theme
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateIcon(newTheme);

        // If user is logged in, save preference to database
        if (isLoggedIn()) {
            saveThemePreference(newTheme);
        }
    });

    function updateIcon(theme) {
        themeIcon.textContent = theme === 'light' ? '🌙' : '☀️';
    }
});

function isLoggedIn() {
    // Check if user is logged in (you'll need to implement this)
    return document.cookie.includes('session');
}

async function saveThemePreference(theme) {
    try {
        const response = await fetch('/save-theme', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ theme })
        });
        if (!response.ok) throw new Error('Failed to save theme preference');
    } catch (error) {
        console.error('Error saving theme:', error);
    }
}