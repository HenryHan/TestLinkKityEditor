from TlNode import Project,Suite,Case,remove_tags,TlNode
from testlink import TestlinkAPIClient, TestLinkHelper, TestGenReporter, testlinkerrors
import json
import xml.etree.ElementTree

class Converter():
    def __init__(self,url="",key="",projectid="",user_name=None):
        self.tree = []
        self.top=None
        self.tls = TestlinkAPIClient(url, key)
        self.projectid=projectid
        self.user_name = user_name
        projects = self.tls.getProjects()
        for project in projects:
            if project["id"] == self.projectid:
                self.project = Project(self.projectid,project["name"])
                self.project.prefix=project["prefix"]

    def get_tl_nodes(self,id=None,depth=3):
        self.top=None
        node = None
        if not id or id==self.projectid:
            node = Project(self.projectid,self.project.name)
        else:
            try:
                suite = self.tls.getTestSuiteByID(id)
                node = Suite(suite["id"],suite["name"])
                node.prefix=self.project.prefix
            except testlinkerrors.TLResponseError:
                case = self.tls.getTestCase(id)[0]
                node = Case(case["testcase_id"],case["name"])
                node.preconditions = remove_tags(case["preconditions"])
                node.summary = remove_tags(case["summary"])
                node.importance = case["importance"]
                node.steps = case["steps"]
                node.tc_external_id = case["tc_external_id"]
                node.prefix=self.project.prefix
        self.top=node
        if node:
            node.cur_depth=1
            node.get_children(self.tls,depth)

    def to_tree_node(self):
        results = []
        if self.top:
            if self.top.id == self.projectid:
                node = self.top.to_tree()
                node["children"]=[]
                for child in self.top.children:
                    node["children"].append(child.to_tree())
                results.append(node)
            else:
                for child in self.top.children:
                    results.append(child.to_tree())
        return json.dumps(results)

    def export_to_km(self):
        out = {	"root":{},
            "template": "right",
	        "theme": "classic-compact"
            }
        out["root"]=self.top.to_km()
        return out

    def get_km_nodes(self,km):
        self.top=None
        self.top = TlNode().judge_type(km["root"])
        self.top.project_id=self.projectid
        self.top.prefix=self.project.prefix
        self.top.author=self.user_name
        self.top.from_km(km["root"])


    def save_to_testlink(self,is_preview):
        results=self.top.to_testlink(self.tls,is_preview)
        return json.dumps(results)
        
            

if __name__ == "__main__":
    c = Converter()
    c.get_tl_nodes("503444",1)


    


            

