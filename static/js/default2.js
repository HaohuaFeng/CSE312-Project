$(document).ready(function() {
    var socket = io();


    socket.on('new_user', function(user) {
        var users = document.getElementById('current_users');
        var all_users = users.innerHTML;
        if (!all_users.includes(user.username)){
            var new_user = '<img src="static/images/' + user.icon + '" width=50/>';
            new_user += '<a href="user_profile/' + user.username + '" class="profile"> ' + user.username + '</a>';
            new_user += '&nbsp;';
            new_user += '<a href="direct_chat/' + user.username + '"> Chat </a><br/>';
//            new_user += '<span id="new' + user.username + '"</span><br/>';

            users.innerHTML += new_user;
        }
    });


    socket.on('blog_done', function(record) {
        var history = document.getElementById('chat');
        response = "<div class='history'><p>Uploaded by " + record.user + " by date: " + record.date + "</p><hr>";
        if(record.filename){
            response += "<embed src='static/images/" + record.filename + "' type='"+ record.filetype + "' width='90%'>";
        }
        response += "<p>" + record.comment + "</p><br/></div>";
        history.innerHTML += response;
    });

    socket.on('privateMessage',function(msg) {
//      using Snackbar/Toast to notice user there is new message comes
//      https://www.w3schools.com/howto/tryit.asp?filename=tryhow_js_snackbar
        var x = document.getElementById("newCome");
        x.innerHTML = "New message come from "+msg.sender;
        x.className = "show";
        setTimeout(function(){ x.className = x.className.replace("show", ""); }, 10000);
//        alert("New message from "+msg.sender);

    });

    $('button').click(function(){
        var comment = $('#comment').val();
        var file = document.getElementById("form-file").files[0];
        document.getElementById("comment").value = "";
        document.getElementById("form-file").value = "";

        if(file){
            var reader = new FileReader();
            reader.readAsDataURL(file);
            reader.addEventListener("load", function(){
                var x = document.getElementById("newCome");
                x.innerHTML = "Thank you for sharing.";
                x.className = "show";
                setTimeout(function(){ x.className = x.className.replace("show", ""); }, 10000);
                socket.emit('send-message', {'comment': comment, 'filename': file.name , 'filetype': file.type, 'file': reader.result});
            }, false);
        }
        else if(comment !== ''){
            var x = document.getElementById("newCome");
            x.innerHTML = "Thank you for sharing.";
            x.className = "show";
            setTimeout(function(){ x.className = x.className.replace("show", ""); }, 10000);
            socket.emit('send-message', {'comment': comment});
        }
        else{
            var x = document.getElementById("newCome");
            x.innerHTML = "Please enter something.";
            x.className = "show";
            setTimeout(function(){ x.className = x.className.replace("show", ""); }, 10000);
        }
    });
});

getUsers();
setInterval (getUsers, 5000);

function getUsers() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            renderUsers(this.response);
        }
    };
    request.open("GET", "get-users");
    request.send()
}

function renderUsers(rawUsers) {
    let list = document.getElementById('current_users');
    list.innerHTML = "";
    var users = JSON.parse(rawUsers);
    for (i = 0; i < users.length; i++){
        var new_user = '<img src="static/images/' + users[i]['icon'] + '" width=50/>';
        new_user += '<a href="user_profile/' + users[i].username + '" class="profile"> ' + users[i].username + '</a>';
        new_user += '&nbsp;';
        new_user += '<a href="direct_chat/' + users[i].username + '">  Chat </a><br/>';
//        new_user += '<span id="new' + users[i].username + '"</span><br/>';


        list.innerHTML += new_user;
    }
}

