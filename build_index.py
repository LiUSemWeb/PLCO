#!/usr/bin/env python3
from pybars import Compiler
from glob import glob
import re
import logging
import sys
#from bs4 import BeautifulSoup, formatter
#import os
#import urllib.request
#import zipfile
#from pylode.profiles.vocpub import VocPub
#from rdflib import Graph

#from playwright.sync_api import sync_playwright
#import xml.etree.ElementTree
#import xml.dom.minidom

# Configure root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(format='%(levelname)-8s [%(filename)s:%(lineno)d] %(message)s', level=logging.DEBUG)


def create_index_file(index_file):
    print("Generating index file")
    compiler = Compiler()
    template_file = "index.hbs"
    #index_file = "docs/index.html"
    
    core = ["actorODP", "observation", "processODP", "product", "resourceODP",  "location"]
    
    core_actor = ["actorODP"]
    core_process = ["processODP"]
    core_resource = ["resourceODP", "product"]
    core_obsrvation = ["observation"]
    core_supplementary = ["location"]
    
    data = {
        "core": [],
        "other": [],
        "demo": [],
        "actor": [],
        "observation": [],
        "process": [],
        "resource": [],
        "supplementary": []
    }

    for type in ["modules", "demo"]:
        ontologies = {}
        for source in glob(f"ontology/{type}/*/*/*", recursive=True):
            if not source.endswith(".ttl"):
                continue
            parts = re.match(f"ontology/{type}/([^/]*)/([^/]*)", source)    
            name = parts.group(1)
            version = parts.group(2)
            
            if not ontologies.get(name):
                ontologies[name] = {
                    "name": name,
                    "versions": []
                }
            
            ontologies[name]["versions"].append(version)
            ontologies[name]["versions"].sort(reverse=True)
        
        # Split into core, other and demo
        for name in ontologies:
            ontology = {
                "name": name,
                "versions": ontologies[name]["versions"]
            }
            if type == "demo":
                data["demo"].append(ontology)
            else:
                if name in core:
                    data["core"].append(ontology)
                    # New added code below
                    if name in core_actor:
                        data["actor"].append(ontology)
                    if name in core_process:
                        data["process"].append(ontology)
                    if name in core_resource:
                        data["resource"].append(ontology)
                    if name in core_obsrvation:
                        data["observation"].append(ontology)
                    if name in core_supplementary:
                        data["supplementary"].append(ontology)
                else:
                    data["other"].append(ontology)

    for list in data.values():     
        list.sort(key=lambda x: x["name"])

    # sort by name ascending, version descending
    with open(template_file, "r") as f:
        template = compiler.compile(f.read())

    with open(index_file, "w") as f:
        f.write(template({"data": data}))
        

def main():
    if len(sys.argv) > 1:
        index_file = sys.argv[1]
    else:
        index_file = 'docs/index.html'
        
    create_index_file(index_file)

if __name__ == "__main__":
    main()
