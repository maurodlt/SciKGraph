# SciKGraph
Web Application to assist researchers in understanding Scientific Fields using Knowledge Graph visualization

## To use application:

Install Cytoscape version 3.7.2: https://cytoscape.org/download_old_versions.html

Register on BabelNet: https://babelnet.org/register

Install ScikGrapp-App: pip3 install scikgraph

Install server: sudo apt install python3-waitress

## To start application:

Open Cytoscape application.

Run: waitress-serve --call 'scikgraph:create_app'



# License
Academic and Personal use and modification is permitted. For commercial use, please contact us. 


# Cite us
https://doi.org/10.1177/0165551520937915

https://doi.org/10.1016/j.joi.2020.101109

@article{scikgraphApp-Tosi,
author = {Mauro Dalle Lucca Tosi and Julio Cesar dos Reis},
title ={Understanding the evolution of a scientific field by clustering and visualizing knowledge graphs},
journal = {Journal of Information Science},
volume = {0},
number = {0},
pages = {0165551520937915},
year = {0},
doi = {10.1177/0165551520937915}
URL = {https://doi.org/10.1177/0165551520937915}
}

@article{tosi2021scikgraph,
  title={SciKGraph: A knowledge graph approach to structure a scientific field},
  author={Tosi, Mauro Dalle Lucca and dos Reis, Julio Cesar},
  journal={Journal of Informetrics},
  volume={15},
  number={1},
  pages={101109},
  year={2021},
  publisher={Elsevier}
}


