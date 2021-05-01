$(document).ready(function() {
    var socket = io();
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
});
