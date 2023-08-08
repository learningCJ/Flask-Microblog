function getDarkModeSetting() {
    return new Promise(function(resolve, reject) {
        var cachedDarkMode = localStorage.getItem('darkMode');
        if (cachedDarkMode !== null) {
            // If cached, resolve the Promise with the cached value
            resolve(JSON.parse(cachedDarkMode));
        } else {
            // If not cached, make the AJAX request
            $.ajax({
                type: 'GET',
                url: '/get-session-data', 
                dataType: 'json',
                success: function(response) {
                    var darkMode = response['dark-mode'];
                    applyDarkMode(darkMode);

                    // Cache the dark mode value in the local storage
                    localStorage.setItem('darkMode', JSON.stringify(darkMode));

                    // Resolve the Promise with the retrieved value
                    resolve(darkMode);
                },
                error: function(xhr, status, error) {
                    // Reject the Promise with the error
                    reject(error);
                }
            });
        }
    });
}

// Function to apply dark mode based on the value
function applyDarkMode(darkMode) {
    if (darkMode) {
        // Enable dark mode
        $('main').addClass('dark-mode');
    } else {
        // Disable dark mode
        $('main').removeClass('dark-mode');
    }
}

$(document).ready(function() {
    getDarkModeSetting()
        .then(function(darkMode) {
            applyDarkMode(darkMode);
        })
        .catch(function(error) {
            console.error('Error fetching session data:', error);
        });
});

function toggleDarkMode() {
    getDarkModeSetting().then(function(darkMode){
        $.ajax({
            type: 'POST',
            url: '/toggle-dark-mode',
            success: function(response) {
                var darkMode = response['dark-mode'];
                applyDarkMode(darkMode);

                // Cache the dark mode value in the local storage
                localStorage.setItem('darkMode', JSON.stringify(darkMode));
            },
            error: function(error){
                console.error('Error toggling dark mode: ', error);
            }
        });
    })

   
}; 