// Welcome Message

console.log("AI Resume Analyzer Loaded Successfully");

// Navbar Shadow

window.addEventListener("scroll",function(){

const navbar=document.querySelector(".navbar");

if(window.scrollY>30){

navbar.classList.add("shadow");

}
else{

navbar.classList.remove("shadow");

}

});