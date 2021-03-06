#-*-coding:utf-8-*-
#__author__='maxiaohui'
from utils import apitest,filesHandler
import re
import datetime,time,os
from config import config
from adb import deviceHandler

todayTag=datetime.datetime.fromtimestamp(time.time()).strftime('%m%d')
print(todayTag)

def downloadLatestDailyBuild():
    method = "get"
    url = "/rom_new/dailybuild/"
    swHost = "http://192.168.100.136:8000"

    html = apitest.testAPI(method, url, host=swHost).text
    latestBuild=re.findall(r'<a.*?href=.*?>(.*?)<\/a>(.*)-\r',html)
    for i in latestBuild:
        try:
            if re.findall(r'\d{8}',i[0])[0][:4]==todayTag:
                latestBuild=i[0]
                break
        except IndexError:
            pass
    if isinstance(latestBuild,list):
        print("没有当天的最新build")
        otaFile=""
    else:
        url=url+latestBuild+"OTA/"
        html = apitest.testAPI(method, url, host=swHost).text
        try:
            downloadBuild = re.findall(r'<a.*?href=.*?>(.*?ota.zip)<\/a>', html)[0]
            otaFile = config.log_path + "\\" + downloadBuild
        #在当前目录中查找文件downloadBuild，如果有改文件，无需下载，如果没有再去下载
            if not filesHandler.search(config.log_path, downloadBuild):
                url=url+downloadBuild
                #执行下载
                print("开始下载文件，请等待。。。")
                res=apitest.testAPI(method, url, host=swHost)
                res.raise_for_status()
                newfile = open(otaFile, 'wb')  # 本地文件
                for chunk in res.iter_content(10240     ):
                    newfile.write(chunk)
                newfile.close()
            print("下载完成")
            return otaFile
        except IndexError:
            print("无升级软件")
            return False

def pushDailyBuild(deviceId):
    file=downloadLatestDailyBuild()
    if file:
        deviceHandler.checkConnected(deviceId)
        deviceHandler.pushOtaFile(file)
    return file
if __name__ == "__main__":  #当前脚本运行实例
    pushDailyBuild(config.deviceId)