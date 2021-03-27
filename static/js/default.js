//window.onload = function(){
//
//    const fake_user_list = {'a': 'Jimmy', 'b': 'Tonny', 'c': 'Haohua', 'd' : "none"};
//
//    function generate_online_user_list(user) {
//        const list = document.createElement('ul')
//        for(let i = 0; i < Object.keys(user).length; i++) {
//            const item = document.createElement('li')
//            const avatar = document.createElement('img');
//            const url = document.createElement('a')
//            url.href = "https://www.google.com/"
//            url.target = "_blank"
//            avatar.src = "../images/avatar/fakeuser.png"
//            avatar.alt = ""
//            url.appendChild(avatar)
//            url.appendChild(document.createTextNode(Object.values(user)[i]))
//            item.appendChild(url)
//            list.appendChild(item)
//        }
//        return list
//    }
//    document.getElementsByClassName("online_user")[0].appendChild(generate_online_user_list(fake_user_list))
//    const spans = document.getElementsByTagName("span")
//    for (let i = 0; i < spans.length; i++) {
//        spans[i].onclick = function () {
//            if (this.id === "home") {
//                window.location.href = 'default.html'
//            }
//            else if (this.id === "login") {
//                window.location.href = 'new_login.html'
//            }
//            else if(this.id === "register") {
//                window.location.href = 'new_register.html'
//            }
//        }
//    }
//}