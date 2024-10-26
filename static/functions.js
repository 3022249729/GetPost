function updateHome() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            console.log(JSON.parse(this.response));
        }
    }
    request.open("GET", "/posts");
    request.send();
}

