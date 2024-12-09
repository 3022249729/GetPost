const ws = true;
var socket;
let posts = {};

let currentFontSize = 'medium';
let user;

function changeThemeMode() {
    const img = document.getElementById('themeModeIcon');
    const span = document.getElementById('themeModeText')
    
    const isDarkMode = localStorage.getItem('darkMode') === 'enabled';

    if (isDarkMode) {
        img.src = "/images/dark-mode.svg";
        span.textContent = "Dark Mode";
        document.body.classList.remove('dark-mode');
        localStorage.setItem('darkMode', 'disabled');
    } else {
        img.src = "/images/light-mode.svg";
        span.textContent = "Light Mode";
        document.body.classList.add('dark-mode'); 
        localStorage.setItem('darkMode', 'enabled');
    }
}

function initDarkMode() {
    const isDarkMode = localStorage.getItem('darkMode') === 'enabled';
    const img = document.getElementById('themeModeIcon');
    const span = document.getElementById('themeModeText')
    
    if (isDarkMode) {
        document.body.classList.add('dark-mode');
        img.src = "/images/light-mode.svg";
        span.textContent = "Light Mode";
    } else {
        img.src = "/images/dark-mode.svg";
        span.textContent = "Dark Mode";
    }
}

function getXSRF() {
    const cookies_string = document.cookie.replaceAll('; ', ';');
    const cookies = cookies_string.split(';');
    let xsrf_token;
    for (const cookie of cookies) {
        const [key, val] = cookie.split('=');
        if (key === "xsrf_token") {
            xsrf_token = val;
            break;
        }
    } 
    return xsrf_token
}

function welcome() {
    initDarkMode();

    const postMessageInput = document.getElementById("postMessageInput");

    document.addEventListener("keydown", function (event) {
        if (event.code === "Enter" && document.activeElement === postMessageInput) {
            event.preventDefault();
            createNewPost();
        }
    });

    getPosts();

    if (ws) {
        initWS();
    } else {
        setInterval(getPosts, 3000);
    }
}

function addPostToContainer(messageJSON) {
    const postsContainer = document.getElementById("postsContainer");
    postsContainer.insertAdjacentHTML("afterbegin", createPostHTML(messageJSON));
    if (document.body.classList.contains('dark-mode')) {
        const postElement = document.getElementById(messageJSON.id);
        if (postElement) {
            postElement.classList.add('dark-mode');
        }
    }
}

function redirectToRegister() {
    window.location.href = "/register";
}



function createNewPost() {
    const postMessageInput = document.getElementById("postMessageInput");
    const message = postMessageInput.value;
    postMessageInput.value = "";

    if (!message) {
        alert("You need to type something in order to post!");
        return;
    }

    if (ws){
        const scheduleCheckbox = document.getElementById("schedule-checkbox");
        const scheduleInput = document.getElementById("schedule-input");
    
        if (scheduleCheckbox.checked) {
            const scheduledTime = scheduleInput.value;
            if (!scheduledTime) {
                alert("Please select a time for the scheduled post.");
                return;
            }

            socket.send(JSON.stringify({
                action: 'schedule_post',
                data: { message: message, scheduledTime: scheduledTime }
            }));
            scheduleCheckbox.checked = false;
            scheduleInput.style.display = "none";

        } else {
            socket.send(JSON.stringify({
                action: 'create_post',
                data: { message: message }
            }));
        }

    } else {
        const request = new XMLHttpRequest();
        request.onreadystatechange = function () {
            if (this.readyState === 4 && this.status === 200) {
                getPosts();
            }
        };
        const messageJSON = { "message": message, "fontSize": currentFontSize};
        request.open("POST", "/posts");
        request.setRequestHeader('Content-Type', 'application/json');
        request.send(JSON.stringify(messageJSON));
    }
}


function getPosts() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            user = localStorage.getItem('auth_user');
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
    const fontSize = messageJSON.fontSize || currentFontSize;
    messageJSON.fontSize = fontSize;
    postsContainer.insertAdjacentHTML("afterbegin", createPostHTML(messageJSON));
}

function createPostHTML(postData) {
    const postContainer = document.createElement("div");

    const fontSizeClass = `font-${postData.fontSize || currentFontSize}`;
    postContainer.className = `post-container ${fontSizeClass}`;
    postContainer.id = postData.id;

    const authorLine = document.createElement("div");
    authorLine.className = "post-author-line";

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
    authorLine.appendChild(author)

    if (postData.author === user){
        const delete_icon = document.createElement("img");
        delete_icon.className = "delete-icon";
        delete_icon.src = `/images/delete.svg`;
        delete_icon.alt = `Delete post ${postData.id}`;
        delete_icon.setAttribute("onclick", `handleDelete("${postData.id}")`);
        authorLine.appendChild(delete_icon)

    }
    
    author.setAttribute("onclick", `openAuthorModal(${JSON.stringify(postData.author_pfp)})`);

    const content = document.createElement("div");
    content.className = `post-content ${fontSizeClass}`
    content.innerHTML = postData.content;

    const timestamp = document.createElement("div");
    timestamp.className = "post-timestamp";
    timestamp.textContent = new Date(postData.timestamp).toLocaleString();

    const buttonsContainer = document.createElement("div");
    buttonsContainer.className = "buttons-container";

    const likesCount = Array.isArray(postData.likes) ? postData.likes.length : 0;
    const likeButton = document.createElement("button");
    likeButton.className = "post-like";
    likeButton.textContent = `❤️ Like (${likesCount})`;
    likeButton.setAttribute("onclick", `handleLike("${postData.id}")`);

    buttonsContainer.appendChild(likeButton);
    postContainer.appendChild(authorLine);
    postContainer.appendChild(content);
    postContainer.appendChild(timestamp);
    postContainer.appendChild(buttonsContainer);

    if (likesCount > 0) {
        const likedBy = document.createElement("div");
        likedBy.className = "post-likes-list"
        likedBy.innerHTML = `Liked by: ${postData.likes.join(', ')}`;
        postContainer.appendChild(likedBy);
    }


    return postContainer.outerHTML;
}

function handleLike(postId) {
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
}

function handleDelete(postId) {
    if (ws){
        socket.send(JSON.stringify({
            action: 'delete_post',
            data: { post_id: postId }
        }));
    } else {
        const request = new XMLHttpRequest();
        request.onreadystatechange = function () {
            if (this.readyState === 4 && this.status === 200) {
                getPosts();
            }
        };
        request.open("POST", `/delete/${postId}`);
        request.setRequestHeader('Content-Type', 'application/json');
        request.send();
    }
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
    const xsrfToken = getXSRF();
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (request.readyState === 4) {
            if (request.status === 200) {
                const response = JSON.parse(request.responseText)
                if (response.success) {
                    window.location.reload();
                } else {
                    alert("Failed to set profile picture.");
                }
            } else {
                const response = JSON.parse(request.responseText)
                alert(response.message);
                if (request.status === 403){
                    document.cookie = 'xsrf_token=; max-age=0; path=/; domain=' + window.location.hostname;
                    window.location.href = '/login'; 
                } else {
                    window.location.reload();
                }
            }
        }
    };
    request.open("POST", `/setpfp/${image}`);
    request.setRequestHeader('Content-Type', 'application/json');
    request.setRequestHeader('XSRF-TOKEN', xsrfToken);
    request.send();
}

function uploadProfilePicture(event) {
    const xsrfToken = getXSRF();
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
                if (request.status === 403){
                    document.cookie = 'xsrf_token=; max-age=0; path=/; domain=' + window.location.hostname;
                    window.location.href = '/login'; 
                } else {
                    window.location.reload();
                }
            }
        }
    };

    request.open("POST", `/uploadpfp`);
    request.setRequestHeader('XSRF-TOKEN', xsrfToken);
    request.send(formData);
}

function initWS() {
    
    const xsrfToken = getXSRF();
    socket = io({
        query: {
            xsrf_token: xsrfToken,
        },
    });

    socket.on('connect', function() {
        console.log('WebSocket connected');
        
    });

    socket.on('disconnect', function() {
        console.log('WebSocket disconnected');
    });

    socket.on('auth', function(data) {
        localStorage.setItem('auth_user', data.username);
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

    socket.on('unlike_post', function(data) {
        console.log('Unlike post received, id:', data.post_id, 'like count:', data.like_count, 'liked by:', data.like_list);
        const postContainer = document.getElementById(data.post_id);
        if (postContainer) {
            const likeButton = postContainer.querySelector('.post-like');
            likeButton.textContent = `❤️ Like (${data.like_count})`;

            postContainer.querySelector('.post-likes-list');

            let likedBy = postContainer.querySelector('.post-likes-list');
            if (data.like_list.length > 0){
                likedBy.innerHTML = `Liked by: ${data.like_list.join(', ')}`;
            } else {
                likedBy.remove();
            }
        }
    });

    socket.on('delete_post', function(data) {
        console.log('Delete post received, id:', data.post_id);
        const postContainer = document.getElementById(data.post_id);
        postContainer.remove();
        
    });

    socket.on('unauthorized', function(data) {
        let hostname = window.location.hostname;
        let parts = hostname.split('.');
        let secondLevelDomain = parts.length > 1 ? parts[parts.length - 2] : hostname;
        console.log(secondLevelDomain); 

        document.cookie = `xsrf_token=; max-age=0; path=/; domain=${secondLevelDomain}`;
        console.log(document.cookie);

        socket.disconnect();
        alert(data.message);
        window.location.href = '/login'; 
    });

    socket.on('schedule_post_error', function(data) {
        alert(data.message);
    });

    socket.on('remaining_time', function(data) {
        addScheduledPostToContainer(data);
    });
    
    socket.on('created_scheduled_post', function() {
            const scheduledPostContainer = document.getElementById("scheduledPostContainer");
            scheduledPostContainer.innerHTML = "";
            scheduledPostContainer.style.display = "none";
    });
    
}

function setFontSize(size) {
    currentFontSize = size;
    const posts = document.querySelectorAll('.post-content');
    posts.forEach(post => {
        post.classList.remove('font-small', 'font-medium', 'font-large', 'font-xlarge');
        post.classList.add(`font-${size}`);
    });
}

function toggleScheduler() {
    const scheduleCheckbox = document.getElementById("schedule-checkbox");
    const scheduleInput = document.getElementById("schedule-input");

    if (scheduleCheckbox.checked) {
        scheduleInput.style.display = "block";
    } else {
        scheduleInput.style.display = "none";
    }
}

function addScheduledPostToContainer(messageJSON) {
    const scheduledPostContainer = document.getElementById("scheduledPostContainer");
    scheduledPostContainer.innerHTML = "";

    if (scheduledPostContainer.style.display === "none") {
        scheduledPostContainer.style.display = "flex";
    }

    const fontSize = messageJSON.fontSize || currentFontSize;
    messageJSON.fontSize = fontSize;
    scheduledPostContainer.insertAdjacentHTML("afterbegin", createScheduledPostHTML(messageJSON));
}

function createScheduledPostHTML(postData) {
    const scheduledPostContainer = document.createElement("div");

    const fontSizeClass = `font-${postData.fontSize || currentFontSize}`;
    scheduledPostContainer.className = `scheduled-post-container ${fontSizeClass}`;
    scheduledPostContainer.id = postData.scheduled_id;

    const authorLine = document.createElement("div");
    authorLine.className = "post-author-line";
    
    const username = document.createElement("div");
    username.className = "post-username";
    username.textContent = postData.message;

    authorLine.appendChild(username)

    const content = document.createElement("div");
    content.className = `post-content ${fontSizeClass}`
    content.innerHTML = postData.content;

    scheduledPostContainer.appendChild(authorLine);
    scheduledPostContainer.appendChild(content);

    return scheduledPostContainer.outerHTML;
}