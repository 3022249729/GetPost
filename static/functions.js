let posts = {};

function redirectToRegister() {
    window.location.href = "/register";
}

function welcome() {
    document.addEventListener("keypress", function (event) {
        if (event.code === "Enter") {
            createNewPost();
        }
    });

    getPosts();
    setInterval(getPosts, 3000); 
}

function createNewPost() {
    const postMessageInput = document.getElementById("postMessageInput");
    const message = postMessageInput.value;
    postMessageInput.value = "";

    if (!message) {
        alert("You need to type something in order to post!");
        return;
    }

    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            getPosts();
        }
    };
    const messageJSON = { "message": message };
    request.open("POST", "/posts");
    request.setRequestHeader('Content-Type', 'application/json');
    request.send(JSON.stringify(messageJSON));
}


function getPosts() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            updatePosts(JSON.parse(this.responseText));
        }
    };
    request.open("GET", "/posts");
    request.send();
}

function updatePosts(serverPosts) {
    let serverIndex = 0;
    let localIndex = 0;

    while (serverIndex < serverPosts.length && localIndex < posts.length) {
        let fromServer = serverPosts[serverIndex];
        let localMessage = posts[localIndex];

        if (fromServer["id"] !== localMessage["id"]) {
            const PostElem = document.getElementById(localMessage["id"]);
            if (PostElem) {
                PostElem.parentNode.removeChild(PostElem);
            }
            localIndex++;
        } else {
            if (fromServer.likes.length !== localMessage.likes.length) {
                const PostElem = document.getElementById(localMessage["id"]);
                if (PostElem) {
                    const likeButton = PostElem.querySelector(".post-like");
                    likeButton.textContent = `❤️ Like (${fromServer.likes.length})`;
                }
            }
            serverIndex++;
            localIndex++;
        }
    }

    while (localIndex < posts.length) {
        let localMessage = posts[localIndex];
        const PostElem = document.getElementById(localMessage["id"]);
        if (PostElem) {
            PostElem.parentNode.removeChild(PostElem);
        }
        localIndex++;
    }

    while (serverIndex < serverPosts.length) {
        addPostToContainer(serverPosts[serverIndex]);
        serverIndex++;
    }
    posts = serverPosts;
}

function addPostToContainer(messageJSON) {
    const postsContainer = document.getElementById("postsContainer");
    postsContainer.insertAdjacentHTML("afterbegin", createPostHTML(messageJSON));
}

function createPostHTML(postData) {
    const postContainer = document.createElement("div");
    postContainer.className = "post-container";
    postContainer.id = postData.id;

    const author = document.createElement("div");
    author.className = "post-author";

    const profilePicture = document.createElement("img");
    profilePicture.className = "post-profile-picture";
    profilePicture.src = `/images/${postData.author_pfp}`;
    profilePicture.alt = `${postData.author}'s pfp`;

    const username = document.createElement("div");
    username.className = "post-username";
    username.textContent = postData.author;

    author.appendChild(profilePicture);
    author.appendChild(username);

    author.setAttribute("onclick", `openAuthorModal(${JSON.stringify(postData.author_pfp)})`);


    const content = document.createElement("div");
    content.className = "post-content";
    content.innerHTML = postData.content;

    const timestamp = document.createElement("div");
    timestamp.className = "post-timestamp";
    timestamp.textContent = new Date(postData.timestamp).toLocaleString();

    const buttonsContainer = document.createElement("div");
    buttonsContainer.className = "buttons-container";

    const likeButton = document.createElement("button");
    likeButton.className = "post-like";
    likeButton.textContent = `❤️ Like (${postData.likes.length})`;
    likeButton.setAttribute("onclick", `handleLike("${postData.id}")`);

    buttonsContainer.appendChild(likeButton);
    postContainer.appendChild(author);
    postContainer.appendChild(content);
    postContainer.appendChild(timestamp);
    postContainer.appendChild(buttonsContainer);

    return postContainer.outerHTML;
}

function handleLike(postId) {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            getPosts();
        }
    };
    request.open("POST", `/like/${postId}`);
    request.setRequestHeader('Content-Type', 'application/json');
    request.send();
}


function openProfileModal() {
    const modal = document.getElementById("profileModal");
    modal.style.display = "block";
}

function closeProfileModal() {
    const modal = document.getElementById("profileModal");
    modal.style.display = "none";
}

function openAuthorModal(author_pfp) {
    const modal = document.getElementById("authorModal");
    const pfp = document.getElementById("authorpfp");

    pfp.src = `/images/${author_pfp}`;
    modal.style.display = "flex";
}

function closeAuthorModal() {
    const modal = document.getElementById("authorModal");
    const pfp = document.getElementById("authorpfp");

    pfp.src = ``;
    modal.style.display = "none";
}

function setProfilePicture(image) {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            window.location.reload();
        }
    };
    request.open("POST", `/setpfp/${image}`);
    request.setRequestHeader('Content-Type', 'application/json');
    request.send();
}

function uploadProfilePicture(event) {
    const file = event.target.files[0];
    const formData = new FormData();
    formData.append('pfp', file);

    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (request.readyState === 4) {
            if (request.status === 200) {
                const response = JSON.parse(request.responseText)
                if (response.success) {
                    window.location.reload();
                } else {
                    alert("Failed to upload profile picture.");
                }
            } else {
                const response = JSON.parse(request.responseText)
                alert(response.message);
            }
        }
    };

    request.open("POST", `/uploadpfp`);
    request.send(formData);
}