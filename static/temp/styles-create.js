var styles = [ {
  "format_version" : "1.0",
  "generated_by" : "cytoscape-3.7.2",
  "target_cytoscapejs_version" : "~2.1",
  "title" : "default_0",
  "style" : [ {
    "selector" : "node",
    "css" : {
      "height" : 35.0,
      "color" : "rgb(0,0,0)",
      "border-color" : "rgb(204,204,204)",
      "shape" : "ellipse",
      "width" : 35.0,
      "background-opacity" : 1.0,
      "text-opacity" : 1.0,
      "text-valign" : "center",
      "text-halign" : "center",
      "font-size" : 12,
      "font-family" : "SansSerif.plain",
      "font-weight" : "normal",
      "background-color" : "rgb(137,208,245)",
      "border-opacity" : 1.0,
      "border-width" : 0.0,
      "content" : "data(dicionario)"
    }
  }, {
    "selector" : "node[ peso < 2]",
    "css" : {
      "height" : 5.0,
      "width" : 5.0
    }
  }, {
    "selector" : "node[ peso > 45 ]",
    "css" : {
      "height" : 200.0,
      "width" : 200.0
    }
  }, {
    "selector" : "node[peso > 3][peso < 46]",
    "css" : {
      "height" : "mapData(peso,3,46,20,200)",
      "width" : "mapData(peso,3,46,20,200)"
    }
  }, {
    "selector" : "node[peso > 46]",
    "css" : {
      "background-color" : "rgb(102,37,6)"
    }
  }, {
    "selector" : "node[peso = 45]",
    "css" : {
      "background-color" : "rgb(153,52,4)"
    }
  }, {
    "selector" : "node[peso > 30][peso < 45]",
    "css" : {
      "background-color" : "mapData(peso,30,45,rgb(254,153,41),rgb(153,52,4))"
    }
  }, {
    "selector" : "node[peso > 1][peso < 30]",
    "css" : {
      "background-color" : "mapData(peso,1,30,rgb(255,247,188),rgb(254,153,41))"
    }
  }, {
    "selector" : "node[peso = 1]",
    "css" : {
      "background-color" : "rgb(255,247,188)"
    }
  }, {
    "selector" : "node[peso < 1]",
    "css" : {
      "background-color" : "rgb(255,255,229)"
    }
  }, {
    "selector" : "node[peso > 45]",
    "css" : {
      "font-size" : 1
    }
  }, {
    "selector" : "node[peso = 45]",
    "css" : {
      "font-size" : 40
    }
  }, {
    "selector" : "node[peso > 3][peso < 45]",
    "css" : {
      "font-size" : "mapData(peso,3,45,5,40)"
    }
  }, {
    "selector" : "node[peso = 3]",
    "css" : {
      "font-size" : 5
    }
  }, {
    "selector" : "node[peso < 3]",
    "css" : {
      "font-size" : 1
    }
  }, {
    "selector" : "node:selected",
    "css" : {
      "background-color" : "rgb(255,255,0)"
    }
  }, {
    "selector" : "edge",
    "css" : {
      "content" : "",
      "font-family" : "Dialog.plain",
      "font-weight" : "normal",
      "opacity" : 1.0,
      "width" : 2.0,
      "color" : "rgb(0,0,0)",
      "text-opacity" : 1.0,
      "line-color" : "rgb(132,132,132)",
      "target-arrow-shape" : "none",
      "line-style" : "solid",
      "source-arrow-shape" : "none",
      "target-arrow-color" : "rgb(0,0,0)",
      "font-size" : 10,
      "source-arrow-color" : "rgb(0,0,0)"
    }
  }, {
    "selector" : "edge:selected",
    "css" : {
      "line-color" : "rgb(255,0,0)"
    }
  } ]
} ]
