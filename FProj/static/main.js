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