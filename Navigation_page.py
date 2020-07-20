from selenium import webdriver
import time
import html
import sys
import os
from datetime import datetime, timedelta
import Global_var
import wx
import string
import html
import re
from Insert_On_Datbase import insert_in_Local,create_filename

app = wx.App()


def ChromeDriver():
    browser = webdriver.Chrome(executable_path=str(f"C:\\chromedriver.exe"))
    browser.get("http://www.cebw.org/en/biddings-in-progress")
    browser.maximize_window()
    time.sleep(2)
    tr_count = 2
    for Iframe_outerHTML in browser.find_elements_by_xpath('//*[@id="blockrandom"]'):
        Iframe_outerHTML = Iframe_outerHTML.get_attribute('outerHTML').replace('<!---->','').replace('-\t','').replace('-\n','').replace('\t','').replace('\n','').strip()
        Iframe_outerHTML = re.sub(' +', ' ', str(Iframe_outerHTML))
        Link = Iframe_outerHTML.partition('name="iframe" src="')[2].partition('" width="100%" height="700"')[0].strip()
        browser.get(Link)
        time.sleep(2)
        break

    for tr in browser.find_elements_by_xpath('//*[@id="body"]/form/table/tbody/tr/td/table/tbody/tr'):
        if tr_count != 14:
            Tender_id = ''
            Document = ''
            start_date = ''
            Deadline = ''
            SCHEDULED_DATE = ''
            Title = ''
            for Tender_id in browser.find_elements_by_xpath(f'//*[@id="body"]/form/table/tbody/tr/td/table/tbody/tr[{str(tr_count)}]/td[1]'):
                Tender_id = Tender_id.get_attribute('innerText').strip()
                break
            for Document in browser.find_elements_by_xpath(f'//*[@id="body"]/form/table/tbody/tr/td/table/tbody/tr[{str(tr_count)}]/td[1]/a'):
                Document = Document.get_attribute('href').strip()
                Document = Document.partition("('")[2].partition("',")[0]
                Document = f'https://dakota.cebw.org/cebwWeb/Bids?action=showDocument&documentId={str(Document)}&documentType=TERM'
                break
            for start_date in browser.find_elements_by_xpath(f'//*[@id="body"]/form/table/tbody/tr/td/table/tbody/tr[{str(tr_count)}]/td[2]'):
                start_date = start_date.get_attribute('innerText').strip()
                break
            for Deadline in browser.find_elements_by_xpath(f'//*[@id="body"]/form/table/tbody/tr/td/table/tbody/tr[{str(tr_count)}]/td[3]'):
                Deadline = Deadline.get_attribute('innerText')
                break
            for SCHEDULED_DATE in browser.find_elements_by_xpath(f'//*[@id="body"]/form/table/tbody/tr/td/table/tbody/tr[{str(tr_count)}]/td[4]'):
                SCHEDULED_DATE = SCHEDULED_DATE.get_attribute('innerText').strip()
                break
            tr_count += 1
            for Title in browser.find_elements_by_xpath(f'//*[@id="body"]/form/table/tbody/tr/td/table/tbody/tr[{str(tr_count)}]/td[1]'):
                Title = Title.get_attribute('innerText').strip()
                break
            tr_count += 1
            scrap_data(Tender_id, Document, start_date,Deadline, SCHEDULED_DATE, Title)
            Global_var.Total += 1
            print(f'Total: {str(Global_var.Total)} Deadline Not given: {Global_var.deadline_Not_given} duplicate: {Global_var.duplicate} inserted: {Global_var.inserted} expired: {Global_var.expired} QC Tenders: {Global_var.QC_Tenders}')
        eles:
            wx.MessageBox(f'Total: {str(Global_var.Total)}\nDeadline Not given: {Global_var.deadline_Not_given}\nduplicate: {Global_var.duplicate}\ninserted: {Global_var.inserted}\nexpired: {Global_var.expired}\nQC Tenders: {Global_var.QC_Tenders}','cebw.org', wx.OK | wx.ICON_INFORMATION)
            browser.close()
            sys.exit()
    wx.MessageBox(f'Total: {str(Global_var.Total)}\nDeadline Not given: {Global_var.deadline_Not_given}\nduplicate: {Global_var.duplicate}\ninserted: {Global_var.inserted}\nexpired: {Global_var.expired}\nQC Tenders: {Global_var.QC_Tenders}','cebw.org', wx.OK | wx.ICON_INFORMATION)
    browser.close()
    sys.exit()

def scrap_data(Tender_id, Document, start_date, Deadline, SCHEDULED_DATE, Title):
    SegField = []
    for data in range(42):
        SegField.append('')
    a = True
    while a == True:
        try:

            SegField[1] = 'cebw@cebw.org'
            SegField[2] = '4632 Wisconsin Ave, NW, Washington, DC, 20016-4622, USA, Tel : (202)244-5010'
            SegField[8] = 'http://www.cebw.org/'
            SegField[12] = 'BRAZILIAN ARMY COMMISSION (BAC)'
            SegField[13] = Tender_id
            SegField[19] = string.capwords(str(Title)).replace('`','')
            SegField[5] = Document
            SegField[18] = f'{SegField[19]}<br>\nStart Date: {start_date}<br>\nSubmitting Initial Proposal: {Deadline}<br>\nScheduled Date: {SCHEDULED_DATE}'

            Deadline = Deadline.replace('AM', '').replace('PM', '').strip()
            datetime_object = datetime.strptime(Deadline, '%m/%d/%Y %H:%M:%S')
            Deadline = datetime_object.strftime("%Y-%m-%d")
            SegField[24] = Deadline.strip()
            SegField[14] = '2'
            SegField[22] = "0"
            SegField[26] = "0.0"
            SegField[27] = "0"  # Financier
            SegField[7] = 'BR'
            SegField[28] = 'http://www.cebw.org/en/biddings-in-progress'
            SegField[31] = 'cebw.org'

            for SegIndex in range(len(SegField)):
                print(SegIndex, end=' ')
                print(SegField[SegIndex])
                SegField[SegIndex] = html.unescape(str(SegField[SegIndex]))
                SegField[SegIndex] = str(SegField[SegIndex]).replace("'", "''")

            if len(SegField[19]) >= 200:
                SegField[19] = str(SegField[19])[:200]+'...'

            if len(SegField[18]) >= 1500:
                SegField[18] = str(SegField[18])[:1500]+'...'

            if SegField[19] == '':
                wx.MessageBox(' Short Desc Blank ', 'cebw.org',wx.OK | wx.ICON_INFORMATION)
            else:
                check_date(SegField)
            a = False
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error ON : ", sys._getframe().f_code.co_name + "--> " + str(e), "\n", exc_type, "\n", fname, "\n",
                  exc_tb.tb_lineno)
            a = True
            time.sleep(5)


def check_date(SegField):
    deadline = str(SegField[24])
    curdate = datetime.now()
    curdate_str = curdate.strftime("%Y-%m-%d")
    try:
        if deadline != '':
            datetime_object_deadline = datetime.strptime(deadline, '%Y-%m-%d')
            datetime_object_curdate = datetime.strptime(curdate_str, '%Y-%m-%d')
            timedelta_obj = datetime_object_deadline - datetime_object_curdate
            day = timedelta_obj.days
            if day > 0:
                insert_in_Local(SegField)
            else:
                print("Expired Tender")
                Global_var.expired += 1
        else:
            print("Deadline Not Given")
            Global_var.deadline_Not_given += 1
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("Error ON : ", sys._getframe().f_code.co_name + "--> " +
              str(e), "\n", exc_type, "\n", fname, "\n", exc_tb.tb_lineno)


ChromeDriver()
