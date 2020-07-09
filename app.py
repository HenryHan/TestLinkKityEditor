import flask
import json
import traceback
from Converter import Converter

app = flask.Flask(__name__,static_folder='static')

tlp_map = {}

def get_converter(tl_url,tl_token,project_id="9999999999",user_name=None):
    key = tl_token+project_id
    if key not in tlp_map.keys():
        tlp_map[key] = Converter(tl_url,tl_token,project_id,user_name)
    return tlp_map[key]


@app.route('/')
def hello_world():
    return flask.render_template("index.html")

@app.route('/get_project_list',methods=['GET', 'POST'])
def get_project_list():
    tl_url = flask.request.args.get('tl_url', None)
    tl_token = flask.request.args.get('tl_token', None)
    converter = get_converter(tl_url,tl_token)
    return converter.get_projects()

@app.route('/update', methods=['GET', 'POST'])
def update():
    data=flask.request.get_json()
    tl_url=data["tl_url"]
    tl_token=data["tl_token"]
    project_id=data["project_id"]
    user_name=data["user_name"]
    is_preview = data["is_preview"] if "is_preview" in data.keys() else None
    converter=get_converter(tl_url,tl_token,project_id,user_name)
    converter.get_km_nodes(data["data"])
    return converter.save_to_testlink(is_preview)

@app.route('/tree_nodes')
def get_tree_nodes():
    tl_url = flask.request.args.get('tl_url', None)
    tl_token = flask.request.args.get('tl_token', None)
    project_id = flask.request.args.get('project_id', None)
    user_name = flask.request.args.get('user_name', None)
    if tl_url and tl_token and project_id:
        try:
            key = flask.request.args.get('id', None)
            converter=get_converter(tl_url,tl_token,project_id,user_name)
            converter.get_tl_nodes(key,2)
            result = converter.to_tree_node(key)
            if not result:
                errorinfo={'error':'未找到节点信息，请确认配置正确'}
            else:
                return result
        except Exception as e:
            errorinfo={"error":("出现错误：%s" % e)}
    else:
        errorinfo={"error":"缺少testlink配置信息，请先配置"}
    return errorinfo
    
@app.route('/get_km')
def get_km():
    key = flask.request.args.get('id', None)
    tl_url = flask.request.args.get('tl_url', None)
    tl_token = flask.request.args.get('tl_token', None)
    project_id = flask.request.args.get('project_id', None)
    depth = flask.request.args.get('depth', 1)
    converter=get_converter(tl_url,tl_token,project_id)
    converter.get_tl_nodes(key,int(depth))
    return converter.export_to_km()
 
if __name__ == '__main__':
    app.run(host="0.0.0.0",threaded=True)