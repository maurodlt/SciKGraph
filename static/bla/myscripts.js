$('#verticesThresholdSelect').mousedown(function(e){
    e.preventDefault();

    var select = this;
    var scroll = select .scrollTop;

    e.target.selected = !e.target.selected;

    setTimeout(function(){select.scrollTop = scroll;}, 0);
    $(select ).focus();


    document.querySelector('#verticesThresholdInput').value = ""


}).mousemove(function(e){e.preventDefault()});

/*
function myFunction() {
  window.alert('banana');
  select = document.querySelector('#verticesThresholdSelect');
  input = document.querySelector('#verticesThresholdInput');

  var nElements = parseInt(verticeThresholdInput.value)
  var select = []
  for (var i = 0; i < nElements; i++){
    select.push(i)
  }

  for (var o = 0; o < select.options.length; o++){
    if(select.options[o].selected == true && select.includes(o) == false || select.options[o].selected == false && select.includes(o) == true){
      document.querySelector('#verticesThresholdInput').value = ""
    }
  }

}

document.getElementById('verticesThresholdSelect').addEventListener('change', function (e) {
  //  window.alert('banana');
});
*/




const verticesThresholdSelect = document.querySelector('#verticesThresholdSelect');
const verticeThresholdInput = document.querySelector('#verticesThresholdInput');
verticeThresholdInput.addEventListener('change', (event) => {
  var nElements = parseInt(verticeThresholdInput.value)
  var select = []
  for (var i = 0; i < nElements; i++){
    select.push(i)
  }

  for (var o = 0; o < document.getElementById("verticesThresholdSelect").options.length; o++){
    //window.alert(select);
      if(select.includes(o)){
        //window.alert(o);
        document.getElementById("verticesThresholdSelect").options[o].selected = true;
      }else{
        document.getElementById("verticesThresholdSelect").options[o].selected = false;

      }
  }

});
