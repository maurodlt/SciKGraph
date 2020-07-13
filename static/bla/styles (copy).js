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
    "selector" : "node[ id = '76275' ]",
    "css" : {
      "width" : 80.0,
      "background-opacity" : 0.19607843137254902,
      "shape" : "roundrectangle",
      "height" : 60.0
    }
  }, {
    "selector" : "node[ id = '76028' ]",
    "css" : {
      "width" : 294.16407445059576,
      "background-opacity" : 0.19607843137254902,
      "shape" : "roundrectangle",
      "height" : 132.10797714509283
    }
  }, {
    "selector" : "node[ id = '76042' ]",
    "css" : {
      "width" : 192.76960930951043,
      "background-opacity" : 0.19607843137254902,
      "shape" : "roundrectangle",
      "height" : 96.09381675583143
    }
  }, {
    "selector" : "node[ id = '76055' ]",
    "css" : {
      "width" : 174.90483883840307,
      "background-opacity" : 0.19607843137254902,
      "shape" : "roundrectangle",
      "height" : 229.52059133054695
    }
  }, {
    "selector" : "node[ id = '76067' ]",
    "css" : {
      "width" : 112.50904055743649,
      "background-opacity" : 0.19607843137254902,
      "shape" : "roundrectangle",
      "height" : 243.487732025
    }
  }, {
    "selector" : "node[ id = '75818' ]",
    "css" : {
      "width" : 310.3824670779313,
      "background-opacity" : 0.19607843137254902,
      "shape" : "roundrectangle",
      "height" : 298.07342348170323
    }
  }, {
    "selector" : "node[ id = '76079' ]",
    "css" : {
      "width" : 142.98576959926754,
      "background-opacity" : 0.19607843137254902,
      "shape" : "roundrectangle",
      "height" : 142.52400821906735
    }
  }, {
    "selector" : "node[ id = '76092' ]",
    "css" : {
      "width" : 80.0,
      "background-opacity" : 0.19607843137254902,
      "shape" : "roundrectangle",
      "height" : 60.0
    }
  }, {
    "selector" : "node[ id = '75840' ]",
    "css" : {
      "width" : 467.1869979004575,
      "background-opacity" : 0.19607843137254902,
      "shape" : "roundrectangle",
      "height" : 254.45053862620523
    }
  }, {
    "selector" : "node[ id = '76105' ]",
    "css" : {
      "width" : 89.59091399947488,
      "background-opacity" : 0.19607843137254902,
      "shape" : "roundrectangle",
      "height" : 154.49099588101558
    }
  }, {
    "selector" : "node[ id = '75860' ]",
    "css" : {
      "width" : 336.1933295415598,
      "background-opacity" : 0.19607843137254902,
      "shape" : "roundrectangle",
      "height" : 237.79745388929962
    }
  }, {
    "selector" : "node[ id = '76118' ]",
    "css" : {
      "width" : 80.0,
      "background-opacity" : 0.19607843137254902,
      "shape" : "roundrectangle",
      "height" : 60.0
    }
  }, {
    "selector" : "node[ id = '75874' ]",
    "css" : {
      "width" : 307.4843626974821,
      "background-opacity" : 0.19607843137254902,
      "shape" : "roundrectangle",
      "height" : 244.1922638281644
    }
  }, {
    "selector" : "node[ id = '76131' ]",
    "css" : {
      "width" : 193.4742688834515,
      "background-opacity" : 0.19607843137254902,
      "shape" : "roundrectangle",
      "height" : 68.83657750339876
    }
  }, {
    "selector" : "node[ id = '75888' ]",
    "css" : {
      "width" : 197.91970069668923,
      "background-opacity" : 0.19607843137254902,
      "shape" : "roundrectangle",
      "height" : 149.76327523255247
    }
  }, {
    "selector" : "node[ id = '76143' ]",
    "css" : {
      "width" : 109.51223018974815,
      "background-opacity" : 0.19607843137254902,
      "shape" : "roundrectangle",
      "height" : 150.87892236075805
    }
  }, {
    "selector" : "node[ id = '76155' ]",
    "css" : {
      "width" : 116.15775640704373,
      "background-opacity" : 0.19607843137254902,
      "shape" : "roundrectangle",
      "height" : 149.60810679752808
    }
  }, {
    "selector" : "node[ id = '75903' ]",
    "css" : {
      "width" : 297.9318433653027,
      "background-opacity" : 0.19607843137254902,
      "shape" : "roundrectangle",
      "height" : 210.69169485985822
    }
  }, {
    "selector" : "node[ id = '76167' ]",
    "css" : {
      "width" : 106.26955584260622,
      "background-opacity" : 0.19607843137254902,
      "shape" : "roundrectangle",
      "height" : 151.51742422151153
    }
  }, {
    "selector" : "node[ id = '75916' ]",
    "css" : {
      "width" : 310.59026717119275,
      "background-opacity" : 0.19607843137254902,
      "shape" : "roundrectangle",
      "height" : 177.16382429342093
    }
  }, {
    "selector" : "node[ id = '76179' ]",
    "css" : {
      "width" : 188.3593550565488,
      "background-opacity" : 0.19607843137254902,
      "shape" : "roundrectangle",
      "height" : 111.24481784144814
    }
  }, {
    "selector" : "node[ id = '75930' ]",
    "css" : {
      "width" : 187.091447556327,
      "background-opacity" : 0.19607843137254902,
      "shape" : "roundrectangle",
      "height" : 156.69588267478332
    }
  }, {
    "selector" : "node[ id = '76191' ]",
    "css" : {
      "width" : 151.3999380136339,
      "background-opacity" : 0.19607843137254902,
      "shape" : "roundrectangle",
      "height" : 139.88522192232472
    }
  }, {
    "selector" : "node[ id = '75944' ]",
    "css" : {
      "width" : 189.34440873610401,
      "background-opacity" : 0.19607843137254902,
      "shape" : "roundrectangle",
      "height" : 106.5859954279174
    }
  }, {
    "selector" : "node[ id = '76203' ]",
    "css" : {
      "width" : 192.099153570152,
      "background-opacity" : 0.19607843137254902,
      "shape" : "roundrectangle",
      "height" : 84.72139976487074
    }
  }, {
    "selector" : "node[ id = '75958' ]",
    "css" : {
      "width" : 109.25838975468196,
      "background-opacity" : 0.19607843137254902,
      "shape" : "roundrectangle",
      "height" : 249.4292217107468
    }
  }, {
    "selector" : "node[ id = '76215' ]",
    "css" : {
      "width" : 193.4499758637687,
      "background-opacity" : 0.19607843137254902,
      "shape" : "roundrectangle",
      "height" : 69.57433307935548
    }
  }, {
    "selector" : "node[ id = '75972' ]",
    "css" : {
      "width" : 194.93643630660677,
      "background-opacity" : 0.19607843137254902,
      "shape" : "roundrectangle",
      "height" : 105.84133079386777
    }
  }, {
    "selector" : "node[ id = '76227' ]",
    "css" : {
      "width" : 125.96937016496508,
      "background-opacity" : 0.19607843137254902,
      "shape" : "roundrectangle",
      "height" : 147.33776182651502
    }
  }, {
    "selector" : "node[ id = '76239' ]",
    "css" : {
      "width" : 162.71083113448708,
      "background-opacity" : 0.19607843137254902,
      "shape" : "roundrectangle",
      "height" : 136.26204837845887
    }
  }, {
    "selector" : "node[ id = '75986' ]",
    "css" : {
      "width" : 298.3863656879478,
      "background-opacity" : 0.19607843137254902,
      "shape" : "roundrectangle",
      "height" : 142.2993455161792
    }
  }, {
    "selector" : "node[ id = '76251' ]",
    "css" : {
      "width" : 187.34134390110353,
      "background-opacity" : 0.19607843137254902,
      "shape" : "roundrectangle",
      "height" : 116.4783498154045
    }
  }, {
    "selector" : "node[ id = '76000' ]",
    "css" : {
      "width" : 112.38245787852725,
      "background-opacity" : 0.19607843137254902,
      "shape" : "roundrectangle",
      "height" : 172.24177081457435
    }
  }, {
    "selector" : "node[ id = '76263' ]",
    "css" : {
      "width" : 187.5800900984716,
      "background-opacity" : 0.19607843137254902,
      "shape" : "roundrectangle",
      "height" : 115.28183273751677
    }
  }, {
    "selector" : "node[ id = '76014' ]",
    "css" : {
      "width" : 80.0,
      "background-opacity" : 0.19607843137254902,
      "shape" : "roundrectangle",
      "height" : 60.0
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
},{},{}
,{
                        "selector" : "node[ peso <= 1]",
                        "css" : {
                            "height" : 10.0,
                            "width" : 10.0
                        }
                    }, {
                        "selector" : "node[ peso >= 3 ]",
                        "css" : {
                            "height" : 200.0,
                            "width" : 200.0
                        }
                    }, {
                        "selector" : "node[peso > 1][peso < 3]",
                        "css" : {
                            "height" : "mapData(peso,1,3,10,200)",
                            "width" : "mapData(peso,1,3,10,200)"
                        }
                    }, {
                        "selector" : "node[peso >= 3]",
                        "css" : {
                          "background-color" : "rgb(102,37,6)"
                        }
                      }, {
                        "selector" : "node[peso >= 2][peso < 3]",
                        "css" : {
                          "background-color" : "mapData(peso,2,3,rgb(254,153,41),rgb(153,52,4))"
                        }
                      }, {
                        "selector" : "node[peso > 1][peso < 2]",
                        "css" : {
                          "background-color" : "mapData(peso,1,2,rgb(255,247,188),rgb(254,153,41))"
                        }
                      }, {
                        "selector" : "node[peso <= 1]",
                        "css" : {
                          "background-color" : "rgb(255,247,188)"
                        }
                      }, {
                            "selector" : "node[peso >= 3]",
                            "css" : {
                              "font-size" : 50.0
                            }
                          }, {
                            "selector" : "node[peso > 1][peso < 3]",
                            "css" : {
                              "font-size" : "mapData(peso,1,3,10,50.0)"
                            }
                          }, {
                            "selector" : "node[peso <= 1]",
                            "css" : {
                              "font-size" : 10
                            }
                          }, {
                                        "selector" : "node[ id = '6964' ]",
                                        "css" : {
                                            "height" : 99.0,
                                            "shape" :" roundrectangle ",
                                            "width" : 225.0,
                                            "background-opacity" : 0.19607843137254902
                                        }
                                    }, {
                                        "selector" : "node[ id = '6951' ]",
                                        "css" : {
                                            "height" : 55.0,
                                            "shape" :" roundrectangle ",
                                            "width" : 95.0,
                                            "background-opacity" : 0.19607843137254902
                                        }
                                    }, {
                                        "selector" : "node[ id = '6938' ]",
                                        "css" : {
                                            "height" : 145.0,
                                            "shape" :" roundrectangle ",
                                            "width" : 215.0,
                                            "background-opacity" : 0.19607843137254902
                                        }
                                    }, {
                                        "selector" : "node[ id = '6925' ]",
                                        "css" : {
                                            "height" : 55.0,
                                            "shape" :" roundrectangle ",
                                            "width" : 95.0,
                                            "background-opacity" : 0.19607843137254902
                                        }
                                    }, {
                                        "selector" : "node[ id = '6911' ]",
                                        "css" : {
                                            "height" : 181.0,
                                            "shape" :" roundrectangle ",
                                            "width" : 173.0,
                                            "background-opacity" : 0.19607843137254902
                                        }
                                    }, {
                                        "selector" : "node[ id = '6897' ]",
                                        "css" : {
                                            "height" : 259.0,
                                            "shape" :" roundrectangle ",
                                            "width" : 350.0,
                                            "background-opacity" : 0.19607843137254902
                                        }
                                    }, {
                                        "selector" : "node[ id = '6883' ]",
                                        "css" : {
                                            "height" : 120.0,
                                            "shape" :" roundrectangle ",
                                            "width" : 293.0,
                                            "background-opacity" : 0.19607843137254902
                                        }
                                    }, {
                                        "selector" : "node[ id = '6869' ]",
                                        "css" : {
                                            "height" : 171.0,
                                            "shape" :" roundrectangle ",
                                            "width" : 227.0,
                                            "background-opacity" : 0.19607843137254902
                                        }
                                    }, {
                                        "selector" : "node[ id = '6855' ]",
                                        "css" : {
                                            "height" : 95.0,
                                            "shape" :" roundrectangle ",
                                            "width" : 229.0,
                                            "background-opacity" : 0.19607843137254902
                                        }
                                    }, {
                                        "selector" : "node[ id = '6841' ]",
                                        "css" : {
                                            "height" : 165.0,
                                            "shape" :" roundrectangle ",
                                            "width" : 304.0,
                                            "background-opacity" : 0.19607843137254902
                                        }
                                    }, {
                                        "selector" : "node[ id = '6827' ]",
                                        "css" : {
                                            "height" : 280.0,
                                            "shape" :" roundrectangle ",
                                            "width" : 404.0,
                                            "background-opacity" : 0.19607843137254902
                                        }
                                    }, {
                                        "selector" : "node[ id = '6813' ]",
                                        "css" : {
                                            "height" : 55.0,
                                            "shape" :" roundrectangle ",
                                            "width" : 95.0,
                                            "background-opacity" : 0.19607843137254902
                                        }
                                    }, {
                                        "selector" : "node[ id = '6799' ]",
                                        "css" : {
                                            "height" : 192.0,
                                            "shape" :" roundrectangle ",
                                            "width" : 148.0,
                                            "background-opacity" : 0.19607843137254902
                                        }
                                    }, {
                                        "selector" : "node[ id = '6785' ]",
                                        "css" : {
                                            "height" : 235.0,
                                            "shape" :" roundrectangle ",
                                            "width" : 125.0,
                                            "background-opacity" : 0.19607843137254902
                                        }
                                    }, {
                                        "selector" : "node[ id = '6771' ]",
                                        "css" : {
                                            "height" : 55.0,
                                            "shape" :" roundrectangle ",
                                            "width" : 95.0,
                                            "background-opacity" : 0.19607843137254902
                                        }
                                    }, {
                                        "selector" : "node[ id = '6756' ]",
                                        "css" : {
                                            "height" : 109.0,
                                            "shape" :" roundrectangle ",
                                            "width" : 232.0,
                                            "background-opacity" : 0.19607843137254902
                                        }
                                    }, {
                                        "selector" : "node[ id = '6740' ]",
                                        "css" : {
                                            "height" : 252.0,
                                            "shape" :" roundrectangle ",
                                            "width" : 695.0,
                                            "background-opacity" : 0.19607843137254902
                                        }
                                    }, {
                                        "selector" : "node[ id = '6722' ]",
                                        "css" : {
                                            "height" : 335.0,
                                            "shape" :" roundrectangle ",
                                            "width" : 583.0,
                                            "background-opacity" : 0.19607843137254902
                                        }
                                    }, {
                                        "selector" : "node[ id = '6706' ]",
                                        "css" : {
                                            "height" : 257.0,
                                            "shape" :" roundrectangle ",
                                            "width" : 347.0,
                                            "background-opacity" : 0.19607843137254902
                                        }
                                    }, {
                                        "selector" : "node[ id = '6686' ]",
                                        "css" : {
                                            "height" : 401.0,
                                            "shape" :" roundrectangle ",
                                            "width" : 939.0,
                                            "background-opacity" : 0.19607843137254902
                                        }
                                    }]
} ]