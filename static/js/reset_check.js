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