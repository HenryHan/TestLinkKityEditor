import flask
import json
import traceback
from Converter import Converter

app = flask.Flask(__name__,static_folder='static')

tlp_map = {}

@app.route('/')
def hello_world():
    return flask.render_template("index.html")

@app.route('/update', methods=['GET', 'POST'])
def update():
    data=flask.request.get_json()
    tl_token=data["tl_token"]
    is_preview = data["is_preview"] if "is_preview" in data.keys() else None
    tlp_map[tl_token].get_km_nodes(data["data"])
    return tlp_map[tl_token].save_to_testlink(is_preview)

@app.route('/tree_nodes')
def get_tree_nodes():
    tl_url = flask.request.args.get('tl_url', None)
    tl_token = flask.request.args.get('tl_token', None)
    project_id = flask.request.args.get('project_id', None)
    user_name = flask.request.args.get('user_name', None)
    if tl_url and tl_token and project_id:
        try:
            key = flask.request.args.get('id', None)
            if tl_token not in tlp_map.keys():
                tlp_map[tl_token] = Converter(tl_url,tl_token,project_id,user_name)
            tlp_map[tl_token].get_tl_nodes(key,2)
            result = tlp_map[tl_token].to_tree_node()
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
    tl_token = flask.request.args.get('tl_token', None)
    depth = flask.request.args.get('depth', 1)
    tlp_map[tl_token].get_tl_nodes(key,int(depth))
    return tlp_map[tl_token].export_to_km()
 
if __name__ == '__main__':
    app.run(host="0.0.0.0",threaded=True)