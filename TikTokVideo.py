#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 开发人员  :  chengc
# 开发时间  :  2021/7/5 20:29
# 文件名称  :  TikTokVideo.py
# 开发工具  :  PyCharm

import os
import re
import sys
import wget
import json
import requests
import urllib.parse
from PyQt5.QtWidgets import *


class MainWidgets(QMainWindow):
    def __init__(self):
        self.tikTok = TikTokLinkParse()
        self.videoPath = ""
        self.musicPath = ""
        super(MainWidgets, self).__init__()
        self.initUI()

    def initUI(self):
        self.resize(800, 600)
        self.setWindowTitle('抖音视频下载器')
        self.stateBar = self.statusBar()
        self.setStatusBar(self.stateBar)

        # 垂直布局
        widget = QWidget()
        v_layout = QVBoxLayout()

        # 水平布局 下载地址
        h_layout = QHBoxLayout()
        self.downloadPath = QLineEdit()
        self.downloadPath.setPlaceholderText('下载目录')
        self.pathBtn = QPushButton('选择目录')
        self.pathBtn.clicked.connect(self.selectDownloadPath)
        h_layout.addWidget(self.downloadPath)
        h_layout.addWidget(self.pathBtn)
        v_layout.addLayout(h_layout)

        # 分享链接输入框
        self.shareLinkEdit = QTextEdit()
        self.shareLinkEdit.setPlaceholderText('请输入抖音的分享链接')
        v_layout.addWidget(self.shareLinkEdit)

        self.parseLinkBtn = QPushButton('解析地址')
        self.parseLinkBtn.clicked.connect(self.parseLink)
        v_layout.addWidget(self.parseLinkBtn)

        # 水平布局 显示解析出的视频地址
        h_layout = QHBoxLayout()
        self.videoLinkNoWm = QLineEdit('此处显示视频的无水印地址')
        self.videoBtnNoWm = QPushButton('复制视频地址')
        self.videoBtnNoWm.setDisabled(True)
        self.videoBtnNoWm.clicked.connect(self.copyVideoUrl)
        h_layout.addWidget(self.videoLinkNoWm)
        h_layout.addWidget(self.videoBtnNoWm)
        v_layout.addLayout(h_layout)

        # 水平布局 显示视频背景音乐的地址
        h_layout = QHBoxLayout()
        self.musicLink = QLineEdit('此处显示视频背景音乐的地址')
        self.musicBtn = QPushButton('复制音乐地址')
        self.musicBtn.setDisabled(True)
        self.musicBtn.clicked.connect(self.copyMusicUrl)
        h_layout.addWidget(self.musicLink)
        h_layout.addWidget(self.musicBtn)
        v_layout.addLayout(h_layout)

        # 水平布局，显示现在按钮
        self.videoDownloadBtn = QPushButton('下载视频')
        self.musicDownloadBtn = QPushButton('下载背景音乐')
        self.videoDownloadBtn.setDisabled(True)
        self.musicDownloadBtn.setDisabled(True)
        self.videoDownloadBtn.clicked.connect(self.downloadVideoEvent)
        self.musicDownloadBtn.clicked.connect(self.downloadMusicEvent)
        v_layout.addWidget(self.videoDownloadBtn)
        v_layout.addWidget(self.musicDownloadBtn)

        # 设置布局并显示widget
        widget.setLayout(v_layout)
        self.setCentralWidget(widget)

    def selectDownloadPath(self):
        path = QFileDialog.getExistingDirectory()
        # path = QFileDialog.getExistingDirectory(directory=r'F:/04-影音视频')
        if path != "":
            path = path + "/TikTok"
            if not os.path.exists(path):
                os.mkdir(path)
            self.downloadPath.setText(path)

            self.videoPath = path + "/video"
            self.musicPath = path + "/music"

            if not os.path.exists(self.videoPath):
                os.mkdir(self.videoPath)

            if not os.path.exists(self.musicPath):
                os.mkdir(self.musicPath)

    def parseLink(self):
        shareLink = self.shareLinkEdit.toPlainText()
        if "" == shareLink:
            QMessageBox.warning(self, "警告", "分享链接不能为空")
            return None

        self.tikTok.setShareLink(shareLink)
        urllist = self.tikTok.getVideoItemInfo()
        if urllist is None:
            QMessageBox.warning(self, "警告", "链接解析出错")
            return None
        else:
            self.videoLinkNoWm.setText(urllist['videoUrl'])
            self.musicLink.setText(urllist['musicUrl'])
            self.musicBtn.setDisabled(False)
            self.videoBtnNoWm.setDisabled(False)
            self.videoDownloadBtn.setDisabled(False)
            self.musicDownloadBtn.setDisabled(False)

    def copyVideoUrl(self):
        clipBoard = QApplication.clipboard()
        clipBoard.setText(self.videoLinkNoWm.text())
        self.stateBar.showMessage(self, "复制成功", 3000)

    def copyMusicUrl(self):
        clipBoard = QApplication.clipboard()
        clipBoard.setText(self.musicLink.text())
        self.stateBar.showMessage(self, "复制成功", 3000)

    def downloadVideoEvent(self):
        if "" == self.videoPath:
            QMessageBox.warning(self, "警告", "下载目录不能为空")
            return False

        videoUrl = self.videoLinkNoWm.text()
        if "" == videoUrl:
            QMessageBox.warning(self, "警告", "视频下载地址为空，请先解析地址")
            return False

        result = self.tikTok.downloadVideo(self.videoPath)
        if result:
            self.stateBar.showMessage("视频下载成功", 5000)
            self.videoDownloadBtn.setDisabled(True)

    def downloadMusicEvent(self):
        if "" == self.musicPath:
            QMessageBox.warning(self, "警告", "下载目录不能为空")
            return False

        musicUrl = self.videoLinkNoWm.text()
        if "" == musicUrl:
            QMessageBox.warning(self, "警告", "音乐下载地址为空，请先解析地址")
            return False

        result = self.tikTok.downloadMusic(self.musicPath)
        if result:
            self.stateBar.showMessage("音乐下载成功", 5000)
            self.musicDownloadBtn.setDisabled(True)


class TikTokLinkParse:
    def __init__(self):
        self.winHeader = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.videoUri = ""
        self.urllist = {}
        self.tikTokShareLink = ""

    def setShareLink(self, link):
        self.tikTokShareLink = link

    def getTikTokUrl(self):
        compile = re.compile(r"(https?|http?)://(\w|\.|/|\?|&|=)+")
        try:
            url = re.search(compile, self.tikTokShareLink).group()
        except AttributeError as e:
            print("[Error getTikTokUrl]", e)
            return None
        else:
            return url

    def getVideoID(self):
        shareUrl = self.getTikTokUrl()
        if shareUrl is not None:
            try:
                response = requests.get(url=shareUrl, timeout=5, headers=self.winHeader, allow_redirects=False)
            except requests.exceptions as e:
                print(e)
                return None
            else:
                if response.status_code == 302:
                    try:
                        location = response.headers['location']
                    except Exception as e:
                        print("[Error getVideoID]", e)
                        return None
                    else:
                        result = urllib.parse.urlsplit(location)
                        path = result.path
                        pathSpilt = path.split('/')
                        try:
                            return pathSpilt[-2]
                        except TypeError as e:
                            print(e)
                            return None

    def getVideoItemInfo(self):
        self.urllist = {}
        videoID = self.getVideoID()
        if videoID is not None:
            videoInfoLink = "https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={}".format(videoID)
            try:
                response = requests.get(url=videoInfoLink, timeout=5, headers=self.winHeader)
            except Exception as e:
                print("[Error getVideoItemInfo]", e)
                return None
            else:
                itemInfo = json.loads(response.text)
                videoInfo = itemInfo["item_list"][0]["video"]
                musicInfo = itemInfo["item_list"][0]["music"]

                musicUrl = musicInfo["play_url"]["url_list"][0]
                videoUrl = videoInfo["play_addr"]["url_list"][0]
                videoUrl = videoUrl.replace("playwm", "play")
                videoUri = videoInfo["play_addr"]["uri"]
                self.videoUri = videoUri
                self.urllist['musicUrl'] = musicUrl
                self.urllist["videoUrl"] = videoUrl
                return self.urllist

    def downloadVideo(self, path):
        videoUrl = self.urllist['videoUrl']
        filename = path + "/" + self.videoUri + ".mp4"
        if "" == videoUrl:
            return False

        try:
            response = requests.get(url=videoUrl, timeout=5, headers=self.winHeader, allow_redirects=False)
        except Exception as e:
            print("[Error downloadVideo]", e)
            return False
        else:
            try:
                location = response.headers['location']
            except Exception as e:
                print("[Error downloadVideo]", e)
                return None
            else:
                filename = wget.download(url=location, out=filename)
                if filename is not None:
                    return True
                else:
                    return False

    def downloadMusic(self, path):
        musicUrl = self.urllist['musicUrl']
        filename = path + "/" + self.videoUri + ".mp3"
        if "" == musicUrl:
            return False

        filename = wget.download(url=musicUrl, out=filename)
        if filename is not None:
            return True
        else:
            return False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWidgets()
    mainWin.show()
    sys.exit(app.exec_())
