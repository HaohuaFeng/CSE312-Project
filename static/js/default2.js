$(document).ready(function() {

//    namespace = '/test';
//    var socket = io(namespace);
    var socket = io()
    socket.on('blog_done', function(record) {
        var history = document.getElementById('chat');
        response = "<div class='history'><p>Uploaded by " + record.user + " by date: " + record.date + "</p><hr>";
        if(record.filename){
            response += "<embed src='static/images/" + record.filename + "' type='"+ record.filetype + "' width='90%'>";
        }
        response += "<p>Description: " + record.comment + "</p><br/></div>"
        history.innerHTML += response;
    });

    socket.on('privateMessage',function(msg) {
        var unread = document.getElementById('unread')
        unread.innerHTML = "UNREAD"
        alert("New message from "+msg.sender);
        });



    $('button').click(function(){
        var comment = $('#comment').val();
        var file = document.getElementById('form-file').files[0];
        if(file){
            console.log("type and name")
            console.log(file.type)
            console.log(file.name)
            var reader = new FileReader();
            reader.readAsDataURL(file);
            reader.addEventListener("load", function(){
                socket.emit('send-message', {'comment': comment, 'filename': file.name , 'filetype': file.type, 'file': reader.result});
            }, false);
        }
        else{
            socket.emit('send-message', {'comment': comment});
        }
    });
});

