function updateHome() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            const posts = JSON.parse(this.response);
            const postsContainer = document.getElementById('postsContainer');

            // Clear the existing posts
            postsContainer.innerHTML = ''; 

            // Dynamically add posts to the container
            posts.forEach(post => {
                const postDiv = document.createElement('div');
                postDiv.className = 'post';

                postDiv.innerHTML = `
                    <h3>${post.title}</h3>
                    <p>${post.content}</p>
                    <p>By: ${post.author}</p>
                    <p>Likes: ${post.likes}</p>
                    <a href="/like/${post.id}">Like</a>
                    <h4>Comments</h4>
                `;

                // Add comments
                post.comments.forEach(comment => {
                    const commentParagraph = document.createElement('p');
                    commentParagraph.textContent = `${comment.username}: ${comment.text}`;
                    postDiv.appendChild(commentParagraph);
                });

                // Comment form
                const commentForm = document.createElement('form');
                commentForm.method = 'POST';
                commentForm.action = `/comment/${post.id}`; // Adjusted to use 'id'

                // Prevent default form submission for AJAX-style comment posting
                commentForm.onsubmit = function (event) {
                    event.preventDefault();

                    const formData = new FormData(commentForm);
                    const commentRequest = new XMLHttpRequest();

                    commentRequest.onreadystatechange = function () {
                        if (this.readyState === 4 && this.status === 200) {
                            updateHome(); // Refresh posts to show the new comment
                        }
                    };

                    commentRequest.open("POST", commentForm.action);
                    commentRequest.send(formData);
                };

                commentForm.innerHTML = `
                    <input type="text" name="comment" placeholder="Add a comment" required>
                    <button type="submit">Comment</button>
                `;
                postDiv.appendChild(commentForm);

                postsContainer.appendChild(postDiv);
            });
        }
    };

    request.open("GET", "/posts");
    request.send();
}
