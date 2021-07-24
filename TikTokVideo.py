#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 开发团队  :  chengc
# 开发人员  :  chengc
# 开发时间  :  2021/7/24 17:15
# 文件名称  :  TikTok.py
# 开发工具  :  PyCharm

import os
import re
import sys
import json
import logging
import urllib.parse

import requests
from PyQt5.QtWidgets import *


def DownloadFile(url, path):
    if path == "" or url == "":
        return False

    winHeader = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url=url, headers=winHeader, allow_redirects=True, stream=True)
    except requests.exceptions as e:
        logging.error(e)
        return False
    else:
        total_size = int(response.headers['Content-Length'])
        if total_size == 0:
            return False
        with open(path, "wb") as f:
            for chunk in response.iter_content(chunk_size=102400):
                if chunk:
                    f.write(chunk)
        return True


class TikTokUI(QMainWindow):
    def __init__(self):
        super(TikTokUI, self).__init__()
        self.InitUI()
        self.save_path = None
        self.item_info = None
        self.videoPath = None
        self.musicPath = None
        self.imagesPath = None
        self.TikTok = TikTokLinkParse()

    def InitUI(self):
        self.setWindowTitle('抖音视频无水印下载器')
        self.resize(800, 600)
        # 状态栏
        self.stateBar = self.statusBar()
        self.setStatusBar(self.stateBar)

        # 主布局，是一个纵向布局
        main_layout = QVBoxLayout()

        # 子布局，横向布局
        h_layout = QHBoxLayout()
        self.pathInputEdit = QLineEdit()
        self.pathInputEdit.setPlaceholderText('请先设置保存路径')
        self.selectPathBtn = QPushButton("选择目录")
        self.selectPathBtn.clicked.connect(self.eventSelectSavePath)
        h_layout.addWidget(self.pathInputEdit)
        h_layout.addWidget(self.selectPathBtn)
        main_layout.addLayout(h_layout)

        self.shareLinkEdit = QTextEdit()
        self.shareLinkEdit.setPlaceholderText('在此处输入抖音视频的分享链接')
        main_layout.addWidget(self.shareLinkEdit)

        self.parseShareLinkBtn = QPushButton("解析链接")
        self.parseShareLinkBtn.clicked.connect(self.eventParseShareLink)
        main_layout.addWidget(self.parseShareLinkBtn)

        h_layout = QHBoxLayout()
        self.videoLinkEdit = QLineEdit()
        self.videoLinkEdit.setPlaceholderText('此处将显示视频真实下载地址')
        self.copyVideoLinkBtn = QPushButton('复制视频下载地址')
        self.copyVideoLinkBtn.clicked.connect(self.eventCopyVideoLink)
        h_layout.addWidget(self.videoLinkEdit)
        h_layout.addWidget(self.copyVideoLinkBtn)
        main_layout.addLayout(h_layout)

        h_layout = QHBoxLayout()
        self.musicLinkEdit = QLineEdit()
        self.musicLinkEdit.setPlaceholderText('此处将显示背景音乐下载地址')
        self.copyMusicLinkBtn = QPushButton('复制音乐下载地址')
        self.copyMusicLinkBtn.clicked.connect(self.eventCopyMusicLink)
        h_layout.addWidget(self.musicLinkEdit)
        h_layout.addWidget(self.copyMusicLinkBtn)
        main_layout.addLayout(h_layout)

        self.downloadVideoBtn = QPushButton('下载视频')
        self.downloadVideoBtn.setDisabled(True)
        self.downloadVideoBtn.clicked.connect(self.eventDownloadVideo)
        main_layout.addWidget(self.downloadVideoBtn)

        self.downloadMusicBtn = QPushButton('下载背景音乐')
        self.downloadMusicBtn.setDisabled(True)
        self.downloadMusicBtn.clicked.connect(self.eventDownloadMisuc)
        main_layout.addWidget(self.downloadMusicBtn)

        self.downloadImageBtn = QPushButton('下载图集')
        self.downloadImageBtn.setDisabled(True)
        self.downloadImageBtn.clicked.connect(self.eventDownloadImage)
        main_layout.addWidget(self.downloadImageBtn)

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

    def eventCopyVideoLink(self):
        clipBoard = QApplication.clipboard()
        clipBoard.setText(self.videoLinkEdit.text())
        self.stateBar.showMessage("复制视频下载地址成功", 3000)

    def eventCopyMusicLink(self):
        clipBoard = QApplication.clipboard()
        clipBoard.setText(self.musicLinkEdit.text())
        self.stateBar.showMessage("复制视频下载地址成功", 3000)

    def eventSelectSavePath(self):
        self.save_path = QFileDialog.getExistingDirectory()
        if self.save_path != "":
            path = self.save_path + "/抖音"
            if not os.path.exists(path):
                os.mkdir(path)
            self.pathInputEdit.setText(path)

            self.videoPath = path + "/视频"
            self.musicPath = path + "/音乐"
            self.imagesPath = path + "/图片"

            if not os.path.exists(self.videoPath):
                os.mkdir(self.videoPath)

            if not os.path.exists(self.musicPath):
                os.mkdir(self.musicPath)

            if not os.path.exists(self.imagesPath):
                os.mkdir(self.imagesPath)

    def eventParseShareLink(self):
        linkText = self.shareLinkEdit.toPlainText()
        if linkText == "":
            self.stateBar.showMessage("链接不能为空", 3000)
        else:
            self.TikTok.setShareLink(linkText)
            self.item_info = self.TikTok.getVideoItemInfo()
            if self.item_info['video_url'] is not None:
                self.downloadVideoBtn.setDisabled(False)
                self.videoLinkEdit.setText(self.item_info['video_url'])

            if self.item_info['music_url'] is not None:
                self.downloadMusicBtn.setDisabled(False)
                self.musicLinkEdit.setText(self.item_info['music_url'])

            if self.item_info['image_list'] is not None:
                self.downloadImageBtn.setDisabled(False)

    def eventDownloadVideo(self):
        if self.save_path is None:
            QMessageBox.warning(self, "警告", "下载目录不能为空")
        else:
            mid = self.item_info['mid']
            video_url = self.item_info['video_url']
            if mid is not None:
                filename = "{}/{}.mp4".format(self.videoPath, mid)
                if os.path.isfile(filename):
                    self.stateBar.showMessage("视频文件已经存在", 3000)
                else:
                    reslut = DownloadFile(video_url, filename)
                    if reslut:
                        self.stateBar.showMessage("视频下载成功", 3000)
                    else:
                        self.stateBar.showMessage("视频下载失败", 3000)
            else:
                self.stateBar.showMessage("视频信息错误", 3000)
        self.downloadVideoBtn.setDisabled(True)

    def eventDownloadMisuc(self):
        if self.save_path is None:
            QMessageBox.warning(self, "警告", "下载目录不能为空")
        else:
            mid = self.item_info['mid']
            music_url = self.item_info['music_url']
            if mid is not None:
                filename = "{}/{}.mp3".format(self.musicPath, mid)
                if os.path.isfile(filename):
                    self.stateBar.showMessage("音乐文件已经存在", 3000)
                else:
                    reslut = DownloadFile(music_url, filename)
                    if reslut:
                        self.stateBar.showMessage("背景音乐下载成功", 3000)
                    else:
                        self.stateBar.showMessage("背景音乐下载失败", 3000)
            else:
                self.stateBar.showMessage("音乐信息错误", 3000)
        self.downloadMusicBtn.setDisabled(True)

    def eventDownloadImage(self):
        if self.save_path is None:
            QMessageBox.warning(self, "警告", "下载目录不能为空")
        else:
            image_list = self.item_info['image_list']
            image_num = len(image_list)
            for i in range(image_num):
                image_url = image_list[i][1]
                filename = "{}/{}.jpg".format(self.imagesPath, image_list[i][0])
                if os.path.isfile(filename):
                    self.stateBar.showMessage("图片已经存在", 3000)
                else:
                    reslut = DownloadFile(image_url, filename)
                    if reslut:
                        info = "共{}张图片，第{}张下载成功".format(image_num, i + 1)
                        self.stateBar.showMessage(info)
                    else:
                        info = "共{}张图片，第{}张下载失败".format(image_num, i + 1)
                        self.stateBar.showMessage(info)
        self.downloadImageBtn.setDisabled(True)


class TikTokLinkParse:
    def __init__(self):
        self.winHeader = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.tikTokShareLink = ""

    def setShareLink(self, link):
        self.tikTokShareLink = link

    def getShareLink(self):
        link = None
        compile = re.compile(r"(https?|http?)://(\w|\.|/|\?|&|=)+")
        try:
            link = re.search(compile, self.tikTokShareLink).group()
        except AttributeError as e:
            logging.error(e)
        finally:
            return link

    def getTikTokMid(self):
        mid = None
        link = self.getShareLink()
        if link is not None:
            try:
                response = requests.get(url=link, headers=self.winHeader, allow_redirects=False)
            except requests.exceptions as e:
                logging.error(e)
            finally:
                if response.status_code == 302:
                    Location = response.headers['Location']
                    path = urllib.parse.urlsplit(Location).path
                    pathSplit = path.split('/')
                    try:
                        mid = pathSplit[-2]
                    except IndexError as e:
                        logging.error("获取视频 mid 出错")

        return mid

    def getVideoItemInfo(self):
        item_list = {
            "mid": None,
            "video_url": None,
            "music_url": None,
            "image_list": None
        }
        mid = self.getTikTokMid()
        if mid is not None:
            item_list['mid'] = mid
            url = "https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids=" + str(mid)
            try:
                response = requests.get(url=url, headers=self.winHeader)
            except requests.exceptions as e:
                logging.error(e)
            else:
                if response.status_code == 200:
                    item_info = json.loads(response.text)
                    music_info = item_info["item_list"][0]["music"]
                    video_info = item_info["item_list"][0]["video"]
                    image_info = item_info["item_list"][0]["images"]

                    if music_info is not None:
                        item_list['music_url'] = music_info['play_url']['url_list'][0]

                    if video_info is not None:
                        video_url = video_info['play_addr']['url_list'][0]
                        item_list['video_url'] = video_url.replace("playwm", "play")

                    if image_info is not None:
                        item_list['image_list'] = []
                        for i in range(len(image_info)):
                            tmp = []
                            uri = image_info[i]['uri'].split('/')[-1]
                            url = image_info[i]['url_list'][0]
                            tmp.append(uri)
                            tmp.append(url)
                            item_list['image_list'].append(tmp)
        return item_list


if __name__ == '__main__':
    LOG_FORMAT = "%(levelname)s:\t%(message)s"
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    app = QApplication(sys.argv)
    mainWin = TikTokUI()
    mainWin.show()
    sys.exit(app.exec_())
