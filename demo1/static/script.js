// Update your script.js to include code for displaying statistics
document.addEventListener('DOMContentLoaded', function() {
    // ... (your existing code)

    // Sample data for recipe statistics
    var statisticsData = {
        labels: ['Veg', 'Non-Veg', 'Desserts', 'Healthy'],
        datasets: [{
            data: [30, 25, 20, 25],
            backgroundColor: ['#F5B041', '#36A2EB', '#EAECEE', '#76D7C4'],
        }]
    };

    // Get the chart container
    var chartContainer = document.getElementById('recipeStatisticsChart').getContext('2d');

    // Create the chart
    var statisticsChart = new Chart(chartContainer, {
        type: 'doughnut', // You can change the chart type (bar, line, etc.)
        data: statisticsData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
        }
    });

    // Add animations to the chart using Anime.js
    anime({
        targets: statisticsChart.data.datasets[0].data,
        duration: 1000,
        easing: 'easeInOutQuad',
        delay: anime.stagger(200),
        loop: false,
        update: function(animation) {
            statisticsChart.update();
        }
    });
});


document.addEventListener('DOMContentLoaded', function() {
    var lines = [
        "Welcome to your food dashboard🌟",
        "Explore delicious recipes and create your own culinary masterpieces 🍳",
        "Discover new cooking techniques, ingredients, and flavors 🌶️📚",
        "Plan your meals, create shopping lists, and stay organized with ease 📅📋",
        "Find inspiration for your next meal and enjoy the art of cooking!🎨🍽️"
    ];

    var typingConfig = {
        strings: lines, // Join lines into a single string
        typeSpeed: 40, // Typing speed in milliseconds
        backSpeed: 20, // Backspacing speed in milliseconds
        backDelay: 2000, // Delay before starting to backspace
        showCursor: false, 
        loop: true,
        // Hide the blinking cursor
    };
    

    // Use typed.js to simulate typing effect
    var typed = new Typed('#typing-text', typingConfig);

    // Use typed.js to simulate typing effect
    

    // Listen for typing completion
    typed.on('completed', function() {
       // Add your fade-in/fade-out logic or any other actions here
    });
});

window.addEventListener('scroll', function() {
    var typingContainer = document.querySelector('.typing-container');

    // Check if the typing container is in the viewport
    if (isElementInViewport(typingContainer)) {
        // Trigger the typing animation when it comes into view
        var typed = new Typed('#typing-text', typingConfig);
    }
});

// Function to check if an element is in the viewport