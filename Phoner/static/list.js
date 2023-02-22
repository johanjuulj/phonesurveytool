

var button = document.getElementById('button').addEventListener("click", buttonClick);

function buttonClick(e){
    console.log("click")
    console.log(e)
    alert(e)
}