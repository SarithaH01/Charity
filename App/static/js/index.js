function showLogin(){
    document.querySelector('.login-wrapper').style.display = "flex"
    document.querySelector('.signup-wrapper').style.display = "none"
}

function closeLogin(){
    document.querySelector('.login-wrapper').style.display = "none"
}


function showSignup(){
    document.querySelector('.login-wrapper').style.display = "none"
    document.querySelector('.signup-wrapper').style.display = "flex"
}

function closeSignup(){
    document.querySelector('.signup-wrapper').style.display = "none"
}