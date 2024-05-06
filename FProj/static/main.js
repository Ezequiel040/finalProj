function likePost(postId) {
    fetch(`/like/${postId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            // You may need to include additional headers depending on your requirements
        },
        body: JSON.stringify({ postId: postId }),
    })
    .then(response => {
        if (response.ok) {
            // Post was liked successfully, update the UI if needed
            console.log('Post liked successfully');
            location.reload();
            // You can update the UI here if needed, e.g., increment the like count without refreshing the page
        } else {
            // Handle errors
            console.error('Failed to like post');
        }
    })
    .catch(error => {
        console.error('Error occurred while liking post:', error);
    });
}

function dislikePost(postId) {
    fetch(`/dislike/${postId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            // You may need to include additional headers depending on your requirements
        },
        body: JSON.stringify({ postId: postId }),
    })
    .then(response => {
        if (response.ok) {
            // Post was liked successfully, update the UI if needed
            console.log('Post liked successfully');
            location.reload();
            // You can update the UI here if needed, e.g., increment the like count without refreshing the page
        } else {
            // Handle errors
            console.error('Failed to like post');
        }
    })
    .catch(error => {
        console.error('Error occurred while liking post:', error);
    });
}

function verifyIdentity() {
    const usrnm = document.getElementById("username").value;
    const passwrd = document.getElementById("password").value;
    const data = { "username": usrnm, "password": passwrd };

    fetch('http://127.0.0.1:5000/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data) // Include the JSON data here
    })
        .then(response => response.json())
        .then(data => console.log('Success:', data))
        .catch(error => console.error('Error:', error));
};

function createAccount() {
    const usrnm = document.getElementById("username").value;
    const passwrd = document.getElementById("password").value;

    const data = { "username": usrnm, "password": passwrd};

    fetch('http://127.0.0.1:5000/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        // Redirect to login page after account creation
        window.location.href = "/login";
    })
    .catch(error => console.error('Error:', error));
}


function rememberScrollPosition() {
    // Get the current scroll position of the element
    var scrollableContent = document.getElementById('scrollContent');
    var scrollPos = scrollableContent.scrollTop;

    // Store the scroll position in sessionStorage
    sessionStorage.setItem('scrollPosition', scrollPos);
}

// Function to restore scroll position
function restoreScrollPosition() {
    // Get the stored scroll position from sessionStorage
    var scrollPos = sessionStorage.getItem('scrollPosition');

    // If there's a stored scroll position, scroll to it
    if (scrollPos !== null) {
        var scrollableContent = document.getElementById('scrollContent');
        scrollableContent.scrollTop = scrollPos;
    }
}

// Call rememberScrollPosition() before refreshing the page
window.addEventListener('beforeunload', rememberScrollPosition);

// Call restoreScrollPosition() after the page has loaded
window.addEventListener('load', restoreScrollPosition);