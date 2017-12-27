# -*- coding: utf-8 -*-
# @author AoBeom
# @create date 2017-12-25 05:26:05
# @modify date 2017-12-25 05:26:05
# @desc [ keyakizaka offical blog download ]

import argparse
import os
import re
import sys
from multiprocessing.dummy import Pool

import requests


class keyablog(object):
    def __init__(self):
        self.homepage = "http://www.keyakizaka46.com"

    # requests处理函数 / requests
    def __requests(self, url, params=None, timeout=30):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
        }
        if params:
            response = requests.get(
                url, headers=headers, params=params, timeout=timeout)
            return response
        else:
            response = requests.get(url, headers=headers, timeout=timeout)
            return response

    # 获取成员名 / member name
    def __memberGet(self, url):
        blog_owner_rule = r'<title>(.*?)</title>'
        blog_owner_response = self.__requests(url)
        blog_owner_title = blog_owner_response.text
        blog_owner_regex = re.findall(
            blog_owner_rule, blog_owner_title, re.S | re.M)
        blog_owner = blog_owner_regex[0].split("|")[0].strip()
        return blog_owner

    # 检查获取方式 按页码page获取 | 按单篇next|prev获取
    def keyaModeCheck(self, url, method=None, value=None):
        # 页码 page
        if ("diary/member/list" or "/artist/" in url) and (method == "page"):
            if "page" in url:
                # 移除第二页以后的page和cd请求参数 / remove para
                url = re.sub(r'\&page\=[0-9]+\&cd\=member', "", url)
                return url, method, value
            elif "artist" in url:
                # 个人首页转换为个人页数首页 / profile to page_index
                blog_head = url.rfind("artist")
                blog_member_code = url.split("/")[-1].split("?")[0]
                blog_page_tail = "diary/member/list?ima=0000&ct={}&page=0&cd=member".format(
                    blog_member_code)
                url = url[0:blog_head] + blog_page_tail
                return url, method, value
            else:
                return url, method, value
        # 单篇 single
        elif "diary/detail" in url and method == "single":
            return url, method, value
        else:
            print "The url and mode do not match."
            sys.exit()

    # 获取总页数 / pages
    def __keyaPages(self, url):
        response = self.__requests(url)
        # 第一页 / first page
        blog_first_page_content = response.text
        blog_pager_rule = r'<li><span class="active">|<li><a href="(.*?)">'
        blog_pages = re.findall(
            blog_pager_rule, blog_first_page_content, re.S | re.M)
        blog_pages_new = [page for page in blog_pages if page]
        blog_first_page_total = len(blog_pages_new)
        pages = 0
        blog_next_page_total = blog_first_page_total
        # 小于9页没有next / check next
        if blog_first_page_total < 9:
            pages = blog_first_page_total
        else:
            blog_max_page = max(blog_pages_new)
            blog_next_page = self.homepage + blog_max_page
            blog_older_page = ""
            # 自动翻页 / autopager
            while blog_next_page_total <= 10:
                response = self.__requests(blog_next_page)
                blog_first_page_content = response.text
                blog_pager_rule = r'<li><a href="(.*?)">'
                blog_pages = re.findall(
                    blog_pager_rule, blog_first_page_content, re.S | re.M)
                blog_pages_new_list = [page for page in blog_pages if page]
                blog_page_tmp = ""
                blog_page_max_index = 0
                for blog_index, blog_value in enumerate(blog_pages_new_list):
                    blog_page_str = blog_value.split(
                        "&")[1].split("=")[-1].zfill(4)
                    # 最后一页 / last page
                    if blog_page_str > blog_page_tmp:
                        blog_page_tmp = blog_page_str
                        blog_page_max_index = blog_index
                blog_max_page = blog_pages_new_list[blog_page_max_index]
                if blog_max_page > blog_older_page:
                    blog_older_page = blog_max_page
                else:
                    break
                blog_next_page = self.homepage + blog_max_page
                blog_next_page_total = len(blog_pages_new_list)
            page_rul = r'page\=[0-9]+'
            pages = re.findall(page_rul, blog_older_page,
                               re.S | re.M)[-1].split("=")[-1]
        return pages

    # 获取每篇博客的地址 / blog url
    def keyaUrlsGet(self, url_mode):
        url = url_mode[0]
        method = url_mode[1]
        value = url_mode[2]
        blog_name = self.__memberGet(url)
        member_info = {}
        member_info["name"] = blog_name
        # 页数处理 page
        if method == "page":
            if value[0] == "0" and value[1] == "0":
                pages = self.__keyaPages(url)
                blog_page_range_s = 1
                blog_page_range_e = int(pages) + 1
            else:
                blog_page_range_s = int(value[0])
                blog_page_range_e = int(value[1]) + 1
            # 单篇博客的地址标签 page html element
            blog_rule_single = r'<li class="singlePage">(.*?)<a href="(.*?)">(.*?)</a>'
            blog_urls = []
            for page in range(blog_page_range_s, blog_page_range_e):
                # 拼接页数页面 请求参数request page=x&cd=member
                url_new = url + "&page={page}&cd=member".format(page=page - 1)
                blog_page_response = self.__requests(url_new)
                blog_content_page = blog_page_response.text
                blog_content_urls = re.findall(
                    blog_rule_single, blog_content_page, re.S | re.M)
                if blog_content_urls:
                    urls = [self.homepage + c[1] for c in blog_content_urls]
                    blog_urls = blog_urls + urls
                else:
                    break
            member_info["urls"] = blog_urls
            return member_info
        # 单篇处理 single
        if method == "single":
            value = ''.join(value)
            plus_minus = value[0]
            blog_urls = []
            if len(value) > 1:
                numbers = int(value[1:])
            # 下一页 next
            if plus_minus == "+":
                blog_urls.append(url)
                flag = 0
                # next翻页标签
                blog_rule_next = r'<div class="btn-navi btn-next">(.*?)<a href="(.*?)">'
                blog_single_response = self.__requests(url)
                blog_content_single = blog_single_response.text
                blog_next_regex = re.findall(
                    blog_rule_next, blog_content_single, re.S | re.M)
                # 一直获取，直到小于指定页数
                while blog_next_regex and flag < numbers:
                    url_new = self.homepage + blog_next_regex[0][1]
                    blog_urls.append(url_new)
                    flag = flag + 1
                    blog_single_response = self.__requests(url_new)
                    blog_content_single = blog_single_response.text
                    blog_next_regex = re.findall(
                        blog_rule_next, blog_content_single, re.S | re.M)
                member_info["urls"] = blog_urls
                return member_info
            # 上一页 prev
            elif plus_minus == "-":
                blog_urls.append(url)
                flag = 0
                # prev翻页标签
                blog_rule_prev = r'<div class="btn-navi btn-prev">(.*?)<a href="(.*?)">'
                blog_single_response = self.__requests(url)
                blog_content_single = blog_single_response.text
                blog_prev_regex = re.findall(
                    blog_rule_prev, blog_content_single, re.S | re.M)
                # 一直获取，直到小于指定页数
                while blog_prev_regex and flag < numbers:
                    url_new = self.homepage + blog_prev_regex[0][1]
                    blog_urls.append(url_new)
                    flag = flag + 1
                    blog_single_response = self.__requests(url_new)
                    blog_content_single = blog_single_response.text
                    blog_prev_regex = re.findall(
                        blog_rule_prev, blog_content_single, re.S | re.M)
                member_info["urls"] = blog_urls
                return member_info
            else:
                # 只有1篇 / only one
                blog_urls.append(url)
                member_info["urls"] = blog_urls
                return member_info

    # 获取每篇博客的内容 / blog content
    def keyakiBlog(self, urls):
        blog = {}
        # 标题 内容 时间匹配
        rule_title = r'<div class="box-ttl">(.*?)<h3>(.*?)</h3>'
        rule_box = r'<div class="box-article">(.*?)<div class="box-bottom">'
        rule_bottom = r'<div class="box-bottom">(.*?)<ul>(.*?)<li>(.*?)</li>(.*?)</ul>(.*?)</div>'
        u = urls
        blog_index_response = self.__requests(u)
        blog_index_text = blog_index_response.text
        blog_title_regex = re.findall(
            rule_title, blog_index_text, re.S | re.M)
        # 第一次定位内容标签
        blog_content_regex = re.findall(
            rule_box, blog_index_text, re.S | re.M)
        blog_date_regex = re.findall(
            rule_bottom, blog_index_text, re.S | re.M)
        blog_title = blog_title_regex[0][1].strip()
        blog_content = blog_content_regex[0].strip()
        blog_date = blog_date_regex[0][2].strip()
        # 第二次获取内容
        rule_text = r'(>(.*?)<|src="(.*?)")'
        blog_text = re.findall(rule_text, blog_content, re.S | re.M)
        blog_text_list = []
        for b_text in blog_text:
            b_text = re.sub('[\<\>\"]|src\=|\&nbsp\;|\n|[\s]+',
                            "", b_text[0].strip())
            if len(b_text) != 0:
                blog_text_list.append(b_text)
        # 博客字典 blog dict
        blog["title"] = blog_title
        blog["date"] = blog_date
        blog["text"] = blog_text_list
        blog["url"] = u
        return blog

    # 图片下载 / img download
    def __keyaImgGet(self, imgurls, path):
        for i in imgurls:
            try:
                r = self.__requests(i)
                img_name = os.path.join(path, i.split("/")[-1])
                with open(img_name, "wb") as code:
                    for chunk in r.iter_content(chunk_size=1024):
                        code.write(chunk)
            except BaseException:
                print i

    # 博客记录 写文件 / blog write to file
    def keyaRecord(self, paras):
        blog = paras[0]
        path = paras[1]
        blog_title = blog["title"]
        blog_date = blog["date"]
        blog_text = blog["text"]
        blog_url = blog["url"]
        # 博客图片地址获取 / img url
        imgurls = [
            b_img for b_img in blog_text if "cdn.keyakizaka46.com" in b_img]
        # 格式化日期 移除非法字符 / filename
        blog_date_format = blog_date.replace(
            "/", "-").replace(" ", "-").replace(":", "-")
        # 文件夹 folder
        folder_name = os.path.join(path, blog_date_format)
        img_folder = os.path.join(path, folder_name)
        # 记录正文 / record
        if not os.path.exists(folder_name):
            os.mkdir(folder_name)
            text_file = os.path.join(folder_name, "blog.txt")
            f = open(text_file, "wb")
            try:
                f.write(blog_url + "\r\n")
            except BaseException:
                print "Error: Blog_url {}".format(blog_url)
            try:
                f.write(blog_title.encode("utf-8") + "\r\n")
            except BaseException:
                print "Error: Title {}".format(blog_title)
            for b_text in blog_text:
                try:
                    f.write(b_text.encode("utf-8") + "\r\n")
                except BaseException:
                    print "Error: Text {}".format(b_text)
            # 调用图片下载
            self.__keyaImgGet(imgurls, img_folder)


def opts():
    paras = argparse.ArgumentParser(
        prog='keyablog', description="Keyakizaka46 Blog Download.")
    group = paras.add_mutually_exclusive_group()
    group.add_argument('-p', dest='pagerange', action="store",
                       default=None, help="Download some blogs by page [1-2,3,4-6..]")
    group.add_argument('-s', dest='singlerange', action="store",
                       default=None, help="Download some blogs by single [1,+5,-3...]")
    paras.add_argument('-u', dest='url', action="store",
                       type=str, required=True, help="Blog url")
    args = paras.parse_args()
    return args


def optsCheck():
    args = opts()
    pagerange = args.pagerange
    singlerange = args.singlerange
    url = args.url
    if pagerange or singlerange:
        mode = {}
        if pagerange:
            if "-" in pagerange:
                mode["method"] = "page"
                mode["url"] = url
                page_cut = pagerange.split("-")
                print page_cut
                if page_cut[0] == "0" and page_cut[1] > "0":
                    print "The input format is wrong."
                    sys.exit()
                if page_cut[0] != "" and int(page_cut[1]) > int(page_cut[0]):
                    mode["value"] = page_cut
                else:
                    print "The input format is wrong."
                    sys.exit()
            elif isinstance(int(pagerange), int):
                mode["method"] = "page"
                mode["url"] = url
                mode["value"] = [pagerange, pagerange]
            else:
                print "The input format is wrong."
                sys.exit()
        if singlerange:
            if singlerange.startswith("+") or singlerange.startswith("-"):
                mode["method"] = "single"
                mode["value"] = [singlerange]
                mode["url"] = url
            elif singlerange == "1":
                mode["method"] = "single"
                mode["value"] = [singlerange]
                mode["url"] = url
            else:
                print "The input format is wrong."
                sys.exit()
        return mode
    else:
        print "python keyablog -h"
        sys.exit()


def main():
    mode = optsCheck()
    method = mode["method"]
    value = mode["value"]
    url = mode["url"]
    k = keyablog()
    # 获取方式判断 / mode check
    url_mode = k.keyaModeCheck(url, method=method, value=value)
    print "Checking..."
    # 单篇博客地址获取 / blog url
    blog_dict = k.keyaUrlsGet(url_mode)
    blog_owner = blog_dict["name"]
    blog_urls = blog_dict["urls"]
    blog_total = len(blog_urls)
    if blog_total == 0:
        raw_input("No Blog.")
        sys.exit()
    # 创建文件夹 统计条数 / save to folder
    blog_folder = os.path.join(os.getcwd(), blog_owner)
    if not os.path.exists(blog_folder):
        os.mkdir(blog_folder)
    thread = blog_total / 2
    blog_folders = [blog_folder] * blog_total
    print "Total [{}]".format(blog_total)
    # 线程数 / thread
    if thread < 2:
        thread = 1
    elif thread > 100:
        thread = 50
    else:
        thread = thread
    print "Downloading..."
    # 并发下载 / pool
    pool = Pool(thread)
    # 博客内容获取 / blog content
    blog_content = pool.map(k.keyakiBlog, blog_urls)
    # 博客记录 / record
    blog_record = zip(blog_content, blog_folders)
    pool.map(k.keyaRecord, blog_record)
    pool.close()
    pool.join()
    raw_input("Good!")


if __name__ == "__main__":
    main()
