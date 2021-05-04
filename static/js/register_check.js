let username_check = false;
let password_valid = false;
let password_check = false;
let password_match = false;
function check_user(){
    const username = document.getElementById("username").value;
    const url = "/username_validation/?username=" + username;
    $.ajax(
        {
            url: url,
            type: "get",
            data: "",
            success: function (get_from_server) {
                console.log(get_from_server);
                if (get_from_server['exists']) {
                    username_check = false;
                    document.getElementById("display_exist").innerHTML = get_from_server['display'];
                } else {
                    username_check = true;
                    document.getElementById("display_exist").innerHTML = get_from_server['display'];
                }
            }
        }
    )
    document.getElementById("reg_sub").disabled
        = !(username_check && password_check);
}

function check_password_match() {
    const pw = document.getElementById("password").value;
    const cpw = document.getElementById("pcheck").value;
    if (pw === cpw && cpw.length > 0) {
        document.getElementById("checkpw").innerHTML = "<font color='green'> ✔ Matched</font>";
        password_match = true;
        password_check = password_valid && password_match;
    } else{
        document.getElementById("checkpw").innerHTML = "<font color='red'> ❌ Passwords are not matched</font>";
        password_check = false;
    }
    document.getElementById("reg_sub").disabled
        = !(username_check && password_check);
}

function password_validation(){
    const pw = document.getElementById("password").value;
    let length = pw.length;
    let num = false;
    let lowercase = false;
    let uppercase = false;
    let specialChar = false;
    const lenRequire = "❌ &nbsp;&nbsp; Length >= 8 <br>";
    const lowRequire = "❌ &nbsp;&nbsp;1 lowercase letter <br>";
    const upperRequire= "❌ &nbsp;&nbsp;1 uppercase letter <br>";
    const specialRequire = "❌ &nbsp;&nbsp;1 special character <br>";
    const numRequire = "❌ &nbsp;&nbsp;1 digit character <br>";
    let strong = 0;
    let return_msg = "❌ Password requirements: <br>";
    if (length < 8){
        return_msg += lenRequire;
    } else{
        strong++;
    }
    if(pw.match(/([0-9])+/)){
        strong++;
        num = true;
    } else{
        return_msg += numRequire;
    }
    if(pw.match(/([a-z])+/)){
        strong++;
        lowercase = true;
    } else{
        return_msg += lowRequire;
    }
    if(pw.match(/([A-Z])+/)){
        strong++;
        uppercase = true;
    } else{
        return_msg += upperRequire;
    }
    const pattern = new RegExp(/[ !@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/g);
    if(pattern.test(pw)){
        strong++;
        specialChar = true;
    } else{
        return_msg += specialRequire;
    }
    if(length >= 8 && num && lowercase && uppercase && specialChar){
        password_valid = true;
        password_check = password_valid && password_match;
        document.getElementById("valid_pw").innerHTML = "<font color='green'> ✔ You can user this password</font>";
    }else{
        document.getElementById("valid_pw").innerHTML = "<font color='red'>"+ return_msg +"</font>";
    }
}