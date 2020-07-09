# TestLinkKityEditor 在脑图上编辑testlink测试用例
摆脱testlink难用的操作界面，可以将Testlink用例及目录结构导出到脑图，在脑图中编辑后再导入testlink。

## 部署
只有个人使用的话，建议直接用flask环境部署。

一、安装python3环境
下载地址：https://www.python.org/downloads/
二、安装flask库：
        ```pip install flask```
三、安装testlink api库：
        ```pip install TestLink-API-Python-client```
四、下载本项目后，双击run.bat运行，或在命令行中执行：
        ```python app.py```
五、访问页面上显示的地址，如:http://127.0.0.1:5000

使用人数较多的话，需要正常部署，可参考：https://www.jianshu.com/p/d607ca5718a5
如有安全性上的考虑，建议启用https，可参考：https://blog.csdn.net/yannanxiu/article/details/70672744

## 使用说明
访问页面，点击右上角的问号可以查看使用说明