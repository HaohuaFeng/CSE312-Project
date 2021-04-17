let username_check = false;
let password_check = false;
function check_user(){
    const username = document.getElementById("username").value;
    const url = "/username_validation/?username=" + username;
    $.ajax(
        {
            url: url,
            type: "get",
            data: "",
            success: function (get_from_server) {
                if (get_from_server['exists']) {
                    username_check = true;
                    document.getElementById("display_exist").innerHTML = "<font color='green'> ✔</font>";
                } else {
                    username_check = false;
                    document.getElementById("display_exist").innerHTML = "<font color='red'> ❌ username not found</font>"
                }
                document.getElementById("submit").disabled
                    = (!username_check && !password_check) || !username_check || !password_check;
            }
        }
    )
}

function check_password_match() {
    const pw = document.getElementById("new_password").value;
    const cpw = document.getElementById("cnew_password").value;
    if (pw !== cpw) {
        document.getElementById("checkpw").innerHTML = "<font color='red'> ❌ passwords are not matched</font>";
        password_check = false;
    } else if (pw === cpw) {
        document.getElementById("checkpw").innerHTML = "<font color='green'> ✔</font>";
        password_check = true;
    }
    document.getElementById("submit").disabled
        = (!username_check && !password_check) || !username_check || !password_check;
}

function password_validation(){
    const pw = document.getElementById("new_password").value;
    let length = pw.length
    let num = false
    let lowercase = false
    let uppercase = false
    let specialChar = false
    const lenRequire = "length >= 8; "
    const lowRequire = "1 lowercase letter; "
    const upperRequire= "1 uppercase letter; "
    const specialRequire = "1 special character; "
    const numRequire = "1 number character; "
    let strong = 0
    let return_msg = " ❌ "
    if (length < 8){
        return_msg += lenRequire
    } else{
        strong++;
    }
    if(pw.match(/([0-9])+/)){
        strong++;
        num = true;
    } else{
        return_msg += numRequire
    }
    if(pw.match(/([a-z])+/)){
        strong++;
        lowercase = true;
    } else{
        return_msg += lowRequire
    }
    if(pw.match(/([A-Z])+/)){
        strong++;
        uppercase = true;
    } else{
        return_msg += upperRequire
    }
    const pattern = new RegExp(/[ !@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/g);
    if(pattern.test(pw)){
        strong++;
        specialChar = true
    } else{
        return_msg += specialRequire
    }
    if(length > 8 && num && lowercase && uppercase && specialChar){
        document.getElementById("valid_pw").innerHTML = "<font color='green'> ✔</font>";
    }else{
        document.getElementById("valid_pw").innerHTML = "<font color='red'>"+ return_msg +"</font>";
    }
}