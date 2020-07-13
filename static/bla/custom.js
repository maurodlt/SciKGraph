$( document ).ready(function(){
  document.getElementById("verticesThresholdSelect").options[0].selected = true;
  //document.getElementById("verticesThresholdSelect").selectedIndex = 2;
  //document.getElementById("verticesThresholdSelect").selectedIndex = [2,3,4];
  //document.getElementById("verticesThresholdSelect").options[0].selected = true;
  //document.getElementById("verticesThresholdSelect").options[2].selected = true;

  //window.alert(document.getElementById("verticesThresholdSelect").value);
  //window.alert(verticeThresholdInput.value);
  // Custom Cytoscape.JS code goes here.

  // Example: add linkouts to nodes that opens the "href" node attribute on click
  // cy.on('tap', 'node', function(){
  //   try { // your browser may block popups
  //     window.open( this.data('href') );
  //   } catch(e){ // fall back on url change
  //     window.location.href = this.data('href');
  //   }
  // });

  // For more options, check out http://js.cytoscape.org/

});
