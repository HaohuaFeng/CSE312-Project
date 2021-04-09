$(document).ready(function() {
    // Use a "/test" namespace.
    // An application can open a connection on multiple namespaces, and
    // Socket.IO will multiplex all those connections on a single
    // physical channel. If you don't care about multiple channels, you
    // can set the namespace to an empty string.
    namespace = '/test';

    // Connect to the Socket.IO server.
    // The connection URL has the following format, relative to the current page:
    //     http[s]://<domain>:<port>[/<namespace>]
    var socket = io(namespace);

    // Event handler for new connections.
    // The callback function is invoked when a connection with the
    // server is established.
    socket.on('connect', function() {
        socket.emit('my_event', {data: 'I\'m connected!'});
    });

    // Event handler for server sent data.
    // The callback function is invoked whenever the server emits data
    // to the client. The data is then displayed in the "Received"
    // section of the page.
    socket.on('my_response', function(msg, cb) {
        $('#log').append('<br>' + $('<div/>').text('Received #' + msg.count + ': ' + msg.data).html());

        if (cb)
            cb();
    });

    // Handler for the "pong" message. When the pong is received, the
    // time from the ping is stored, and the average of the last 30
    // samples is average and displayed.
    socket.on('blog_done', function(record) {
        var history = document.getElementById('chat');
        response = "<div class='history'><p>Uploaded by " + record.user + " by date: " + record.date + "</p><hr>";
        if(record.image){
            response += "<img src='static/images/" + record.image + "'>";
        }
        response += "<p>Description: " + record.comment + "</p><br/></div>"


        history.innerHTML += response;
    });

    // Handlers for the different forms in the page.
    // These accept data from the user and send it to the server in a
    // variety of ways
    $('button').click(function(){
        var comment = $('#comment').val();
        var file = document.getElementById('form-file').files[0];
        if(file){
            var reader = new FileReader();
            reader.readAsDataURL(file);
            reader.addEventListener("load", function(){
                socket.emit('send-message', {'comment': comment, 'image': reader.result});
            }, false);
        }
        else{
            socket.emit('send-message', {'comment': comment});
        }
    });
});

