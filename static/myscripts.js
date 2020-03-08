$('#verticesThresholdSelect').mousedown(function(e){
    e.preventDefault();

    var select = this;
    var scroll = select .scrollTop;

    e.target.selected = !e.target.selected;

    setTimeout(function(){select.scrollTop = scroll;}, 0);

    $(select ).focus();
}).mousemove(function(e){e.preventDefault()});


const verticesThresholdSelect = document.querySelector('#verticesThresholdSelect');
const verticeThresholdInput = document.querySelector('#verticesThresholdInput');
verticeThresholdInput.addEventListener('change', (event) => {
  var nElements = parseInt(verticeThresholdInput.value)
  var select = []
  for (var i = 0; i < nElements; i++){
    select.push(i+1)
  }


  $('#verticesThresholdSelect').val(select);

});
