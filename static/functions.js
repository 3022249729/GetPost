<<<<<<< HEAD
=======
const ws = true;
var socket;
>>>>>>> d8dadfd (websocket-liked-comments)
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
<<<<<<< HEAD
    setInterval(getPosts, 3000); 
=======

    if (ws) {
        initWS();
    } else {
        setInterval(getPosts, 3000);
    }

>>>>>>> d8dadfd (websocket-liked-comments)
}

function createNewPost() {
    const postMessageInput = document.getElementById("postMessageInput");
    const message = postMessageInput.value;
    postMessageInput.value = "";

    if (!message) {
        alert("You need to type something in order to post!");
        return;
    }

<<<<<<< HEAD
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
=======
    if (ws){
        socket.send(JSON.stringify({
            action: 'create_post',
            data: { message: message }
        }));
    } else {
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
>>>>>>> d8dadfd (websocket-liked-comments)
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

<<<<<<< HEAD
    const likeButton = document.createElement("button");
    likeButton.className = "post-like";
    likeButton.textContent = `❤️ Like (${postData.likes.length})`;
=======
    const likesCount = Array.isArray(postData.likes) ? postData.likes.length : 0;
    const likeButton = document.createElement("button");
    likeButton.className = "post-like";
    likeButton.textContent = `❤️ Like (${likesCount})`;
>>>>>>> d8dadfd (websocket-liked-comments)
    likeButton.setAttribute("onclick", `handleLike("${postData.id}")`);

    buttonsContainer.appendChild(likeButton);
    postContainer.appendChild(author);
    postContainer.appendChild(content);
    postContainer.appendChild(timestamp);
    postContainer.appendChild(buttonsContainer);

<<<<<<< HEAD
=======
    if (likesCount > 0) {
        const likedBy = document.createElement("div");
        likedBy.className = "post-likes-list"
        likedBy.innerHTML = `Liked by: ${postData.likes.join(', ')}`;
        postContainer.appendChild(likedBy);
    }


>>>>>>> d8dadfd (websocket-liked-comments)
    return postContainer.outerHTML;
}

function handleLike(postId) {
<<<<<<< HEAD
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            getPosts();
        }
    };
    request.open("POST", `/like/${postId}`);
    request.setRequestHeader('Content-Type', 'application/json');
    request.send();
=======
    if (ws){
        socket.send(JSON.stringify({
            action: 'like_post',
            data: { post_id: postId }
        }));
    } else {
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
>>>>>>> d8dadfd (websocket-liked-comments)
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
<<<<<<< HEAD
}
=======
}

function initWS() {
    socket = io();
    socket.on('connect', function() {
        console.log('WebSocket connected');
    });

    socket.on('disconnect', function() {
        console.log('WebSocket disconnected');
    });

    socket.on('create_post', function(data) {
        console.log('New post received: ', data.data);
        addPostToContainer(data.data)
    });

    socket.on('like_post', function(data) {
        console.log('Like post received, id:', data.post_id, 'like count:', data.like_count, 'liked by:', data.like_list);
        const postContainer = document.getElementById(data.post_id);
        if (postContainer) {
            const likeButton = postContainer.querySelector('.post-like');
            likeButton.textContent = `❤️ Like (${data.like_count})`;

            postContainer.querySelector('.post-likes-list');

            let likedBy = postContainer.querySelector('.post-likes-list');
            if (likedBy){
                likedBy.innerHTML = `Liked by: ${data.like_list.join(', ')}`;
            } else {
                likedBy = document.createElement('div');
                likedBy.className = 'post-likes-list';
                likedBy.innerHTML = `Liked by: ${data.like_list.join(', ')}`;
                postContainer.appendChild(likedBy);
            }
        }


    });
}
>>>>>>> d8dadfd (websocket-liked-comments)
