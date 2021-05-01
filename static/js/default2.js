function change1(x) {
    x.src = 'static/images/msg2.png';
}

function normal1(x) {
    x.src = 'static/images/msg1.png';
}

function change2(x) {
    x.src = 'static/images/game2.png';
}

function normal2(x) {
    x.src = 'static/images/game1.png';
}

$(document).ready(function() {
    var socket = io();
    socket.on('new_user', function(user) {
        var users = document.getElementById('current_users');
        var all_users = users.innerHTML;
        if (!all_users.includes(user.username)){
            var new_user = '<a href="user_profile/' + user.username + '" class="profile">'
            new_user += '<img src="static/images/' + user.icon + '" width=50/>' + user.username + '</a>';
            new_user += '&nbsp;&nbsp;&nbsp;';
            new_user += '<a href="direct_chat/' + user.username + '"><img src="static/images/msg1.png" ' +
                        'onmouseover="change1(this)" onmouseout="normal1(this)" class="mini_icon"/></a>';
            new_user += '&nbsp;&nbsp;&nbsp;';
            new_user += '<a href="game/' + user.username + '"><img src="static/images/game1.png" ' +
                        'onmouseover="change2(this)" onmouseout="normal2(this)" class="mini_icon"/></a><br/>';

            users.innerHTML += new_user;
        }
    });

    socket.on('blog_done', function(record) {
        var history = document.getElementById('view_blog');
        response = "<div class='history'><p><a href='user_profile/" + record.user + "' class='profile'>" +
                    record.user + "</a> | " + record.date + "</p><hr>";
        if(record.filename){
            response += "<embed src='static/images/" + record.filename + "' type='"+ record.filetype + "' width='90%'>";
        }
        response += "<p>" + record.comment + "</p><br/></div>";
        response += history.innerHTML;
        history.innerHTML = response;
    });

    socket.on('privateMessage',function(msg) {
//      using Snackbar/Toast to notice user there is new message comes
//      https://www.w3schools.com/howto/tryit.asp?filename=tryhow_js_snackbar
        var x = document.getElementById("newCome");
        x.innerHTML = "New message come from "+msg.sender;
        x.className = "show";
        setTimeout(function(){ x.className = x.className.replace("show", ""); }, 10000);
    });

    socket.on('notice', function(players) {
    //  using Snackbar/Toast to notice user there is new message comes
    //  https://www.w3schools.com/howto/tryit.asp?filename=tryhow_js_snackbar
        var y = document.getElementById("invitation");
        y.innerHTML = "A game invitation come from "+ players.sender;
        y.className = "show";
        setTimeout(function(){ y.className = y.className.replace("show", ""); }, 10000);
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
        var new_user = '<a href="user_profile/' + users[i].username + '" class="profile">'
        new_user += '<img src="static/images/' + users[i].icon + '" width=50/>' + users[i].username + '</a>';
        new_user += '&nbsp;&nbsp;&nbsp;';
        new_user += '<a href="direct_chat/' + users[i].username + '"><img src="static/images/msg1.png" ' +
                    'onmouseover="change1(this)" onmouseout="normal1(this)" class="mini_icon"/></a>';
        new_user += '&nbsp;&nbsp;&nbsp;';
        new_user += '<a href="game/' + users[i].username + '"><img src="static/images/game1.png" ' +
                    'onmouseover="change2(this)" onmouseout="normal2(this)" class="mini_icon"/></a><br/>';

        list.innerHTML += new_user;
    }
}

