document.getElementById("newuser").onclick = function () {
    document.getElementById("welcome_cont").style.display="none"
    document.getElementById("register").style.display = "block";
};

document.getElementById("reg_close").onclick=function () {
    document.getElementById("welcome_cont").style.display="flex"
    document.getElementById("register").style.display = "none";
};

document.getElementById("tuser").onclick = function () {
    // document.getElementById("alg").style.display = "none";
    document.getElementById("welcome_cont").style.display="none"
    document.getElementById("register").style.display='none'
    document.getElementById("lg").style.display = "block";
};


// document.getElementById("tadmin").onclick = function () {
//     document.getElementById("lg").style.display = "none";
//     document.getElementById("welcome_cont").style.display="none"
//     document.getElementById("alg").style.display = "block";
//     document.getElementById("register").style.display='none'


// };


document.getElementById("user").onclick = function () {
    document.getElementById("welcome_cont").style.display="none"
    document.getElementById("lg").style.display = "block";
};

document.getElementById("lgn_close").onclick=function () {
    document.getElementById("welcome_cont").style.display="flex"
    document.getElementById("lg").style.display = "none";
};


// document.getElementById("admin").onclick = function () {
//     document.getElementById("welcome_cont").style.display="none"
//     document.getElementById("alg").style.display = "block";
// };


// document.getElementById("algn_close").onclick=function () {
//     document.getElementById("welcome_cont").style.display="flex"
//     document.getElementById("alg").style.display = "none";
//     // document.getElementById("lg").style.display = "none";
// };






