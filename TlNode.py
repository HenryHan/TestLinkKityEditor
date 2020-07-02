from testlink import testlinkerrors
class TlNode():
    def __init__(self,id=None,name=None,type="unknown"):
        self.id = id
        self.name = name
        self.type = type
        self.prefix=""
        self.parent_id=None
        self.project_id=None
        self.author=None
        self.cur_count=0
        self.cur_depth=0
        self.children = []
        self.preview=[]

    def to_km(self):
        out = {"data":{},"children":[]}
        out["data"]["internal_id"]=self.id
        out["data"]["type"]=self.type
        out["data"]["text"]=self.name
        out["data"]["priority"]=1
        for child in self.children:
            out["children"].append(child.to_km())
        return out

    def to_tree(self):
        return {"id":self.id,"text":self.name,"state":"closed"}

    def get_children(self,tls,depth):
        return []

    def judge_type(self,data):
        type = "suite"
        if "type" in data["data"].keys():
            type = data["data"]["type"]
        else:
            for c in data["children"]:
                if c["data"]["text"]=="steps":
                    type = "case"
        if type=="case":
            return Case()
        elif type == "suite":
            return Suite()
        elif type == "project":
            return Project()
        else:
            raise "未找到类型"

    def from_km(self,data):
        if "internal_id" in data["data"].keys():
            self.id = data["data"]["internal_id"]
        self.name=data["data"]["text"]
        for child in data["children"]:
            node = self.judge_type(child)
            node.parent_id=self.id
            node.project_id=self.project_id
            node.author=self.author
            node.prefix=self.prefix
            node.from_km(child)
            self.children.append(node)

    def to_testlink(self,tls,is_preview):
        preview=[]
        if not self.id:
            preview.append({"type":"目录","name":self.name,"result":"新增"})
            if not is_preview:
                info = tls.createTestSuite(checkduplicatedname=False,parentid=self.parent_id,testsuitename=self.name,prefix=self.prefix)
                for child in self.children:
                    child.parent_id= info[0]["id"]         
        else:
            suite = tls.getTestSuiteByID(self.id)
            if self.name != suite["name"]:
                preview.append({"type":"目录","name":self.name,"result":"修改"})
                if not is_preview:
                    tls.updateTestSuite(testsuiteid=self.id,testsuitename=self.name,prefix=self.prefix)
        for child in self.children:
            preview+=child.to_testlink(tls,is_preview)
        return preview


class Project(TlNode):
    def __init__(self,id=None,name=None):
        TlNode.__init__(self,id,name)
        self.type="project"

    def get_children(self,tls,depth):
        if self.cur_depth>=depth:
            return []
        suites = tls.getFirstLevelTestSuitesForTestProject(self.id)
        for suite in suites:
            node = Suite(suite["id"],suite["name"])
            node.cur_depth=self.cur_depth+1
            node.prefix=self.prefix
            self.children.append(node)
            node.get_children(tls,depth)
    
    def to_testlink(self,tls,is_preview):
        preview=[]
        for child in self.children:
            preview+=child.to_testlink(tls,is_preview)
        return preview
    

class Suite(TlNode):
    def __init__(self,id=None,name=None):
        TlNode.__init__(self,id,name)
        self.type="suite"
    def get_children(self,tls,depth):
        if self.cur_depth>=depth:
            return []
        suites = tls.getTestSuitesForTestSuite(self.id)
        cases = tls.getTestCasesForTestSuite(self.id,False,"full")
        if type(suites) is dict:
                if "id" in suites.keys():
                    node = Suite(suites["id"],suites["name"])
                    node.cur_depth=self.cur_depth+1
                    node.prefix=self.prefix
                    self.children.append(node)
                    node.get_children(tls,depth)
                else:
                    for key in suites.keys():
                        node = Suite(suites[key]["id"],suites[key]["name"])
                        node.cur_depth=self.cur_depth+1
                        node.prefix=self.prefix
                        self.children.append(node)
                        node.get_children(tls,depth)
        else:
            for suite in suites:
                node = Suite(suite["id"],suite["name"])
                node.prefix=self.prefix
                node.cur_depth=self.cur_depth+1
                self.children.append(node)
                node.get_children(tls,depth)
        for case in cases:      
            node = Case(case["id"],case["name"])
            node.preconditions = remove_tags(case["preconditions"])
            node.summary = remove_tags(case["summary"])
            node.importance =case["importance"]
            node.steps = case["steps"]
            node.cur_depth=self.cur_depth+1
            node.prefix=self.prefix
            node.tc_external_id = case["tc_external_id"]
            self.children.append(node)

class Case(TlNode):
    def __init__(self,id=None,name=None):
        TlNode.__init__(self,id,name)
        self.type="case"
        self.tc_external_id=""
        self.prefix=""
        self.summary=""
        self.importance="2"
        self.preconditions=""
        self.steps=[]
        
    def get_display_name(self):
        return self.prefix+"-"+self.tc_external_id+":"+self.name

    def to_tree(self):
        return {"id":self.id,"text":self.get_display_name()}

    def to_km(self):
        out=TlNode.to_km(self)
        out["data"]["text"]=self.get_display_name()
        out["data"]["priority"]=9
        if self.cur_depth>1:
            out["data"]["expandState"]="collapse"
        summary = {"data":{"text":"summary"},"children":[{"data":{"text":self.summary}}]}
        preconditions = {"data":{"text":"preconditions"},"children":[{"data":{"text":self.preconditions}}]}
        importance = {"data":{"text":"importance"},"children":[{"data":{"text":self.importance}}]}
        step_descriptions = []
        for step in self.steps:
            step_description = {"data":{"text":remove_tags(step["actions"])},"children":[]}
            if step["expected_results"]:
                step_description["children"].append({"data":{"text":remove_tags(step["expected_results"])},"children":[]})
            step_descriptions.append(step_description)
        steps={"data":{"text":"steps"},"children":step_descriptions}
        out["children"].append(summary)
        out["children"].append(preconditions)
        out["children"].append(importance)
        out["children"].append(steps)
        return out

    def from_km(self,data):
        if "internal_id" in data["data"].keys():
            self.id = data["data"]["internal_id"]
        self.name = data["data"]["text"].split(":")[-1]
        case_details = data["children"]
        for c in case_details:
            if c["data"]["text"]=="summary":
                self.summary = "" if len(c["children"])==0 else c["children"][0]["data"]["text"]
            if c["data"]["text"]=="preconditions":
                self.preconditions = "" if len(c["children"])==0 else c["children"][0]["data"]["text"]
            if c["data"]["text"]=="importance":
                self.importance = "2" if len(c["children"])==0 else c["children"][0]["data"]["text"]
            if c["data"]["text"]=="steps":
                n=1
                for step in c["children"]:
                    actions = step["data"]["text"]
                    step_number=n
                    n+=1
                    expected_results = step["children"][0]["data"]["text"] if len(step["children"])>0 else ""
                    self.steps.append({"actions":actions,"step_number":step_number,"expected_results":expected_results})
        
    def to_testlink(self,tls,is_preview):
        preview=[]
        if not self.id:
            preview.append({"type":"测试用例","name":self.name,"result":"新增"})
            if not is_preview:
                info=tls.createTestCase(testsuiteid=self.parent_id,testcasename=self.name,testprojectid=self.project_id,authorlogin=self.author,preconditions=self.preconditions,importance=self.importance,summary=self.summary,steps=self.steps)
                print(info)
        else:
            case = tls.getTestCase(self.id)[0]
            rs=""
            if case["testsuite_id"]!=self.parent_id and self.parent_id:
                rs += "移动"
                if not is_preview:
                    tls.setTestCaseTestSuite(testsuiteid=self.parent_id,testcaseexternalid=case["full_tc_external_id"])
            modify = " 修改："
            if self.name != case["name"]:
                modify+="name,"
            if self.summary != case["summary"]:
                modify+="summary,"
            if self.importance != case["importance"]:
                modify+="importance,"
            if self.preconditions != case["preconditions"]:
                modify+="preconditions,"
            all_steps_same = True
            if len(self.steps) == len(case["steps"]):
                for i in range(len(self.steps)):
                    n_step=self.steps[i]["actions"]
                    c_step = case["steps"][i]["actions"]
                    n_num = str(self.steps[i]["step_number"])
                    c_num = case["steps"][i]["step_number"]
                    n_rs = self.steps[i]["expected_results"]
                    c_rs = case["steps"][i]["expected_results"]
                    if n_step!=c_step or n_num!=c_num or n_rs!=c_rs:
                        all_steps_same=False
            else:
                all_steps_same=False
            if not all_steps_same:
                modify+="steps,"
            if modify != " 修改：":
                rs+=modify.strip(",")
                if not is_preview:
                    tls.updateTestCase(testcaseexternalid=case["full_tc_external_id"],testcasename=self.name,importance=self.importance,summary=self.summary,preconditions=self.preconditions,steps=self.steps,prefix=self.prefix)
            if rs:
                preview.append({"type":"测试用例","name":self.name,"result":rs})
        return preview


def remove_tags(text):
    lines = [x.strip() for x in text.split() if x.strip()]
    result=[]
    for line in lines:
        try:
            striped = ''.join(xml.etree.ElementTree.fromstring(line).itertext())
            result.append(striped)
        except:
            striped= line
            if line.startswith("<p>"):
                striped= line[3:]
            if line.endswith("</p>"):
                striped= line[:len(line)-4]
            result.append(striped)
    return "\n".join(result)
